from telegram import Update
from telegram.ext import ContextTypes
from src.gemini_client import GeminiClient
from src.calendar_client import CalendarClient

gemini = GeminiClient()
calendar = CalendarClient()


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    await update.message.chat.send_action("typing")

    calendar_context = ""
    if any(kw in user_text for kw in ["일정", "스케줄", "언제", "몇시", "추가", "잡아", "예약"]):
        events = calendar.get_events(days=7)
        if events:
            calendar_context = "현재 등록된 일정:\n" + "\n".join(events)

    reply = gemini.chat(user_id, user_text, calendar_context)

    if any(kw in user_text for kw in ["추가", "잡아", "등록", "넣어"]):
        parsed = gemini.parse_event(user_text)
        if parsed:
            result = calendar.create_event(
                title=parsed["title"],
                start_time=parsed["start_time"],
                end_time=parsed["end_time"],
            )
            if result:
                reply += f"\n\n✅ 캘린더에 [{parsed['title']}] 추가 완료!"
            else:
                reply += f"\n\n❌ 캘린더 추가에 실패했어요. 다시 시도해주세요."
        else:
            reply += f"\n\n⚠️ 일정 정보를 파악하지 못했어요. 날짜와 시간을 명확히 알려주세요."

    await update.message.reply_text(reply)
