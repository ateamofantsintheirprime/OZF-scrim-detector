from db import league_engine
from sqlalchemy.orm import Session
from league_models import Log, Player, PlayerInLog, PlayerLogTracker
from datetime import datetime

def get_log(log_id:int) -> Log:
	with Session(league_engine) as session:
		return session.get(Log, log_id)

def get_all_logs() -> set[Log]:
	with Session(league_engine) as session:
		return set(session.query(Log).all())

def get_all_log_ids() -> set[int]:
	with Session(league_engine) as session:
		return {l.id for l in session.query(Log).all()}
	# TODO fix this 


def insert_log(log_id:int, date:datetime):
	with Session(league_engine) as session:
		if session.get(Log, log_id) is None:
			log = Log(id=log_id, date=date)
			session.add(log)
			session.commit()

# =================================

def add_player_to_log(player_id_64:int, log_id:int):
	with Session(league_engine) as session:
		if len(session.query(PlayerInLog).filter_by(player_id_64=player_id_64,log_id=log_id).all()) ==0:
			player_in_log = PlayerInLog(player_id_64=player_id_64,log_id=log_id)
			session.add(player_in_log)
			session.commit()

def add_player_to_log_batch(player_id_64:int, logs:set[Log]):
	with Session(league_engine) as session:
		assert session.get(Player,player_id_64) != None
		# log_ids = [l.id for l in logs]

		player_in_log_list = [
			PlayerInLog(player_id_64=player_id_64,
			   log_id=l.id)
			for l in logs
		]
		session.add_all(player_in_log_list)
		session.commit()

def add_player_to_log_batch_id(player_id_64:int, log_ids:list[int]):
	with Session(league_engine) as session:
		assert session.get(Player,player_id_64) != None
		# log_ids = [l.id for l in logs]

		player_in_log_list = [
			PlayerInLog(player_id_64=player_id_64,
			   log_id=id)
			for id in log_ids
		]
		session.add_all(player_in_log_list)
		session.commit()

def add_log_batch(logs:set[Log]):
	with Session(league_engine) as session:
		session.add_all(logs)
		session.commit()
