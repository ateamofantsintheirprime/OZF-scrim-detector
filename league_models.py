from ast import Div
from codecs import backslashreplace_errors
from turtle import back
from sqlalchemy.inspection import inspect
from sqlalchemy import String, Integer, ForeignKey, DateTime, Boolean, Column, Table, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from pairing import pair

# TODO change all mapped columns to just column()

# data models
class LeagueBase(DeclarativeBase):
	pass

	def ident(self):
		return inspect(self).identity
	# def __hash__(self):
	# 	ident = self.ident()
	# 	h = ident[0] 
	# 	for key in ident[1:]: # iteratively apply cantor pairing
	# 		assert isinstance(key,Integer)
	# 		h = pair(h,key)
	# 	return h
	def __eq__(self, other):
		if type(self) == type(other):	
			return self.__hash__() == other.__hash__()
		return False			
	# def __str__(self):
	# 	for attr in inspect(self).attrs:

	# def __repr__(self):


class PlayerOnRoster(LeagueBase):
	__tablename__ = "playeronroster"

	# Foreign Keys
	player_id_64 = Column(Integer, ForeignKey("player.id_64"))
	player_ozf_id = Column(Integer, ForeignKey("player.ozf_id"), primary_key=True)
	roster_id = Column(Integer, ForeignKey("roster.id"), primary_key=True)
	league_id = Column(Integer, ForeignKey("league.id"), nullable=True)
 
	# Relationships
	player  = relationship("Player", foreign_keys=[player_ozf_id])
	roster = relationship("Roster")
	league  = relationship("League")

	# def __init__(self, player_ozf_id, roster_id, league_id=None, player_id_64=None):
	# 	self.player_ozf_id=player_ozf_id
	# 	self.roster_id=roster_id
	# 	if league_id is None:
	# 		self.league_id = self.league.id
	# 	if player_id_64 is None:
	# 		self.player_id_64 = get_player_id64(player_ozf_id)

class Player(LeagueBase):
	__tablename__ = "player"
	# Attributes
	id_64 = Column(Integer, primary_key=True)
	id3 = Column(String, unique=True, nullable=False)
	name = Column(String)
	ozf_id = Column(Integer, unique=True)
	
	# def __eq__(self, other):
	# 	if isinstance(other, Player):
	# 		return self.id_64 == other.id_64
	# 	return False
	# def __hash__(self):
	# 	return self.id_64
	def __str__(self):
		return f"""Player:\n\tName: {self.name}\n\tOZFID: {self.ozf_id}\n\tID_64: {self.id_64}\n\tID_3: {self.id3}\n"""
	def __repr__(self):
		return f"PLAYER({self.name},{self.id_64})"

class Roster(LeagueBase):
	__tablename__ = "roster"

	# Attributes
	id  = Column(Integer, primary_key=True) 
	name = Column(String, nullable=False)
	
	# Foreign Keys
	league_id = Column(Integer, ForeignKey("league.id"))
	division_name  = Column(String, ForeignKey("division.name"))
	
	# Relationships
	league = relationship("League")
	division = relationship("Division", foreign_keys=[league_id,division_name])
	
	# def __eq__(self, other):
	# 	if isinstance(other, Roster):
	# 		return self.id == other.id
	# 	return False
	def __hash__(self):
		return self.id
	def __str__(self):
		return f"""Roster:\n\tName: {self.name}\n\tID: {self.id}\n\tLeague: {self.league_id}\n\tDIV: {self.division_name}\n"""


class League(LeagueBase):
	__tablename__ = "league"

	# Attributes
	id  = Column(Integer, primary_key=True)
	name  = Column(String, nullable=False)
	start_date = Column(DateTime, nullable=True, default=None)
	end_date = Column(DateTime, nullable=True, default=None)

class Division(LeagueBase):
	__tablename__ = "division"

	# Attributes
	name = Column(String, primary_key=True)
	# Foreign Keys
	league_id = Column(Integer, ForeignKey("league.id"), primary_key=True)
	# Relationships
	league = relationship(League)

class PlayerInLog(LeagueBase):
	__tablename__ = "playerinlog"
	# Attributes
	team_colour = Column(String, nullable=True)
	
	# Foreign Keys
	player_id_64 = Column(Integer, ForeignKey("player.id_64"), primary_key=True)
	log_id = Column(Integer, ForeignKey("log.id"), primary_key=True)
	player_ozf_id = Column(Integer, ForeignKey("player.ozf_id"), nullable=True)

	# Relationships
	player = relationship(Player, foreign_keys=[player_id_64])
	log = relationship('Log')
	
	def __init__(self,player_id_64,log_id):
		self.player_id_64=player_id_64
		self.log_id=log_id

