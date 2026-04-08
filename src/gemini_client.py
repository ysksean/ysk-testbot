import os
import json
from datetime import date
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = f"""당신은 친근한 한국어 일정 관리 비서입니다.
오늘 날짜: {date.today().isoformat()}
사용자의 일정을 조회하거나 추가하는 것을 도와줍니다.
항상 간결하고 자연스러운 한국어로 답변하세요.
일정 추가가 필요하면 반드시 create_calendar_event 함수를 호출하세요.
종료 시간이 언급되지 않으면 시작 시간 +1시간으로 설정하세요."""

MODEL = "llama-3.1-8b-instant"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_calendar_event",
            "description": "구글 캘린더에 일정을 추가합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "일정 제목"},
                    "start_time": {"type": "string", "description": "시작 시간 (YYYY-MM-DDTHH:MM:00)"},
                    "end_time": {"type": "string", "description": "종료 시간 (YYYY-MM-DDTHH:MM:00)"},
                },
                "required": ["title", "start_time", "end_time"],
            },
        },
    }
]


class GeminiClient:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.histories: dict[int, list] = {}

    def chat(self, user_id: int, message: str, calendar_context: str = "") -> tuple[str, dict | None]:
        if user_id not in self.histories:
            self.histories[user_id] = []

        full_message = message
        if calendar_context:
            full_message = f"{calendar_context}\n\n사용자 질문: {message}"

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages += self.histories[user_id]
        messages.append({"role": "user", "content": full_message})

        response = self.client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        choice = response.choices[0]
        event_args = None

        if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
            tool_call = choice.message.tool_calls[0]
            event_args = json.loads(tool_call.function.arguments)

            messages.append(choice.message)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": "일정 추가 요청을 처리합니다.",
            })

            follow_up = self.client.chat.completions.create(
                model=MODEL,
                messages=messages,
            )
            reply = follow_up.choices[0].message.content
        else:
            reply = choice.message.content

        self.histories[user_id].append({"role": "user", "content": full_message})
        self.histories[user_id].append({"role": "assistant", "content": reply})

        return reply, event_args
