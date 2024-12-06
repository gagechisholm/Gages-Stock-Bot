import discord
import os
import asyncio
import requests
import logging
import sqlite3
from datetime import datetime

# Configure logging
logging.basicConfig(filename="app.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

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

# Initialize the database
def initialize_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stocks (
                guild_id INTEGER,
                symbol TEXT,
                last_price REAL,
                PRIMARY KEY (guild_id, symbol)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_usage (
                request_count INTEGER,
                reset_date TEXT
            )
        """)
        conn.commit()

        # Initialize API usage if it doesn't exist
        cursor.execute("SELECT COUNT(*) FROM api_usage")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO api_usage (request_count, reset_date) VALUES (?, ?)", (0, next_reset_date()))
            conn.commit()

def next_reset_date():
    """Calculate the next reset date for API requests (1st of next month at midnight)."""
    now = datetime.now()
    next_month = (now.month % 12) + 1
    year = now.year if next_month > 1 else now.year + 1
    return datetime(year, next_month, 1).strftime("%Y-%m-%d %H:%M:%S")

# Update API usage in the database
def update_request_count():
    global request_count
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        # Check if we need to reset the count
        cursor.execute("SELECT request_count, reset_date FROM api_usage")
        current_count, reset_date = cursor.fetchone()
        reset_date = datetime.strptime(reset_date, "%Y-%m-%d %H:%M:%S")
        if datetime.now() >= reset_date:
            current_count = 0
            reset_date = next_reset_date()
            cursor.execute("UPDATE api_usage SET request_count = ?, reset_date = ?", (current_count, reset_date.strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()

        # Increment the request count
        current_count += 1
        request_count = current_count
        cursor.execute("UPDATE api_usage SET request_count = ?", (current_count,))
        conn.commit()

def get_request_count():
    """Retrieve the current request count and reset date."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT request_count, reset_date FROM api_usage")
        return cursor.fetchone()

def load_stocks(guild_id):
    """Load stocks for a specific guild."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT symbol, last_price FROM stocks WHERE guild_id = ?", (guild_id,))
        return {row[0]: row[1] for row in cursor.fetchall()}

def save_stock(guild_id, symbol, last_price=None):
    """Save a stock for a specific guild."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO stocks (guild_id, symbol, last_price)
            VALUES (?, ?, ?)
        """, (guild_id, symbol, last_price))
        conn.commit()

def remove_stock(guild_id, symbol):
    """Remove a stock for a specific guild."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM stocks WHERE guild_id = ? AND symbol = ?", (guild_id, symbol))
        conn.commit()

@client.event
async def on_ready():
    logging.info(f"We have logged in as {client.user}")
    initialize_db()
    logging.info("Database initialized")

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
            "2. **!removestock SYMBOL** - Removes a stock from the tracking list for this server (e.g., `!removestock TSLA`).\n"
            "3. **!watchlist** - Displays the current stock watchlist for this server.\n"
            "4. **!requests** - Shows how many API requests have been used out of the monthly limit.\n"
            "5. **!help** - Displays this help message.\n\n"
            "Once a stock is added, the bot will monitor its price and notify if significant changes occur."
        )
        await message.channel.send(help_message)
        return

    if message.content.startswith("!addstock"):
        parts = message.content.split()
        if len(parts) < 2:
            await message.channel.send("Usage: !addstock SYMBOL")
            return

        stock_symbol = parts[1].upper()
        tracked_stocks = load_stocks(guild_id)

        if stock_symbol not in tracked_stocks:
            save_stock(guild_id, stock_symbol)
            await message.channel.send(f"Added {stock_symbol} to the tracking list for this server.")
        else:
            await message.channel.send(f"{stock_symbol} is already being tracked for this server.")

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

async def fetch_stock_price(symbol):
    """Fetch the stock price from the Finnhub API."""
    try:
        update_request_count()  # Track API usage
        response = requests.get(STOCK_API_URL.format(symbol=symbol, apikey=FINNHUB_API_KEY))
        response.raise_for_status()
        data = response.json()
        logging.info(f"API response for {symbol}: {data}")

        if "c" in data:  # 'c' is the current price in Finnhub response
            return data["c"]
        else:
            logging.error(f"Invalid response for {symbol}: {data}")
            return None
    except Exception as e:
        logging.exception(f"Error fetching price for {symbol}")
        return None

token = os.getenv('TOKEN')
client.run(token)
