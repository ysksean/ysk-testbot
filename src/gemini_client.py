import os
import json
import redis
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
HISTORY_LIMIT = 20  # 저장할 최대 메시지 수

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
        redis_url = os.getenv("REDIS_URL")
        self.redis = redis.from_url(redis_url) if redis_url else None

    def _get_history(self, user_id: int) -> list:
        if not self.redis:
            return []
        raw = self.redis.get(f"history:{user_id}")
        return json.loads(raw) if raw else []

    def _save_history(self, user_id: int, history: list):
        if not self.redis:
            return
        trimmed = history[-HISTORY_LIMIT:]
        self.redis.set(f"history:{user_id}", json.dumps(trimmed, ensure_ascii=False))

    def chat(self, user_id: int, message: str, calendar_context: str = "") -> tuple[str, dict | None]:
        history = self._get_history(user_id)

        full_message = message
        if calendar_context:
            full_message = f"{calendar_context}\n\n사용자 질문: {message}"

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages += history
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

        history.append({"role": "user", "content": full_message})
        history.append({"role": "assistant", "content": reply})
        self._save_history(user_id, history)

        return reply, event_args
