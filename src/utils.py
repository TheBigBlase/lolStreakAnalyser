def sanitizeSummonerName(summoner_name: str) -> str:
    """
    replace space in summoner name
    (useful for puting it into an url)
    """
    # Replacing spaces with plus
    return summoner_name.replace(" ", "+")
