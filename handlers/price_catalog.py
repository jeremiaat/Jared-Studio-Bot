from pathlib import Path
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputMediaPhoto
from telegram.ext import ContextTypes
from drawings import drawings
from utils.helpers import is_creator

async def list_prices(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Open the price viewer starting at the first item (one item at a time)."""
    query = update.callback_query
    user = query.from_user if query else update.effective_user

    # Check if user is creator - creators cannot view price list
    if is_creator(user):
        target = query.message if query else update.effective_message
        await target.reply_text("Access denied. Creators cannot view the price list.")
        return

    if query:
        try:
            await query.answer()
        except Exception:
            pass
        await _render_price(update, context, 0)
    else:
        # command /prices — show first item in chat
        await _render_price(update, context, 0, from_command=True)

async def show_price_detail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback handler for price_{index} — show the item at that index with nav buttons."""
    query = update.callback_query
    if not query:
        return
    try:
        await query.answer()
    except Exception:
        pass

    user = query.from_user

    # Check if user is creator - creators cannot view price list
    if is_creator(user):
        await query.edit_message_text("Access denied. Creators cannot view the price list.")
        return

    # Check membership for non-creators
    bot = context.application.bot
    try:
        member = await bot.get_chat_member("@Jaredrawing", user.id)
        is_member = member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"Membership check failed: {e}")
        is_member = False

    if not is_member:
        join_url = "https://t.me/Jaredrawing"
        keyboard = [
            [InlineKeyboardButton("Join Channel", url=join_url)],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
        ]
        await query.edit_message_text(
            "ℹ️ You must be a member of @Jaredrawing to view prices.\n\n"
            "Please join the channel first:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    data = query.data or ""
    if not data.startswith("price_"):
        try:
            await query.edit_message_text("Unknown selection.")
        except Exception:
            pass
        return

    try:
        index = int(data.split("_", 1)[1])
    except Exception:
        try:
            await query.edit_message_text("Invalid selection.")
        except Exception:
            pass
        return

    await _render_price(update, context, index)

async def _render_price(update: Update, context: ContextTypes.DEFAULT_TYPE, index: int, from_command: bool = False) -> None:
    """Internal: render a single drawing/price item with Prev/Next, Order and Main Menu buttons."""
    if not drawings:
        target = update.callback_query.message if getattr(update, "callback_query", None) else update.effective_message
        await target.reply_text("No price entries available.")
        return

    if index < 0 or index >= len(drawings):
        # out of range
        try:
            if update.callback_query:
                await update.callback_query.edit_message_text("Selection out of range.")
            else:
                await update.effective_message.reply_text("Selection out of range.")
        except Exception:
            pass
        return

    item = drawings[index]
    caption_lines = [
        f"🎨 *Category:* {item.get('category','')}",
        f"💰 *Price:* {item.get('price','')}",
        f"📏 *Size:* {item.get('size','')}",
        f"📝 *Description:* {item.get('description','')}",
        f"\nPage {index+1} of {len(drawings)}"
    ]
    caption = "\n".join(caption_lines)

    # build nav buttons
    nav_row = []
    if index > 0:
        nav_row.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"price_{index-1}"))
    if index < len(drawings) - 1:
        nav_row.append(InlineKeyboardButton("Next ➡️", callback_data=f"price_{index+1}"))

    keyboard = []
    if nav_row:
        keyboard.append(nav_row)

    # Removed "Order Now" button here — only Main Menu remains for neatness
    keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")])

    image = item.get("image")

    query = getattr(update, "callback_query", None)
    try:
        if query and query.message:
            # try to edit existing message into a photo with the caption and nav buttons
            media = InputMediaPhoto(media=image, caption=caption, parse_mode="Markdown")
            try:
                await query.edit_message_media(media=media, reply_markup=InlineKeyboardMarkup(keyboard))
                return
            except Exception:
                # fallback to sending a new photo message and editing old message text
                try:
                    await query.message.reply_photo(photo=image, caption=caption, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
                    await query.edit_message_text(f"Viewed: {item.get('category','')}")
                    return
                except Exception:
                    pass

        # If we get here, no callback context or editing failed - send a new photo/message
        if from_command and update.effective_message:
            await update.effective_message.reply_photo(photo=image, caption=caption, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        else:
            await update.effective_chat.send_photo(photo=image, caption=caption, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    except Exception as e:
        # last resort: send text-only with nav buttons
        try:
            if query and query.message:
                await query.edit_message_text(caption, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
            else:
                await update.effective_chat.send_message(caption, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        except Exception:
            print(f"price render error: {e}")