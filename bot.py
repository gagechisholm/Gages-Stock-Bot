import calendar
import discord
from discord import app_commands
from discord.ext import commands, tasks
from zoneinfo import ZoneInfo
import asyncio
import os
import logging
import sys
from datetime import datetime, timedelta, timezone
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from openai import AsyncOpenAI

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

ET = ZoneInfo("America/New_York")
PREMIUM_PRO_SKU_ID  = os.environ.get("PREMIUM_PRO_SKU_ID")
PREMIUM_PLUS_SKU_ID = os.environ.get("PREMIUM_PLUS_SKU_ID")
API_URL             = os.environ.get("API_URL", "")

FREE_WATCHLIST_LIMIT = 5
FREE_ALERT_LIMIT     = 3
FREE_ROAST_LIMIT     = 2


def upgrade_link(guild_id: int) -> str:
    return f"{API_URL}/stripe/checkout?guild_id={guild_id}"

_openai_client: AsyncOpenAI | None = None
_leaderboard_posted: set[str] = set()  # "guild_id:date" keys to prevent double-posting

# In-memory roast usage: "guild_id:user_id" -> (iso_week_str, count)
_roast_usage: dict[str, tuple[str, int]] = {}


def _current_week() -> str:
    return datetime.now(timezone.utc).strftime("%Y-W%W")


def _roasts_used(guild_id: int, user_id: int) -> int:
    key = f"{guild_id}:{user_id}"
    week, count = _roast_usage.get(key, ("", 0))
    return count if week == _current_week() else 0


def _increment_roast(guild_id: int, user_id: int) -> None:
    key = f"{guild_id}:{user_id}"
    _roast_usage[key] = (_current_week(), _roasts_used(guild_id, user_id) + 1)


def get_openai() -> AsyncOpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    return _openai_client


async def has_premium(guild_id: int) -> bool:
    return await db.is_premium(guild_id)


# ---------------------------------------------------------------------------
# Leaderboard helpers
# ---------------------------------------------------------------------------

async def compute_leaderboard(guild: discord.Guild) -> list[dict]:
    """Ranks members by avg % gain across watchlist picks since they were added."""
    entries = await db.get_all_guild_watchlists(guild.id)
    if not entries:
        return []

    symbols = list({e["symbol"] for e in entries})
    quotes = await market.get_quotes(symbols)

    user_gains: dict[int, list[float]] = {}
    for entry in entries:
        uid = entry["user_id"]
        sym = entry["symbol"]
        added = entry.get("added_price")
        q = quotes.get(sym)
        if not q or not added or added <= 0:
            continue
        current = q.get("close") or 0
        gain_pct = (current - added) / added * 100
        user_gains.setdefault(uid, []).append(gain_pct)

    ranked = []
    for uid, gains in sorted(
        user_gains.items(),
        key=lambda x: sum(x[1]) / len(x[1]),
        reverse=True,
    ):
        avg = sum(gains) / len(gains)
        member = guild.get_member(uid)
        if not member:
            try:
                member = await guild.fetch_member(uid)
            except Exception:
                member = None
        name = member.display_name if member else f"Unknown ({uid})"
        ranked.append({"user_id": uid, "name": name, "avg_gain": avg, "pick_count": len(gains)})

    for i, row in enumerate(ranked):
        row["rank"] = i + 1

    return ranked


def _get_leaderboard_period(now: datetime) -> str | None:
    """Returns 'monthly', 'weekly', 'daily', or None for weekends."""
    if now.weekday() > 4:
        return None
    if now.weekday() == 4:  # Friday
        last_day = calendar.monthrange(now.year, now.month)[1]
        last_date = now.replace(day=last_day)
        days_back = (last_date.weekday() - 4) % 7
        last_friday = last_date - timedelta(days=days_back)
        if now.date() == last_friday.date():
            return "monthly"
        return "weekly"
    return "daily"


