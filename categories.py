from __future__ import annotations

from typing import Optional

CATEGORY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "mobile": ("iphone", "samsung", "realme", "redmi", "oneplus", "mobile", "smartphone"),
    "laptop": ("laptop", "notebook", "macbook"),
    "fashion": ("shirt", "t-shirt", "jeans", "saree", "dress", "shoes"),
    "electronics": ("earbuds", "headphone", "speaker", "tv", "smartwatch"),
    "home": ("kitchen", "cooker", "cookware", "mixer", "mattress", "sofa"),
}


def detect_category(text: str) -> Optional[str]:
    normalized = (text or "").lower()
    if not normalized:
        return None

    for label, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in normalized for kw in keywords):
            return label
    return None
