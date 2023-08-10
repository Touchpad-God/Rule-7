from mysql import connector
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv
from dbbuilder import Database

db = Database()

load_dotenv()

headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
        }
mydb = connector.pooling.MySQLConnectionPool(pool_name="mypool", **db.dbconfig, pool_size=20)
months = {
    "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
    "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
}


def add_tourney(url):
    db.add_logs.info(f"Adding {url}")
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    name = str(soup.find_all("h2")[1])[4:len(soup.find_all("h2")[1])-6]
    date = str(soup.find_all("h5")[0])[4:len(soup.find_all("h5")[0])-6].split()
    month, day, year = months[date[-3]], int(date[-2][:2]), int(date[-1])

    cnx = mydb.get_connection()
    cursor = cnx.cursor()
    query = "INSERT INTO tournaments (month, day, year, link, name) VALUES (%s, %s, %s, %s, %s)"
    params = (month, day, year, url.replace("https", "http"), name)
    cursor.execute(query, params)
    params = (month, day, year, url.replace("http", "https"), name)
    cursor.execute(query, params)
    cnx.commit()
    cnx.close()
    db.add_logs.info(f"{url} added to database")


def in_db(url):
    cnx = mydb.get_connection()
    cursor = cnx.cursor(buffered=True)
    id = "%" + url.split("/")[5] + "%"
    query = "SELECT * FROM tournaments WHERE link LIKE %s"
    params = (id,)
    cursor.execute(query, params)
    res = cursor.fetchone()
    if res:
        db.add_logs.warning(f"WARNING: {url} already in database!")
        cnx.close()
        return True
    cnx.close()
    return False

