from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler, CallbackQueryHandler
from telegram.constants import ParseMode

async def start(update: Update, context: CallbackContext) -> None:
    """Sends a welcome message with the main menu."""
    user = update.effective_user

    # Import is_creator function
    from utils.helpers import is_creator

    if is_creator(user):
        keyboard = [
            [InlineKeyboardButton("🎨 Creator Panel", callback_data='creator_menu')],
            [InlineKeyboardButton("🛍️ Price List", callback_data='price_list')],
            [InlineKeyboardButton("📝 Place an Order", callback_data='order')],
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("🛍️ Price List", callback_data='price_list')],
            [InlineKeyboardButton("📝 Place an Order", callback_data='order')],
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        'Welcome to Jared Studio Bot! How can I help you today?',
        reply_markup=reply_markup
    )

async def back_to_main_menu(update: Update, context: CallbackContext) -> int:
    """Ends the conversation and sends a new main menu message."""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("🛍️ Price List", callback_data='price_list')],
        [InlineKeyboardButton("📝 Place an Order", callback_data='order')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send a new message instead of editing
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Welcome back to the main menu!',
        reply_markup=reply_markup
    )
    
    return ConversationHandler.END

# This handler can be used as a fallback in other conversation handlers
main_menu_handler = CallbackQueryHandler(back_to_main_menu, pattern="^main_menu$")

# Dummy implementation (button removed, so this won't be called from start menu)
async def check_membership(update: Update, context: CallbackContext):
    pass