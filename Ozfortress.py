from League import League
from Player import OZFPlayer
from Roster import OZFRoster

class Ozfortress():
	def __init__(self):
		self.leagues : list[League]
		self.players : list[OZFPlayer]
		self.rosters : list[OZFRoster]
		#self.teams # different to rosters