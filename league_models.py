from __future__ import annotations
from ast import Div
from codecs import backslashreplace_errors
from turtle import back
from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, DateTime, Boolean, Column, Table, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from sympy import true

# TODO change all mapped columns to just column()

# data models
class LeagueBase(DeclarativeBase):
	pass

class PlayerOnTeamInstance(LeagueBase):
	__tablename__ = "playeronteaminstance"
	player_id: Mapped[Integer] = mapped_column(Integer, ForeignKey("player.id_64"), primary_key=True)
	game_id: Mapped[Integer] = mapped_column(Integer, ForeignKey("game.game_id"), primary_key=True)
	roster_id: Mapped[Integer] = mapped_column(Integer, ForeignKey("roster.id"), primary_key=True)

class TeamInstance(LeagueBase):
	__tablename__ = "teaminstance"
	__table_args__ = (UniqueConstraint("game_id", "roster_id"),)

	game_id: Mapped[Integer] = mapped_column(Integer, ForeignKey("game.game_id"), primary_key=True)
	roster_id: Mapped[Integer] = mapped_column(Integer, ForeignKey("roster.id"), primary_key=True)
	# A null ozf team means its a merc team
	score : Mapped[Integer] = mapped_column(Integer)# score of THIS team

class PlayerOnRoster(LeagueBase):
	__tablename__ = "playeronroster"
	# player_ozf_id: Mapped[Integer] = mapped_column(Integer, ForeignKey("player.ozf_id"), primary_key=True)
	player_ozf_id: Mapped[Integer] = mapped_column(Integer, ForeignKey("player.ozf_id"), primary_key=True)
	roster_id: Mapped[Integer] = mapped_column(Integer, ForeignKey("roster.id"), primary_key=True)
	player_id_64: Mapped[Integer] = mapped_column(Integer, ForeignKey("player.id_64"))
	league_id: Mapped[Optional[Integer]] = mapped_column(Integer, ForeignKey("league.id"))
 
	player: Mapped[Player] = relationship("Player", foreign_keys=[player_ozf_id])
	roster: Mapped[Roster] = relationship("Roster")
	league: Mapped[League] = relationship("League")

	# def __init__(self, player_ozf_id, roster_id, league_id=None, player_id_64=None):
	# 	self.player_ozf_id=player_ozf_id
	# 	self.roster_id=roster_id
	# 	if league_id == None:
	# 		self.league_id = self.league.id
	# 	if player_id_64 == None:
	# 		self.player_id_64 = get_player_id64(player_ozf_id)

class Player(LeagueBase):
	__tablename__ = "player"
	id_64: Mapped[Integer] = mapped_column(Integer, primary_key=True)
	id3: Mapped[String] = mapped_column(String, unique=True, nullable=False)
	name: Mapped[String] = mapped_column(String, nullable=False)

	ozf_id: Mapped[int] = mapped_column(Integer, unique=True)
	
	def __eq__(self, other):
		if isinstance(other, Player):
			return self.id_64 == other.id_64
		return False
	def __hash__(self):
		return self.id_64
	def __str__(self):
		return f"""Player:\n\tName: {self.name}\n\tOZFID: {self.ozf_id}\n\tID_64: {self.id_64}\n\tID_3: {self.id3}\n"""

class Roster(LeagueBase):
	__tablename__ = "roster"

	id : Mapped[int] = mapped_column(Integer, primary_key=True) 
	name: Mapped[String] = mapped_column(String, nullable=False)
	# players = relationship(Player, back_populates="rosters")
	# ozf_league: Mapped["League"] = relationship()
	league_id: Mapped[Integer] = mapped_column(Integer, ForeignKey("league.id"))
	division_name : Mapped[String] = mapped_column(String, ForeignKey("division.name"))
	
	league: Mapped[League] = relationship("League")
	division: Mapped[Division] = relationship("Division", foreign_keys=[league_id,division_name])
	
	def __eq__(self, other):
		if isinstance(other, Roster):
			return self.id == other.id
		return False
	def __hash__(self):
		return self.id
	def __str__(self):
		return f"""Roster:\n\tName: {self.name}\n\tID: {self.id}\n\tLeague: {self.league_id}\n\tDIV: {self.division_name}\n"""

class League(LeagueBase):
	__tablename__ = "league"
	id : Mapped[Integer] = mapped_column(Integer, primary_key=True)
	name : Mapped[String] = mapped_column(String, nullable=False)
	start_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, default=None)
	end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, default=None)

