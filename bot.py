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

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log", mode='a'),
        logging.StreamHandler(sys.stdout)
    ]
)

logging.info("Bot has started.")

# Heroku API Key (For User Restarts)
HEROKU_API_KEY = heroku_api_key = os.getenv("HEROKU_API_KEY")
HEROKU_APP_NAME = heroku_app_name = os.getenv("HEROKU_APP_NAME")


# Discord client setup
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Finnhub API Key
FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')
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
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            # Create the stocks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stocks (
                    guild_id BIGINT,
                    symbol TEXT,
                    last_price FLOAT,
                    PRIMARY KEY (guild_id, symbol)
                )
            """)

            # Create the API usage table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_usage (
                    request_count INTEGER,
                    reset_date TIMESTAMP
                )
            """)

            # Create the settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    guild_id BIGINT PRIMARY KEY,
                    update_channel_id BIGINT
                )
            """)

            # Initialize API usage if missing
            cursor.execute("SELECT COUNT(*) FROM api_usage")
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    "INSERT INTO api_usage (request_count, reset_date) VALUES (%s, %s)",
                    (0, next_reset_date())
                )
            conn.commit()




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
        cursor.execute("UPDATE api_usage SET request_count = ?", (current_count,))
        conn.commit()

def get_request_count():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT request_count, reset_date FROM api_usage")
        return cursor.fetchone()


def load_stocks(guild_id):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT symbol, last_price FROM stocks WHERE guild_id = %s", (guild_id,))
            return {row["symbol"]: row["last_price"] for row in cursor.fetchall()}




def save_stock(guild_id, symbol, last_price=None):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO stocks (guild_id, symbol, last_price) VALUES (%s, %s, %s) "
                "ON CONFLICT (guild_id, symbol) DO UPDATE SET last_price = EXCLUDED.last_price",
                (guild_id, symbol, last_price)
            )
            conn.commit()

        
        
def remove_stock(guild_id, symbol):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM stocks WHERE guild_id = %s AND symbol = %s", (guild_id, symbol))
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
    logging.info("Shutting down gracefully...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(client.close())
    loop.stop()
    
async def shutdown():
    await client.close()
    tasks = [task for task in asyncio.all_tasks() if task is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks, return_exceptions=True)

@client.event
async def on_ready():
    logging.info(f"Logged in as {client.user}")
    asyncio.create_task(monitor_stock_changes())

@client.event
async def on_message(message):
    global request_count

    if message.author == client.user:
        return

    guild_id = message.guild.id  # Unique ID for the server

    if message.content.startswith("!help"):
        help_message = (
            "**Stock Bot Commands**:\n"
            "1. **!addstock SYMBOL** - Adds a stock to the tracking list for this server (e.g., `!addstock AAPL`).\n"
            "2. **!addstocks SYMBOL1 SYMBOL2 ...** - Adds multiple stocks to the tracking list at once (e.g., `!addstocks AAPL TSLA AMZN`).\n"
            "3. **!removestock SYMBOL** - Removes a stock from the tracking list for this server (e.g., `!removestock TSLA`).\n"
            "4. **!watchlist** - Displays the current stock watchlist for this server.\n"
            "5. **!requests** - Shows how many API requests have been used out of the monthly limit.\n"
            "6. **!price SYMBOL** - Shows the current price of requested stock.\n"
            "7. **!setthreshold PERCENTAGE** - Set the percentage threshold for stock change alerts (e.g., `!setthreshold 10`).\n"
            "8. **!forcecheck** - Force check stock prices in the watchlist and notify of changes.\n"
            "9. **!setchannel** - Sets the current channel as the default for stock update notifications.\n"
            "10. **!69** - Gives you a nice compliment.\n"
            "11. **!help** - Displays this help message.\n\n"
            "Once a stock is added, the bot will monitor its price and notify if significant changes occur in the designated channel."
        )
        await message.channel.send(help_message)
        return
    
    if message.content.startswith("!restart"):
        logging.info(f"Restart command received from {message.author}")
        if not HEROKU_API_KEY or not HEROKU_APP_NAME:
            await message.channel.send("Heroku API key or app name not configured.")
            return

        url = f"https://api.heroku.com/apps/{HEROKU_APP_NAME}/dynos"
        headers = {
            "Authorization": f"Bearer {HEROKU_API_KEY}",
            "Accept": "application/vnd.heroku+json; version=3"
        }

        response = requests.delete(url, headers=headers)
        if response.status_code == 202:
            await message.channel.send("Bot is restarting...")
        else:
            await message.channel.send(f"Failed to restart: {response.status_code} - {response.text}")

    if message.content.startswith("!addstocks"):
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
                save_stock(guild_id, stock_symbol, current_price)
                added_stocks.append(stock_symbol)

        if added_stocks:
            await message.channel.send(f"Added to watchlist: {', '.join(added_stocks)}")
        if invalid_stocks:
            await message.channel.send(f"Invalid symbols: {', '.join(invalid_stocks)}")

    if message.content.startswith("!setchannel"):
        set_update_channel(guild_id, message.channel.id)
        await message.channel.send(f"Updates will be sent to this channel: {message.channel.mention}")


    if message.content.startswith("!forcecheck"):
        tracked_stocks = load_stocks(guild_id)
        if not tracked_stocks:
            await message.channel.send("The stock watchlist for this server is empty.")
            return

        results = []
        for symbol, last_price in tracked_stocks.items():
            current_price = await fetch_stock_price(symbol)
            if current_price is None:
                results.append(f"{symbol}: Unable to fetch current price.")
                continue

            if last_price:
                price_change = current_price - last_price
                percent_change = (price_change / last_price) * 100
                direction = "up" if price_change > 0 else "down"
                results.append(
                    f"{symbol}: {direction} {abs(percent_change):.2f}% - ${abs(price_change):.2f}"
                )
            else:
                results.append(f"{symbol}: No previous price to compare.")

        if results:
            await message.channel.send("**Force Check Results:**\n" + "\n".join(results))
        else:
            await message.channel.send("No stocks found to check.")
        return

    if message.content.startswith("!setthreshold"):
        parts = message.content.split()
        if len(parts) < 2 or not parts[1].isdigit():
            await message.channel.send("Usage: !setthreshold PERCENTAGE (e.g., !setthreshold 10)")
            return

        threshold = int(parts[1])
        alert_thresholds[guild_id] = threshold
        await message.channel.send(f"Threshold for stock change alerts set to {threshold}% for this server.")

    if message.content.startswith("!addstock"):
        parts = message.content.split()
        if len(parts) < 2:
            await message.channel.send("Usage: !addstock SYMBOL")
            return

        stock_symbol = parts[1].upper()
        current_price = await fetch_stock_price(stock_symbol)
        if current_price is None or current_price == 0:
            await message.channel.send(f"Hey retard,\n{stock_symbol} is not a valid stock:/\nPlease use your brain and try again.")
            return

        tracked_stocks = load_stocks(guild_id)
        if stock_symbol not in tracked_stocks:
            save_stock(guild_id, stock_symbol, current_price)
            await message.channel.send(f"Added {stock_symbol} to the tracking list for this server.")
        else:
            await message.channel.send(f"{stock_symbol} is already being tracked for this server.")

    
    if message.content.startswith("!price"):
        parts = message.content.split()
        if len(parts) < 2:
            await message.channel.send("Usage: !price SYMBOL")
            return

        stock_symbol = parts[1].upper()

        # Fetch stock price
        stock_price = await fetch_stock_price(stock_symbol)

        if stock_price is not None:
            await message.channel.send(f"The current price of {stock_symbol} is ${stock_price:.2f}.")
        else:
            await message.channel.send(f"Hey retard,\n{stock_symbol} is not a valid stock:/\nPlease use your brain and try again.")

    if message.content.startswith("!69"):
        compliment = await get_random_compliment()
        await message.channel.send(f"{message.author.mention} {compliment}")

    if message.content.startswith("!removestock"):
        parts = message.content.split()
        if len(parts) < 2:
            await message.channel.send("Usage: !removestock SYMBOL")
            return

        stock_symbol = parts[1].upper()
        tracked_stocks = load_stocks(guild_id)

        if stock_symbol in tracked_stocks:
            remove_stock(guild_id, stock_symbol)
            await message.channel.send(f"Removed {stock_symbol} from the tracking list for this server.")
        else:
            await message.channel.send(f"{stock_symbol} is not being tracked for this server.")

    if message.content.startswith("!watchlist"):
        tracked_stocks = load_stocks(guild_id)
        if not tracked_stocks:
            await message.channel.send("The stock watchlist for this server is empty.")
        else:
            watchlist = "\n".join(tracked_stocks.keys())
            await message.channel.send(f"Current stock watchlist for this server:\n```\n{watchlist}\n```")

    if message.content.startswith("!requests"):
        current_count, reset_date = get_request_count()
        await message.channel.send(f"API requests used: {current_count}/{MONTHLY_LIMIT}\nResets on: {reset_date}")

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
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT guild_id FROM stocks")
                guild_ids = [row["guild_id"] for row in cursor.fetchall()]

                for guild_id in guild_ids:
                    channel_id = get_update_channel(guild_id)
                    if not channel_id:
                        continue

                    channel = client.get_channel(channel_id)
                    if not channel:
                        continue

                    cursor.execute("SELECT symbol, last_price FROM stocks WHERE guild_id = %s", (guild_id,))
                    stocks = cursor.fetchall()

                    for row in stocks:
                        symbol = row["symbol"]
                        last_price = row["last_price"]
                        current_price = await fetch_stock_price(symbol)

                        if current_price and last_price:
                            percent_change = ((current_price - last_price) / last_price) * 100
                            if abs(percent_change) >= 5:
                                await channel.send(
                                    f"⚠️ Stock Alert! {symbol} changed by {percent_change:.2f}% "
                                    f"and is now ${current_price:.2f}."
                                )

                        cursor.execute(
                        "UPDATE stocks SET last_price = %s WHERE guild_id = %s AND symbol = %s",
                        (current_price, guild_id, symbol)
                    )
                        conn.commit()
        except Exception as e:
            logging.exception("Error in monitor_stock_changes loop")
        await asyncio.sleep(1800)
        
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