from __future__ import annotations


def build_forward_text(text: str, category: str | None = None) -> str:
    body = (text or "").strip()
    if not body:
        return ""

    if category:
        return f"[{category}]\n\n{body}"
    return body
