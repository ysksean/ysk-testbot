import os
import redis
from datetime import datetime, timezone, timedelta
from telegram.ext import ContextTypes
from src.calendar_client import CalendarClient

calendar = CalendarClient()

NOTIFY_BEFORE_MINUTES = 120  # 2시간 전
WINDOW_MINUTES = 5           # ±5분 윈도우


def _get_redis():
    url = os.getenv("REDIS_URL")
    return redis.from_url(url) if url else None


def _format_time(iso_str: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_str).astimezone()
        hour = dt.hour
        minute = dt.minute
        ampm = "오전" if hour < 12 else "오후"
        hour12 = hour % 12 or 12
        if minute:
            return f"{ampm} {hour12}시 {minute}분"
        return f"{ampm} {hour12}시"
    except Exception:
        return iso_str


async def check_and_notify(context: ContextTypes.DEFAULT_TYPE):
    r = _get_redis()
    user_ids_raw = os.getenv("ALLOWED_USER_IDS", "")
    user_ids = [int(uid) for uid in user_ids_raw.split(",") if uid.strip()]
    if not user_ids:
        return

    now = datetime.now(timezone.utc)
    target_start = now + timedelta(minutes=NOTIFY_BEFORE_MINUTES - WINDOW_MINUTES)
    target_end = now + timedelta(minutes=NOTIFY_BEFORE_MINUTES + WINDOW_MINUTES)

    events = calendar.get_events(days=2)
    for event in events:
        try:
            event_start = datetime.fromisoformat(event["start"])
            if event_start.tzinfo is None:
                event_start = event_start.replace(tzinfo=timezone.utc)
        except Exception:
            continue

        if not (target_start <= event_start <= target_end):
            continue

        redis_key = f"notified:{event['id']}"
        if r and r.get(redis_key):
            continue

        time_str = _format_time(event["start"])
        message = (
            f"⏰ 2시간 후 일정이 있어요!\n\n"
            f"📅 {event['title']}\n"
            f"🕐 {time_str}"
        )

        for user_id in user_ids:
            await context.bot.send_message(chat_id=user_id, text=message)

        if r:
            r.set(redis_key, "1", ex=86400)  # 24시간 TTL
