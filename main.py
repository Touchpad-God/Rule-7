import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("TOKEN")


class Rule7(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="/",
            intents=discord.Intents.default()
        )
    
    async def setup_hook(self) -> None:
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await bot.load_extension(f"cogs.{filename[:-3]}")
        await bot.tree.sync()
    
    async def on_ready(self):
        await bot.change_presence(activity=discord.Game("Use /add or /add-all to expand the database!"))
        print(f'We have logged in as {bot.user}')

bot = Rule7()
bot.run(token)
