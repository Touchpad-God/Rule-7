import os
from bs4 import BeautifulSoup
import requests
from mysql import connector
from dotenv import load_dotenv
from dbbuilder import Database

load_dotenv()

headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
        }
mydb = connector.connect(
    host=os.getenv("HOST"),
    user=os.getenv("PROGRAM_SQL_USERNAME"),
    password=os.getenv("PROGRAM_SQL_PASSWORD"),
    database="stats"
)

database = Database()
cursor = mydb.cursor()


def build_matrix(url):
    matrix = []
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            temp = link_stats(row, [])
            if temp:
                matrix.append(temp)
    matrix.append([i for i in matrix[0]])
    return matrix


def link_stats(row, temp):
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


def manual_add(url):
    try:
        assert "individuals" in url
    except AssertionError:
        print("you aren't doing individual stats, you idiot")
    else:
        matrix = build_matrix(url)
        stats, statline = database.refine(matrix)
        statdict = database.to_player(stats, statline)
        database.create_stats(statdict)


def manual_delete(url):
    try:
        assert "individuals" in url
    except AssertionError:
        print("you aren't doing individual stats, you idiot")
    else:
        matrix = build_matrix(url)
        stats, statline = database.refine(matrix)
        statdict = database.to_player(stats, statline)
        get = """SELECT gp, thirty, twenty, fifteen, ten, neg FROM averageStats WHERE name=%s AND team=%s"""
        update = """UPDATE averageStats SET gp=%s, thirty=%s, twenty=%s, fifteen=%s, ten=%s, neg=%s WHERE name=%s AND team=%s"""
        for i in range(len(statdict)):
            if statdict[i].team != "Open":
                statdict[i].team = database.check_team(statdict[i].team).strip()
            params = (statdict[i].name.lower(), statdict[i].team,)
            cursor.execute(get, params)
            res = cursor.fetchone()
            params = (res[0] - statdict[i].stats["gp"], res[1] - statdict[i].stats["thirty"], res[2] - statdict[i].stats["twenty"],
                      res[3] - statdict[i].stats["fifteen"], res[4] - statdict[i].stats["ten"], res[5] - statdict[i].stats["neg"],
                      statdict[i].name, statdict[i].team)
            if params[0] <= 0:
                cursor.execute("DELETE FROM averageStats WHERE name=%s AND team=%s", (statdict[i].name.lower(), statdict[i].team))
            else:
                cursor.execute(update, params)
        mydb.commit()








