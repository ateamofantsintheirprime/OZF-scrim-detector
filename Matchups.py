class Matchup():
    def __init__(self, teams, log):

        self.blue_team
        self.red_team

        self.result = log.score
        player_threshhold = 4
        for roster in teams:
            red_count = len([player.id3 for player in roster.players if player.id3 in log.red_team])
            blue_count = len([player.id3 for player in roster.players if player.id3 in log.blue_team])

            if red_count > blue_count:
                self.red_team = roster
            else:
                self.blue_team = roster
class PugTeam():
    def __init__(self, players):
        self.players = players
