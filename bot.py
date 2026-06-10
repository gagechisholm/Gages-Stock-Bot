import discord
from discord import app_commands
from discord.ext import commands, tasks
import asyncio
import os
import logging
import sys
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

import market
import db

load_dotenv()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

handler = RotatingFileHandler("app.log", maxBytes=10 * 1024 * 1024, backupCount=5)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[handler, logging.StreamHandler(sys.stdout)],
)

# ---------------------------------------------------------------------------
# Bot setup
# ---------------------------------------------------------------------------

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

PREMIUM_PRO_SKU_ID = os.environ.get("PREMIUM_PRO_SKU_ID")
PREMIUM_PLUS_SKU_ID = os.environ.get("PREMIUM_PLUS_SKU_ID")


async def has_premium(guild_id: int) -> bool:
    return await db.is_premium(guild_id)


# ---------------------------------------------------------------------------
# Bot events
# ---------------------------------------------------------------------------

@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user} ({bot.user.id})")
    try:
        synced = await bot.tree.sync()
        logging.info(f"Synced {len(synced)} slash commands globally")
    except Exception:
        logging.exception("Failed to sync slash commands")
    monitor_alerts.start()


@bot.event
async def on_guild_join(guild: discord.Guild):
    logging.info(f"Joined guild: {guild.name} ({guild.id})")
    await db.register_guild(guild.id, guild.name, guild.owner_id)

    embed = discord.Embed(
        title="StockNPC is here!",
        description=(
            "Thanks for adding StockNPC. Here's how to get started:\n\n"
            "**Step 1 — Set an alert channel (admin only)**\n"
            "Run `/setup channel #your-channel` to choose where price alerts post.\n\n"
            "**Step 2 — Start using commands**"
        ),
        color=discord.Color.green(),
    )
    embed.add_field(
        name="/quote",
        value="Get the current price of any stock",
        inline=False,
    )
    embed.add_field(
        name="/watchlist add/remove/view",
        value="Track stocks on your personal watchlist",
        inline=False,
    )
    embed.add_field(
        name="/alert set/list/remove",
        value="Get notified when a stock moves by a % you set",
        inline=False,
    )
    embed.add_field(
        name="/portfolio buy/sell/view",
        value="Paper-trade and track a virtual portfolio",
        inline=False,
    )
    embed.add_field(
        name="/leaderboard",
        value="See who's winning the paper-trading competition",
        inline=False,
    )
    embed.set_footer(text="Run /setup info at any time to check your configuration.")

    channel = guild.system_channel
    if channel is None:
        channel = next(
            (c for c in guild.text_channels if c.permissions_for(guild.me).send_messages),
            None,
        )
    if channel:
        await channel.send(embed=embed)


# ---------------------------------------------------------------------------
# /quote
# ---------------------------------------------------------------------------

@bot.tree.command(name="quote", description="Look up the current price of a stock")
@app_commands.describe(symbol="Ticker symbol (e.g. AAPL, TSLA, SPY)")
async def quote(interaction: discord.Interaction, symbol: str):
    await interaction.response.defer()
    q = await market.get_quote(symbol)
    if not q:
        await interaction.followup.send(
            f"Could not find a price for **{symbol.upper()}**. "
            "Double-check the ticker symbol.",
            ephemeral=True,
        )
        return
    await interaction.followup.send(market.format_quote(q))


# ---------------------------------------------------------------------------
# /watchlist group
# ---------------------------------------------------------------------------

watchlist_group = app_commands.Group(
    name="watchlist", description="Manage your personal stock watchlist"
)


