import json
from datetime import date
import time
import pycurl as curl
from io import BytesIO


class GameExtractor:
    """
    Class used to extract data from Riot Games API
    """

    def __init__(self, use_cache_file=True):
        # load our summoner data
        with open("./apikey.json", "r") as key_file:
            self.json_file = json.load(key_file)

        self.use_cache_file = use_cache_file

        if use_cache_file:
            self.cache_path = "./cache.json"

            with open(self.cache_path, "r") as cache_file:
                self.cache_data = json.load(cache_file)

        self.api_key = self.json_file["X-Riot-Token"]

    @staticmethod
    def sanitizeSummonerName(summoner_name: str):
        # Replacing spaces with plus
        return summoner_name.replace(" ", "+")

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

        # Checks if the puuid is already in cache
        if self.use_cache_file \
                and summoner_name in self.cache_data \
                and "puuid" in self.cache_data[summoner_name]:
            return self.cache_data[summoner_name]["puuid"]

        url = 'https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/' \
              + summoner_name + '?api_key=' + self.api_key

        # Executing API request
        res = self.execCurl(url)
        print(res)

        # Saving the results in cache file if activated
        if self.use_cache_file:
            self.cache_data[summoner_name] = res

            with open(self.cache_path, "w", encoding="utf-8") as file:
                file.write(json.dumps(self.cache_data))

        return res["puuid"]

    def getSummonerMatchesID(self, puuid: str, summoner_name: str = "Phoque éberlué") -> list[str]:
        """
        Gets the matches IDs of a given summoner
        :param puuid: the puuid of the summoner
        :param summoner_name: the name of the summoner
        :return: a list of match ID
        """

        # Checks if the matches id are in the cache file
        if self.use_cache_file \
                and "matches_id" in self.cache_data[summoner_name]:
            return self.cache_data[summoner_name]["matches_id"]

        url = f'https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids' \
              f'?start=0' \
              f'&count=100' \
              f'&api_key={self.api_key}' \
              f'&queue=420'  # Indicates that we only want ranked games

        res = self.execCurl(url)

        # Saves matches id in the cache file
        if self.use_cache_file:
            self.cache_data[summoner_name]["matches_id"] = res

            with open(self.cache_path, "w", encoding="utf-8") as file:
                file.write(json.dumps(self.cache_data))

        return res

    def getMatchData(self, match_id: str, summoner_name: str = "Phoque éberlué") -> dict:
        """
        Gets the matches IDs of a given summoner
        :param match_id: the match_id of the game
        :param summoner_name: the name of the summoner
        :return: match data
        """

        # Checks if the match data already in cache file
        if self.use_cache_file \
                and "matches_data" in self.cache_data[summoner_name] \
                and match_id in self.cache_data[summoner_name]["matches_data"]:
            return self.cache_data[summoner_name]["matches_data"][match_id]

        url = f'https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={self.api_key}'

        res = self.execCurl(url)
        print(res)

        # Saves match data in cache file
        if self.use_cache_file:
            # Create a dictionary for matches data
            if "matches_data" not in self.cache_data[summoner_name]:
                self.cache_data[summoner_name]["matches_data"] = {}

            self.cache_data[summoner_name]["matches_data"][match_id] = res

            with open(self.cache_path, "w", encoding="utf-8") as file:
                file.write(json.dumps(self.cache_data))

        return res

    def getMatchesData(self, matches_id: list[str], summoner_name: str) -> dict:
        """
        Gets the data from the matches id passed as parameter
        :param matches_id: a list of matches id
        :param summoner_name:  the summoner name
        :return: dict of matches data
        """
        time.sleep(1)

        res = {}
        for i, match_id in enumerate(matches_id):
            # Respecting rate limits of riot API
            if i % 20 == 0:
                time.sleep(1)

            res[match_id] = self.getMatchData(match_id, summoner_name)

        return res

    # ------------------------- NOT WORKING ----------------------------------
    def getSummonerAllMatchesID(self, puuid: str, season: int) -> set[str]:
        """
        Gets the matches IDs of a given summoner
        :param puuid: the puuid of the summoner
        :param season: the year of the season e.g: S12 = 2022
        :return: a list of match ID
        """
        matches_id = set()

        start_date = date.fromisocalendar(season, 1, 1)
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
