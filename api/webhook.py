import asyncio
import json
import logging
from http.server import BaseHTTPRequestHandler

import telegram

# Make sure to import the application object from your bot.py
from bot import application


async def handle_update(body):
    """Asynchronously initialize the application, process the update, and shut down."""
    await application.initialize()
    update = telegram.Update.de_json(json.loads(body), application.bot)
    await application.process_update(update)
    await application.shutdown()

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """
        Handles incoming POST requests from Telegram.
        """
        try:
            # Get the request body
            content_length = int(self.headers["Content-Length"])
            body = self.rfile.read(content_length)
            
            # Run the async handler
            asyncio.run(handle_update(body))

            # Send a 200 OK response
            self.send_response(200)
            self.end_headers()
        except Exception as e:
            logging.error(f"Error processing update: {e}")
            self.send_response(500)
            self.end_headers()