async def generate_brainrot_announcement(period: str, rankings: list[dict]) -> str:
    total = len(rankings)
    lines = []
    for r in rankings[:10]:
        percentile = r["rank"] / total if total > 0 else 0.5
        if percentile <= 0.25:
            tone_hint = "(top of server, give props)"
        elif percentile <= 0.60:
            tone_hint = "(mid, balanced)"
        else:
            tone_hint = "(bottom, go ruthless)"
        lines.append(
            f"#{r['rank']} {r['name']}: {r['avg_gain']:+.2f}% over {r['pick_count']} picks {tone_hint}"
        )
    stats = "\n".join(lines)
    prompt = (
        f"Post the {period} leaderboard for this server's stock picks. "
        f"Go through each person with a short reaction — praise winners, roast losers. "
        f"Make it feel like a group chat, not a monologue. Reference how people compare to each other.\n\n"
        f"Standings:\n{stats}"
    )
    try:
        response = await get_openai().chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Stock NPC, a Gen-Z stock market commentator in a Discord server. "
                        "React to the leaderboard like a funny friend in a group chat would. "
                        "Ruthless toward people at the bottom, respectful toward people at the top. "
                        "The roast level has to match their rank — calling a top performer trash makes no sense. "
                        "Be witty and natural. If a joke isn't casually funny, don't say it. "
                        "Reference comparisons between people to make it feel like a server moment, not solo callouts. "
                        "Casual Gen-Z tone, emojis only when they add something. "
                        "NEVER use em dashes (—) under any circumstances. "
                        "NEVER use 'it's not X, it's Y' constructions — that's forced and try-hard. "
                        "Never use asterisks or markdown formatting."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=600,
        )
        return response.choices[0].message.content
    except Exception:
        logging.exception("OpenAI call failed, falling back to plain leaderboard")
        medals = ["🥇", "🥈", "🥉"]
        lines = [f"**{period.capitalize()} Leaderboard**"]
        for r in rankings[:10]:
            prefix = medals[r["rank"] - 1] if r["rank"] <= 3 else f"{r['rank']}."
            lines.append(f"{prefix} **{r['name']}** {r['avg_gain']:+.2f}%")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Bot events
# ---------------------------------------------------------------------------

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    logging.exception(f"Slash command error in /{interaction.command.name if interaction.command else '?'}", exc_info=error)
    cause = getattr(error, "__cause__", error)
    msg = f"Something went wrong: `{type(cause).__name__}: {str(cause)[:200]}`"
    try:
        if interaction.response.is_done():
            await interaction.followup.send(msg, ephemeral=True)
        else:
            await interaction.response.send_message(msg, ephemeral=True)
    except Exception:
        pass


@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user} ({bot.user.id})")
    try:
        synced = await bot.tree.sync()
        logging.info(f"Synced {len(synced)} slash commands globally")
    except Exception:
        logging.exception("Failed to sync slash commands")
    monitor_alerts.start()
    scheduled_leaderboard.start()


