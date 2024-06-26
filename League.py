import os.path, config
import datetime
from datetime import datetime, timedelta
from pprint import pprint
from Data import request_safe
from Roster import Roster, PugTeam 
from Player import OZFPlayer, NonOZFPlayer
from Matchup import PugScrim, TeamGame, OfficialGame, OfficialSeries

"""I'm honestly starting to think that I should just use an
SQL library to run a database here. This is probably going to be
a waste of time to do this semi-database thing"""

class League():
	"""Also called a season of ozfortress"""
	def __init__(self, id):
		self.id: int = id
		self.name: str

		self.start_date: datetime = None
		self.end_date: datetime = None

		"""The private variables are usually just used for construction.
		They can be used if we don't want to bother requesting all the
		details of the league. 
		
		If we are going to request more information than just fetch_league_data()
		then these should NOT be accessed, and instead the info should be
		retrieved from other members / the children of those members"""
		# but can be used if only a little bit of info on the league is needed
		self.__data_fetched = False
		self.__roster_ids: list[int]
		self.__roster_names: list[str]
		self.__match_dates: list[datetime]
		self.__match_ids: list[int]


		# Child variables, contain eachother
		self.ozf_players: list[OZFPlayer]
		self.non_ozf_players: list[NonOZFPlayer] # This probably wont be of much use aside from bug testing
		self.rosters: list[Roster]
		# self.pug_teams: list[PugTeam] ???  do we want to track all the pug teams?? prob not??
		self.divisions #??? TODO typehint this
		self.team_games: list[TeamGame]
		self.pug_scrims: list[PugScrim]
		self.official_games: list[OfficialGame]
		self.official_series: list[OfficialSeries]

	### GETTING THE DATA ==============

	def fetch_league_data(self):
		"""The reply to this contains:
			- league id
			- league name
			- description
			- rosters (id, team_id, name, division)
			- matches (id, sstatus, name, round_number, creation date)
		"""
		assert not self.__data_fetched
		print(f"Requesting league data, id: {self.id}")
		
		# Fetch data
		cache_filepath = os.path.join(config.league_response_cache, str(self.id) + ".json")
		url = os.path.join(config.ozf_url_prefix, "leagues/", str(self.id))
		raw_league_data = request_safe(cache_filepath, url, config.headers)["league"]
		self.__data_fetched = True

		assert raw_league_data['id'] == self.id
		
		# Clean up data
		rst = raw_league_data['rosters']
		mtch = raw_league_data['matches']

		self.__roster_ids = [r['id'] for r in rst]
		self.__roster_names = [r['name'] for r in rst]
		self.__match_ids = [m['id'] for m in mtch]
		self.__match_dates = [datetime.fromisoformat(m['created_at']) for m in mtch]
		self.name = raw_league_data['name']
		self.divisions = set([r['division'] for r in rst])

	def construct_league(self):
		"""Fetch all data related to all players, rosters, and officials
		Instantiate all child objects and fetch all of their data recursively"""
		if not self.__data_fetched:
			# raw_data = self.fetch_league_data()
			
			# construct_matches(raw_data['matches'])

			self.estimate_dates()
			self.get_all_rosters()
			self.get_all_officials()


	# NOTE: we actually get all the player data that we use from ozf 
	# With the roster data call. TODO: investigate what the api gives us
	# If we request player data.


	def get_all_rosters(self):
		"""Request roster information for all ozf rosters and build roster objects
		The reply to a roster request contains:
			- roster id
			- team id
			- roster name
			- desription
			- division
			- players (id, name, steam_ids)
		"""
		assert len(self.__roster_ids) != 0
		for id in self.__roster_ids:
			# Fetch roster data
			print(f"Requesting roster data, id: {id}")
			cache_filepath = os.path.join(config.roster_response_cache, str(self.id) + ".json")
			url = os.path.join(config.ozf_url_prefix , "rosters/", str(self.id))
			raw_roster_data = request_safe(cache_filepath, url, config.headers)["roster"]
			
			assert raw_roster_data['id'] == id

			# Construct Roster
			roster = Roster()
			roster.from_json(raw_roster_data)

			for raw_player_data in raw_roster_data['players']:
				# Construct each player
				player = OZFPlayer()
				player.from_json(raw_player_data)

				# Add each player to roster
				roster.players.append(player)
				# Add each player the league
				self.ozf_players.append(player)

			# Add roster to league
			self.rosters.append(roster)

	def get_all_officials(self):
		"""Request official match information for all officials
		and construct official series objects"""
		assert len(self.__match_ids) != 0
		for id in self.__match_ids:
			print(f"Requesting match data, id: {id}")
			cache_filepath = os.path.join(config.roster_response_cache, str(self.id) + ".json")
			url = os.path.join(config.ozf_url_prefix , "rosters/", str(self.id))
			raw_roster_data = request_safe(cache_filepath, url, config.headers)["roster"]
			pprint(raw_roster_data)
			raise Exception

	# ANALYSING DATA FROM APIS

	def construct_matchups(self):
		"""Go through team logs and identify when two teams are playing
		against eachother or when a team is playing against a pug team"""
		pass

	def identify_official_candidates(self):
		"""Try and identify what games could be two teams playing thier official."""
		pass

	def estimate_dates(self):
		"""Attempt to estimate the period of time that the league spans"""
		assert len(self.__match_dates) != 0
		raise Exception
		pass