@watchlist_group.command(name="add", description="Add a stock to your personal watchlist")
@app_commands.describe(symbol="Ticker symbol to add (e.g. AAPL)")
async def watchlist_add(interaction: discord.Interaction, symbol: str):
    await interaction.response.defer(ephemeral=True)
    symbol = symbol.upper()

    current_list = await db.get_member_watchlist(interaction.guild_id, interaction.user.id)
    if len(current_list) >= 10 and not await has_premium(interaction.guild_id):
        await interaction.followup.send(
            "Free watchlists are limited to 10 stocks. "
            "Upgrade to Pro to add more.",
            ephemeral=True,
        )
        return

    q = await market.get_quote(symbol)
    if not q:
        await interaction.followup.send(
            f"**{symbol}** doesn't look like a valid ticker. "
            "Check the symbol and try again.",
            ephemeral=True,
        )
        return

    added = await db.add_to_member_watchlist(interaction.guild_id, interaction.user.id, symbol)
    if not added:
        await interaction.followup.send(
            f"**{symbol}** is already in your watchlist.", ephemeral=True
        )
        return

    await interaction.followup.send(
        f"Added **{symbol}** to your watchlist.\n{market.format_quote(q)}",
        ephemeral=True,
    )


@watchlist_group.command(name="remove", description="Remove a stock from your personal watchlist")
@app_commands.describe(symbol="Ticker symbol to remove")
async def watchlist_remove(interaction: discord.Interaction, symbol: str):
    await interaction.response.defer(ephemeral=True)
    symbol = symbol.upper()
    removed = await db.remove_from_member_watchlist(
        interaction.guild_id, interaction.user.id, symbol
    )
    if removed:
        await interaction.followup.send(
            f"Removed **{symbol}** from your watchlist.", ephemeral=True
        )
    else:
        await interaction.followup.send(
            f"**{symbol}** wasn't on your watchlist.", ephemeral=True
        )


@watchlist_group.command(name="view", description="View your personal watchlist with current prices")
async def watchlist_view(interaction: discord.Interaction):
    await interaction.response.defer()
    symbols = await db.get_member_watchlist(interaction.guild_id, interaction.user.id)
    if not symbols:
        await interaction.followup.send(
            "Your watchlist is empty. Use `/watchlist add SYMBOL` to start tracking stocks."
        )
        return

    quotes = await market.get_quotes(symbols)
    lines = []
    for sym in symbols:
        q = quotes.get(sym)
        lines.append(market.format_quote(q) if q else f"**{sym}**  —  price unavailable")

    embed = discord.Embed(
        title=f"{interaction.user.display_name}'s Watchlist",
        description="\n".join(lines),
        color=discord.Color.blue(),
        timestamp=datetime.now(timezone.utc),
    )
    await interaction.followup.send(embed=embed)


bot.tree.add_command(watchlist_group)


# ---------------------------------------------------------------------------
# /alert group
# ---------------------------------------------------------------------------

alert_group = app_commands.Group(
    name="alert", description="Manage price movement alerts"
)


@alert_group.command(name="set", description="Set a price movement alert for a stock")
@app_commands.describe(
    symbol="Ticker symbol (e.g. AAPL)",
    threshold="Percentage move to trigger alert (e.g. 5 for 5%)",
    direction="Direction to watch: up, down, or both",
)
@app_commands.choices(direction=[
    app_commands.Choice(name="Both directions", value="both"),
    app_commands.Choice(name="Up only", value="up"),
    app_commands.Choice(name="Down only", value="down"),
])
async def alert_set(
    interaction: discord.Interaction,
    symbol: str,
    threshold: float,
    direction: str = "both",
):
    await interaction.response.defer(ephemeral=True)
    symbol = symbol.upper()

    settings = await db.get_settings(interaction.guild_id)
    channel_id = settings.get("alert_channel_id")
    if not channel_id:
        await interaction.followup.send(
            "No alert channel configured. An admin must run `/setup channel` first.",
            ephemeral=True,
        )
        return

    q = await market.get_quote(symbol)
    if not q:
        await interaction.followup.send(
            f"**{symbol}** doesn't look like a valid ticker.", ephemeral=True
        )
        return

    alert = await db.create_alert(
        guild_id=interaction.guild_id,
        user_id=interaction.user.id,
        symbol=symbol,
        threshold_pct=abs(threshold),
        direction=direction,
        channel_id=channel_id,
    )
    if alert:
        await interaction.followup.send(
            f"Alert set: notify when **{symbol}** moves {threshold}% ({direction}) "
            f"from its current price of ${q.get('close', 0):,.2f}.",
            ephemeral=True,
        )
    else:
        await interaction.followup.send("Failed to create alert. Try again.", ephemeral=True)


