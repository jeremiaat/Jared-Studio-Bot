import asyncio
import json
import logging
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

import telegram
from telegram import Update
from telegram.ext import Application, PicklePersistence

# Import your handler-adding function from bot.py
from bot import add_handlers

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def handle_request(body: str):
    """
    Builds the application, processes a single update, and shuts down.
    This is the serverless-friendly approach.
    """
    persistence = PicklePersistence(filepath="/tmp/bot_persistence")
    
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .persistence(persistence)
        .build()
    )

    # Add all your handlers
    add_handlers(application)

    await application.initialize()
    update = Update.de_json(json.loads(body), application.bot)
    await application.process_update(update)
    await application.shutdown()

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers["Content-Length"])
            body = self.rfile.read(content_length).decode("utf-8")

            # Process the update asynchronously
            asyncio.run(handle_request(body))

            # Send a 200 OK response
            self.send_response(200)
            self.end_headers()
        except Exception as e:
            logging.error(f"Error processing update: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Error: {e}".encode("utf-8"))