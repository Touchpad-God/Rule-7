import discord
from discord import app_commands
from discord.ext import commands
from dbbuilder import Database
import time
from typing import Optional
from random import randint

database = Database()


class PlayerList(discord.ui.Select):
    def __init__(self):
        options = []
        super().__init__(custom_id="players", placeholder="Select a player...", min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        option = self.values[0].split("∫")
        res, x = database.get_stats(option[0], option[1])
        embed = discord.Embed(
            title=f"Stats of {res[1].title()} ({res[2].title()})",
            color=randint(0, 16777215),
        )
        embed.add_field(name="Games Played", value=str(res[3]), inline=True)
        embed.add_field(name="PPG", value=str(
            round((res[4] * 30 + res[5] * 20 + res[6] * 15 + res[7] * 10 - res[8] * 5) / res[3], 2)), inline=True)
        embed.add_field(name="\u200b", value="\u200b")
        embed.add_field(name="Superpowers", value=str(res[4] + res[5]), inline=True)
        embed.add_field(name="Powers", value=str(res[6]), inline=True)
        embed.add_field(name="\u200b", value="\u200b")
        embed.add_field(name="Tens", value=str(res[7]), inline=True)
        embed.add_field(name="Negs", value=str(res[8]), inline=True)
        embed.add_field(name="\u200b", value="\u200b")
        embed.set_footer(text="""Because of dropdown limits, only a random sample of 25 players is represented. 
If you do not see your desired result, try narrowing your search or searching again.""")
        await interaction.response.edit_message(embed=embed)


class GetStats(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("/get-stats loaded.")

    @commands.command()
    async def getstats_sync(self, ctx) -> None:
        fmt = await ctx.bot.tree.sync()
        await ctx.send(f"Synced {len(fmt)} commands to the current guild.")
        return

    @app_commands.command(name="get-stats", description="Gets the stat of a player.", )
    async def get_stats(self, interaction: discord.Interaction, name: str, team: Optional[str] = ""):
        database.fetch_logs.info(
            f"""/get-stats: {interaction.user} ({interaction.user.id}) is accessing stats for {name} ({team})
    at {time.ctime(time.time())} (Interaction ID {interaction.id})""")
        res, others = database.get_stats(name, team)

        if type(res) is str:
            await interaction.response.send_message(res)
        else:
            menu = PlayerList()
            for (i, j) in others:
                menu.add_option(label=f"{i} ({j})", value=f"{i}∫{j}")

            view = discord.ui.View()
            view.add_item(menu)

            embed = discord.Embed(
                title=f"Stats of {res[1].title()} ({res[2].title()})",
                color=randint(0, 16777215),
            )
            embed.add_field(name="Games Played", value=str(res[3]), inline=True)
            embed.add_field(name="PPG", value=str(
                round((res[4] * 30 + res[5] * 20 + res[6] * 15 + res[7] * 10 - res[8] * 5) / res[3], 2)), inline=True)
            embed.add_field(name="\u200b", value="\u200b")
            embed.add_field(name="Superpowers", value=str(res[4] + res[5]), inline=True)
            embed.add_field(name="Powers", value=str(res[6]), inline=True)
            embed.add_field(name="\u200b", value="\u200b")
            embed.add_field(name="Tens", value=str(res[7]), inline=True)
            embed.add_field(name="Negs", value=str(res[8]), inline=True)
            embed.add_field(name="\u200b", value="\u200b")
            embed.set_footer(text="""Because of dropdown limits, only a random sample of 25 players is represented.
    If you do not see your desired result, try narrowing your search or searching again.""")
            await interaction.response.send_message(embed=embed, view=view)
            database.fetch_logs.info(f"Done (Interaction ID {interaction.id})")


async def setup(bot):
    await bot.add_cog(GetStats(bot))
