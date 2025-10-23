import os
import asyncio
from fastapi import FastAPI, Request
from starlette.responses import Response
from telegram import Update, InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.error import TelegramError

# --- FastAPI app ---
app = FastAPI()

# --- Config ---
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN not set in environment variables!")

CHANNEL_USERNAME = "@Jaredrawing"
CHANNEL_URL = "https://t.me/Jaredrawing"

VERCEL_DOMAIN = "jared-studio-bot.vercel.app"

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
        "image": f"https://{VERCEL_DOMAIN}/images/1.jpg"
    }
]

# --- Helper ---
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
async def ask_to_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Join Channel", url=CHANNEL_URL)],
        [InlineKeyboardButton("View Price List", callback_data="nav_0")]
    ]
    await update.effective_chat.send_message(
        "Please join our channel to view the full price list.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_member_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            await show_member_options(update, context)
        else:
            await ask_to_join(update, context)
    except TelegramError:
        await show_member_options(update, context)
    except Exception as e:
        print(f"[start handler error]: {e}", flush=True)
        await show_member_options(update, context)

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

# --- Telegram Application ---
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(navigate_drawings, pattern="^nav_"))

# --- Async update processor for webhook ---
async def process_update_async(update_json):
    try:
        update = Update.de_json(update_json, application.bot)
        await application.process_update(update)
    except Exception as e:
        print(f"[async process error]: {e}", flush=True)

# --- FastAPI webhook ---
@app.post("/")
async def webhook(request: Request):
    try:
        update_json = await request.json()
        asyncio.create_task(process_update_async(update_json))
        return Response("OK", status_code=200)
    except Exception as e:
        print(f"[webhook error]: {e}", flush=True)
        return Response("OK, but error processing update", status_code=200)
