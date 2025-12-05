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

async def check_membership_order(update: Update, context: CallbackContext):
    """Re-checks membership after user clicks 'I Joined ✅' during order process."""
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    bot = context.application.bot

    try:
        member = await bot.get_chat_member("@Jaredrawing", user.id)
        is_member = member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"Membership re-check failed: {e}")
        is_member = False

    if is_member:
        # If now a member, send the size selection to restart the order process
        context.user_data['order'] = {} # Clear any previous partial order data
        keyboard = [
            [InlineKeyboardButton("A4", callback_data="size_A4")],
            [InlineKeyboardButton("A3", callback_data="size_A3")]
        ]
        await query.edit_message_text(
            "✅ You are now a member! Let's continue with your order.\n\n"
            "🎨 *Select Size*\n\nChoose the paper size for your drawing:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
        return 0 # Corresponds to the SIZE state in order_conversation
    else:
        # Still not a member, re-prompt
        join_url = "https://t.me/Jaredrawing"
        keyboard = [
            [InlineKeyboardButton("Join Channel", url=join_url)],
            [InlineKeyboardButton("Check Membership", callback_data="check_membership_order")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
        ]
        await query.edit_message_text(
            "ℹ️ You are still not a member of @Jaredrawing.\n\n"
            "Please join the channel and try again:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )