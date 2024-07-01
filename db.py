
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from league_models import *
from cache_models import *
from pathlib import Path
from pprint import pprint
from debug import debug_print

# creates the database directory
Path("database\data") \
	.mkdir(exist_ok=True)
# TODO split database methods across files

# "database/main.db" specifies the database file
# turn echo = True to display the sql output
SQLALCHEMY_DATABASE_URI = "postgresql:///main"
SQLALCHEMY_BINDS = {
    "league": "sqlite:///database/data/league.db",
    "cache": "sqlite:///database/data/cache.db",
}

# Create engines
cache_engine = create_engine(SQLALCHEMY_BINDS["cache"], echo=False)
league_engine = create_engine(SQLALCHEMY_BINDS["league"], echo=False)

# Create tables in respective databases
LeagueBase.metadata.create_all(league_engine)
CacheBase.metadata.create_all(cache_engine)

# def reset_search_expiry(id_64):
# 	with Session(league_engine) as session:
# 		expiry_days = 3
# 		search_info = session.get(LogSearchInfo, id_64)
# 		assert not search_info is None
# 		search_info.expiry_date=datetime.today() + timedelta(days=expiry_days)
# 		session.commit()

# def add_search_info(id_64, num_logs, last_log_id=None):
# 	with Session(league_engine) as session:
# 		expiry_days = 3
# 		search_info = LogSearchInfo(
# 			id_64=id_64,
# 			num_logs=num_logs,
# 			last_log_id=last_log_id,
# 			expiry_date=datetime.today() + timedelta(days=expiry_days))
# 		session.add(search_info)
# 		session.commit()
# def add_log_batch(id_64:int, batch_json:dict):
# 	with Session(cache_engine) as session:
# 		search_info = session.get(LogSearchInfo, id_64)
# 		assert not search_info is None
# 		stopping_id = search_info.last_log.log_id

def add_player_to_roster(roster_id:int, player_ozf_id:int=None):
	with Session(league_engine) as session:
		# Make sure player exists
		player= session.query(Player).filter_by(ozf_id=player_ozf_id).one()

		# Make sure roster exists
		roster= session.get(Roster, roster_id)
		# debug_print(f"roster id: {roster.id}")
		assert not roster is None
		# Add the league_id to the playeronroster to make searching players easier
		player_on_roster = session.get(PlayerOnRoster, (player_ozf_id, roster_id))
		if player_on_roster is None:
			league_id = roster.league_id
			player_on_roster = PlayerOnRoster(player_ozf_id=player_ozf_id, player_id_64=player.id_64,roster_id=roster_id,league_id=league_id)
			session.add(player_on_roster)
			session.commit()
		else:
			debug_print("Player already on roster in db!")



# Other access methods

def get_all_player_logs() -> list[PlayerInLog]:
	with Session(league_engine) as session:
		return session.query(PlayerInLog).all()


def get_date_filtered_player_log_ids(league_id:int, player:Player):
	with Session(league_engine) as session:
		unfiltered_log_ids = get_player_log_ids(player)
		print(f"unfiltered log ids: {unfiltered_log_ids}")
		filtered_result = []
		for log_id in unfiltered_log_ids:
			log_date = session.get(Log,log_id).date
			if within_season_duration(league_id, date=log_date):
				filtered_result.append(log_id)
		return filtered_result

def get_player_group_log_ids(league_id: int, players:list[Player], threshold:int):
	with Session(league_engine) as session:
		# Assert the players are all playing in the same league maybe
		
		log_appearances: dict[int:int]= {}# {log_id : appearance_count}
		
		# There's probably an sql way you could do this
		# Count the number of times 
		#https://docs.sqlalchemy.org/en/14/orm/query.html#sqlalchemy.orm.Query.join
		
		for p in players:
			log_ids = get_date_filtered_player_log_ids(league_id=league_id,player=p)
			for id in log_ids:
				if id in log_appearances.keys():
					log_appearances[id] += 1
				else:
					log_appearances[id] = 1
		return [id for (id,count) in log_appearances.items() if count >= threshold]



# def add_player_to_roster(roster_id:int, player_id:int):

	
# def update_league_info(id:int, name:str="", rosters:List[Roster]=[], matches:List[Official]=[]):
# 	with Session(engine) as session:
# 		pass

