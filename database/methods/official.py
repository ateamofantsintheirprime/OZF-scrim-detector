from db import league_engine
from sqlalchemy.orm import Session
from league_models import LogCandidate, Official, League, Log
from database.methods import roster, log
from typing import Union
from datetime import datetime, timedelta

def get_official(id:int) -> Official:
	with Session(league_engine) as session:
		return session.get(Official, id)

def insert_official(id:int, r_name:str, r_number:int, c_date:datetime, league_id:int):
	with Session(league_engine) as session:
		assert not session.get(League, league_id) is None
		if session.get(Official, id) is None:
			official = Official(
				id=id,
				round_name=r_name,
				round_number=r_number,
				creation_date=c_date,
				league_id=league_id)
			session.add(official)
			session.commit()

def update_official(id:int, home_team_id:int, forfeit:str,bye:bool, away_team_id:int=None):
	with Session(league_engine) as session:
		official= session.get(Official, id)
		assert not official is None
		official.home_team_id=home_team_id
		official.bye=bye
		if not bye:
			official.away_team_id=away_team_id
		official.forfeit=forfeit
		session.commit()
	# TODO this
	pass

def get_player_ids(official:Union[int,Official]):
	with Session(league_engine) as session:
		if isinstance(official,int):
			official=session.get(Official, official)
		elif isinstance(official,Official):
			official=official # lol
		else:
			raise Exception
		return roster.get_roster_player_ids(official.home_team_id).\
			union(roster.get_roster_player_ids(official.away_team_id))

def get_candidate_logs(official_id:int) -> list[Log]:
	with Session(league_engine) as session:
		# return set(session.query(Log).join(LogCandidate).\
		# 	filter(LogCandidate.official_id==official_id))
		return session.query(LogCandidate).order_by(LogCandidate.log_id).\
			filter(LogCandidate.official_id==official_id).all()


def create_candidate_logs(official:Union[int,Official], date_range:int=14):
	with Session(league_engine) as session:
		if isinstance(official,int):
			official=session.get(Official, official)
		elif isinstance(official,Official):
			official=official # lol
		else:
			raise Exception
		with Session(league_engine) as session:
			players_ids_to_look_for = roster.get_roster_player_ids(official.home_team_id).\
				union(roster.get_roster_player_ids(official.away_team_id))
			log_dicts = log.get_logs_with_players(players_ids_to_look_for,8)
			
			# print(f"prefiltered len: {len(log_dicts)}")
			filtered = []
			for dict in log_dicts:
				if dict['log'].date > official.creation_date - timedelta(days=date_range)\
				and dict['log'].date < official.creation_date + timedelta(days=date_range):
					# print(f"{dict['log'].date} falls between {official.creation_date - timedelta(days=date_range)} and {official.creation_date + timedelta(days=date_range)}")
					filtered.append(dict)

			for dict in filtered:
				# print(l)
				if session.get(LogCandidate,(official.id,dict['log'].id)) is None:
					log_candidate = LogCandidate(
						official_id=official.id,
						log_id=dict['log'].id,
						player_names=", ".join(p.name for p in dict['players'])
					)
					session.add(log_candidate)
			session.commit()