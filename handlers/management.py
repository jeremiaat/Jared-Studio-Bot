from pathlib import Path
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CallbackQueryHandler, ConversationHandler
from utils.helpers import is_creator

ORDERS_FILE = Path("orders.json")

STATE_LIST, STATE_DETAIL = range(2)


def _load_orders():
    if not ORDERS_FILE.exists():
        return []
    try:
        with ORDERS_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save_orders(data):
    try:
        with ORDERS_FILE.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


async def start_view_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Entry: show list of saved orders to the creator."""
    query = update.callback_query
    if query:
        try:
            await query.answer()
        except Exception:
            pass
        target = query.message
        user = query.from_user
    else:
        target = update.effective_message
        user = update.effective_user

    # Check if user is creator
    if not is_creator(user):
        if query:
            await query.edit_message_text("Access denied. This feature is for creators only.")
        else:
            await target.reply_text("Access denied. This feature is for creators only.")
        return ConversationHandler.END

    orders = _load_orders()
    if not orders:
        # Update the message to show that no orders were found, with a back button.
        keyboard = [[InlineKeyboardButton("⬅️ Back to Menu", callback_data="main_menu")]]
        await target.edit_text("No orders found.", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    buttons = []
    for i, o in enumerate(orders):
        label = f"Order #{i+1} - @{o.get('username') or o.get('user_id')}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"view_order_{i}")])
    
    buttons.append([InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")])
    await target.edit_text("Select an order to view:", reply_markup=InlineKeyboardMarkup(buttons))
    return STATE_LIST


async def show_order_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show detailed order and actions (delete/back)."""
    query = update.callback_query
    if not query:
        return ConversationHandler.END
    try:
        await query.answer()
    except Exception:
        pass

    data = query.data or ""
    try:
        idx = int(data.split("_", 2)[2])
    except Exception:
        await query.edit_message_text("Invalid selection.")
        return STATE_LIST

    orders = _load_orders()
    if idx < 0 or idx >= len(orders):
        await query.edit_message_text("Order not found.")
        return STATE_LIST

    o = orders[idx]
    lines = [
        f"👤 Customer: @{o.get('username') or o.get('user_id')}",
        f"📏 Size: {o.get('order',{}).get('size','')}",
        f"🖼️ Frame: {o.get('order',{}).get('frame','')}",
        f"⏰ Delivery: {o.get('order',{}).get('delivery_time','')}",
        f"📍 Location: {o.get('order',{}).get('location','')}",
        f"📝 Description: {o.get('order',{}).get('description','') or '—'}"
    ]
    text = "\n".join(lines)

    kb = [
        [InlineKeyboardButton("🗑️ Delete Order", callback_data=f"delete_order_{idx}")],
        [InlineKeyboardButton("⬅️ Back to list", callback_data="back_to_orders")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
    ]
    # Update the message to show the order details
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb))
    return STATE_DETAIL


async def delete_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete an order and return to list."""
    query = update.callback_query
    if query:
        try:
            await query.answer()
        except Exception:
            pass
    data = query.data or ""
    try:
        idx = int(data.split("_", 2)[2])
    except Exception:
        await query.edit_message_text("Invalid delete request.")
        return STATE_LIST

    orders = _load_orders()
    if 0 <= idx < len(orders):
        removed = orders.pop(idx)
        _save_orders(orders)
        await query.answer(f"Deleted order from @{removed.get('username') or removed.get('user_id')}.")
    else:
        await query.answer("Order index out of range.")

    # show updated list
    return await start_view_orders(update, context)


async def back_to_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.callback_query.answer()
    except Exception:
        pass
    return await start_view_orders(update, context)


# Simple stubs for price management flows (expand later)
async def manage_prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user if query else update.effective_user

    # Check if user is creator
    if not is_creator(user):
        target = query.message if query else update.effective_message
        await target.reply_text("Access denied. This feature is for creators only.")
        return

    if query:
        try:
            await query.answer()
            # Update the message instead of sending a new one
            await query.edit_message_text("Price management not implemented yet.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back to Menu", callback_data="main_menu")]]))
        except Exception:
            pass


async def add_catalogue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user if query else update.effective_user

    # Check if user is creator
    if not is_creator(user):
        target = query.message if query else update.effective_message
        await target.reply_text("Access denied. This feature is for creators only.")
        return

    if query:
        try:
            await query.answer()
            # Update the message instead of sending a new one
            await query.edit_message_text("Add catalogue flow not implemented yet.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back to Menu", callback_data="main_menu")]]))
        except Exception:
            pass


# Export handlers for bot.py to register
view_orders_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_view_orders, pattern="^manage_orders$")],
    states={
        STATE_LIST: [
            CallbackQueryHandler(show_order_detail, pattern="^view_order_"),
            CallbackQueryHandler(back_to_orders, pattern="^back_to_orders$"),
        ],
        STATE_DETAIL: [
            CallbackQueryHandler(delete_order, pattern="^delete_order_"),
            CallbackQueryHandler(back_to_orders, pattern="^back_to_orders$"),
        ],
    },
    fallbacks=[CallbackQueryHandler(back_to_orders, pattern="^main_menu$")],
    per_message=True,  # Changed to True to fix PTB warning
    per_user=True,  # use per_user (or per_chat) because we mix CallbackQueryHandler and message handlers
)

update_price_handler = CallbackQueryHandler(manage_prices, pattern="^manage_prices$")
add_catalogue_handler = CallbackQueryHandler(add_catalogue, pattern="^add_catalogue$")
