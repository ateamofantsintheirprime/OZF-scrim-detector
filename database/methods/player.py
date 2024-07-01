from db import league_engine
from sqlalchemy.orm import Session
from sqlalchemy import select
from league_models import Player, PlayerInLog, Log, PlayerLogTracker
from typing import Union

def get_player_id64(ozf_id:int) -> int:
	with Session(league_engine) as session:
		return session.query(Player).filter(ozf_id=ozf_id).one_or_none()

def get_player(identifier) -> Player:
	with Session(league_engine) as session:
		if isinstance(identifier,int):
			return session.get(Player, identifier)
		if isinstance(identifier,str):
			return session.query(Player).filter_by(name=identifier).one_or_none()
		print("Provide player id_64 or ozf_id please")
		raise Exception

def insert_player(id_64:int, id3:int, name:str, ozf_id:int=None):
	with Session(league_engine) as session:
		if session.get(Player, id_64) is None:
			player = Player(id_64=id_64, id3=id3, name=name, ozf_id=ozf_id)
			session.add(player)
			session.commit()

def update_player(id_64:int, id3:int, name:str, ozf_id:int=None):
	with Session(league_engine) as session:
		# If player is not in the database, insert them
		player = session.get(Player, id_64)
		if player is None:
			insert_player(id_64=id_64, id3=id3, name=name, ozf_id=ozf_id)
		elif player.ozf_id != ozf_id:
			print("Warning, we currently do not support changing player ID_64 or OZF_ID. Make sure these match")
			raise Exception
		elif player.id3 != id3 or player.name != name:
			# Only commit if changes were made
			player.id3 = name
			player.name = name
			session.commit()
		else:
			print("no changes made to player")

# =============================

# TODO MAYBE DONT NEED THIS
def get_player_log_ids(player_id_64:int=None, player:Player=None) -> set[int]:
	assert not (player_id_64==player==None)
	if player_id_64 is None:
		if player is None:
			raise Exception
		else:
			player_id_64 = player.id_64
	with Session(league_engine) as session:
		player_log_associations = session.query(PlayerInLog).filter_by(player_id_64=player_id_64).all()
		#https://docs.sqlalchemy.org/en/14/orm/query.html#sqlalchemy.orm.Query.join
		return {a.log_id for a in player_log_associations}

def get_player_logs(identifier: Union[int,str,Player]) -> set[Log]:
	with Session(league_engine) as session:
		if isinstance(identifier,Player):
			id_64 = identifier.id_64
		elif isinstance(identifier,str):
			id_64 = session.query(Player).filter_by(name=identifier).one()
		elif isinstance(identifier,int):
			id_64 = identifier
		else:
			raise Exception

		# player = session.get(Player,id_64)
		# print("getting logs",player.name)
		query = session.query(Log).join(PlayerInLog,Log.id==PlayerInLog.log_id and PlayerInLog.player_id_64==id_64)
		# print(f"{player.name} is in {query.first().id}")
		return set(query.all())

def get_existing_logs(player_ids:set[int]) -> dict[int:set[Log]]:
	with Session(league_engine, expire_on_commit=False) as session:
		# player_ids = session.query(PlayerLogTracker).filter(PlayerLogTracker.id_64 in player_ids and )
		
		ids_of_players_with_logs = session.execute(select(PlayerLogTracker.id_64).where(PlayerLogTracker.id_64 in player_ids and PlayerLogTracker.num_logs_tracked>0)).scalars().all()
		ids_of_players_without_logs = player_ids.difference(ids_of_players_with_logs)
		result = {
			p_id : get_player_logs(p_id)
			for p_id in ids_of_players_with_logs
		}
		result.update({
			p_id : set()
			for p_id in ids_of_players_without_logs
		})
		return result