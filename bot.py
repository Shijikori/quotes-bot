import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('GUILD_NAME')

bot = commands.Bot(command_prefix='!')

#intents
intents = discord.Intents.default()
intents.members = True
intents.messages = True

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

@bot.command(name='imp2met', help='Converts inches to cms.')
async def imp2met(ctx, measure):
    print ("someone used this command")
    metricmeasure = (measure*2.54)
    response = (measure + ' is ' + metricmeasure + 'cm')
    await ctx.send(response)

@bot.command(name='met2imp', help='Converts cm to inches.')
async def met2imp(ctx, measure):
    imperialmeasure = (measure/2.54)
    response = (measure + ' is ' + imperialmeasure + 'inches')
    await ctx.send(response)

client.run(TOKEN)