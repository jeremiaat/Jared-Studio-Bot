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

def add_handlers(application: Application):
    """Add all handlers to the application."""
    # core handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(main_menu_handler)
    application.add_handler(CallbackQueryHandler(check_membership, pattern="^check_membership$"))
    application.add_handler(CallbackQueryHandler(check_membership_order, pattern="^check_membership_order$"))
    application.add_handler(order_conversation)

    # register price handlers if available
    if list_prices and show_price_detail:
        price_list_conversation = ConversationHandler(
            entry_points=[
                CommandHandler("prices", list_prices),
                CallbackQueryHandler(list_prices, pattern="^price_list$"),
            ],
            states={
                # Assuming show_price_detail is a state. Add more states if needed.
                "SHOW_DETAIL": [CallbackQueryHandler(show_price_detail, pattern="^price_")],
            },
            fallbacks=[main_menu_handler],
            map_to_parent={ConversationHandler.END: ConversationHandler.END}
        )
        application.add_handler(price_list_conversation)

    # register management handlers if available
    if view_orders_handler:
        application.add_handler(view_orders_handler)
    if update_price_handler:
        application.add_handler(update_price_handler)
    if add_catalogue_handler:
        application.add_handler(add_catalogue_handler)

# This part is for local development (polling) and will not be used by Vercel
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    persistence = PicklePersistence(filepath="bot_persistence")
    application = Application.builder().token(BOT_TOKEN).persistence(persistence).build()
    add_handlers(application)
    print("Bot is running in polling mode...")
    application.run_polling()