# Telegram Forwarder Project

A clean Telegram forwarder using Telethon.

## Main File

Use main.py as the main code for this project.

## Features

- Forward new messages from a source chat/channel to a destination chat/channel
- Filter forwarding by keywords
- Optional media forwarding
- Optional link-only forwarding
- Optional category hint prefix
- Dedupe protection using SQLite
- Chat listing utility

## Setup

1. Install requirements:

```bash
pip install -r requirements.txt
```

2. Save credentials:

```bash
python setup.py
```

3. List chats to get IDs:

```bash
python main.py --list-chats
```

4. Start forwarding:

```bash
python main.py
```

For production (Railway/VPS/Docker), set `TELEGRAM_STRING_SESSION` so login does not require interactive OTP input.
Also set `SOURCE_CHAT_IDS` and `DESTINATION_CHAT_ID` to avoid interactive prompts.

## CLI Options

```bash
python main.py --help
```

Useful options:

- --list-chats
- --source-chat-id <id>
- --destination-chat-id <id>
- --keywords "deal,offer,discount"
- --once

## Environment Variables

You can use .env with:

- TELEGRAM_API_ID
- TELEGRAM_API_HASH
- TELEGRAM_PHONE_NUMBER
- TELEGRAM_STRING_SESSION (recommended for production)
- TELEGRAM_SESSION_NAME (optional)
- DEDUPE_DB_PATH (optional)
- SOURCE_CHAT_IDS (required in non-interactive deployments, comma-separated IDs)
- DESTINATION_CHAT_ID (required in non-interactive deployments)
- FORWARD_KEYWORDS (optional; if omitted, all messages are forwarded)
- FORWARD_MEDIA=true|false (optional)
- FORWARD_ONLY_WITH_LINKS=true|false (optional)
- INCLUDE_CATEGORY_HINT=true|false (optional)
