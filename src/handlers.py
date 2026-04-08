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
    if events:
        lines = [f"- [ID:{e['id']}] {e['start']}: {e['title']}" for e in events]
        calendar_context = "현재 등록된 일정:\n" + "\n".join(lines)
    else:
        calendar_context = "등록된 일정 없음"

    reply, tool_name, tool_args = gemini.chat(user_id, user_text, calendar_context)

    if tool_name == "create_calendar_event":
        result = calendar.create_event(
            title=tool_args["title"],
            start_time=tool_args["start_time"],
            end_time=tool_args["end_time"],
        )
        reply += f"\n\n✅ [{tool_args['title']}] 추가 완료!" if result else "\n\n❌ 추가 실패"

    elif tool_name == "delete_calendar_event":
        result = calendar.delete_event(event_id=tool_args["event_id"])
        reply += f"\n\n🗑️ [{tool_args['title']}] 삭제 완료!" if result else "\n\n❌ 삭제 실패"

    elif tool_name == "update_calendar_event":
        result = calendar.update_event(
            event_id=tool_args["event_id"],
            title=tool_args["title"],
            start_time=tool_args["start_time"],
            end_time=tool_args["end_time"],
        )
        reply += f"\n\n✏️ [{tool_args['title']}] 수정 완료!" if result else "\n\n❌ 수정 실패"

    await update.message.reply_text(reply)
