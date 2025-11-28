from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import TelegramError
from telegram.constants import ParseMode
from config import CREATOR_USER_ID, CHANNEL_USERNAME
from utils.helpers import is_creator

# Detect whether management handlers exist (so we only show the button when functional)
try:
    import handlers.management as management  # noqa: F401
    MANAGEMENT_AVAILABLE = True
except Exception:
    MANAGEMENT_AVAILABLE = False

async def show_main_menu(update: Update, context, name: str, user):
    """Displays the main menu, differentiating between creators and standard users."""
    try:
        if is_creator(user):
            if MANAGEMENT_AVAILABLE:
                keyboard = [
                    [InlineKeyboardButton("Manage Orders", callback_data="manage_orders")],
                    [InlineKeyboardButton("Edit Prices", callback_data="manage_prices")],
                    [InlineKeyboardButton("Add Catalogue", callback_data="add_catalogue")],
                ]
                text = f"👋 Hello Creator {name}!\n\nWelcome to the management panel."
            else:
                text = f"Hello Creator {name}! Management module is not available."
                keyboard = []
        else:
            # Standard user UI for channel members
            keyboard = [
                [InlineKeyboardButton("View Price List", callback_data="price_list")],
                [InlineKeyboardButton("Order Now", callback_data="start_order")],
            ]
            text = (
                f"👋 Hello {name}!\n\n"
                "Welcome to Jared Studio. Choose an option below to continue."
            )
        
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        
        # If it's a callback, edit the message. Otherwise, reply.
        if update.callback_query:
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        else:
            await update.effective_message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    except Exception as e:
        print(f"[DEBUG] Error in show_main_menu: {e}")

async def start(update: Update, context):
    """Handle /start - show welcome menu"""
    user = update.effective_user
    name = f"@{user.username}" if user and user.username else (user.full_name if user else "there")

    # Check channel membership for non-creators
    if not is_creator(user):
        bot = context.application.bot
        channel_username = "@Jaredrawing"
        try:
            member = await bot.get_chat_member(channel_username, user.id)
            is_member = member.status in ["member", "administrator", "creator"]
        except Exception as e:
            print(f"Membership check failed: {e}")
            is_member = False

        if not is_member:
            join_url = f"https://t.me/{channel_username.lstrip('@')}"
            keyboard = [
                [InlineKeyboardButton("Join Channel", url=join_url)],
                [InlineKeyboardButton("I Joined ✅", callback_data="check_membership")]
            ]
            text = (
                f"👋 Hello {name}!\n\n"
                f"Welcome to Jared Studio. To access our services, you must first join our channel: {channel_username}\n\n"
                "Please join the channel and then click 'Check Membership' to continue."
            )
            try:
                await update.effective_message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)
            except TelegramError:
                try:
                    await update.effective_chat.send_message(text, reply_markup=InlineKeyboardMarkup(keyboard))
                except Exception:
                    pass
            return

    # If we get here, the user is a member (or a creator), so show the main menu.
    await show_main_menu(update, context, name, user)

async def check_membership(update: Update, context):
    """Handle membership check callback"""
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    name = f"@{user.username}" if user and user.username else (user.full_name if user else "there")

    # Check channel membership
    bot = context.application.bot
    channel_username = CHANNEL_USERNAME or "@Jaredrawing"
    try:
        member = await bot.get_chat_member(channel_username, user.id)
        is_member = member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"Membership check failed: {e}")
        is_member = False

    if is_member:
        # User is a member, show the main menu.
        await show_main_menu(update, context, name, user)
    else:
        join_url = f"https://t.me/{channel_username.lstrip('@')}"
        keyboard = [
            [InlineKeyboardButton("Join Channel", url=join_url)],
            [InlineKeyboardButton("I Joined ✅", callback_data="check_membership")]
        ]
        text = (
            f"❌ {name}, you are not yet a member of our channel.\n\n"
            f"Please join {channel_username} and then click 'Check Membership' to continue."
        )
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)

async def check_membership_order(update: Update, context):
    """Handle membership check callback for order flow"""
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    name = f"@{user.username}" if user and user.username else (user.full_name if user else "there")

    # If creator, show management menu instead of proceeding with order flow
    if is_creator(user):
        return await show_main_menu(update, context, name, user)

    # Check channel membership
    bot = context.application.bot
    channel_username = CHANNEL_USERNAME or "@Jaredrawing"
    try:
        member = await bot.get_chat_member(channel_username, user.id)
        is_member = member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"Membership check failed: {e}")
        is_member = False

    if is_member:
        # Start order process
        from .order import start_order
        # Simulate starting order by calling the function with modified update
        update.callback_query.data = "start_order"
        return await start_order(update, context)
    else:
        join_url = f"https://t.me/{channel_username.lstrip('@')}"
        keyboard = [
            [InlineKeyboardButton("Join Channel", url=join_url)],
            [InlineKeyboardButton("I Joined ✅", callback_data="check_membership_order")]
        ]
        text = (
            f"❌ {name}, you are not yet a member of our channel.\n\n"
            f"Please join {channel_username} and then click 'Check Membership' to continue with your order."
        )
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)

async def back_to_main_menu(update: Update, context):
    """Handler for the 'main_menu' callback button.
    This function is crucial for ensuring the correct menu is always shown.
    """
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    name = f"@{user.username}" if user and user.username else (user.full_name if user else "there")

    await show_main_menu(update, context, name, user)
