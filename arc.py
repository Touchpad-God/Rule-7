# # if "<" in str(row):
# #     return []
# for i in row.children:
#     line_soup = BeautifulSoup(str(i), "html.parser")
#     try:
#         tag = line_soup.find(["a", "b", "td"])
#         if not tag or not tag.contents:
#             temp.append("")
#         elif tag.name == "a":
#             content = tag.contents[0]
#             if content in ["Standings", "Individuals", "Scoreboard", "Team Detail", "Individual Detail",
#                            "Round Report"]:
#                 break
#             temp.append(content)
#         elif tag.name == "b":
#             content = str(tag.contents[0])
#             value_map = {"30": "thirty", "20": "twenty", "15": "fifteen", "10": "ten", "-5": "neg"}
#             temp.append(value_map.get(content, content.lower()))
#         else:
#             temp.append(tag.contents[0])
#     except Exception:
#         temp.append("")
# return temp

# client = discord.Client(intents=intents)
# tree = app_commands.CommandTree(client)
#
#
# @client.event
# async def on_ready():
#     await tree.sync()
#     await client.change_presence(activity=discord.Game("Use /add or /add-all to expand the database!"))
#     print(f'We have logged in as {client.user}')
#
#
# @tree.command(name="help", description="Documentation.", )
# async def help(interaction: discord.Interaction):
#     menu = Help()
#     view = View()
#     view.add_item(menu)
#
#     embed = discord.Embed(title="Rule 7 Wiki", color=randint(0, 16777215))
#     embed.add_field(name="\u200B", value="Welcome to the Rule 7 Wiki! Please select an option from the menu below to continue.")
#
#     await interaction.response.send_message(embed=embed, view=view)
#
#
# @tree.command(name="get-stats", description="Gets the stat of a player.", )
# async def get_stats(interaction: discord.Interaction, name: str, team: Optional[str] = ""):
#     database.fetch_logs.info(f"""/get-stats: {interaction.user} ({interaction.user.id}) is accessing stats for {name} ({team})
# at {time.ctime(time.time())} (Interaction ID {interaction.id})""")
#     res, others = database.get_stats(name, team)
#
#     if type(res) is str:
#         await interaction.response.send_message(res)
#     else:
#         menu = PlayerList()
#         for (i, j) in others:
#             menu.add_option(label=f"{i} ({j})", value=f"{i}∫{j}")
#
#         view = View()
#         view.add_item(menu)
#
#         embed = discord.Embed(
#             title=f"Stats of {res[1].title()} ({res[2].title()})",
#             color=randint(0, 16777215),
#         )
#         embed.add_field(name="Games Played", value=str(res[3]), inline=True)
#         embed.add_field(name="PPG", value=str(
#             round((res[4] * 30 + res[5] * 20 + res[6] * 15 + res[7] * 10 - res[8] * 5) / res[3], 2)), inline=True)
#         embed.add_field(name="\u200b", value="\u200b")
#         embed.add_field(name="Superpowers", value=str(res[4] + res[5]), inline=True)
#         embed.add_field(name="Powers", value=str(res[6]), inline=True)
#         embed.add_field(name="\u200b", value="\u200b")
#         embed.add_field(name="Tens", value=str(res[7]), inline=True)
#         embed.add_field(name="Negs", value=str(res[8]), inline=True)
#         embed.add_field(name="\u200b", value="\u200b")
#         embed.set_footer(text="""Because of dropdown limits, only a random sample of 25 players is represented.
# If you do not see your desired result, try narrowing your search or searching again.""")
#         await interaction.response.send_message(embed=embed, view=view)
#         database.fetch_logs.info(f"Done (Interaction ID {interaction.id})")
#
#
# @tree.command(name="last", description="Gets the previous X stats of a player", )
# @app_commands.describe(first="The tournament to start recording stats")
# @app_commands.describe(last="The tournament to end recording stats")
# async def last_stats(interaction: discord.Interaction, name: str, team: str, last: int, first: Optional[int] = 0):
#     database.search_logs.info(f"""/last: {interaction.user} ({interaction.user.id}) accessing {str(last-first)} pages for {name} ({team}) at {time.ctime(time.time())}""")
#
#     await interaction.response.send_message("Getting stats...")
#     pattern = re.compile("https?://hsquizbowl\.org/db/tournaments/\d+")
#     response = get(f"""https://hdwhite.org/qb/stats/player/{"+".join(name.split())}/{team.strip()}""")
#     soup = BeautifulSoup(response.content, "html.parser")
#     links = []
#     res = {}
#     a, b, stats, names = 0, 0, {}, []
#
#     def combine(name):
#         person_name = None
#         for j in range(first, last):
#             database.search_logs.info(f"/last: Fetching stats from {links[j]} (Interaction ID {interaction.id})")
#             a, b = database.build_matrix(links[j])
#             stats = database.to_player(a, b)
#
#             for i in range(len(stats)):
#                 if name in stats[i].name.lower() and team.lower() in stats[i].team.lower():
#                     person = stats[i]
#                     if person_name is None:
#                         person_name = person.name
#                     break
#             if not res:
#                 res[person_name] = person.stats
#                 res[person_name]["team"] = person.team
#                 continue
#             res[person_name]["gp"] += person.stats["gp"]
#             res[person_name]["thirty"] += person.stats["thirty"]
#             res[person_name]["twenty"] += person.stats["twenty"]
#             res[person_name]["fifteen"] += person.stats["fifteen"]
#             res[person_name]["ten"] += person.stats["ten"]
#             res[person_name]["neg"] += person.stats["neg"]
#
#     for j in soup.find_all("a"):
#         b = pattern.fullmatch(str(j.get("href")))
#         if b:
#             links.append(str(j.get("href")))
#
#     if last > len(links):
#         await interaction.edit_original_response(content="Not enough stat reports! Try a lower number.")
#         database.search_logs.info(f"Done (Interaction ID {interaction.id})")
#     else:
#         t = Thread(target=combine, args=(name,))
#         t.start()
#
#         while t.is_alive():
#             await asyncio.sleep(1)
#         name = list(res.keys())[0]
#         embed = discord.Embed(title=f"Stats of {name.title()} ({res[name]['team'].title()})",
#                               color=randint(0, 16777215))
#         embed.add_field(name="Games Played", value=str(res[name]["gp"]), inline=True)
#         embed.add_field(name="PPG", value=str(
#             round((res[name]["thirty"] * 30 + res[name]["twenty"] * 20 + res[name]["fifteen"] * 15 +
#                    res[name]["ten"] * 10 - res[name]["neg"] * 5) / res[name]["gp"], 2)), inline=True)
#         embed.add_field(name="\u200b", value="\u200b")
#         embed.add_field(name="Superpowers", value=str(res[name]["thirty"] + res[name]["twenty"]), inline=True)
#         embed.add_field(name="Powers", value=str(res[name]["fifteen"]), inline=True)
#         embed.add_field(name="\u200b", value="\u200b")
#         embed.add_field(name="Tens", value=str(res[name]["ten"]), inline=True)
#         embed.add_field(name="Negs", value=str(res[name]["neg"]), inline=True)
#         embed.add_field(name="\u200b", value="\u200b")
#         await interaction.edit_original_response(content="", embed=embed)
#         database.search_logs.info(f"Done (Interaction ID {interaction.id})")
#
#
# @tree.command(name="tournament", description="Gets the stats of a player from a specific tournament. ")
# @app_commands.describe(tournament="Tournament name")
# @app_commands.describe(date="Input date in mm/dd/yyyy format.")
# async def tournament_stats(interaction: discord.Interaction, name: str, tournament: str,
#                            date: Optional[str] = "", team: Optional[str] = ""):
#     database.search_logs.info(f"""/tournament: Fetching stats from {tournament} at {time.ctime(time.time())} (Interaction ID {interaction.id})""")
#
#     await interaction.response.send_message("Getting stats...")
#
#     t = helperthreads.TournamentStatsHelper1(tournament, date)
#     t.start()
#
#     while t.is_alive():
#         await asyncio.sleep(1)
#
#     t.join()
#
#     res = t.res
#     tournament_name = t.tournament_name
#
#     if not res:
#         await interaction.edit_original_response(content="Tournament not found.")
#         return
#
#     t = helperthreads.TournamentStatsHelper2(name, res, team)
#     t.start()
#
#     while t.is_alive():
#         await asyncio.sleep(1)
#
#     t.join()
#
#     person = t.person
#
#     if person is None:
#         await interaction.edit_original_response(content="Person not found.")
#         database.search_logs.info(f"Done (Interaction ID {interaction.id})")
#     else:
#         ppg = round((30 * person.stats['thirty'] + 20 * person.stats['twenty'] +
#                     15 * person.stats['fifteen'] + 10 * person.stats['ten']
#                     - 5 * person.stats['neg']) / person.stats['gp'], 2)
#         embed = discord.Embed(
#             title=f"Stats of {person.name.title()} ({person.team.title()}) \nfrom {tournament_name}",
#             color=randint(0, 16777215),
#         )
#         embed.add_field(name="Games Played", value=str(person.stats['gp']), inline=True)
#         embed.add_field(name="PPG", value=str(ppg), inline=True)
#         embed.add_field(name="\u200b", value="\u200b")
#         embed.add_field(name="Superpowers", value=str(person.stats['thirty'] + person.stats['twenty']), inline=True)
#         embed.add_field(name="Powers", value=person.stats['fifteen'], inline=True)
#         embed.add_field(name="\u200b", value="\u200b")
#         embed.add_field(name="Tens", value=str(person.stats['ten']), inline=True)
#         embed.add_field(name="Neg", value=person.stats['neg'], inline=True)
#         embed.add_field(name="\u200b", value="\u200b")
#         await interaction.edit_original_response(content="", embed=embed)
#         database.search_logs.info(f"Done (Interaction ID {interaction.id})")
#
#
# @tree.command(name="profile", description="Gets the stats linked to your Discord account.")
# async def profile(interaction: discord.Interaction):
#     database.fetch_logs.info(f"""/profile: {interaction.user} ({interaction.user.id}) accessing profile at {time.ctime(time.time())} (Interaction ID {interaction.id})""")
#     res = database.get_linked_stats(str(interaction.user.id))
#     if type(res) is str:
#         database.fetch_logs.warning(f"""WARNING: /profile for {interaction.user} ({interaction.user.id}) does not work""")
#         await interaction.response.send_message(res)
#     else:
#         embed = discord.Embed(
#             title=f"{res[1].title()}'s Stats",
#             color=randint(0, 16777215)
#         )
#         embed.add_field(name="Games Played", value=str(res[0][0]), inline=True)
#         res = res[0]
#         embed.add_field(name="PPG", value=str(
#             round((res[1] * 30 + res[2] * 20 + res[3] * 15 + res[4] * 10 - res[5] * 5) / res[0], 2)), inline=True)
#         embed.add_field(name="\u200b", value="\u200b")
#         embed.add_field(name="Superpowers", value=str(res[1] + res[2]), inline=True)
#         embed.add_field(name="Powers", value=str(res[3]), inline=True)
#         embed.add_field(name="\u200b", value="\u200b")
#         embed.add_field(name="Tens", value=str(res[4]), inline=True)
#         embed.add_field(name="Negs", value=str(res[5]), inline=True)
#         embed.add_field(name="\u200b", value="\u200b")
#         await interaction.response.send_message(embed=embed)
#         database.fetch_logs.info(f"/profile: Done (Interaction ID {interaction.id})")
#
#
# @tree.command(name="link", description="Links account to multiple affiliations")
# @app_commands.describe(teams="Separate each team using a pipe symbol (|).")
# async def link(interaction: discord.Interaction, teams: str, name: str):
#     database.fetch_logs.info(f"""{interaction.user} ({interaction.user.id}) linking to {teams} at {time.ctime(time.time())} (Interaction ID {interaction.id})""")
#     await interaction.response.send_message(database.linkaccount(str(interaction.user.id), teams, name))
#     database.fetch_logs.info(f"Done (Interaction ID {interaction.id})")
#
#
# @tree.command(name="unlink", description="Unlinks account.")
# async def unlink(interaction: discord.Interaction):
#     database.fetch_logs.info(f"""{interaction.user} ({interaction.user.id}) unlinked at {time.ctime(time.time())} (Interaction ID {interaction.id})""")
#     await interaction.response.send_message(database.unlink(str(interaction.user.id)))
#     database.fetch_logs.info(f"Done (Interaction ID {interaction.id})")
#
#
# @tree.command(name="add", description="Tournament link ending in its tournament ID (eg. hsquizbowl.org/.../1)")
# async def add(interaction: discord.Interaction, link: str):
#     database.add_logs.info(f"/add: {interaction.user} ({interaction.user.id}) at {time.ctime(time.time())} ")
#     database.add_logs.info(f"/add: Now adding {link} at {time.ctime(time.time())} (Interaction ID {interaction.id})")
#
#     def helper(link):
#         stats, b = database.build_matrix(link)
#         link = link.replace("https", "http")
#         tourneydb.add_tourney(link)
#         link = link.replace("http", "https")
#         tourneydb.add_tourney(link)
#
#         if stats:
#             stats = database.to_player(stats, b)
#             if stats[0].stats["gp"] < 10:
#                 database.add_logs.warning(
#                     f"""WARNING: gp is unusually low ({stats[0].stats["gp"]}) (Interaction ID {interaction.id})""")
#             database.create_stats(stats)
#
#     if len(link.split("/")) > 7:
#         await interaction.response.send_message("Link is not correctly formatted! Use links with the format of https://hsquizbowl.org/db/tournaments/8231/")
#     elif tourneydb.in_db(link):
#         database.add_logs.info(f"/add: {link} already in database (Interaction ID {interaction.id})")
#         await interaction.response.send_message("Stat report already in database.")
#     else:
#         await interaction.response.send_message("Getting stats...")
#
#         t = Thread(target=helper, args=(link,))
#         t.start()
#
#         while t.is_alive():
#             await asyncio.sleep(1)
#
#         await interaction.edit_original_response(content="Stats added.")
#         database.add_logs.info(f"Done (Interaction ID {interaction.id})")
#
#
# @tree.command(name="compare", description="Compares the stats of two players.")
# async def compare(interaction: discord.Interaction, player1: str, team1: str, player2: str, team2: str):
#     database.fetch_logs.info(f"""/compare: {interaction.user} ({interaction.user.id}) comparing
# {player1} ({team1}) to {player2} ({team2}) ({interaction.user.id}) at {time.ctime(time.time())} (Interaction ID {interaction.id})""")
#     image = imgpcs.compare(player1, team1, player2, team2)
#     if image.find("/") == -1:
#         await interaction.response.send_message(image)
#         database.fetch_logs.info(f"Done (Interaction ID {interaction.id})")
#     else:
#         await interaction.response.send_message(
#             attachments=discord.File(imgpcs.compare(player1, team1, player2, team2)))
#         database.fetch_logs.info(f"Done (Interaction ID {interaction.id})")
#
#
# @tree.command(name="add-all", description="Gets all stats of a player using HDWhite search.")
# async def add_all(interaction: discord.Interaction, name: str, team: str):
#     database.add_logs.info(f"/add-all: {interaction.user} ({interaction.user.id}) at {time.ctime(time.time())} (Interaction ID {interaction.id})")
#
#     def helper():
#         for link in links:
#             while link[-1] == "/":
#                 link = link[:len(link) - 1]
#             if tourneydb.in_db(link):
#                 database.add_logs.info(f"/add-all: {link} already in database (Interaction ID {interaction.id})")
#             else:
#                 database.add_logs.info(f"/add-all: Now adding {link} (Interaction ID {interaction.id})")
#                 stats, b = database.build_matrix(link)
#                 link = link.replace("https", "http")
#                 tourneydb.add_tourney(link)
#                 link = link.replace("http", "https")
#                 tourneydb.add_tourney(link)
#
#                 if stats:
#                     stats = database.to_player(stats, b)
#                     if stats[0].stats["gp"] < 10:
#                         database.add_logs.warning(
#                             f"""WARNING: gp is unusually low ({stats[0].stats["gp"]}) (Interaction ID {interaction.id})""")
#                     database.create_stats(stats)
#
#     await interaction.response.send_message("Getting stats...")
#     pattern = re.compile("https?://hsquizbowl\.org/db/tournaments/\d+")
#     response = get(f"""https://hdwhite.org/qb/stats/player/{"+".join(name.split())}/{team.strip()}""")
#     soup = BeautifulSoup(response.content, "html.parser")
#     links = []
#
#     for link in soup.find_all("a"):
#         b = pattern.fullmatch(str(link.get("href")))
#         if b:
#             links.append(str(link.get("href")))
#
#     t = Thread(target=helper)
#     t.start()
#
#     while t.is_alive():
#         await asyncio.sleep(1)
#     await interaction.edit_original_response(content="Stats added.")
#     database.add_logs.info(f"Done (Interaction ID {interaction.id})")
#
#
# @tree.command(name="plot", description="Creates a scatterplot graphing PPG against P/G for every player at a tournament.")
# async def plot(interaction: discord.Interaction, link: str):
#     if len(link.split("/")) > 7:
#         await interaction.response.send_message("Link is not correctly formatted! Use links with the format of https://hsquizbowl.org/db/tournaments/8231/")
#     else:
#         await interaction.response.send_message("Creating graph...")
#         t = helperthreads.PlotHelper(link)
#         t.start()
#
#         while t.is_alive():
#             await asyncio.sleep(1)
#
#         t.join()
#         image = t.image
#
#         await interaction.edit_original_response(content="", attachments=[discord.File(image)])
#
# client.run(os.getenv("TOKEN"))
