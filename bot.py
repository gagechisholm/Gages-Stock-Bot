import discord
import os
import random
import asyncio
import requests
import logging
import time
from datetime import datetime
import logging
import sys
import psycopg2
from psycopg2.extras import DictCursor
import signal
import requests
import aiohttp
from logging.handlers import RotatingFileHandler

# UPDATE MESSAGE
update_message = (
    "**📢 Update Notification 📢**\n\n"
    "🚀 **What's New in Gage's Stock Bot** 🚀\n\n"
    "1. **Individual Watchlists**: Track your own stocks separately from others in the server. "
    "Your watchlist is private to you, and you can add or remove stocks as you like.\n\n"
    "2. **Leaderboard**: Compete with other users! See the best-performing watchlists based on daily percentage changes. "
    "The leaderboard updates every day after market close.\n\n"
    "3. **Automatic Update Summaries**: Whenever the bot restarts, this message will notify you about recent updates and improvements.\n\n"
    "**Commands Refresher**:\n\n"
    "- Use `!addstock SYMBOL` to add a stock to your watchlist.\n\n"
    "- Use `!watchlist` to view your tracked stocks.\n\n"
    "- Set a channel for notifications with `!setchannel`.\n\n"
    "- View the leaderboard with `!leaderboard`.\n\n"
    "- Customize stock alert thresholds with `!set PERCENTAGE`.\n\n"
    "For detailed help, type `!help`.\n\n\n"
    "Thank you for your continued support 💼📈"
)

# Logging Configuration
handler = RotatingFileHandler("app.log", maxBytes=10 * 1024 * 1024, backupCount=5)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        handler,  # Rotating file handler
        logging.StreamHandler(sys.stdout)  # Console output
    ]
)

logging.info("Bot has started.")

# Heroku API Key (For User Restarts)
HEROKU_API_KEY = heroku_api_key = os.getenv("HEROKU_API_KEY")
if not HEROKU_API_KEY:
    logging.warning("HEROKU_API_KEY is not set. Stock price fetches may fail.")

HEROKU_APP_NAME = heroku_app_name = os.getenv("HEROKU_APP_NAME")
if not HEROKU_APP_NAME:
    logging.warning("HEROKU_APP_NAME is not set. Stock price fetches may fail.")

# Discord client setup
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Finnhub API Key
FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')
if not FINNHUB_API_KEY:
    logging.warning("FINNHUB_API_KEY is not set. Stock price fetches may fail.")

STOCK_API_URL = "https://finnhub.io/api/v1/quote?symbol={symbol}&token={apikey}"

# SQLite database file
DB_FILE = "stocks.db"

# Universal request tracking
request_count = 0
MONTHLY_LIMIT = 30000

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logging.error("DATABASE_URL environment variable not found. Cannot connect to PostgreSQL.")
    exit(1)
else:
    logging.info("Successfully Connected to PostgreSQL.")

# Thresholds for stock change alerts (default to 5% per guild)
alert_thresholds = {}

