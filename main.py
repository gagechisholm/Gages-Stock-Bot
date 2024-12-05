import discord
import os
import asyncio
import requests

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# Dictionary to store stocks and their last prices
tracked_stocks = {}

# Stock price API URL (Using Alpha Vantage as an example)
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')  # Store your API key in Replit Secrets
STOCK_API_URL = "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={apikey}"

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    # Dynamically find the first available text channel
    for guild in client.guilds:
        for channel in guild.text_channels:
            print(f"Found text channel: {channel.name} (ID: {channel.id}) in guild: {guild.name}")
            client.default_channel = channel
            break
    # Start monitoring stocks
    client.loop.create_task(monitor_stocks())

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Command to show help when bot is mentioned with "help"
    if client.user.mentioned_in(message) and "help" in message.content.lower():
        help_message = (
            "Here are the available commands:\n"
            "1. **!addstock SYMBOL** - Adds a stock to the tracking list (e.g., `!addstock AAPL`).\n"
            "2. **!price SYMBOL** - Fetches the current price of a specific stock (e.g., `!price TSLA`).\n"
            "3. **@Gage's Stock Bot help** - Shows this help message.\n\n"
            "Once a stock is added, the bot will monitor its price and notify if it changes by ±5%."
        )
        await message.channel.send(help_message)
        return

    # Command to add a stock to monitor
    if message.content.startswith("!addstock"):
        parts = message.content.split()
        if len(parts) < 2:
            await message.channel.send("Usage: !addstock SYMBOL")
            return

        stock_symbol = parts[1].upper()
        if stock_symbol in tracked_stocks:
            await message.channel.send(f"{stock_symbol} is already being tracked!")
        else:
            tracked_stocks[stock_symbol] = None  # Initialize with no price
            await message.channel.send(f"Added {stock_symbol} to the tracking list.")

    # Command to fetch the current stock price
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
                await message.channel.send(f"Could not fetch the price for {stock_symbol}. Please try again.")
        except Exception as e:
            await message.channel.send(f"Error fetching price for {stock_symbol}: {e}")

async def fetch_stock_price(symbol):
    """Fetch the latest stock price using the Alpha Vantage API."""
    try:
        response = requests.get(STOCK_API_URL.format(symbol=symbol, apikey=ALPHA_VANTAGE_API_KEY))
        data = response.json()
        price = float(data["Global Quote"]["05. price"])
        return price
    except Exception as e:
        print(f"Error fetching price for {symbol}: {e}")
        return None

async def monitor_stocks():
    """Periodically check stock prices and notify changes."""
    global tracked_stocks

    if not hasattr(client, 'default_channel'):
        print("No default channel found. Bot may not send updates until a command is issued.")
        return

    while True:
        for symbol in list(tracked_stocks.keys()):
            try:
                current_price = await fetch_stock_price(symbol)
                if current_price is None:
                    continue

                last_price = tracked_stocks[symbol]

                # Notify if price change exceeds ±5%
                if last_price is not None:
                    percent_change = ((current_price - last_price) / last_price) * 100
                    if abs(percent_change) >= 5:
                        direction = "📈" if percent_change > 0 else "📉"
                        await client.default_channel.send(
                            f"{direction} {symbol} price has changed by {percent_change:.2f}%! "
                            f"New price: ${current_price:.2f} (Previous: ${last_price:.2f})"
                        )

                # Update the last price
                tracked_stocks[symbol] = current_price

            except Exception as e:
                print(f"Error processing {symbol}: {e}")

        # Wait for 60 seconds before the next check
        await asyncio.sleep(60)

# Use the TOKEN from Replit Secrets
token = os.getenv('TOKEN')

if not token:
    raise ValueError("No token found! Ensure 'TOKEN' is added to Replit Secrets.")

client.run(token)
