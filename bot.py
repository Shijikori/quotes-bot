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

def findChannels(name:str):
    chanlist = []
    for guild in client.guilds:
        for channel in guild.text_channels:
            if channel.name == name:
                chanlist.append(channel)
    return chanlist


#events
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    general_list = findChannels("general")
    
    for channel in general_list:
        await channel.send('I am now online!')

@client.event
async def on_member_join(member):
    await member.send(f'{member.name}, welcome to the most sophisticated discord server in the universe.')

client.run(TOKEN)