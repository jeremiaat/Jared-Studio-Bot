import os
from dotenv import load_dotenv

load_dotenv()

def _int_or_none(v):
    if v is None:
        return None
    try:
        return int(v)
    except Exception:
        return None

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")
CHANNEL_URL = os.getenv("CHANNEL_URL")
ORDER_CONTACT_USERNAME = os.getenv("ORDER_CONTACT_USERNAME")
ORDER_CONTACT_CHAT_ID = _int_or_none(os.getenv("ORDER_CONTACT_CHAT_ID"))
CREATOR_USER_ID = _int_or_none(os.getenv("CREATOR_USER_ID"))
CREATOR_USER_IDS = os.getenv("CREATOR_USER_IDS")  # optional comma-separated
CREATOR_USERNAMES = os.getenv("CREATOR_USERNAMES")  # optional comma-separated

__all__ = [
    "BOT_TOKEN",
    "CHANNEL_USERNAME",
    "CHANNEL_URL",
    "ORDER_CONTACT_USERNAME",
    "ORDER_CONTACT_CHAT_ID",
    "CREATOR_USER_ID",
    "CREATOR_USER_IDS",
    "CREATOR_USERNAMES",
]
