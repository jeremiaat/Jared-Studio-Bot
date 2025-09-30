from telegram import Bot, Update, InputMediaPhoto,InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ChatMemberHandler,
    CallbackQueryHandler,
)
from telegram.error import TelegramError
import logging
import os
from dotenv import load_dotenv
load_dotenv()

# Your Telegram Bot Token
 
TOKEN = os.environ.get('Bot_TOKEN')

CHANNEL_USERNAME = '@Jaredrawing'
CHANNEL_URL = 'https://t.me/Jaredrawing'

# --- Drawings list (Ensure images exist in 'images/' folder) ---
drawings = [
    {
        "category": "Realistic Drawing",
        "price": "400-600 ETB",
        "size": "A4",
        "description": "A detailed realistic drawing on A4 paper without frame",
        "image": "images/1.jpg"
    },
    {
        "category": "Realistic Drawing",
        "price": "1000-1400 ETB",
        "size": "A4",
        "description": "A realistic drawing in A4 paper with frame. The price vary based on place and frame type",
        "image": "images/2.jpg"
    },
    {
        "category": "Realistic Drawing",
        "price": "2000-2300 ETB",
        "size": "A3",
        "description": "A realistic drawing in A4 paper with Frame",
        "image": "images/1.jpg"
    }
]

# --- Function to generate image, caption, and buttons ---
def get_drawing_message(drawing_data, index):
    """
    Returns image path, caption text, and inline keyboard for a single drawing.
    """
    caption = (
        f"🎨 *Category:* {drawing_data['category']}\n\n"
        f"📝 *Description:* {drawing_data['description']}\n"
        f"📏 *Size:* {drawing_data['size']}\n"
        f"💰 *Price:* {drawing_data['price']}\n\n"
        f"Page {index + 1} of {len(drawings)}"
    )

    keyboard = []
    nav_buttons = []

    if index > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Back", callback_data=f"nav_{index - 1}"))
    if index < len(drawings) - 1:
        nav_buttons.append(InlineKeyboardButton("➡️ Next", callback_data=f"nav_{index + 1}"))

    if nav_buttons:
        keyboard.append(nav_buttons)

    # Note: Using the bot's deep-linking start parameter is generally correct for ordering.
    keyboard.append([InlineKeyboardButton("Order Now", url="https://t.me/Ja_r_ed")])

    # The image path is returned as is, assuming it will be opened later
    return drawing_data["image"], caption, InlineKeyboardMarkup(keyboard)

# --- Ask user to join channel ---
async def ask_to_join(update: Update):
    keyboard = [
        [InlineKeyboardButton("Join Channel", url=CHANNEL_URL)],
        [InlineKeyboardButton("View Price List", callback_data='nav_0')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Use update.effective_chat.send_message for consistency
    await update.effective_chat.send_message(
        "Please join our channel to view the full price list.",
        reply_markup=reply_markup
    )

# --- Show member options ---
async def show_member_options(update: Update):
    keyboard = [
        [InlineKeyboardButton("View Price List", callback_data='nav_0')],
        [InlineKeyboardButton("Order Now", url="https://t.me/Jaredstudio_bot?start=order")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Use update.effective_chat.send_message for consistency
    await update.effective_chat.send_message("Welcome! What would you like to do?", reply_markup=reply_markup)

# --- /start handler ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not user:
        # Handle case where effective_user is not available (e.g., non-message update)
        return

    # Only check membership if CHANNEL_USERNAME is a valid channel handle
    try:
        # Check membership is an API call, so it's a potential point of failure.
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user.id)
        if member.status in ['member', 'administrator', 'creator']:
            await show_member_options(update)
        else:
            await ask_to_join(update)
    except Exception as e:
        # This block runs if the bot can't access the channel, or another error occurs.
        print(f"Membership check failed: {e}. Defaulting to show options.")
        await show_member_options(update)

# --- Handle navigation buttons ---
async def navigate_drawings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Extract index from callback_data (e.g., 'nav_0' -> '0')
    try:
        _, index_str = query.data.split('_')
        index = int(index_str)
    except ValueError:
        # Handle malformed callback data
        print(f"Malformed callback data: {query.data}")
        return

    # Check for valid index range
    if not (0 <= index < len(drawings)):
        return

    current_drawing = drawings[index]

    # Get image, caption, and keyboard
    image_path, caption, reply_markup = get_drawing_message(current_drawing, index)

    # Ensure the image file exists before attempting to open it
    if not os.path.exists(image_path):
        await query.edit_message_text("Error: Image file not found.", reply_markup=None)
        return

    # Edit message to show the new image and caption
    # Since query.edit_message_media requires a file input for media updates, 
    # we open the file here for the new InputMediaPhoto object.
    try:
        with open(image_path, "rb") as img:
            await query.edit_message_media(
                media=InputMediaPhoto(media=img, caption=caption, parse_mode="Markdown"),
                reply_markup=reply_markup
            )
    except Exception as e:
        print(f"Error editing message media: {e}")
        await query.edit_message_text("An error occurred while updating the price list.", reply_markup=None)


# --- Main bot setup ---
def main():
    if TOKEN is None:
        print("ERROR: Please replace 'YOUR_BOT_TOKEN' with your actual bot token.")
        return

    # Build the Application object, which handles the ExtBot initialization correctly
    application = Application.builder().token(TOKEN).build()
    
    # Handlers MUST be added BEFORE calling run_polling()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(navigate_drawings, pattern='^nav_'))

    print("Bot is running and started polling...")
    # Run the bot (this is the single entry point for the polling loop)
    # timeout=30 is a good default for polling
    application.run_polling(timeout=30)

if __name__ == "__main__":
    main()