from db import league_engine
from sqlalchemy.orm import Session
from league_models import Division, League

def get_division(league_id, name) -> Division:
	with Session(league_engine) as session:
		return session.query(Division).filter_by(league_id=league_id).filter_by(name=name).one_or_none()

def insert_division(league_id, name):
	with Session(league_engine) as session:
		assert not session.get(League,league_id) is None
		if get_division(league_id, name) is None:
			division = Division(league_id=league_id,name=name)
			session.add(division)
			session.commit()

def update_division():
	# TODO this
	pass