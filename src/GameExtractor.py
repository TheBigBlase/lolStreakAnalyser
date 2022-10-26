import json
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

    def getPuuidBySummonerName(self, summoner_name: str = "TheBausffs") -> str:
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

    def getSummonerMatchesID(self, puuid: str) -> list[str]:
        """
        Gets the matches IDs of a given summoner
        :param puuid: the puuid of the summoner
        :return: a list of match ID
        """
        url = f'https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids' \
              f'?start=0&count=20&api_key={self.api_key}'

        print(url)

        res = self.execCurl(url)

        return res
