from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
import sys

from telethon import TelegramClient, errors, events
from telethon.sessions import StringSession

from categories import detect_category
from config import AppConfig, load_config, save_credentials_file
from dedupe_store import DedupeStore
from filters import message_matches, parse_keywords
from formatter import build_forward_text
from link_extractor import has_urls

# Optional hardcoded fallbacks (ID format, e.g. -1001234567890).
# Prefer environment variables SOURCE_CHAT_IDS / DESTINATION_CHAT_ID.
DEFAULT_SOURCE_CHAT_IDS: list[int] = []
DEFAULT_DESTINATION_CHAT_ID: int | None = None


async def ensure_authorized(client: TelegramClient, phone_number: str) -> None:
    await client.connect()
    if await client.is_user_authorized():
        return

    if not sys.stdin.isatty():
        raise RuntimeError(
            "Telegram session is not authorized in non-interactive mode. "
            "Set a valid TELEGRAM_STRING_SESSION for production deployments."
        )

    await client.send_code_request(phone_number)
    try:
        code = input("Enter the Telegram verification code: ").strip()
        await client.sign_in(phone_number, code)
    except errors.rpcerrorlist.SessionPasswordNeededError:
        password = input("Two-step verification enabled. Enter password: ").strip()
        await client.sign_in(password=password)


def create_client(cfg: AppConfig) -> TelegramClient:
    if cfg.string_session:
        try:
            session = StringSession(cfg.string_session)
        except Exception as exc:
            raise RuntimeError(
                "Provided TELEGRAM_STRING_SESSION is invalid. Generate a fresh one using gen_session.py"
            ) from exc
        return TelegramClient(session, cfg.api_id, cfg.api_hash)

    return TelegramClient(cfg.session_name, cfg.api_id, cfg.api_hash)


async def list_chats(client: TelegramClient, output_file: str) -> None:
    dialogs = await client.get_dialogs()
    out_path = Path(output_file)

    with out_path.open("w", encoding="utf-8") as fh:
        fh.write("Chat ID | Title | Type\n")
        fh.write("-" * 72 + "\n")
        for dialog in dialogs:
            chat_type = "Channel" if dialog.is_channel else ("Group" if dialog.is_group else "Private")
            line = f"{dialog.id} | {dialog.title} | {chat_type}"
            print(line)
            fh.write(line + "\n")

    print(f"\nSaved {len(dialogs)} chats to {out_path}")


async def run_forwarder(cfg: AppConfig, args: argparse.Namespace) -> None:
    client = create_client(cfg)
    await ensure_authorized(client, cfg.phone_number)

    source_chat_ids = [args.source_chat_id] if args.source_chat_id is not None else list(cfg.source_chat_ids)
    if not source_chat_ids and DEFAULT_SOURCE_CHAT_IDS:
        source_chat_ids = list(DEFAULT_SOURCE_CHAT_IDS)

    destination_chat_id = (
        args.destination_chat_id
        if args.destination_chat_id is not None
        else (
            cfg.destination_chat_id
            if cfg.destination_chat_id is not None
            else DEFAULT_DESTINATION_CHAT_ID
        )
    )

    if not source_chat_ids:
        if not sys.stdin.isatty():
            raise RuntimeError(
                "SOURCE_CHAT_IDS is required in non-interactive mode. "
                "Set SOURCE_CHAT_IDS in environment variables or pass --source-chat-id."
            )
        source_chat_ids = [int(input("Enter source chat ID: ").strip())]
    if destination_chat_id is None:
        if not sys.stdin.isatty():
            raise RuntimeError(
                "DESTINATION_CHAT_ID is required in non-interactive mode. "
                "Set DESTINATION_CHAT_ID in environment variables or pass --destination-chat-id."
            )
        destination_chat_id = int(input("Enter destination chat ID: ").strip())

    raw_keywords = args.keywords if args.keywords is not None else cfg.default_keywords
    if raw_keywords is None:
        if sys.stdin.isatty():
            raw_keywords = input("Keywords (comma-separated, blank = forward all): ").strip()
        else:
            raw_keywords = ""
    keywords = parse_keywords(raw_keywords)

    dedupe = DedupeStore(cfg.db_path)
    await dedupe.init()

    print("Forwarder started")
    print(f"Sources: {source_chat_ids}")
    print(f"Destination: {destination_chat_id}")
    print(f"Keywords: {keywords if keywords else '[ALL MESSAGES]'}")

    @client.on(events.NewMessage(chats=source_chat_ids))
    async def handle_new_message(event: events.NewMessage.Event) -> None:
        message = event.message
        text = message.message or ""
        event_source_chat_id = int(event.chat_id) if event.chat_id is not None else 0

        if not text and not (cfg.forward_media and message.media):
            return

        if await dedupe.has_processed(event_source_chat_id, message.id):
            return

        if cfg.forward_only_with_links and text and not has_urls(text):
            return

        if text and not message_matches(text, keywords):
            return

        category = detect_category(text) if cfg.include_category_hint else None
        outbound_text = build_forward_text(text, category=category)

        if cfg.forward_media and message.media:
            await client.forward_messages(destination_chat_id, message)
            if outbound_text.strip():
                await client.send_message(destination_chat_id, outbound_text)
        else:
            await client.send_message(destination_chat_id, outbound_text)

        await dedupe.mark_processed(event_source_chat_id, message.id)
        print(f"Forwarded message {message.id}")

        if args.once:
            await client.disconnect()

    await client.run_until_disconnected()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Telegram Forwarder")
    parser.add_argument("--list-chats", action="store_true", help="List chats and exit")
    parser.add_argument("--source-chat-id", type=int, help="Source chat/channel ID")
    parser.add_argument("--destination-chat-id", type=int, help="Destination chat/channel ID")
    parser.add_argument("--keywords", type=str, help="Comma-separated keywords")
    parser.add_argument("--once", action="store_true", help="Forward one matching message and exit")
    return parser


async def main() -> None:
    args = build_parser().parse_args()
    cfg = load_config()

    save_credentials_file(cfg.api_id, cfg.api_hash, cfg.phone_number)

    client = create_client(cfg)
    await ensure_authorized(client, cfg.phone_number)

    if args.list_chats:
        await list_chats(client, cfg.chats_output_file)
        await client.disconnect()
        return

    await client.disconnect()
    await run_forwarder(cfg, args)


if __name__ == "__main__":
    asyncio.run(main())
