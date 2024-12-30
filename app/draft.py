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
        rosters = draft_payload['rosters']
        
        self.teams = {team.Team(team_id=t, pick=rosters[t], roster=[]) for t in rosters}

        # #1. load projection files
        # projection_files = raw_projection_data()
        # self.projection_data = calculate_projections(projection_files) #all projection categories for all players (current function does not have this), use specific scoring settings
        # self.projection_data = calculate_vorp(self.projection_data, self.roster_settings, self.num_teams) #add VORP to projection data

        # #2. load adp data
        # adp_files = raw_adp_data()
        # #3. connect names
        # self.projection_data = assign_adp(self.projection_data, adp_files, self.scoring_settings)

        #simulated data for testing
        import pandas as pd
        self.projection_data = pd.DataFrame({'Player': ['Player1', 'Player2', 'Player3', 'Player4', 'Player5'],
                                                'ID': ['1234', '2345', '3456', '4567', '5678'],
                                                'Team': ['Team1', 'Team2', 'Team3', 'Team4', 'Team5'],
                                                'POS': ['QB', 'RB', 'WR', 'TE', 'K'],
                                                'PASS_ATT': [1, 2, 3, 4, 5],
                                                'PASS_YDS': [1, 2, 3, 4, 5],
                                                'PASS_TDS': [1, 2, 3, 4, 5],
                                                'INT': [1, 2, 3, 4, 5],
                                                'FUM': [1, 2, 3, 4, 5],
                                                'RUSH_ATT': [1, 2, 3, 4, 5],
                                                'RUSH_YDS': [1, 2, 3, 4, 5],
                                                'RUSH_TDS': [1, 2, 3, 4, 5],
                                                'REC': [1, 2, 3, 4, 5],
                                                'REC_YDS': [1, 2, 3, 4, 5],
                                                'REC_TDS': [1, 2, 3, 4, 5],
                                                'KICKER_PTS': [1, 2, 3, 4, 5],
                                                'DEF_PTS': [1, 2, 3, 4, 5],
                                                'FPTS': [1, 2, 3, 4, 5],
                                                'VORP': [1, 2, 3, 4, 5],
                                                'ADP': [1, 2, 3, 4, 5]})



        self.players = {player.Player(p) for i, p in self.projection_data.iterrows()}
        self.models = {
            "Top Player": None,
            "Player 2": None,
            "Player 3": None,
            "QB": None,
            "RB": None,
            "WR": None,
            "TE": None,
            "K": None,
            "DEF": None  
        }

        # ASSUME STARTING AT ROUND 1
        self.current_pick = 1
        self.drafted_players = {}
        self.available_players = self.players
        self.projected_picks = {}
    

    def _calculate_projections(self):
        '''
        Calculates the projections for each player
        '''
        pass


    def _calculate_vorp(self):
        '''
        Calculates the VORP for each player
        '''
        pass


    def _project_picks(self, num_picks):
        '''
        Projects the next num_picks picks.
            - Runs the optimization model to determine who each team will pick over the next two rounds
            - Updates the projected_picks dictionary with the projected picks
        '''
        for i in range(num_picks):
            self.projected_picks[self.current_pick+i] = self.optimize_draft(i)


    def reset_draft(self):
        ''' 
        Resets the draft to the beginning
        '''
        self.drafted_players = {}
        self.available_players = self.players
        for t in self.teams:
            t.roster = []
        return self

    
    def update_draft(self, picks):
        ''' 
        Looks at the picks endpoint of the draft and updates the drafted players and teams
        '''
        for pick in picks:
            player = self.available_players[pick['player_id']]
            self.drafted_players[player] = pick['round']
            self.available_players.remove(player)
            self.teams[pick['team_id']].roster.append(player)

        self._project_picks(20)
        return self


    def optimize_draft(self, team: str):
        '''
        Optimizes the draft
        '''
        

        ''' THIS MUST RETURN A MODEL OBJECT: 
            NEXT PLAYER TO PICK
            OPTIMAL ROSTER
            SCORE
        '''
        self.models[team] = model.Model(team, self.current_pick)

