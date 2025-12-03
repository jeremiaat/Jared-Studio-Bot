import os
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

PRICES_FILE = 'prices.json'

def load_prices():
    """Load prices from JSON file, fallback to hardcoded if file doesn't exist"""
    if os.path.exists(PRICES_FILE):
        try:
            with open(PRICES_FILE, 'r', encoding='utf-8') as f:
                prices = json.load(f)
                # Ensure we return a list even if the file is empty or malformed
                return prices if isinstance(prices, list) else []
        except (json.JSONDecodeError, IOError):
            # If file is corrupt or unreadable, return empty list
            return []
    # If the file doesn't exist, create it with an empty list
    with open(PRICES_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)
    return []

# Load drawings from storage
drawings = load_prices()

def get_drawing_message(drawing, index):
    """Return (image_url, caption, reply_markup) for a drawing with nav buttons."""
    caption = (
        f"🎨 Category: {drawing.get('category','')}\n"
        f"📝 Description: {drawing.get('description','')}\n"
        f"📏 Size: {drawing.get('size','')}\n"
        f"💰 Price: {drawing.get('price','')}\n\n"
        f"Page {index + 1} of {len(drawings)}"
    )

    nav_buttons = []
    if index > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"nav_{index-1}"))
    if index < len(drawings) - 1:
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"nav_{index+1}"))

    keyboard = []
    if nav_buttons:
        keyboard.append(nav_buttons)
    keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu"),
                     InlineKeyboardButton("View Price List", callback_data="price_list")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    image_url = drawing.get('image')
    return image_url, caption, reply_markup