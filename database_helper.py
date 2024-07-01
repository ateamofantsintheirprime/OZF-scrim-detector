import db, requests, json, re, config
from datetime import datetime
from pprint import pprint
from league_models import League, Roster
from database.methods import league, roster, division, official, player, response

# TODO Add bulk methods for any database interactions where possible to reduce # of session.commits()
# TODO add all parameter type hints and return type hints
# TODO raise warning if type hints are not followed

def construct_league(json: dict) -> League:
	# create initial league

	league_id = int(json['id'])
	league_name = json['name']
	league.insert_league(id=league_id,name=league_name)

	# create initial divisions
	division_names = set([r['division'] for r in json['rosters']])
	for name in division_names:
		division.insert_division(league_id, name=name)
	
	# create initial rosters
	for roster_json in json['rosters']:
		# roster["division"] gives the division NAME
		roster_info = [
			int(roster_json['id']),
			roster_json['name'],
			roster_json["division"],
			league_id
		]
		roster.insert_roster(*roster_info)

	# create initial official series
	for official_json in json['matches']:
		official_info = [
			int(official_json['id']), 
			official_json['round_name'],
			int(official_json['round_number']),
			datetime.fromisoformat(official_json["created_at"]),
			league_id
		]
		official.insert_official(*official_info)
	
	# estimate league start-end dates based on match creation dates
	league.estimate_league_dates(league_id)
	return league.get_league(league_id)	

def update_all_roster_info(league_id:int=None, rosters_to_update:list[Roster]=None):
	if rosters_to_update is None:
		if league_id is None:
			print("Missing arguments")
			raise Exception
		rosters_to_update = league.get_league_rosters(league_id=league_id)
	# TODO Add a bulk roster update method to avoid more session.commit()s than necessary?
	for roster in rosters_to_update:
		update_roster_info(roster_id=roster.id, update_players=True)


def update_roster_info(json:dict=None, roster_id:int=None, update_players:bool=True):
	#If not provided json content, we request it ourselves
	if json is None:
		if roster_id is None:
			print("either roster id or json must be provided")
			raise Exception
		json = request_from_ozf("roster", roster_id)
	# Determine what roster is being updated
	roster_id = int(json['id'])

	# Update existing info.
	roster_name = json['name']
	division_name = json['division']
	roster.update_roster(roster_id,roster_name,division_name)
	
	# OZF API Roster request also gives player info. So we add that in this function too
	if update_players:
		for player_json in json['players']:
			# If player is not in the db, add them
			player.insert_player(
				id_64=player_json['steam_64'],
				id3=player_json['steam_id3'],
				name=player_json['name'],
				ozf_id=player_json['id']
			)
			# If player is not on the team in db, add them
			# Move this out of db.py
			db.add_player_to_roster(roster_id, player_ozf_id=player_json['id'])

def request_all_officials(league_id:int) -> list[dict]:
	officials= league.get_league_officials(league_id)
	data_list=[]
	for o in officials:
		data_list.append(request_from_ozf("match",o.id))
	return data_list
		
def update_all_official_info(league_id:int):
	data_list = request_all_officials(league_id)
	for data in data_list:
		update_official_info(data)

def update_official_info(json:dict):
	id=int(json['id'])
	forfeit=json['forfeit_by']
	home_team_id=int(json['home_team']['id'])
	away_team_id=None
	bye=True
	if not json['away_team'] is None:
		away_team_id=int(json['away_team']['id'])
		bye=False
	official.update_official(id,home_team_id,forfeit,bye,away_team_id)

### DATA FETCH METHODS

def request_from_ozf(type:str, id:str, force_update:bool=False):
	# TODO Check in the league_database if the league object is stored
	# BEFORE we check in the cache_database for the response object
	prefixes = {
		"roster":"rosters",
		"league":"leagues",
		"match":"matches",
		"user":"users"
	}
	key = f"{type}{str(id)}"
	resp = response.get_response(key=key)
	if resp is None or force_update:
		url = f"{config.ozf_url_prefix}/{prefixes[type]}/{str(id)}"
		data = request_basic(url, config.headers)[type]
		if force_update:
			response.update_response(key, data)
		else:
			response.insert_response(key, data)
	else:
		data = resp.data
	return data

def request_basic(url:str, headers = {}) -> dict:
	# Add error codes, reattempting etc
	resp = requests.get(url, headers=headers)
	data = json.loads(expunge_unicode(resp.text))
	return data

def expunge_unicode(text:str) -> str:
	"""For some reason unicode characters will sometimes
	turn into a 6 character string that consist of the actual
	code. And sometimes they will 'recombine' into the single
	unicode character. We do .encode() to catch cases of the 
	latter, and a regex substitute to catch the former"""
	step_1 = text.encode("ascii", "ignore").decode()
	step_2 = re.sub(r"\\+u\S{4}", "", step_1)
	return step_2