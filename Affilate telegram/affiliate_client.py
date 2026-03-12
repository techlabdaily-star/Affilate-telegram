from __future__ import annotations

import asyncio
from typing import Dict, List

from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.tl.custom import Conversation
from telethon.tl.types import Message

from link_extractor import extract_urls


class AffiliateClient:
    def __init__(
        self,
        client: TelegramClient,
        extrape_username: str,
        rate_limit_seconds: float = 1.0,
    ) -> None:
        self._client = client
        self._extrape_username = extrape_username
        self._rate_limit_seconds = rate_limit_seconds
        self._lock = asyncio.Lock()

    async def convert_links(self, urls: List[str]) -> Dict[str, str]:
        """
        Send product URLs to ExtraPe bot and return a mapping of
        original -> affiliate URLs.
        """
        if not urls:
            return {}

        async with self._lock:
            # Serialize to be nice to the bot and avoid spam/flood limits
            mapping: Dict[str, str] = {}
            async with self._client.conversation(
                self._extrape_username, timeout=60
            ) as conv:  # type: Conversation
                for url in urls:
                    try:
                        await conv.send_message(url)
                        reply: Message = await conv.get_response()
                    except FloodWaitError as e:
                        await asyncio.sleep(e.seconds + 1)
                        continue

                    affiliate_urls = extract_urls(reply.message or "")
                    if affiliate_urls:
                        # Use first affiliate URL
                        mapping[url] = affiliate_urls[0]

                    await asyncio.sleep(self._rate_limit_seconds)

        return mapping

