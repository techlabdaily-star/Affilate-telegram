"""Helpers for using the Pollinations public APIs.

This module is intentionally minimal: it does not require any API keys and
works using Pollinations' public endpoints.

It includes:
- `rewrite_text()` for AI-powered text rewriting (used by the bot when enabled)
- `generate_image()` for image generation via the Pollinations `flux` model

The module also exposes a small CLI for quick experimentation.
"""

from __future__ import annotations

import argparse
import os
import random
from datetime import datetime
from urllib.parse import quote

import requests


def rewrite_text(original_text: str, tone: str = "professional", grok_api_key: str | None = None) -> str:
    """Rewrite input text using Pollinations (Grok integration disabled due to API issues).

    Args:
        original_text: The text to rewrite.
        tone: A single-word description of how the text should sound.
        grok_api_key: Ignored for now.

    Returns:
        The rewritten text (or an error string on failure).
    """

    # Use Pollinations (free and working)
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


def generate_image(
    prompt: str,
    save_dir: str = ".",
    width: int = 1080,
    height: int = 1920,
    enhance: bool = True,
    seed: int | None = None,
) -> str:
    """Generate an image from a text prompt using Pollinations' flux endpoint.

    Returns the saved image path.
    """

    if seed is None:
        seed = random.randint(1, 999_999_999)

    params = {
        "safe": True,
        "seed": seed,
        "width": width,
        "height": height,
        "nologo": True,
        "private": True,
        "model": "flux",
        "enhance": enhance,
        "referrer": "pollinations.py",
    }

    encoded_prompt = quote(prompt)
    query_params = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?{query_params}"

    try:
        response = requests.get(url=url, headers={"Content-Type": "application/json"}, timeout=60)
        if response.status_code != 200:
            raise RuntimeError(f"Failed to generate image. Status code: {response.status_code}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_name = f"img_{timestamp}.png"
        os.makedirs(save_dir, exist_ok=True)
        image_path = os.path.join(save_dir, image_name)
        with open(image_path, "wb") as f:
            f.write(response.content)
        return image_path
    except Exception as e:
        raise RuntimeError(f"Image generation failed: {e}") from e


def _main() -> int:
    parser = argparse.ArgumentParser(description="Pollinations helpers (text rewrite + image generation)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    rewrite = subparsers.add_parser("rewrite", help="Rewrite text using Pollinations")
    rewrite.add_argument("text", help="Text to rewrite")
    rewrite.add_argument("--tone", default="professional", help="Tone to rewrite in")

    image = subparsers.add_parser("image", help="Generate an image from a prompt")
    image.add_argument("prompt", help="Text prompt for the image")
    image.add_argument("--save-dir", default=".", help="Directory to save generated images")
    image.add_argument("--width", type=int, default=1080, help="Image width")
    image.add_argument("--height", type=int, default=1920, help="Image height")
    image.add_argument(
        "--enhance",
        action="store_true",
        help="Apply automatic enhancement (default: enabled with --enhance)",
    )
    image.add_argument("--no-enhance", dest="enhance", action="store_false")
    image.add_argument("--seed", type=int, default=None, help="Optional seed for deterministic output")

    args = parser.parse_args()

    if args.command == "rewrite":
        print(rewrite_text(args.text, tone=args.tone))
        return 0

    if args.command == "image":
        path = generate_image(
            prompt=args.prompt,
            save_dir=args.save_dir,
            width=args.width,
            height=args.height,
            enhance=args.enhance,
            seed=args.seed,
        )
        print(path)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(_main())
