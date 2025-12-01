# bot.py
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
import os
import threading

# Load environment variables from .env file for production
load_dotenv()

# known handlers
from handlers.start import start, back_to_main_menu
from handlers.start import check_membership, check_membership_order
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

BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    print("Error: BOT_TOKEN not found in environment variables")
    exit(1)

application = Application.builder().token(BOT_TOKEN).build()

# core handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(back_to_main_menu, pattern="^main_menu$"))
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