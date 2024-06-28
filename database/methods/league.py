from db import league_engine
from sqlalchemy.orm import Session
from sqlalchemy import select
from league_models import League, Official, Roster, Player, PlayerOnRoster
from datetime import timedelta, datetime

def get_league(id:int) -> League:
	with Session(league_engine) as session:
		return session.get(League, id)
	
def insert_league(id:int, name:str):
	with Session(league_engine) as session:
		if session.get(League, id) is None:
			print(id, name)
			league = League(id=id, name=name)
			session.add(league)
			session.commit()

def update_league():
	# TODO
	pass

# =================================

def estimate_league_dates(league_id:int):
	with Session(league_engine) as session:
		league = session.get(League, league_id)
		officials = get_league_officials(league_id=league_id)

		dates = [o.creation_date for o in officials]
		first = min(dates)
		last = max(dates)

		start_leeway = 10
		end_leeway = 14

		league.start_date = first - timedelta(days=start_leeway)
		league.end_date = last + timedelta(days=end_leeway)

		session.commit()

	
def within_season_duration(league_id:int, date:datetime):
	with Session(league_engine) as session:
		league = session.get(League,league_id)
		return league.start_date < date and league.end_date > date


# =================================

def get_league_officials(league_id:int) -> list[Official]:
	with Session(league_engine) as session:
		return session.query(Official).filter_by(league_id=league_id).all()

def get_league_rosters(league_id:int) -> list[Roster]:
	with Session(league_engine) as session:
		return session.query(Roster).filter_by(league_id=league_id).all()

def get_league_players(league_id:int) -> set[Player]:
	with Session(league_engine) as session:
		return set(session.query(Player).\
			join(PlayerOnRoster, Player.ozf_id==PlayerOnRoster.player_ozf_id).\
			join(Roster).join(League).filter_by(id=league_id).all())

def get_league_player_id_64s(league_id:int) -> set[int]:
	with Session(league_engine) as session:
		result = session.execute(select(Player.id_64)).scalars().all()
		return set(result)

def get_league_player_ozf_ids(league_id:int) -> set[int]:
	with Session(league_engine) as session:
		return set(session.query(Player.ozf_id).\
			join(PlayerOnRoster, Player.ozf_id==PlayerOnRoster.player_ozf_id).\
			join(Roster).join(League).filter(League.id==league_id).scalars().all())
