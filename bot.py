# bot.py
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
import os
import threading
import http.server
import socketserver

load_dotenv()

# known handlers
from handlers.start import start
from handlers.navigation import navigate_drawings, main_menu
from handlers.order import order_conversation

# optional handlers (import if present)
try:
    from handlers.price_catalog import list_prices, show_price_detail
except Exception:
    list_prices = None
    show_price_detail = None

# try importing management handlers if you have them
try:
    from handlers.management import view_orders_handler, update_price_handler, add_catalogue_handler
except Exception:
    view_orders_handler = None
    update_price_handler = None
    add_catalogue_handler = None

def _start_dummy_http_server():
    """Start a tiny HTTP server in a daemon thread to bind PORT (for Render web services)."""
    port_raw = os.getenv("PORT") or os.getenv("RENDER_PORT") or "8080"
    try:
        port = int(port_raw)
    except Exception:
        port = 8080

    class _Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"OK")

        # quiet logging
        def log_message(self, format, *args):
            return

    def _serve():
        with socketserver.TCPServer(("0.0.0.0", port), _Handler) as httpd:
            print(f"Dummy HTTP server listening on 0.0.0.0:{port}")
            httpd.serve_forever()

    t = threading.Thread(target=_serve, daemon=True)
    t.start()

def main():
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN not found in environment variables")
        return

    # Start the dummy server so Render's port scan detects an open port.
    _start_dummy_http_server()

    application = Application.builder().token(BOT_TOKEN).build()

    # core handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(navigate_drawings, pattern="^nav_"))
    application.add_handler(CallbackQueryHandler(main_menu, pattern="^main_menu$"))
    application.add_handler(order_conversation)

    # register price handlers if available
    if list_prices and show_price_detail:
        application.add_handler(CommandHandler("prices", list_prices))
        application.add_handler(CallbackQueryHandler(list_prices, pattern="^price_list$"))
        application.add_handler(CallbackQueryHandler(show_price_detail, pattern="^price_"))

    # register management handlers if available
    if view_orders_handler:
        application.add_handler(view_orders_handler)
    if update_price_handler:
        application.add_handler(update_price_handler)
    if add_catalogue_handler:
        application.add_handler(add_catalogue_handler)

    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()