"""Vercel serverless webhook entrypoint for the Jared Studio Telegram bot.

The bot is normally run as a polling worker (see bot.py). On Vercel the bot is
driven by Telegram instead: Telegram POSTs every update to this function.

Endpoints
---------
GET  /api/webhook  -> deployment diagnostics (bot, webhook status, config)
POST /api/webhook  -> Telegram update delivery

After deploying, register the webhook once:

    python scripts/set_webhook.py https://<your-deployment>.vercel.app/api/webhook
"""
import asyncio
import json
import logging
import os
from http.server import BaseHTTPRequestHandler

from telegram import Bot, Update
from telegram.ext import Application, PicklePersistence

# Import your handler-adding function from bot.py
from bot import add_handlers
from config import CREATOR_USER_ID, CREATOR_USER_IDS, CREATOR_USERNAMES, ORDER_CONTACT_CHAT_ID

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("webhook")

BOT_TOKEN = os.getenv("BOT_TOKEN")
# Optional: shared secret Telegram sends in X-Telegram-Bot-Api-Secret-Token.
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set in the environment")


def _persistence_path() -> str:
    """Unique per process so concurrent serverless instances don't corrupt the pickle."""
    return f"/tmp/bot_persistence_{os.getpid()}.pkl"


async def handle_request(body: str) -> None:
    """Builds the application, processes a single update, and shuts down."""
    persistence = PicklePersistence(filepath=_persistence_path())

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .persistence(persistence)
        .build()
    )

    # Add all your handlers
    add_handlers(application)

    await application.initialize()
    try:
        update = Update.de_json(json.loads(body), application.bot)
        await application.process_update(update)
    finally:
        await application.shutdown()


async def diagnostics() -> dict:
    """Collects the state you need to verify a deployment from a browser."""
    report = {
        "status": "ok",
        "env": {
            "BOT_TOKEN": bool(BOT_TOKEN),
            "WEBHOOK_SECRET": bool(WEBHOOK_SECRET),
            "CREATOR_USER_ID": CREATOR_USER_ID,
            "CREATOR_USER_IDS": CREATOR_USER_IDS,
            "CREATOR_USERNAMES": CREATOR_USERNAMES,
            "ORDER_CONTACT_CHAT_ID": ORDER_CONTACT_CHAT_ID,
        },
    }

    try:
        async with Bot(BOT_TOKEN) as bot:
            me = await bot.get_me()
            report["bot"] = {
                "id": me.id,
                "username": me.username,
                "name": me.first_name,
            }
            hook = await bot.get_webhook_info()
            report["webhook"] = {
                "url": hook.url,
                "pending_update_count": hook.pending_update_count,
                "last_error_message": hook.last_error_message,
                "last_error_date": hook.last_error_date,
            }
    except Exception as e:
        report["status"] = "error"
        report["error"] = str(e)

    try:
        from drawings import drawings
        report["price_items"] = len(drawings)
    except Exception as e:
        report["price_items"] = f"unavailable: {e}"

    return report


class handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _respond(self, code: int, payload: str) -> None:
        body = payload.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        """Diagnostics, so you can confirm the deployment without reading logs."""
        try:
            info = asyncio.run(diagnostics())
            self._respond(200, json.dumps(info, indent=2))
        except Exception as e:
            logger.exception("Error building diagnostics")
            self._respond(500, json.dumps({"status": "error", "error": str(e)}, indent=2))

    def do_POST(self) -> None:
        if WEBHOOK_SECRET:
            provided = self.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
            if provided != WEBHOOK_SECRET:
                logger.warning("Rejected update: invalid secret token")
                self._respond(403, "Forbidden")
                return

        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8") if content_length else ""

            # Process the update asynchronously
            asyncio.run(handle_request(body))

            self._respond(200, "ok")
        except Exception as e:
            logger.exception("Error processing update")
            self._respond(500, f"Error: {e}")