@bot.event
async def on_guild_join(guild: discord.Guild):
    logging.info(f"Joined guild: {guild.name} ({guild.id})")
    try:
        await db.register_guild(guild.id, guild.name, guild.owner_id)
    except Exception:
        logging.exception(f"Failed to register guild {guild.id} in DB")

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
    embed.add_field(name="/quote", value="Get the current price of any stock", inline=False)
    embed.add_field(name="/watchlist add/remove/view", value="Track stocks on your personal watchlist and compete on the leaderboard", inline=False)
    embed.add_field(name="/alert set/list/remove", value="Get notified when a stock moves by a % you set", inline=False)
    embed.add_field(name="/leaderboard", value="See who has the best stock picks in the server", inline=False)
    embed.set_footer(text="Run /setup info at any time to check your configuration.")

    channel = guild.system_channel
    if channel is None:
        channel = next(
            (c for c in guild.text_channels if c.permissions_for(guild.me).send_messages),
            None,
        )
    if channel:
        try:
            await channel.send(embed=embed)
        except Exception:
            logging.exception(f"Failed to send welcome message to guild {guild.id}")


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
            f"Could not find a price for **{symbol.upper()}**. Double-check the ticker symbol.",
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

    await db.register_guild(interaction.guild_id, interaction.guild.name, interaction.guild.owner_id)

    current_list = await db.get_member_watchlist(interaction.guild_id, interaction.user.id)
    is_premium = await has_premium(interaction.guild_id)
    if len(current_list) >= FREE_WATCHLIST_LIMIT and not is_premium:
        await interaction.followup.send(
            f"Free servers are limited to {FREE_WATCHLIST_LIMIT} stocks per watchlist.\n"
            f"Upgrade to Pro for unlimited picks: {upgrade_link(interaction.guild_id)}",
            ephemeral=True,
        )
        return

    q = await market.get_quote(symbol)
    if not q:
        await interaction.followup.send(
            f"**{symbol}** doesn't look like a valid ticker. Check the symbol and try again.",
            ephemeral=True,
        )
        return

    added_price = q.get("close") or None
    result = await db.add_to_member_watchlist(
        interaction.guild_id, interaction.user.id, symbol, added_price
    )
    if result == "duplicate":
        await interaction.followup.send(f"**{symbol}** is already in your watchlist.", ephemeral=True)
        return
    if not result:
        await interaction.followup.send("Failed to add to watchlist. Try again.", ephemeral=True)
        return

    await interaction.followup.send(
        f"Added **{symbol}** to your watchlist at **${added_price:,.2f}**. "
        f"Your gain will be tracked from this price.\n{market.format_quote(q)}",
        ephemeral=True,
    )


@watchlist_group.command(name="remove", description="Remove a stock from your personal watchlist")
@app_commands.describe(symbol="Ticker symbol to remove")
async def watchlist_remove(interaction: discord.Interaction, symbol: str):
    await interaction.response.defer(ephemeral=True)
    symbol = symbol.upper()
    removed = await db.remove_from_member_watchlist(interaction.guild_id, interaction.user.id, symbol)
    if removed:
        await interaction.followup.send(f"Removed **{symbol}** from your watchlist.", ephemeral=True)
    else:
        await interaction.followup.send(f"**{symbol}** wasn't on your watchlist.", ephemeral=True)


@watchlist_group.command(name="view", description="View your personal watchlist with gains since added")
async def watchlist_view(interaction: discord.Interaction):
    await interaction.response.defer()
    entries = await db.get_member_watchlist_detailed(interaction.guild_id, interaction.user.id)
    if not entries:
        await interaction.followup.send(
            "Your watchlist is empty. Use `/watchlist add SYMBOL` to start tracking stocks."
        )
        return

    symbols = [e["symbol"] for e in entries]
    quotes = await market.get_quotes(symbols)
    lines = []
    for entry in entries:
        sym = entry["symbol"]
        added_price = entry.get("added_price")
        q = quotes.get(sym)
        if not q:
            lines.append(f"**{sym}**  —  price unavailable")
            continue
        current = q.get("close") or 0
        line = market.format_quote(q)
        if added_price and added_price > 0:
            gain_pct = (current - added_price) / added_price * 100
            arrow = "📈" if gain_pct >= 0 else "📉"
            line += f"  {arrow} {gain_pct:+.2f}% since added"
        lines.append(line)

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

alert_group = app_commands.Group(name="alert", description="Manage price movement alerts")


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

    is_premium = await has_premium(interaction.guild_id)
    if not is_premium:
        alert_count = await db.count_active_alerts(interaction.guild_id, interaction.user.id)
        if alert_count >= FREE_ALERT_LIMIT:
            await interaction.followup.send(
                f"Free servers are limited to {FREE_ALERT_LIMIT} active alerts per person.\n"
                f"Upgrade to Pro for unlimited alerts: {upgrade_link(interaction.guild_id)}",
                ephemeral=True,
            )
            return

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

    lines = [
        f"`{str(a['id'])[:8]}` — **{a['symbol']}** {a['threshold_pct']}% ({a['direction']})"
        for a in alerts
    ]
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
    match = next((a for a in alerts if str(a["id"]).startswith(alert_id.strip())), None)
    if not match:
        await interaction.followup.send(
            "Alert not found. Use `/alert list` to see your alerts.", ephemeral=True
        )
        return
    await db.deactivate_alert(match["id"])
    await interaction.followup.send(f"Removed alert for **{match['symbol']}**.", ephemeral=True)


