from __future__ import annotations

import re
from typing import Iterable, List


URL_REGEX = re.compile(
    r"(https?://[^\s]+)",
    re.IGNORECASE,
)

SUPPORTED_DOMAINS = (
    "flipkart.com",
    "myntra.com",
    "ajio.com",
    "amazon.in",
)


def extract_urls(text: str) -> List[str]:
    if not text:
        return []
    return [m.group(1).strip() for m in URL_REGEX.finditer(text)]


def filter_supported(urls: Iterable[str]) -> List[str]:
    result: List[str] = []
    for url in urls:
        lower = url.lower()
        if any(domain in lower for domain in SUPPORTED_DOMAINS):
            result.append(url)
    return result

