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
    print("message received!")
    if message.author == client.user:
        print("author is me!")
        return
    print("author is not me!")
    save = False
    quote = ""
    if message.channel.id == quotesChan[0].id:
        print("message is a quote!")
        for i in range(0,len(message.content)):
            if save and not message.content[i] == '\"':
                quote += message.content[i]
            if message.content[i] == '\"' and save:
                break
            if message.content[i] == '\"':
                save = True
          
        print(f"{message.guild} | {message.mentions[0]} | {quote}")

client.run(TOKEN)