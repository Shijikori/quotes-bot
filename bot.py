import os
import discord
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('GUILD_NAME')


#intents
intents = discord.Intents.default()
intents.members = True
intents.messages = True

quotesChan = None

client = discord.Client(intents=intents)

def findChannels(name:str):
    chanlist = []
    for guild in client.guilds:
        for channel in guild.text_channels:
            if channel.name == name:
                chanlist.append(channel)
    return chanlist

def extractQuote(message:str):
    quote = ""
    save = False
    for i in range(0,len(message)):
        if save and not message[i] == '\"':
            quote += message[i]
        if message[i] == '\"' and save:
            break
        if message[i] == '\"':
            save = True
    return quote

#events
@client.event
async def on_ready():
    global quotesChan
    print(f'{client.user} has connected to Discord!')
    general_list = findChannels("general")
    quotesChan = findChannels("quotes")
    print(f" {general_list} | {quotesChan}")


    for channel in general_list:
        await channel.send('I am now online!')

@client.event
async def on_member_join(member):
    await member.send(f'{member.name}, welcome to the most sophisticated discord server in the universe.')

@client.event
async def on_message(message):
    global quotesChan
    if message.author == client.user:
        return

    
    if message.channel.id == quotesChan[0].id:
        
        print(f"{message.guild} | {message.mentions[0]} | {extractQuote(message.content)}")

client.run(TOKEN)