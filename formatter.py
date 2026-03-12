from __future__ import annotations

import re
from typing import Optional


PRICE_REGEX = re.compile(r"(₹\s?\d[\d,]*)")


def extract_price(text: str) -> Optional[str]:
    if not text:
        return None
    m = PRICE_REGEX.search(text)
    if not m:
        return None
    return m.group(1).replace(" ", "")


def build_deal_message(
    original_text: str,
    product_name: str | None,
    affiliate_url: str,
    channel_mention: str,
    is_trending: bool = False,
    is_flash: bool = False,
    category_label: str | None = None,
) -> str:
    """
    Build the final deal message to post.

    - Tries to keep useful original context.
    - Extracts a price if present.
    """
    price = extract_price(original_text)

    title = product_name or "Exclusive Deal"

    lines: list[str] = []
    if is_flash:
        lines.append("⚡ FLASH DEAL")
    elif is_trending:
        lines.append("🚀 VIRAL DEAL")
    else:
        lines.append("🔥 HOT DEAL")
    lines.append("")
    if category_label:
        lines.append(f"{category_label}")
        lines.append(title.strip())
    else:
        lines.append(title.strip())

    if price:
        lines.append("")
        lines.append(f"💰 Price: {price}")

    lines.append("")
    lines.append("🛒 Buy Now")
    lines.append(affiliate_url.strip())
    lines.append("")
    lines.append(f"📢 Join: {channel_mention}")

    return "\n".join(lines)

