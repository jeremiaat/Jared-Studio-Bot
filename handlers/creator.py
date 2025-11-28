from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
import json
import os

ORDERS_FILE = 'orders.json'
PRICES_FILE = 'prices.json'

def load_orders():
    """Load orders from JSON file"""
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_orders(orders):
    """Save orders to JSON file"""
    with open(ORDERS_FILE, 'w') as f:
        json.dump(orders, f, indent=2)

def load_prices():
    """Load prices from JSON file"""
    if os.path.exists(PRICES_FILE):
        with open(PRICES_FILE, 'r') as f:
            return json.load(f)
    return []

def save_prices(prices):
    """Save prices to JSON file"""
    with open(PRICES_FILE, 'w') as f:
        json.dump(prices, f, indent=2)

async def view_orders(update, context):
    """View all available orders"""
    query = update.callback_query
    await query.answer()

    orders = load_orders()

    if not orders:
        message = "📋 No orders available."
    else:
        message = "📋 Available Orders:\n\n"
        for i, order in enumerate(orders, 1):
            message += f"{i}. Customer: @{order.get('customer_username', 'Unknown')}\n"
            message += f"   Size: {order.get('size', 'N/A')}\n"
            message += f"   Frame: {order.get('frame', 'N/A')}\n"
            message += f"   Delivery: {order.get('delivery_time', 'N/A')}\n"
            message += f"   Location: {order.get('location', 'N/A')}\n\n"

    keyboard = [
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
    ]

    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def update_price(update, context):
    """Update price for a drawing"""
    query = update.callback_query
    await query.answer()

    prices = load_prices()

    if not prices:
        message = "No prices available to update."
    else:
        message = "Select a drawing to update price:\n\n"
        keyboard = []
        for i, price in enumerate(prices):
            keyboard.append([
                InlineKeyboardButton(
                    f"{price['category']} - {price['size']}: {price['price']}",
                    callback_data=f"update_price_{i}"
                )
            ])
        keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")])

        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]]
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def add_catalogue(update, context):
    """Add new catalogue item"""
    query = update.callback_query
    await query.answer()

    message = "To add a new catalogue item, please provide the details in this format:\n\n"
    message += "Category: [category]\n"
    message += "Size: [size]\n"
    message += "Price: [price]\n"
    message += "Description: [description]\n"
    message += "Image URL: [url]\n\n"
    message += "Send this information as a message."

    keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]]
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Create handlers
view_orders_handler = CallbackQueryHandler(view_orders, pattern="^view_orders$")
update_price_handler = CallbackQueryHandler(update_price, pattern="^update_price$")
add_catalogue_handler = CallbackQueryHandler(add_catalogue, pattern="^add_catalogue$")
