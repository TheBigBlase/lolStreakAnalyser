from src.GameExtractor import GameExtractor
import argparse

if __name__ == "__main__":
    ## BEGIN ARGUMENT PARSER
    parser = argparse.ArgumentParser(description="Retrieve and analyse data from" \
            + "league games")

    parser.add_argument("-s", "--summonerName", help = "set whose game should be looked into"\
            + "(default = Phoque éberlué)", default = "Phoque éberlué")

    parser.add_argument("-n", "--noCache", help = "do not use already retrieved data"\
            "(default = false)", action="store_true", default = False)

    args = parser.parse_args()
    ## END ARGUMENT PARSER

    GameExtractor = GameExtractor(use_cache_file = not(args.noCache))

    summoner_name = GameExtractor.sanitizeSummonerName(args.summonerName)

    puuid: str = GameExtractor.getPuuidBySummonerName(summoner_name)
    #matches_id: list[str] = GameExtractor.getSummonerMatchesID(puuid, summoner_name)
    #matches_data: list[any] = GameExtractor.getMatchesData(matches_id, summoner_name)
    matches_ids = GameExtractor.getSummonerAllMatchesID(summoner_name)
    GameExtractor.getMatchesData(matches_ids, summoner_name)
