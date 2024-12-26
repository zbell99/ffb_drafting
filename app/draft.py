import league_settings as settings
import model as model
import team as team
import player as player
from payload_processor_factory import get_payload_processor

class Draft:
    def __init__(self, host: str, id: str, name: str):
        self.host = host
        self.id = id
        self.name = name
        
        processor = get_payload_processor(host)
        draft_payload = processor.process(id)
        
        self.num_teams = draft_payload['num_teams']
        self.rounds = draft_payload['rounds']
        self.roster_settings = settings.RosterSettings(draft_payload['roster_settings'])
        self.scoring_settings = settings.ScoringSettings(draft_payload['scoring_settings'])
        self.rosters = draft_payload['rosters']
        
        self.teams = {team.Team(team_id=t, pick=self.rosters[t], roster=[]) for t in self.rosters}
        #TODO: everything below this line is a placeholder
        self.players = {player.Player() for p in range(1000)}
        self.drafted_players = {}
        self.remaining_players = self.players
        self.model = []