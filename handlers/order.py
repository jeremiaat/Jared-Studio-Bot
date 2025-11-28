from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.error import BadRequest
from telegram.ext import ConversationHandler, CallbackQueryHandler, MessageHandler, CommandHandler, filters
from telegram.constants import ParseMode
# ensure config values are loaded whether your code imports the package or the module
try:
    from config import ORDER_CONTACT_CHAT_ID, ORDER_CONTACT_USERNAME
except Exception:
    try:
        from config.config import ORDER_CONTACT_CHAT_ID, ORDER_CONTACT_USERNAME
    except Exception:
        ORDER_CONTACT_CHAT_ID = None
        ORDER_CONTACT_USERNAME = None
from utils.helpers import is_creator
import html, os, json

def escape_markdown(text):
    """Escape markdown special characters"""
    if not text:
        return text
    return text.replace('*', '\\*').replace('_', '\\_').replace('[', '\\[').replace('`', '\\`')

# Conversation states
SIZE, FRAME, DELIVERY_TIME, LOCATION, PICTURE, DESCRIPTION, CONFIRM = range(7)

ORDERS_FILE = 'orders.json'

def save_order(order_data):
    """Save order to JSON file"""
    orders = []
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'r') as f:
            orders = json.load(f)
    orders.append(order_data)
    with open(ORDERS_FILE, 'w') as f:
        json.dump(orders, f, indent=2)

