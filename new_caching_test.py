from pprint import pprint
import db
from league_models import *
from time import sleep
from datetime import datetime
from database_helper import construct_league, request_basic, update_all_roster_info, update_roster_info, update_all_official_info, request_from_ozf
import config
from database.methods import official, player, roster, league
from fast_log_downloader import LogSearcher, GameRequester
import cProfile
import io
import pstats

def reduce_log_search_result(json:dict) -> dict:
	return {
		"success": json['success'],
		"results": json['results'],
		"total": json['total'],
		"parameters": json['parameters'],
		"logs": [
			{
				"id": log['id'],
				"date": log['date']
			}
			for log in json['logs']
		]
	}

def get_roster(id:int):
	pass

def get_match(id:int):
	pass

def search_logs(id_64:int):
	pass

def get_log(log_id:int):
	pass

def cached_request():
	pass

# pr = cProfile.Profile()
# pr.enable()

# # Initialising the log searcher causes it to immediately start retreiving logs from db in the background

data = request_from_ozf("league",30)
s_30 = construct_league(data)
update_all_roster_info(30)
update_all_official_info(30)
last_n_found = roster.get_roster(1097)
lnf_opponents = roster.get_opposing_teams(1097)

log_downloader = LogSearcher()
log_downloader.targets = [last_n_found, lnf_opponents]
log_downloader.execute_task()

game_requester = GameRequester() 
game_requester.targets = [last_n_found, lnf_opponents]
game_requester.execute_task()


# officials = roster.get_roster_officials(last_n_found.id)
# # print(officials)
# # player_on_rosters = roster.get_player_on_rosters(last_n_found.id)

# # for opp in lnf_opponents:
# # 	print(f"{opp}\nLogs:{roster.get_roster_logs(opp.id,4)}")

# for o in officials:
# 	print(o)
# 	official.create_candidate_logs(o,14)
# 	candidates = official.get_candidate_logs(o.id)
# 	print("Candidates:", len(candidates))
# 	for c in candidates:
# 		print(f"Candidate log: {c.log.link()}")
# 		print(f"Players: {c.player_names}")
# 		# print(f"{o.home_team.name} players:")
# 		# print(roster.get_rostered_players_in_log(o.home_team_id,c))
# 		# print(f"{o.away_team.name} players:")
# 		# print(roster.get_rostered_players_in_log(o.away_team_id,c))
# 		print()



# # pr.disable()
# s = io.StringIO()
# # sortby = SortKey.CUMULATIVE
# sortby = 'cumtime'
# ps = pstats.Stats(pr, stream=s)
# ps.strip_dirs().sort_stats(sortby).print_stats()

# ps.strip_dirs().sort_stats(sortby).print_callers()
# print(s.getvalue())
