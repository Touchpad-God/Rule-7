import discord
from discord import app_commands
from discord.ext import commands
import time
import asyncio
from requests import get
from bs4 import BeautifulSoup
from dbbuilder import Database
from helpers import helperthreads, imgpcs

database = Database()


class Images(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("/compare, /plot loaded.")

    @commands.command()
    async def images_sync(self, ctx) -> None:
        fmt = await ctx.bot.tree.sync()
        await ctx.send(f"Synced {len(fmt)} commands to the current guild.")
        return

    @app_commands.command(name="compare", description="Compares the stats of two players.")
    async def compare(self, interaction: discord.Interaction, player1: str, team1: str, player2: str, team2: str):
        database.fetch_logs.info(f"""/compare: {interaction.user} ({interaction.user.id}) comparing
    {player1} ({team1}) to {player2} ({team2}) ({interaction.user.id}) at {time.ctime(time.time())} (Interaction ID {interaction.id})""")
        image = imgpcs.compare(player1, team1, player2, team2)
        if image.find("/") == -1:
            await interaction.response.send_message(image)
            database.fetch_logs.info(f"Done (Interaction ID {interaction.id})")
        else:
            await interaction.response.send_message(
                attachments=discord.File(imgpcs.compare(player1, team1, player2, team2)))
            database.fetch_logs.info(f"Done (Interaction ID {interaction.id})")

    @app_commands.command(name="plot", description="Creates a scatterplot graphing PPG against P/G for every player at a tournament.")
    async def plot(self, interaction: discord.Interaction, link: str):
        if len(link.split("/")) > 7:
            await interaction.response.send_message(
                "Link is not correctly formatted! Use links with the format of https://hsquizbowl.org/db/tournaments/8231/")
        else:
            await interaction.response.send_message("Creating graph...")
            t = helperthreads.PlotHelper(link)
            t.start()

            while t.is_alive():
                await asyncio.sleep(1)

            t.join()
            image = t.image

            await interaction.edit_original_response(content="", attachments=[discord.File(image)])


async def setup(bot):
    await bot.add_cog(Images(bot))