import os.path, config
from Log import MiniLog, FullLog
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from pprint import pprint
from Data import request, request_batch, request_safe

class Roster():
    def __init__(self, id, league_dir, league_start_date, league_end_date):
        self.id = id
        self.logs = {}
        self.roster_dir = self.build_roster_dir(league_dir)
        self.start_date = league_start_date
        self.end_date = league_end_date
        
        # Make request for roster data
        data = self.get_roster_data()

        # Store roster data
        self.name = data["name"]
        self.players = []

        request_progress = 0
        for player in data["players"]:
            ozfid = player["id"]
            id64 = player["steam_64_str"]
            id3 = player["steam_id3"]
            name = player["name"]
            new_player = Player(id64, id3,ozfid, name)
            self.players.append(new_player)
            # print(f"Constructing Player: {request_progress}/{len(data['players'])}\n\tRoster id: {self.id}\n\tRoster name: {self.name}\n\tID64: {new_player.id64}\n\tName: {new_player.name}")
            request_progress += 1

        self.potential_logs = self.get_potential_logs()
        # self.get_logs()
        self.get_logs_parallel()
        print(f"Team:\n\tname:{self.name}\n\troster id:{self.id}")
        print(f"\tlogs:{[log.id for log in self.logs]}")

    def get_logs_parallel(self):
        print(f"Parrallelised request for logs of roster : {self.id}, {self.name}")
        cache_filepath_prefix = config.log_cache
        url_prefix = config.logs_url_prefix + "/"
        ids = [str(id) for id in self.potential_logs.keys()]
        batch = request_batch(cache_filepath_prefix, url_prefix, ids)
        self.logs = []
        for i in range(len(batch)):
            self.logs.append(FullLog(batch[i], ids[i]))
        # self.logs = [FullLog(log_data) for log_data in batch]
        self.trim_logs()


    # def get_logs(self):
    #     """ Check that there are at least count players
    #     from this roster on the SAME TEAM in each log.
    #     This involves requesting each log INDIVIDUALLY"""

    #     print(f"Requesting logs for roster: {self.id}, {self.name}")

    #     progress = 0
    #     # pprint(self.potential_logs)
    #     for id in self.potential_logs.keys():
    #         print(f"Requesting log: {progress} / {len(self.potential_logs)}", end = '\r')
    #         cache_filepath = os.path.join(config.log_cache, str(id) + ".json")
    #         url = config.logs_url_prefix + "/" + str(id)
    #         log = request_safe(cache_filepath, url)
    #         # print(f"Recieved log: {id}")
    #         self.logs[id] = log
    #         progress += 1

    #     print(f"PRETRIM:\n\t{len(self.logs)} Logs associated with team:\n\tTeam id: {self.id}\n\tTeam name: {self.name}")
    #     # self.trim_logs()

    def get_roster_data(self):
        print(f"Requesting roster data, id: {self.id}")
        cache_filepath = os.path.join(config.roster_response_cache, str(self.id) + ".json")
        url = os.path.join(config.ozf_url_prefix , "rosters/", str(self.id))
        data = request_safe(cache_filepath, url, config.headers)["roster"]
        return data

    def build_roster_dir(self, league_dir) -> str:
        path = os.path.join(league_dir, str(self.id), "")
        if not os.path.exists(path):
            os.mkdir(path)
        return path
    
    def guess_core_players(self):
        # TODO get the most common steam ids in logs belonging to this team
        pass

    def get_potential_logs(self, count =4):
        """Check if at least 4 players on the roster are in the game
        And that the log was played during the season."""
        log_count = {}
        for player in self.players:
            for minilog in player.minilogs:
                if minilog.falls_within_dates(self.start_date, self.end_date):
                    if minilog.id in log_count.keys():
                        log_count[minilog.id]["players"].append([player.id64, player.name])
                    else:
                        log_count[minilog.id] = {"date": minilog.date, "players": [[player.id64, player.name]]}
        logs = {} # we could just delete from the old dict
        for id in log_count.keys():
            if len(log_count[id]["players"]) >= count:
                logs[id] = log_count[id]
        # print(f"Roster id:{self.id}, Trimmed logs:")
        # pprint(trimmed_logs)
        # print(trimmed_logs.keys())
        return logs

    def trim_logs(self, count =4):
        trimmed_logs = []
        for log in self.logs:
            red_count = len([player.id3 for player in self.players if player.id3 in log.red_team])
            blue_count = len([player.id3 for player in self.players if player.id3 in log.blue_team])

            if red_count > count or blue_count > count:
                trimmed_logs.append(log)

        self.logs = trimmed_logs

    def print(self):
        # TODO
        pass

class Player():
    def __init__(self, id64, id3, ozfid, name = "" ):
        self.ozfid = ozfid
        self.name = name
        self.id64 = id64
        self.id3 = id3
        self.minilogs = self.get_minilogs()

    def print(self):
        # TODO
        pass

    def get_minilogs(self):
        # print(f"Requesting Player: <{self.name}>, log search")
        cache_filepath = os.path.join(config.player_log_search_cache, self.id64 + ".json")
        url = config.logs_url_prefix + "?player=" + self.id64
        log_search = request_safe(cache_filepath, url)
        # print(f"Was given {log_search['results']} / {log_search['total']} logs that contain player {log_search['parameters']['player']}")
        return [MiniLog(log) for log in log_search['logs']]

class League():
    def __init__(self, id):
        self.id = id
        data = self.get_league_data()
        self.path = self.build_league_dir()
        # TODO: Get date data
        self.name = data["name"]
        dates = self.get_dates(data["matches"])
        self.start_date = dates["start date"]
        self.end_date = dates["end date"]
        self.rosters = self.get_rosters(data["rosters"])
        # count = 0
        # for roster in self.rosters:
        #     count += len(roster.potential_logs)
        # print(f"TOTAL LOG REQUESTS NEEDED: {count}")

    def get_rosters(self, rosters):
        roster_ids = [roster["id"] for roster in rosters]
        return [Roster(id, self.path, self.start_date, self.end_date) for id in roster_ids]

    def build_league_dir(self):
        path = os.path.join(config.leagues_directory, str(self.id), "")
        if not os.path.exists(path):
            os.mkdir(path)
        return path

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
    