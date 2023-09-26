import itertools, os.path
from pprint import pprint
from Data import make_request
class Team():
    def __init__(self, id, name, players):
        self.id = id
        self.name = name
        self.players = players
        self.logs = {}

    def get_logs(self):
        print("Requesting logs for team:", self.id)

        team_dir = self.get_team_dir()
        request_count = 0
        for player in self.players: # Get last 1k logs of each player on the self.
            print(f"Making log request:{request_count}/{len(self.players)}\n\tRoster id:{self.id}\n\tID64:{player.id64}")
            player.get_log_ids(team_dir)
            request_count += 1
            # for log_id in player.log_ids:
            #     self.logs[log_id] = None # Will be replaced with the log object later

        self.logs = self.trim_logs()
        print(f"{len(self.logs)} Logs associated with team {self.id}")

    def get_team_dir(self) -> str:
        path = "log_ids\\roster_id_" + str(self.id)
        if not os.path.exists(path):
            os.mkdir(path)
        return path

    def guess_core_players(self):
        # get the most common steam ids in logs belonging to this team
        pass
    def trim_logs(self, count =4):
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
    
    def detailed_trim_logs(self, count =4):
        """ Check that there are at least count players
        from this roster on the SAME TEAM in each log.
        This involves requesting each log INDIVIDUALLY"""
        # for id in self.logs.keys():

        pass

    def print(self):
        # TODO
        pass


class Player():
    def __init__(self, id64, id3, name = ""):
        self.name = name
        self.id64 = id64
        self.id3 = id3
        self.log_ids = []
    def print(self):
        # TODO
        pass
    def get_log_ids(self, team_dir):
        filepath = team_dir + "/" + self.id64 + ".json"
        url_prefix = f"http://logs.tf/api/v1/log?player="
        url_ids = [str(self.id64)]
        log_batch = make_request(filepath, url_prefix, url_ids)[0]
        print(f"Was given {log_batch['results']} / {log_batch['total']} logs that contain player {self.id64}")
        self.log_ids = [log['id'] for log in log_batch['logs']]
