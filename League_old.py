import os.path, config
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from pprint import pprint
from Data import request_safe
from Roster_old import Roster
from Matchups_old import Matchup, PugTeam
from time import sleep
from Log import FullLog

class League():
	def __init__(self, id):
		self.id = id
		data = self.get_league_data()
		self.data = data
		
		self.get_officials()
		self.path = self.build_league_dir()
		# TODO: Get date data
		self.name = data["name"]
		print("season name:", self.name)
		dates = self.get_dates(data["matches"])
		self.start_date = dates["start date"]
		self.end_date = dates["end date"]
		# print("dates:", self.start_date.strftime("%d/%m/%Y"), self.end_date.strftime("%d/%m/%Y"))
		self.rosters = self.get_rosters(data["rosters"])
		self.init_rosters_parallel()
		self.identify_matchups()
		self.get_official_candidates()
		# self.print_matchups()
		# count = 0
		# for roster in self.rosters:
		#	 count += len(roster.potential_logs)
		# print(f"TOTAL LOG REQUESTS NEEDED: {count}")

	def get_rosters(self, rosters):
		roster_ids = [roster["id"] for roster in rosters]
		return [Roster(id, self.path, self.start_date, self.end_date) for id in roster_ids]

	def init_rosters(self):
		for roster in self.rosters:
			roster.init()

	def init_single_roster(self, roster):
		roster.init()

	def init_rosters_parallel(self):
		max_concurrent = 10
		with ThreadPoolExecutor(max_concurrent) as executor:
			results = executor.map(self.init_single_roster, self.rosters)


	def build_league_dir(self):
		path = os.path.join(config.leagues_directory, str(self.id), "")
		if not os.path.exists(path):
			os.mkdir(path)
		return path

	def identify_matchups(self):
		self.all_matchups: list[Matchup] = []
		self.team_matchups: list[Matchup] = []
		self.pugscrim_matchups: list[Matchup] = []
		log_matchups = {}
		for roster in self.rosters:
			for log_side in roster.log_sides:
				log : FullLog = log_side["log"]
				side : int = log_side["side"]
				if not log.id in log_matchups.keys():
					log_matchups[log.id] = {"log": log, "rosters" : [{"roster":roster, "side":side}]}
				else:
					log_matchups[log.id]["rosters"].append({"roster":roster, "side":side})
		for log_id in log_matchups.keys():
			matchup_data = log_matchups[log_id]
			matchup_obj = Matchup(teams=matchup_data["rosters"], log=matchup_data["log"])
			self.all_matchups.append(matchup_obj)
			if isinstance(matchup_obj.red_team, PugTeam):
				matchup_obj.blue_team.pugscrim_matchups.append(matchup_obj)
				self.pugscrim_matchups.append(matchup_obj)
			elif isinstance(matchup_obj.blue_team, PugTeam):
				matchup_obj.red_team.pugscrim_matchups.append(matchup_obj)
				self.pugscrim_matchups.append(matchup_obj)
			else:
				matchup_obj.red_team.team_matchups.append(matchup_obj)
				matchup_obj.blue_team.team_matchups.append(matchup_obj)
				self.team_matchups.append(matchup_obj)
		
		for m in self.all_matchups:
			print("blue team:", m.blue_team.name)
			print("red team:", m.red_team.name)
			print("result:", m.result)
			print("============")

	def print_matchups(self):
		for team in self.rosters:
			team_matchups = []
			pugscrim_matchups = []
			for matchup in self.all_matchups:
				if matchup.blue_team == team:
					result = (matchup.result[1], matchup.result[0]) # reverse it cos it should be from the perspective of this team
					m = {"opponent": matchup.red_team.name, "score" : result, "log_id" : matchup.log.id}
					if isinstance(matchup.red_team, PugTeam):
						pugscrim_matchups.append(m)
					else:
						team_matchups.append(m)
				if matchup.red_team == team:
					m = {"opponent": matchup.blue_team.name, "score" : matchup.result, "log_id" : matchup.log.id}

					if isinstance(matchup.blue_team, PugTeam):
						pugscrim_matchups.append(m)
					else:
						team_matchups.append(m)

			print(f"name: {team.name} [id: {team.id}] Scrims:")
			print("team matchups:")
			pprint(team_matchups)
			print("pugscrims:")
			pprint(pugscrim_matchups)

	def get_league_data(self):
		print(f"Requesting league data, id: {self.id}")
		cache_filepath = os.path.join(config.league_response_cache, str(self.id) + ".json")
		url = os.path.join(config.ozf_url_prefix, "leagues/", str(self.id))
		return request_safe(cache_filepath, url, config.headers)["league"]

	def get_dates(self, match_list):
		#TODO 
		earliest_match = match_list[0]
		latest_match = match_list[0]
		
		for match in match_list:
			match_date = datetime.fromisoformat(match["created_at"])
			earliest_match_date = datetime.fromisoformat(earliest_match["created_at"])
			latest_match_date = datetime.fromisoformat(latest_match["created_at"])
			# print(f"Match in question: {match_date}")
			# print(f"Earliest Match: {earliest_match_date}")
			# print(f"Latest Match: {latest_match_date}")
			if match_date < earliest_match_date:
				earliest_match = match
			if match_date > latest_match_date:
				latest_match = match 
		# print(f"Earliest Match: {earliest_match_date}")
		# print(f"Latest Match: {latest_match_date}")

		# Number of days before the first match and after the last match are generated, to place the start and end markers of the seasons.
		# These are total estimates and liable to change.
		# Upon initial 'testing' the estimates seem to be fine, on the generous side.
		start_leeway = 10
		end_leeway = 14
		# Make sure the dates are timezone naive. this is only for ozfotress after all
		start_date = datetime.fromisoformat(earliest_match["created_at"]).replace(tzinfo=None)
		start_date = start_date - timedelta(days=start_leeway)
		end_date = datetime.fromisoformat(latest_match["created_at"]).replace(tzinfo=None)
		end_date = end_date + timedelta(days=end_leeway)

		return {"start date": start_date, "end date": end_date}
	
	def get_officials(self) :
		# pprint(self.data['matches'])
		self.officials = [
			#m['id'] : at some point it might help for this to be a dict
			{
					"id":m['id'], 
					"created_at": m['created_at'],
					"round_number": m['round_number'],
					'home_team_id' : None,
					'away_team_id' : None,
					'match_candidates' : []
			} for m in self.data['matches']
		]
		for m in self.officials:
			cache_filepath = os.path.join(config.official_response_cache, str(m['id']) + ".json")
			url = os.path.join(config.ozf_url_prefix, "matches/", str(m['id']))
			further_match_data = request_safe(cache_filepath, url, config.headers)['match']
			# print("further match data:")
			# pprint(further_match_data)
			if further_match_data['home_team'] != None:
				# This is what a bye looks like and needs to be addressed in future
				m["home_team_id"] = further_match_data['home_team']['id']
			if further_match_data['away_team'] != None:
				m["away_team_id"] = further_match_data['away_team']['id']

	def get_official_candidates(self):
		print("Official Candidates:")
		for roster in self.rosters:
			print(f"{roster.name} : team matches")
			if len(roster.team_matchups) == 0:
				print("\tCould not find any team vs team matchups for this roster!")
			for match in roster.team_matchups:
				print(f"\t{match.blue_team.name} vs {match.red_team.name}")
				print(f"\t\t{match.log.id}")
			print()

		for official in self.officials:
			if official['home_team_id'] == None:
				home_team_name = "Bye"
			else:
				home_team = [r for r in self.rosters if r.id == official['home_team_id']][0]
				home_team_name = home_team.name

			if official['away_team_id'] == None:
				away_team_name = "Bye"
			else:
				away_team = [r for r in self.rosters if r.id == official['away_team_id']][0]
				away_team_name = away_team.name

			print(f"looking for {home_team_name} ({official['home_team_id']}) vs {away_team_name} ({official['away_team_id']})")

			if official["away_team_id"] != None and official["home_team_id"] != None:
				for match in home_team.team_matchups:
					print(f"\t{match.blue_team.name} ({match.blue_team.id}) vs {match.red_team.name} ({match.red_team.id}): [{match.log.id}]")
					# print(type(match.blue_team.id))
					# print(type(match.red_team.id))
					# print(type(official['home_team_id']))
					# print(type(official['away_team_id']))
					if official['home_team_id'] == match.blue_team.id and official['away_team_id'] == match.blue_team.id:
						official['match_candidates'].append(match)
						print("success!")
					if official['away_team_id'] == match.blue_team.id and official['home_team_id'] == match.blue_team.id:
						official['match_candidates'].append(match)
						print("success!")
				if len(official['match_candidates']) == 0:
					print("trying pugscrim logs...")
					for match in home_team.pugscrim_matchups:
						print(f"\t{match.blue_team.name} ({match.blue_team.id}) vs {match.red_team.name} ({match.red_team.id}): [{match.log.id}]")
						self.check_match_closeness(match, home_team, away_team)
					for match in away_team.pugscrim_matchups:
						print(f"\t{match.blue_team.name} ({match.blue_team.id}) vs {match.red_team.name} ({match.red_team.id}): [{match.log.id}]")
						self.check_match_closeness(match, home_team, away_team)
			print()
		# pprint(self.officials)
		
	def check_match_closeness(self, match: Matchup, roster1: Roster, roster2: Roster):
		if isinstance(match.blue_team, PugTeam):
			blue_player_ids = [id3 for id3 in match.blue_team.players]
		else:
			blue_player_ids = [player.id3 for player in match.blue_team.players]
		if isinstance(match.red_team, PugTeam):
			red_player_ids = [id3 for id3 in match.red_team.players]
		else:
			red_player_ids = [player.id3 for player in match.red_team.players]

		roster1_player_ids = [player.id3 for player in roster1.players]
		roster2_player_ids = [player.id3 for player in roster2.players]

		print("red team player ids: ", red_player_ids)
		print("blue team player ids: ", blue_player_ids)

		print(f"{roster1.name} player ids: ", roster1_player_ids)
		print(f"{roster2.name} player ids: ", roster2_player_ids)

		roster1_blue_sim = len([p_id for p_id in blue_player_ids if p_id in roster1_player_ids])
		roster1_red_sim = len([p_id for p_id in red_player_ids if p_id in roster1_player_ids])

		roster2_blue_sim = len([p_id for p_id in blue_player_ids if p_id in roster2_player_ids])
		roster2_red_sim = len([p_id for p_id in red_player_ids if p_id in roster2_player_ids])

		print(f"{roster1.name}-blue_team similarity: {roster1_blue_sim}/{len(blue_player_ids)}")
		print(f"{roster1.name}-red_team similarity: {roster1_red_sim}/{len(red_player_ids)}")

		print(f"{roster2.name}-blue_team similarity: {roster2_blue_sim}/{len(blue_player_ids)}")
		print(f"{roster2.name}-red_team similarity: {roster2_red_sim}/{len(red_player_ids)}")
