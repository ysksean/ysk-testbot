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

    events = calendar.get_events(days=14)
    calendar_context = "현재 등록된 일정:\n" + "\n".join(events) if events else "등록된 일정 없음"

    reply, event_args = gemini.chat(user_id, user_text, calendar_context)

    if event_args:
        result = calendar.create_event(
            title=event_args["title"],
            start_time=event_args["start_time"],
            end_time=event_args["end_time"],
        )
        if result:
            reply += f"\n\n✅ 캘린더에 [{event_args['title']}] 추가 완료!"
        else:
            reply += f"\n\n❌ 캘린더 추가에 실패했어요. 다시 시도해주세요."

    await update.message.reply_text(reply)
