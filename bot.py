import os
import discord
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('GUILD_NAME')

client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    general_list = []
    for guild in client.guilds:
        for channel in guild.text_channels:
            if channel.name == 'general':
                general_list.append(channel)
    for channel in general_list:
        await channel.send('I am now online!')


client.run(TOKEN)