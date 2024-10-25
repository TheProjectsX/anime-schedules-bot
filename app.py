from datetime import datetime, timedelta
import os
import re
import time
from typing import Callable
import telegram
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


### Utility Functions ###


# Timeout Wrapper
async def timeoutWrapper(
    function: Callable, update: Update, context: ContextTypes.DEFAULT_TYPE
):
    try:
        await function(update, context)
    except telegram.error.TimedOut:
        print("Timeout")
        await time.sleep(3)
        await function(update, context)


# Escape Safe Characters
def escapeMarkdownV2(text: str) -> str:
    specialCharacters = r"\[\]()~>#+-=|{}.!"
    escapedText = re.sub(f"([{re.escape(specialCharacters)}])", r"\\\1", text)

    return escapedText


# Return Formatted Number
def formatNumber(num):
    if len(str(num)) == 1:
        return f"0{num}"
    else:
        return num


# Format Anime Info
def getAnimeInfoFormatted(data):
    future_time = datetime.fromtimestamp(data.get("next", {}).get("timestamp"))
    now = datetime.now()
    time_left = future_time - now
    if time_left < timedelta(0):
        publishTime = f"None"
        timeLeft = f"None"
    else:
        seconds = time_left.seconds
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        publishTime = f"**`{future_time.strftime("%b %d, %Y")}`** at **`{future_time.strftime("%I:%M %p")}`**"
        timeLeft = f"**`{hours}H {minutes}M {seconds}S`**"

    message = f"""**`{data.get("title")}`
**Episode No: *{formatNumber(data.get("next", {}).get("episode"))}*
Publish Time: {publishTime}
Time Left: {timeLeft}"""

    return message


### Command Functions ###


# Start Command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""Get Anime Schedules Information Easily!""")


# Help Command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""Some Help in here""")


# Anime Next 24 Hours
async def next_24_hours_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    animeScheduleData = anis.getAnimeScheduleOfNextHours(hours=24)

    messages = []
    for data in animeScheduleData.get("data", []):
        message = getAnimeInfoFormatted(data)
        messages.append(message)

    response_message = f"""__*Anime Schedule*__
Here are the anime in next 24 Hours!

{"\n\n".join(messages)}"""

    await update.message.reply_text(
        escapeMarkdownV2(response_message), parse_mode="MarkdownV2"
    )


# Anime Today
async def anime_today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    nextMidnight = datetime(now.year, now.month, now.day) + timedelta(days=1)
    timeRemaining = nextMidnight - now
    hoursLeft = timeRemaining.seconds // 3600

    animeScheduleData = anis.getAnimeScheduleOfNextHours(hours=hoursLeft)

    messages = []
    for data in animeScheduleData.get("data", []):
        message = getAnimeInfoFormatted(data)
        messages.append(message)

    response_message = f"""__*Anime Schedule*__
Here are the anime scheduled today (till 12AM)!

{"\n\n".join(messages)}"""

    await update.message.reply_text(
        escapeMarkdownV2(response_message), parse_mode="MarkdownV2"
    )


# Error Handler
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error: {context.error}")

    await update.message.reply_text("Server Error, Please try again!")


if __name__ == "__main__":
    print("Starting...")
    app = Application.builder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(
        CommandHandler(
            "anime_today",
            lambda update, context: timeoutWrapper(
                anime_today_command, update, context
            ),
        )
    )
    app.add_handler(
        CommandHandler(
            "next_24_hours",
            lambda update, context: timeoutWrapper(
                next_24_hours_command, update, context
            ),
        )
    )

    # Error handle
    app.add_error_handler(error)

    print("Pooling...")
    app.run_polling(poll_interval=3, timeout=60)
