# handlers/navigation.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from drawings import drawings, get_drawing_message

async def navigate_drawings(update, context):
    """Handle navigation between drawings"""
    query = update.callback_query

    # Answer the query immediately to avoid timeout
    try:
        await query.answer()
    except Exception as e:
        print(f"Query answer failed (likely timeout): {e}")
        return

    # Extract index from callback data (format: "nav_0", "nav_1", etc.)
    try:
        index = int(query.data.split('_')[1])
        await show_drawing(update, context, index)
    except (IndexError, ValueError) as e:
        print(f"Error parsing callback data: {query.data} - {e}")
        try:
            await query.answer("Navigation error", show_alert=True)
        except Exception as e2:
            print(f"Failed to show navigation error: {e2}")

async def show_drawing(update, context, index):
    """Show a specific drawing"""
    if index < 0 or index >= len(drawings):
        await update.callback_query.answer("Invalid drawing index")
        return

    drawing = drawings[index]
    image_url, caption, reply_markup = get_drawing_message(drawing, index)

    try:
        # Edit the existing message with new drawing
        await update.callback_query.edit_message_media(
            media=InputMediaPhoto(media=image_url, caption=caption, parse_mode='Markdown')
        )
        await update.callback_query.edit_message_reply_markup(reply_markup=reply_markup)
    except Exception as e:
        print(f"Error showing drawing: {e}")
        await update.callback_query.answer("Error loading image", show_alert=True)

async def main_menu(update, context):
    """Return to main menu"""
    query = update.callback_query

    # Answer the query immediately to avoid timeout
    try:
        await query.answer()
    except Exception as e:
        print(f"Query answer failed in main_menu (likely timeout): {e}")
        return

    user = query.from_user
    bot = context.application.bot

    try:
        # Check membership every time and print to terminal
        member = await bot.get_chat_member("@Jaredrawing", user.id)
        print(f"User {user.id} membership status: {member.status}")

        if member.status in ["member", "administrator", "creator"]:
            # Send new message instead of editing to avoid media issues
            keyboard = [
                [InlineKeyboardButton("View Price List", callback_data="nav_0")],
                [InlineKeyboardButton("Order Now", url="https://t.me/Ja_r_ed")]
            ]

            message_text = (
                "✅ Welcome to Jared Drawing Studio!\n\n"
                "Choose an option below to get started:"
            )

            await query.message.reply_text(
                message_text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            # User is not a member, show join message
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

            await query.message.reply_text(
                message_text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    except Exception as e:
        print(f"Error in main_menu: {e}")
        try:
            await query.answer("Error returning to main menu", show_alert=True)
        except Exception as e2:
            print(f"Failed to show main menu error: {e2}")