# Helper: Get reusable database connection
def get_db_connection(retries=3, delay=2):
    for attempt in range(retries):
        try:
            conn = psycopg2.connect(DATABASE_URL, sslmode='require', cursor_factory=DictCursor)
            return conn
        except psycopg2.OperationalError as e:
            logging.warning(f"Database connection failed (attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(delay)
    logging.error("Failed to connect to the database after retries.")
    raise Exception("Database connection failed.")


# Initialize the database
def initialize_db():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Create the stocks table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS stocks (
                        guild_id BIGINT,
                        user_id BIGINT,
                        symbol TEXT,
                        last_price FLOAT,
                        PRIMARY KEY (guild_id, user_id, symbol)
                    )
                """)
                logging.info("Stocks table checked/created.")
                
                # Create the API usage table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS api_usage (
                        request_count INTEGER,
                        reset_date TIMESTAMP
                    )
                """)
                logging.info("API usage table checked/created.")
                
                # Create the settings table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS settings (
                        guild_id BIGINT PRIMARY KEY,
                        update_channel_id BIGINT
                    )
                """)
                logging.info("Settings table checked/created.")
                
                # Create leaderboard table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS leaderboard (
                        date DATE,
                        user_id BIGINT,
                        username TEXT,
                        guild_id BIGINT,
                        score FLOAT,
                        PRIMARY KEY (date, user_id, guild_id)
                    )
                """)
                logging.info("Leaderboard table checked/created.")

                # Initialize API usage if missing
                cursor.execute("SELECT COUNT(*) FROM api_usage")
                if cursor.fetchone()[0] == 0:
                    cursor.execute(
                        "INSERT INTO api_usage (request_count, reset_date) VALUES (%s, %s)",
                        (0, next_reset_date())
                    )
                logging.info("API usage initialized.")
                    
                # Create thresholds table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS thresholds (
                    user_id BIGINT,
                    guild_id BIGINT,
                    threshold FLOAT,
                    PRIMARY KEY (user_id, guild_id)
                )
            """)
                logging.info("Thresholds table checked/created.")
                
                conn.commit()
                
    except Exception as e:
        logging.exception("Database initialization failed.")




# Calculate next reset date for API requests
def next_reset_date():
    now = datetime.now()
    next_month = (now.month % 12) + 1
    year = now.year if next_month > 1 else now.year + 1
    return datetime(year, next_month, 1).strftime("%Y-%m-%d %H:%M:%S")


# Update API usage in the database
def update_request_count():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT request_count, reset_date FROM api_usage")
        current_count, reset_date = cursor.fetchone()
        if isinstance(reset_date, str):
            reset_date = datetime.strptime(reset_date, "%Y-%m-%d %H:%M:%S")


        if datetime.now() >= reset_date:
            current_count = 0
            reset_date = next_reset_date()
            cursor.execute(
                "UPDATE api_usage SET request_count = %s, reset_date = %s",
                (current_count, reset_date.strftime("%Y-%m-%d %H:%M:%S"))
            )
        current_count += 1
        cursor.execute("UPDATE api_usage SET request_count = %s", (current_count,))
        conn.commit()

def get_request_count():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT request_count, reset_date FROM api_usage")
        return cursor.fetchone()


def load_stocks(guild_id, user_id):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT symbol, last_price FROM stocks WHERE guild_id = %s AND user_id = %s", (guild_id, user_id))
            return {row["symbol"]: row["last_price"] for row in cursor.fetchall()}




def save_stock(guild_id, user_id, symbol, last_price=None):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO stocks (guild_id, user_id, symbol, last_price) VALUES (%s, %s, %s, %s) "
                "ON CONFLICT (guild_id, user_id, symbol) DO UPDATE SET last_price = EXCLUDED.last_price",
                (guild_id, user_id, symbol, last_price)
            )
            conn.commit()

        
        
def remove_stock(guild_id, user_id, symbol):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM stocks WHERE guild_id = %s AND user_id = %s AND symbol = %s",
                (guild_id, user_id, symbol)
            )
            conn.commit()

        
def set_update_channel(guild_id, channel_id):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO settings (guild_id, update_channel_id) VALUES (%s, %s) "
                "ON CONFLICT (guild_id) DO UPDATE SET update_channel_id = EXCLUDED.update_channel_id",
                (guild_id, channel_id)
            )
            conn.commit()


def get_update_channel(guild_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT update_channel_id FROM settings WHERE guild_id = %s", (guild_id,))
        row = cursor.fetchone()
        return row["update_channel_id"] if row else None
    
def shutdown_handler(signum, frame):
    logging.info(f"Received signal {signum}. Initiating shutdown...")
    loop = asyncio.get_event_loop()
    asyncio.create_task(client.close())
    loop.stop()
    
def calculate_daily_performance():
    logging.info(f"Calculating daily performance for leaderboard.")
    today = datetime.now().date()
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Fetch distinct users and their stocks
        cursor.execute("SELECT DISTINCT user_id, guild_id FROM stocks")
        users = cursor.fetchall()

        leaderboard_updates = []

        for user in users:
            logging.info(f"Fetching {user}")
            user_id, guild_id = user
            cursor.execute("""
                SELECT symbol, last_price FROM stocks 
                WHERE user_id = %s AND guild_id = %s
            """, (user_id, guild_id))

            stocks = cursor.fetchall()
            total_percent_change = 0
            count = 0

            for stock in stocks:
                logging.info(f"Parsing {user}'s Watchlist")
                symbol, last_price = stock
                current_price = asyncio.run(fetch_stock_price(symbol))

                if current_price and last_price:
                    percent_change = ((current_price - last_price) / last_price) * 100
                    total_percent_change += percent_change
                    count += 1

            # Calculate average percentage change for the user
            if count > 0:
                avg_percent_change = total_percent_change / count
                cursor.execute("SELECT username FROM users WHERE user_id = %s", (user_id,))
                username = cursor.fetchone()
                leaderboard_updates.append((today, user_id, username, guild_id, avg_percent_change))

        # Insert updates into the leaderboard table
        for update in leaderboard_updates:
            cursor.execute("""
                INSERT INTO leaderboard (date, user_id, username, guild_id, score)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (date, user_id, guild_id) DO UPDATE
                SET score = EXCLUDED.score
            """, update)

        conn.commit()
        logging.info(f"Calculation complete.")

def check_rank(user_id, guild_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT RANK() OVER (ORDER BY score DESC) AS rank
                FROM leaderboard
                WHERE date = %s AND guild_id = %s AND user_id = %s
            """, (datetime.now().date(), guild_id, user_id))
            result = cursor.fetchone()
            return result["rank"] if result else None
    except Exception as e:
        logging.exception(f"Unable to fetch ranking for user {user_id} in guild {guild_id}.")
        return None

