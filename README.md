# Telegram Affiliate Deal Automation Bot

Automates collecting deal messages from selected Telegram channels, converts product links into affiliate links using `@ExtraPeBot`, and republishes them to your own Telegram channel.

## Features

- **Monitor source channels** for new deal messages.
- **Extract and expand product links** asynchronously for Flipkart, Myntra, Ajio, Amazon, and more.
- **Send links to `@ExtraPeBot`** and capture converted affiliate links.
- **Format deals** into a consistent Markdown template.
- **AI-powered text rewriting** using Pollinations API for clearer deal descriptions.
- **Forward original messages** (text + images) when enabled.
- **Post to your target channel** automatically.
- **Avoid duplicates** using a SQLite database.
- **Repost trending deals** after configurable hours.

## Tech Stack

- Python (asyncio for concurrent operations)
- [Telethon](https://github.com/LonamiWebs/Telethon) for Telegram API
- [aiohttp](https://docs.aiohttp.org/) for async URL expansion
- SQLite (for deduplication)
- Pollinations API (for AI text rewriting)

## Setup

### 1. Quick Setup (Recommended)

Use the interactive setup script:

```bash
python setup.py
```

This will:
- Guide you through credential setup
- Generate your session string
- Save credentials for future use
- Provide next steps

### 2. Manual Setup

If you prefer manual setup, follow these steps:

#### Create credentials.txt

Create a `credentials.txt` file with your Telegram API credentials:

```
YOUR_API_ID
YOUR_API_HASH
YOUR_PHONE_NUMBER
```

#### Generate Session String

```bash
python gen_session.py
```

Or to list all your chats:

```bash
python gen_session.py --list-chats
```

### 2. Create a Telegram API app

1. Open `https://my.telegram.org/apps` in your browser.
2. Log in with the **Telegram account** that will run this automation.
3. Create an app and note:
   - `api_id`
   - `api_hash`

This account must be joined to all **source channels** and have permission to post in your **target channel**.

### 3. Create `.env`

Create a `.env` file in the project root:

```env
TELEGRAM_API_ID=123456
TELEGRAM_API_HASH=your_api_hash_here

# Telethon string session for the account that will run the bot.
# The first run of main.py can generate this for you interactively.
TELEGRAM_STRING_SESSION=

# Comma-separated list of source channels (usernames or numeric IDs).
# The bot will resolve @usernames to numeric IDs at runtime so the bot
# keeps working even if a channel changes its @username.
SOURCE_CHANNELS=@TechFactsDeals,@iamprasadtech,@ExtraPe

# Your target channel username or ID (e.g. @YourChannel)
TARGET_CHANNEL=@YourChannel

# Optional: forward the original source message (text + media) to the target channel
# before sending the formatted affiliate deal message.
# Set to "true" to enable.
FORWARD_ORIGINAL=false

# Optional: rewrite incoming deal text using Pollinations (free AI text rewrite)
POLLINATIONS_REWRITE=false
POLLINATIONS_TONE=professional

# Optional: how many seconds to wait between messages to ExtraPe
EXTRAPE_RATE_LIMIT_SECONDS=1.0
```

> **Security:** Never commit `.env` to git or share it.

### 4. Generate a string session

You must provide a valid `TELEGRAM_STRING_SESSION` for the bot to run in non-interactive environments (Railway, Docker, VPS, etc.).

We include a helper script to create one locally:

```bash
python gen_session.py
```

The script will ask you to log in with your phone number and will then print the session string. Copy that value and set it in your `.env` (or in the Railway variables) under `TELEGRAM_STRING_SESSION`.

> **Important:** The bot will **not** prompt interactively at runtime. It will fail immediately if the session is missing or invalid.

### 5. Run the bot

```bash
python main.py
```

**Useful commands:**
- `python main.py --list-chats` - List all chats you have access to
- `python main.py` - Start the bot normally

The bot will:

1. Connect to Telegram.
2. Start listening for new messages in `SOURCE_CHANNELS`.
3. For each new message:
   - Extract and asynchronously expand supported product links.
   - Send them to `@ExtraPeBot` for affiliate conversion.
   - Receive affiliate links.
   - Optionally rewrite text using AI for clarity.
   - Optionally forward original message (text + media).
   - Build a formatted Markdown deal message.
   - Post it to `TARGET_CHANNEL`, skipping duplicates.

## Customization

- **Message template:** Edit `formatter.py` if you want to change the way deals are formatted.
- **Supported domains:** Edit `SUPPORTED_DOMAINS` in `link_extractor.py` to add/remove e-commerce sites.
- **Rate limiting:** Adjust `EXTRAPE_RATE_LIMIT_SECONDS` in `.env` to be more conservative if you hit limits with `@ExtraPeBot`.

## Optional: Pollinations helpers (text rewrite + image generation)

This repo includes a small helper module for Pollinations' free, no-key APIs:

- `pollinations.rewrite_text(...)` (used by the bot when `POLLINATIONS_REWRITE=true`)
- `pollinations.generate_image(...)` (create images from text prompts)

### CLI usage

```bash
python -m pollinations rewrite --tone academic "write a short tweet about coding"

python -m pollinations image "a futuristic city skyline" --save-dir ./imgs --width 1024 --height 1024
```

## Production / 24x7 Running

On a VPS you can use:

- `systemd` service
- `pm2` (with `--interpreter python`)
- `screen` or `tmux`

Basic idea:

```bash
python main.py >> bot.log 2>&1
```

Keep the process running and monitor logs for errors.

## Notes & Limitations

- This project uses a **user account** (Telethon session), not a bot token, so it can read public channels like `@TechFactsDeals` directly.
- Make sure your Telegram account respects Telegram’s terms of service and local regulations for affiliate marketing and automation.

