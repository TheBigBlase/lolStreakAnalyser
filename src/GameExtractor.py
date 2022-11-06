import json
#from datetime import date
from io import BytesIO
import time
import pycurl as curl
from src.utils import sanitizeSummonerName

###TODO : - optimize api call (for now 3 if no cache)
#         - remove useless prints
#         - keep stylish batch prints for more styles points
#         - cache should be separatted in mutliple files ?
#         - putting this to merge, take care of that plz thx <3


class GameExtractor:
    """
    Class used to extract data from Riot Games API
    """

    def __init__(self, use_cache_file=True, force_cache_reload=False):
        # load our summoner data
        with open("./apikey.json", "r") as key_file:
            self.json_file = json.load(key_file)

        self.api_key = self.json_file["X-Riot-Token"]

        self.use_cache_file = use_cache_file
        self.force_cache_reload = force_cache_reload

        if force_cache_reload:
            self.use_cache_file = True
            self.cache_path = "./out/cache.json" #beware windows, may fuck up relative path
            with open(self.cache_path, "w") as cache_file:
                cache_file.write("{}")

            with open(self.cache_path, "r") as cache_file:
                self.cache_data = json.load(cache_file)

        elif use_cache_file:
            self.cache_path = "./out/cache.json" #beware windows, may fuck up relative path

            #create file if not exist
            with open(self.cache_path, 'a') as cache_file:
                pass

            #r+ is read and write
            with open(self.cache_path, "r+") as cache_file:
                #check if file empty
                try:
                    self.cache_data = json.load(cache_file)
                    summoner_name = self.cache_data["name"]
                    self.summuary_file = f"./out/{sanitizeSummonerName(summoner_name)}_summuary.json"
                    with open(self.summuary_file, "r") as summuary_file:
                        self.summuary_data = json.load(summuary_file)

                #if emtpy then write
                except json.JSONDecodeError:
                    print("Exception json")
                    self.cache_data = json.loads("")
                    cache_file.write(self.cache_data)
                except KeyError:
                    print("error : no summuary or cache file ! "\
                            + "please force cache refresh with -f.")
                    exit(-1)

        else:
            self.cache_data = json.loads("")

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

        # put everything into json, decode with special caracters
        return json.loads(buffer.getvalue().decode('utf-8'))

    def getIdByPuuid(self, puuid: str) -> str:
        """
        Gets the id of the summoner linked by puuid
        :param puuid: puuid of a summoner
        :return: id
        """

        # Checks if the puuid is already in cache
        # NOTE not sure if loading and then parsing a 6mB json file 
        # is more efficient 

        # THIS IS NOT WORKING ie we're making another api call
        if self.use_cache_file:
            for k in self.cache_data: #look through all sum names
                if "id" in k and puuid in k:
                    return k["id"]

        url = 'https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/' \
              + puuid + '?api_key=' + self.api_key

        # Executing API request
        res = self.execCurl(url)


        #already written in getPuuidBySummonerName
        #with open("./out/" + self.cache_path, "a", encoding="utf-8") as file:
        #    file.writelines(json.dumps(res, indent=4))

        return res["id"]



    # NOTE no need of default str since default handled in main

    def getPuuidBySummonerName(self, summoner_name: str = "Phoque éberlué") -> str:
        """
        Gets the puuid of the summoner
        :param summoner_name: summoner name
        :return: puuid
        """

        # Checks if the puuid is already in cache
        # NOTE not sure if loading and then parsing a 6mB json file 
        # is more efficient
        if self.use_cache_file:
            if summoner_name == self.cache_data["name"] :
                if "puuid" in self.cache_data:
                    return self.cache_data["puuid"]

        summoner_name = sanitizeSummonerName(summoner_name)

        url = 'https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/' \
              + summoner_name + '?api_key=' + self.api_key

        # Executing API request
        res = self.execCurl(url)
        print("Retrieved summoner data :")
        print(res)

        # Saving the results in cache file if activated
        if self.use_cache_file:
            self.cache_data = res

            with open(self.cache_path, "w", encoding="utf-8") as file:
                file.writelines(json.dumps(res, indent=4))

            file.close()

        return res["puuid"]

    def getSummonerMatchesID(self, puuid: str, summoner_name: str = "Phoque éberlué") -> str|list[str]:
        """
        Gets the first 100 matches IDs of a given summoner. 
        Please use getSummonerAllMatchesIDinstead to get all
        :param puuid: the puuid of the summoner
        :param summoner_name: the name of the summoner
        :return: a list of match ID
        """

        summoner_name = sanitizeSummonerName(summoner_name)

        # Checks if the matches id are in the cache file
        if self.summuary_file:
            return json.dumps(self.summuary_file, indent=4)

        url = f'https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids' \
              f'?start=0' \
              f'&count=100' \
              f'&api_key={self.api_key}' \
              f'&queue=420'  # Indicates that we only want ranked games

        res = self.execCurl(url)

        # Saves matches id in the cache file
        if self.use_cache_file:

            with open(self.summuary_file, "w", encoding="utf-8") as file:
                file.writelines(json.dumps(res, indent=4))

        return res

    def getMatchData(self, match_id: str, summoner_name: str = "Phoque éberlué") -> dict:
        """
        Gets the matches IDs of a given summoner
        :param match_id: the match_id of the game
        :param summoner_name: the name of the summoner
        :return: match data
        """

        summoner_name = sanitizeSummonerName(summoner_name)

        # Checks if the match data already in cache file
        if self.use_cache_file \
                and match_id in self.summuary_file \
                and match_id in self.cache_data[summoner_name]["matches_data"]:
            return self.cache_data[summoner_name]["matches_data"][match_id]

        url = f'https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={self.api_key}'

        res = self.execCurl(url)
        #print(res)

        # Saves match data in cache file
        if self.use_cache_file:
            # Create a dictionary for matches data
            #if "matches_data" not in self.cache_data[summoner_name]:
            #    self.cache_data[summoner_name]["matches_data"] = {}

            #self.cache_data[summoner_name]["matches_data"][match_id] = res

            with open(f"./out/{summoner_name}_{match_id}.json", "w", encoding="utf-8") as file:
                file.writelines({json.dumps(res, indent=4)})

            file.close()
            if res == None:
                print('ERROR IN getMatchData')

        return res

    def getMatchesData(self, matches_id: list[str], summoner_name: str) -> dict:
        """
        Gets the data from the matches id passed as parameter
        :param matches_id: a list of matches id
        :param summoner_name:  the summoner name
        :return: dict of matches data
        """

        #DONT sanitze sum name here

        if self.use_cache_file \
                and list(self.summuary_data.keys())[0]:
            print("Using cached files for summuary file...")
            return self.summuary_data

        res = {}
        json_file = {}

        for i, match_id in enumerate(matches_id):
            #stylish, print state of current queries
            current_progress = "{:.2f}".format(i * 100 / len(matches_id))
            print(f"\rGathering data from matches : {current_progress} % done", end='')
            # Respecting rate limits of riot API (only for 20 secs)
            #if i % 20 == 0:
            #    time.sleep(1)

            # this already sanitize sum name
            res[match_id] = self.getMatchData(match_id, summoner_name)

            # see if our summoner won :
            has_won = False
            champion_name = ""

            for k in res[match_id]["info"]["participants"]:
                if k["puuid"] == self.cache_data["puuid"]:
                    has_won = k["win"]#json false not python False
                    champion_name = k["championName"]

                    dictionary = {
                            match_id:{
                                "win":has_won,
                                "champion": champion_name
                                }
                            }
                    json_file.update(dictionary)

                    break #stop for loop, we got what we were searching for


            time.sleep(1) #dont blow up api calls (respecc 2 mins)

        #last closing brace in json
        with open(f"./out/{sanitizeSummonerName(summoner_name)}_summuary.json",\
                "w", encoding="utf-8") as file:
            file.writelines(json.dumps(json_file, indent=4))

        return res

    def getNumberOfMatches(self, puuid) -> int:
        """
        Gets number of match of a summoner by puuid
        :param puuid: puuid of a summoner
        :return: numer of matches of a sum
        """

        summoner_id = self.getIdByPuuid(puuid)
        url = f'https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}'\
                + "?api_key=" + self.api_key

        res = self.execCurl(url)

        for k in res:
            if k["queueType"] == "RANKED_SOLO_5x5": #only care about ranked
                return int(k["wins"] + k["losses"])
        return -1 # if found nothing, error

    def getSummonerAllMatchesID(self, summoner_name: str) -> list[str]:
        """
        Gets the matches IDs of a given summoner
        :param summoner_name: the summoner name
        :return: a list of match ID
        """

        # instead of proceeding by dates, lets look at the number of game in the season
        # we're requesting a batch of 100 game, then the next one until
        # we gain no information, ie we append nothing to the list of matches

        puuid = self.getPuuidBySummonerName(summoner_name)
        summoner_name = sanitizeSummonerName(summoner_name)
        nb_matches = self.getNumberOfMatches(puuid)
        matches_id = []  # list instead of set to extract data later
        match_counter = 0

        #if summuary has at least 1 game : 
        #this way we bypass the mathces_id file, less memory used on runtime
        if self.use_cache_file \
                and list(self.summuary_data.keys())[0]:
            print("using cached files for list of game ids...")
            return list(self.summuary_data.keys())

        #start_date = date.fromisocalendar(season, 1, 1)
        #start_time = time.mktime(start_date.timetuple())

        #nb_day_this_season = (date.today() - start_date).days

        # Gathering 100 games per 10 day
        while match_counter < nb_matches: # while we can append new results
            #end_time = int(start_time + 60 * 60 * 24 * 10)

            #stylish, print state of current queries {:.2f} is to keep 3 digits of float
            current_progress = "{:.2f}".format(match_counter * 100 / nb_matches)
            print(f"\rGettig match list : {current_progress} % done", end='')

            url = f'https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids' \
                  f'?start={match_counter}' \
                  f'&count=100' \
                  f'&api_key={self.api_key}' \
                  f'&queue=420'  # Indicates that we only want ranked games

            res = self.execCurl(url)

            matches_id = matches_id + res
            #matches_id[f'{match_counter}'] = res
            match_counter+=100

            #start_time = end_time

            time.sleep(1)

        #extra spaces to erease last line
        print(f"\rPulled all matches id !          ")

        # has to save ???
        with open("./out/" + summoner_name + "_matchIds.json", "w", encoding="utf-8") as file:
            file.writelines(json.dumps({"id_array" : matches_id},indent=4))

        return matches_id
