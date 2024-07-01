from db import league_engine
from sqlalchemy.orm import Session
from league_models import PlayerLogTracker, Player
from datetime import datetime

def get_log_tracker(id_64:int) -> PlayerLogTracker:
	with Session(league_engine) as session:
		return session.get(PlayerLogTracker, id_64)

def insert_log_tracker(id_64:int,num_logs_total:int,num_logs_tracked:int,valid_until:datetime) -> PlayerLogTracker:
	with Session(league_engine) as session:
		assert not session.get(Player, id_64) is None
		tracker = PlayerLogTracker(
			id_64=id_64,
			num_logs_total=num_logs_total,
			num_logs_tracked=num_logs_tracked,
			valid_until=valid_until
			# earliest_log_id=earliest_log_id,
			# latest_log_id=latest_log_id
		)
		session.add(tracker)
		session.commit()
		return tracker

def update_log_tracker(id_64:int, new_total:int=None, num_logs_tracked:int=None, valid_until:datetime=None):#, latest_log_id:int=None):
	with Session(league_engine) as session:
		assert not session.get(Player, id_64) is None
		tracker = session.get(PlayerLogTracker, id_64)
		assert not tracker is None
		if not new_total is None:
			tracker.num_logs_total = new_total
		if not num_logs_tracked is None:
			tracker.num_logs_tracked = num_logs_tracked
		# if not latest_log_id is None:
		# 	tracker.latest_log_id = latest_log_id
		if not valid_until is None:
			tracker.valid_until = valid_until
		session.commit()

def expired(log_tracker: PlayerLogTracker) -> bool:
	return log_tracker.valid_until <= datetime.today()