# Lol Streak Analyzer  

This is a student project to fulfill a data science achievement.  
The goal is to see what parameters of a game are most important 
to determine its outcome and help escape the loose queue.

## Installation 
This is written in python. In order to install it, first clone the repo, then 
go to its root and run : 
```bash
pip install -r ./requirements.txt
```

## Usage 
Put your api key in the json file "apikey.json" like such : 

```json
{
	"X-Riot-Token": "YOUR_TOKEN_HERE"
}
```
then launch it with : 
```bash 
python ./src/main.py [-s | --summonerName "Phoque éberlué"] [-n | --noCache]
```
replacing "Phoque éberlué" with your summoner name.
