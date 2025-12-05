# bot.py
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, PicklePersistence
import os, logging
import threading

# Load environment variables from .env file for production
load_dotenv()

# known handlers
from handlers.start import start, main_menu_handler
from handlers.start import check_membership, check_membership_order
from handlers.order import order_conversation

# optional handlers (import if present)
try:
    from handlers.price_catalog import list_prices, price_list_conversation
except Exception:
    list_prices = None
    price_list_conversation = None

# try importing management handlers if you have them
# try importing creator handlers if you have them
try:
    from handlers.creator import (
        creator_menu_handler, edit_catalog_handler, edit_item_handler, edit_field_handler,
        add_item_conversation, delete_item_handler, confirm_delete_handler, execute_delete_handler,
        manage_orders_handler, manage_order_handler, order_complete_handler, edit_item_conversation
    )
except Exception:
    creator_menu_handler = None
    edit_catalog_handler = None
    edit_item_handler = None
    edit_field_handler = None
    add_item_conversation = None
    delete_item_handler = None
    confirm_delete_handler = None
    execute_delete_handler = None
    manage_orders_handler = None
    manage_order_handler = None
    order_complete_handler = None
    edit_item_conversation = None

BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    print("Error: BOT_TOKEN not found in environment variables")
    exit(1)

def add_handlers(application: Application):
    """Add all handlers to the application."""
    # core handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(main_menu_handler)
    application.add_handler(CallbackQueryHandler(check_membership, pattern="^check_membership$"))
    application.add_handler(CallbackQueryHandler(check_membership_order, pattern="^check_membership_order$"))
    application.add_handler(order_conversation)

    # register price handlers if available
    if list_prices and price_list_conversation:
        # Separate command handler for /prices
        application.add_handler(CommandHandler("prices", list_prices))
        # Add the conversation handler for interactive price list browsing
        application.add_handler(price_list_conversation)

    # register creator handlers if available
    if creator_menu_handler:
        application.add_handler(creator_menu_handler)
    if edit_catalog_handler:
        application.add_handler(edit_catalog_handler)
    if edit_item_handler:
        application.add_handler(edit_item_handler)
    if edit_field_handler:
        application.add_handler(edit_field_handler)
    if add_item_conversation:
        application.add_handler(add_item_conversation)
    if delete_item_handler:
        application.add_handler(delete_item_handler)
    if confirm_delete_handler:
        application.add_handler(confirm_delete_handler)
    if execute_delete_handler:
        application.add_handler(execute_delete_handler)
    if manage_orders_handler:
        application.add_handler(manage_orders_handler)
    if manage_order_handler:
        application.add_handler(manage_order_handler)
    if order_complete_handler:
        application.add_handler(order_complete_handler)
    if edit_item_conversation:
        application.add_handler(edit_item_conversation)

# This part is for local development (polling) and will not be used by Vercel
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    persistence = PicklePersistence(filepath="bot_persistence")
    application = Application.builder().token(BOT_TOKEN).persistence(persistence).build()
    add_handlers(application)
    print("Bot is running in polling mode...")
    application.run_polling()