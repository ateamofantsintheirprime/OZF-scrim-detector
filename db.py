'''
db
database file, containing all the logic to interface with the sql database
'''

from sqlalchemy import create_engine , select
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from models import *
from pathlib import Path

# creates the database directory
Path("database") \
	.mkdir(exist_ok=True)

# "database/main.db" specifies the database file
# turn echo = True to display the sql output
engine = create_engine("sqlite:///database/main.db", echo=False)

# initializes the database
Base.metadata.create_all(engine)

# Basic insertion and access methods

# League
def get_league(id:int) -> League:
	with Session(engine) as session:
		return session.get(League, id)
	
def insert_league(id:int, name:str):
	with Session(engine) as session:
		if session.get(League, id) is None:
			print(id, name)
			league = League(id=id, name=name)
			session.add(league)
			session.commit()

# Division
def get_division(league_id, name) -> Division:
	with Session(engine) as session:
		return session.query(Division).filter_by(league_id=league_id, name=name).one_or_none()

def insert_division(league_id, name):
	with Session(engine) as session:
		assert session.get(League, league_id) != None
		if get_division(league_id, name) == None:
			division = Division(league_id=league_id,name=name)
			session.add(division)
			session.commit()

# Roster
def get_roster(id:int) -> Roster:
	with Session(engine) as session:
		return session.get(Roster, id)

def insert_roster(id:int, name:str, division_name:str, league_id:int):
	with Session(engine) as session:
		assert get_division(league_id=league_id, name=division_name) != None
		assert session.get(League, league_id) != None
		if session.get(Roster, id) is None:
			# print("league_id:", league_id, "division name: ", division_name)
			# print(session.query(Division).all())
			roster= Roster(id=id, name=name, division_name=division_name, league_id=league_id)
			session.add(roster)
			# league.rosters.add(roster)
			session.commit()

# Official
def get_official(id:int) -> Official:
	with Session(engine) as session:
		return session.get(Official, id)

def insert_official(id:int, r_name:str, r_number:int, c_date:datetime, league_id:int):
	with Session(engine) as session:
		assert session.get(League, league_id) != None
		if session.get(Official, id) is None:
			official_series = Official(id=id, round_name=r_name, round_number=r_number, creation_date=c_date, league_id=league_id)
			session.add(official_series)
			# league.officials.add(official_series)
			session.commit()

def get_player(id_64:int) -> Player:
	with Session(engine) as session:
		return session.get(Player, id_64)

def insert_player(id_64:int, id3:int, name:str, ozf_id:int=None):
	with Session(engine) as session:
		if session.get(Player, id_64) is None:
			player = Player(id_64=id_64, id3=id3, name=name, ozf_id=ozf_id)
			session.add(player)
			session.commit()

def add_player_to_roster(player_ozf_id:int, roster_id:int):
	with Session(engine) as session:
		# Add the league_id to the playeronroster to make searching players easier
		if len(session.query(PlayerOnRoster).filter_by(player_ozf_id=player_ozf_id, roster_id=roster_id).all()) ==0:
			league_id = session.get(Roster, roster_id).league_id
			player_on_roster = PlayerOnRoster(player_ozf_id=player_ozf_id, roster_id=roster_id,league_id=league_id)
			session.add(player_on_roster)
			session.commit()

def get_log(log_id:int) -> Log:
	with Session(engine) as session:
		return session.get(Log, log_id)

def insert_log(log_id:int, date:datetime):
	with Session(engine) as session:
		if session.get(Log, log_id) is None:
			log = Log(id=log_id, date=date)
			session.add(log)
			session.commit()

def add_player_to_log(player_id_64:int, log_id:int):
	with Session(engine) as session:
		if len(session.query(PlayerInLog).filter_by(player_id_64=player_id_64,log_id=log_id).all()) ==0:
			player_in_log = PlayerInLog(player_id_64=player_id_64,log_id=log_id)
			session.add(player_in_log)
			session.commit()

# Other access methods

def get_league_officials(league_id:int) -> list[Official]:
	with Session(engine) as session:
		return session.query(Official).filter_by(league_id=league_id).all()

def get_players_on_roster(roster_id:int) -> list[Player]:
	with Session(engine) as session:
		associations = session.query(PlayerOnRoster).filter_by(roster_id=roster_id).all()
		return [session.get(Player, a.player_ozf_id) for a in associations]

