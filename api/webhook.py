"""Vercel serverless webhook entrypoint for the Jared Studio Telegram bot.

The bot is normally run as a polling worker (see bot.py). On Vercel the bot is
driven by Telegram instead: Telegram POSTs every update to this function.

After deploying, register the webhook once:

    python scripts/set_webhook.py https://<your-deployment>.vercel.app/api/webhook
"""
import asyncio
import json
import logging
import os
from http.server import BaseHTTPRequestHandler

from telegram import Update
from telegram.ext import Application, PicklePersistence

# Import your handler-adding function from bot.py
from bot import add_handlers

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
        """Health check so you can confirm the function is live."""
        self._respond(200, "Jared Studio Bot webhook is running.\n")

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
