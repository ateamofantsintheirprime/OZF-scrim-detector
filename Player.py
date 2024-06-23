import os, config
from Data import request_safe
from Log import MiniLog

class Player():
    def __init__(self, id64, id3, ozfid, name = "" ):
        self.ozfid = ozfid
        self.name = name
        self.id64 = id64
        self.id3 = id3
        self.minilogs = []

    def print(self):
        # TODO
        pass

    def update_minilogs(self):
        # print(f"Requesting Player: <{self.name}>, log search")
        cache_filepath = os.path.join(config.player_log_search_cache, self.id64 + ".json")
        url = config.logs_url_prefix + "?player=" + self.id64
        log_search = request_safe(cache_filepath, url)
        # print(f"Was given {log_search['results']} / {log_search['total']} logs that contain player {log_search['parameters']['player']}")
        self.minilogs = [MiniLog(log) for log in log_search['logs']]