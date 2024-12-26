import player as player

class Team:
    def __init__(self, team_id: str, pick: int, roster: list[player.Player]):
        self.team_id = team_id
        self.name = "Team " + team_id
        self.pick = pick
        self.roster = roster