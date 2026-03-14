import asyncio
import os
import sys

from dotenv import load_dotenv
from telethon.sessions import StringSession
from telethon.sync import TelegramClient


load_dotenv()


def log_env_presence():
    checks = {
        "API_ID": bool(os.getenv("API_ID", "").strip()),
        "API_HASH": bool(os.getenv("API_HASH", "").strip()),
        "PHONE_NUMBER": bool(os.getenv("PHONE_NUMBER", "").strip()),
        "SOURCE_CHAT_IDS": bool(os.getenv("SOURCE_CHAT_IDS", "").strip() or os.getenv("DEFAULT_SOURCE_CHAT_IDS", "").strip()),
        "DESTINATION_TARGET": bool(os.getenv("DESTINATION_TARGET", "").strip() or os.getenv("DEFAULT_DESTINATION_TARGET", "").strip()),
        "TELEGRAM_SESSION_STRING": bool(os.getenv("TELEGRAM_SESSION_STRING", "").strip()),
    }
    formatted = ", ".join(f"{name}={'yes' if present else 'no'}" for name, present in checks.items())
    print(f"Environment check: {formatted}")


class TelegramForwarder:
    def __init__(self, api_id, api_hash, phone_number):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number or ""

        self.session_string = os.getenv("TELEGRAM_SESSION_STRING", "").strip()
        default_session_name = "session_" + (self.phone_number or "default") + "_multi"
        self.session_name = os.getenv("SESSION_NAME", "").strip() or default_session_name

        if self.session_string:
            self.client = TelegramClient(StringSession(self.session_string), api_id, api_hash)
        else:
            self.client = TelegramClient(self.session_name, api_id, api_hash)

    async def resolve_destination_entity(self, destination_target):
        target = destination_target.strip()

        # Support usernames (for example, @SomeBot) directly.
        if target.startswith("@") or not target.lstrip("-").isdigit():
            return await self.client.get_entity(target)

        destination_id = int(target)

        # Prefer dialogs first because they include access hashes for known peers.
        dialogs = await self.client.get_dialogs()
        for dialog in dialogs:
            if dialog.id == destination_id:
                return dialog.entity

        try:
            return await self.client.get_input_entity(destination_id)
        except ValueError as exc:
            raise ValueError(
                "Could not resolve destination entity from this ID. Open the destination chat once in Telegram, "
                "or use the destination @username instead of numeric ID."
            ) from exc

    async def forward_messages_to_channel(self, source_chat_ids, destination_target):
        await self.client.connect()

        # Ensure the session is authorized before forwarding.
        if not await self.client.is_user_authorized():
            if not sys.stdin.isatty():
                raise RuntimeError(
                    "Telegram session is not authorized in this environment. "
                    "Set TELEGRAM_SESSION_STRING to a valid authorized session string, "
                    "or run locally once to authorize SESSION_NAME and redeploy."
                )
            if not self.phone_number:
                raise RuntimeError(
                    "PHONE_NUMBER is required for interactive sign-in when no valid TELEGRAM_SESSION_STRING is provided."
                )
            await self.client.send_code_request(self.phone_number)
            await self.client.sign_in(self.phone_number, input("Enter the code: "))

        # Allow either a single source ID or multiple IDs.
        if isinstance(source_chat_ids, int):
            source_chat_ids = [source_chat_ids]

        # Track last seen message per source chat.
        last_message_ids = {}
        for source_chat_id in source_chat_ids:
            latest = await self.client.get_messages(source_chat_id, limit=1)
            last_message_ids[source_chat_id] = latest[0].id if latest else 0

        destination_entity = await self.resolve_destination_entity(destination_target)

        while True:
            print("Checking for messages and forwarding them...")
            for source_chat_id in source_chat_ids:
                # Get new messages since the last checked message for this source.
                messages = await self.client.get_messages(
                    source_chat_id,
                    min_id=last_message_ids[source_chat_id],
                    limit=None,
                )

                for message in reversed(messages):
                    # Forward normal content posts: text, links, and media.
                    has_text = bool((message.raw_text or "").strip())
                    has_media = message.media is not None
                    if has_text or has_media:
                        await self.client.forward_messages(destination_entity, message, source_chat_id)
                        print(f"Message forwarded from {source_chat_id}")

                    # Update the last message ID for this source.
                    last_message_ids[source_chat_id] = max(last_message_ids[source_chat_id], message.id)

            # Add a delay before checking for new messages again.
            await asyncio.sleep(5)


def read_credentials():
    env_api_id = os.getenv("API_ID")
    env_api_hash = os.getenv("API_HASH")
    env_phone_number = os.getenv("PHONE_NUMBER")
    has_string_session = bool(os.getenv("TELEGRAM_SESSION_STRING", "").strip())
    if env_api_id and env_api_hash and (env_phone_number or has_string_session):
        return env_api_id, env_api_hash, env_phone_number

    try:
        with open("credentials.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()
            api_id = lines[0].strip() if len(lines) > 0 else None
            api_hash = lines[1].strip() if len(lines) > 1 else None
            phone_number = lines[2].strip() if len(lines) > 2 else ""
            if api_id and api_hash and (phone_number or has_string_session):
                return api_id, api_hash, phone_number
    except FileNotFoundError:
        pass

    return None, None, None


def parse_source_chat_ids(value):
    return [int(chat_id.strip()) for chat_id in value.split(",") if chat_id.strip()]


def read_forwarding_config():
    source_env = os.getenv("SOURCE_CHAT_IDS") or os.getenv("DEFAULT_SOURCE_CHAT_IDS")
    destination_env = os.getenv("DESTINATION_TARGET") or os.getenv("DEFAULT_DESTINATION_TARGET")
    if source_env and destination_env:
        return parse_source_chat_ids(source_env), destination_env.strip()
    return None, None


def write_credentials(api_id, api_hash, phone_number):
    with open("credentials.txt", "w", encoding="utf-8") as file:
        file.write(api_id + "\n")
        file.write(api_hash + "\n")
        file.write(phone_number + "\n")


async def main():
    log_env_presence()
    api_id, api_hash, phone_number = read_credentials()

    if api_id is None or api_hash is None or phone_number is None:
        has_string_session = bool(os.getenv("TELEGRAM_SESSION_STRING", "").strip())
        if not sys.stdin.isatty():
            raise RuntimeError(
                "Missing credentials. Set API_ID and API_HASH. "
                "Also set PHONE_NUMBER (file sessions) or TELEGRAM_SESSION_STRING (recommended for deployments)."
            )

        api_id = input("Enter your API ID: ")
        api_hash = input("Enter your API Hash: ")
        if has_string_session:
            phone_number = ""
        else:
            phone_number = input("Enter your phone number: ")
            write_credentials(api_id, api_hash, phone_number)

    forwarder = TelegramForwarder(api_id, api_hash, phone_number)

    print("Forwarding mode: text + media + links")
    source_chat_ids, destination_target = read_forwarding_config()
    if source_chat_ids is None or destination_target is None:
        if not sys.stdin.isatty():
            raise RuntimeError(
                "Missing forwarding config. Set SOURCE_CHAT_IDS and DESTINATION_TARGET "
                "environment variables for non-interactive deployments."
            )
        source_chat_input = input("Enter source chat IDs (comma separated): ")
        source_chat_ids = parse_source_chat_ids(source_chat_input)
        destination_target = input("Enter the destination chat ID or @username: ").strip()

    await forwarder.forward_messages_to_channel(source_chat_ids, destination_target)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nForwarder stopped by user.")
    except RuntimeError as exc:
        print(f"Startup error: {exc}")
        raise SystemExit(1)