async def update_leaderboard():
    await client.wait_until_ready()
    while not client.is_closed():
        now = datetime.now()
        # Run at 4:00 PM daily (market close)
        if now.hour == 16 and now.minute == 0:
            logging.info("Updating leaderboard...")
            calculate_daily_performance()
            logging.info("Leaderboard updated.")
        await asyncio.sleep(1800)  # Check every 30 minutes

async def shutdown():
    await client.close()
    tasks = [task for task in asyncio.all_tasks() if task is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks, return_exceptions=True)

@client.event
async def on_ready():
    logging.info(f"Logged in as {client.user}")
    
        # Fetch all guilds where the bot is a member
    guilds = client.guilds

    for guild in guilds:
        try:
            # Fetch the update channel for this guild
            update_channel_id = get_update_channel(guild.id)

            if update_channel_id:
                # Get the channel object
                channel = client.get_channel(update_channel_id)

                if channel:
                    await channel.send(update_message)
                    logging.info(f"Sent update summary to {guild.name} in channel {channel.name}")
                else:
                    logging.warning(f"Channel ID {update_channel_id} not found for guild {guild.name}")
            else:
                logging.info(f"No update channel set for guild {guild.name}")

        except Exception as e:
            logging.exception(f"Failed to send update message for guild {guild.name}: {e}")

    asyncio.create_task(monitor_stock_changes())
    asyncio.create_task(update_leaderboard())

