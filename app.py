from flask import Flask, jsonify, redirect, request, abort
import os
import urllib.parse
import logging
import asyncio
import stripe
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

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
STRIPE_SECRET_KEY     = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
STRIPE_PRO_PRICE_ID   = os.environ.get("STRIPE_PRO_PRICE_ID", "")

stripe.api_key = STRIPE_SECRET_KEY

BOT_PERMISSIONS = 84992

# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://",
)

# ---------------------------------------------------------------------------
# Security headers on every response
# ---------------------------------------------------------------------------

@app.after_request
def set_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    frontend = FRONTEND_URL.rstrip("/")
    response.headers["Access-Control-Allow-Origin"] = frontend
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST"
    return response


# ---------------------------------------------------------------------------
# Discord OAuth — install flow
# ---------------------------------------------------------------------------

@app.route("/auth/discord")
@limiter.limit("30 per minute")
def auth_discord():
    params = urllib.parse.urlencode({
        "client_id": DISCORD_CLIENT_ID,
        "permissions": BOT_PERMISSIONS,
        "scope": "bot applications.commands",
        "redirect_uri": DISCORD_REDIRECT_URI,
        "response_type": "code",
    })
    return redirect(f"https://discord.com/api/oauth2/authorize?{params}")


@app.route("/auth/callback")
@limiter.limit("30 per minute")
def auth_callback():
    guild_id = request.args.get("guild_id")
    error    = request.args.get("error")

    if error:
        app.logger.warning(f"OAuth error: {error}")
        return redirect(f"{FRONTEND_URL}?error=cancelled")

    if guild_id:
        try:
            asyncio.run(db.register_guild(int(guild_id), "Pending", 0))
            app.logger.info(f"Registered guild {guild_id} via OAuth callback")
        except Exception:
            app.logger.exception("Failed to register guild in OAuth callback")

    return redirect(f"{FRONTEND_URL}?installed=true&guild_id={guild_id or ''}")


# ---------------------------------------------------------------------------
# Stripe — checkout session creation
# ---------------------------------------------------------------------------

@app.route("/stripe/checkout")
@limiter.limit("20 per minute")
def stripe_checkout():
    guild_id = request.args.get("guild_id")
    if not guild_id:
        return jsonify({"error": "guild_id required"}), 400

    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            automatic_payment_methods={"enabled": True},
            line_items=[{"price": STRIPE_PRO_PRICE_ID, "quantity": 1}],
            metadata={"guild_id": guild_id},
            subscription_data={"metadata": {"guild_id": guild_id}},
            success_url=f"{FRONTEND_URL}?upgraded=true&guild_id={guild_id}",
            cancel_url=f"{FRONTEND_URL}?cancelled=true",
        )
        return redirect(session.url)
    except Exception as e:
        app.logger.exception("Stripe checkout creation failed")
        return jsonify({"error": "Failed to create checkout session", "detail": str(e)}), 500


# ---------------------------------------------------------------------------
# Stripe — webhook (must be raw body, no JSON parsing)
# ---------------------------------------------------------------------------

@app.route("/stripe/webhook", methods=["POST"])
def stripe_webhook():
    payload   = request.get_data(as_text=False)
    sig_header = request.headers.get("Stripe-Signature", "")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except stripe.error.SignatureVerificationError:
        app.logger.warning("Invalid Stripe webhook signature")
        abort(400)
    except Exception:
        app.logger.exception("Stripe webhook parsing error")
        abort(400)

    event_type = event["type"]
    app.logger.info(f"Stripe webhook: {event_type}")

    if event_type == "checkout.session.completed":
        session     = event["data"]["object"]
        guild_id    = session.get("metadata", {}).get("guild_id")
        customer_id = session.get("customer")
        if guild_id:
            try:
                asyncio.run(db.set_premium_tier(int(guild_id), "pro"))
                if customer_id:
                    asyncio.run(db.set_stripe_customer(int(guild_id), customer_id))
                app.logger.info(f"Guild {guild_id} upgraded to pro")
            except Exception:
                app.logger.exception(f"Failed to upgrade guild {guild_id}")

    elif event_type in ("customer.subscription.deleted", "customer.subscription.paused"):
        subscription = event["data"]["object"]
        guild_id = subscription.get("metadata", {}).get("guild_id")
        if guild_id:
            try:
                asyncio.run(db.set_premium_tier(int(guild_id), "free"))
                app.logger.info(f"Guild {guild_id} downgraded to free")
            except Exception:
                app.logger.exception(f"Failed to downgrade guild {guild_id}")

    return jsonify({"status": "ok"})


# ---------------------------------------------------------------------------
# Stripe — customer billing portal (manage/cancel subscription)
# ---------------------------------------------------------------------------

@app.route("/stripe/portal")
@limiter.limit("20 per minute")
def stripe_portal():
    guild_id = request.args.get("guild_id")
    if not guild_id:
        return jsonify({"error": "guild_id required"}), 400

    try:
        guild = asyncio.run(db.get_guild(int(guild_id)))
        customer_id = guild.get("stripe_customer_id") if guild else None
        if not customer_id:
            return jsonify({"error": "No billing account found"}), 404

        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=f"{FRONTEND_URL}?guild_id={guild_id}",
        )
        return redirect(session.url)
    except Exception:
        app.logger.exception("Stripe portal creation failed")
        return jsonify({"error": "Failed to open billing portal"}), 500


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
