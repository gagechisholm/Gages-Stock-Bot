from flask import Flask, jsonify, redirect, request
import os
import urllib.parse
import logging
import asyncio
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

import db

load_dotenv()

app = Flask(__name__)

handler = RotatingFileHandler("app.log", maxBytes=10 * 1024 * 1024, backupCount=5)
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

DISCORD_CLIENT_ID     = os.environ.get("DISCORD_CLIENT_ID", "")
DISCORD_CLIENT_SECRET = os.environ.get("DISCORD_CLIENT_SECRET", "")
DISCORD_REDIRECT_URI  = os.environ.get("DISCORD_REDIRECT_URI", "http://localhost:5000/auth/callback")
FRONTEND_URL          = os.environ.get("FRONTEND_URL", "http://localhost:8080")

# Permissions: VIEW_CHANNEL + SEND_MESSAGES + EMBED_LINKS + READ_MESSAGE_HISTORY
BOT_PERMISSIONS = 84992


# ---------------------------------------------------------------------------
# Discord OAuth — install flow
# ---------------------------------------------------------------------------

@app.route("/auth/discord")
def auth_discord():
    """Redirect the user to Discord's bot-install OAuth page."""
    params = urllib.parse.urlencode({
        "client_id": DISCORD_CLIENT_ID,
        "permissions": BOT_PERMISSIONS,
        "scope": "bot applications.commands",
        "redirect_uri": DISCORD_REDIRECT_URI,
        "response_type": "code",
    })
    return redirect(f"https://discord.com/api/oauth2/authorize?{params}")


@app.route("/auth/callback")
def auth_callback():
    """
    Discord redirects here after the user installs the bot.
    guild_id is provided automatically in the query string.
    The bot's on_guild_join event handles full registration;
    this endpoint just captures the guild early and redirects to success.
    """
    guild_id  = request.args.get("guild_id")
    error     = request.args.get("error")

    if error:
        app.logger.warning(f"OAuth error: {error}")
        return redirect(f"{FRONTEND_URL}?error=cancelled")

    if guild_id:
        try:
            # Register the guild immediately so it's in Supabase before the bot event fires
            asyncio.run(db.register_guild(int(guild_id), "Pending", 0))
            app.logger.info(f"Registered guild {guild_id} via OAuth callback")
        except Exception:
            app.logger.exception("Failed to register guild in OAuth callback")

    return redirect(f"{FRONTEND_URL}?installed=true&guild_id={guild_id or ''}")


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------

@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/logs")
def get_logs():
    if not os.path.exists("app.log"):
        return jsonify({"logs": []}), 200
    with open("app.log") as f:
        logs = f.readlines()[-200:]
    return jsonify({"logs": logs})


if __name__ == "__main__":
    app.run()
