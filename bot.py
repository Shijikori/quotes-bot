import os
import discord
import sqlite3
import random
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

#environment vars
TOKEN = os.getenv('DISCORD_TOKEN')
DATABASE = os.getenv('DB_FILE')

#intents
intents = discord.Intents.default()
intents.members = True
intents.messages = True

#globals
client = commands.Bot(command_prefix='!', intents=intents)
quotesChan = None
db_con = None

#function that outputs the contents of the channels table
def getChannelsDB():
    global db_con
    chanlist = []
    with db_con as conn:
        cursor = conn.cursor()
        for row in cursor.execute("SELECT chanid FROM channels"):
            chanlist.append(row)
        conn.commit()
    return chanlist

#extracts a quote from a message containing a quote
def extractQuote(message:str):
    quote = ""
    save = False
    for i in range(0,len(message)):
        if save and not (message[i] == '\"' or message[i] == '\\'):
            quote += message[i]
        if message[i] == '\"' and save:
            break
        if message[i] == '\"':
            save = True
    return quote

#function that creates a table for guild if guild is empty
def createGuildTable(guildid):
    global db_con
    with db_con as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT count(name) FROM sqlite_master WHERE type='table' AND name=\'s{guildid}\'")

        if cursor.fetchone()[0] == 1:
            conn.commit()
            return
        
        cursor.execute(f" CREATE TABLE s{guildid} (userid text, quote text) ")

        conn.commit()

#function that stores the quote on guildid table with userid of quoted user.
def pushQuoteToDB(guildid, userid, quote):
    global db_con
    with db_con as conn:
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO s{guildid} VALUES ('{userid}', '{quote}')")
        conn.commit()

#function that queries the database for user's quotes.
def queryDB(guildid, userid):
    global db_con
    quotes = []
    with db_con as conn:
        cursor = conn.cursor()
        for row in cursor.execute(f"SELECT quote FROM s{guildid} WHERE userid='{userid}'"):
            quotes.append(row[0])
        conn.commit()
        return quotes

#query command
@client.command(name='query', help="Gets a quote from mentionned user.")
async def query(ctx, query:discord.Member):
    quotes = queryDB(ctx.guild.id, query.id)
    if len(quotes) == 0:
        await ctx.send(f"{query} never said anything remarkable :c")
    else:
        await ctx.send(f"{query} once said \"{quotes[random.randrange(0, len(quotes))]}\"")
        if random.randrange(0,38) == 20:
            await ctx.send("Wise words to stand by.")

#command that purges all quotes in the database that comes from specified user.
@client.command(name='purge', help="Purges all of a user's quotes from the database.")
async def purge(ctx, user:discord.Member):
    global db_con
    with db_con as conn:
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM s{ctx.guild.id} WHERE userid='{user.id}'")
        conn.commit()

#command to create a database table for the context guild.
@client.command(name='createdb', help="Creates the database table for the guild.")
async def createDB(ctx):
    createGuildTable(ctx.guild.id)

#command to register the quotes channel.
@client.command(name='register', help="Registers current channel as quotes channel for the current guild.")
async def register(ctx):
    global db_con
    with db_con as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT count(chanid) FROM channels WHERE chanid=\'{ctx.channel.id}\'")
        if cursor.fetchone() == 0:
            cursor.execute(f"INSERT INTO channels VALUES (\'{ctx.channel.id}\')")
        conn.commit()

#command to unregister a quotes channel
@client.command(name='unregister', help="Unregister the current channel from the quotes channels.")
async def unregister(ctx):
    global db_con
    with db_con as conn:
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM channels WHERE chanid=\'{ctx.channel.id}\'")
        conn.commit()

#events
@client.event
async def on_ready():
    global quotesChan
    print(f'{client.user} has connected to Discord!')
    quotesChan = getChannelsDB()
    for guild in client.guilds:
        createGuildTable(guild.id)

@client.event
async def on_message(message):
    global quotesChan
    if message.author == client.user:
        return

    #if channel id is one of the quotes channels, push the quote to DB.
    if f"{message.channel.id}" in quotesChan:
        if len(message.mentions) > 0:
            quote = extractQuote(message.content)
            if len(quote) > 1:
                pushQuoteToDB(message.guild.id, message.mentions[0].id, quote)
            else:
                await message.author.send(f"Your message in #{message.channel} in {message.guild} didn't include a quote.")
        else:
            await message.author.send("Missing mention of quoted user (@) after quote.")
    
    await client.process_commands(message)
    
#running client with keyboard interrupt handling
try:
    db_con = sqlite3.connect(DATABASE)
    cursor = db_con.cursor()
    cursor.execute(f"SELECT count(name) FROM sqlite_master WHERE type='table' AND name='channels'")
    if cursor.fetchone()[0] == 0:
        cursor.execute(f" CREATE TABLE channels (chanid text) ")
    
    db_con.commit()
    
    client.run(TOKEN)
except KeyboardInterrupt:
    db_con.commit()
    db_con.close()
exit(0)