@alert_group.command(name="list", description="View your active alerts")
async def alert_list(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    alerts = await db.get_active_alerts(interaction.guild_id, interaction.user.id)
    if not alerts:
        await interaction.followup.send("You have no active alerts.", ephemeral=True)
        return

    lines = []
    for a in alerts:
        lines.append(
            f"`{str(a['id'])[:8]}` — **{a['symbol']}** {a['threshold_pct']}% ({a['direction']})"
        )

    embed = discord.Embed(
        title="Your Active Alerts",
        description="\n".join(lines),
        color=discord.Color.orange(),
    )
    embed.set_footer(text="Use /alert remove <id> to cancel an alert")
    await interaction.followup.send(embed=embed, ephemeral=True)


@alert_group.command(name="remove", description="Remove a price alert")
@app_commands.describe(alert_id="The alert ID prefix shown in /alert list")
async def alert_remove(interaction: discord.Interaction, alert_id: str):
    await interaction.response.defer(ephemeral=True)
    alerts = await db.get_active_alerts(interaction.guild_id, interaction.user.id)
    match = next(
        (a for a in alerts if str(a["id"]).startswith(alert_id.strip())), None
    )
    if not match:
        await interaction.followup.send(
            "Alert not found. Use `/alert list` to see your alerts.", ephemeral=True
        )
        return

    await db.deactivate_alert(match["id"])
    await interaction.followup.send(
        f"Removed alert for **{match['symbol']}**.", ephemeral=True
    )


bot.tree.add_command(alert_group)


# ---------------------------------------------------------------------------
# /leaderboard
# ---------------------------------------------------------------------------

@bot.tree.command(name="leaderboard", description="View the server's paper-portfolio leaderboard")
async def leaderboard(interaction: discord.Interaction):
    await interaction.response.defer()

    rows = await db.get_leaderboard(interaction.guild_id)
    if not rows:
        await interaction.followup.send(
            "No portfolio data yet. Members can paper-trade with `/portfolio buy`."
        )
        return

    all_symbols = list({r["symbol"] for r in rows})
    quotes = await market.get_quotes(all_symbols)

    user_totals: dict[int, dict] = {}
    for row in rows:
        uid = row["user_id"]
        sym = row["symbol"]
        q = quotes.get(sym)
        if not q:
            continue
        current = q.get("close") or 0
        avg = row["avg_cost"] or 0
        gain_pct = ((current - avg) / avg * 100) if avg else 0
        if uid not in user_totals:
            user_totals[uid] = {"total_pct": 0.0, "count": 0}
        user_totals[uid]["total_pct"] += gain_pct
        user_totals[uid]["count"] += 1

    ranked = sorted(
        user_totals.items(),
        key=lambda x: x[1]["total_pct"] / max(x[1]["count"], 1),
        reverse=True,
    )

    medals = ["🥇", "🥈", "🥉"]
    lines = []
    for i, (uid, stats) in enumerate(ranked[:10]):
        avg_gain = stats["total_pct"] / max(stats["count"], 1)
        prefix = medals[i] if i < 3 else f"{i+1}."
        lines.append(f"{prefix} <@{uid}>  {avg_gain:+.2f}%")

    embed = discord.Embed(
        title="📈 Portfolio Leaderboard",
        description="\n".join(lines) if lines else "Not enough data yet.",
        color=discord.Color.gold(),
        timestamp=datetime.now(timezone.utc),
    )
    embed.set_footer(text="Ranked by avg unrealized gain % across all holdings")
    await interaction.followup.send(embed=embed)


# ---------------------------------------------------------------------------
# /portfolio group
# ---------------------------------------------------------------------------

portfolio_group = app_commands.Group(
    name="portfolio", description="Paper-trade and track your virtual portfolio"
)


@portfolio_group.command(name="buy", description="Paper-buy shares of a stock")
@app_commands.describe(symbol="Ticker symbol", shares="Number of shares to buy")
async def portfolio_buy(interaction: discord.Interaction, symbol: str, shares: float):
    await interaction.response.defer(ephemeral=True)
    symbol = symbol.upper()

    if shares <= 0:
        await interaction.followup.send("Shares must be a positive number.", ephemeral=True)
        return

    q = await market.get_quote(symbol)
    if not q:
        await interaction.followup.send(f"**{symbol}** is not a valid ticker.", ephemeral=True)
        return

    price = q.get("close") or 0
    holdings = await db.get_portfolio(interaction.guild_id, interaction.user.id)
    existing = next((h for h in holdings if h["symbol"] == symbol), None)

    if existing:
        total_shares = existing["shares"] + shares
        avg_cost = (existing["avg_cost"] * existing["shares"] + price * shares) / total_shares
    else:
        total_shares = shares
        avg_cost = price

    await db.upsert_portfolio_holding(
        interaction.guild_id, interaction.user.id, symbol, total_shares, avg_cost
    )
    await db.log_trade(interaction.guild_id, interaction.user.id, symbol, "buy", shares, price)

    await interaction.followup.send(
        f"Bought **{shares:g} shares** of **{symbol}** at **${price:,.2f}**.\n"
        f"Total position: {total_shares:g} shares @ avg ${avg_cost:,.2f}",
        ephemeral=True,
    )


@portfolio_group.command(name="sell", description="Paper-sell shares of a stock")
@app_commands.describe(symbol="Ticker symbol", shares="Number of shares to sell")
async def portfolio_sell(interaction: discord.Interaction, symbol: str, shares: float):
    await interaction.response.defer(ephemeral=True)
    symbol = symbol.upper()

    holdings = await db.get_portfolio(interaction.guild_id, interaction.user.id)
    existing = next((h for h in holdings if h["symbol"] == symbol), None)

    if not existing:
        await interaction.followup.send(f"You don't hold any **{symbol}**.", ephemeral=True)
        return

    if shares > existing["shares"]:
        await interaction.followup.send(
            f"You only hold {existing['shares']:g} shares of **{symbol}**.", ephemeral=True
        )
        return

    q = await market.get_quote(symbol)
    price = (q.get("close") or 0) if q else existing["avg_cost"]

    remaining = existing["shares"] - shares
    if remaining < 0.001:
        await db.remove_portfolio_holding(interaction.guild_id, interaction.user.id, symbol)
    else:
        await db.upsert_portfolio_holding(
            interaction.guild_id, interaction.user.id, symbol, remaining, existing["avg_cost"]
        )

    await db.log_trade(interaction.guild_id, interaction.user.id, symbol, "sell", shares, price)

    gain = (price - existing["avg_cost"]) * shares
    gain_pct = ((price - existing["avg_cost"]) / existing["avg_cost"] * 100) if existing["avg_cost"] else 0

    await interaction.followup.send(
        f"Sold **{shares:g} shares** of **{symbol}** at **${price:,.2f}**.\n"
        f"Realized P&L: **${gain:+,.2f}** ({gain_pct:+.2f}%)",
        ephemeral=True,
    )


@portfolio_group.command(name="view", description="View your paper portfolio")
async def portfolio_view(interaction: discord.Interaction):
    await interaction.response.defer()
    holdings = await db.get_portfolio(interaction.guild_id, interaction.user.id)

    if not holdings:
        await interaction.followup.send(
            "Your portfolio is empty. Use `/portfolio buy SYMBOL SHARES` to start."
        )
        return

    symbols = [h["symbol"] for h in holdings]
    quotes = await market.get_quotes(symbols)

    lines = []
    total_value = 0.0
    total_cost = 0.0
    for h in holdings:
        sym = h["symbol"]
        q = quotes.get(sym)
        current = (q.get("close") or 0) if q else 0
        cost_basis = h["avg_cost"] * h["shares"]
        market_value = current * h["shares"]
        gain_pct = ((market_value - cost_basis) / cost_basis * 100) if cost_basis else 0
        total_value += market_value
        total_cost += cost_basis
        lines.append(f"**{sym}**  {h['shares']:g} sh @ ${current:,.2f}  ({gain_pct:+.2f}%)")

    total_gain = total_value - total_cost
    total_gain_pct = (total_gain / total_cost * 100) if total_cost else 0

    embed = discord.Embed(
        title=f"{interaction.user.display_name}'s Portfolio",
        description="\n".join(lines),
        color=discord.Color.green() if total_gain >= 0 else discord.Color.red(),
        timestamp=datetime.now(timezone.utc),
    )
    embed.add_field(
        name="Total P&L",
        value=f"${total_gain:+,.2f} ({total_gain_pct:+.2f}%)",
        inline=False,
    )
    await interaction.followup.send(embed=embed)


bot.tree.add_command(portfolio_group)


# ---------------------------------------------------------------------------
# /setup group (admin only)
# ---------------------------------------------------------------------------

setup_group = app_commands.Group(
    name="setup",
    description="Configure the bot for this server (admin only)",
    default_permissions=discord.Permissions(manage_guild=True),
)


@setup_group.command(name="channel", description="Set the channel where alerts and updates post")
@app_commands.describe(channel="The channel to use for bot alerts")
async def setup_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    await interaction.response.defer(ephemeral=True)
    await db.register_guild(interaction.guild_id, interaction.guild.name, interaction.guild.owner_id)
    await db.set_alert_channel(interaction.guild_id, channel.id)
    await interaction.followup.send(
        f"Alert channel set to {channel.mention}.", ephemeral=True
    )


@setup_group.command(name="info", description="View current bot configuration for this server")
async def setup_info(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    settings = await db.get_settings(interaction.guild_id)
    guild = await db.get_guild(interaction.guild_id)

    channel_id = settings.get("alert_channel_id")
    channel_mention = f"<#{channel_id}>" if channel_id else "Not set — run `/setup channel`"
    tier = guild.get("premium_tier", "free") if guild else "free"

    embed = discord.Embed(title="Bot Configuration", color=discord.Color.blurple())
    embed.add_field(name="Alert Channel", value=channel_mention, inline=True)
    embed.add_field(name="Plan", value=tier.capitalize(), inline=True)
    await interaction.followup.send(embed=embed, ephemeral=True)


bot.tree.add_command(setup_group)


# ---------------------------------------------------------------------------
# Background task: monitor alerts every 30 minutes
# ---------------------------------------------------------------------------

@tasks.loop(minutes=30)
async def monitor_alerts():
    logging.info("Running alert monitor...")
    try:
        alerts = await db.get_all_active_alerts()
        if not alerts:
            return

        symbols = list({a["symbol"] for a in alerts})
        quotes = await market.get_quotes(symbols)

        for alert in alerts:
            sym = alert["symbol"]
            q = quotes.get(sym)
            if not q:
                continue

            current = q.get("close") or 0
            open_p = q.get("open") or current
            if not open_p:
                continue

            pct_change = ((current - open_p) / open_p) * 100
            direction = alert["direction"]
            threshold = alert["threshold_pct"]

            triggered = (
                (direction == "both" and abs(pct_change) >= threshold)
                or (direction == "up" and pct_change >= threshold)
                or (direction == "down" and pct_change <= -threshold)
            )

            if not triggered:
                continue

            channel = bot.get_channel(alert["channel_id"])
            if not channel:
                continue

            arrow = "📈" if pct_change > 0 else "📉"
            await channel.send(
                f"{arrow} **{sym}** moved **{pct_change:+.2f}%** today "
                f"and is now **${current:,.2f}** — "
                f"<@{alert['user_id']}>'s {threshold}% alert triggered"
            )
            await db.deactivate_alert(alert["id"])
            logging.info(f"Alert fired: {sym} {pct_change:+.2f}% for user {alert['user_id']}")

    except Exception:
        logging.exception("Error in monitor_alerts task")


@monitor_alerts.before_loop
async def before_monitor():
    await bot.wait_until_ready()


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

token = os.environ.get("DISCORD_TOKEN")
if not token:
    logging.error("DISCORD_TOKEN not set.")
    sys.exit(1)

bot.run(token, log_handler=None)
