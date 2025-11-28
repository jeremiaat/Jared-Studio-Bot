from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import TelegramError
from telegram.constants import ParseMode
from config.config import CREATOR_USER_ID
from utils.helpers import is_creator

# Detect whether management handlers exist (so we only show the button when functional)
try:
    import handlers.management as management  # noqa: F401
    MANAGEMENT_AVAILABLE = True
except Exception:
    MANAGEMENT_AVAILABLE = False

async def start(update: Update, context):
    """Handle /start - show welcome menu"""
    user = update.effective_user
    name = f"@{user.username}" if user and user.username else (user.full_name if user else "there")

    # For creators show management UI (only if management handlers are present)
    print(f"Debug: user.id={user.id if user else None}, CREATOR_USER_ID={CREATOR_USER_ID}, is_creator={is_creator(user) if user else False}, MANAGEMENT_AVAILABLE={MANAGEMENT_AVAILABLE}")
    if is_creator(user) and MANAGEMENT_AVAILABLE:
        print("Debug: Showing management UI for creator")
        keyboard = [
            [InlineKeyboardButton("Manage Orders", callback_data="manage_orders")],
            [InlineKeyboardButton("Edit Prices", callback_data="manage_prices")],
            [InlineKeyboardButton("Add Catalogue", callback_data="add_catalogue")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
        ]
    else:
        # Standard user UI
        keyboard = [
            [InlineKeyboardButton("View Price List", callback_data="price_list")],
            [InlineKeyboardButton("Order Now", callback_data="start_order")],
        ]

    text = (
        f"👋 Hello {name}!\n\n"
        "Welcome to Jared Studio. Choose an option below to continue."
    )

    try:
        await update.effective_message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)
    except TelegramError:
        try:
            await update.effective_chat.send_message(text, reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            pass


