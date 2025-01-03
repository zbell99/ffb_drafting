import pandas as pd

import league_settings as settings
import app.model as model
import team as team
import player as player
from payload_processor_factory import get_payload_processor
import app.helpers as helpers
import constants

class Draft:
    def __init__(self, host: str, id: str, name: str):
        self.host = host
        self.id = id
        self.name = name
        
        processor = get_payload_processor(self.host)
        draft_payload = processor.process(self.id)
        
        self.num_teams = draft_payload['num_teams']
        self.rounds = draft_payload['rounds']
        self.roster_settings = settings.RosterSettings(draft_payload['roster_settings'])
        self.scoring_settings = settings.ScoringSettings(draft_payload['scoring_settings'])
        if self.roster_settings.slots_sflex > 0:
            self.scoring_format = '2qb'
        rosters = draft_payload['rosters']
        
        self.teams = {team.Team(team_id=t, pick=rosters[t], roster=[]) for t in rosters}

        #projection data
        projection_files = self.raw_projection_data()
        projection_data = self.process_projection_data(projection_files)
        projection_data = self.calculate_projections(projection_data)
        projection_data = self.calculate_vorp(projection_data) #add VORP to projection data

        #adp data
        adp = self.raw_adp_data()

        # #3. connect names
        projection_data = self.assign_adp(projection_data, adp)

        #simulated data for testing
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
    

    def raw_projection_data(self):
        '''
        Parameters:
            - None

        Loads the raw projection data

        Returns a dictionary of dataframes with the raw projection data
        '''
        raw_data = {}
        raw_data_dict = constants.FANTASYPROS_FILES
        for pos in raw_data_dict:
            raw_data[pos] = pd.read_csv(raw_data_dict[pos])
        return raw_data


    def process_projection_data(self, projection_files):
        '''
        Parameters:
            - projection_files: dictionary of dataframes with the raw projection data

        Processes the projection data:
            - Standardizes the column names
            - Adds the other columns in the scoring settings
            - Standardizes the column types
            - Adds the position column
        
        Returns a dataframe with the concatenated position data
        '''

        for pos in projection_files:
            #drop na rows
            projection_files[pos] = projection_files[pos].dropna()

            #standardize column names
            projection_files[pos] = projection_files[pos].rename(columns=constants.FANTASYPROS_RENAMING[pos])
            
            #add the other columns in scoring settings
            projection_files[pos] = helpers.fill_missing_columns(projection_files[pos], self.scoring_settings.__dict__.keys())
            projection_files[pos] = helpers.fill_missing_columns(projection_files[pos], ['KICKER_PTS', 'DEF_PTS'])

            #standardize column types
            projection_files[pos] = helpers.standardize_column_types(projection_files[pos], to_exclude=['Player', 'Team'])

            #add position column
            projection_files[pos]['POS'] = constants.FANTASYPROS_POSITIONS[pos]

        #create a df concatenating all the position data via for loop
        position_data = pd.concat([projection_files[pos][constants.FANTASYPROS_POSITIONS] for pos in projection_files])
        return position_data      


    def calculate_projections(self, position_data):
        '''
        Parameters:
            - position_data: dataframe with all the position data

        Calculates the projections for each player

        Returns the dataframe with the calculated projections
        '''
        starter_cols = [col for col in constants.FANTASYPROS_COLS if col not in ['Player', 'Team', 'POS', 'KICKER_PTS', 'DEF_PTS']]
        position_data['FPTS'] = sum([position_data[col]*self.scoring_settings.__dict__[col] for col in starter_cols])
        position_data['FPTS'] += position_data['REC']*self.scoring_settings.TE_PREM
        position_data['FPTS'] += position_data['KICKER_PTS'] + position_data['DEF_PTS']
        return position_data


    def _set_vorp_replacement_level(self):
        replacements = {}
        replacements['QB'] = int((self.num_teams * (self.roster_settings.slots_qb + self.roster_settings.slots_sflex + 0.25))//1 + 1)
        replacements['RB'] = int((self.num_teams * (self.roster_settings.slots_rb + 0.5*self.roster_settings.slots_flex + self.roster_settings.slots_bn*0.3))//1 + 1)
        replacements['WR'] = int(self.num_teams * (self.roster_settings.slots_wr + 0.5*self.roster_settings.slots_flex + self.roster_settings.slots_bn*0.3)//1 + 1)
        replacements['TE'] = int(self.num_teams * (self.roster_settings.slots_te + 0*self.roster_settings.slots_flex + 0.75)//1 + 1)
        replacements['K'] = self.num_teams * self.roster_settings.slots_k
        replacements['DEF'] = self.num_teams * self.roster_settings.slots_def
        replacements['FLEX'] = self.num_teams * (self.rounds-self.roster_settings.slots_k-self.roster_settings.slots_def-self.roster_settings.slots_qb)
        replacements['SFLEX'] = self.num_teams * (self.rounds-self.roster_settings.slots_k-self.roster_settings.slots_def)
        return replacements


    def calculate_vorp(self, position_data):
        '''
        Calculates the VORP, Flex VORP, and SFlex VORP for each player
        '''
        replacements = self._set_vorp_replacement_level()
        position_data['VORP'] = 0

        #REFACTOR BELOW
        for pos in ['QB', 'RB', 'WR', 'TE', 'K', 'DEF']:
            x = position_data['POS'] == pos
            position_data.loc[x, 'VORP'] = position_data.loc[x, 'FPTS'] - position_data.loc[x, 'FPTS'].nlargest(replacements[pos]).min()

        position_data['VORP_FLEX'] =  position_data['VORP']
        temp_flex = position_data['POS'].isin(['RB', 'WR', 'TE'])
        position_data.loc[temp_sflex, 'VORP_FLEX'] = position_data.loc[temp_flex, 'FPTS'] - position_data.loc[temp_flex, 'FPTS'].nlargest(replacements['FLEX']).min()

        
        position_data['VORP_SFLEX'] =  position_data['VORP_FLEX']
        temp_sflex = position_data['POS'].isin(['QB', 'RB', 'WR', 'TE'])
        position_data.loc[temp_sflex, 'VORP_SFLEX'] = position_data.loc[temp_sflex, 'FPTS'] - position_data.loc[temp_sflex, 'FPTS'].nlargest(replacements['SFLEX']).min()

        #round to 2 decimal places
        position_data[['VORP', 'VORP_FLEX', 'VORP_SFLEX']] = position_data[['VORP', 'VORP_FLEX', 'VORP_SFLEX']].round(2)

        return position_data
    

    def raw_adp_data():
        return pd.read_csv("adp/ADP2024.csv")
    

    def assign_adp(self, position_data, adp):
        '''
        Parameters:
            - position_data: dataframe with all the position data
            - adp_files: dataframe with the adp data

        Assigns the ADP to the position data

        Returns the dataframe with the ADP assigned
        '''
        adp['Player'] = adp['Player First Name'] + ' ' + adp['Player Last Name']
        adp_players = adp['Player'].unique()

        # Create a dictionary to store the matches
        matches = {}
        for player in position_data['Player'].unique():
            #match player names
            matches = helpers.fuzzy_match(item=player, list=adp_players, matches=matches, score=95)

        # Replace the player names in df with the matches
        position_data['Player'] = position_data['Player'].replace(matches)
        #replace JAC with JAX
        position_data['Team'] = position_data['Team'].replace('JAC', 'JAX')

        #TODO: THIS IS SLEEPER SPECIFIC -- PROBABLY NEED A FACTORY
        league_type = {'ppr': 'Redraft PPR ADP', 'half_ppr': 'Redraft Half PPR ADP', 'std': 'Redraft Half PPR ADP', '2qb': 'Redraft SF ADP'}
        draft_type = league_type[self.scoring_format]

        # Merge df and adp on player and team
        position_data = position_data.merge(adp[['Player', 'Player First Name', 'Player Last Name', 'Player Team', draft_type]], how='left', left_on=['Player', 'Team'], right_on=['Player', 'Player Team'])
        #rename columns
        position_data = position_data.rename(columns={draft_type: 'ADP'})
        position_data['ADP'].fillna(2*self.rounds*self.num_teams, inplace=True)

        #drop periods in player name
        position_data['Player'] = position_data['Player'].str.replace('.', '')

        return position_data
    

    def _project_picks(self, num_picks):
        '''
        Projects the next num_picks picks.
            - Runs the optimization model to determine who each team will pick over the next two rounds
            - Updates the projected_picks dictionary with the projected picks
        '''
        for i in range(num_picks):
            self.projected_picks[self.current_pick+i] = model.Model()


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

