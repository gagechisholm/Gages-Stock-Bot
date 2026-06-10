import asyncio
import logging
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

_client: Client | None = None


def get_client() -> Client:
    global _client
    if _client is None:
        url = os.environ["SUPABASE_URL"]
        key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
        _client = create_client(url, key)
    return _client


# Run sync supabase calls off the event loop
async def _run(fn):
    return await asyncio.to_thread(fn)


# ---------------------------------------------------------------------------
# Guilds
# ---------------------------------------------------------------------------

async def register_guild(guild_id: int, guild_name: str, owner_id: int) -> None:
    await _run(lambda: get_client().table("guilds").upsert({
        "id": guild_id,
        "name": guild_name,
        "owner_id": owner_id,
    }, on_conflict="id").execute())


async def get_guild(guild_id: int) -> dict | None:
    result = await _run(lambda: get_client().table("guilds")
        .select("*")
        .eq("id", guild_id)
        .maybe_single()
        .execute())
    return result.data


async def is_premium(guild_id: int) -> bool:
    guild = await get_guild(guild_id)
    if not guild:
        return False
    return guild.get("premium_tier", "free") != "free"


async def set_premium_tier(guild_id: int, tier: str) -> None:
    await _run(lambda: get_client().table("guilds")
        .update({"premium_tier": tier})
        .eq("id", guild_id)
        .execute())


async def set_stripe_customer(guild_id: int, customer_id: str) -> None:
    await _run(lambda: get_client().table("guilds")
        .update({"stripe_customer_id": customer_id})
        .eq("id", guild_id)
        .execute())


# ---------------------------------------------------------------------------
# Guild Settings
# ---------------------------------------------------------------------------

async def get_settings(guild_id: int) -> dict:
    result = await _run(lambda: get_client().table("guild_settings")
        .select("*")
        .eq("guild_id", guild_id)
        .maybe_single()
        .execute())
    return result.data or {}


async def set_alert_channel(guild_id: int, channel_id: int) -> None:
    await _run(lambda: get_client().table("guild_settings").upsert({
        "guild_id": guild_id,
        "alert_channel_id": channel_id,
    }, on_conflict="guild_id").execute())


async def set_update_channel(guild_id: int, channel_id: int) -> None:
    await _run(lambda: get_client().table("guild_settings").upsert({
        "guild_id": guild_id,
        "update_channel_id": channel_id,
    }, on_conflict="guild_id").execute())


# ---------------------------------------------------------------------------
# Member Watchlists
# ---------------------------------------------------------------------------

async def get_member_watchlist(guild_id: int, user_id: int) -> list[str]:
    result = await _run(lambda: get_client().table("member_watchlists")
        .select("symbol")
        .eq("guild_id", guild_id)
        .eq("user_id", user_id)
        .execute())
    return [row["symbol"] for row in (result.data or [])]


async def add_to_member_watchlist(
    guild_id: int, user_id: int, symbol: str, added_price: float | None = None
) -> bool:
    try:
        row = {"guild_id": guild_id, "user_id": user_id, "symbol": symbol.upper()}
        if added_price is not None:
            row["added_price"] = added_price
        await _run(lambda: get_client().table("member_watchlists").insert(row).execute())
        return True
    except Exception as e:
        if "duplicate" in str(e).lower() or "unique" in str(e).lower():
            return False
        logging.exception(f"Error adding {symbol} to watchlist")
        return False


async def get_member_watchlist_detailed(guild_id: int, user_id: int) -> list[dict]:
    result = await _run(lambda: get_client().table("member_watchlists")
        .select("symbol, added_price, created_at")
        .eq("guild_id", guild_id)
        .eq("user_id", user_id)
        .execute())
    return result.data or []


async def get_all_guild_watchlists(guild_id: int) -> list[dict]:
    """All watchlist entries for a guild with added_price, for leaderboard computation."""
    result = await _run(lambda: get_client().table("member_watchlists")
        .select("user_id, symbol, added_price")
        .eq("guild_id", guild_id)
        .not_.is_("added_price", "null")
        .execute())
    return result.data or []


async def get_all_guilds() -> list[dict]:
    result = await _run(lambda: get_client().table("guilds").select("id").execute())
    return result.data or []


