from db import league_engine
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from league_models import Roster, Game, PlayerOnRoster, Player, Official, TeamInstance, MercTeam
from debug import debug_print
from typing import Union
from database.methods.division import get_division

def delete_all_team_instances():
	with Session(league_engine) as session:
		session.query(TeamInstance).delete()
		print("deleting all teaminstances")
		session.commit()
def delete_all_merc_teams():
	with Session(league_engine) as session:
		session.query(MercTeam).delete()
		print("deleting all mercteams")
		session.commit()



def build_all_team_instances():
	with Session(league_engine) as session:
		# games = session.query(Game)
		merc_team_query = session.query(MercTeam)
		# print(f"merc teams before team instances were built: {len(merc_team_query.all())}")
		for mt in merc_team_query.all():
			id3_list = mt.player_ids.split("$")
			# print(id3_list)
			id_64_list = session.execute(select(Player.id_64).filter(Player.id3.in_(id3_list))).scalars().fetchall()
			# print(session.query(Player.id3).all())
			# print(id_64_list)
			# print(len(id_64_list))
			# print(id3_list)
			# print(id_64_list)
			# print(session.query(PlayerOnRoster).filter(PlayerOnRoster.player_id_64.in_(id_64_list)).all())
			stmt = \
				select(\
					Roster,\
					Roster.name,\
					Roster.id,\
					Roster.ozf_team_id,\
					func.count(PlayerOnRoster.player_id_64),\
					func.group_concat(PlayerOnRoster.player_id_64, ", ")\
				).join(\
					PlayerOnRoster, PlayerOnRoster.roster_id==Roster.id)\
				.filter(PlayerOnRoster.player_id_64.in_(id_64_list))\
				.group_by(Roster.id)\
				.having(func.count(PlayerOnRoster.player_id_64) >= len(id3_list)/2)\
				.order_by(-func.count(PlayerOnRoster.player_id_64))
			result = session.execute(stmt).fetchall()
			# print(mt)
			# print("result",result)
			if len(result) == 2:
				print()
				print("NOT SURE WHICH TEAM THIS IS: ")
				for id in id_64_list:
					print(session.get(Player,id).name)
				print(f"is it {result[0][1]} ({result[0][3]}) or {result[1][1]} ({result[1][3]})?")
				print(f"Log id: {mt.game_id}")
				print()
				continue
			assert len(result) <= 1

			if len(result) == 1:
				if session.get(TeamInstance, (mt.game_id,result[0][2])) is None:
					team_instance = TeamInstance(
						score=mt.score,
						game_id=mt.game_id,
						roster_id=result[0][2]
					)
					session.add(team_instance)
				# print(f"Log id: {mt.game_id} has team {result[0][1]} ({result[0][3]}) in it")
				# session.query(MercTeam).filter_by(merc_team_id=mt.merc_team_id).delete()
				# mt.delete()
			# print(mt.game_id)
		# merc_teams_to_delete = session.query(MercTeam).filter()
		# print(f"merc teams after team instances were built: {len(merc_team_query.all())}")
		# merc_team_query.delete() # Make this a little better
		session.commit()

def check_teams_in_game(game_id:int):
	with Session(league_engine) as session:
		team_instances = session.query(TeamInstance).filter(TeamInstance.game_id==game_id).all()
		print(f"we already knew that present teams are: {[(t.roster.name, t.roster_id) for t in team_instances]}")
		print(f"game id: {game_id}")
		if len(team_instances) == 2:
			return
		
		merc_teams = session.query(MercTeam).filter(MercTeam.game_id==game_id).all()
		print(f"unknown merc teams in the game are: {[(mt.player_ids) for mt in merc_teams]}")
		print(f"game id: {game_id}")

		for mt in merc_teams:
			id3_list = mt.player_ids.split("$")
			# print(id3_list)
			player_list = session.execute(select(Player).filter(Player.id3.in_(id3_list))).scalars().fetchall()
			print([(p.id_64, p.name) for p in player_list])