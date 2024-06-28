from db import league_engine
from sqlalchemy.orm import Session
from league_models import Official, League
from datetime import datetime

def get_official(id:int) -> Official:
	with Session(league_engine) as session:
		return session.get(Official, id)

def insert_official(id:int, r_name:str, r_number:int, c_date:datetime, league_id:int):
	with Session(league_engine) as session:
		assert session.get(League, league_id) != None
		if session.get(Official, id) is None:
			official_series = Official(id=id, round_name=r_name, round_number=r_number, creation_date=c_date, league_id=league_id)
			session.add(official_series)
			session.commit()

def update_official():
	# TODO this
	pass
