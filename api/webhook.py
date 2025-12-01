import asyncio
import json
import logging
from http.server import BaseHTTPRequestHandler

import telegram

# Make sure to import the application object from your bot.py
from bot import application


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """
        Handles incoming POST requests from Telegram.
        """
        try:
            # Get the request body
            content_length = int(self.headers["Content-Length"])
            body = self.rfile.read(content_length)
            
            # Parse the update and process it
            update = telegram.Update.de_json(json.loads(body), application.bot)
            asyncio.run(application.process_update(update))
            
            # Send a 200 OK response
            self.send_response(200)
            self.end_headers()
        except Exception as e:
            logging.error(f"Error processing update: {e}")
            self.send_response(500)
            self.end_headers()