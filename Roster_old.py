import os, config
from Data import request_batch, request_safe
from Player_old import Player
from Log_old import FullLog
from pprint import pprint


class Matchup():
	def __init__(self):
		self.url
		self.opponent
		self.score

class Roster():
	def __init__(self, id, league_dir, league_start_date, league_end_date):
		self.id = id
		self.logs: list[FullLog] = []
		self.roster_dir = self.build_roster_dir(league_dir)
		self.start_date = league_start_date
		self.end_date = league_end_date
		
		# Make request for roster data
		data = self.get_roster_data()
		self.data = data

		# Store roster data
		self.name = data["name"]
		self.players: list[Player] = []

		self.team_matchups = []
		self.pugscrim_matchups = []

		# request_progress = 0
		for player in data["players"]:
			ozfid = player["id"]
			id64 = player["steam_64_str"]
			id3 = player["steam_id3"]
			name = player["name"]
			new_player: Player = Player(id64, id3,ozfid, name)
			self.players.append(new_player)
			# print(f"Constructing Player: {request_progress}/{len(data['players'])}\n\tRoster id: {self.id}\n\tRoster name: {self.name}\n\tID64: {new_player.id64}\n\tName: {new_player.name}")
			# request_progress += 1

		print(f"Team:\n\tname:{self.name}\n\troster id:{self.id}")
		self.get_official_matches()

	def init(self):
		print("Initialising player logs")
		for player in self.players:
			player.update_minilogs()
		print("Gathering team logs")
		self.potential_logs = self.get_potential_logs()
		# self.get_logs()
		self.get_logs_parallel()
		print(f"\tlogs:{[log.id for log in self.logs]}")


	def get_logs_parallel(self):
		print(f"Parrallelised request for logs of roster : {self.id}, {self.name}")
		cache_filepath_prefix = config.log_cache
		url_prefix = config.logs_url_prefix + "/"
		ids = [str(id) for id in self.potential_logs.keys()]
		batch = request_batch(cache_filepath_prefix, url_prefix, ids)
		self.logs.clear()
		for i in range(len(batch)):
			self.logs.append(FullLog(batch[i], ids[i]))
		# self.logs = [FullLog(log_data) for log_data in batch]
		self.trim_logs()


	def get_roster_data(self):
		print(f"Requesting roster data, id: {self.id}")
		cache_filepath = os.path.join(config.roster_response_cache, str(self.id) + ".json")
		url = os.path.join(config.ozf_url_prefix , "rosters/", str(self.id))
		data = request_safe(cache_filepath, url, config.headers)["roster"]
		return data

	def build_roster_dir(self, league_dir) -> str:
		path = os.path.join(league_dir, str(self.id), "")
		if not os.path.exists(path):
			os.mkdir(path)
		return path
	
	def guess_core_players(self):
		# TODO get the most common steam ids in logs belonging to this team
		pass

	def get_potential_logs(self, count =4):
		"""Check if at least 4 players on the roster are in the game
		And that the log was played during the season."""
		log_count = {}
		for player in self.players:
			for minilog in player.minilogs:
				if minilog.falls_within_dates(self.start_date, self.end_date):
					if minilog.id in log_count.keys():
						log_count[minilog.id]["players"].append([player.id64, player.name])
					else:
						log_count[minilog.id] = {"date": minilog.date, "players": [[player.id64, player.name]]}
		logs = {} # we could just delete from the old dict
		for id in log_count.keys():
			if len(log_count[id]["players"]) >= count:
				logs[id] = log_count[id]
		# print(f"Roster id:{self.id}, Trimmed logs:")
		# pprint(trimmed_logs)
		# print(trimmed_logs.keys())
		return logs

	def trim_logs(self, player_threshhold =3):
		trimmed_logs = []
		self.log_sides = []
		# filters out non-sixes logs
		# trimmed_logs = self.only_sixes(self.logs)
		for log in self.logs:
			# Filter out non-sixes logs or logs missing lots of players
			if abs(len(log.red_team) - 6) <= 1 and abs(len(log.blue_team) - 6) <= 1:
				red_count = len([player.id3 for player in self.players if player.id3 in log.red_team])
				blue_count = len([player.id3 for player in self.players if player.id3 in log.blue_team])

				if red_count > player_threshhold:
					self.log_sides.append({"log" : log, "side": 0})
					trimmed_logs.append(log)
				elif blue_count > player_threshhold:
					self.log_sides.append({"log" : log, "side": 1})
					trimmed_logs.append(log)

		# print("trimmed logs:", trimmed_logs)
		assert len(trimmed_logs) > 0 # If this fails we have some problems

		self.logs = trimmed_logs

	# def only_sixes(self, logs):
	#	 trimmed_logs = []
	#	 for log in logs:
	#		 if abs(len(log.red_team) - 6) <= 1 and abs(len(log.blue_team) - 6) <= 1:
	#			 trimmed_logs.append(log)
	#	 return trimmed_logs

	def print(self):
		# TODO
		pass

	def get_official_matches(self):
		print("DATA:")
		""" Request info for each match associated with that roster for the season. 
		We want to create a "guess" as to which logs are for which matches.
		The info we know for sure: 
			- what map we're looking for
			- what teams we're looking for
			- what the scoreline was 
			- if it DID go to golden cap
			- (we cant always say that the match DIDNT go to gc)
		The info we can approximate:
			- What teams are present in what logs
			- Around about what dates we expect the match to be played
				(What if they get an extension?)
		"""

		# pprint(self.data['matches'])
		self.officials = [
			{
				"id":m['id'], 
				"created_at" : m['created_at'],
				"round_number": m['round_number']
			} for m in self.data['matches']
		]
		pprint(self.officials)


	# def get_logs(self):
	#	 """ Check that there are at least count players
	#	 from this roster on the SAME TEAM in each log.
	#	 This involves requesting each log INDIVIDUALLY"""

	#	 print(f"Requesting logs for roster: {self.id}, {self.name}")

	#	 progress = 0
	#	 # pprint(self.potential_logs)
	#	 for id in self.potential_logs.keys():
	#		 print(f"Requesting log: {progress} / {len(self.potential_logs)}", end = '\r')
	#		 cache_filepath = os.path.join(config.log_cache, str(id) + ".json")
	#		 url = config.logs_url_prefix + "/" + str(id)
	#		 log = request_safe(cache_filepath, url)
	#		 # print(f"Recieved log: {id}")
	#		 self.logs[id] = log
	#		 progress += 1

	#	 print(f"PRETRIM:\n\t{len(self.logs)} Logs associated with team:\n\tTeam id: {self.id}\n\tTeam name: {self.name}")

	#	 # self.trim_logs()