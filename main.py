import asyncio
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import dbbuilder
intents = discord.Intents.default()

load_dotenv()
token = os.getenv("TOKEN")

database = dbbuilder.Database()
bot = commands.Bot(command_prefix="/", intents=intents)


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game("Use /add or /add-all to expand the database!"))
    print(f'We have logged in as {bot.user}')


async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")


async def main():
    await load()
    await bot.start(token)
    await bot.tree.sync()


asyncio.run(main())
