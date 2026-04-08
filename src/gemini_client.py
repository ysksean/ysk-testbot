import os
import json
from datetime import date
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """당신은 친근한 한국어 일정 관리 비서입니다.
사용자의 일정을 조회하거나 추가하는 것을 도와줍니다.
항상 간결하고 자연스러운 한국어로 답변하세요.
중요: 일정 추가/수정/삭제는 시스템이 직접 처리합니다. 당신이 직접 일정을 추가했다고 말하지 마세요.
일정 추가 요청이 오면 "일정을 추가해드릴게요!" 정도로만 말하세요."""

MODEL = "llama-3.1-8b-instant"


class GeminiClient:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.histories: dict[int, list] = {}

    def chat(self, user_id: int, message: str, calendar_context: str = "") -> str:
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
        )
        reply = response.choices[0].message.content

        self.histories[user_id].append({"role": "user", "content": full_message})
        self.histories[user_id].append({"role": "assistant", "content": reply})

        return reply

    def parse_event(self, message: str) -> dict | None:
        today = date.today().isoformat()
        prompt = f"""오늘 날짜: {today}
다음 메시지에서 일정 정보를 JSON으로 추출하세요.
반드시 아래 형식만 반환하고 다른 텍스트는 넣지 마세요.
일정 정보가 불충분하면 null을 반환하세요.
종료 시간이 없으면 시작 시간 +1시간으로 설정하세요.

형식:
{{"title": "일정 제목", "start_time": "YYYY-MM-DDTHH:MM:00", "end_time": "YYYY-MM-DDTHH:MM:00"}}

메시지: {message}"""

        try:
            response = self.client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )
            text = response.choices[0].message.content.strip().strip("```json").strip("```").strip()
            if text == "null":
                return None
            return json.loads(text)
        except Exception as e:
            print(f"[parse_event 오류] {e}")
            return None