def get_rosters_in_league(league_id:int) -> list[Roster]:
	with Session(engine) as session:
		return session.query(Roster).filter_by(league_id=league_id).all()

def get_players_in_league(league_id:int) -> list[Player]:
	with Session(engine) as session:
		associations = session.query(PlayerOnRoster).filter_by(league_id=league_id)
		# I know there's definitely a faster way of getting these players but it should be fine
		return [session.get(Player, a.player_ozf_id) for a in associations]

def update_roster(roster_id:int, new_name:str=None, new_division_name:str=None):
	if new_name==None and new_division_name == None:
		return
	with Session(engine) as session:
		roster_to_update = session.get(Roster, roster_id)
		if new_name != None:
			roster_to_update.name=new_name
		if new_division_name != None:
			roster_to_update.division_name=new_division_name

# def update_log(log_id:int, date:datetime=None, map_name:str=None, duration:int=None, red_team_score:int=None, blue_team_score:int=None):
# 	with Session(engine) as session:
# 		log = session.get(Log, log_id)
# 		if date != None:
# 			log.date=date 
# 		if map_name != None:
# 			log.map_name=map_name 
# 		if date != None:
# 			log.duration=duration 
# 		if date != None:
# 			log.red_team_score=red_team_score 
# 		if date != None:
# 			log.blue_team_score=blue_team_score 
# 		session.commit()
# Methods for analysing data

# def get_game(log_id)

# def get_logs_of_player():
def within_season_duration(league_id:int, date:datetime):
	with Session(engine) as session:
		league = session.get(League,league_id)
		return league.start_date < date and league.end_date > date

def get_player_log_ids(player:Player):
	with Session(engine) as session:
		player_log_associations = session.query(PlayerInLog).filter_by(player_id_64=player.id_64).all()
		return [a.log_id for a in player_log_associations]

def get_date_filtered_player_log_ids(league_id:int, player:Player):
	with Session(engine) as session:
		unfiltered_log_ids = get_player_log_ids(player)
		print(f"unfiltered log ids: {unfiltered_log_ids}")
		filtered_result = []
		for log_id in unfiltered_log_ids:
			log_date = session.get(Log,log_id).date
			if within_season_duration(league_id, date=log_date):
				filtered_result.append(log_id)
		return filtered_result

def get_player_group_log_ids(league_id: int, players:list[Player], threshold:int):
	with Session(engine) as session:
		# Assert the players are all playing in the same league maybe
		
		log_appearances: dict[int:int]= {}# {log_id : appearance_count}
		
		# There's probably an sql way you could do this
		# Count the number of times 
		
		for p in players:
			log_ids = get_date_filtered_player_log_ids(league_id=league_id,player=p)
			for id in log_ids:
				if id in log_appearances.keys():
					log_appearances[id] += 1
				else:
					log_appearances[id] = 1
		return [id for (id,count) in log_appearances.items() if count >= threshold]

def get_logs_of_roster(roster_id:int, player_threshold:int):
	with Session(engine) as session:
		league_id = session.get(Roster, roster_id).league_id
		players = get_players_on_roster(roster_id=roster_id)
		return get_player_group_log_ids(league_id,players,player_threshold)

def insert_game(log_id:int, map_name:str, date:datetime, duration:timedelta):
	pass


def update_league_dates(league_id:int):
	with Session(engine) as session:
		league = session.get(League, league_id)
		officials = get_league_officials(league_id=league_id)
		# league = session.query(League).filter_by(id=id).one()

		dates = [o.creation_date for o in officials]
		first = min(dates)
		last = max(dates)

		start_leeway = 10
		end_leeway = 14

		# league.start_date = datetime.fromisoformat(first).replace(tzinfo=None)
		league.start_date = first - timedelta(days=start_leeway)

		# league.end_date = datetime.fromisoformat(last).replace(tzinfo=None)
		league.end_date = last + timedelta(days=end_leeway)

		session.commit()

	



# def add_player_to_roster(roster_id:int, player_id:int):

	
# def update_league_info(id:int, name:str="", rosters:List[Roster]=[], matches:List[Official]=[]):
# 	with Session(engine) as session:
# 		pass

