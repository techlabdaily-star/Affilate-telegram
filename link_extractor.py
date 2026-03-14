from __future__ import annotations

import re
from typing import List

URL_REGEX = re.compile(r"(https?://[^\s]+)", re.IGNORECASE)


def extract_urls(text: str) -> List[str]:
    if not text:
        return []
    return [m.group(1).strip() for m in URL_REGEX.finditer(text)]


def has_urls(text: str) -> bool:
    return bool(extract_urls(text))
