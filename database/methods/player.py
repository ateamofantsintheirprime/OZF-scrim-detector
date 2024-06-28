from db import league_engine
from sqlalchemy.orm import Session
from league_models import Player, PlayerInLog, Log

def get_player_id64(ozf_id:int) -> int:
	with Session(league_engine) as session:
		return session.query(Player).filter(ozf_id=ozf_id).one_or_none()

def get_player(id_64:int=None,ozf_id:int=None) -> Player:
	with Session(league_engine) as session:
		if id_64 != None:
			return session.get(Player, id_64)
		if ozf_id != None:
			return session.query(Player).filter_by(ozf_id=ozf_id).one_or_none()
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
	if player_id_64 == None:
		if player == None:
			raise Exception
		else:
			player_id_64 = player.id_64
	with Session(league_engine) as session:
		player_log_associations = session.query(PlayerInLog).filter_by(player_id_64=player_id_64).all()
		#https://docs.sqlalchemy.org/en/14/orm/query.html#sqlalchemy.orm.Query.join
		return {a.log_id for a in player_log_associations}

def get_player_logs(player_id_64:int=None,player:Player=None) -> set[Log]:
	assert not (player_id_64==player==None)
	if player_id_64 == None:
		if player == None:
			raise Exception
		else:
			player_id_64 = player.id_64
	with Session(league_engine) as session:
		query = session.query(Log).join(PlayerInLog,Log.id==PlayerInLog.log_id and PlayerInLog.player_id_64==player_id_64)
		return set(query.all())