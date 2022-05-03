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
            chanlist.append(row[0])
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

        cursor.execute(f"CREATE TABLE IF NOT EXISTS s{guildid} (userid integer, quote text)")

        conn.commit()

#function that stores the quote on guildid table with userid of quoted user.
def pushQuoteToDB(guildid, userid, quote):
    global db_con
    with db_con as conn:
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO s{guildid} VALUES ({userid}, '{quote}')")
        conn.commit()

#function that queries the database for user's quotes.
def queryDB(guildid, userid):
    global db_con
    quotes = []
    with db_con as conn:
        cursor = conn.cursor()
        for row in cursor.execute(f"SELECT quote FROM s{guildid} WHERE userid={userid}"):
            quotes.append(row[0])
        conn.commit()
        return quotes

#function to drop/delete a guild's table
def deleteGuildTable(guildid):
    global db_con
    with db_con as conn:
        cursor = conn.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS s{guildid}")
        conn.commit()

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
        cursor.execute(f"DELETE FROM s{ctx.guild.id} WHERE userid={user.id}")
        conn.commit()

#command to create a database table for the context guild.
@client.command(name='createdb', help="Creates the database table for the guild.")
@commands.has_permissions(administrator=True)
async def createDB(ctx):
    createGuildTable(ctx.guild.id)

#command to register the quotes channel.
@client.command(name='register', help="Registers current channel as quotes channel for the current guild.")
@commands.has_permissions(manage_channels=True)
async def register(ctx):
    global db_con
    with db_con as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT count(chanid) FROM channels WHERE chanid={ctx.channel.id}")
        if cursor.fetchone()[0] == 0:
            cursor.execute(f"INSERT INTO channels VALUES ({ctx.guild.id},{ctx.channel.id})")
        conn.commit()

#command to unregister a quotes channel
@client.command(name='unregister', help="Unregister the current channel from the quotes channels.")
@commands.has_permissions(manage_channels=True)
async def unregister(ctx):
    global db_con
    with db_con as conn:
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM channels WHERE chanid={ctx.channel.id}")
        conn.commit()

#command to store all quotes from the quotes channel
@client.command(name='readall', help="Reads and stores all quotes from the quotes channels.")
@commands.has_permissions(administrator=True)
async def readall(ctx):
    global quotesChan
    deleteGuildTable(ctx.guild.id)
    createGuildTable(ctx.guild.id)
    if ctx.channel.id in quotesChan:
        async for msg in ctx.channel.history(limit=150):
            if msg.author != client.user:
                quote = extractQuote(msg.content)
                if len(quote) > 1 and len(msg.mentions) > 0:
                    pushQuoteToDB(msg.guild.id, msg.mentions[0].id, quote)
    await ctx.author.send(f"Quotes from the last 150 messages from {ctx.channel.name} in {ctx.guild.name} have been read and stored")

#command to delete a guild's database entries
@client.command(name='deletedb', help="Deletes the database contents of this server. (does not create a blank table for the guild afterwards)")
@commands.has_permissions(administrator=True)
async def deleteDB(ctx):
    global db_con
    with db_con as conn:
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM channels WHERE guildid={ctx.guild.id}")
        conn.commit()
    deleteGuildTable(ctx.guild.id)

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
    if message.channel.id in quotesChan:
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
    
    cursor.execute(f"CREATE TABLE IF NOT EXISTS channels (guildid integer, chanid integer)")

    db_con.commit()
    cursor = None
    client.run(TOKEN)
finally:
    db_con.commit()
    db_con.close()
exit(0)

