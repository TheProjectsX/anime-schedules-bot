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
    ContextTypes,
)
import anime_schedules as anis
import dotenv

dotenv.load_dotenv(".env")


# Global Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = ""

### Utility Functions ###


def paginateList(messages: list[str], charLimit=3080, headerSkip=0) -> list[str]:
    pages = []
    currentPage = ""

    for idx, item in enumerate(messages):
        if idx == 0:
            limit = charLimit - headerSkip
        else:
            limit = charLimit

        if len(currentPage) + len(item) + 1 <= limit:
            if currentPage:
                currentPage += "\n\n"
            currentPage += item
        else:

            pages.append(currentPage)
            currentPage = item

    if currentPage:
        pages.append(currentPage)

    return pages


# Timeout Wrapper
async def timeoutWrapper(
    function: Callable, update: Update, context: ContextTypes.DEFAULT_TYPE
):
    try:
        await function(update, context)
    except telegram.error.TimedOut:
        print("Timeout")
        time.sleep(3)
        await function(update, context)


# Escape Safe Characters
def escapeMarkdownV2(text: str) -> str:
    specialCharacters = r"\[\]()~>#+-=|{}.!_"
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
    timestamp = data.get("next", {}).get("timestamp", "None")
    if type(timestamp) is str:
        publishTime = f"**`{timestamp}`**"
        timeLeft = f"_None_"
    else:
        futureTime = datetime.fromtimestamp(timestamp)
        now = datetime.now()
        timeLeft = futureTime - now

        days, seconds = timeLeft.days, timeLeft.seconds
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        publishTime = f"**`{futureTime.strftime('%b %d, %Y')}`** at **`{futureTime.strftime('%I:%M %p')}`**"
        timeLeft = f"**`{(str(days) + 'D ') if days > 0 else ''}{hours}H {minutes}M {seconds}S`**"

    message = f"""**`{data.get('title')}`
**Episode No: *{formatNumber(data.get("next", {}).get("episode"))}*
Publish Time: {publishTime}
Time Left: {timeLeft}"""

    return message


# Send Reply
async def sendReply(
    header: str, messages: list, update: Update, context: ContextTypes.DEFAULT_TYPE
):
    headerSkip = len(header) + 10
    pageWiseMessages = paginateList(messages, headerSkip=headerSkip)

    for i, page in enumerate(pageWiseMessages):
        message = page
        if i == 0:
            message = header + "\n\n" + message
        await update.message.reply_text(
            escapeMarkdownV2(message), parse_mode="MarkdownV2"
        )
        time.sleep(2)
    await update.message.reply_text("------ END ------")


### Command Functions ###


# Start Command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        escapeMarkdownV2(
            """*Welcome to the Anime Schedule Bot! 🎉*

I'm here to help you stay updated with all your favorite anime schedules. Here’s what I can do:

- /anime_today: Get the schedule for anime airing today.
- /next_24_hours: Find out what anime is scheduled in the next 24 hours.
- /current_season: View all anime scheduled for the current season.
- /season [season_name] [year]: Check anime schedules for a specific season.

Just type the command you want to use, and let's dive into the world of anime! If you need assistance, type /help for more options. Enjoy! 🌟
"""
        ),
        parse_mode="MarkdownV2",
    )


# Help Command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        escapeMarkdownV2(
            """📚 **Help Menu**

Here are the commands you can use with this bot:

1. **/start** - Start the Bot
   - Begin your interaction with the bot and receive a warm welcome!

2. **/help** - Get Help
   - Display this help message with a list of available commands.

3. **/anime_today** - Anime Schedule of Today
   - Get the schedule of anime that will be airing today, until 12 AM.

4. **/next_24_hours** - Get Anime Schedule of Next 24 Hours
   - Receive a list of anime that will be airing in the next 24 hours!

5. **/current_season** - Get Anime Scheduled for Current Season
   - Retrieve a complete list of anime scheduled to air in the current season.

6. **/season [season_name] [year]** - Get Anime Scheduled for Given Season
   - Specify a season (e.g., "Spring", "Summer", "Fall", "Winter") and a year to get all anime scheduled for that season.

Feel free to use these commands to explore anime schedules! 🎉
"""
        ),
        parse_mode="MarkdownV2",
    )


# Anime Schedule of Today
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

    joinedMessages = "\n\n".join(messages)
    response_message = f"""__*Anime Schedule*__
Here are the Anime scheduled today (till 12AM)!

{joinedMessages}"""

    await update.message.reply_text(
        escapeMarkdownV2(response_message), parse_mode="MarkdownV2"
    )


# Anime Schedule of Next 24 Hours
async def next_24_hours_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    animeScheduleData = anis.getAnimeScheduleOfNextHours(hours=24)

    messages = []
    for data in animeScheduleData.get("data", []):
        message = getAnimeInfoFormatted(data)
        messages.append(message)

    joinedMessages = "\n\n".join(messages)
    response_message = f"""__*Anime Schedule*__
Here are the Anime in next 24 Hours!

{joinedMessages}"""

    await update.message.reply_text(
        escapeMarkdownV2(response_message), parse_mode="MarkdownV2"
    )


# Anime Schedule of Current Season
async def anime_current_season_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    animeScheduleData = anis.getCurrentSeasonAnimeScheduled(sortby="countdown")
    seasonName, year = anis.getCurrentSeason()

    messages = []
    for data in animeScheduleData.get("data", []):
        message = getAnimeInfoFormatted(data)
        messages.append(message)

    header = f"""__*Anime Schedule*__
Here are the Anime scheduled in {seasonName.title()} {year}!"""

    await sendReply(header, messages=messages, update=update, context=context)


# Anime Schedule of Given season
async def anime_by_season_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not (len(args) >= 2):
        await update.message.reply_text(
            escapeMarkdownV2(
                "You Must Provide season And year\n\nExample: **`/season fall 2024`**"
            ),
            parse_mode="MarkdownV2",
        )
        return

    seasonName = args[0]
    year = args[1]

    validation = anis.validateSeasonInfo(season=seasonName, year=year)
    if not validation.get("valid"):
        await update.message.reply_text(
            escapeMarkdownV2(
                f"{validation.get('message')}\n\nExample: **`/season fall 2024`**"
            ),
            parse_mode="MarkdownV2",
        )
        return

    animeScheduleData = anis.getAnimeScheduleOfSeason(
        season=seasonName, year=year, sortby="countdown"
    )

    messages = []
    for data in animeScheduleData.get("data", []):
        message = getAnimeInfoFormatted(data)
        messages.append(message)

    header = f"""__*Anime Schedule*__
Here are the Anime scheduled in {seasonName.title()} {year}!"""
    await sendReply(header, messages=messages, update=update, context=context)


# Error Handler
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error: {context.error}")

    await update.message.reply_text("Server Error, Please try again!")


# START APP
def setup_app(app):
    # Commands
    app.add_handler(
        CommandHandler(
            "start",
            lambda update, context: timeoutWrapper(start_command, update, context),
        )
    )
    app.add_handler(
        CommandHandler(
            "help",
            lambda update, context: timeoutWrapper(help_command, update, context),
        )
    )
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
    app.add_handler(
        CommandHandler(
            "current_season",
            lambda update, context: timeoutWrapper(
                anime_current_season_command, update, context
            ),
        )
    )
    app.add_handler(
        CommandHandler(
            "season",
            lambda update, context: timeoutWrapper(
                anime_by_season_command, update, context
            ),
        )
    )

    # Error Handler
    app.add_error_handler(error)


if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()

    print("Starting...")
    setup_app(app)

    print("Pooling...")
    app.run_polling()
