from db import league_engine

from sqlalchemy.orm import Session, column_property
from sqlalchemy import func, select
from sqlalchemy.sql import label
from league_models import Log, Player, PlayerInLog, PlayerLogTracker
from datetime import datetime
from typing import Union

def get_log(log_id:int) -> Log:
	with Session(league_engine) as session:
		return session.get(Log, log_id)

def get_all_logs() -> set[Log]:
	with Session(league_engine, expire_on_commit=False) as session:
		return set(session.execute(select(Log)).scalars().fetchall())

def get_all_log_ids() -> set[int]:
	with Session(league_engine) as session:
		return set(session.execute(select(Log.id)).fetchall())

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
		assert not session.get(Player,player_id_64) is None
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
		assert not session.get(Player,player_id_64) is None
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

def get_logs_with_players(players:set[Union[Player,int]], threshold:int) -> dict:
	with Session(league_engine) as session:
		assert len(players)>0
		if isinstance(list(players)[0],Player):
			player_ids = {p.id_64 for p in players}
		elif isinstance(list(players)[0],int):
			player_ids=players
		stmt = \
			select(\
				Log,\
				func.count(PlayerInLog.player_id_64),\
				func.group_concat(Player.id_64 ,', ').label("players")\
			).join(\
				PlayerInLog, PlayerInLog.log_id==Log.id)\
			.join(Player, Player.id_64==PlayerInLog.player_id_64)\
			.filter(Player.id_64.in_(player_ids))\
			.group_by(Log.id)\
			.having(func.count(PlayerInLog.player_id_64) >= threshold)\
			.order_by(-func.count(PlayerInLog.player_id_64))
		result = session.execute(stmt).fetchall()
		formatted = [
			{
				'log' : res[0],
				'count' : res[1],
				'players' : [
						session.get(Player,int(p_id))
						for p_id in res[2].split(", ")
					]
			}
			for res in result
		]
		return formatted