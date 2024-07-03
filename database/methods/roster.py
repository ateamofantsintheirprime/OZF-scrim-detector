from db import league_engine
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func, select
from league_models import Roster, League, Game, Division, PlayerOnRoster, Player, PlayerInLog, Log, Official, TeamInstance
from exceptions import UpdateRosterParameterWarning
from debug import debug_print
from typing import Union
from database.methods.division import get_division

def delete_all_rosters():
	with Session(league_engine) as session:
		session.query(Roster).delete()
		session.query(PlayerOnRoster).delete()
		print("deleting all rosters and playeronrosters")
		session.commit()

def get_player_on_rosters(roster_id:int) -> list[PlayerOnRoster]:
	with Session(league_engine) as session:
		return session.query(PlayerOnRoster).filter_by(roster_id=roster_id)

def get_roster(identifier:Union[int,str]) -> Roster:
	with Session(league_engine) as session:
		if isinstance(identifier, int):
			return session.get(Roster, identifier)
		if isinstance(identifier, str):
			return session.query(Roster).filter_by(name=identifier)
		raise Exception

def insert_roster(id:int, name:str, division_name:str, league_id:int, team_id:int) -> Roster:
	with Session(league_engine) as session:
		assert not get_division(league_id, division_name) is None
		assert not session.get(League, league_id) is None
		if session.get(Roster, id) is None:
			roster= Roster(id=id, name=name, division_name=division_name, league_id=league_id, ozf_team_id=team_id)
			session.add(roster)
			session.commit()
			return roster

def update_roster(roster_id:int, new_name:str=None, new_division_name:str=None) -> Roster:
	if new_name==None and new_division_name is None:
		raise UpdateRosterParameterWarning
	with Session(league_engine) as session:
		roster = session.get(Roster, roster_id)
		if roster is None:
			debug_print("Roster not found. Please insert first.")
			raise Exception
		debug_print("Roster found in DB. Updating now")
		if not new_name is None:
			roster.name=new_name
		if not new_division_name is None:
			roster.division_name=new_division_name
		session.commit()
		return roster

# =============================

def get_opposing_teams(roster_id:int) -> set[Roster]:
	with Session(league_engine) as session:
		return set(session.query(Roster).\
			join(Official, Roster.id == Official.home_team_id).\
			filter(Official.away_team_id==roster_id)).union(
			set(session.query(Roster).\
			join(Official, Roster.id == Official.away_team_id).\
			filter(Official.home_team_id==roster_id)
			))
			
def get_rostered_players_in_log(roster_id:int, log:Log) -> set[Player]:
	with Session(league_engine) as session:
		return set(session.query(Player).\
			join(PlayerOnRoster, Player.ozf_id==PlayerOnRoster.player_ozf_id).filter_by(roster_id=roster_id).\
			join(PlayerInLog, PlayerOnRoster.player_id_64==PlayerInLog.player_id_64).filter(PlayerInLog.log_id==log.id).all())

def get_roster_officials(roster_id:int) -> set[Official]:
	with Session(league_engine) as session:
		return set(session.query(Official).\
			join(Roster, Official.home_team_id==Roster.id or Official.away_team_id==Roster.id).\
			filter(Roster.id==roster_id).all())

def get_roster_players(roster_id:int) -> set[Player]:
	with Session(league_engine) as session:
		return set(session.query(Player).join(PlayerOnRoster, Player.ozf_id==PlayerOnRoster.player_ozf_id).filter_by(roster_id=roster_id).all())

def get_roster_player_ids(roster_id:int) -> set[int]:
	with Session(league_engine) as session:
		# return set(session.query(Player.id_64).join(PlayerOnRoster, Player.ozf_id==PlayerOnRoster.player_ozf_id).filter_by(roster_id=roster_id).all())
		# print(roster_id)
		return set(session.execute(select(Player.id_64).\
			join(PlayerOnRoster, Player.ozf_id==PlayerOnRoster.player_ozf_id).
			filter(PlayerOnRoster.roster_id == roster_id)).scalars().all())

def get_roster_logs(roster_id:int, player_threshold:int):
	with Session(league_engine) as session:

		player_ids = get_roster_player_ids(roster_id=roster_id)

		inner_query = (session.query(PlayerInLog.log_id)
			.filter(PlayerInLog.player_id_64.in_(player_ids))
			.group_by(PlayerInLog.log_id)
			.having(func.count(PlayerInLog.player_id_64) >= player_threshold))
		subquery = (
			inner_query.subquery()
		)
		# print(inner_query.all())
		# Query to get the actual logs
		logs_with_min_players = session.query(Log).join(PlayerInLog).filter(PlayerInLog.log_id.in_(select(subquery.c.log_id))).all()
		return logs_with_min_players	

def get_all_team_instances():
	with Session(league_engine) as session:
		return set(session.query(TeamInstance).all())

def find_roster_games(roster_id:int):
	with Session(league_engine) as session:
		return session.query(Game)\
			.join(TeamInstance,TeamInstance.game_id==Game.game_id)\
			.filter(TeamInstance.roster_id==roster_id).all()

def find_roster_matchup(roster_id1:int, roster_id2:int):
	with Session(league_engine) as session:
		roster1_games = find_roster_games(roster_id1)
		for game in roster1_games:
			assert not session.get(TeamInstance, (game.game_id, roster_id1)) is None
		roster2_games = find_roster_games(roster_id2)
		for game in roster2_games:
			assert not session.get(TeamInstance, (game.game_id, roster_id2)) is None
		# This is just some sanity checking
		

		result = [game for game in roster1_games if game in roster2_games]
		# print(result)
		return result

		# # team_instance_1 = session.get(TeamInstance, roster_id1)
		# stmt = select(TeamInstance, team2_table).join(team2_table, team2_table.game_id==TeamInstance.game_id)
		# result = session.execute(stmt).fetchall()
		# print(stmt)
		# print(result)
		
		# select(Game)\
		# 	.join(TeamInstance,TeamInstance.game_id==Game.game_id)\
		# 	.filter(TeamInstance.roster_id==roster_id1)\
		# 	.join(TeamInstance,TeamInstance.game_id==Game.game_id)\
		# 	.filter(TeamInstance.roster_id==roster_id1)\
