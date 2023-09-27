import os.path, config
from pprint import pprint
from Data import request, request_batch

class Roster():
    def __init__(self, id, league_dir):
        self.id = id
        self.logs = {}
        self.build_roster_dir(league_dir)
        # TODO: Get date data
        
        # Make request for roster data
        data = self.get_roster_data()

        # Store roster data
        self.name = data["name"]
        self.players = []
        for player in data["players"]:
            id64 = player["steam_64_str"]
            id3 = player["steam_id3"]
            name = player["name"]
            self.players.append(Player(id64, id3, name))

        self.get_logs()

    def get_logs(self):
        print("Requesting logs for roster:", self.id)

        request_progress = 0
        for player in self.players: # Get last 1k logs of each player on the self.
            print(f"Making log request:{request_progress}/{len(self.players)}\n\tRoster id:{self.id}\n\tRoster name:{self.name}\n\tID64:{player.id64}\n\tName:{player.name}")
            player.get_log_ids()
            request_progress += 1

        self.logs = self.potential_log_ids()
        #self.trim_logs()
        print(f"{len(self.logs)} Logs associated with team {self.id}")

    def get_roster_data(self):
        print(f"Requesting roster data, id: {self.id}")
        cache_filepath = os.path.join(config.roster_response_cache, str(self.id) + ".json")
        url = os.path.join(config.ozf_url_prefix , "rosters/", str(self.id))
        data = request(cache_filepath, url, config.headers)["roster"]
        return data

    def build_roster_dir(self, league_dir) -> str:
        self.roster_dir = os.path.join(league_dir, str(self.id), "")
        if not os.path.exists(self.roster_dir):
            os.mkdir(self.roster_dir)

    def guess_core_players(self):
        # TODO get the most common steam ids in logs belonging to this team
        pass

    def potential_log_ids(self, count =4):
        """Check if at least 4 players on the roster are in the game
        Then poll every log in this list for trimming round 2
        (where we make sure they are on the same team)"""
        log_count = {}
        for player in self.players:
            for id in player.log_ids:
                if id in log_count.keys():
                    log_count[id].append(player.name)
                else:
                    log_count[id] = [player.name]
        trimmed_logs = {} # we could just delete from the old dict
        for id in log_count.keys():
            if len(log_count[id]) >= count:
                trimmed_logs[id] = log_count[id]
        print(f"Roster id:{self.id}, Trimmed logs:")
        pprint(trimmed_logs)
        print(trimmed_logs.keys())
        return trimmed_logs

    def trim_logs(self, count =4):
        """ Check that there are at least count players
        from this roster on the SAME TEAM in each log.
        This involves requesting each log INDIVIDUALLY"""
        pass

    def print(self):
        # TODO
        pass


class Player():
    def __init__(self, id64, id3, name = ""):
        self.name = name
        self.id64 = id64
        self.id3 = id3
        self.log_ids = self.get_log_ids()

    def print(self):
        # TODO
        pass

    def get_log_ids(self):
        print(f"Requesting Player: <{self.name}>, log search")
        cache_filepath = os.path.join(config.player_log_search_cache, self.id64 + ".json")
        url = config.logs_url_prefix + "?player=" + self.id64
        log_search = request(cache_filepath, url)
        print(f"Was given {log_search['results']} / {log_search['total']} logs that contain player {log_search['parameters']['player']}")
        return [log['id'] for log in log_search['logs']]

class League():
    def __init__(self, id):
        self.id = id
        data = self.get_league_data()
        self.build_league_dir()
        # TODO: Get date data
        self.name = data["name"]
        self.get_rosters(data["rosters"])

        count = 0
        for roster in self.rosters:
            count += len(roster.logs)
        print(f"TOTAL LOG REQUESTS NEEDED: {count}")

    def get_rosters(self, rosters):
        roster_ids = [roster["id"] for roster in rosters]
        self.rosters = [Roster(id, self.path) for id in roster_ids]

    def build_league_dir(self):
        self.path = os.path.join(config.leagues_directory, str(self.id), "")
        if not os.path.exists(self.path):
            os.mkdir(self.path)

    def get_league_data(self):
        print(f"Requesting league data, id: {self.id}")
        cache_filepath = os.path.join(config.league_response_cache, str(self.id) + ".json")
        url = os.path.join(config.ozf_url_prefix, "leagues/", str(self.id))
        return request(cache_filepath, url, config.headers)["league"]

    def get_dates(self):
        #TODO 
        pass