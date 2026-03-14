# Telegram Autoforwarder

This project forwards Telegram deals from one or more source chats into a destination chat or bot, then reformats them into cleaner posts before sending.

## Current Features

- Multi-source forwarding to one destination.
- Smart deal formatting for text posts and media captions.
- Amazon affiliate tag rewriting from `.env`.
- Store-aware labels for Amazon, Flipkart, Myntra, Ajio, Meesho, Nykaa, Tata Cliq, and Snapdeal.
# Telegram Forwarder

This project forwards Telegram messages from one or more source chats to a single destination chat or bot.
It forwards text, links, images, and other media posts.

## Features

- Multi-source forwarding.
- Destination can be chat ID or `@username`.
- Forwards both text and media messages.
- Works in interactive local mode and non-interactive deployment mode.

## Local Run

1. Install dependencies:

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

2. Start:

```bash
./.venv/bin/python TelegramForwarder.py
```

You will be prompted for:
- Telegram credentials (first run only)
- Source chat IDs (comma separated)
- Destination chat ID or `@username`

## Deployment (Worker)

Set these environment variables in your deployment platform:

```env
API_ID=123456
API_HASH=your_api_hash
SOURCE_CHAT_IDS=-1001422047391,-1001412868909
DESTINATION_TARGET=2015117555
TELEGRAM_SESSION_STRING=your_authorized_string_session
# Optional when using file session instead of string session:
# PHONE_NUMBER=+911234567890
# SESSION_NAME=session_+91XXXXXXXXXX_multi
```

Notes:
- `Procfile` defines a worker process: `python TelegramForwarder.py`
- `TELEGRAM_SESSION_STRING` is the recommended production auth method because `.session` files are usually git-ignored.
- If you prefer file sessions, use a fixed `SESSION_NAME` and persist that session file in your host volume.

## Required Files

- `TelegramForwarder.py`
- `requirements.txt`
- `Procfile`
Stop it with:
