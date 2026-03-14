"""Utility script to generate a Telethon string session.

Run this locally in the same environment where your project dependencies are installed.
It will prompt you to log in via phone and then print the session string, which
you can copy into your Railway environment variables.

Usage:
    python gen_session.py
    python gen_session.py --list-chats  # List all chats and save to file
"""

import os
import asyncio
import argparse

from telethon import TelegramClient, errors
from telethon.sessions import StringSession


def read_credentials():
    """Read credentials from credentials.txt file."""
    try:
        with open("credentials.txt", "r") as file:
            lines = file.readlines()
            if len(lines) >= 3:
                api_id = lines[0].strip()
                api_hash = lines[1].strip()
                phone_number = lines[2].strip()
                return api_id, api_hash, phone_number
    except FileNotFoundError:
        pass
    return None, None, None


def write_credentials(api_id, api_hash, phone_number):
    """Write credentials to credentials.txt file."""
    with open("credentials.txt", "w") as file:
        file.write(api_id + "\n")
        file.write(api_hash + "\n")
        file.write(phone_number + "\n")


async def list_chats(client):
    """List all chats and save to file."""
    print("Getting list of all chats...")

    dialogs = await client.get_dialogs()

    # Save to file
    with open("chats_list.txt", "w", encoding="utf-8") as chats_file:
        chats_file.write("Chat ID | Title | Type\n")
        chats_file.write("-" * 50 + "\n")

        for dialog in dialogs:
            chat_type = "Channel" if dialog.is_channel else ("Group" if dialog.is_group else "Private")
            print(f"ID: {dialog.id}, Title: {dialog.title}, Type: {chat_type}")
            chats_file.write(f"{dialog.id} | {dialog.title} | {chat_type}\n")

    print(f"\nList of {len(dialogs)} chats saved to 'chats_list.txt'")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Telegram session or list chats")
    parser.add_argument("--list-chats", action="store_true", help="List all chats instead of generating session")
    args = parser.parse_args()

    # Try to read credentials from file first
    api_id, api_hash, phone_number = read_credentials()

    # If not found in file, prompt user
    if not api_id or not api_hash:
        api_id = input("Enter your API ID: ")
        api_hash = input("Enter your API Hash: ")
        phone_number = input("Enter your phone number (with country code): ")

        # Save credentials for future use
        write_credentials(api_id, api_hash, phone_number)
        print("Credentials saved to 'credentials.txt'")

    try:
        api_id = int(api_id)
    except ValueError:
        print("API ID must be a number")
        return

    async def _run():
        async with TelegramClient(StringSession(), api_id, api_hash) as client:
            print("Connecting to Telegram...")

            # Handle two-step verification
            if not await client.is_user_authorized():
                print("Not authorized. Sending code request...")
                await client.send_code_request(phone_number)

                try:
                    code = input('Enter the verification code: ')
                    await client.sign_in(phone_number, code)
                except errors.rpcerrorlist.SessionPasswordNeededError:
                    password = input('Two-step verification enabled. Enter your password: ')
                    await client.sign_in(password=password)

            print("Successfully logged in!")

            if args.list_chats:
                await list_chats(client)
            else:
                print("Copy the value below and set it as TELEGRAM_STRING_SESSION in your environment:")
                print(client.session.save())

    asyncio.run(_run())


if __name__ == "__main__":
    main()
