import os.path, Config
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from pprint import pprint
from Data import request_safe
from Roster import Roster
from Matchups import Matchup, PugTeam

class League():
    def __init__(self, id):
        self.id = id
        data = self.get_league_data()
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
        self.print_matchups()
        # count = 0
        # for roster in self.rosters:
        #     count += len(roster.potential_logs)
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
        path = os.path.join(Config.leagues_directory, str(self.id), "")
        if not os.path.exists(path):
            os.mkdir(path)
        return path

    def identify_matchups(self):
        self.matchups = []
        log_matchups = {}
        for roster in self.rosters:
            for log_side in roster.logs:
                log = log_side["log"]
                side = log_side["side"]
                if not log.id in log_matchups.keys():
                    log_matchups[log.id] = {"log": log, "rosters" : [(roster, side)]}
                else:
                    log_matchups[log.id]["rosters"].append((roster, side))
        for log_id in log_matchups.keys():
            matchup = log_matchups[log_id]
            self.matchups.append(Matchup(matchup["rosters"], matchup["log"]))
        
        for log_id in log_matchups.keys():
            matchup = log_matchups[log_id]
            blue_team = []
            red_team = []
            for team in match["rosters"]:
                if team[1] == 0:
                    red_team.append(team[0])
                else:
                    blue_team.append(team[0])
            assert len(self.blue_team) <= 1
            assert len(self.red_team) <= 1
            assert len(self.blue_team) + len(self.red_team) > 0

        # for m in self.matchups:
        #     print("blue team:", m.blue_team.name)
        #     print("red team:", m.red_team.name)
        #     print("result:", m.result)
        #     print("============")

    def print_matchups(self):
        for team in self.rosters:
            team_matchups = []
            pugscrim_matchups = []
            for matchup in self.matchups:
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
        cache_filepath = os.path.join(Config.league_response_cache, str(self.id) + ".json")
        url = os.path.join(Config.ozf_url_prefix, "leagues/", str(self.id))
        return request_safe(cache_filepath, url, Config.headers)["league"]

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
    