from db import league_engine
from sqlalchemy.orm import Session
from sqlalchemy import select
from league_models import Game, Log, Roster
from datetime import datetime
from database.methods import roster as roster_methods, log

def get_all_games():
	with Session(league_engine) as session:
		return set(session.query(Game).all())
def get_all_game_ids():
	with Session(league_engine) as session:
		return set(session.query(Game.game_id).all())

def get_game(game_id:int):
	with Session(league_engine) as session:
		return session.get(Game,game_id)
def insert_game_from_log(l:Log):
	with Session(league_engine) as session:
		if session.get(Game, l.id) is None:
			game = Game(
				game_id=l.id,
				map_name=l.map_name,
				date=l.date,
			)
			session.add(game)
			session.commit()

def create_all_games():
	with Session(league_engine) as session:
		existing_game_ids = session.query(Game.game_id).all()
		filtered_logs = session.query(Log).filter(Log.id not in existing_game_ids).all()
		new_games = set()
		for l in filtered_logs:
			new_games.add(Game(
				game_id=l.id,
				map_name=l.map_name,
				date=l.date,
			))
		session.add_all(new_games)
		session.commit()

# def generate_all_team_instances():
# 	with Session(league_engine) as session:
# 		for roster in session.query(Roster).all():
# 			players= roster_methods.get_player_on_rosters(roster.id)
# 			logs = log.get_logs_with_players(players, 4)

# 			pass
# 		for game in session.query(Game).all():
# 			pass

def update_game(game_id:int):
	with Session(league_engine) as session:
		pass