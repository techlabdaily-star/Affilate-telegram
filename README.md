# Telegram Autoforwarder

This project forwards Telegram deals from one or more source chats into a destination chat or bot, then reformats them into cleaner posts before sending.

## Current Features

- Multi-source forwarding to one destination.
- Smart deal formatting for text posts and media captions.
- Amazon affiliate tag rewriting from `.env`.
- Store-aware labels for Amazon, Flipkart, Myntra, Ajio, Meesho, Nykaa, Tata Cliq, and Snapdeal.
- Duplicate-deal blocking with a configurable TTL.
- Optional strict mode to skip stickers, polls, and service messages.
- Optional blocked-keyword filtering.
- Optional minimum discount filtering.
- Background service scripts for start, stop, and status.

## Setup

1. Create a virtual environment and install dependencies:

   ```bash
   python3 -m venv .venv
   ./.venv/bin/python -m pip install -r requirements.txt
   ```

2. Run the script once interactively to create credentials and Telegram session files:

   ```bash
   ./.venv/bin/python TelegramForwarder.py
   ```

3. Configure `.env` with your affiliate and forwarding defaults.

## Important `.env` Settings

```env
AFFILIATE_AMAZON_TAG=bypineapple-21
AFFILIATE_GENERIC_TEMPLATE=
SEEN_DEAL_TTL_HOURS=24
BLOCKED_KEYWORDS=expired,out of stock,sold out
FORWARDER_LOG_FILE=forwarder.log
MIN_DISCOUNT_PERCENT=0
AUTO_START_FORWARDING=true
DEFAULT_SOURCE_CHAT_IDS=-1001422047391,-1001412868909,-1001670336143,-1001389782464
DEFAULT_DESTINATION_TARGET=2015117555
DEFAULT_KEYWORDS=
DEFAULT_STRICT_MODE=true
```

## Run Modes

### Interactive mode

```bash
./.venv/bin/python TelegramForwarder.py
```

### Background mode

```bash
./start_forwarder.sh
```

Stop it with:

```bash
./stop_forwarder.sh
```

Check status with:

```bash
./status_forwarder.sh
```

Watch logs with:

```bash
tail -f forwarder.log
```

## Preview Formatter

You can preview how a raw deal will be cleaned and rewritten before sending it live.

Paste from stdin:

```bash
printf "Boat Watch\nMRP Rs 2999\nPrice Rs 1499\nhttps://www.amazon.in/dp/B0TEST1234\n" | ./.venv/bin/python preview_deal.py
```

Or pass a text file:

```bash
./.venv/bin/python preview_deal.py sample_deal.txt
```

## How Posting Works

1. The bot reads incoming message text and media captions.
2. It extracts the first link and rewrites Amazon links with your affiliate tag.
3. It detects product name, prices, coupon codes, bank offers, and store.
4. It formats the deal into a cleaner post.
5. It skips duplicates, blocked keywords, and optionally low-discount deals.
6. It sends the result to the configured destination.

## Project Files

- `TelegramForwarder.py`: main runtime and forwarding loop.
- `smart_formatter.py`: deal cleanup and formatting logic.
- `affiliate_links.py`: link rewriting logic.
- `deal_cache.py`: duplicate-deal cache.
- `start_forwarder.sh`: start background service.
- `stop_forwarder.sh`: stop background service.
- `status_forwarder.sh`: check current service status.

## Notes

- Keep `.env`, `credentials.txt`, and `.session` files private.
- Open the destination bot or chat at least once in Telegram if entity resolution fails.
- Leave `AFFILIATE_GENERIC_TEMPLATE` empty unless you have a real generic tracking service.
