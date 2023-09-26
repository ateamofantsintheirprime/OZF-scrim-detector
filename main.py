import json, os.path
from Team import Team, Player
from Data import make_request
from pprint import pprint
from requests.structures import CaseInsensitiveDict

headers = CaseInsensitiveDict()
with open("ozf_api_key.json", "r") as f:
    key = json.loads(f.read())["key"]
headers["X-API-Key"] = key

# PUT THIS API KEY IN A FILE

log_ids_path = "log_ids/"
if not os.path.exists(log_ids_path):
    os.mkdir(log_ids_path)

filepath = "league_data.json"
url_prefix = "https://ozfortress.com/api/v1/leagues/"
current_season = 56
# url_ids = list(range(current_season-2, current_season + 1)) # this includes non-sixes seasons
url_ids = [current_season]
# Get last 3 seasons
# Make requests for the last 3 leagues
league_list = [league["league"] for league in make_request(filepath, url_prefix, url_ids, headers)]

# Get all ids from those seasons

active_team_ids = []

for league in league_list:
    league_team_list = league["rosters"]
    league_team_ids = [int(team["id"]) for team in league_team_list]
    active_team_ids += league_team_ids

url_ids = list(set(active_team_ids)) # Get rid of duplicates.

# Get all those teams

filepath = "team_data.json"
url_prefix = "https://ozfortress.com/api/v1/rosters/"

# pprint(make_request(filepath, url_prefix, url_ids, headers))
team_list = [team["roster"] for team in make_request(filepath, url_prefix, url_ids, headers)]

# Create team objects from all those JSON objects.

team_obj_list = []

for team in team_list:
    team_players = [Player(player["steam_64_str"], player["steam_id3"], player["name"]) for player in team["players"]]
    new_team = Team(int(team["id"]), team["name"], team_players)
    team_obj_list.append(new_team)

team_list = team_obj_list

# Make a search request from logs.tf for each players from that roster.
#       Get the log_ids of each log that those players played in.

for team in team_list: # Get the logs pertaining to each active team
    team.get_logs()

total_log_requests = 0
for team in team_list:
    print(f"rid:{team.id}={len(team.logs)}", end=", ")
    total_log_requests += len(team.logs)
print(f"= total log requests needed: {total_log_requests}")

# Get the logs individually from logs.tf in order to check for team alignment and date



# Trim it down to only logs where those players on the same team



# Sort those logs by team



# CONSIDER: if a team plays multiple leagues. If a team has the same players as another team. 
