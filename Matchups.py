from Roster import Roster
from Log import FullLog
class Matchup():
    def __init__(self, teams: list[Roster], log: FullLog):

        self.blue_team: Roster = []
        self.red_team: Roster = []
        self.log = log

        self.result = log.score

        for team in teams:
            if team[1] == 0:
                self.red_team.append(team[0])
            else:
                self.blue_team.append(team[0])
        assert len(self.blue_team) <= 1
        assert len(self.red_team) <= 1
        assert len(self.blue_team) + len(self.red_team) > 0

        if len(self.blue_team) == 0:
            self.blue_team = PugTeam(log.blue_team)
        else:
            self.blue_team = self.blue_team[0]

        if len(self.red_team) == 0:
            self.red_team = PugTeam(log.red_team)
        else:
            self.red_team = self.red_team[0]


class PugTeam():
    def __init__(self, player_id3s):
        self.id = 0
        self.name = "unnamed"
        self.players = player_id3s
