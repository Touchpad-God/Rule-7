import discord
from discord import app_commands
from discord.ext import commands
from random import randint
from typing import Optional
import time
from dbbuilder import Database
import asyncio
from helpers import helperthreads

database = Database()


class Tournament(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("/tournament loaded.")

    @commands.command()
    async def tournament_sync(self, ctx) -> None:
        fmt = await ctx.bot.tree.sync()
        await ctx.send(f"Synced {len(fmt)} commands to the current guild.")
        return

    @app_commands.command(name="tournament", description="Gets the stats of a player from a specific tournament. ")
    @app_commands.describe(tournament="Tournament name")
    @app_commands.describe(date="Input date in mm/dd/yyyy format.")
    async def tournament_stats(self, interaction: discord.Interaction, name: str, tournament: str,
                               date: Optional[str] = "", team: Optional[str] = ""):
        database.search_logs.info(
            f"""/tournament: Fetching stats from {tournament} at {time.ctime(time.time())} (Interaction ID {interaction.id})""")

        await interaction.response.send_message("Getting stats...")

        t = helperthreads.TournamentStatsHelper1(tournament, date)
        t.start()

        while t.is_alive():
            await asyncio.sleep(1)

        t.join()

        res = t.res
        tournament_name = t.tournament_name

        if not res:
            await interaction.edit_original_response(content="Tournament not found.")
            return

        t = helperthreads.TournamentStatsHelper2(name, res, team)
        t.start()

        while t.is_alive():
            await asyncio.sleep(1)

        t.join()

        person = t.person

        if person is None:
            await interaction.edit_original_response(content="Person not found.")
            database.search_logs.info(f"Done (Interaction ID {interaction.id})")
        else:
            ppg = round((30 * person.stats['thirty'] + 20 * person.stats['twenty'] +
                         15 * person.stats['fifteen'] + 10 * person.stats['ten']
                         - 5 * person.stats['neg']) / person.stats['gp'], 2)
            embed = discord.Embed(
                title=f"Stats of {person.name.title()} ({person.team.title()}) \nfrom {tournament_name}",
                color=randint(0, 16777215),
            )
            embed.add_field(name="Games Played", value=str(person.stats['gp']), inline=True)
            embed.add_field(name="PPG", value=str(ppg), inline=True)
            embed.add_field(name="\u200b", value="\u200b")
            embed.add_field(name="Superpowers", value=str(person.stats['thirty'] + person.stats['twenty']), inline=True)
            embed.add_field(name="Powers", value=person.stats['fifteen'], inline=True)
            embed.add_field(name="\u200b", value="\u200b")
            embed.add_field(name="Tens", value=str(person.stats['ten']), inline=True)
            embed.add_field(name="Neg", value=person.stats['neg'], inline=True)
            embed.add_field(name="\u200b", value="\u200b")
            await interaction.edit_original_response(content="", embed=embed)
            database.search_logs.info(f"Done (Interaction ID {interaction.id})")


async def setup(bot):
    await bot.add_cog(Tournament(bot))
