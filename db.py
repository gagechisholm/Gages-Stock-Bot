import httpx
import logging
import os
from dotenv import load_dotenv

load_dotenv()

_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")


def _headers(extra_prefer: str = "") -> dict:
    prefer = "return=representation"
    if extra_prefer:
        prefer = f"{extra_prefer},{prefer}"
    return {
        "apikey": _KEY,
        "Authorization": f"Bearer {_KEY}",
        "Content-Type": "application/json",
        "Prefer": prefer,
    }


async def _get(table: str, params: dict, count: bool = False) -> tuple[list[dict], int]:
    headers = _headers()
    if count:
        headers["Prefer"] = "count=exact"
        headers["Range"] = "0-0"
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(f"{_URL}/rest/v1/{table}", params=params, headers=headers)
        r.raise_for_status()
        if count:
            cr = r.headers.get("content-range", "0/0")
            total = int(cr.split("/")[-1]) if "/" in cr else 0
            return [], total
        data = r.json()
        return (data if isinstance(data, list) else []), 0


async def _post(table: str, body: dict | list, on_conflict: str = "") -> list[dict]:
    params = {}
    prefer_extra = ""
    if on_conflict:
        params["on_conflict"] = on_conflict
        prefer_extra = "resolution=merge-duplicates"
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.post(
            f"{_URL}/rest/v1/{table}",
            params=params,
            json=body,
            headers=_headers(prefer_extra),
        )
        r.raise_for_status()
        data = r.json()
        return data if isinstance(data, list) else [data] if data else []


async def _patch(table: str, filters: dict, body: dict) -> list[dict]:
    params = {f"{k}": f"eq.{v}" for k, v in filters.items()}
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.patch(
            f"{_URL}/rest/v1/{table}",
            params=params,
            json=body,
            headers=_headers(),
        )
        r.raise_for_status()
        data = r.json()
        return data if isinstance(data, list) else [data] if data else []


async def _delete(table: str, filters: dict) -> list[dict]:
    params = {f"{k}": f"eq.{v}" for k, v in filters.items()}
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.delete(
            f"{_URL}/rest/v1/{table}",
            params=params,
            headers=_headers(),
        )
        r.raise_for_status()
        data = r.json()
        return data if isinstance(data, list) else [data] if data else []


# ---------------------------------------------------------------------------
# Guilds
# ---------------------------------------------------------------------------

async def register_guild(guild_id: int, guild_name: str, owner_id: int) -> None:
    await _post("guilds", {
        "id": guild_id,
        "name": guild_name,
        "owner_id": owner_id,
    }, on_conflict="id")


async def get_guild(guild_id: int) -> dict | None:
    rows, _ = await _get("guilds", {"id": f"eq.{guild_id}", "select": "*"})
    return rows[0] if rows else None


async def is_premium(guild_id: int) -> bool:
    guild = await get_guild(guild_id)
    if not guild:
        return False
    return guild.get("premium_tier", "free") != "free"


async def set_premium_tier(guild_id: int, tier: str) -> None:
    await _patch("guilds", {"id": guild_id}, {"premium_tier": tier})


async def set_stripe_customer(guild_id: int, customer_id: str) -> None:
    await _patch("guilds", {"id": guild_id}, {"stripe_customer_id": customer_id})


# ---------------------------------------------------------------------------
# Guild Settings
# ---------------------------------------------------------------------------

async def get_settings(guild_id: int) -> dict:
    rows, _ = await _get("guild_settings", {"guild_id": f"eq.{guild_id}", "select": "*"})
    return rows[0] if rows else {}


async def set_alert_channel(guild_id: int, channel_id: int) -> None:
    await _post("guild_settings", {
        "guild_id": guild_id,
        "alert_channel_id": channel_id,
    }, on_conflict="guild_id")


async def set_update_channel(guild_id: int, channel_id: int) -> None:
    await _post("guild_settings", {
        "guild_id": guild_id,
        "update_channel_id": channel_id,
    }, on_conflict="guild_id")


# ---------------------------------------------------------------------------
# Member Watchlists
# ---------------------------------------------------------------------------

