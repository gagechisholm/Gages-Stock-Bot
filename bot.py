import discord
import os
import asyncio
import requests
import logging
import sqlite3

# Configure logging
logging.basicConfig(filename="app.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Discord client setup
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Stock price API URL (Using Alpha Vantage as an example)
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')  # Store your API key in environment variables
STOCK_API_URL = "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={apikey}"

# SQLite database file
DB_FILE = "stocks.db"

# In-memory cache of tracked stocks
tracked_stocks = {}
notification_threshold = 5  # Default percentage for notifications

# Initialize the database
def initialize_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stocks (
                symbol TEXT PRIMARY KEY,
                last_price REAL
            )
        """)
        conn.commit()

# Save stock to database
def save_stock(symbol, last_price=None):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO stocks (symbol, last_price)
            VALUES (?, ?)
        """, (symbol, last_price))
        conn.commit()

# Load stocks from database
def load_stocks():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT symbol, last_price FROM stocks")
        return {row[0]: row[1] for row in cursor.fetchall()}

@client.event
async def on_ready():
    logging.info(f"We have logged in as {client.user}")
    initialize_db()
    global tracked_stocks
    tracked_stocks = load_stocks()
    logging.info(f"Loaded stocks from database: {tracked_stocks}")

    # Dynamically find the first available text channel
    for guild in client.guilds:
        for channel in guild.text_channels:
            client.default_channel = channel
            break

    client.loop.create_task(monitor_stocks())

@client.event
async def on_message(message):
    global notification_threshold

    if message.author == client.user:
        return

    if client.user.mentioned_in(message) and "help" in message.content.lower():
        help_message = (
            "Here are the available commands:\n"
            "1. **!addstock SYMBOL** - Adds a stock to the tracking list (e.g., `!addstock AAPL`).\n"
            "2. **!removestock SYMBOL** - Removes a stock from the tracking list (e.g., `!removestock TSLA`).\n"
            "3. **!price SYMBOL** - Fetches the current price of a specific stock (e.g., `!price TSLA`).\n"
            "4. **!watchlist** - Displays the current stock watchlist.\n"
            "5. **!setthreshold PERCENT** - Changes the price change notification threshold (e.g., `!setthreshold 10`).\n"
            "6. **@Bot help** - Shows this help message.\n\n"
            "Once a stock is added, the bot will monitor its price and notify if it changes by ± the specified percentage."
        )
        await message.channel.send(help_message)
        return

    # Add a stock to the tracking list
    if message.content.startswith("!addstock"):
        parts = message.content.split()
        if len(parts) < 2:
            await message.channel.send("Usage: !addstock SYMBOL")
            return

        stock_symbol = parts[1].upper()
        if stock_symbol not in tracked_stocks:
            tracked_stocks[stock_symbol] = None
            save_stock(stock_symbol)
            await message.channel.send(f"Added {stock_symbol} to the tracking list.")
        else:
            await message.channel.send(f"{stock_symbol} is already being tracked!")

    # Remove a stock from the tracking list
    if message.content.startswith("!removestock"):
        parts = message.content.split()
        if len(parts) < 2:
            await message.channel.send("Usage: !removestock SYMBOL")
            return

        stock_symbol = parts[1].upper()
        if stock_symbol in tracked_stocks:
            del tracked_stocks[stock_symbol]
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM stocks WHERE symbol = ?", (stock_symbol,))
                conn.commit()
            await message.channel.send(f"Removed {stock_symbol} from the tracking list.")
        else:
            await message.channel.send(f"{stock_symbol} is not in the tracking list.")

    # Display the current stock watchlist
    if message.content.startswith("!watchlist"):
        if not tracked_stocks:
            await message.channel.send("The stock watchlist is empty.")
        else:
            watchlist = "\n".join(tracked_stocks.keys())
            await message.channel.send(f"Current stock watchlist:\n```\n{watchlist}\n```")

    # Change the notification threshold
    if message.content.startswith("!setthreshold"):
        parts = message.content.split()
        if len(parts) < 2:
            await message.channel.send("Usage: !setthreshold PERCENT")
            return

        try:
            threshold = float(parts[1])
            if threshold <= 0:
                await message.channel.send("Threshold must be a positive number.")
            else:
                notification_threshold = threshold
                await message.channel.send(f"Notification threshold set to {notification_threshold}%.")
        except ValueError:
            await message.channel.send("Please provide a valid percentage.")

    # Fetch the current price of a specific stock
    if message.content.startswith("!price"):
        parts = message.content.split()
        if len(parts) < 2:
            await message.channel.send("Usage: !price SYMBOL")
            return

        stock_symbol = parts[1].upper()
        try:
            current_price = await fetch_stock_price(stock_symbol)
            if current_price is not None:
                await message.channel.send(f"Current price of {stock_symbol}: ${current_price:.2f} USD")
            else:
                await message.channel.send(f"Could not fetch the price for {stock_symbol}.")
        except Exception as e:
            await message.channel.send(f"Error fetching price for {stock_symbol}: {e}")

async def fetch_stock_price(symbol):
    try:
        response = requests.get(STOCK_API_URL.format(symbol=symbol, apikey=ALPHA_VANTAGE_API_KEY))
        response.raise_for_status()
        data = response.json()
        logging.info(f"API response for {symbol}: {data}")

        if "Global Quote" not in data or "05. price" not in data["Global Quote"]:
            logging.error(f"Invalid response for {symbol}: {data}")
            return None

        return float(data["Global Quote"]["05. price"])
    except Exception as e:
        logging.exception(f"Error fetching price for {symbol}")
        return None

async def monitor_stocks():
    global notification_threshold

    while True:
        for symbol in list(tracked_stocks.keys()):
            try:
                current_price = await fetch_stock_price(symbol)
                if current_price is None:
                    continue

                last_price = tracked_stocks[symbol]

                if last_price is not None:
                    percent_change = ((current_price - last_price) / last_price) * 100
                    if abs(percent_change) >= notification_threshold:
                        direction = "📈" if percent_change > 0 else "📉"
                        await client.default_channel.send(
                            f"{direction} {symbol} price changed by {percent_change:.2f}%! "
                            f"New price: ${current_price:.2f} (Previous: ${last_price:.2f})"
                        )

                tracked_stocks[symbol] = current_price
                save_stock(symbol, current_price)

            except Exception as e:
                logging.exception(f"Error processing {symbol}")
        await asyncio.sleep(60)

token = os.getenv('TOKEN')
client.run(token)
