from pprint import pprint
import db
from league_models import *
from time import sleep
from datetime import datetime
from database_helper import construct_league, request_basic, update_all_roster_info, update_roster_info, update_all_official_info, request_from_ozf
import config
from database.methods import official, player, roster, league, team_instance, game, log
from fast_log_downloader import LogSearcher, GameRequester
import cProfile
import io
import pstats

# pr = cProfile.Profile()
# pr.enable()

# # Initialising the log searcher causes it to immediately start retreiving logs from db in the background
# roster.delete_all_rosters()
# team_instance.delete_all_team_instances()
# team_instance.delete_all_merc_teams()
# game.delete_all_games()

data = request_from_ozf("league",30)
s_30 = construct_league(data)
update_all_roster_info(30)
update_all_official_info(30)
last_n_found = roster.get_roster(1097)
footie_mate = roster.get_roster(1077)
lnf_opponents = roster.get_opposing_teams(1097)
footie_mate_opponents = roster.get_opposing_teams(1077)

log_downloader = LogSearcher()
log_downloader.targets = [footie_mate, footie_mate_opponents]
log_downloader.execute_task()

game_requester = GameRequester() 
game_requester.targets = [footie_mate]
game_requester.execute_task()

team_instance.build_all_team_instances()

for opp in footie_mate_opponents:
	print(f"Last n found vs {opp.name} ({opp.id}):")
	matchup_games = roster.find_roster_matchup(footie_mate.id, opp.id)
	if len(matchup_games) == 0:
		print("no games found for this matchup!")
		# team_instance.check_teams_in_game(game)
	print([g.game_id for g in matchup_games])
	
	all_players = roster.get_roster_players(footie_mate.id)
	all_players.update(roster.get_roster_players(opp.id))

	# offic = official.get_officials_from_roster_ids(last_n_found.id,opp.id)[0]

	# official.create_candidate_logs(offic)
	if len(matchup_games) == 0:
		candidate_logs = log.get_logs_with_players(all_players, threshold=8)
		print(f"there are {len(candidate_logs)} candidates for this game")
		for dict in candidate_logs:
			team_instance.check_teams_in_game(dict['log'].id)
			opp_players_in_log = roster.get_rostered_players_in_log(opp.id,dict['log'])
			print("opp players in log:", opp_players_in_log)
	# print("candidate logs:",candidate_logs)
# log1 = log.get_log(2833433)
# log2 = log.get_log(2833449)
# opp_players_in_log1 = roster.get_rostered_players_in_log(1077,log1)
# opp_players_in_log2 = roster.get_rostered_players_in_log(1077,log2)

# opp_players = roster.get_player_on_rosters(1077)
# print("foote mate players on ozf: ", [p.player_id_64 for p in opp_players] )

# print("footie mate players in real log 1: ", opp_players_in_log1)
# print("footie mate players in real log 2: ", opp_players_in_log2)

# team_instance.check_teams_in_game(2833433)
# team_instance.check_teams_in_game(2833449)

# s = io.StringIO()
# # sortby = SortKey.CUMULATIVE
# sortby = 'cumtime'
# ps = pstats.Stats(pr, stream=s)
# ps.strip_dirs().sort_stats(sortby).print_stats()

# ps.strip_dirs().sort_stats(sortby).print_callers()
# print(s.getvalue())