async def remove_from_member_watchlist(guild_id: int, user_id: int, symbol: str) -> bool:
    result = await _run(lambda: get_client().table("member_watchlists")
        .delete()
        .eq("guild_id", guild_id)
        .eq("user_id", user_id)
        .eq("symbol", symbol.upper())
        .execute())
    return bool(result.data)


# ---------------------------------------------------------------------------
# Server Watchlists
# ---------------------------------------------------------------------------

async def get_server_watchlist(guild_id: int) -> list[dict]:
    result = await _run(lambda: get_client().table("server_watchlists")
        .select("symbol, added_by, created_at")
        .eq("guild_id", guild_id)
        .order("created_at")
        .execute())
    return result.data or []


async def add_to_server_watchlist(guild_id: int, user_id: int, symbol: str) -> bool:
    try:
        await _run(lambda: get_client().table("server_watchlists").insert({
            "guild_id": guild_id,
            "symbol": symbol.upper(),
            "added_by": user_id,
        }).execute())
        return True
    except Exception:
        return False


async def remove_from_server_watchlist(guild_id: int, symbol: str) -> bool:
    result = await _run(lambda: get_client().table("server_watchlists")
        .delete()
        .eq("guild_id", guild_id)
        .eq("symbol", symbol.upper())
        .execute())
    return bool(result.data)


# ---------------------------------------------------------------------------
# Alerts
# ---------------------------------------------------------------------------

async def get_active_alerts(guild_id: int, user_id: int) -> list[dict]:
    result = await _run(lambda: get_client().table("alerts")
        .select("*")
        .eq("guild_id", guild_id)
        .eq("user_id", user_id)
        .eq("active", True)
        .execute())
    return result.data or []


async def get_all_active_alerts() -> list[dict]:
    result = await _run(lambda: get_client().table("alerts")
        .select("*")
        .eq("active", True)
        .execute())
    return result.data or []


async def create_alert(
    guild_id: int,
    user_id: int,
    symbol: str,
    threshold_pct: float,
    direction: str,
    channel_id: int,
) -> dict | None:
    result = await _run(lambda: get_client().table("alerts").insert({
        "guild_id": guild_id,
        "user_id": user_id,
        "symbol": symbol.upper(),
        "threshold_pct": threshold_pct,
        "direction": direction,
        "channel_id": channel_id,
        "active": True,
    }).execute())
    return result.data[0] if result.data else None


async def deactivate_alert(alert_id: str) -> None:
    await _run(lambda: get_client().table("alerts")
        .update({"active": False})
        .eq("id", alert_id)
        .execute())


# ---------------------------------------------------------------------------
# Paper Portfolios / Leaderboard
# ---------------------------------------------------------------------------

async def get_portfolio(guild_id: int, user_id: int) -> list[dict]:
    result = await _run(lambda: get_client().table("portfolios")
        .select("*")
        .eq("guild_id", guild_id)
        .eq("user_id", user_id)
        .execute())
    return result.data or []


async def upsert_portfolio_holding(
    guild_id: int, user_id: int, symbol: str, shares: float, avg_cost: float
) -> None:
    await _run(lambda: get_client().table("portfolios").upsert({
        "guild_id": guild_id,
        "user_id": user_id,
        "symbol": symbol.upper(),
        "shares": shares,
        "avg_cost": avg_cost,
    }, on_conflict="guild_id,user_id,symbol").execute())


async def remove_portfolio_holding(guild_id: int, user_id: int, symbol: str) -> None:
    await _run(lambda: get_client().table("portfolios")
        .delete()
        .eq("guild_id", guild_id)
        .eq("user_id", user_id)
        .eq("symbol", symbol.upper())
        .execute())


async def log_trade(
    guild_id: int, user_id: int, symbol: str, action: str, shares: float, price: float
) -> None:
    await _run(lambda: get_client().table("trades").insert({
        "guild_id": guild_id,
        "user_id": user_id,
        "symbol": symbol.upper(),
        "action": action,
        "shares": shares,
        "price": price,
    }).execute())


async def get_leaderboard(guild_id: int, limit: int = 10) -> list[dict]:
    """Returns top portfolio holders ranked by unrealized gain % (computed at query time)."""
    result = await _run(lambda: get_client().table("portfolios")
        .select("user_id, symbol, shares, avg_cost")
        .eq("guild_id", guild_id)
        .execute())
    return result.data or []
