from pprint import pprint
import db
from league_models import LogSearchInfo
from time import sleep
from datetime import datetime
from database_helper import construct_league, request_basic, update_all_roster_info, request_from_ozf
import config
from database.methods import league, log, player
from fast_log_downloader import LogSearcher
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

log_downloader = LogSearcher()
# # Initialising the log searcher causes it to immediately start retreiving logs from db in the background
data = request_from_ozf("league",30)
# pprint(data)
# # pprint(data)
construct_league(data)
data = request_from_ozf("league",62)
# pprint(data)
construct_league(data)
update_all_roster_info(30)
update_all_roster_info(62)

players = league.get_league_players(30)
for p in players:
	print(p.name, p.id_64)

ants = player.get_player("pengstah")
print(ants.name)


log_downloader.targets = [ants]
log_downloader.execute_task()

logs = player.get_player_logs(ants)
for l in logs:
	print(l.id)

# pr.disable()
# s = io.StringIO()
# # sortby = SortKey.CUMULATIVE
# sortby = 'cumtime'
# ps = pstats.Stats(pr, stream=s)
# ps.strip_dirs().sort_stats(sortby).print_stats()

# ps.strip_dirs().sort_stats(sortby).print_callers()
# print(s.getvalue())
