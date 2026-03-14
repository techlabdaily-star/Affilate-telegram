from __future__ import annotations

import asyncio

from telethon import TelegramClient, errors
from telethon.sessions import StringSession

from config import load_config


async def main() -> None:
    cfg = load_config()

    async with TelegramClient(StringSession(), cfg.api_id, cfg.api_hash) as client:
        if not await client.is_user_authorized():
            await client.send_code_request(cfg.phone_number)
            try:
                code = input("Enter the verification code: ").strip()
                await client.sign_in(cfg.phone_number, code)
            except errors.rpcerrorlist.SessionPasswordNeededError:
                password = input("Two-step verification enabled. Enter your password: ").strip()
                await client.sign_in(password=password)

        print("Copy and store this string as TELEGRAM_STRING_SESSION:")
        print(client.session.save())


if __name__ == "__main__":
    asyncio.run(main())
