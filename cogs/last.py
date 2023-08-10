import discord
from discord import app_commands
from discord.ext import commands
from random import randint
from dbbuilder import Database
import re
from requests import get
from bs4 import BeautifulSoup
from threading import Thread
import asyncio
import time
from typing import Optional

database = Database()


class Last(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("/last loaded.")

    @commands.command()
    async def last_sync(self, ctx) -> None:
        fmt = await ctx.bot.tree.sync()
        await ctx.send(f"Synced {len(fmt)} commands to the current guild.")
        return

    @app_commands.command(name="last", description="Gets the previous X stats of a player", )
    @app_commands.describe(first="The tournament to start recording stats")
    @app_commands.describe(last="The tournament to end recording stats")
    async def last_stats(self, interaction: discord.Interaction, name: str, team: str, last: int, first: Optional[int] = 0):
        database.search_logs.info(
            f"""/last: {interaction.user} ({interaction.user.id}) accessing {str(last - first)} pages for {name} ({team}) at {time.ctime(time.time())}""")

        await interaction.response.send_message("Getting stats...")
        pattern = re.compile("https?://hsquizbowl\.org/db/tournaments/\d+")
        response = get(f"""https://hdwhite.org/qb/stats/player/{"+".join(name.split())}/{team.strip()}""")
        soup = BeautifulSoup(response.content, "html.parser")
        links = []
        res = {}
        a, b, stats, names = 0, 0, {}, []

        def combine(name):
            person_name = None
            for j in range(first, last):
                database.search_logs.info(f"/last: Fetching stats from {links[j]} (Interaction ID {interaction.id})")
                a, b = database.build_matrix(links[j])
                stats = database.to_player(a, b)

                for i in range(len(stats)):
                    if name in stats[i].name.lower() and team.lower() in stats[i].team.lower():
                        person = stats[i]
                        if person_name is None:
                            person_name = person.name
                        break
                if not res:
                    res[person_name] = person.stats
                    res[person_name]["team"] = person.team
                    continue
                res[person_name]["gp"] += person.stats["gp"]
                res[person_name]["thirty"] += person.stats["thirty"]
                res[person_name]["twenty"] += person.stats["twenty"]
                res[person_name]["fifteen"] += person.stats["fifteen"]
                res[person_name]["ten"] += person.stats["ten"]
                res[person_name]["neg"] += person.stats["neg"]

        for j in soup.find_all("a"):
            b = pattern.fullmatch(str(j.get("href")))
            if b:
                links.append(str(j.get("href")))

        if last > len(links):
            await interaction.edit_original_response(content="Not enough stat reports! Try a lower number.")
            database.search_logs.info(f"Done (Interaction ID {interaction.id})")
        else:
            t = Thread(target=combine, args=(name,))
            t.start()

            while t.is_alive():
                await asyncio.sleep(1)
            name = list(res.keys())[0]
            embed = discord.Embed(title=f"Stats of {name.title()} ({res[name]['team'].title()})",
                                  color=randint(0, 16777215))
            embed.add_field(name="Games Played", value=str(res[name]["gp"]), inline=True)
            embed.add_field(name="PPG", value=str(
                round((res[name]["thirty"] * 30 + res[name]["twenty"] * 20 + res[name]["fifteen"] * 15 +
                       res[name]["ten"] * 10 - res[name]["neg"] * 5) / res[name]["gp"], 2)), inline=True)
            embed.add_field(name="\u200b", value="\u200b")
            embed.add_field(name="Superpowers", value=str(res[name]["thirty"] + res[name]["twenty"]), inline=True)
            embed.add_field(name="Powers", value=str(res[name]["fifteen"]), inline=True)
            embed.add_field(name="\u200b", value="\u200b")
            embed.add_field(name="Tens", value=str(res[name]["ten"]), inline=True)
            embed.add_field(name="Negs", value=str(res[name]["neg"]), inline=True)
            embed.add_field(name="\u200b", value="\u200b")
            await interaction.edit_original_response(content="", embed=embed)
            database.search_logs.info(f"Done (Interaction ID {interaction.id})")


async def setup(bot):
    await bot.add_cog(Last(bot))
