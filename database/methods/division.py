from db import league_engine
from sqlalchemy.orm import Session
from league_models import Division, League

def get_division(league_id, name) -> Division:
	with Session(league_engine) as session:
		return session.get(Division, (league_id, name))

def insert_division(league_id, name):
	with Session(league_engine) as session:
		assert session.get(League, league_id) != None
		if get_division(league_id, name) == None:
			division = Division(league_id=league_id,name=name)
			session.add(division)
			session.commit()

def update_division():
	# TODO this
	pass