import pycurl as curl
from io import BytesIO
import json 

def main():
    apikey = json.load(open("../apikey", "r"))
    c = curl.Curl()
    buffer = BytesIO()
    c.setopt(c.URL, 'https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/thebigblase')
    c.setopt(c.WRITEDATA, buffer)
    [print(key + '\n') for key in apikey]
    c.setopt(c.HTTPHEADER, apikey)

     
if __name__=="__main__":
    main()
