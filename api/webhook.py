import os
import asyncio
from flask import Flask, request, Response
from http import HTTPStatus
from telegram import Update, InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.error import TelegramError

# --- Flask app ---
app = Flask(__name__)

# --- Config ---
TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_USERNAME = "@Jaredrawing"
CHANNEL_URL = "https://t.me/Jaredrawing"
VERCEL_DOMAIN = os.environ.get("VERCEL_URL", "your-vercel-domain.vercel.app")

# --- Drawings list (public URLs) ---
drawings = [
    {
        "category": "Realistic Drawing",
        "price": "400-600 ETB",
        "size": "A4",
        "description": "A detailed realistic drawing on A4 paper without frame",
        "image": f"https://{VERCEL_DOMAIN}/images/1.jpg"
    },
    {
        "category": "Realistic Drawing",
        "price": "1000-1400 ETB",
        "size": "A4",
        "description": "A realistic drawing in A4 paper with frame",
        "image": f"https://{VERCEL_DOMAIN}/images/2.jpg"
    },
    {
        "category": "Realistic Drawing",
        "price": "2000-2300 ETB",
        "size": "A3",
        "description": "A realistic drawing in A3 paper with frame",
        "image": f"https://{VERCEL_DOMAIN}/images/3.jpg"
    }
]

# --- Helper to generate message ---
def get_drawing_message(drawing, index):
    caption = (
        f"🎨 *Category:* {drawing['category']}\n\n"
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
    return drawing["image"], caption, InlineKeyboardMarkup(keyboard)

# --- Command Handlers ---
async def ask_to_join(update: Update):
    keyboard = [
        [InlineKeyboardButton("Join Channel", url=CHANNEL_URL)],
        [InlineKeyboardButton("View Price List", callback_data="nav_0")]
    ]
    await update.effective_chat.send_message(
        "Please join our channel to view the full price list.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_member_options(update: Update):
    keyboard = [
        [InlineKeyboardButton("View Price List", callback_data="nav_0")],
        [InlineKeyboardButton("Order Now", url="https://t.me/Ja_r_ed")]
    ]
    await update.effective_chat.send_message(
        "Welcome! What would you like to do?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.application.bot
    user = update.effective_user
    if not user:
        return
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user.id)
        if member.status in ["member", "administrator", "creator"]:
            await show_member_options(update)
        else:
            await ask_to_join(update)
    except TelegramError:
        await show_member_options(update)
    except Exception as e:
        print(f"Error in start: {e}")
        await show_member_options(update)

async def navigate_drawings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        _, index_str = query.data.split("_")
        index = int(index_str)
    except ValueError:
        return

    if not (0 <= index < len(drawings)):
        return

    image_url, caption, reply_markup = get_drawing_message(drawings[index], index)
    media = InputMediaPhoto(media=image_url, caption=caption, parse_mode="Markdown")
    try:
        await query.edit_message_media(media=media, reply_markup=reply_markup)
    except Exception:
        await query.edit_message_text(caption, reply_markup=reply_markup, parse_mode="Markdown")

# --- Flask Webhook ---
@app.route("/", methods=["POST"])
def webhook():
    if TOKEN is None:
        return Response("Bot token not set", status=HTTPStatus.INTERNAL_SERVER_ERROR)

    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(navigate_drawings, pattern="^nav_"))

    try:
        update_json = request.get_json(force=True)
        update = Update.de_json(update_json, application.bot)
        asyncio.run(application.process_update(update))
    except Exception as e:
        print(f"Error processing update: {e}")
        return Response("OK, but error processing update", status=HTTPStatus.OK)

    return Response("OK", status=HTTPStatus.OK)
