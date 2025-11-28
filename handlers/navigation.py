# handlers/navigation.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from drawings import drawings, get_drawing_message
from utils.helpers import is_creator

async def navigate_drawings(update, context):
    """Handle navigation between drawings"""
    query = update.callback_query

    # Answer the query immediately to avoid timeout
    try:
        await query.answer()
    except Exception as e:
        # query too old or already answered — continue without failing
        print(f"Query answer failed in navigate_drawings (likely timeout): {e}")

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
        try:
            await update.callback_query.answer("Invalid drawing index")
        except Exception:
            pass
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
        try:
            await update.callback_query.answer("Error loading image", show_alert=True)
        except Exception:
            pass

async def main_menu(update, context):
    """Return to main menu"""
    query = update.callback_query

    # Try to answer quickly; if it fails, continue silently
    try:
        if query:
            await query.answer()
    except Exception as e:
        print(f"Query answer failed in main_menu (likely timeout): {e}")

    user = query.from_user if query else update.effective_user
    bot = context.application.bot

    # If user is creator, show management UI (no price/order buttons)
    if is_creator(user):
        keyboard = [
            [InlineKeyboardButton("Manage Orders", callback_data="manage_orders")],
            [InlineKeyboardButton("Edit Prices", callback_data="manage_prices")],
            [InlineKeyboardButton("Add Catalogue", callback_data="add_catalogue")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
        ]
        text = "Creator control panel:"
        try:
            if query and query.message:
                await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
            else:
                await update.effective_chat.send_message(text, reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            try:
                if query:
                    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
            except Exception:
                pass
        return

    # non-creator flow: check membership and show user options
    try:
        member = await bot.get_chat_member("@Jaredrawing", user.id)
        is_member = member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"Error checking membership: {e}")
        is_member = False

    if is_member:
        keyboard = [
            [InlineKeyboardButton("Order Now", callback_data="start_order")],
            [InlineKeyboardButton("View Price List", callback_data="price_list")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
        ]
        text = "Welcome back! Choose an option:"
    else:
        keyboard = [
            [InlineKeyboardButton("View Price List", callback_data="price_list")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
        ]
        text = "You are not a member. You can view the price list:"

    try:
        if query and query.message:
            await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await update.effective_chat.send_message(text, reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        print(f"Failed to display main menu: {e}")