@client.event
async def on_message(message):
    global request_count

    if message.author == client.user:
        return

    user_id = message.author.id # Unique ID for the user
    guild_id = message.guild.id  # Unique ID for the server

    if message.content.startswith("!help"):
        help_message = (
            "``` Stock Bot Commands ```\n"
            "1. **!addstock SYMBOL** - Adds a stock to your personal tracking list (e.g., `!addstock AAPL`).\n\n"
            "2. **!addstocks SYMBOL1 SYMBOL2 ...** - Adds multiple stocks to your personal tracking list at once (e.g., `!addstocks AAPL TSLA AMZN`).\n\n"
            "3. **!removestock SYMBOL** - Removes a stock from your personal tracking list (e.g., `!removestock TSLA`).\n\n"
            "4. **!watchlist** - Displays your current stock watchlist with the latest prices.\n\n"
            "5. **!requests** - Shows how many API requests have been used out of the monthly limit.\n\n"
            "6. **!price SYMBOL** - Shows the current price of a specific stock (e.g., `!price TSLA`).\n\n"
            "7. **!set PERCENTAGE** - Sets the percentage threshold for stock change alerts (e.g., `!setthreshold 10`).\n\n"
            "8. **!setchannel** - Sets the current channel as the default for stock update notifications.\n\n"
            "9. **!leaderboard** - Displays the leaderboard for today, showing users with the best-performing watchlists.\n\n"
            "10. **!69** - Gives you a nice compliment.\n\n"
            "11. **!imbored** - For when you're bored.\n\n"
            "12. **!help** - Displays this help message.\n\n"
            "```Once a stock is added to your watchlist, the bot will monitor its price. Daily performance is tracked, and the leaderboard is updated at market close.```"
        )
        await message.channel.send(help_message)
        logging.info(f"HELP command received from {message.author}: {message.content}")
        return
    
    if message.content.startswith("!restart"):
        logging.info(f"Restart command received from {message.author}")
        if not HEROKU_API_KEY or not HEROKU_APP_NAME:
            logging.info(f"Heroku API key or app name not configured - {message.author}: {message.content}")
            await message.channel.send("Heroku API key or app name not configured.")
            return

        url = f"https://api.heroku.com/apps/{HEROKU_APP_NAME}/dynos"
        headers = {
            "Authorization": f"Bearer {HEROKU_API_KEY}",
            "Accept": "application/vnd.heroku+json; version=3"
        }

        response = requests.delete(url, headers=headers)
        if response.status_code == 202:
            logging.info(f"Bot Restart command successful from {message.author}: {message.content}")
            await message.channel.send("Bot is restarting...")
        else:
            logging.info(f"Bot Restart command FAILED from {message.author}: {message.content}")
            await message.channel.send(f"Failed to restart: {response.status_code} - {response.text}")

    if message.content.startswith("!addstocks"):
        logging.info(f"Command received from {message.author}: {message.content}")
        parts = message.content.split()[1:]
        if not parts:
            await message.channel.send("Usage: !addstocks SYMBOL1 SYMBOL2 ...")
            return

        added_stocks = []
        invalid_stocks = []

        for stock_symbol in parts:
            stock_symbol = stock_symbol.upper()
            current_price = await fetch_stock_price(stock_symbol)

            if current_price is None:
                invalid_stocks.append(stock_symbol)
            else:
                save_stock(guild_id, user_id, stock_symbol, current_price)
                added_stocks.append(stock_symbol)

        if added_stocks:
            logging.info(f"{message.author} added to watchlist {', '.join(added_stocks)}")
            await message.channel.send(f"{message.author.mention} added ```{', '.join(added_stocks)}``` to their watchlist.")
        if invalid_stocks:
            logging.info(f"{message.author} FAILED to add INVALID stocks to watchlist: {', '.join(invalid_stocks)}")
            await message.channel.send(f"Invalid symbols: {', '.join(invalid_stocks)}")

    if message.content.startswith("!setchannel"):
        logging.info(f"Command received from {message.author}: {message.content}")
        set_update_channel(guild_id, message.channel.id)
        logging.info(f"{message.author} set active bot channel to {guild_id, message.channel.id}")
        await message.channel.send(f"Updates will be sent to this channel: {message.channel.mention}")

    if message.content.startswith("!set"):
        logging.info(f"Command received from {message.author}: {message.content}")
        parts = message.content.split()
        if len(parts) < 2 or not parts[1].isdigit():
            await message.channel.send("Usage: `!set PERCENTAGE` (e.g., `!set 10`).")
            return

        threshold = float(parts[1])

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO thresholds (user_id, guild_id, threshold)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, guild_id) DO UPDATE SET threshold = EXCLUDED.threshold
            """, (user_id, guild_id, threshold))
            conn.commit()

        logging.info(f"Threshold set to {threshold}% for user {message.author} in guild {guild_id}.")
        await message.channel.send(f"{message.author.mention} set his watchlist notification threshold to {threshold}%.")


    if message.content.startswith("!addstock"):
        logging.info(f"Command received from {message.author}: {message.content}")
        parts = message.content.split()
        if len(parts) < 2:
            logging.info(f"{message.author} FAILED to use addstock: {message.content}")
            await message.channel.send("Usage: !addstock SYMBOL")
            return

        stock_symbol = parts[1].upper()
        current_price = await fetch_stock_price(stock_symbol)
        if current_price is None or current_price == 0:
            logging.info(f"{message.author} tried to add an INVALID stock to watchlist: {message.content}")
            await message.channel.send(f"Hey {message.author.mention}, womp womp:\n{stock_symbol} is not a valid stock.\nMake sure the stock is available on NASDAQ\nIf you need additional support go here: https://www.dummies.com/category/books/reading-33710/")
            return

        tracked_stocks = load_stocks(guild_id, user_id)
        if stock_symbol not in tracked_stocks:
            user_id = message.author.id
            save_stock(guild_id, user_id, stock_symbol, current_price)
            logging.info(f"{message.author} successfully added {stock_symbol} to watchlist")
            await message.channel.send(f"{message.author.mention} added {stock_symbol} to their watchlist.")
        else:
            await message.channel.send(f"Hey {message.author.mention}, {stock_symbol} is already being tracked on your watchlist.")

    if message.content.startswith("!price"):
        logging.info(f"Command received from {message.author}: {message.content}")
        parts = message.content.split()
        if len(parts) < 2:
            logging.info(f"{message.author} FAILED to use price check: {message.content}")
            await message.channel.send("Usage: !price SYMBOL")
            return

        stock_symbol = parts[1].upper()

        # Fetch stock price
        stock_price = await fetch_stock_price(stock_symbol)

        if stock_price is not None:
            logging.info(f"{message.author} successfully checked the price of {stock_symbol}")
            await message.channel.send(f"The current price of {stock_symbol} is ${stock_price:.2f}.")
        else:
            logging.info(f"{message.author} tried to check the price of an INVALID stock: {stock_symbol}")
            await message.channel.send(f"Hey {message.author.mention}, womp womp:\n{stock_symbol} is not a valid stock.\nMake sure the stock is available on NASDAQ\nIf you need additional support go here: https://www.dummies.com/category/books/reading-33710/")

    if message.content.startswith("!69"):
        logging.info(f"{message.author} asked for a compliment")
        compliment = await get_random_compliment()
        await message.channel.send(f"{message.author.mention} {compliment}")

    if message.content.startswith("!removestock"):
        logging.info(f"Command received from {message.author}: {message.content}")
        parts = message.content.split()
        if len(parts) < 2:
            logging.info(f"{message.author} FAILED to use remove stock: {message.content}")
            await message.channel.send("Usage: !removestock SYMBOL")
            return

        stock_symbol = parts[1].upper()
        tracked_stocks = load_stocks(guild_id, user_id)

        if stock_symbol in tracked_stocks:
            remove_stock(guild_id, user_id, stock_symbol)
            logging.info(f"{message.author} successfully removed {stock_symbol} from watchlist")
            await message.channel.send(f"{message.author.mention} removed {stock_symbol} from their watchlist.")
        else:
            logging.info(f"{message.author} tried to remove an INVALID stock: {message.content}")
            await message.channel.send(f"{stock_symbol} is not on your watchlist.")

    if message.content.startswith("!watchlist"):
        logging.info(f"Command received from {message.author}: {message.content}")

        try:
            tracked_stocks = load_stocks(guild_id, user_id)  # Pass both guild_id and user_id
            if not tracked_stocks:
                logging.info(f"{message.author} tried to check an EMPTY watchlist")
                await message.channel.send(f"Hey {message.author.mention}, your watchlist is empty.\nTry using ```!addstock SYMBOL``` or ```!addstocks SYMBOL SYMBOL ...```")
            else:
                watchlist_lines = []
                for symbol, last_price in tracked_stocks.items():
                    current_price = await fetch_stock_price(symbol)
                    if current_price is not None:
                        logging.info(f"WATCHLIST REQUEST: Checked price for {symbol}")
                        watchlist_lines.append(f"{symbol}: ${current_price:.2f}")
                    else:
                        logging.info(f"WATCHLIST REQUEST FAILED: Couldn't fetch price for {symbol}")
                        watchlist_lines.append(f"{symbol}: Unable to fetch current price.")
                
                user_rank = check_rank(user_id, guild_id)
                rank_message = f"{message.author}'s current leaderboard ranking: {user_rank}" if user_rank else "You are not currently ranked."
                watchlist = "\n".join(watchlist_lines)
                logging.info(f"{message.author} checked their watchlist")
                await message.channel.send(f"{message.author.mention}'s watchlist:\n```\n{watchlist}\n```\n{rank_message}")
        except Exception as e:
            logging.exception("Error fetching watchlist")
            await message.channel.send("An error occurred while fetching your watchlist. Please try again later.")

    if message.content.startswith("!imbored"):
        logging.info(f"{message.author} is bored...")
        async with aiohttp.ClientSession() as session:
            async with session.get("https://uselessfacts.jsph.pl/random.json?language=en") as response:
                if response.status == 200:
                    data = await response.json()
                    activity = data.get("text", "Couldn't fetch a fun fact.")
                else:
                    activity = "Too bad."
        await message.channel.send(activity)
    
    if message.content.startswith("!requests"):
        current_count, reset_date = get_request_count()
        logging.info(f"{message.author} checked API request limit")
        await message.channel.send(f"API requests used: {current_count}/{MONTHLY_LIMIT}\nResets on: {reset_date}")

    if message.content.startswith("!leaderboard"):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT username, score FROM leaderboard
                WHERE date = %s AND guild_id = %s
                ORDER BY score DESC LIMIT 10
            """, (datetime.now().date(), message.guild.id))

            leaderboard = cursor.fetchall()
            if leaderboard:
                result = "\n".join([f"{i+1}. {row['username']}: {row['score']:.2f}%" for i, row in enumerate(leaderboard)])
                await message.channel.send(f"**Today's Leaderboard:**\n{result}")
            else:
                await message.channel.send("No leaderboard data available for today. Please wait 24hrs for results to populate.")


