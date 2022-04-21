import os
import discord
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('GUILD_NAME')

#intents
intents = discord.Intents()
intents.members = True

client = discord.Client(intents=intents)

#events
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

@client.event
async def on_member_join(member):
    print("yes i saw u joined")
    print(member)
    await member.send(f'{member.name}, welcome to the most sophisticated discord server in the universe.')

client.run(TOKEN)