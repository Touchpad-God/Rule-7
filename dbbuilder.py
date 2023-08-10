from mysql import connector
from bs4 import BeautifulSoup
import requests
import os
from dotenv import load_dotenv
from random import randint
from logs import logs
import time

load_dotenv()


class Player:

    def __init__(self):
        self.name = None
        self.team = None
        self.stats = {"gp": 0.0, "thirty": 0, "twenty": 0, "fifteen": 0, "ten": 0, "neg": 0}


class Database:
    add_logs = logs.setup_logger("add_logs", "logs/add_logs.log")
    fetch_logs = logs.setup_logger("fetch_logs", "logs/fetch_logs.log")
    search_logs = logs.setup_logger("search_logs", "logs/search_logs.log")
    dbconfig = {"host": os.getenv("HOST"), "database": "stats", "user": os.getenv("PROGRAM_SQL_USERNAME"), "password": os.getenv("PROGRAM_SQL_PASSWORD")}
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
    }

    def __init__(self):
        self.template = {"team": "", "gp": 0, "thirty": 0, "twenty": 0, "fifteen": 0, "ten": 0, "neg": 0}

        self.mydb = connector.pooling.MySQLConnectionPool(pool_name="mypool", **Database.dbconfig)
        self.schools = None
        cnx = self.mydb.get_connection()
        cursor = cnx.cursor(buffered=True)
        res = cursor.execute("SELECT team FROM averageStats")
        if res:
            self.schools = {i[0] for i in res}
        if not self.schools:
            self.schools = set()
        self.schools.add("Open")
        cursor.close()

    def get_stats(self, name, team):
        Database.fetch_logs.info(f"""Getting stats for {name} ({team}) at {time.ctime(time.time())}""")
        person = 0

        query = f"""SELECT * FROM averageStats WHERE name LIKE "%{name}%" AND team LIKE "%{team}%" """
        cnx = self.mydb.get_connection()
        cursor = cnx.cursor(buffered=True)
        cursor.execute(query)
        temp = cursor.fetchall()

        if not temp:
            Database.fetch_logs.warning(f"""WARNING: No stats found for {name} ({team}) at {time.ctime(time.time())}""")
            cnx.close()
            return f"Player {name} from {team} not found.", 0
        if len(temp) > 1:
            person = randint(0, len(temp) - 1)
        people = [(temp[person][1], temp[person][2])]
        res = temp[person]
        seen = {person}
        cnx.close()
        if len(temp) > 25:
            for i in range(24):
                while person in seen:
                    person = randint(1, len(temp) - 1)
                seen.add(person)
                people.append((temp[person][1], temp[person][2]))
            if temp is not None:
                return res, people
        elif len(temp) > 1:
            return res, [(temp[i][1], temp[i][2]) for i in range(0, len(temp))]
        else:
            return res, [(temp[0][1], temp[0][2])]

    def linkaccount(self, userid, teams, name):
        cnx = self.mydb.get_connection()
        cursor = cnx.cursor(buffered=True)
        query = """SELECT * FROM accounts WHERE userid=%s"""
        cursor.execute(query, (userid,))
        if not cursor.fetchone():
            query = """INSERT INTO accounts (userid, teams, name) VALUES (%s, %s, %s)"""
            params = (userid, teams, name)
            cursor.execute(query, params)

        else:
            query = """UPDATE accounts SET teams=%s, name=%s WHERE userid=%s"""
            params = (teams, name, userid)
            cursor.execute(query, params)
        teams = teams.replace("|", ", ")
        cnx.commit()
        cnx.close()
        return f"Account {userid} linked to teams {teams.replace('|', ',')}!"

    def unlink(self, userid):
        cnx = self.mydb.get_connection()
        cursor = cnx.cursor(buffered=True)
        query = """UPDATE accounts SET teams=%s, name=%s WHERE userid=%s"""
        params = ("∫", "∫", userid)
        cursor.execute(query, params)
        cnx.commit()
        cnx.close()
        return "Account unlinked!"

    def get_linked_stats(self, userid):
        cnx = self.mydb.get_connection()
        cursor = cnx.cursor(buffered=True)
        query = """SELECT * FROM accounts WHERE userid=%s"""
        cursor.execute(query, (userid,))
        user = cursor.fetchone()
        res = []
        if not user or user[1] == "∫":
            return f"No stats found for user {userid}. Link an account with /link before trying again."
        teams = user[1].split("|")
        query = "SELECT SUM(gp) AS gp FROM averageStats where name=%s AND ("
        for i in range(len(teams)-1):
            query += "team=%s OR "
        query += "team=%s)"
        params = tuple([user[-1]] + [i for i in teams])

        try:
            cursor.execute(query, params)
            res.append(float(cursor.fetchone()[0]))
        except:
            cnx.close()
            return "Something went wrong. Are you sure you put in your affiliations correctly? Try searching yourself using /get_stats to check."
        else:
            query = query.replace("gp", "thirty")
            cursor.execute(query, params)
            res.append(int(cursor.fetchone()[0]))

            query = query.replace("thirty", "twenty")
            cursor.execute(query, params)
            res.append(int(cursor.fetchone()[0]))

            query = query.replace("twenty", "fifteen")
            print(query)
            cursor.execute(query, params)
            res.append(int(cursor.fetchone()[0]))

            query = query.replace("fifteen", "ten")
            cursor.execute(query, params)
            res.append(int(cursor.fetchone()[0]))

            query = query.replace("ten", "neg")
            cursor.execute(query, params)
            res.append(int(cursor.fetchone()[0]))

            cnx.close()
            return [res, user[-1]]

    def build_matrix(self, url):
        from helpers.debug import manual_add
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        links = []

        for report in soup.find_all("a"):
            if "stats" in str(report.get("href")).split("/"):
                links.append(report.get("href"))

        matrix = []
        count = self.report_counter(links)
        if (count[0] == count[1] and count[0] + count[1] == len(links)) or (count[0] == count[1] and count[0] == count[2] and sum(count) == len(links)):
            for link in links:
                report = "https://hsquizbowl.org/db/" + link + "individuals/"
                manual_add(report)
            return False, False
        else:
            for link in links:
                response = requests.get("https://hsquizbowl.org/db/" + link + "individuals/", headers=self.headers)
                soup = BeautifulSoup(response.content, 'html.parser')
                for table in soup.find_all("table"):
                    for row in table.find_all("tr"):
                        temp = self.link_stats(row, [])
                        if temp:
                            matrix.append(temp)
            matrix.append([i for i in matrix[0]])
            return self.refine(matrix)

    def link_stats(self, row, temp):
        for i in row.children:
            line_soup = BeautifulSoup(str(i), "html.parser")
            if line_soup.find("a"):
                if not line_soup.find("a").contents:
                    temp.append("")
                    continue
                if line_soup.find("a").contents[0] in ["Standings", "Individuals", "Scoreboard",
                                                       "Team Detail", "Individual Detail", "Round Report"]:
                    break
                temp.append(line_soup.find("a").contents[0])
            elif line_soup.find("b"):
                if not line_soup.find("b").contents:
                    temp.append("")
                    continue
                if str(line_soup.find("b").contents[0]) == "30":
                    temp.append("thirty")
                elif str(line_soup.find("b").contents[0]) == "20":
                    temp.append("twenty")
                elif str(line_soup.find("b").contents[0]) == "15":
                    temp.append("fifteen")
                elif str(line_soup.find("b").contents[0]) == "10":
                    temp.append("ten")
                elif str(line_soup.find("b").contents[0]) == "-5":
                    temp.append("neg")
                else:
                    temp.append(str(line_soup.find("b").contents[0]).lower())
            elif line_soup.find("td"):
                if not line_soup.find("td").contents:
                    temp.append("")
                    continue
                temp.append(line_soup.find("td").contents[0])
        return temp

    def to_dict(self, matrix, statline):
        """DEPRECATED because it doesn't account for people with the same name in stat reports"""
        new_stats = {}
        for stat in matrix:
            if None in stat:
                continue
            temp = stat[0].split()
            key = " ".join(temp[:2]).lower()
            if key not in new_stats:
                new_stats[key] = {j: self.template[j] for j in self.template.keys()}
                for j in range(len(statline)):
                    new_stats[key][statline[j]] = stat[j + 1]
            else:
                if new_stats[key]["gp"] <= stat[statline.index("gp") + 1]:
                    for i in range(1, len(statline)):
                        new_stats[key][statline[i]] = stat[statline.index(statline[i]) + 1]
        if self.is_open(new_stats):
            for i in new_stats.keys():
                new_stats[i]["team"] = "Open"
        return new_stats

    def to_player(self, matrix, statline):
        names = set()
        new_stats = []
        for stat in matrix:
            if None in stat:
                continue
            player = Player()
            player.name = stat[0].lower()
            player.team = stat[1].lower()
            if player.name not in names:
                names.add(player.name)
                for i in range(len(statline)):
                    player.stats[statline[i]] = stat[i+1]
                new_stats.append(player)
            else:
                for i in range(len(new_stats)):
                    if new_stats[i].name == player.name:
                        for j in range(1, len(statline)):
                            new_stats[i].stats[statline[j]] = stat[statline.index(statline[j]) + 1]

        if self.is_open(new_stats):
            for i in new_stats:
                i.stats["team"] = "Open"
        return new_stats

    def create_stats_old(self, new_stats):
        """DEPRECATED because it doesn't account for people with the same name in stat reports"""
        cnx = self.mydb.get_connection()
        cursor = cnx.cursor(buffered=True)

        for i in new_stats.keys():
            if new_stats[i]["team"] != "Open":
                new_stats[i]["team"] = self.check_team(new_stats[i]["team"]).strip()
            query = """SELECT gp, thirty, twenty, fifteen, ten, neg FROM averageStats WHERE name=%s AND team=%s"""
            params = (i, new_stats[i]["team"])
            cursor.execute(query, params)
            temp = cursor.fetchone()
            if temp is not None:
                new_values = [i for i in temp]
                new_values[0] += new_stats[i]["gp"]
                new_values[1] += new_stats[i]["thirty"]
                new_values[2] += new_stats[i]["twenty"]
                new_values[3] += new_stats[i]["fifteen"]
                new_values[4] += new_stats[i]["ten"]
                new_values[5] += new_stats[i]["neg"]
                query = """UPDATE averageStats SET gp=%s, thirty=%s, twenty=%s, fifteen=%s, ten=%s, neg=%s 
                WHERE name=%s AND team=%s"""
                params = (new_values[0], new_values[1], new_values[2], new_values[3],
                          new_values[4], new_values[5], i, new_stats[i]["team"])
                cursor.execute(query, params)
                continue
            query = """INSERT INTO averageStats (name, team, gp, thirty, twenty, fifteen, ten, neg) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            params = (i, new_stats[i]["team"], new_stats[i]["gp"], new_stats[i]["thirty"], new_stats[i]["twenty"],
                      new_stats[i]["fifteen"], new_stats[i]["ten"], new_stats[i]["neg"])
            cursor.execute(query, params)
        cnx.commit()
        cnx.close()

    def create_stats(self, stats):
        cnx = self.mydb.get_connection()
        cursor = cnx.cursor(buffered=True)

        for player in stats:
            if player.team is None:
                continue
            if player.team != "Open":
                player.team = self.check_team(player.team).strip()
            query = """SELECT gp, thirty, twenty, fifteen, ten, neg FROM averageStats WHERE name=%s AND team=%s"""
            params = (player.name, player.team)
            cursor.execute(query, params)
            temp = cursor.fetchone()
            if temp is not None:
                new_values = [i for i in temp]
                new_values[0] += player.stats["gp"]
                new_values[1] += player.stats["thirty"]
                new_values[2] += player.stats["twenty"]
                new_values[3] += player.stats["fifteen"]
                new_values[4] += player.stats["ten"]
                new_values[5] += player.stats["neg"]
                query = """UPDATE averageStats SET gp=%s, thirty=%s, twenty=%s, fifteen=%s, ten=%s, neg=%s 
                WHERE name=%s AND team=%s"""
                params = (new_values[0], new_values[1], new_values[2], new_values[3],
                          new_values[4], new_values[5], player.name, player.team)
                cursor.execute(query, params)
                continue
            query = """INSERT INTO averageStats (name, team, gp, thirty, twenty, fifteen, ten, neg) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            params = (player.name, player.team, player.stats["gp"], player.stats["thirty"], player.stats["twenty"],
                      player.stats["fifteen"], player.stats["ten"], player.stats["neg"])
            cursor.execute(query, params)
        cnx.commit()
        cnx.close()

    def refine(self, matrix):
        i = 0
        matrix_final = []
        statline = None
        while i < len(matrix):
            if matrix[i][0] == "rank":
                # I should probably just pass in the array with all the types of stats directly instead of using index
                statline = self.find_important(i, matrix)
            if i == 0:
                for j in range(len(matrix)):
                    matrix_final.append([None] * (len(statline) + 1))
                i += 1
                continue
            if i != 1:
                i += 1
            counter = 0
            if matrix_final[1][0] is None:
                for person in matrix:
                    if person[0] == "rank":
                        counter += 1
                        continue
                    matrix_final[counter][0] = person[1]
                    counter += 1
            j = 1
            for stat in statline.keys():
                counter = i
                while counter < len(matrix) and matrix[counter][0] != "rank":
                    if stat in {"thirty", "twenty", "fifteen", "ten", "neg"}:
                        matrix_final[counter][j] = int(matrix[counter][statline[stat]])
                    elif stat == "gp":
                        matrix_final[counter][j] = float(matrix[counter][statline[stat]])
                    else:
                        if matrix[counter][statline[stat]].find("(") > -1:
                            matrix[counter][statline[stat]] = matrix[counter][statline[stat]][
                                                              :matrix[counter][statline[stat]].find("(")]
                        matrix_final[counter][j] = matrix[counter][statline[stat]]
                    counter += 1
                j += 1
            i = counter

        return matrix_final, list(statline.keys())

    def find_important(self, ind, matrix):
        important = {}
        for k in [str(i) for i in self.template.keys()]:
            if k in matrix[ind]:
                important[k] = matrix[ind].index(k)
        return important

    def check_team(self, team):
        if team.find("(") > -1:
            team = team[:team.find("(")]
        if team[-2] == ' ':
            team = team[:len(team) - 2]
        if team in self.schools:
            return team
        for i in self.schools:
            if i in team or team in i:
                return i
        self.schools.add(team)
        return team

    def is_strange(self, team):
        if len(team.split()) > 3:
            return True
        team = team.replace(" ", "")
        if team.upper() == team and len(team) > 5:
            return True
        for i in team:
            if not (i in {" ", ".", "'"} or i.isalpha()):
                return True
        return False

    def is_open(self, data):
        strangeness, count, teams = 0, 0, set()
        for player in data:
            if player.team not in teams:
                count += 1
                teams.add(player.team)
                if self.is_strange(player.team):
                    strangeness += 1
        if (strangeness ** 2) / (count ** 2) >= 0.1:
            return True
        return False

    def report_counter(self, links):
        prelims, playoffs, finals = 0, 0, 0
        for i in links:
            if "prelims" in i:
                prelims += 1
            elif "playoffs" in i:
                playoffs += 1
            elif "finals" in i:
                finals += 1
        return tuple([prelims, playoffs, finals])


