from __future__ import annotations

from typing import Optional


CATEGORY_KEYWORDS = {
    "📱 Mobile Deals": (
        "mobile",
        "smartphone",
        "iphone",
        "android",
        "realme",
        "redmi",
        "samsung",
        "oneplus",
    ),
    "💻 Laptop Deals": (
        "laptop",
        "notebook",
        "macbook",
        "gaming laptop",
    ),
    "🎧 Electronics": (
        "earbuds",
        "headphone",
        "headset",
        "tws",
        "bluetooth",
        "speaker",
        "soundbar",
        "tv",
        "smartwatch",
    ),
    "👕 Fashion": (
        "t-shirt",
        "shirt",
        "jeans",
        "kurta",
        "saree",
        "dress",
        "shoes",
        "sneakers",
        "heels",
        "hoodie",
    ),
    "🏠 Home & Kitchen": (
        "kitchen",
        "mixer",
        "grinder",
        "cooker",
        "cookware",
        "bedsheet",
        "pillow",
        "mattress",
        "sofa",
        "chair",
        "table",
        "lamp",
    ),
}


def detect_category(text: str) -> Optional[str]:
    if not text:
        return None

    lower = text.lower()
    for label, keywords in CATEGORY_KEYWORDS.items():
        if any(k in lower for k in keywords):
            return label
    return None