async def get_random_compliment():
    compliments = [
    "You make things better just by being here!",
    "Your energy is infectious!",
    "You always bring the best vibes.",
    "You have an amazing perspective.",
    "Your ideas are always so thoughtful.",
    "You’re a true problem-solver!",
    "You handle challenges with grace.",
    "You make a difference every single day.",
    "Your support means so much.",
    "You’re an inspiration to everyone around you.",
    "You’ve got a heart of gold.",
    "You light up the room with your presence.",
    "Your kindness is contagious.",
    "You’re braver than you think.",
    "You always know the right thing to say.",
    "You’ve got an amazing sense of humor!",
    "Your creativity knows no bounds.",
    "You’re always so helpful.",
    "You make people feel heard and valued.",
    "Your positivity is magnetic.",
    "You’re a fantastic listener.",
    "You’ve got a brilliant mind.",
    "Your passion is inspiring.",
    "You bring out the best in others.",
    "You’re so dependable and trustworthy.",
    "You’re a joy to be around.",
    "Your work ethic is unmatched.",
    "You’re always learning and growing.",
    "You’ve got a knack for solving tough problems.",
    "You have a great eye for detail.",
    "You’re a beacon of hope and positivity.",
    "You inspire others to do better.",
    "Your dedication is remarkable.",
    "You have a contagious enthusiasm.",
    "Your laughter is the best sound.",
    "You’re great at making people feel special.",
    "You’re always willing to lend a hand.",
    "You’ve got a wonderful perspective on life.",
    "Your courage is admirable.",
    "You’re an excellent role model.",
    "Your smile brightens the day.",
    "You’re incredibly thoughtful.",
    "You make hard things look easy.",
    "Your honesty is refreshing.",
    "You bring so much joy to this space.",
    "You’re incredibly talented.",
    "You’ve got a way of making things fun.",
    "Your determination is inspiring.",
    "You’re so easy to talk to.",
    "You always make people feel welcome.",
    "You’re genuinely one of a kind.",
    "You’re great at turning ideas into reality.",
    "Your insights are always so valuable.",
    "You make complicated things seem simple.",
    "You’re so open-minded and understanding.",
    "Your presence makes a difference.",
    "You’re an awesome team player.",
    "You’ve got an incredible sense of humor.",
    "Your hard work doesn’t go unnoticed.",
    "You have a calming presence.",
    "You’re amazing just as you are.",
    "You’re so full of good ideas.",
    "You have a way of seeing the best in people.",
    "You’re someone people can always count on.",
    "You’re a natural leader.",
    "You make the world brighter.",
    "You’re so quick-witted!",
    "You’ve got the best attitude.",
    "Your confidence is inspiring.",
    "You’re a force of nature in the best way.",
    "Your perspective is always appreciated.",
    "You make people feel comfortable and safe.",
    "You’re incredibly wise.",
    "Your enthusiasm is energizing.",
    "You’ve got a great sense of humor.",
    "You’re amazing at finding solutions.",
    "You’re a real go-getter.",
    "You make this community better.",
    "You’re so compassionate.",
    "You’ve got a real gift for understanding people.",
    "You always find the silver lining.",
    "You’re one of the most genuine people around.",
    "You have a fantastic work ethic.",
    "You’re so patient and kind.",
    "Your contributions are invaluable.",
    "You’re great at making people laugh.",
    "Your optimism is infectious.",
    "You always find a way to make it work.",
    "You bring out the best in those around you.",
    "You’re a true original.",
    "You’re so thoughtful and considerate.",
    "You always show up when it matters.",
    "You make people feel included.",
    "You’ve got an incredible amount of talent.",
    "You’re an amazing problem-solver.",
    "You’re so supportive and uplifting.",
    "Your encouragement means the world to others.",
    "You make even tough days better.",
    "You're doing amazing!",
    "Your effort truly shows!",
    "Keep up the great work!",
    "You're a valuable member of this community.",
    "Your positivity is inspiring!",
    "You're making a difference.",
    "You have a fantastic attitude!",
    "You're stronger than you think.",
    "Your creativity is awesome!",
    "You're a great listener.",
    "You brighten up this space!",
    "Your hard work pays off.",
    "You're appreciated more than you know.",
    "Your kindness is contagious!",
    "You're a joy to be around.",
    "You have a wonderful sense of humor.",
    "You're crushing it!",
    "You’re capable of amazing things.",
    "Your dedication is inspiring.",
    "You're making progress every day."
]
    return random.choice(compliments)
    
