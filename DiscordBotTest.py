import requests
from bs4 import BeautifulSoup
import discord
import asyncio
import hashlib
import os

# Define the URL of the website you want to monitor
URL = 'https://www.timeanddate.com/worldclock/'

# Path to store the last hash of the website content
HASH_FILE_PATH = 'website_hash.txt'

# Discord bot token and channel ID
DISCORD_BOT_TOKEN = 'Add Here'
DISCORD_CHANNEL_ID = 123456789012345678  # Replace with your actual channel ID

# Function to get the website content and hash it
def get_website_hash(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    content = soup.get_text()
    return hashlib.md5(content.encode()).hexdigest()

# Function to read the last hash from file
def read_last_hash():
    if os.path.exists(HASH_FILE_PATH):
        with open(HASH_FILE_PATH, 'r') as file:
            return file.read().strip()
    return ''

# Function to write the new hash to file
def write_new_hash(new_hash):
    with open(HASH_FILE_PATH, 'w') as file:
        file.write(new_hash)

# Discord client setup
class MyClient(discord.Client):
    async def setup_hook(self):
        self.bg_task = self.loop.create_task(self.check_for_changes())

    async def on_ready(self):
        print(f'Logged in as {self.user}')
        channel = self.get_channel(DISCORD_CHANNEL_ID)
        if channel is None:
            print(f'Error: Channel ID {DISCORD_CHANNEL_ID} not found or bot does not have access.')
        else:
            print(f'Channel {channel.name} found successfully.')

    async def check_for_changes(self):
        await self.wait_until_ready()
        channel = self.get_channel(DISCORD_CHANNEL_ID)
        
        if channel is None:
            print(f'Error: Channel ID {DISCORD_CHANNEL_ID} not found or bot does not have access.')
            return
        
        while True:
            try:
                current_hash = get_website_hash(URL)
                last_hash = read_last_hash()
                
                if current_hash != last_hash:
                    await channel.send(f'The website {URL} has changed.')
                    write_new_hash(current_hash)
                else:
                    print('No change detected.')
                    
            except Exception as e:
                print(f'An error occurred: {e}')
            
            # Wait for 24 hours before checking again
            await asyncio.sleep(5)

# Define intents
intents = discord.Intents.default()
intents.message_content = True  # Add this line to enable the message content intent

# Run the Discord bot
client = MyClient(intents=intents)

async def main():
    async with client:
        await client.start(DISCORD_BOT_TOKEN)

asyncio.run(main())