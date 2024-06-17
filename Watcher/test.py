import discord
import asyncio

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


async def my_background_task():
    await client.wait_until_ready()
    counter = 0
    channel = client.get_channel(1242857942542319676) # replace with channel_id
    while not client.is_closed():
        counter += 1
        await channel.send("this is a test")
        await asyncio.sleep(60) # task runs every 60 seconds

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

#client.loop.create_task(my_background_task())



