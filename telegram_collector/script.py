from telethon import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch, PeerUser, PeerChannel, PeerChat
import telethon
from elasticsearch import Elasticsearch
import os
import re
import time

# Telegram API credentials
api_id = os.getenv('TELEGRAM_ID', 'telegram')
api_hash = os.getenv('TELEGRAM_HASH', 'telegram')
client = TelegramClient('anon', api_id, api_hash)

# Elasticsearch credentials
# Get Elasticsearch credentials from environment variables
username = os.getenv('ELASTIC_USER', 'elastic')
password = os.getenv('ELASTIC_PASSWORD', 'changeme')  # Use a default or handle it differently
ca_certs = os.getenv('ELASTICSEARCH_SSL_CERT', None)
es_host = os.getenv('ELASTICSEARCH_HOSTS', 'elasticsearch')




try:
    es = Elasticsearch(
        [{'scheme': 'https', 'host': 'es01', 'port': 9200}],
        basic_auth=(username, password),
        verify_certs=True,
        ca_certs=ca_certs
    )
    if not es.ping():
        raise ValueError("Connection failed")
except Exception as e:
    print("Error connecting to Elasticsearch:", e)
    exit()


def sanitize_index_name(name):
    # Remove or replace invalid characters for Elasticsearch index names
    return re.sub(r'[\/,|>?*<" \\]', '_', name).lower()

async def main():
    await client.start()
    
    dialogs = await client.get_dialogs()
    for dialog in dialogs:
        if dialog.is_channel:
            channel = dialog.entity
            
            

            async for message in client.iter_messages(channel):
                if message.from_id is not None:
                    while True:
                        try:
                            user_info = await client.get_entity(message.from_id)
                            break
                        except telethon.errors.FloodWaitError as e:
                            print(f"Flood wait error: Waiting for {e.seconds} seconds")
                            time.sleep(e.seconds)

                    
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
                
                    index_name = sanitize_index_name(f"telegram-{channel.title}-{channel.id}")
                    es.index(index=index_name, body=data)
                else:
                    print("Message has no from_id")

    await client.disconnect()

with client:
    client.loop.run_until_complete(main())
