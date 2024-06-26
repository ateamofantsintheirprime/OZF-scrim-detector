from abc import ABC, abstractclassmethod
from Roster import Roster
from Matchup import TeamGame, OfficialGame, OfficialSeries, PugScrim, BaseGameTemplate
from Log import FullLog, MiniLog
from typing import Union
from Data import request_safe
import os, config

class BasePlayerTemplate(ABC):
	"""The base template for a player. They have a name
	and steamID and logs and stuff"""
	def __init__(self):
		self.name : str = ""
		self.id3 : str = ""
		self.id64 : str = "" 
		self.__fulllogs : list[FullLog]
		## WARNING, DO NOT EDIT __fulllogs DIRECTLY, BE VERY CAREFUL
		## TO MAINTAIN DATA CONSISTENCY WITH ALL OTHER GAME/ MATCHUP DATA
		## ASSOCIATED WITH THE PLAYER

		self.minilogs : list[MiniLog]
		self.pugscrims : list[PugScrim]

		self.mercing : dict[
			"team_games" : list[TeamGame],
			"official_games" : list[OfficialGame],
			"official_series" : list[OfficialSeries]]
		"These games should have zero overlap with any other sets of games"

	def get_full_logs(self) -> list[FullLog]: return self.__fulllogs

	def fetch_all_minilogs(self, force = False):
		"""Requests limited info on each and every log
		in which this player is present. Can be requested
		from Logs.tf API in batches."""
		if not force:
			assert len(self.minilogs) == 0

		self.minilogs = list[MiniLog]
		
		# We may not get every single minilog in one request, so we do a loop
		done = False
		total = 0
		while not done:
			offset = 0
			# Make one request
			cache_filepath = os.path.join(config.player_log_search_cache, f"id{self.id64}" + f"off{offset}" + ".json")
			url = config.logs_url_prefix + f"?player={self.id64}&offset={offset}"
			raw_minilog_data = request_safe(cache_filepath, url)
			total = raw_minilog_data['total']

			# Check if we're done
			if raw_minilog_data['results']+offset == total:
				done = True
			offset += raw_minilog_data['results']

			# Add the data from the request to the list of minilogs
			self.minilogs.extend([MiniLog(log) for log in raw_minilog_data['logs']])
		
		assert len(self.minilogs) == total

	def fetch_all_fulllogs(self):
		"""Requests more expansive info on each log in
		which this player is present. Cannot be requested 
		from the API in batches. This function should not
		be used on large numbers of players."""
		pass

	@abstractclassmethod
	def get_logs(self):
		"""Gets a list of logs across the player's games"""
		pass

	def get_shared_logs(self, other_player: Union['NonOZFPlayer', 'OZFPlayer']) -> dict[str:list[FullLog],str:list[MiniLog]]:
		"""Get all logs in the database which feature these two players"""
		shared_full_logs : list[FullLog] = []
		shared_mini_logs : list[MiniLog] = []
		# Fill out these lists
		return {
			"shared_full_logs" : shared_full_logs,
			"shared_mini_logs" : shared_mini_logs
		}


class NonOZFPlayer(BasePlayerTemplate):
	"""The exact set of all players who are ever seen by the system
	who are not known to be associated with an ozf account"""
	def __init__(self):
		pass

	def get_games(self):
		"""Return the games where this player has been on a
		pugteam as well as the games where this player was
		mercing for a different kind of team."""
		pass

	def check_for_ozf_account(self) -> bool:
		"""Check if there is an ozfortress account associated
		with this players' steamID. This should only be used
		for sanity checks, it is costly.
		
		If you want to attempt to turn a NonOZFPlayer into an
		OZFPlayer, use to_OZFPlayer()"""
		pass

	def from_json(self, json:dict):
		pass
	
	def to_OZFPlayer(self):
		ozf_player = OZFPlayer()
		ozf_player.name = self.name
		ozf_player.id3 = self.id3
		ozf_player.id64 = self.id64
		print("this function isnt done")
		raise Exception

class OZFPlayer(BasePlayerTemplate):
	def __init__(self):
		self.ozfid : int
		self.rosters: list[Roster] = []
		self.official_games: list[OfficialSeries] = []
		self.official_series: list[OfficialSeries] = []

	def from_json(self, json: dict):
		self.ozfid = json["id"]
		self.id64 = json["steam_64_str"]
		self.id3 = json["steam_id3"]
		self.name = json["name"]

		# Note this doesnt fill out roster or game data

	def fetch_info_with_id3(self):
		assert len(self.id3) < 5 # random length reqiurement to make sure id3 isnt empty or smth
		""" Make a request to the ozf api with ip3
		and fill out variables"""
		print("not done")
		raise Exception

	def get_games(self, flags: dict["official_games": bool,"team_games":bool,"pugscrims":bool,"mercing":bool]) -> dict:
		"""Return all kind of games featuring this player
		in a dict"""
		pugscrims = list[PugScrim]
		# this ozf player playing on a pugteam against another ozf roster
		rostered_games: dict[
			"r_pugscrims" : list[PugScrim], 
			# this ozf player's roster vs a pugteam
			"r_team_games" : list[TeamGame], 
			# this ozf player's roster vs another ozf roster
			"r_official_games": list[OfficialGame], 
			# this ozf player's official game against another ozf roster
		]
		mercing_games: dict[
			"m_pugscrims" : list[PugScrim], 
			# this ozf player mercing for another ozf roster vs a pugteam
			"m_team_games" : list[TeamGame], 
			# this ozf player mercing for another ozf roster vs a third ozf roster
			"m_official_games": list[OfficialGame], 
			# this ozf player mercing for another ozf roster in an official game against a third ozf roster
		]
		return {
			"pugscrims" : pugscrims,
			"rostered_games" : rostered_games,
			"mercing_games" : mercing_games
		}

	
	def get_officials(self, roster_id=None, season_id=None, mercing=False) -> list[OfficialGame]:
		""" Get all officials played by this player, can
		be filtered by the roster they were a part of during
		the official, or the season the official was a part
		of. Can specify mercing to control whether or not
		we should make sure the player is rostered on to 
		the team they're playing for on ozf for that season."""
		pass

def validate(player: BasePlayerTemplate):
	"""The validate functions exist as sanity checks that
	all the data in the system in consistent. 
	
	For example the if we have a object 'ants' who is a subclass of BasePlayerTemplate:
		ants.get_full_logs()
		[game.log for game in ants.all_games]
	These two lines should return the exact same information
	"""
	if issubclass(player, BasePlayerTemplate):
		assert player.get_full_logs() == [game.log for game in player.get_games()]

	if isinstance(player, OZFPlayer):
		assert player.official_games == [game for series in player.official_series for game in series.games]

	if isinstance(player, NonOZFPlayer):
		# A NonOZFPlayer by definition should not have an ozf account (that we know of so far)
		assert not player.check_for_ozf_account()

	# Add more sanity checks here as needed