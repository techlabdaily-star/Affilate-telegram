# Telegram Affiliate Deal Automation Bot

Automates collecting deal messages from selected Telegram channels, converts product links into affiliate links using `@ExtraPeBot`, and republishes them to your own Telegram channel.

## Features

- **Monitor source channels** for new deal messages.
- **Extract product links** for Flipkart, Myntra, Ajio, Amazon, and more.
- **Send links to `@ExtraPeBot`** and capture converted affiliate links.
- **Format deals** into a consistent template.
- **Post to your target channel** automatically.
- **Avoid duplicates** using a small SQLite database.

## Tech Stack

- Python
- [Telethon](https://github.com/LonamiWebs/Telethon)
- SQLite (for deduplication)

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
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

The bot will:

1. Connect to Telegram.
2. Start listening for new messages in `SOURCE_CHANNELS`.
3. For each new message:
   - Extract supported product links.
   - Send them to `@ExtraPeBot`.
   - Receive affiliate links.
   - Build a formatted deal.
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

