"""Register / inspect / remove the Telegram webhook for the deployed bot.

Usage:
    python scripts/set_webhook.py https://your-app.vercel.app/api/webhook
    python scripts/set_webhook.py --info
    python scripts/set_webhook.py --delete

BOT_TOKEN is read from the environment or from the project's .env file.
WEBHOOK_SECRET (optional) is sent to Telegram as the shared secret and must
also be set as an environment variable on the hosting platform.
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(PROJECT_ROOT / ".env")

ALLOWED_UPDATES = ["message", "callback_query", "my_chat_member", "chat_member"]


def call(token: str, method: str, **params) -> dict:
    url = f"https://api.telegram.org/bot{token}/{method}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage the Telegram webhook")
    parser.add_argument("url", nargs="?", help="Public HTTPS URL Telegram will POST to")
    parser.add_argument("--secret", default=os.getenv("WEBHOOK_SECRET"),
                        help="Shared secret (max 256 chars, A-Z a-z 0-9 _ -)")
    parser.add_argument("--delete", action="store_true", help="Remove the webhook")
    parser.add_argument("--info", action="store_true", help="Show the current webhook status")
    parser.add_argument("--drop-pending", action="store_true",
                        help="Also discard updates queued before the webhook was set")
    args = parser.parse_args()

    token = os.getenv("BOT_TOKEN")
    if not token:
        sys.exit("BOT_TOKEN not found (set it in .env or in the environment)")

    if args.info:
        print(json.dumps(call(token, "getWebhookInfo"), indent=2))
        return

    if args.delete:
        print(json.dumps(call(token, "deleteWebhook", drop_pending_updates="true"), indent=2))
        print("Webhook removed - the bot now receives no updates until a new one is set.")
        return

    if not args.url:
        sys.exit("Provide the webhook URL, e.g. https://your-app.vercel.app/api/webhook")
    if not args.url.startswith("https://"):
        sys.exit("The webhook URL must start with https://")
    if "." not in args.url.split("//")[-1].split("/")[0]:
        sys.exit("The webhook URL must point at a public domain")

    params = {
        "url": args.url,
        "allowed_updates": json.dumps(ALLOWED_UPDATES),
    }
    if args.secret:
        params["secret_token"] = args.secret
    if args.drop_pending:
        params["drop_pending_updates"] = "true"

    print(json.dumps(call(token, "setWebhook", **params), indent=2))
    print(json.dumps(call(token, "getWebhookInfo"), indent=2))


if __name__ == "__main__":
    main()