bot.tree.add_command(alert_group)


# ---------------------------------------------------------------------------
# /leaderboard (on-demand, plain embed)
# ---------------------------------------------------------------------------

@bot.tree.command(name="leaderboard", description="View the server's stock-picking leaderboard")
async def leaderboard(interaction: discord.Interaction):
    await interaction.response.defer()

    rankings = await compute_leaderboard(interaction.guild)
    if not rankings:
        await interaction.followup.send(
            "No leaderboard data yet. Members need to add stocks with `/watchlist add` to appear here."
        )
        return

    medals = ["🥇", "🥈", "🥉"]
    lines = []
    for r in rankings[:10]:
        prefix = medals[r["rank"] - 1] if r["rank"] <= 3 else f"{r['rank']}."
        lines.append(f"{prefix} **{r['name']}**  {r['avg_gain']:+.2f}%  ({r['pick_count']} picks)")

    embed = discord.Embed(
        title="📈 Stock Picking Leaderboard",
        description="\n".join(lines),
        color=discord.Color.gold(),
        timestamp=datetime.now(timezone.utc),
    )
    is_premium = await has_premium(interaction.guild.id)
    embed.set_footer(text="Ranked by avg % gain across watchlist picks since added")
    await interaction.followup.send(embed=embed)
    if not is_premium:
        await interaction.followup.send(
            f"Want Stock NPC to roast these picks every market close? "
            f"**[Upgrade to Pro for $5/mo]({upgrade_link(interaction.guild.id)})**  ·  or run `/upgrade` to learn more"
        )


# ---------------------------------------------------------------------------
# /setup group (admin only)
# ---------------------------------------------------------------------------

setup_group = app_commands.Group(
    name="setup",
    description="Configure the bot for this server (admin only)",
    default_permissions=discord.Permissions(manage_guild=True),
)


@setup_group.command(name="channel", description="Set the channel where alerts and leaderboards post")
@app_commands.describe(channel="The channel to use for bot alerts")
async def setup_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    await interaction.response.defer(ephemeral=True)
    try:
        await db.register_guild(interaction.guild_id, interaction.guild.name, interaction.guild.owner_id)
        await db.set_alert_channel(interaction.guild_id, channel.id)
        await interaction.followup.send(f"Alert channel set to {channel.mention}.", ephemeral=True)
    except Exception:
        logging.exception("setup_channel failed")
        await interaction.followup.send("Something went wrong saving that channel. Try again.", ephemeral=True)


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
# /roastme — Stock NPC roasts your watchlist picks
# ---------------------------------------------------------------------------

