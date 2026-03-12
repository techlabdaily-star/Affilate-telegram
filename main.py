from __future__ import annotations

import asyncio
from typing import Optional

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import Message

from affiliate_client import AffiliateClient
from categories import detect_category
from config import Settings, load_settings
from dedupe_store import DedupeStore
from filters import looks_like_deal
from formatter import build_deal_message
from link_extractor import extract_urls, filter_supported


async def _create_client(settings: Settings) -> TelegramClient:
    if settings.string_session:
        session = StringSession(settings.string_session)
    else:
        # Use a temporary in-memory session; user can later copy the string session
        session = StringSession()

    client = TelegramClient(
        session=session,
        api_id=settings.api_id,
        api_hash=settings.api_hash,
    )
    await client.connect()

    if not await client.is_user_authorized():
        print("You are not logged in. Starting interactive login flow.")
        phone = input("Enter your phone number (with country code): ")
        await client.send_code_request(phone)
        code = input("Enter the code you received: ")
        await client.sign_in(phone=phone, code=code)
        print("Logged in successfully.")
        print("Your string session (store securely, do NOT share):")
        print(StringSession.save(client.session))

    return client


def _guess_product_name(message: Message) -> Optional[str]:
    text = (message.message or "").strip()
    if not text:
        return None
    # Simple heuristic: first non-empty line, without URLs
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if "http://" in line or "https://" in line:
            continue
        if len(line) < 4:
            continue
        return line
    return None


async def main() -> None:
    settings = load_settings()
    dedupe = DedupeStore(settings.db_path)
    await dedupe.init()

    client = await _create_client(settings)

    affiliate_client = AffiliateClient(
        client=client,
        extrape_username=settings.extrape_username,
        rate_limit_seconds=settings.extrape_rate_limit_seconds,
    )

    print("Listening for new deal messages...")

    @client.on(events.NewMessage(chats=settings.source_channels))
    async def handler(event: events.NewMessage.Event) -> None:
        msg: Message = event.message
        print(f"New message in chat {msg.chat_id} with id {msg.id}")

        if await dedupe.has_processed(msg.chat_id, msg.id):
            print("Message already processed, skipping.")
            return

        text = msg.message or ""
        if not looks_like_deal(text):
            print("Message does not look like a deal, skipping.")
            return

        lower_text = text.lower()
        is_flash = any(
            phrase in lower_text
            for phrase in ("lightning deal", "limited time", "flash sale", "only few minutes")
        )
        category_label = detect_category(text)

        all_urls = extract_urls(text)
        if not all_urls:
            print("No URLs found in message, skipping.")
            return

        urls = filter_supported(all_urls)
        if urls:
            print(f"Found supported URLs: {urls}")
        else:
            # Fall back to sending all URLs to ExtraPe; it will ignore unsupported ones.
            urls = all_urls
            print(f"No supported domains matched. Falling back to all URLs: {urls}")

        if not urls:
            print("No URLs to send after filtering, skipping.")
            return

        try:
            url_map = await affiliate_client.convert_links(urls)
        except Exception as exc:  # noqa: BLE001
            # In production you might want structured logging here
            print(f"Error converting links via ExtraPe: {exc}")
            return

        if not url_map:
            print("ExtraPe did not return any affiliate URLs, skipping.")
            return

        # For simplicity, only use the first affiliate link
        original_url, affiliate_url = next(iter(url_map.items()))

        # Record link observation for basic trending detection
        await dedupe.record_link_seen(msg.chat_id, msg.id, original_url)
        stats = await dedupe.get_link_stats(original_url)
        is_trending = stats["source_count"] >= settings.trending_min_sources
        if is_trending:
            print(
                f"Link {original_url} is trending: "
                f"seen {stats['seen_count']} times across {stats['source_count']} sources.",
            )

        product_name = _guess_product_name(msg)
        final_text = build_deal_message(
            original_text=text,
            product_name=product_name,
            affiliate_url=affiliate_url,
            channel_mention=settings.target_channel,
            is_trending=is_trending,
            is_flash=is_flash,
            category_label=category_label,
        )

        try:
            if msg.media:
                await client.send_file(
                    settings.target_channel,
                    msg.media,
                    caption=final_text,
                    link_preview=True,
                )
            else:
                await client.send_message(settings.target_channel, final_text, link_preview=True)
            await dedupe.mark_processed(msg.chat_id, msg.id, affiliate_url=affiliate_url)

            # Schedule reposts for extra exposure if enabled
            if settings.repost_enabled and (
                not settings.repost_trending_only or is_trending
            ):
                await dedupe.schedule_repost(
                    affiliate_url=affiliate_url,
                    message_text=final_text,
                    hours_from_now=settings.repost_after_hours,
                )
            print(
                f"Posted deal from chat {msg.chat_id} message {msg.id} to {settings.target_channel}",
            )
        except Exception as exc:  # noqa: BLE001
            print(f"Failed to post deal: {exc}")

    async def repost_loop() -> None:
        if not settings.repost_enabled:
            return
        while True:
            try:
                due = await dedupe.get_due_reposts()
                for repost_id, affiliate_url, message_text in due:
                    try:
                        await client.send_message(settings.target_channel, message_text, link_preview=True)
                        await dedupe.mark_repost_sent(repost_id)
                        print(f"Reposted deal for {affiliate_url} from repost queue.")
                    except Exception as exc:  # noqa: BLE001
                        print(f"Failed to repost deal {affiliate_url}: {exc}")
            except Exception as exc:  # noqa: BLE001
                print(f"Error while processing repost queue: {exc}")
            await asyncio.sleep(300)  # check every 5 minutes

    # Run until Ctrl+C
    try:
        # launch background tasks
        asyncio.create_task(repost_loop())
        await client.run_until_disconnected()
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

