# handlers/start.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError

async def start(update, context):
    bot = context.application.bot
    user = update.effective_user
    if not user:
        return
    
    try:
        # Verify user is a member of @Jaredrawing channel
        member = await bot.get_chat_member("@Jaredrawing", user.id)
        print(f"User {user.id} membership status on start: {member.status}")

        # Check if user is an active member (not left/kicked/banned)
        if member.status in ["member", "administrator", "creator"]:
            await show_member_options(update, context)
        else:
            await ask_to_join(update)
            
    except TelegramError as e:
        # Handle cases where bot can't access chat member info
        if "chat not found" in str(e).lower() or "user not found" in str(e).lower():
            print(f"Bot may not be admin in @Jaredrawing channel: {e}")
            await ask_to_join(update)
        else:
            print(f"Telegram error in start handler: {e}")
            await ask_to_join(update)
    except Exception as e:
        print(f"[start handler error]: {e}", flush=True)
        await ask_to_join(update)

async def ask_to_join(update):
    keyboard = [
        [InlineKeyboardButton("Join Channel", url="https://t.me/Jaredrawing")],
        [InlineKeyboardButton("I've Joined ✅", callback_data="check_membership")]
    ]
    
    message_text = (
        "👋 Welcome to Jared Drawing Bot!\n\n"
        "To access our full price list and services, "
        "please join our official channel first:\n"
        "📢 @Jaredrawing\n\n"
        "After joining, click 'I've Joined ✅' to continue."
    )
    
    await update.effective_chat.send_message(
        message_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_member_options(update, context):
    """Show options for members who have joined the channel"""
    keyboard = [
        [InlineKeyboardButton("View Price List", callback_data="nav_0")],
        [InlineKeyboardButton("Order Now", url="https://t.me/Ja_r_ed")]
    ]
    
    message_text = (
        "✅ Welcome to Jared Drawing Studio!\n\n"
        "Choose an option below to get started:"
    )
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            message_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.effective_chat.send_message(
            message_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def check_membership(update, context):
    """Check if user has joined after clicking the button"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    bot = context.application.bot
    
    try:
        # Re-check membership
        member = await bot.get_chat_member("@Jaredrawing", user.id)
        print(f"User {user.id} membership status on check_membership: {member.status}")

        if member.status in ["member", "administrator", "creator"]:
            await query.edit_message_text("✅ Thank you for joining! Here's our price list:")
            print(f"User {user.id} verified as member after re-check.")
            await show_member_options(update, context)
        else:
            await query.edit_message_text(
                "❌ I still don't see you in our channel. Please make sure you've joined @Jaredrawing and try again.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Join Channel", url="https://t.me/Jaredrawing")],
                    [InlineKeyboardButton("Try Again", callback_data="check_membership")]
                ])
            )
            
    except TelegramError as e:
        print(f"Error checking membership: {e}")
        await query.edit_message_text(
            "❌ Unable to verify channel membership. Please try again later.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Try Again", callback_data="check_membership")]
            ])
        )