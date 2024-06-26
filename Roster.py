from typing import Union
from Player import NonOZFPlayer, OZFPlayer
from Log import FullLog, MiniLog
from League import League
from Matchup import TeamGame, PugScrim, OfficialGame, OfficialSeries
from Data import request_batch
from log_filtration_variables import *
import config

class Roster():
	"""A group of players with an ozf team page
	signed up to a season (NOTE: this roster is 
	specific to that season. Last & Found in S30
	is totally distinct from Last & Found in S31)"""
	def __init__(self):
		self.players= list[OZFPlayer]
		self.id= int
		self.name= str
		self.division= str

		self.parent_league = League 

		self.__fulllogs: list[FullLog] = []
		self.__minilogs: list[MiniLog] = []

		self.pugscrims: list[PugScrim] = []
		self.team_games: list[TeamGame] = []
		self.official_games: list[OfficialSeries] = []
		self.official_series: list[OfficialSeries] = []

		"""NOTE: The difference between the fetch and get methods is
		the fetch method requests the data from the API and 
		stores it. The get method will attempt to fetch if not
		already fetched, and then will filter and process it into
		a useful form """

	def from_json(self, json:dict):
		self.id = json['id']
		self.name = json['name']
		self.division = json['division']

	def fetch_all_player_minilogs(self):
		assert len(self.players) >= 6
		for player in self.players:
			if len(player.minilogs) == 0:
				player.fetch_all_minilogs()

	def get_roster_minilogs(self):
		"""Get all minilogs that occur in at least
		THRESHOLD players minilog lists, and that
		are within the start and end dates of the
		parent league"""
		assert len(self.__minilogs) == 0
		self.__minilogs.clear()
		# Make sure all plays have their minilogs
		self.fetch_all_player_minilogs()
		# Make sure we have league dates 
		if self.parent_league.start_date == None or self.parent_league.end_date == None:
			self.parent_league.estimate_dates()
		# Data structure for counting and storing minilogs
		counting_dict = {
			"id" : { # ID of a minilog
				"minilog" : MiniLog, # The minilog its self
				"count" : int # The number of players of this roster who are in the minilog
			}
		}

		# Count all minilogs 
		start = self.parent_league.start_date
		end = self.parent_league.end_date
		all_minilogs = [minilog for player in self.players for minilog in player.minilogs]
		for minilog in all_minilogs:
			# Check date
			if not minilog.falls_within_dates(start,end):
				continue

			# Count
			if minilog.id in counting_dict.keys():
				counting_dict[minilog.id]['count'] += 1
			else:
				counting_dict[minilog.id] = {
					"minilog" : minilog,
					"count" : 1
				}

		# Filter down roster minilogs using threshhold constant
		for id in counting_dict.keys():
			if counting_dict[id]['count'] >= ROSTER_IDENTIFICATION_THRESHHOLD:
				self.__minilogs.append(counting_dict[id]['minilog'])


	def fetch_full_logs_from_minilogs(self):
		"""
		Get full logs for every minilog. Make sure to
		Fetch AND filter (get) every minilog first,
		note: this uses the request_batch() function which
		is parallelised.
		"""
		assert len(self.__fulllogs) == 0
		# Make sure we first have the rosters minilogs
		if len(self.__minilogs) == 0:
			self.get_roster_minilogs()
		self.__fulllogs.clear()

		# Get the log ids we are requesting for
		ids = [str(m.id) for m in self.__minilogs]

		# Execute cached+batched request
		cache_filepath_prefix = config.log_cache
		url_prefix = config.logs_url_prefix + "/"
		raw_full_log_data = request_batch(cache_filepath_prefix, url_prefix, ids)
		# FYI the result of this request does not contain the id we queried it with, so we gotta store that

		for i in range(len(raw_full_log_data)):
			full_log = FullLog()
			full_log.id = ids[i]
			full_log.from_json(raw_full_log_data[i])
			self.__fulllogs.append(full_log)

			
	def get_roster_full_logs(self):
		# Filter down roster full logs using 
		#	- gamemode (determined by player numbers)
		# 	- player team alignment
		if len(self.__fulllogs) == 0:
			self.fetch_full_logs_from_minilogs()
		
		filtered = list[FullLog]
		for full_log in self.__fulllogs:
			# Check team sizes as an indication of gamemode
			if full_log.deviant_team_sizes():
				continue
			# Make sure rostered players are present on the same team
			player_presence = self.roster_presence_in_log(full_log)
			if player_presence['blue'] >= ROSTER_IDENTIFICATION_THRESHHOLD:
				filtered.append(full_log)
			if player_presence['red'] >= ROSTER_IDENTIFICATION_THRESHHOLD:
				filtered.append(full_log)
		
		# Use filtered fulllogs as our new fulllogs, discarding all others
		self.__fulllogs = filtered

	def roster_presence_in_log(self, full_log: FullLog) -> dict["blue":int,"red":int]:
		"""Returns how many of this roster's players
		are present on the red and blue team in the
		given log"""
		b_p_ids = full_log.blue_team_player_ids
		r_p_ids = full_log.red_team_player_ids
		# blue_team_player_count = len(b_p_ids)
		# red_team_player_count = len(r_p_ids)
		blue_team_roster_presence = len(p for p in self.players if p.id in b_p_ids)
		red_team_roster_presence = len(p for p in self.players if p.id in r_p_ids)
		return {
			"blue": blue_team_roster_presence,
			"red": red_team_roster_presence
		}


	def validate(self):
		# Assert all minilogs have a corresponding full log and vice versa
		# Assert all minilogs and logs occur within the league dates
		# Assert all matchups occur within the league dates
		# Etc
		pass


class PugTeam():
	""" A group of players who may or may not
	be registered on ozf. And who are present
	in one or potentially multiple logs"""
	def __init__(self):
		self.players= list[Union[OZFPlayer, NonOZFPlayer]]
		pass

