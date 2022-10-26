import pycurl as curl
from io import BytesIO
import json 

def getBySummonerName():
    #load our summoner data
    jsonFile = json.load(open("./apikey.json", "r"))
    apikey = jsonFile["X-Riot-Token"]
    name = jsonFile["SummonerName"]

    #init curl + buffer
    c = curl.Curl()
    buffer = BytesIO()
    url = 'https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/' \
        + name + '?api_key=' + apikey

    #set option for curl
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, buffer)
    
    #perform requests
    c.perform()
    c.close()

    #put everything into json
    res = json.loads(buffer.getvalue().decode('iso-8859-1'))
    print(res)

    #is puuid what we wanted ? in case there it is
    print(res["puuid"])
