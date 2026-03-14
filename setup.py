#!/usr/bin/env python3
from __future__ import annotations

from config import save_credentials_file


def main() -> None:
    print("Telegram Forwarder Setup")
    print("=" * 30)

    api_id_raw = input("API ID: ").strip()
    api_hash = input("API Hash: ").strip()
    phone_number = input("Phone number (with country code): ").strip()

    if not api_id_raw.isdigit():
        print("API ID must be numeric")
        return
    if not api_hash or not phone_number:
        print("API Hash and phone number are required")
        return

    save_credentials_file(int(api_id_raw), api_hash, phone_number)
    print("\nSaved credentials to credentials.txt")
    print("Run: python main.py --list-chats")
    print("Run: python main.py")


if __name__ == "__main__":
    main()
