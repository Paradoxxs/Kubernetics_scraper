from elasticsearch import Elasticsearch
import discord
import asyncio
import os 

# Elasticsearch connection settings
ELASTICSEARCH_HOST = 'es1'
ELASTICSEARCH_PORT = 9200
ELASTICSEARCH_INDEX_PATTERN = 'scraped*'  # Use wildcard for index pattern
KEYWORDS = os.getenv('KEYWORDS', '').split(',')  # List of keywords to search for



# Get Elasticsearch credentials from environment variables
username = os.getenv('ELASTIC_USER', 'elastic')
password = os.getenv('ELASTIC_PASSWORD', 'changeme')  # Use a default or handle it differently
ca_certs = os.getenv('ELASTICSEARCH_SSL_CERT', None)
es_host = os.getenv('ELASTICSEARCH_HOSTS', 'elasticsearch')

# Discord bot settings

discord_token = os.getenv('DISCORD_TOKEN', 'changeme')
discord_channel = os.getenv('DISCORD_CHANNEL', 'changeme')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

def send_discord_message(message):
    async def send():
        channel = client.get_channel(discord_channel)
        await channel.send(message)
    
    client.loop.create_task(send())

def search_documents():
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

    # Construct query for multiple keywords
    should_queries = [{'match': {'body': keyword}} for keyword in KEYWORDS]
    query = {"query": {"bool": {"should": should_queries}}}

    result = es.search(index=ELASTICSEARCH_INDEX_PATTERN, body=query)

    hits = result['hits']['hits']
    if hits:
        # Send Discord message
        message = f"A new document containing one of the keywords {KEYWORDS} was found in Elasticsearch."
        send_discord_message(message)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

def main():
    client.run(discord_token)

if __name__ == "__main__":
    main()
