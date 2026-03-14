from __future__ import annotations

import asyncio
import sys

from telethon import TelegramClient, errors
from telethon.sessions import StringSession

from config import load_config


async def main() -> None:
    cfg = load_config()
    print("Starting Telegram session generation...")
    print("Connecting to Telegram servers. This can take a few seconds.")

    async with TelegramClient(StringSession(), cfg.api_id, cfg.api_hash) as client:
        print("Connected.")
        if not await client.is_user_authorized():
            print("Account is not authorized yet. Sending login code...")
            await client.send_code_request(cfg.phone_number)
            try:
                code = input("Enter the verification code: ").strip()
                await client.sign_in(cfg.phone_number, code)
            except errors.rpcerrorlist.SessionPasswordNeededError:
                password = input("Two-step verification enabled. Enter your password: ").strip()
                await client.sign_in(password=password)

        print("Authorization successful.")
        print("Copy and store this string as TELEGRAM_STRING_SESSION:")
        print(client.session.save())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSession generation cancelled by user.")
        sys.exit(130)
