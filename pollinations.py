"""Helpers for using the Pollinations public APIs.

This module is intentionally minimal: it does not require any API keys and
works using Pollinations' public endpoints.

The `rewrite_text` helper demonstrates how to call the text-generation endpoint.
"""

from __future__ import annotations

import requests


def rewrite_text(original_text: str, tone: str = "professional") -> str:
    """Rewrite input text using Pollinations text generation API.

    Args:
        original_text: The text to rewrite.
        tone: A single-word description of how the text should sound.

    Returns:
        The rewritten text (or an error string on failure).
    """

    url = "https://text.pollinations.ai"
    system_prompt = (
        "You are a helpful assistant. Rewrite the user's text to be "
        f"{tone}, clear, and grammatically correct. Only return the rewritten text."
    )

    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": original_text},
        ],
        "model": "openai",  # alternatives: "mistral", "llama"
        "jsonMode": False,
    }

    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            return response.text
        return f"Error: {response.status_code}"
    except Exception as e:
        return f"Request failed: {e}"


if __name__ == "__main__":
    # Example usage when running this module directly.
    sample = "i need help for making my paper more better for school"
    print("Original:", sample)
    print("Rewritten:", rewrite_text(sample, tone="academic"))