# Fetch stock price with retry logic
async def fetch_stock_price(symbol, retries=3, delay=2):
    for attempt in range(retries):
        try:
            update_request_count()
            response = requests.get(STOCK_API_URL.format(symbol=symbol, apikey=FINNHUB_API_KEY), timeout=10)
            response.raise_for_status()
            data = response.json()

            # Log the API response for debugging
            logging.info(f"API response for {symbol}: {data}")

            # Validate the response based on the API's behavior
            if data.get("c", 0) > 0:  # "c" is the current price
                return data["c"]
            else:
                logging.warning(f"Invalid stock symbol: {symbol}. API returned: {data}")
                return None  # Invalid stock symbol
        except requests.exceptions.RequestException as e:
            logging.warning(f"Request error for {symbol} (attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                await asyncio.sleep(delay)
        except Exception as e:
            logging.exception(f"Unexpected error for {symbol}: {e}")
            return None
    return None


    
# Monitor stock changes
async def monitor_stock_changes():
    await client.wait_until_ready()
    while not client.is_closed():
        logging.debug("Starting stock monitoring iteration.")
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT guild_id FROM stocks")
                guild_ids = [row["guild_id"] for row in cursor.fetchall()]

                for guild_id in guild_ids:
                    channel_id = get_update_channel(guild_id)
                    if not channel_id:
                        logging.debug(f"Skipping guild {guild_id}: No update channel set.")
                        continue

                    channel = client.get_channel(channel_id)
                    if not channel:
                        continue

                    # Fetch distinct users for the guild
                    cursor.execute("SELECT DISTINCT user_id FROM stocks WHERE guild_id = %s", (guild_id,))
                    user_ids = [row["user_id"] for row in cursor.fetchall()]

                    for user_id in user_ids:
                        # Fetch user's threshold
                        cursor.execute("""
                            SELECT threshold FROM thresholds 
                            WHERE user_id = %s AND guild_id = %s
                        """, (user_id, guild_id))
                        threshold_row = cursor.fetchone()
                        threshold = threshold_row["threshold"] if threshold_row else 5  # Default 5%

                        cursor.execute("""
                            SELECT symbol, last_price FROM stocks 
                            WHERE guild_id = %s AND user_id = %s
                        """, (guild_id, user_id))
                        stocks = cursor.fetchall()

                        for row in stocks:
                            symbol = row["symbol"]
                            last_price = row["last_price"]
                            current_price = await fetch_stock_price(symbol)

                            if current_price and last_price:
                                percent_change = ((current_price - last_price) / last_price) * 100
                                if abs(percent_change) >= threshold:
                                    logging.info(f"Stock alert triggered for {symbol}: {percent_change:.2f}% change.")
                                    await channel.send(
                                        f"⚠️ Stock Alert for <@{user_id}>! {symbol} changed by {percent_change:.2f}% "
                                        f"and is now ${current_price:.2f}."
                                    )

                                # Update the last known price in the database
                                cursor.execute(
                                    "UPDATE stocks SET last_price = %s WHERE guild_id = %s AND user_id = %s AND symbol = %s",
                                    (current_price, guild_id, user_id, symbol)
                                )
                        conn.commit()
        except Exception as e:
            logging.exception("Error in monitor_stock_changes loop")
        await asyncio.sleep(1800)
        logging.debug("Sleeping for 1800 seconds before next iteration.")
        
async def main(token):
    async with client:
        await client.start(token)

# Main Script
token = os.getenv('TOKEN')
if not token:
    logging.error("TOKEN environment variable not found. Bot cannot start.")
    exit(1)

if __name__ == "__main__":
    initialize_db()
    # Register signal handlers
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)
    asyncio.run(main(token))