@bot.tree.command(name="roastme", description="Roast your stock picks — or someone else's")
@app_commands.describe(user="Who to roast (leave empty to roast yourself)")
async def roastme(interaction: discord.Interaction, user: discord.Member = None):
    await interaction.response.defer()

    requester = interaction.user
    target = user or requester

    # Rate limit check for the person triggering the command
    is_premium = await has_premium(interaction.guild_id)
    if not is_premium:
        used = _roasts_used(interaction.guild_id, requester.id)
        if used >= FREE_ROAST_LIMIT:
            await interaction.followup.send(
                f"You've used both your roasts for this week. "
                f"Upgrade to Pro for unlimited roasts: {upgrade_link(interaction.guild_id)}",
                ephemeral=True,
            )
            return

    # Get full server leaderboard for context
    rankings = await compute_leaderboard(interaction.guild)
    user_rank = next((r for r in rankings if r["user_id"] == target.id), None)

    entries = await db.get_member_watchlist_detailed(interaction.guild_id, target.id)
    no_picks = not entries

    pick_lines = []
    if not no_picks:
        symbols = [e["symbol"] for e in entries]
        quotes = await market.get_quotes(symbols)
        for entry in entries:
            sym = entry["symbol"]
            added = entry.get("added_price")
            q = quotes.get(sym)
            current = (q.get("close") or 0) if q else 0
            if added and added > 0:
                pct = (current - added) / added * 100
                pick_lines.append(f"  {sym}: {pct:+.2f}%")
            else:
                pick_lines.append(f"  {sym}: no price data")

    total = len(rankings)
    if user_rank:
        rank_num = user_rank["rank"]
        avg = user_rank["avg_gain"]
        rank_context = f"Rank #{rank_num} out of {total} in this server ({avg:+.2f}% avg)"
        # Percentile: 1 = best, total = worst
        percentile = rank_num / total if total > 0 else 0.5
    else:
        rank_context = "Not ranked (no tracked data yet)"
        percentile = 0.5

    # Build server standings for comparison
    server_lines = [
        f"  #{r['rank']} {r['name']}: {r['avg_gain']:+.2f}%"
        for r in rankings[:8]
    ]
    server_context = "\n".join(server_lines) if server_lines else "  (no one else has picks)"

    third_party = target != requester

    if no_picks:
        tone = "They have zero stocks. Not bottom of the leaderboard — not even on it. Roast them for not participating at all while everyone else has skin in the game."
        if third_party:
            setup = f"{requester.display_name} is calling out {target.display_name}, who hasn't added a single stock pick."
        else:
            setup = f"{target.display_name} asked to be roasted but hasn't added any stock picks."
        prompt = (
            f"{setup}\n\n"
            f"Person being roasted: {target.display_name}\n"
            f"Their picks: none — completely empty watchlist\n\n"
            f"Full server standings:\n{server_context}\n\n"
            f"Tone: {tone}\n"
            f"Reference what other people in the server are doing to make them feel left out."
        )
    else:
        if percentile <= 0.25:
            tone = "They're near the top of the server so keep it light — give them props but still find something to clown on."
        elif percentile <= 0.60:
            tone = "They're mid-pack. Balanced roast, point out what's working and what isn't."
        else:
            tone = "They're near the bottom of the server. Go ruthless. Destroy them. No mercy."

        if third_party:
            setup = f"{requester.display_name} is calling out {target.display_name}'s picks."
        else:
            setup = f"{target.display_name} asked to be roasted."

        prompt = (
            f"{setup}\n\n"
            f"Person being roasted: {target.display_name}\n"
            f"Their rank: {rank_context}\n"
            f"Their picks:\n" + "\n".join(pick_lines) + "\n\n"
            f"Full server standings:\n{server_context}\n\n"
            f"Tone: {tone}\n"
            f"Reference other people's performance to make it feel like a group chat moment, not a solo callout."
        )

    try:
        response = await get_openai().chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Stock NPC, a Gen-Z financial commentator in a Discord server. "
                        "Write a roast that feels like something a funny friend would text in a group chat. "
                        "It has to be witty and land naturally — if a joke is forced or try-hard, cut it. "
                        "Ruthless when the person is doing badly, respectful when they're winning. "
                        "Reference the server leaderboard to make comparisons. Keep it short. "
                        "Casual Gen-Z tone, emojis used sparingly and only when they actually add something. "
                        "NEVER use em dashes (—) under any circumstances. "
                        "NEVER use 'it's not X, it's Y' constructions — that's forced and try-hard. "
                        "Never use asterisks or markdown formatting."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=350,
        )
        roast = response.choices[0].message.content
    except Exception:
        logging.exception("OpenAI roastme failed")
        if no_picks:
            roast = "doesn't even have a single stock pick. watching from the sidelines while everyone else has skin in the game."
        elif percentile > 0.6:
            roast = "bro is bottom of the leaderboard and still asked to get roasted. respect the confidence at least 💀"
        else:
            roast = "solid picks honestly. still not beating the market tho lol"

    # Increment usage and build upsell if needed
    upsell = ""
    if not is_premium:
        _increment_roast(interaction.guild_id, requester.id)
        remaining = FREE_ROAST_LIMIT - _roasts_used(interaction.guild_id, requester.id)
        if remaining <= 0:
            upsell = f"\n\n*{requester.display_name}, that was your last free roast this week. Upgrade for unlimited: {upgrade_link(interaction.guild_id)}*"
        else:
            upsell = f"\n\n*{requester.display_name}: {remaining} roast{'s' if remaining != 1 else ''} left this week.*"

    ping = target.mention if target != requester else requester.mention
    await interaction.followup.send(f"{ping}\n{roast}{upsell}")


