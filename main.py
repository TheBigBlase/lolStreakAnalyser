from src.GameExtractor import GameExtractor

if __name__ == "__main__":
    GameExtractor = GameExtractor(use_cache_file=True)

    summoner_name = GameExtractor.sanitizeSummonerName("Phoque éberlué")

    puuid: str = GameExtractor.getPuuidBySummonerName(summoner_name)
    matches_id: list[str] = GameExtractor.getSummonerMatchesID(puuid, summoner_name)
    matches_data: list[any] = GameExtractor.getMatchesData(matches_id, summoner_name)

