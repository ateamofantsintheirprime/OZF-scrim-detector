from League import League
from Player import OZFPlayer
from Roster import Roster

class Ozfortress():
	def __init__(self):
		self.leagues : list[League]
		self.players : list[OZFPlayer]
		self.rosters : list[Roster]
		#self.teams # different to rosters