# ---------------------------------------------------------------------------
# /upgrade — show Pro features and checkout link
# ---------------------------------------------------------------------------

@bot.tree.command(name="upgrade", description="See what's included in StockNPC Pro and how to upgrade")
async def upgrade(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    is_pro = await has_premium(interaction.guild_id)
    if is_pro:
        await interaction.followup.send(
            "This server is already on **StockNPC Pro**. Use `/setup info` to check your config.",
            ephemeral=True,
        )
        return

    link = upgrade_link(interaction.guild_id)
    embed = discord.Embed(
        title="Upgrade to StockNPC Pro — $5/month",
        description=(
            f"**[Upgrade now]({link})**\n\n"
            "**What you get on Pro:**\n"
            "📋 **Unlimited watchlist picks** (free = 5 per person)\n"
            "🔔 **Unlimited price alerts** (free = 3 per person)\n"
            "🔥 **Unlimited `/roastme` uses** (free = 2 per person per week)\n"
            "🤖 **Daily Stock NPC leaderboard drops** — Stock NPC roasts your server's stock picks every market close\n"
            "📅 Weekly and monthly leaderboards posted automatically\n"
        ),
        color=discord.Color.gold(),
    )
    embed.set_footer(text="Billed monthly. Cancel anytime.")
    await interaction.followup.send(embed=embed, ephemeral=True)


# ---------------------------------------------------------------------------
# Background task: monitor price alerts every 30 minutes
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
# Background task: scheduled leaderboard at 4:05 PM ET on market days
# Daily Mon-Thu, Weekly Fri, Monthly last Fri of month — no duplicates
# ---------------------------------------------------------------------------

@tasks.loop(minutes=1)
async def scheduled_leaderboard():
    now = datetime.now(ET)

    if not (now.hour == 16 and now.minute == 5):
        return

    period = _get_leaderboard_period(now)
    if period is None:
        return

    period_label = {"daily": "today", "weekly": "this week", "monthly": "this month"}[period]

    try:
        all_guilds = await db.get_all_guilds()
    except Exception:
        logging.exception("Failed to fetch guilds for scheduled leaderboard")
        return

    for guild_row in all_guilds:
        guild_id = guild_row["id"]
        post_key = f"{guild_id}:{now.date()}"
        if post_key in _leaderboard_posted:
            continue

        guild = bot.get_guild(guild_id)
        if not guild:
            continue

        try:
            if not await db.is_premium(guild_id):
                continue

            settings = await db.get_settings(guild_id)
            channel_id = settings.get("alert_channel_id")
            if not channel_id:
                continue

            channel = bot.get_channel(channel_id)
            if not channel:
                continue

            rankings = await compute_leaderboard(guild)
            if not rankings:
                continue

            text = await generate_brainrot_announcement(period_label, rankings)
            await channel.send(text)
            _leaderboard_posted.add(post_key)
            logging.info(f"Posted {period} leaderboard to guild {guild_id}")

        except Exception:
            logging.exception(f"Failed to post leaderboard to guild {guild_id}")


@scheduled_leaderboard.before_loop
async def before_scheduled_leaderboard():
    await bot.wait_until_ready()


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

token = os.environ.get("DISCORD_TOKEN")
if not token:
    logging.error("DISCORD_TOKEN not set.")
    sys.exit(1)

bot.run(token, log_handler=None)