async def get_member_watchlist(guild_id: int, user_id: int) -> list[str]:
    rows, _ = await _get("member_watchlists", {
        "guild_id": f"eq.{guild_id}",
        "user_id": f"eq.{user_id}",
        "select": "symbol",
    })
    return [r["symbol"] for r in rows]


async def add_to_member_watchlist(
    guild_id: int, user_id: int, symbol: str, added_price: float | None = None
) -> bool:
    try:
        row: dict = {
            "guild_id": guild_id,
            "user_id": user_id,
            "symbol": symbol.upper(),
        }
        if added_price is not None:
            row["added_price"] = added_price
        await _post("member_watchlists", row)
        return True
    except httpx.HTTPStatusError as e:
        body = e.response.text.lower()
        if "duplicate" in body or "unique" in body or "23505" in body:
            return False
        logging.exception(f"Error adding {symbol} to watchlist")
        return False
    except Exception:
        logging.exception(f"Error adding {symbol} to watchlist")
        return False


async def get_member_watchlist_detailed(guild_id: int, user_id: int) -> list[dict]:
    rows, _ = await _get("member_watchlists", {
        "guild_id": f"eq.{guild_id}",
        "user_id": f"eq.{user_id}",
        "select": "symbol,added_price,created_at",
    })
    return rows


async def get_all_guild_watchlists(guild_id: int) -> list[dict]:
    rows, _ = await _get("member_watchlists", {
        "guild_id": f"eq.{guild_id}",
        "added_price": "not.is.null",
        "select": "user_id,symbol,added_price",
    })
    return rows


async def get_all_guilds() -> list[dict]:
    rows, _ = await _get("guilds", {"select": "id"})
    return rows


async def remove_from_member_watchlist(guild_id: int, user_id: int, symbol: str) -> bool:
    rows = await _delete("member_watchlists", {
        "guild_id": guild_id,
        "user_id": user_id,
        "symbol": symbol.upper(),
    })
    return bool(rows)


# ---------------------------------------------------------------------------
# Server Watchlists
# ---------------------------------------------------------------------------

async def get_server_watchlist(guild_id: int) -> list[dict]:
    rows, _ = await _get("server_watchlists", {
        "guild_id": f"eq.{guild_id}",
        "select": "symbol,added_by,created_at",
        "order": "created_at.asc",
    })
    return rows


async def add_to_server_watchlist(guild_id: int, user_id: int, symbol: str) -> bool:
    try:
        await _post("server_watchlists", {
            "guild_id": guild_id,
            "symbol": symbol.upper(),
            "added_by": user_id,
        })
        return True
    except Exception:
        return False


async def remove_from_server_watchlist(guild_id: int, symbol: str) -> bool:
    rows = await _delete("server_watchlists", {
        "guild_id": guild_id,
        "symbol": symbol.upper(),
    })
    return bool(rows)


# ---------------------------------------------------------------------------
# Alerts
# ---------------------------------------------------------------------------

async def count_active_alerts(guild_id: int, user_id: int) -> int:
    _, total = await _get("alerts", {
        "guild_id": f"eq.{guild_id}",
        "user_id": f"eq.{user_id}",
        "active": "eq.true",
        "select": "id",
    }, count=True)
    return total


async def get_active_alerts(guild_id: int, user_id: int) -> list[dict]:
    rows, _ = await _get("alerts", {
        "guild_id": f"eq.{guild_id}",
        "user_id": f"eq.{user_id}",
        "active": "eq.true",
        "select": "*",
    })
    return rows


async def get_all_active_alerts() -> list[dict]:
    rows, _ = await _get("alerts", {"active": "eq.true", "select": "*"})
    return rows


async def create_alert(
    guild_id: int,
    user_id: int,
    symbol: str,
    threshold_pct: float,
    direction: str,
    channel_id: int,
) -> dict | None:
    rows = await _post("alerts", {
        "guild_id": guild_id,
        "user_id": user_id,
        "symbol": symbol.upper(),
        "threshold_pct": threshold_pct,
        "direction": direction,
        "channel_id": channel_id,
        "active": True,
    })
    return rows[0] if rows else None


async def deactivate_alert(alert_id: str) -> None:
    await _patch("alerts", {"id": alert_id}, {"active": False})
