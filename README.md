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
- TELEGRAM_SESSION_NAME (optional)
- DEDUPE_DB_PATH (optional)
- FORWARD_MEDIA=true|false (optional)
- FORWARD_ONLY_WITH_LINKS=true|false (optional)
- INCLUDE_CATEGORY_HINT=true|false (optional)
