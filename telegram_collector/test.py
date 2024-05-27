from telethon import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch, PeerUser, PeerChannel, PeerChat
from elasticsearch import Elasticsearch
import json

import os

# Telegram API credentials
api_id = 
api_hash = 

client = TelegramClient('anon', api_id, api_hash)

async def main():
    
    dialogs = await client.get_dialogs()

    for dialog in dialogs:
        if dialog.is_channel:
            channel = dialog.entity
            print(f"Processing channel: {channel.title}")

            async for message in client.iter_messages(channel):
                user_info = await client.get_entity(message.from_id)
                
                from_id = None
                to_id = None

                if isinstance(message.from_id, PeerUser):
                    from_id = message.from_id.user_id
                elif isinstance(message.from_id, PeerChannel):
                    from_id = message.from_id.channel_id
                elif isinstance(message.from_id, PeerChat):
                    from_id = message.from_id.chat_id

                if isinstance(message.to_id, PeerUser):
                    to_id = message.to_id.user_id
                elif isinstance(message.to_id, PeerChannel):
                    to_id = message.to_id.channel_id
                elif isinstance(message.to_id, PeerChat):
                    to_id = message.to_id.chat_id

                data = {
                    'id': message.id,
                    'date': message.date.isoformat(),
                    'message': message.message,
                    'username': user_info.username,
                    'from_id': from_id,
                    'to_id': to_id,
                }
                
                print(data)

with client:
    client.loop.run_until_complete(main())
