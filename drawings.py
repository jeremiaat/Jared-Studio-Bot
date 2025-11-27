# drawings.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Using free image hosting services as examples
drawings = [
    {"category": "Realistic Drawing", "price": "400-600 ETB", "size": "A4",
     "description": "A detailed realistic drawing on A4 paper without frame",
     "image": "https://i.postimg.cc/Zn0wns60/1.jpg"},
    {"category": "Realistic Drawing", "price": "1000-1400 ETB", "size": "A4",
     "description": "A realistic drawing in A4 paper with frame",
     "image": "https://i.postimg.cc/x8WJG3T7/2.jpg"},
    {"category": "Realistic Drawing", "price": "2000-2300 ETB", "size": "A3",
     "description": "A realistic drawing in A3 paper with frame",
     "image": "https://i.postimg.cc/Zn0wns60/1.jpg"},  # Note: Update this URL with a different image
]

def get_drawing_message(drawing, index):
    caption = (
        f"🎨 *Category:* {drawing['category']}\n"
        f"📝 *Description:* {drawing['description']}\n"
        f"📏 *Size:* {drawing['size']}\n"
        f"💰 *Price:* {drawing['price']}\n\n"
        f"Page {index + 1} of {len(drawings)}"
    )

    keyboard = []
    nav_buttons = []
    if index > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Back", callback_data=f"nav_{index-1}"))
    if index < len(drawings) - 1:
        nav_buttons.append(InlineKeyboardButton("➡️ Next", callback_data=f"nav_{index+1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)
    keyboard.append([InlineKeyboardButton("Order Now", url="https://t.me/Ja_r_ed")])
    keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")])
    return drawing["image"], caption, InlineKeyboardMarkup(keyboard)