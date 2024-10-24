from datetime import datetime, timedelta
import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import anime_schedules as anis

import dotenv

dotenv.load_dotenv(".env")

# Global Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = ""


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""Get Anime Schedules Information Easily!""")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""Some Help in here""")


async def anime_today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    animeScheduleData = anis.getAnimeScheduleOfToday()

    messages = []
    for data in animeScheduleData.get("data", []):
        future_time = datetime.fromtimestamp(data.get("next", {}).get("timestamp"))
        now = datetime.now()
        time_left = future_time - now
        if time_left < timedelta(0):
            timeLeft = f"None"
        else:
            days, seconds = time_left.days, time_left.seconds
            hours, remainder = divmod(seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            timeLeft = f"{hours} H, {minutes} M, and {seconds} S"

        message = f"{data.get("title")} - {timeLeft}"
        messages.append(message)

    response_message = f"Anime Schedule\n\n{"\n".join(messages)}"
    await update.message.reply_text(response_message)


if __name__ == "__main__":
    print("Starting...")
    app = Application.builder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("anime_today", anime_today_command))

    print("Polling...")

    app.run_polling(poll_interval=3)
