from datetime import datetime
from pprint import pprint
from log_filtration_variables import *

class MiniLog():
	"""A container for the simple log information given
	in batches by the search function of the logs.tf API """
	def __init__(self, json=None):

		self.id = int
		self.date = datetime

		if json != None:
			self.from_json(json)
		# self.game_mode
		# Double check exactly what info the minilogs contain

	def from_json(self,json: dict):
		""" Fill out information from API search response"""
		print("MiniLog JSON:")
		pprint(json)
		raise Exception
		pass

	def falls_within_dates(self, date1: datetime, date2: datetime) -> bool:
		"""Check if this log falls between two dates"""
		return (self.date > date1 and self.date < date2) or (self.date < date1 and self.date > date2)

class FullLog(MiniLog):
	"""A container for the more detailed log information given
	individually by the raw log data function of the logs.tf API
	
	This should only ever be used when it is not possible to use
	a Game object of some kind instead.
	"""
	def __init__(self):

		# self.game_mode
		self.red_team_player_ids = list[int]
		self.blue_team_player_ids = list[int]

		self.score = tuple[int,int]
		self.length = None
		print("parse time from json!!")

	def from_json(self, json: dict):
		""" Fill out information from API search response"""
		print("finish this")
		raise Exception
	
	def deviant_team_sizes(self):
		if len(self.red_team_player_ids) < MIN_TEAM_SIZE_THRESHHOLD:
			return True
		if len(self.blue_team_player_ids) < MIN_TEAM_SIZE_THRESHHOLD:
			return True
		if len(self.red_team_player_ids) >= MAX_TEAM_SIZE_THRESHHOLD:
			return True
		if len(self.blue_team_player_ids) >= MAX_TEAM_SIZE_THRESHHOLD:
			return True
		if len(self.blue_team_player_ids) + len(self.red_team_player_ids) > MAX_TOTAL_GAME_SIZE_THRESHHOLD:
			return True
		return False

def validate(log_object: MiniLog):
	if isinstance(log_object, MiniLog):
		# I'm not sure what to check for this?
		pass

	if isinstance(log_object, FullLog):
		pass
		## Switching out players causes this number to be wrong
		# assert len(log_object.red_team_player_ids) == 6
		# assert len(log_object.blue_team_player_ids) == 6