async def start_order(update, context):
    """Start the ordering process"""
    query = update.callback_query
    await query.answer()

    user = update.effective_user

    # Check if user is creator
    if is_creator(user.id):
        await query.edit_message_text(
            "🎨 As the creator, you cannot place orders.\n\n"
            "Use the management options to view orders and manage your studio.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
            ])
        )
        return ConversationHandler.END

    # Initialize order data
    context.user_data['order'] = {}

    keyboard = [
        [InlineKeyboardButton("A4", callback_data="size_A4")],
        [InlineKeyboardButton("A3", callback_data="size_A3")]
    ]

    try:
        await query.edit_message_text(
            "🎨 *Select Size*\n\nChoose the paper size for your drawing:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
    except BadRequest as e:
        if "Message is not modified" in str(e):
            # Message is already in the correct state, ignore
            pass
        else:
            raise

    return SIZE

async def select_size(update, context):
    """Handle size selection"""
    query = update.callback_query
    await query.answer()

    size = query.data.split('_')[1]
    context.user_data['order']['size'] = size

    keyboard = [
        [InlineKeyboardButton("With Frame", callback_data="frame_yes")],
        [InlineKeyboardButton("Without Frame", callback_data="frame_no")]
    ]

    await query.edit_message_text(
        f"📏 *Size Selected:* {size}\n\n*Frame Option*\n\nDo you want your drawing framed?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

    return FRAME

async def select_frame(update, context):
    """Handle frame selection"""
    query = update.callback_query
    await query.answer()

    frame = "with frame" if query.data.split('_')[1] == "yes" else "without frame"
    context.user_data['order']['frame'] = frame

    keyboard = [
        [InlineKeyboardButton("3 Days", callback_data="time_3_days")],
        [InlineKeyboardButton("5 Days", callback_data="time_5_days")],
        [InlineKeyboardButton("1 Week", callback_data="time_1_week")],
        [InlineKeyboardButton("2 Weeks", callback_data="time_2_weeks")]
    ]

    await query.edit_message_text(
        f"📏 *Size:* {context.user_data['order']['size']}\n"
        f"🖼️ *Frame:* {frame}\n\n"
        "*Delivery Time*\n\nSelect your preferred delivery time:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )

    return DELIVERY_TIME

async def select_delivery_time(update, context):
    """Handle delivery time selection"""
    query = update.callback_query
    await query.answer()

    time_option = query.data.replace('time_', '').replace('_', ' ')
    context.user_data['order']['delivery_time'] = time_option

    await query.edit_message_text(
        f"📏 *Size:* {context.user_data['order']['size']}\n"
        f"🖼️ *Frame:* {context.user_data['order']['frame']}\n"
        f"⏰ *Delivery Time:* {time_option}\n\n"
        "*Delivery Location*\n\nPlease enter your delivery location (city, address, etc.):",
        parse_mode=ParseMode.MARKDOWN
    )

    return LOCATION

async def enter_location(update, context):
    """Handle location input"""
    location = update.message.text
    context.user_data['order']['location'] = location

    await update.message.reply_text(
        f"📏 *Size:* {context.user_data['order']['size']}\n"
        f"🖼️ *Frame:* {context.user_data['order']['frame']}\n"
        f"⏰ *Delivery Time:* {context.user_data['order']['delivery_time']}\n"
        f"📍 *Location:* {escape_markdown(location)}\n\n"
        "*Picture Upload*\n\nPlease send a photo of what you want drawn:",
        parse_mode=ParseMode.MARKDOWN
    )

    return PICTURE

async def receive_picture(update, context):
    """Receive picture and ask for optional description (show Skip only here)."""
    # Get the highest resolution photo
    message = update.effective_message
    if message and message.photo:
        photo = message.photo[-1]
        file_id = photo.file_id
        context.user_data.setdefault('order', {})['photo_file_id'] = file_id

    # Prompt for description and offer Skip (only here)
    keyboard = [
        [InlineKeyboardButton("Skip", callback_data="skip_description")],
        [InlineKeyboardButton("Cancel", callback_data="cancel_order")]
    ]
    await update.effective_chat.send_message(
        "You can send an optional description for the order now (e.g. reference details). "
        "Or press Skip to continue without a description.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return DESCRIPTION

async def enter_description(update, context):
    """Store entered description and show confirmation."""
    # Only handle textual messages in this handler
    if not (update.message and update.message.text):
        # Ask user to send text or use Skip (still in DESCRIPTION state)
        try:
            await update.effective_chat.send_message("Please send a text description or press Skip.")
        except Exception:
            pass
        return DESCRIPTION

    text = update.message.text.strip()
    context.user_data.setdefault('order', {})['description'] = text

    # show confirmation and advance to CONFIRM
    return await show_order_confirmation(update, context)


async def skip_description(update, context):
    """Skip description and proceed to confirmation. Only available in DESCRIPTION step."""
    query = update.callback_query
    if query:
        try:
            await query.answer()
        except Exception:
            pass
    context.user_data.setdefault('order', {})['description'] = ""
    # show confirmation and advance to CONFIRM
    return await show_order_confirmation(update, context)


async def show_order_confirmation(update, context):
    """Render order summary and present confirm/cancel buttons. Returns CONFIRM."""
    order = context.user_data.get('order', {})

    description_text = f"\n📝 Description: {order.get('description','')}" if order.get('description') else ""

    message_text = (
        "📋 *Order Summary*\n\n"
        f"📏 *Size:* {order.get('size','')}\n"
        f"🖼️ *Frame:* {order.get('frame','')}\n"
        f"⏰ *Delivery Time:* {order.get('delivery_time','')}\n"
        f"📍 *Location:* {order.get('location','')}\n"
        f"{description_text}\n\n"
        "Please confirm your order:"
    )

    keyboard = [
        [InlineKeyboardButton("✅ Confirm Order", callback_data="confirm_order")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel_order")]
    ]

    # Prefer replying in the same context (message or callback)
    try:
        query = getattr(update, "callback_query", None)
        if query and query.message:
            await query.message.reply_text(message_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)
        elif update.message:
            await update.message.reply_text(message_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)
        else:
            await context.application.bot.send_message(chat_id=update.effective_chat.id, text=message_text,
                                                      reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        print(f"show_order_confirmation error: {e}")

    return CONFIRM

def _parse_chat_id(v):
    if v is None:
        return None
    try:
        return int(v)
    except Exception:
        try:
            return int(str(v).strip())
        except Exception:
            return None

async def confirm_order(update, context):
    """Show order confirmation to user and send order data to ORDER_CONTACT_CHAT_ID."""
    query = getattr(update, "callback_query", None)
    if query:
        try:
            await query.answer()
        except Exception:
            pass

    order = context.user_data.get('order', {})
    user = update.effective_user
    bot = context.application.bot

    # Prepare human-friendly order text (use HTML to preserve underscores)
    desc = order.get('description') or "—"
    username = f"@{user.username}" if user and user.username else (user.full_name if user else "Unknown")
    order_lines = [
        "🆕 <b>New Order Received</b>",
        f"👤 <b>Customer:</b> {username} (id: {getattr(user,'id', 'unknown')})",
        f"📏 <b>Size:</b> {order.get('size','')}",
        f"🖼️ <b>Frame:</b> {order.get('frame','')}",
        f"⏰ <b>Delivery Time:</b> {order.get('delivery_time','')}",
        f"📍 <b>Location:</b> {order.get('location','')}",
        f"📝 <b>Description:</b> {desc}",
    ]
    order_message = "\n".join(order_lines)

    # Send to configured contact chat id (if available)
    contact_chat_id = _parse_chat_id(ORDER_CONTACT_CHAT_ID)
    if contact_chat_id:
        try:
            await bot.send_message(chat_id=contact_chat_id, text=order_message, parse_mode=ParseMode.HTML)
            # send photo if provided
            photo_id = order.get('photo_file_id')
            if photo_id:
                try:
                    await bot.send_photo(chat_id=contact_chat_id, photo=photo_id, caption=f"Photo for order from {username}")
                except Exception as e:
                    print(f"Failed to send order photo to contact: {e}")
        except Exception as e:
            print(f"Failed to send order to contact ({contact_chat_id}): {e}")
    else:
        print("ORDER_CONTACT_CHAT_ID not configured or invalid; order not forwarded to contact.")

    # Continue with existing confirmation to user (keep original behavior)
    safe_contact = (ORDER_CONTACT_USERNAME or "the artist")
    confirm_text = (
        "✅ <b>Order placed successfully!</b>\n\n"
        f"📏 <b>Size:</b> {order.get('size','')}\n"
        f"🖼️ <b>Frame:</b> {order.get('frame','')}\n"
        f"⏰ <b>Delivery Time:</b> {order.get('delivery_time','')}\n"
        f"📍 <b>Location:</b> {order.get('location','')}\n"
        f"📝 <b>Description:</b> {desc}\n\n"
        f"📞 Contact: <code>{html.escape(safe_contact)}</code>\n\n"
        "Please contact the artist above to discuss payment and final details."
    )

    keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]]

    try:
        if query and query.message:
            await query.message.reply_text(confirm_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)
        elif update.message:
            await update.message.reply_text(confirm_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)
        else:
            await bot.send_message(chat_id=update.effective_chat.id, text=confirm_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)
    except Exception as e:
        print(f"Failed to send confirmation to user: {e}")

    # clear conversation data if desired
    context.user_data.pop('order', None)
    return ConversationHandler.END

async def cancel_order(update, context):
    """Cancel the current order flow and clean up user_data."""
    query = getattr(update, "callback_query", None)
    try:
        if query:
            await query.answer()
            try:
                await query.edit_message_text("❌ Order cancelled.", reply_markup=None)
            except Exception:
                pass
        else:
            # message-based cancellation
            if update.message:
                await update.message.reply_text("❌ Order cancelled.")
    except Exception:
        pass

    context.user_data.pop('order', None)
    return ConversationHandler.END

# Conversation handler (exported as `order_conversation`)
order_conversation = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_order, pattern="^start_order$")],
    states={
        SIZE: [CallbackQueryHandler(select_size, pattern="^size_")],
        FRAME: [CallbackQueryHandler(select_frame, pattern="^frame_")],
        DELIVERY_TIME: [CallbackQueryHandler(select_delivery_time, pattern="^time_")],
        LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_location)],
        PICTURE: [MessageHandler(filters.PHOTO, receive_picture)],
        DESCRIPTION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, enter_description),
            CallbackQueryHandler(skip_description, pattern="^skip_description$")
        ],
        CONFIRM: [
            CallbackQueryHandler(confirm_order, pattern="^confirm_order$"),
            CallbackQueryHandler(cancel_order, pattern="^cancel_order$")
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel_order)],
    allow_reentry=True,
    per_user=True  # use per_user (or per_chat) so MessageHandler + CallbackQueryHandler can coexist
)
