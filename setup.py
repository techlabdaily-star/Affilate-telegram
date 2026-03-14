#!/usr/bin/env python3
"""Setup script for Telegram Affiliate Deal Bot.

This script helps you:
1. Set up credentials
2. Generate session string
3. List available chats
4. Configure the bot

Usage:
    python setup.py
"""

import asyncio
import os
import sys
from pathlib import Path


def read_credentials():
    """Read credentials from credentials.txt file."""
    credentials_file = Path("credentials.txt")
    if credentials_file.exists():
        try:
            lines = credentials_file.read_text().strip().split('\n')
            if len(lines) >= 3:
                return lines[0].strip(), lines[1].strip(), lines[2].strip()
        except Exception:
            pass
    return None, None, None


def write_credentials(api_id, api_hash, phone_number):
    """Write credentials to credentials.txt file."""
    with open("credentials.txt", "w") as file:
        file.write(api_id + "\n")
        file.write(api_hash + "\n")
        file.write(phone_number + "\n")
    print("✅ Credentials saved to 'credentials.txt'")


def main():
    print("🤖 Telegram Affiliate Deal Bot Setup")
    print("=" * 40)

    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Virtual environment not detected. Consider activating it first:")
        print("   source .venv/bin/activate")
        print()

    # Try to read existing credentials
    api_id, api_hash, phone_number = read_credentials()

    if not api_id or not api_hash or not phone_number:
        print("📝 Enter your Telegram API credentials:")
        api_id = input("API ID: ").strip()
        api_hash = input("API Hash: ").strip()
        phone_number = input("Phone number (with country code, e.g. +1234567890): ").strip()

        if not api_id or not api_hash or not phone_number:
            print("❌ All credentials are required!")
            return

        write_credentials(api_id, api_hash, phone_number)
    else:
        print("✅ Found existing credentials in 'credentials.txt'")

    # Set environment variables for the session generation
    os.environ["TELEGRAM_API_ID"] = api_id
    os.environ["TELEGRAM_API_HASH"] = api_hash

    print("\n🔐 Generating session string...")
    print("You'll need to enter your phone number and verification code.")

    # Import and run the session generator
    try:
        from gen_session import main as gen_session_main
        gen_session_main()
    except KeyboardInterrupt:
        print("\n⚠️  Session generation cancelled.")
        return
    except Exception as e:
        print(f"❌ Error generating session: {e}")
        return

    print("\n📋 Next steps:")
    print("1. Copy the session string above")
    print("2. Set it as TELEGRAM_STRING_SESSION in your .env file")
    print("3. Configure SOURCE_CHANNELS and TARGET_CHANNEL in .env")
    print("4. Run: python main.py --list-chats  # to see available chats")
    print("5. Run: python main.py  # to start the bot")

    print("\n💡 Pro tip: Use 'python main.py --list-chats' anytime to list your chats!")


if __name__ == "__main__":
    main()