# bot.py
import os
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import handlers
from handlers.start import start, check_membership
from handlers.navigation import navigate_drawings, main_menu

def main():
    # Get bot token from environment variables
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN not found in environment variables")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(check_membership, pattern="^check_membership$"))
    application.add_handler(CallbackQueryHandler(navigate_drawings, pattern="^nav_"))
    application.add_handler(CallbackQueryHandler(main_menu, pattern="^main_menu$"))
    
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()