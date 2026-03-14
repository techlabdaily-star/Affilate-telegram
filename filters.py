from __future__ import annotations

from typing import Iterable, List


def parse_keywords(raw: str | None) -> List[str]:
    if not raw:
        return []
    return [k.strip().lower() for k in raw.split(",") if k.strip()]


def message_matches(text: str, keywords: Iterable[str]) -> bool:
    normalized = (text or "").lower()
    kws = [k for k in keywords if k]
    if not kws:
        return True
    return any(k in normalized for k in kws)
