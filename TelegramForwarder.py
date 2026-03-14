import asyncio
from telethon.sync import TelegramClient

class TelegramForwarder:
    def __init__(self, api_id, api_hash, phone_number):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.client = TelegramClient('session_' + phone_number + '_multi', api_id, api_hash)

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

        # Ensure you're authorized
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            await self.client.sign_in(self.phone_number, input('Enter the code: '))

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
                    limit=None
                )

                for message in reversed(messages):
                    # Forward only normal content posts: text, links, media (image/video/document with caption).
                    has_text = bool((message.raw_text or "").strip())
                    has_media = message.media is not None
                    if has_text or has_media:
                        await self.client.forward_messages(destination_entity, message, source_chat_id)
                        print(f"Message forwarded from {source_chat_id}")


                    # Update the last message ID for this source.
                    last_message_ids[source_chat_id] = max(
                        last_message_ids[source_chat_id],
                        message.id
                    )

            # Add a delay before checking for new messages again
            await asyncio.sleep(5)  # Adjust the delay time as needed


# Function to read credentials from file
def read_credentials():
    try:
        with open("credentials.txt", "r") as file:
            lines = file.readlines()
            api_id = lines[0].strip()
            api_hash = lines[1].strip()
            phone_number = lines[2].strip()
            return api_id, api_hash, phone_number
    except FileNotFoundError:
        print("Credentials file not found.")
        return None, None, None

# Function to write credentials to file
def write_credentials(api_id, api_hash, phone_number):
    with open("credentials.txt", "w") as file:
        file.write(api_id + "\n")
        file.write(api_hash + "\n")
        file.write(phone_number + "\n")

async def main():
    # Attempt to read credentials from file
    api_id, api_hash, phone_number = read_credentials()

    # If credentials not found in file, prompt the user to input them
    if api_id is None or api_hash is None or phone_number is None:
        api_id = input("Enter your API ID: ")
        api_hash = input("Enter your API Hash: ")
        phone_number = input("Enter your phone number: ")
        # Write credentials to file for future use
        write_credentials(api_id, api_hash, phone_number)

    forwarder = TelegramForwarder(api_id, api_hash, phone_number)

    print("Forwarding mode: text + media + links")
    source_chat_input = input("Enter source chat IDs (comma separated): ")
    source_chat_ids = [int(chat_id.strip()) for chat_id in source_chat_input.split(",") if chat_id.strip()]
    destination_target = input("Enter the destination chat ID or @username: ").strip()

    await forwarder.forward_messages_to_channel(source_chat_ids, destination_target)

# Start the event loop and run the main function
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nForwarder stopped by user.")
