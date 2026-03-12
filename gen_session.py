"""Utility script to generate a Telethon string session.

Run this locally in the same environment where your project dependencies are installed.
It will prompt you to log in via phone and then print the session string, which
you can copy into your Railway environment variables.

Usage:
    python gen_session.py
"""

import os
import asyncio

from telethon import TelegramClient
from telethon.sessions import StringSession


def main() -> None:
    api_id = int(os.getenv("TELEGRAM_API_ID", "0"))
    api_hash = os.getenv("TELEGRAM_API_HASH", "")
    if not api_id or not api_hash:
        print("Please set TELEGRAM_API_ID and TELEGRAM_API_HASH in your environment.")
        return

    async def _run():
        async with TelegramClient(StringSession(), api_id, api_hash) as client:
            print("Logged in successfully.")
            print("Copy the value below and set it as TELEGRAM_STRING_SESSION:")
            print(client.session.save())

    asyncio.run(_run())


if __name__ == "__main__":
    main()
