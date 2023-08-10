from threading import Thread
from dbbuilder import Database
from bs4 import BeautifulSoup
from requests import get
import helpers.imgpcs

database = Database()


class TournamentStatsHelper1(Thread):

    def __init__(self, tournament, date):
        Thread.__init__(self)

        self.tournament = tournament
        self.date = date
        self.res = None
        self.tournament_name = ""

    def run(self):
        mdy = self.date.split("/")
        if self.date:
            response = get(
                f"https://hsquizbowl.org/db/tournaments/search/?name={self.tournament}&dates=on&startdate={mdy[0]}%2F{mdy[1]}%2F{mdy[2]}"
                , headers=database.headers)
        else:
            response = get(
                f"https://hsquizbowl.org/db/tournaments/search/?name={self.tournament}", headers=database.headers)
        soup = BeautifulSoup(response.content, "html.parser")
        self.res = BeautifulSoup(str(soup.find("span", class_="Name")), "html.parser")
        for i in self.res.a.children:
            self.tournament_name = i


class TournamentStatsHelper2(Thread):

    def __init__(self, name, res, team):
        Thread.__init__(self)

        self.name = name
        self.res = res
        self.team = team
        self.person = None
        # self.found = False

    def run(self):
        if not self.res:
            return
        else:
            stats, statline = database.build_matrix(f'https://hsquizbowl.org/db/{self.res.a["href"]}')
            stats = database.to_player(stats, statline)

            for i in range(len(stats)):
                if self.name in stats[i].name.lower():
                    if self.team and self.team not in stats[i].team.lower():
                        continue
                    self.person = stats[i]
                    # self.found = True
                    break


class PlotHelper(Thread):
    def __init__(self, link):
        Thread.__init__(self)

        self.link = link
        self.image = None

    def run(self):
        self.image = helpers.imgpcs.plot(self.link)

