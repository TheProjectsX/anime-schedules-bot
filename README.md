# Anime Schedules Bot!

Get Anime Schedules information from Telegram Bot!

## Test the Bot:

https://t.me/anime_schedulesbot

### Packages:

-   python-telegram-bot
-   [anime-schedules](https://github.com/TheProjectsX/anime-schedules)
-   python-dotenv

### How to Use:

-   Add token in `.env` file as in `.env.example`
-   Run:

```bash
pip install -r requirements.txt
python app.py
```

### FUTURE Note:

**How I Hosted the Bot for Free**

-   Created a Flask server with all the module/api requests
-   Created a separate script to handle telegram bot requests and Server API
-   Hosted SERVER APP (flask) in the vercel
-   Hosted Bot Script at [https://pella.app/](https://pella.app/)

**Update**::

-   Instead of the above technic, which caused so much time, We tried another method!
-   Create a basic Flask application
-   Create the bot File in same directory
    -   Remove `__name__ == "__main__"` and directly start the pooling
-   Import the Telegram Bot file in Flask
-   Done!
