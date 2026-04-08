import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, MessageHandler, filters
from src.handlers import handle_message

load_dotenv()

def main():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise ValueError(".env에 TELEGRAM_TOKEN이 없습니다.")

    app = ApplicationBuilder().token(token).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("봇 시작됨. Ctrl+C로 종료.")
    app.run_polling()


if __name__ == "__main__":
    main()
