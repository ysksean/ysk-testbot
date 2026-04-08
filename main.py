import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, MessageHandler, filters
from src.handlers import handle_message
from src.notifier import check_and_notify

load_dotenv()


def main():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise ValueError(".env에 TELEGRAM_TOKEN이 없습니다.")

    app = ApplicationBuilder().token(token).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # 5분마다 일정 알림 체크
    app.job_queue.run_repeating(check_and_notify, interval=300, first=10)

    print("봇 시작됨. Ctrl+C로 종료.")
    app.run_polling()


if __name__ == "__main__":
    main()
