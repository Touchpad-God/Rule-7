import time
import matplotlib
import matplotlib.pyplot as plt
import os

from dotenv import load_dotenv
from mysql import connector
import numpy as np
from dbbuilder import Database


load_dotenv()
dbconfig = {"host": "78.108.218.47", "database": "s103030_stats", "user": os.getenv("PROGRAM_SQL_USERNAME"), 
            "password": os.getenv("PROGRAM_SQL_PASSWORD")}
mydb = connector.pooling.MySQLConnectionPool(pool_name="mypool", **dbconfig, pool_size=20)
database = Database()
matplotlib.use('agg')


def clean():
    start = int(time.time())
    for file in os.listdir("helpers/graphs"):
        x = file.split(".")
        if start-int(x[0]) > 300000:
            os.remove(f"helpers/graphs/{file}")


def compare(p1, school1, p2, school2):
    clean()

    cnx = mydb.get_connection()
    cursor = cnx.cursor()

    start = int(time.time())
    query = """SELECT gp, thirty, twenty, fifteen, ten, neg FROM averageStats WHERE name=%s AND team=%s"""

    params1 = (p1, school1)
    cursor.execute(query, params1)
    person1 = cursor.fetchone()
    if not person1:
        return f"{p1} from {school1} not found! Add some stats before trying again."

    params2 = (p2, school2)
    cursor.execute(query, params2)
    person2 = cursor.fetchone()
    if not person2:
        return f"{p2} from {school2} not found! Add some stats before trying again."

    labels = ["PPG", "P/G", "G/N"]
    kpstats = [round((person1[1]*30 + person1[2]*20 + person1[3]*15 + person1[4]*10 - person1[5]*5) / person1[0], 2),
               round((person1[1] + person1[2] + person1[3]) / person1[0], 2), 0]
    agstats = [round((person2[1]*30 + person2[2]*20 + person2[3]*15 + person2[4]*10 - person2[5]*5) / person2[0], 2),
               round((person2[1] + person2[2] + person2[3]) / person2[0], 2), 0]
    if person1[5] > 0:
        kpstats[2] = round((person1[1] + person1[2] + person1[3] + person1[4]) / person1[5], 2)
    if person2[5] > 0:
        agstats[2] = round((person2[1] + person2[2] + person2[3] + person2[4]) / person2[5], 2)

    fig, ax = plt.subplots()
    x = np.arange(len(labels))
    width = 0.35
    rects1 = ax.bar(x - width/2, agstats, width, label=params2[0].title())
    rects2 = ax.bar(x + width/2, kpstats, width, label=params1[0].title())

    ax.set_xticks(x, labels)
    plt.title(f"Stats comparison between {params2[0].title()} and {params1[0].title()}")
    ax.legend()

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)
    plt.savefig(f"helpers/graphs/{start}.jpeg", dpi=300)
    cnx.close()
    plt.close("all")
    return f"helpers/graphs/{start}.jpeg"


def plot(link):
    clean()

    start = int(time.time())
    a, b = database.build_matrix(link)
    players = database.to_player(a, b)

    x = []
    y = []

    for player in players:
        x.append((30 * player.stats["thirty"] + 20 * player.stats["twenty"] + 15 * player.stats["fifteen"] +
                 10 * player.stats["ten"] - 5 * player.stats["neg"])/player.stats["gp"])
        y.append((player.stats["thirty"] + player.stats["twenty"] + player.stats["fifteen"])/player.stats["gp"])
        plt.scatter([(30 * player.stats["thirty"] + 20 * player.stats["twenty"] + 15 * player.stats["fifteen"] +
                    10 * player.stats["ten"] - 5 * player.stats["neg"])/player.stats["gp"]],
                    [(player.stats["thirty"] + player.stats["twenty"] + player.stats["fifteen"])/player.stats["gp"]])

    x = np.array(x)
    y = np.array(y)

    a, b = np.polyfit(x, y, 1)

    plt.plot(x, a * x + b, c="k")
    plt.xlabel("PPG")
    plt.ylabel("P/G")
    plt.title(link)
    plt.savefig(f"helpers/graphs/{start}.jpeg", dpi=300)
    plt.close("all")
    return f"helpers/graphs/{start}.jpeg"
