import db, config, os
from Data import request_safe
from datetime import datetime
from models import League

## FILL IN DB FROM FETCHED JSON

def construct_league(json: dict) -> League:
	# create initial league

	league_id = int(json['id'])
	league_name = json['name']
	db.insert_league(id=league_id,name=league_name)

	# create initial divisions
	division_names = set([r['division'] for r in json['rosters']])
	for name in division_names:
		db.insert_division(league_id, name=name)
	
	# create initial rosters
	for roster in json['rosters']:
		# roster["division"] gives the division NAME
		roster_info = [
			int(roster['id']),
			roster['name'],
			roster["division"],
			league_id
		]
		db.insert_roster(*roster_info)

	# create initial official series
	for official in json['matches']:
		official_info = [
			int(official['id']), 
			official['round_name'],
			int(official['round_number']),
			datetime.fromisoformat(official["created_at"]),
			league_id
		]
		db.insert_official(*official_info)
	
	# estimate league start-end dates based on match creation dates
	db.update_league_dates(league_id)
	return db.get_league(league_id)

def update_all_player_logs(league_id:int):
	i:int = 0
	players = db.get_players_in_league(league_id)
	for player in players:
		i += 1
		print(f"adding logs of {player.name} to db {i}/{len(players)}")
		search_result = search_player_logs(player.id_64)
		construct_logs_from_search(player.id_64, search_result)

def construct_logs_from_search(player_id_64:int, search_result:list[tuple]):
	for (log_id, date) in search_result:
		db.insert_log(log_id=log_id, date=date)
		db.add_player_to_log(player_id_64=player_id_64, log_id=log_id)

def update_all_roster_info(league_id:int):
	"""Because requsting a roster from ozf api gives the players on that roster
	we also go through and add a bunch of players to the database while we're at it"""
	rosters_to_update = db.get_rosters_in_league(league_id=league_id)
	for roster in rosters_to_update:
		data = fetch_roster_data(roster_id = roster.id)
		update_roster_info(data)

		for player in data['players']:
			db.insert_player(int(player['steam_64']), player['steam_id3'], player['name'], player['id'])
			db.add_player_to_roster(int(player['steam_64']), roster_id=data['id'])

def update_roster_info(json:dict):
	# Determine what roster is being updated
	roster_id = int(json['id'])

	# Update existing info.
	roster_name = json['name']
	division_name = json['division']
	db.update_roster(roster_id,roster_name,division_name)
	
### DATA FETCH METHODS
def fetch_league_data(league_id: int) -> dict:
	# Ideally the database would be used in favour of caching
	cache_filepath = os.path.join(config.league_response_cache, str(league_id) + ".json")
	url = os.path.join(config.ozf_url_prefix, "leagues/", str(league_id))
	return request_safe(cache_filepath, url, config.headers)["league"]

def fetch_roster_data(roster_id:int) -> dict:
	cache_filepath = os.path.join(config.roster_response_cache, str(roster_id) + ".json")
	url = os.path.join(config.ozf_url_prefix , "rosters/", str(roster_id))
	return request_safe(cache_filepath, url, config.headers)["roster"]

def update_all_player_logs_fast(league_id:int):
	""" Request most recent player logs and add them to db in order of recency
	stop once we get to a log already in the database."""

	# TODO THIS 

	pass

def search_player_logs(player_id_64:int) -> dict:
	"""Requests limited info on each and every log
	in which this player is present. Can be requested
	from Logs.tf API in batches."""

	ids: list[int] = []
	dates: list[datetime] = []
	# We may not get every single log in one search, so we do a loop
	done = False
	total = 0
	offset = 0
	results = 0
	print("starting log search")
	while not done:
		# Make one request
		cache_filepath = os.path.join(config.player_log_search_cache, f"id{player_id_64}" + f"off{offset}" + ".json")
		url = config.logs_url_prefix + f"?player={player_id_64}&offset={offset}"
		log_search_data = request_safe(cache_filepath, url)
		total = log_search_data['total']
		results = log_search_data['results']

		print(f"log search offset: {offset}")
		print(f"log search results: {results}")
		print(f"log search total: {total}")
		# Check if we're done
		if results+offset == total:
			done = True
		# Make sure we arent getting trolled by logs.tf
		assert results+offset <= total
		offset += results

		# Add the data from the request to the list of minilogs
		for log in log_search_data['logs']:
			ids.append(int(log['id']))
			# print(log['date'])
			dates.append(datetime.fromtimestamp(log['date']))
	
	assert len(ids) == len(dates) == total
	print("finishing log search")

	return zip(ids,dates)