'''
models
defines sql alchemy data models
also contains the definition for the room class used to keep track of socket.io rooms

Just a sidenote, using SQLAlchemy is a pain. If you want to go above and beyond, 
do this whole project in Node.js + Express and use Prisma instead, 
Prisma docs also looks so much better in comparison

or use SQLite, if you're not into fancy ORMs (but be mindful of Injection attacks :) )
'''

from __future__ import annotations
from ast import Div
from codecs import backslashreplace_errors
from turtle import back
from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, DateTime, Boolean, Column, Table, UniqueConstraint, ARRAY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from sympy import true

# data models
class Base(DeclarativeBase):
    pass

class PlayerOnTeamInstance(Base):
    __tablename__ = "playeronteaminstance"
    player_id: Mapped[Integer] = mapped_column(Integer, ForeignKey("player.id_64"), primary_key=True)
    game_id: Mapped[Integer] = mapped_column(Integer, ForeignKey("game.game_id"), primary_key=True)
    roster_id: Mapped[Integer] = mapped_column(Integer, ForeignKey("roster.id"), primary_key=True)

class TeamInstance(Base):
    __tablename__ = "teaminstance"
    __table_args__ = (UniqueConstraint("game_id", "roster_id"),)

    game_id: Mapped[Integer] = mapped_column(Integer, ForeignKey("game.game_id"), primary_key=True)
    roster_id: Mapped[Integer] = mapped_column(Integer, ForeignKey("roster.id"), primary_key=True)
    # A null ozf team means its a merc team
    # player_ids = Column(ARRAY(Integer)) # Players present in the game, may differ somewhat from ozf roster
    score : Mapped[Integer] = mapped_column(Integer)# score of THIS team

class PlayerOnRoster(Base):
    __tablename__ = "playeronroster"
    player_ozf_id: Mapped[Integer] = mapped_column(Integer, ForeignKey("player.ozf_id"), primary_key=True)
    roster_id: Mapped[Integer] = mapped_column(Integer, ForeignKey("roster.id"), primary_key=True)
    league_id: Mapped[Optional[Integer]] = mapped_column(Integer, ForeignKey("league.id"))

class Player(Base):
    __tablename__ = "player"
    id_64: Mapped[String] = mapped_column(String, primary_key=True)
    id3: Mapped[String] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[String] = mapped_column(String, nullable=False)

    ozf_id: Mapped[int] = mapped_column(Integer, unique=True)

class Roster(Base):
    __tablename__ = "roster"

    id : Mapped[int] = mapped_column(Integer, primary_key=True) 
    name: Mapped[String] = mapped_column(String, nullable=False)
    # players = relationship(Player, back_populates="rosters")
    # ozf_league: Mapped["League"] = relationship()
    league_id: Mapped[Integer] = mapped_column(Integer, ForeignKey("league.id"))
    division_name : Mapped[String] = mapped_column(String, ForeignKey("division.name"))

class League(Base):
    __tablename__ = "league"
    id : Mapped[Integer] = mapped_column(Integer, primary_key=True)
    name : Mapped[String] = mapped_column(String, nullable=False)

    # OPTIONAL BELOW HERE (FILLED IN AFTER FIRST INSERTION)
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, default=None)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, default=None)

class Division(Base):
    __tablename__ = "division"

    league_id: Mapped[Integer] = mapped_column(Integer, ForeignKey("league.id"), primary_key=True)
    name: Mapped[String] = mapped_column(String, primary_key=True)

class PlayerInLog(Base):
    __tablename__ = "playerinlog"
    player_id_64: Mapped[Integer] = mapped_column(Integer, ForeignKey("player.id_64"), primary_key=True)
    log_id: Mapped[Integer] = mapped_column(Integer, ForeignKey("log.id"), primary_key=True)
    player_ozf_id: Mapped[Integer] = mapped_column(Integer, ForeignKey("player.ozf_id"), nullable=True)
    team_colour: Mapped[Optional[String]] = mapped_column(String)

class Log(Base):
    __tablename__ = "log"

    id : Mapped[Integer] = mapped_column(Integer, primary_key=True)
    date : Mapped[DateTime] = mapped_column(DateTime)
    map_name : Mapped[Optional[String]] = mapped_column(String)
    duration : Mapped[Optional[Integer]] = mapped_column(Integer)

    red_team_score: Mapped[Optional[Integer]] = mapped_column(Integer)
    blue_team_score: Mapped[Optional[Integer]] = mapped_column(Integer)
    
    # golden_cap : Mapped[Boolean] = mapped_column(Boolean)

class Official(Base):
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

class Game(Base):
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

