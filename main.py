from __future__ import annotations

import asyncio
import logging
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
from link_extractor import extract_and_expand_urls, filter_supported
from pollinations import rewrite_text

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def _create_client(settings: Settings) -> TelegramClient:
    # Telethon StringSession will raise ValueError if the provided string is invalid
    if settings.string_session:
        try:
            session = StringSession(settings.string_session)
        except ValueError:
            logger.warning("Warning: TELEGRAM_STRING_SESSION is invalid, falling back to temporary session")
            session = StringSession()
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
        # cannot perform interactive login in a headless environment like Railway
        if settings.string_session:
            raise RuntimeError("Provided TELEGRAM_STRING_SESSION is invalid or expired; set a valid one in environment variables.")
        else:
            raise RuntimeError("Missing TELEGRAM_STRING_SESSION. Generate one locally and add it to Railway variables.")

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


def shorten_url(url: str) -> str:
    try:
        response = requests.get(f"http://tinyurl.com/api-create.php?url={url}", timeout=5)
        if response.status_code == 200:
            return response.text.strip()
        else:
            return url
    except Exception:
        return url


async def main() -> None:
    settings = load_settings()
    dedupe = DedupeStore(settings.db_path)
    await dedupe.init()

    client = await _create_client(settings)

    async def _resolve_chat_id(chat: str | int) -> str | int:
        """Resolve a username/handle to a numeric chat id (falls back to input on failure)."""
        try:
            entity = await client.get_entity(chat)
            return entity.id
        except Exception:
            return chat

    # Use numeric IDs to avoid username changes breaking the listener.
    resolved_source_channels = [
        await _resolve_chat_id(ch) for ch in settings.source_channels
    ]
    resolved_target_channel = await _resolve_chat_id(settings.target_channel)

    affiliate_client = AffiliateClient(
        client=client,
        extrape_username=settings.extrape_username,
        rate_limit_seconds=settings.extrape_rate_limit_seconds,
    )

    logger.info("Listening for new deal messages...")

    @client.on(events.NewMessage(chats=resolved_source_channels))
    async def handler(event: events.NewMessage.Event) -> None:
        msg: Message = event.message
        logger.info(f"New message in chat {msg.chat_id} with id {msg.id}")

        if await dedupe.has_processed(msg.chat_id, msg.id):
            logger.info("Message already processed, skipping.")
            return

        text = msg.message or ""
        if not looks_like_deal(text):
            logger.info("Message does not look like a deal, skipping.")
            return

        # Optionally rewrite incoming deal text for clarity/consistency using Pollinations.
        text = original_text
        if settings.use_pollinations_rewrite:
            try:
                rewritten = rewrite_text(original_text, tone=settings.pollinations_tone, grok_api_key=settings.grok_api_key)
                # Pollinations returns a short error string on failure.
                if rewritten and not rewritten.startswith("Error:") and not rewritten.startswith("Request failed:"):
                    text = rewritten
                else:
                    logger.warning(f"Text rewrite failed; using original text: {rewritten}")
            except Exception as exc:  # noqa: BLE001
                logger.error(f"Text rewrite error: {exc}")

        lower_text = text.lower()
        is_flash = any(
            phrase in lower_text
            for phrase in ("lightning deal", "limited time", "flash sale", "only few minutes")
        )
        category_label = detect_category(text)


        # Extract and expand all URLs (follows redirects for short links)
        # Use original text for URL extraction so rewriting does not remove/alter links.
        urls = await extract_and_expand_urls(original_text)
        if not urls:
            logger.info("No URLs found in message, skipping.")
            return

        # If you want only the first link, uncomment the next two lines:
        # urls = [urls[0]] if urls else []

        logger.debug(f"Expanded URLs: {urls}")

        try:
            url_map = await affiliate_client.convert_links(urls)
        except Exception as exc:  # noqa: BLE001
            # In production you might want structured logging here
            logger.error(f"Error converting links via ExtraPe: {exc}")
            return

        if not url_map:
            logger.warning("ExtraPe did not return any affiliate URLs, skipping.")
            return

        # For simplicity, only use the first affiliate link
        original_url, affiliate_url = next(iter(url_map.items()))
        affiliate_url = shorten_url(affiliate_url)

        # Record link observation for basic trending detection
        await dedupe.record_link_seen(msg.chat_id, msg.id, original_url)
        stats = await dedupe.get_link_stats(original_url)
        is_trending = stats["source_count"] >= settings.trending_min_sources
        if is_trending:
            logger.info(
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
            reply_to_msg_id = None
            if settings.forward_original:
                try:
                    forwarded = await client.forward_messages(resolved_target_channel, msg)
                    if isinstance(forwarded, list):
                        reply_to_msg_id = forwarded[0].id if forwarded else None
                    else:
                        reply_to_msg_id = forwarded.id if forwarded else None
                except Exception as exc:  # noqa: BLE001
                    logger.error(f"Failed to forward original message: {exc}")

                await client.send_message(
                    resolved_target_channel,
                    final_text,
                    link_preview=True,
                    reply_to=reply_to_msg_id,
                    parse_mode='md',
                )
            else:
                if msg.media:
                    await client.send_file(
                        resolved_target_channel,
                        msg.media,
                        caption=final_text,
                        link_preview=True,
                        parse_mode='md',
                    )
                else:
                    await client.send_message(resolved_target_channel, final_text, link_preview=True, parse_mode='md')

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
            logger.info(
                f"Posted deal from chat {msg.chat_id} message {msg.id} to {settings.target_channel}",
            )
        except Exception as exc:  # noqa: BLE001
            logger.error(f"Failed to post deal: {exc}")

    async def repost_loop() -> None:
        if not settings.repost_enabled:
            return
        while True:
            try:
                due = await dedupe.get_due_reposts()
                for repost_id, affiliate_url, message_text in due:
                    try:
                        await client.send_message(resolved_target_channel, message_text, link_preview=True, parse_mode='md')
                        await dedupe.mark_repost_sent(repost_id)
                        logger.info(f"Reposted deal for {affiliate_url} from repost queue.")
                    except Exception as exc:  # noqa: BLE001
                        logger.error(f"Failed to repost deal {affiliate_url}: {exc}")
            except Exception as exc:  # noqa: BLE001
                logger.error(f"Error while processing repost queue: {exc}")
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

