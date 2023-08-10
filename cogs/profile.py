import discord
from discord import app_commands
from discord.ext import commands
from random import randint
from typing import Optional
import time
from dbbuilder import Database

database = Database()


class Profile(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("/profile, /link, /unlink loaded.")

    @commands.command()
    async def profile_sync(self, ctx) -> None:
        fmt = await ctx.bot.tree.sync()
        await ctx.send(f"Synced {len(fmt)} commands to the current guild.")
        return

    @app_commands.command(name="profile", description="Gets the stats linked to your Discord account.")
    async def profile(self, interaction: discord.Interaction):
        database.fetch_logs.info(
            f"""/profile: {interaction.user} ({interaction.user.id}) accessing profile at {time.ctime(time.time())} (Interaction ID {interaction.id})""")
        res = database.get_linked_stats(str(interaction.user.id))
        if type(res) is str:
            database.fetch_logs.warning(
                f"""WARNING: /profile for {interaction.user} ({interaction.user.id}) does not work""")
            await interaction.response.send_message(res)
        else:
            embed = discord.Embed(
                title=f"{res[1].title()}'s Stats",
                color=randint(0, 16777215)
            )
            embed.add_field(name="Games Played", value=str(res[0][0]), inline=True)
            res = res[0]
            embed.add_field(name="PPG", value=str(
                round((res[1] * 30 + res[2] * 20 + res[3] * 15 + res[4] * 10 - res[5] * 5) / res[0], 2)), inline=True)
            embed.add_field(name="\u200b", value="\u200b")
            embed.add_field(name="Superpowers", value=str(res[1] + res[2]), inline=True)
            embed.add_field(name="Powers", value=str(res[3]), inline=True)
            embed.add_field(name="\u200b", value="\u200b")
            embed.add_field(name="Tens", value=str(res[4]), inline=True)
            embed.add_field(name="Negs", value=str(res[5]), inline=True)
            embed.add_field(name="\u200b", value="\u200b")
            await interaction.response.send_message(embed=embed)
            database.fetch_logs.info(f"/profile: Done (Interaction ID {interaction.id})")

    @app_commands.command(name="link", description="Links account to multiple affiliations")
    @app_commands.describe(teams="Separate each team using a pipe symbol (|).")
    async def link(self, interaction: discord.Interaction, teams: str, name: str):
        database.fetch_logs.info(
            f"""{interaction.user} ({interaction.user.id}) linking to {teams} at {time.ctime(time.time())} (Interaction ID {interaction.id})""")
        await interaction.response.send_message(database.linkaccount(str(interaction.user.id), teams, name))
        database.fetch_logs.info(f"Done (Interaction ID {interaction.id})")

    @app_commands.command(name="unlink", description="Unlinks account.")
    async def unlink(self, interaction: discord.Interaction):
        database.fetch_logs.info(
            f"""{interaction.user} ({interaction.user.id}) unlinked at {time.ctime(time.time())} (Interaction ID {interaction.id})""")
        await interaction.response.send_message(database.unlink(str(interaction.user.id)))
        database.fetch_logs.info(f"Done (Interaction ID {interaction.id})")


async def setup(bot):
    await bot.add_cog(Profile(bot))