class PlayerLogTracker(LeagueBase):
	# Class for tracking what logs might be / are not missing from a player
	__tablename__ = "playerlogtracker"
	
	# Attributes
	num_logs_total = Column(Integer)
	num_logs_tracked = Column(Integer)
	valid_until = Column(DateTime)
	
	# Foreign Keys
	id_64 = Column(Integer, ForeignKey("player.id_64"), primary_key=True)

	# Relationships
	player = relationship(Player)

class Log(LeagueBase):
	__tablename__ = "log"

	# Attributes
	id  = Column(Integer, primary_key=True)
	date  = Column(DateTime)
	map_name  = Column(String, nullable=True)
	duration  = Column(Integer, nullable=True)

	red_team_score = Column(Integer, nullable=True)
	blue_team_score = Column(Integer, nullable=True)
	
	# def __eq__(self, other):
	# 	assert isinstance(other, Log)
	# 	return self.id == other.id
	# def __hash__(self):
	# 	return self.id
	def	link(self):
		return f"logs.tf/{self.id}"
	def __hash__(self):
		return self.id
	def __eq__(self,other):
		return self.id==other.id
	def __str__(self):
		return f"log: {self.id}"
	def __lt__(self,other):
		return self.id < other.id
	def __repr__(self):
		return f"LOG({self.id})"

class LogCandidate(LeagueBase):
	__tablename__ = "logcandidate"
	# Attributes
	player_names = Column(String)
	# Foreign Keys
	official_id = Column(Integer, ForeignKey('official.id'),primary_key=True)
	log_id = Column(Integer, ForeignKey('log.id'),primary_key=True)
	# Relationships
	official= relationship('Official',lazy="selectin")
	log = relationship('Log',lazy="selectin")

	def __str__(self):
		return f"log id: {self.log_id}, participants: {self.player_names}"
	def __hash__(self):
		return pair(self.log_id, self.official_id)

class Official(LeagueBase):
	__tablename__ = "official"
	# Attributes
	id = Column(Integer, primary_key=True)
	round_name = Column(String)
	round_number = Column(Integer)
	creation_date = Column(DateTime)
	bye  = Column(Boolean, nullable=True)
	forfeit  = Column(String, nullable=True)
	home_team_score  = Column(Integer, nullable=True)
	away_team_score  = Column(Integer, nullable=True)

	# Foreign Keys
	league_id = Column(Integer, ForeignKey("league.id"))
	home_team_id  = Column(Integer, ForeignKey("roster.id"), nullable=True)
	away_team_id  = Column(Integer, ForeignKey("roster.id"), nullable=True)

	# Relationships
	home_team=relationship("Roster",foreign_keys=[home_team_id],lazy="selectin")
	away_team=relationship("Roster",foreign_keys=[away_team_id],lazy="selectin")

	def __hash__(self):
		return self.id
	def __str__(self):
		if not self.home_team_id is None:
			h_team_s=f"{self.home_team.name} ({self.home_team.id})"
		else:
			h_team_s="None"
		if not self.away_team_id is None:
			a_team_s=f"{self.away_team.name} ({self.away_team.id})"
		else:
			a_team_s="None"
		return "\n\t".join([
			f"ID: {self.id}",
			f"Round: {self.round_number}",
			f"Date: {self.creation_date}",
			f"Home Team: {h_team_s}",
			f"Away Team: {a_team_s}",	
		])


class PlayerOnTeamInstance(LeagueBase):
	__tablename__ = "playeronteaminstance"

	# Foreign Keys
	player_id = Column(Integer, ForeignKey("player.id_64"), primary_key=True)
	game_id = Column(Integer, ForeignKey("game.game_id"), primary_key=True)
	roster_id = Column(Integer, ForeignKey("roster.id"), primary_key=True)

	# Relationships
	player = relationship('Player')
	game = relationship('Game')
	roster = relationship('Roster')

class TeamInstance(LeagueBase):
	__tablename__ = "teaminstance"
	__table_args__ = (UniqueConstraint("game_id", "roster_id"),)
	
	# Attributes
	score  = Column(Integer, nullable=True)# score of THIS team

	# Foreign Keys
	game_id = Column(Integer, ForeignKey("game.game_id"), primary_key=True)
	roster_id = Column(Integer, ForeignKey("roster.id"), primary_key=True)
	# A null ozf team means its a merc team

	# Relationships
	game = relationship('Game')
	roster = relationship('Roster')

class Game(LeagueBase):
	"""For holding log info once all teams, rosters and players are created"""
	__tablename__ = "game" 
	# Attributes
	game_id = Column(Integer, primary_key=True)
	map_name = Column(String)
	date = Column(DateTime)
	duration = Column(Integer, nullable=True) # maybe change this type

	# Foreign Keys
	official_id = Column(Integer, ForeignKey("official.id"), nullable=True)
	
	# Relationships
	official = relationship(Official)

