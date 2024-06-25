from datetime import datetime
from pprint import pprint

# These can probably be a subclass-superclass situation
class MiniLog():
	def __init__(self, mini_log_data):
		"""Can be requested in batches, used to do preliminary
		culling or trimming of the list of logs played by a team"""
		self.id = mini_log_data["id"]
		self.date = datetime.fromtimestamp(mini_log_data["date"]).replace(tzinfo=None)

	def falls_within_dates(self, date1, date2):
		# print(f"Testing date: {self.date}")
		# print(f"date1: {date1}")
		# print(f"date2: {date2}")
		# print(f"self.date > date1 and self.date < date2: {self.date > date1 and self.date < date2}")
		# print(f"self.date < date1 and self.date > date2: {self.date < date1 and self.date > date2}")
		return self.date > date1 and self.date < date2 or self.date < date1 and self.date > date2

class FullLog():
	def __init__(self, log_data, id):
		"""going to be used to store the full log data in the db"""
		self.id = id
		self.date = datetime.fromtimestamp(log_data["info"]["date"]).replace(tzinfo=None)
		self.red_team = []
		self.blue_team = []
		self.score = (log_data["teams"]["Red"]["score"],
					  log_data["teams"]["Blue"]["score"])
		self.get_teams(log_data)

	def get_teams(self, log_data):
		player_dict = log_data["players"]
		player_ids = log_data["players"].keys()
		print("log player data: ")
		pprint(log_data["players"])
		self.red_team = [id[1:-1] for id in player_ids if player_dict[id]["team"] == "Red"]
		self.blue_team = [id[1:-1] for id in player_ids if player_dict[id]["team"] == "Blue"]
		