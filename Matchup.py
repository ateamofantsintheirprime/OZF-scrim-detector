from abc import ABC, abstractclassmethod
from datetime import datetime
from typing import Union

from Roster import OZFRoster, PugTeam
from Player import NonOZFPlayer
from Log import FullLog
from League import League

class BaseGameTemplate(ABC):
	"""Base Matchup, """
	def __init__(self):
		self.log = FullLog
		self.result = tuple[int]
		self.date = datetime
		self.map = str
	
	def from_log(self, log: FullLog):
		"""Given a log, fills out the values of the matchup"""
		self.log: FullLog = log
		print("fill out this function, process the log and fill out fields")
		raise Exception

class PugScrim(BaseGameTemplate):
	"""A matchup with exactly 1 identifiable ozfortress roster"""
	def __init__(self):
		self.team_alpha = Union[PugTeam, OZFRoster]
		self.team_beta = Union[PugTeam, OZFRoster]

class TeamGame(BaseGameTemplate):
	"""A matchup with exactly 2 identifiable ozfortress rosters.
	A TeamGame instance means it's a scrim, if its being instantiated
	as an official, then it's an ozfortress official.
	
	This should essentially be treated as a scrim object, the only
	issue is that I don't want to imply (yet) that an official is
	a type of scrim. Although maybe I should."""
	def __init__(self):
		self.team_alpha = OZFRoster
		self.team_beta = OZFRoster

		self.alpha_mercs = list[NonOZFPlayer]
		self.beta_mercs = list[NonOZFPlayer]

		self.parent_league: League

class ScrimGroup():
	"""A group of 1 or more scrim / pugscrim games collectively
	comprising a single group of scrims between the same two teams
	on the same night.
	
	These are usually in groups of 2 and usually do not have many
	player changes between maps / games
	
	This may or may not be used"""
	pass

class OfficialGame(TeamGame):
	"""One map/game among multiple, as part of an
	ozfortress official match."""
	def __init__(self):
		self.parent_official = OfficialSeries
		self.golden_cap = bool

class OfficialSeries():
	"""An ozfortress official match, comprised of
	one or more games, associated with its own id
	and matchpage.
	
	Note: An offical match is fundamentally different
	to a pug or a scrim, because it is comprised of
	multiple games."""
	def __init__(self):

		self.official_name = str
		self.official_id = int
		self.round_number = int
		self.created_at : datetime
		self.parent_league = League

		self.home_team = OZFRoster
		self.away_team = OZFRoster

		self.home_team_mercs = list[NonOZFPlayer]
		self.away_team_mercs = list[NonOZFPlayer]

		self.number_of_games = int
		self.games = list[OfficialGame]

		self.maps # Given by the ozf api, must be checked against the maps of the games, which is given by the logs api

		pass

	def fetch_official_data(self):
		"""Request official match information from the ozfortress API"""
		# Should give us maps
		pass

	def find_potential_game_logs(self) -> list[FullLog]:
		"""Try and find the logs of the games for this series
		Filter by date estimates, maps, players. 
		Beware of extensions, player transfers, map versions"""
		pass