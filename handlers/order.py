from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.error import BadRequest
from telegram.ext import ConversationHandler, CallbackQueryHandler, MessageHandler, CommandHandler, filters
from telegram.constants import ParseMode
from config import ORDER_CONTACT_CHAT_ID, ORDER_CONTACT_USERNAME
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

async def confirm_order(update, context):
    """Show order confirmation and send order to contact"""
    query = update.callback_query
    if query:
        try:
            await query.answer()
        except Exception:
            pass

    order = context.user_data.get('order', {})
    bot = context.application.bot
    user = update.effective_user

    description_text = f"\n📝 Description: {order.get('description')}" if order.get('description') else ""

    # Send order details to contact chat if configured
    if ORDER_CONTACT_CHAT_ID:
        try:
            order_message = (
                "🆕 New Order Received\n\n"
                f"Customer: @{user.username or user.full_name} (id: {user.id})\n"
                f"Size: {order.get('size','')}\n"
                f"Frame: {order.get('frame','')}\n"
                f"Delivery Time: {order.get('delivery_time','')}\n"
                f"Location: {order.get('location','')}{description_text}\n"
            )
            await bot.send_message(chat_id=ORDER_CONTACT_CHAT_ID, text=order_message)
            if order.get('photo_file_id'):
                await bot.send_photo(chat_id=ORDER_CONTACT_CHAT_ID, photo=order['photo_file_id'], caption="Order photo")
        except Exception as e:
            print(f"Failed to send order to contact: {e}")

    # Save order locally
    try:
        orders = []
        if os.path.exists(ORDERS_FILE):
            with open(ORDERS_FILE, 'r', encoding='utf-8') as f:
                orders = json.load(f)
        orders.append({
            "user_id": user.id,
            "username": user.username,
            "order": order
        })
        with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(orders, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Failed to save order: {e}")

    # Send confirmation to the user; preserve underscores in contact username using HTML
    safe_contact = html.escape(ORDER_CONTACT_USERNAME or "")
    confirm_text = (
        "✅ Order placed successfully!\n\n"
        f"Size: {order.get('size','')}\n"
        f"Frame: {order.get('frame','')}\n"
        f"Delivery Time: {order.get('delivery_time','')}\n"
        f"Location: {order.get('location','')}\n"
        f"{('Description: ' + order.get('description') + '\\n') if order.get('description') else ''}"
        f"\nContact the artist: <code>{safe_contact}</code>"
    )

    keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]]

    try:
        if query and query.message:
            await query.message.reply_text(confirm_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)
        else:
            await update.effective_message.reply_text(confirm_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)
    except Exception as e:
        print(f"Failed to send confirmation to user: {e}")

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
            CallbackQueryHandler(cancel_order, pattern="^cancel_order$"),
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel_order)],
    allow_reentry=True,
    per_message=False,
)
