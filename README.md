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

# Comma-separated list of source channels (usernames or numeric IDs)
SOURCE_CHANNELS=@TechFactsDeals,@iamprasadtech,@ExtraPe

# Your target channel username or ID (e.g. @YourChannel)
TARGET_CHANNEL=@YourChannel

# Optional: how many seconds to wait between messages to ExtraPe
EXTRAPE_RATE_LIMIT_SECONDS=1.0
```

> **Security:** Never commit `.env` to git or share it.

### 4. Generate a string session (first run)

The first time you run the bot without `TELEGRAM_STRING_SESSION` set, it will:

- Prompt you for your phone number.
- Send you a Telegram login code.
- Ask you to enter that code.
- Save a reusable **string session** to `.session.txt`.

You can then copy the session string into `.env` (`TELEGRAM_STRING_SESSION=`) for non-interactive deployments (VPS, Docker, etc.).

Run:

```bash
python main.py
```

Follow the prompts. Once logged in, stop the script and update `.env` with the printed session (if desired).

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

