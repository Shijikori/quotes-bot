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

#finds all channels of the name name
def findChannels(name:str):
    chanlist = []
    for guild in client.guilds:
        for channel in guild.text_channels:
            if channel.name == name:
                chanlist.append(channel)
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

#imperial to metric conversion command
@client.command(name='imp2met', help='Converts inches to cms.')
async def imp2met(ctx, measure):
    try:
        measure = float(measure)
    except ValueError:
        await ctx.send("Argument is not a number!")
        return
    metricmeasure = (measure*2.54)
    response = f"{measure} inches is about {metricmeasure:.3f} centimeters"
    await ctx.send(response)

#metric to imperial conversion command
@client.command(name='met2imp', help='Converts cm to inches.')
async def met2imp(ctx, measure):
    try:
        measure = float(measure)
    except ValueError:
        await ctx.send("Argument is not a number!")
        return
    imperialmeasure = (measure/2.54)
    response = f"{measure} centimeters is about {imperialmeasure:.3f} inches"
    await ctx.send(response)

#query command
@client.command(name='query', help="Gets quote from mentionned user.")
async def query(ctx, query:discord.Member):
    quotes = queryDB(ctx.guild.id, query.id)
    if len(quotes) == 0:
        await ctx.send(f"{query} never said anything remarkable :c")
    else:
        await ctx.send(f"{query} once said \"{quotes[random.randrange(0, len(quotes))]}\"")
        if random.randrange(0,38) == 20:
            await ctx.send("Wise words to stand by.")

#events
@client.event
async def on_ready():
    global quotesChan
    print(f'{client.user} has connected to Discord!')
    general_list = findChannels("general")
    quotesChan = findChannels("quotes")
    for guild in client.guilds:
        createGuildTable(guild.id)

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

    #if channel id is one of the quotes channels, push the quote to DB.
    if message.channel.id == quotesChan[0].id:
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
    client.run(TOKEN)
except KeyboardInterrupt:
    db_con.commit()
    db_con.close()
exit(0)

