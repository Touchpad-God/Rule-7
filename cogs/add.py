import discord
from discord import app_commands
from discord.ext import commands
import time
from dbbuilder import Database
from helpers import tourneydb
from threading import Thread
import asyncio
import re
from requests import get
from bs4 import BeautifulSoup

database = Database()


class Add(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("/add, /add-all loaded.")

    @commands.command()
    async def add_sync(self, ctx) -> None:
        fmt = await ctx.bot.tree.sync()
        await ctx.send(f"Synced {len(fmt)} commands to the current guild.")
        return

    @app_commands.command(name="add", description="Tournament link ending in its tournament ID (eg. hsquizbowl.org/.../1)")
    async def add(self, interaction: discord.Interaction, link: str):
        database.add_logs.info(f"/add: {interaction.user} ({interaction.user.id}) at {time.ctime(time.time())} ")
        database.add_logs.info(
            f"/add: Now adding {link} at {time.ctime(time.time())} (Interaction ID {interaction.id})")

        def helper(link):
            stats, b = database.build_matrix(link)
            link = link.replace("https", "http")
            tourneydb.add_tourney(link)
            link = link.replace("http", "https")
            tourneydb.add_tourney(link)

            if stats:
                stats = database.to_player(stats, b)
                if stats[0].stats["gp"] < 10:
                    database.add_logs.warning(
                        f"""WARNING: gp is unusually low ({stats[0].stats["gp"]}) (Interaction ID {interaction.id})""")
                database.create_stats(stats)

        if len(link.split("/")) > 7:
            await interaction.response.send_message(
                "Link is not correctly formatted! Use links with the format of https://hsquizbowl.org/db/tournaments/8231/")
        elif tourneydb.in_db(link):
            database.add_logs.info(f"/add: {link} already in database (Interaction ID {interaction.id})")
            await interaction.response.send_message("Stat report already in database.")
        else:
            await interaction.response.send_message("Getting stats...")

            t = Thread(target=helper, args=(link,))
            t.start()

            while t.is_alive():
                await asyncio.sleep(1)

            await interaction.edit_original_response(content="Stats added.")
            database.add_logs.info(f"Done (Interaction ID {interaction.id})")

    @app_commands.command(name="add-all", description="Gets all stats of a player using HDWhite search.")
    async def add_all(self, interaction: discord.Interaction, name: str, team: str):
        database.add_logs.info(
            f"/add-all: {interaction.user} ({interaction.user.id}) at {time.ctime(time.time())} (Interaction ID {interaction.id})")

        def helper():
            for link in links:
                while link[-1] == "/":
                    link = link[:len(link) - 1]
                if tourneydb.in_db(link):
                    database.add_logs.info(
                        f"/add-all: {link} already in database (Interaction ID {interaction.id})")
                else:
                    database.add_logs.info(f"/add-all: Now adding {link} (Interaction ID {interaction.id})")
                    stats, b = database.build_matrix(link)
                    link = link.replace("https", "http")
                    tourneydb.add_tourney(link)
                    link = link.replace("http", "https")
                    tourneydb.add_tourney(link)

                    if stats:
                        stats = database.to_player(stats, b)
                        if stats[0].stats["gp"] < 10:
                            database.add_logs.warning(
                                f"""WARNING: gp is unusually low ({stats[0].stats["gp"]}) (Interaction ID {interaction.id})""")
                        database.create_stats(stats)

        await interaction.response.send_message("Getting stats...")
        pattern = re.compile("https?://hsquizbowl\.org/db/tournaments/\d+")
        response = get(f"""https://hdwhite.org/qb/stats/player/{"+".join(name.split())}/{team.strip()}""")
        soup = BeautifulSoup(response.content, "html.parser")
        links = []

        for link in soup.find_all("a"):
            b = pattern.fullmatch(str(link.get("href")))
            if b:
                links.append(str(link.get("href")))

        t = Thread(target=helper)
        t.start()

        while t.is_alive():
            await asyncio.sleep(1)
        await interaction.edit_original_response(content="Stats added.")
        database.add_logs.info(f"Done (Interaction ID {interaction.id})")


async def setup(bot):
    await bot.add_cog(Add(bot))
