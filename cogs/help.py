from discord.ui import View, Select
import discord
from discord import app_commands
from discord.ext import commands
from random import randint


class HelpMenu(Select):
    def __init__(self):
        super().__init__(custom_id="help-options",
                         options=[
                             discord.SelectOption(label="Adding stats", value="add"),
                             discord.SelectOption(label="Getting stats", value="get"),
                             discord.SelectOption(label="Managing your profile", value="profile"),
                             discord.SelectOption(label="Creating images", value="img")
                         ],
                         min_values=1,
                         max_values=1)

    async def callback(self, interaction: discord.Interaction):
        option = self.values[0]
        if option == "add":
            embed = discord.Embed(
                title="Adding stats",
                color=randint(0, 16777215),
            )
            embed.add_field(name="/add", value="""This is the basic tool for adding your stats to the database. Your input parameter should link directly to the tournament page, not to any stat reports.

            An example of a correctly formatted link: https://hsquizbowl.org/db/tournaments/8231/

            An example of an incorrectly formatted link: https://hsquizbowl.org/db/tournaments/8231/stats/combined/""")
            embed.add_field(name="/add-all",
                            value="""A lazy way to add to the database multiple tournaments that a person has played. Use a person's name and team as the input parameters.""")
        elif option == "get":
            embed = discord.Embed(
                title="Getting stats",
                color=randint(0, 16777215),
            )
            embed.add_field(name="/get-stats",
                            value="""Fetches stats given the inputted name and, optionally, a team. It's case-insensitive, and you can be as specific or unsepcific with your search as you like. However, due to Discord's limitations, only 25 results will be shown, so if you don't see your desired result, please narrow your search.""",
                            inline=True)
            embed.add_field(name="/tournament-stats", value="""Returns the stats of a person from one specific tournament. However, it's a bit slow, so unless you're sharing it with a half-dozen people, it's probably better to just paste the link. Your input parameter should link directly to the tournament page, not to any stat reports.

            An example of a correctly formatted link: https://hsquizbowl.org/db/tournaments/8231/

            An example of an incorrectly formatted link: https://hsquizbowl.org/db/tournaments/8231/stats/combined/""",
                            inline=True)
            embed.add_field(name="/last-stats",
                            value="""Aggregates your stats from the last X tournaments, where X is the "last" parameter. If you want to exclude some of your most recent tournaments, you can use the optional "first" parameter. Keep in mind that this command is zero-indexed (ex. if your parameters for "first" and "last" are 1 and 3 respectively, you will get the aggregate stats for your second-to-last and third-to-last tournaments.)""",
                            inline=True)
        elif option == "profile":
            embed = discord.Embed(
                title="Managing your profile",
                color=randint(0, 16777215),
            )
            embed.add_field(name="/profile",
                            value="You can use your profile to connect all of your affiliations together.", inline=True)
            embed.add_field(name="/link", value="""Use this command to create your profile. When specifying teams, separate each with a pipe (|) symbol, with no spaces between each pipe.

            Example:
            Churchill|Winston Churchill|Winston Churchill High School

            Team are case-insensitive. In addition, you can find all teams you have played for that are in the database with the command /get-stats.""",
                            inline=True)
            embed.add_field(name="/unlink",
                            value="It's very simple. Just call the command, and the bot will unlink your stats.",
                            inline=True)
        else:
            embed = discord.Embed(
                title="Creating images",
                color=randint(0, 16777215),
            )
            embed.add_field(name="/compare",
                            value="Generates a bar graph comparing the PPG, P/G, and N/G of two players. Parameters are case-insensitive.",
                            inline=True)
            embed.add_field(name="/plot", value="""Generates a scatterplot graphing P/G against PPG for all players in the specified tournament. Your input parameter should link directly to the tournament page, not to any stat reports.

            An example of a correctly formatted link: https://hsquizbowl.org/db/tournaments/8231/

            An example of an incorrectly formatted link: https://hsquizbowl.org/db/tournaments/8231/stats/combined/""",
                            inline=True)
        await interaction.response.edit_message(embed=embed)


class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("/help cog loaded.")

    @commands.command()
    async def help_sync(self, ctx) -> None:
        fmt = await ctx.bot.tree.sync()
        await ctx.send(f"Synced {len(fmt)} commands to the current guild.")
        return

    @app_commands.command(name="help", description="Documentation.", )
    async def help(self, interaction: discord.Interaction):
        menu = HelpMenu()
        view = View()
        view.add_item(menu)

        embed = discord.Embed(title="Rule 7 Wiki", color=randint(0, 16777215))
        embed.add_field(name="\u200B",
                        value="Welcome to the Rule 7 Wiki! Please select an option from the menu below to continue.")

        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Help(bot))
