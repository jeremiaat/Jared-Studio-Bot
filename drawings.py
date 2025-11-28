# drawings.py
import os
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

PRICES_FILE = 'prices.json'

def load_prices():
    """Load prices from JSON file, fallback to hardcoded if file doesn't exist"""
    if os.path.exists(PRICES_FILE):
        try:
            with open(PRICES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass

    return [
        {"category": "Realistic Drawing", "price": "400-600 ETB", "size": "A4",
         "description": "A detailed realistic drawing on A4 paper without frame",
         "image": "https://i.postimg.cc/Zn0wns60/1.jpg"},
        {"category": "Realistic Drawing", "price": "1000-1400 ETB", "size": "A4",
         "description": "A realistic drawing in A4 paper with frame",
         "image": "https://i.postimg.cc/x8WJG3T7/2.jpg"},
        {"category": "Realistic Drawing", "price": "2000-2300 ETB", "size": "A3",
         "description": "A realistic drawing in A3 paper with frame",
         "image": "https://i.postimg.cc/Zn0wns60/1.jpg"},
    ]

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