class Division(LeagueBase):
	__tablename__ = "division"

	league_id: Mapped[Integer] = mapped_column(Integer, ForeignKey("league.id"), primary_key=True)
	name: Mapped[String] = mapped_column(String, primary_key=True)

class PlayerInLog(LeagueBase):
	__tablename__ = "playerinlog"
	player_id_64: Mapped[Integer] = mapped_column(Integer, ForeignKey("player.id_64"), primary_key=True)
	log_id: Mapped[Integer] = mapped_column(Integer, ForeignKey("log.id"), primary_key=True)
	player_ozf_id: Mapped[Optional[Integer]] = mapped_column(Integer, ForeignKey("player.ozf_id"), nullable=True)
	team_colour: Mapped[Optional[String]] = mapped_column(String)
	def __init__(self,player_id_64,log_id):
		self.player_id_64=player_id_64
		self.log_id=log_id

class PlayerLogTracker(LeagueBase):
	# Class for tracking what logs might be / are not missing from a player
	__tablename__ = "playerlogtracker"
	id_64 = Column(Integer, primary_key=True)
	num_logs_total = Column(Integer)
	num_logs_tracked = Column(Integer)
	valid_until = Column(DateTime)
	# When this info can no longer be considered trustworthy

	# earliest_log_id = Column(Integer, ForeignKey('log.id'),nullable=True)
	# earliest_log_tracked = relationship('Log')

	# latest_log_id = Column(Integer, ForeignKey('log.id'),nullable=True)
	# latest_log_tracked = relationship('Log')

# This class should be phased out
class LogSearchInfo(LeagueBase):
	__tablename__ = "logsearchinfo"
	id_64 = Column(Integer, primary_key=True)
	num_logs = Column(Integer)
	last_log_id = Column(Integer, ForeignKey('log.id'),nullable=True)
	last_log = relationship('Log')
	expiry_date = Column(DateTime)

class Log(LeagueBase):
	__tablename__ = "log"

	id : Mapped[Integer] = mapped_column(Integer, primary_key=True)
	date : Mapped[DateTime] = mapped_column(DateTime)
	map_name : Mapped[Optional[String]] = mapped_column(String)
	duration : Mapped[Optional[Integer]] = mapped_column(Integer)

	red_team_score: Mapped[Optional[Integer]] = mapped_column(Integer)
	blue_team_score: Mapped[Optional[Integer]] = mapped_column(Integer)
	
	# golden_cap : Mapped[Boolean] = mapped_column(Boolean)
	def __eq__(self, other):
		if isinstance(other, Log):
			return self.id == other.id
	def __hash__(self):
		return self.id
	def __str__(self):
		return self.id

class Official(LeagueBase):
	__tablename__ = "official"
	# __table_args__ = (UniqueConstraint("league_id", "round_number"),)

	id: Mapped[Integer] = mapped_column(Integer, primary_key=True)
	league_id: Mapped[Integer] = mapped_column(Integer, ForeignKey("league.id"), nullable=False)
	round_name: Mapped[String] = mapped_column(String)
	round_number: Mapped[Integer] = mapped_column(Integer)
	creation_date: Mapped[DateTime] = mapped_column(DateTime)

	home_team_id : Mapped[Optional[Integer]] = mapped_column(Integer, ForeignKey("roster.id"))
	away_team_id : Mapped[Optional[Integer]] = mapped_column(Integer, ForeignKey("roster.id"))

	home_team_score : Mapped[Optional[Integer]] = mapped_column(Integer)
	away_team_score : Mapped[Optional[Integer]] = mapped_column(Integer)

class Game(LeagueBase):
	"""For holding log info once all teams, rosters and players are created"""
	__tablename__ = "game" 

	official_id: Mapped[Optional[Integer]] = mapped_column(Integer, ForeignKey("official.id"))
	game_id: Mapped[Integer] = mapped_column(Integer, primary_key=True)
	# not a relationship or foreign key because we never
	# want to go back to accessing the full log once we've turned it into this
	# the full log should be deleted.
	map_name: Mapped[String] = mapped_column(String)
	date: Mapped[DateTime] = mapped_column(DateTime)
	duration: Mapped[Integer] = mapped_column(Integer) # maybe change this type
	# golden_cap: Mapped[Boolean] = mapped_column(Boolean)

