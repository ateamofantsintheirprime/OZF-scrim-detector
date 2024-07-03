from db import league_engine
from sqlalchemy.orm import Session
from sqlalchemy import select
from league_models import Game, Log, Roster, MercTeam
from datetime import datetime, timedelta
from database.methods import roster as roster_methods, log

def delete_all_games():
	with Session(league_engine) as session:
		session.query(Game).delete()
		session.query(MercTeam).delete()
		print("deleting all games and merc teams")
		session.commit()

def get_all_games():
	with Session(league_engine) as session:
		return set(session.query(Game).all())
def get_all_game_ids():
	with Session(league_engine) as session:
		return set(session.execute(select(Game.game_id)).scalars().fetchall())

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

def update_game(game_data:dict):
	red_score = game_data['red_score']
	blue_score = game_data['blue_score']
	red_player_ids = game_data['red_player_ids']
	blue_player_ids = game_data['blue_player_ids']

	with Session(league_engine) as session:
		game = session.get(Game,game_data['id'])
		if len(game_data['red_player_ids']) + len(game_data['blue_player_ids']) < 12:
			print("non-sixes game", game_data['id'])
		if game is None:
			game = Game(game_id=game_data['id'],
			   map_name=game_data['map_name'],
			   duration = game_data['duration'],
			   date = game_data['date'])
			session.add(game)
		else:
			game.map_name = game_data['map_name']
			game.duration = game_data['duration']
			game.date = game_data['date']
		# session.commit()
		merc_team1 = session.query(MercTeam).filter_by(colour="red", game_id=game_data['id']).one_or_none()
		if merc_team1 is None:
			red_team_placeholder = MercTeam(
				player_ids="$".join(red_player_ids),
				score=red_score,
				colour="red",
				game_id=game_data['id']
			)
			session.add(red_team_placeholder)
		merc_team2 = session.query(MercTeam).filter_by(colour="blue", game_id=game_data['id']).one_or_none()
		if merc_team2 is None:
			session.add(red_team_placeholder)
			session.commit()
			blue_team_placeholder = MercTeam(
				player_ids="$".join(blue_player_ids),
				score=blue_score,
				colour="blue",
				game_id=game_data['id']
			)
			session.add(blue_team_placeholder)
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
