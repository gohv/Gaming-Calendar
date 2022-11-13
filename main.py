import requests
import json
import Game

#THIS FILE IS USED ONLY FOR TESTING THE API CALLS

game_request = requests.get(
    "https://api.rawg.io/api/games?key=d430c2ba8e9146d7af53c78d27ba9a57&dates=2022-01-01,2022-11-01&platforms=18,1,7")

games_list_raw = json.loads(game_request.content.decode("utf-8"))

game_results = games_list_raw.get("results")
slug = ""

for single_game in game_results:
    name = single_game["name"]
    release_date = single_game["released"]
    play_time = single_game["playtime"]
    slug = single_game["slug"]
    print(name)

game_details = requests.get("https://api.rawg.io/api/games/"+slug+"?key=d430c2ba8e9146d7af53c78d27ba9a57")
game_details_raw = json.loads(game_details.content.decode("utf-8"))

print(game_details_raw["metacritic_platforms"][0]["url"])
