from __future__ import annotations

from typing import Iterable


DEFAULT_KEYWORDS = (
    "₹",
    "rs",
    "deal",
    "offer",
    "% off",
)


def _normalize(text: str) -> str:
    return text.lower()


def looks_like_deal(text: str, keywords: Iterable[str] = DEFAULT_KEYWORDS) -> bool:
    """Heuristic check to see if a message is likely to be a deal."""
    if not text:
        return False

    normalized = _normalize(text)
    return any(kw in normalized for kw in keywords)

