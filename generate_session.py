from telethon.sync import TelegramClient
from telethon.sessions import StringSession

api_id = 26531485  # TODO: Replace with your API ID
api_hash = "7ae9b39f4acdc709219b8ef1f073d067"  # TODO: Replace with your API Hash

with TelegramClient(StringSession(), api_id, api_hash) as client:
    print("YOUR_STRING_SESSION:")
    print(client.session.save())
