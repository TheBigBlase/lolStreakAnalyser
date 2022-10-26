from src.GameExtractor import GameExtractor

if __name__ == "__main__":
    GameExtractor = GameExtractor()
    puuid = GameExtractor.getPuuidBySummonerName("Phoque éberlué")
    games = GameExtractor.getSummonerMatchesID(puuid)
