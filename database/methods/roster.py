from db import league_engine
from sqlalchemy.orm import Session
from league_models import Roster, League, Division, PlayerOnRoster, Player
from exceptions import UpdateRosterParameterWarning
from debug import debug_print

def get_roster(id:int) -> Roster:
	with Session(league_engine) as session:
		return session.get(Roster, id)

def insert_roster(id:int, name:str, division_name:str, league_id:int) -> Roster:
	with Session(league_engine) as session:
		assert session.get(Division, (league_id, division_name)) != None
		assert session.get(League, league_id) != None
		if session.get(Roster, id) is None:
			roster= Roster(id=id, name=name, division_name=division_name, league_id=league_id)
			session.add(roster)
			session.commit()
			return roster

def update_roster(roster_id:int, new_name:str=None, new_division_name:str=None) -> Roster:
	if new_name==None and new_division_name == None:
		raise UpdateRosterParameterWarning
	with Session(league_engine) as session:
		roster = session.get(Roster, roster_id)
		if roster is None:
			debug_print("Roster not found. Please insert first.")
			raise Exception
		debug_print("Roster found in DB. Updating now")
		if new_name != None:
			roster.name=new_name
		if new_division_name != None:
			roster.division_name=new_division_name
		session.commit()
		return roster

# =============================

def get_roster_players(roster_id:int) -> set[Player]:
	with Session(league_engine) as session:
		return set(session.query(Player).join(PlayerOnRoster, Player.ozf_id==PlayerOnRoster.player_ozf_id).filter(roster_id=roster_id).all())

def get_roster_player_ids(roster_id:int) -> set[int]:
	with Session(league_engine) as session:
		return set(session.query(Player.id_64).join(PlayerOnRoster, Player.ozf_id==PlayerOnRoster.player_ozf_id).filter(roster_id=roster_id).all())

def get_roster_logs(roster_id:int, player_threshold:int):
	with Session(league_engine) as session:
		league_id = session.get(Roster, roster_id).league_id
		players = get_roster_players(roster_id=roster_id)
		return get_player_group_log_ids(league_id,players,player_threshold)

