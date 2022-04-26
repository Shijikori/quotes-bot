import os
import discord
import sqlite3
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('GUILD_NAME')
DATABASE = os.getenv('DB_FILE')



#intents
intents = discord.Intents.default()
intents.members = True
intents.messages = True

quotesChan = None

#database connection
db_con = sqlite3.connect(DATABASE)

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

#function that creates a table for guild if guild is empty
async def createGuildTable(guildid):
    with db_con as conn:
        cursor = conn.cursor()
        cursor.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name=? ''', guildid)

        if cursor.fetchone()[0] == 1:
            conn.commit()
            return
        
        cursor.execute(''' CREATE TABLE ? (userid text, quote text) ''')

        conn.commit()

#events
@client.event
async def on_ready():
    global quotesChan
    print(f'{client.user} has connected to Discord!')
    general_list = findChannels("general")
    quotesChan = findChannels("quotes")


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
        
        print(f"{message.guild} | {message.mentions[0].id} | {extractQuote(message.content)}")

client.run(TOKEN)