import json
from datetime import date
import time
import pycurl as curl
from io import BytesIO


class GameExtractor:
    """
    Class used to extract data from Riot Games API
    """

    def __init__(self):
        # load our summoner data
        self.json_file = json.load(open("./apikey.json", "r"))
        self.api_key = self.json_file["X-Riot-Token"]

    @staticmethod
    def execCurl(url: str) -> any:
        """
        Execute a request using curl
        :param url: the URL
        :return: response
        """
        # init curl + buffer
        c = curl.Curl()
        buffer = BytesIO()

        # set option for curl
        c.setopt(c.URL, url.encode('utf-8'))
        c.setopt(c.WRITEDATA, buffer)

        # perform requests
        c.perform()
        c.close()

        # put everything into json
        return json.loads(buffer.getvalue().decode('iso-8859-1'))

    def getPuuidBySummonerName(self, summoner_name: str = "Phoque éberlué") -> str:
        """
        Gets the puuid of the summoner
        :param summoner_name: summoner name
        :return: puuid
        """
        # Replacing spaces with plus
        summoner_name = summoner_name.replace(" ", "+")

        url = 'https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/' \
              + summoner_name + '?api_key=' + self.api_key

        # Executing API request
        res = self.execCurl(url)
        print(res)
        return res["puuid"]

    def getSummonerMatchesID(self, puuid: str) -> set[str]:
        """
        Gets the matches IDs of a given summoner
        :param puuid: the puuid of the summoner
        :return: a list of match ID
        """
        matches_id = set()

        start_date = date.fromisocalendar(2022, 1, 1)
        start_time = time.mktime(start_date.timetuple())

        nb_day_this_season = (date.today() - start_date).days

        # Gathering 100 games per 10 day
        for i in range(0, int(nb_day_this_season / 10) + 1):
            end_time = int(start_time + 60 * 60 * 24 * 10)

            url = f'https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids' \
                  f'?startTime={int(start_time)}' \
                  f'&?endTime={int(end_time)}' \
                  f'&?start=0' \
                  f'&count=100' \
                  f'&api_key={self.api_key}' \
                  f'&queue=420'  # Indicates that we only want ranked games

            res = self.execCurl(url)

            matches_id.update(res)

            start_time = end_time

            time.sleep(1)

        print(matches_id)

        return matches_id
