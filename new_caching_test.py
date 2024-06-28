from pprint import pprint
import db
from league_models import LogSearchInfo
from time import sleep
from datetime import datetime
from database_helper import construct_league, request_basic, update_all_roster_info, request_from_ozf
import config
from database.methods import league
from fast_log_downloader import LogSearcher

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


# def update_all_player_logs(league_id:int):
# 	i:int = 0
# 	players = db.get_players_in_league(league_id)
# 	for player in players:
# 		i += 1
# 		print(f"adding logs of {player.name} to db {i}/{len(players)}")
# 		update_player_logs(player.id_64)

# def update_player_logs(id_64:int, force_manual_check:bool=False):
# 	"""Only manually check for new logs through logs.tf request if 
# 	the last logs.tf response is older than 3 days"""
# 	last_search_info = db.get_log_search_info(id_64=id_64)
# 	# TODO Fix this

# 	if last_search_info==None or force_manual_check or last_search_info.expiry_date <= datetime.today():
# 		# We now update our records of this players logs
# 		url = config.logs_url_prefix + f"?player={id_64}"
# 		# Reducing the search results might ultimately slow this down
# 		print("checking for new logs")
# 		search_results = reduce_log_search_result(request_basic(url))
# 		if last_search_info == None:
# 			print("requesting logs")
# 			print("no logs on record")
# 			log_batch = request_all_logs(id_64)
# 			# db.add_search_info(id_64, )
# 			db.add_log_batch(id_64, log_batch)
# 			# last_search_info = db.get_log_search_info(id_64)
# 			return
# 		assert isinstance(search_results['total'],int)
# 		if search_results['total'] == last_search_info.num_logs:
# 			# We are up to date, reset the expiry date and return only cached data.
# 			# pprint(search_results)
# 			# print(last_search_info.num_logs)
# 			print("we are up to date on this player's logs")
# 			db.reset_search_expiry(id_64)
# 			# logs = ["tes tes testasets", "saljdfjalskk"]
# 			# logs = db.search_player_logs(id_64=id_64)
# 			return 
# 		# We are missing at least 1 log.
# 		print("requesting logs")
# 		num_missing = search_results['total']-last_search_info.num_logs
# 		log_batch = request_all_missing_logs(last_search_info,num_missing=num_missing, log_search_data=search_results)
# 		db.add_log_batch(id_64, log_batch, last_search_info)

# 		db.reset_search_expiry(id_64)
# 	else:
# 		print("dont need to check")

# def request_all_logs(id_64:int) -> list:
# 	max_request_size = 1000 # limited by logs.tf
# 	offset=0
# 	log_batch = []
# 	url = config.logs_url_prefix + f"?player={id_64}&offset={offset}"
# 	log_search_data = reduce_log_search_result(request_basic(url))
# 	print("making api call")
# 	log_batch.extend(log_search_data['logs'])
# 	print(f"acquired {len(log_batch)} of {log_search_data['total']} needed")
# 	print(f"num logs needed: {log_search_data['total']}")
# 	while len(log_batch) < log_search_data['total']:
# 		offset += max_request_size
# 		url = config.logs_url_prefix + f"?player={id_64}&offset={offset}"
# 		print("making api call")
# 		log_search_data = reduce_log_search_result(request_basic(url))
# 		log_batch.extend(log_search_data['logs'])
# 		print(f"acquired {len(log_batch)} of {log_search_data['total']} needed")
# 	return log_batch

# def request_all_missing_logs(last_search_info:LogSearchInfo, num_missing:int,log_search_data:dict=None) -> list:
# 	max_request_size = 1000 # limited by logs.tf
# 	id_64 = last_search_info.id_64
# 	print(f"number of missing logs: {num_missing}")
# 	if log_search_data == None:
# 		log_batch = []
# 		offset = 0
# 	else:
# 		log_batch = log_search_data['logs']
# 		offset = log_search_data['results']
# 	while num_missing > len(log_batch):
# 		url = config.logs_url_prefix + f"?player={id_64}&offset={offset}"
# 		# Reducing the search results might ultimately slow this down
# 		log_search_data = reduce_log_search_result(request_basic(url))
# 		print(f"requesting missing logs: {len(log_batch)}/{num_missing}")
# 		log_batch.extend(log_search_data['logs'])
# 		offset += max_request_size
# 		sleep(2) # Improve this later
# 	return log_batch

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


data = request_from_ozf("league",30)
# pprint(data)
construct_league(data)
data = request_from_ozf("league",62)
# pprint(data)
construct_league(data)
update_all_roster_info(30)
update_all_roster_info(62)

players = league.get_league_players(30).union(league.get_league_players(62))

log_downloader = LogSearcher()
log_downloader.targets = [league.get_league(30),league.get_league(64)]

log_downloader.execute_task()

# print("updating all player logs in ozf")
# for (i,p) in enumerate(players):
# 	print(f"updating {p.name} logs ({i}/{len(players)})")
# 	update_player_logs(p.id_64)

