from pulp import *
import pandas as pd
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import setup
from itertools import chain
import copy

def optimize(draft_id):
    # Load data
    df = pd.read_csv('../vorp2024.csv')
    # get into the right format
    # df['Player'] = df['Player First Name'] + ' ' + df['Player Last Name']
    players = df['Player'].tolist()
    players = [player.replace('.', '') for player in players]
    df['Player'] = players

    #vorp dictionary player as key, 3 vorps as tuple value
    vorp_df = df.set_index('Player')[['VORP', 'VORP_FLEX', 'VORP_SFLEX']]
    #player_position = df.set_index('Player')['Position'].to_dict()
    player_position = df.set_index('Player')['POS'].to_dict()
    #ADP = df.set_index('Player')['RedraftHalfPPR'].to_dict()
    ADP = df.set_index('Player')['ADP'].to_dict()
    ADP = {k.replace('.', ''): v for k, v in ADP.items()}
    
    #sort players by adp
    players = sorted(players, key=lambda x: ADP[x])

    #update draft in sleeper
    draft_id = draft_id
    roster_settings, scoring_type = setup.league_settings(draft_id)
    print(roster_settings)

    # Constraints -- based on league settings
    min_qbs, max_qbs = roster_settings['slots_qb'], 3
    min_rbs, max_rbs = roster_settings['slots_rb']+roster_settings['slots_flex'], 6
    min_wrs, max_wrs = roster_settings['slots_wr']+roster_settings['slots_flex'], 6
    min_tes, max_tes = roster_settings['slots_te'], 2
    starting_qb = roster_settings['slots_qb']
    starting_rb = roster_settings['slots_rb']
    starting_wr = roster_settings['slots_wr']
    starting_te = roster_settings['slots_te']
    num_flex = roster_settings['slots_flex']
    try: 
        num_sflex = roster_settings['slots_super_flex']
    except:
        num_sflex = 0
    starting_flex = starting_rb + starting_wr + starting_te + num_flex
    starting_sflex = starting_qb + starting_flex + num_sflex
    starting_dst = roster_settings['slots_def']
    starting_k = roster_settings['slots_k']
    roster_size = roster_settings['rounds']
    teams = roster_settings['teams']
    
    data, player_to_index, qbs, rbs, wrs, tes, flex, names = setup.initialize_data()
    drafted_teams, drafted_pos = setup.update_draft(draft_id, names, teams)
    drafted_players = list(chain(*drafted_teams.values()))

    #remove drafted players from available players
    available = [player for player in players if player not in drafted_players]
    sorted(available, key=lambda x: ADP[x])
    
    def get_picks(pick, roster_size, teams):    
        picks = [pick, (2*teams+1)-pick]
        for i in range(2,roster_size):
            picks.append(picks[i-2]+(2*teams))
        return picks

    def get_team_from_pick(pick, teams): #looks complicated bc of team 12 edge cases
        if ((pick-1) // teams + 1) % 2 == 1:
            return (pick-1) % teams + 1
        else:
            return teams - ((pick-1) % teams)
        
    personal_team = 1
    personal_picks = get_picks(personal_team, roster_size, teams)
    
    current_pick = len(drafted_players) + 1 #needs to be based on progress of the draft
    
    #personal picks remaining
    personal_picks = [pick for pick in personal_picks if pick >= current_pick]

    #project picks before your current pick
    while current_pick < personal_picks[0]:
        cur_team = get_team_from_pick(current_pick, teams)
        picks = get_picks(cur_team, roster_size, teams)
        picks = [pick for pick in picks if pick >= current_pick]

        #get players drafted by current team
        drafted_cur = drafted_teams[cur_team]
        #adjust the roster size based on the number of players drafted
        roster_size = roster_settings['rounds'] - len(drafted_cur)

        #TODO: adjust the position size based on the number of players drafted
        qb_low = max(0, min_qbs - drafted_pos[cur_team]['QB'])
        rb_low = max(0, min_rbs - drafted_pos[cur_team]['RB'])
        wr_low = max(0, min_wrs - drafted_pos[cur_team]['WR'])
        te_low = max(0, min_tes - drafted_pos[cur_team]['TE'])

        qb_high = max(0, max_qbs - drafted_pos[cur_team]['QB'])
        rb_high = max(0, max_rbs - drafted_pos[cur_team]['RB'])
        wr_high = max(0, max_wrs - drafted_pos[cur_team]['WR'])
        te_high = max(0, max_tes - drafted_pos[cur_team]['TE'])

        qb_start = max(0, starting_qb - drafted_pos[cur_team]['QB'])
        rb_start = max(0, starting_rb - drafted_pos[cur_team]['RB'])
        wr_start = max(0, starting_wr - drafted_pos[cur_team]['WR'])
        te_start = max(0, starting_te - drafted_pos[cur_team]['TE'])
        flex_starting = max(0, starting_flex - (min(starting_rb+num_flex,drafted_pos[cur_team]['RB']) + min(starting_wr+num_flex, drafted_pos[cur_team]['WR']) + min(starting_te + num_flex, drafted_pos[cur_team]['TE'])))
        sflex_starting = max(0, starting_sflex - (min(starting_qb+num_sflex, drafted_pos[cur_team]['QB']) + min(starting_rb+num_flex+num_sflex, drafted_pos[cur_team]['RB']) + min(starting_wr+num_flex+num_sflex, drafted_pos[cur_team]['WR']) + max(starting_te+num_flex+num_sflex, drafted_pos[cur_team]['TE'])))
        k_start = max(0, starting_k - drafted_pos[cur_team]['K'])
        dst_start = max(0, starting_dst - drafted_pos[cur_team]['DST'])

        roster_vorp = {'min_qbs': qb_low, 'max_qbs': qb_high, 'min_rbs': rb_low, 'max_rbs': rb_high, 'min_wrs': wr_low, 'max_wrs': wr_high, 'min_tes': te_low, 'max_tes': te_high, 'starting_qb': qb_start, 'starting_rb': rb_start, 'starting_wr': wr_start, 'starting_te': te_start, 'starting_flex': flex_starting, 'starting_sflex': sflex_starting, 'starting_k': k_start, 'starting_dst': dst_start}
        
        #TODO: run opti with adjusted positions
        selected_players_temp, starting_players_temp, total_vorp_temp = maximize_vorp(available, roster_size, vorp_df, roster_vorp, picks, player_position)

        #TODO: extract the model's next draft pick and add to drafted players, drafted[team]
        new_pick = selected_players_temp[0]
        drafted_teams[cur_team].append(new_pick)
        drafted_players.append(new_pick)

        print(current_pick, new_pick, ADP[new_pick])

        #TODO: update available players
        available.remove(new_pick)
        current_pick += 1

    #project picks/players available for next round's pick
    available1 = copy.deepcopy(available)
    current_pick1 = current_pick
    print('Current Pick:', current_pick1)
    while current_pick1 < personal_picks[1]:
        cur_team = get_team_from_pick(current_pick1, teams)
        picks = get_picks(cur_team, roster_size, teams)
        picks = [pick for pick in picks if pick >= current_pick1]

        #get players drafted by current team
        drafted_cur = drafted_teams[cur_team]
        #adjust the roster size based on the number of players drafted
        roster_size = roster_settings['rounds'] - len(drafted_cur)

        #TODO: adjust the position size based on the number of players drafted
        qb_low = max(0, min_qbs - drafted_pos[cur_team]['QB'])
        rb_low = max(0, min_rbs - drafted_pos[cur_team]['RB'])
        wr_low = max(0, min_wrs - drafted_pos[cur_team]['WR'])
        te_low = max(0, min_tes - drafted_pos[cur_team]['TE'])

        qb_high = max(0, max_qbs - drafted_pos[cur_team]['QB'])
        rb_high = max(0, max_rbs - drafted_pos[cur_team]['RB'])
        wr_high = max(0, max_wrs - drafted_pos[cur_team]['WR'])
        te_high = max(0, max_tes - drafted_pos[cur_team]['TE'])

        qb_start = max(0, starting_qb - drafted_pos[cur_team]['QB'])
        rb_start = max(0, starting_rb - drafted_pos[cur_team]['RB'])
        wr_start = max(0, starting_wr - drafted_pos[cur_team]['WR'])
        te_start = max(0, starting_te - drafted_pos[cur_team]['TE'])
        flex_starting = max(0, starting_flex - (min(starting_rb+num_flex,drafted_pos[cur_team]['RB']) + min(starting_wr+num_flex, drafted_pos[cur_team]['WR']) + min(starting_te + num_flex, drafted_pos[cur_team]['TE'])))
        sflex_starting = max(0, starting_sflex - (min(starting_qb+num_sflex, drafted_pos[cur_team]['QB']) + min(starting_rb+num_flex+num_sflex, drafted_pos[cur_team]['RB']) + min(starting_wr+num_flex+num_sflex, drafted_pos[cur_team]['WR']) + min(starting_te+num_flex+num_sflex, drafted_pos[cur_team]['TE'])))
        k_start = max(0, starting_k - drafted_pos[cur_team]['K'])
        dst_start = max(0, starting_dst - drafted_pos[cur_team]['DST'])

        roster_vorp = {'min_qbs': qb_low, 'max_qbs': qb_high, 'min_rbs': rb_low, 'max_rbs': rb_high, 'min_wrs': wr_low, 'max_wrs': wr_high, 'min_tes': te_low, 'max_tes': te_high, 'starting_qb': qb_start, 'starting_rb': rb_start, 'starting_wr': wr_start, 'starting_te': te_start, 'starting_flex': flex_starting, 'starting_sflex': sflex_starting, 'starting_k': k_start, 'starting_dst': dst_start}

        #TODO: run opti with adjusted positions
        selected_players_temp, starting_players_temp, total_vorp_temp = maximize_vorp(available1, roster_size, vorp_df, roster_vorp, picks, player_position)

        #TODO: extract the model's next draft pick and add to drafted players, drafted[team]
        new_pick = selected_players_temp[0]
        drafted_teams[cur_team].append(new_pick)
        drafted_players.append(new_pick)
        print(current_pick1, new_pick, ADP[new_pick])

        #TODO: update available players
        available1.remove(new_pick)

        current_pick1 += 1

    #reset data for the actual model
    data, player_to_index, qbs, rbs, wrs, tes, flex, names = setup.initialize_data()
    drafted_teams, drafted_pos = setup.update_draft(draft_id, names, teams)
    drafted_players = list(chain(*drafted_teams.values()))

    roster_size = roster_settings['rounds'] - len(drafted_teams[cur_team])

    max_qbs = max(0, max_qbs - drafted_pos[personal_team]['QB'])
    max_rbs = max(0, max_rbs - drafted_pos[personal_team]['RB'])
    max_wrs = max(0, max_wrs - drafted_pos[personal_team]['WR'])
    max_tes = max(0, max_tes - drafted_pos[personal_team]['TE'])

    min_qbs = max(0, min_qbs - drafted_pos[personal_team]['QB'])
    min_rbs = max(0, min_rbs - drafted_pos[personal_team]['RB'])
    min_wrs = max(0, min_wrs - drafted_pos[personal_team]['WR'])
    min_tes = max(0, min_tes - drafted_pos[personal_team]['TE'])

    starting_flex = max(0, starting_flex - (min(starting_rb+num_flex,drafted_pos[cur_team]['RB']) + min(starting_wr+num_flex, drafted_pos[cur_team]['WR']) + min(starting_te + num_flex, drafted_pos[cur_team]['TE'])))
    starting_sflex = max(0, starting_sflex - (min(starting_qb+num_sflex, drafted_pos[cur_team]['QB']) + min(starting_rb+num_flex+num_sflex, drafted_pos[cur_team]['RB']) + min(starting_wr+num_flex+num_sflex, drafted_pos[cur_team]['WR']) + min(starting_te+num_flex+num_sflex, drafted_pos[cur_team]['TE'])))
    starting_qb = max(0, starting_qb - drafted_pos[personal_team]['QB'])
    starting_rb = max(0, starting_rb - drafted_pos[personal_team]['RB'])
    starting_wr = max(0, starting_wr - drafted_pos[personal_team]['WR'])
    starting_te = max(0, starting_te - drafted_pos[personal_team]['TE'])

    roster_vorp = {'min_qbs': min_qbs, 'max_qbs': max_qbs, 'min_rbs': min_rbs, 'max_rbs': max_rbs, 'min_wrs': min_wrs, 'max_wrs': max_wrs, 'min_tes': min_tes, 'max_tes': max_tes, 'starting_qb': starting_qb, 'starting_rb': starting_rb, 'starting_wr': starting_wr, 'starting_te': starting_te, 'starting_flex': starting_flex, 'starting_sflex': starting_sflex, 'starting_k': starting_k, 'starting_dst': starting_dst}
    
    print('TEST')
    #print(drafted_pos[personal_team]['RB'] + drafted_pos[personal_team]['WR'] + drafted_pos[personal_team]['TE'])
    print('Roster Size:', roster_size)
    print('QB:', min_qbs, max_qbs, starting_qb, 'current', drafted_pos[personal_team]['QB'])
    print('RB:', min_rbs, max_rbs, starting_rb, 'current', drafted_pos[personal_team]['RB'])
    print('WR:', min_wrs, max_wrs, starting_wr, 'current', drafted_pos[personal_team]['WR'])
    print('TE:', min_tes, max_tes, starting_te, 'current', drafted_pos[personal_team]['TE'])
    print('Flex:', starting_flex, 'current', drafted_pos[personal_team]['RB'] + drafted_pos[personal_team]['WR'] + drafted_pos[personal_team]['TE'])
    print('Superflex:', starting_sflex, 'current', drafted_pos[personal_team]['QB'] + drafted_pos[personal_team]['RB'] + drafted_pos[personal_team]['WR'] + drafted_pos[personal_team]['TE'])
    
    # Run optimization
    selected_players, starting_players, total_vorp = maximize_vorp(available, roster_size, vorp_df, roster_vorp, personal_picks,player_position, avail=available1)
    
    # Output results, showing each pos, player, vorp, and adp sorted by adp
    selected_players = sorted(selected_players, key=lambda x: ADP[x])
    print('Selected Players')
    for player in selected_players:
        print(player, player_position[player], ADP[player], vorp_df.loc[player]['VORP_FLEX'])
        
    print('\nStarting Players')
    starting_players = sorted(starting_players, key=lambda x: ADP[x])
    for player in starting_players:
        print(player, player_position[player], ADP[player], vorp_df.loc[player]['VORP_FLEX'])
        
    return selected_players[0]
        
def maximize_vorp(players, roster_size, vorp, roster_vorp, picks, player_position, avail=[]):
    # Initialize model
    model = LpProblem("FantasyFootballOptimization", LpMaximize)
    
    # Decision Variables: Binary variables indicating if a player is selected and/or starting
    players_selected = LpVariable.dicts("PlayerSelected", players, cat='Binary')
    players_starting = LpVariable.dicts("PlayerStarting", players, cat='Binary')
    
    # Objective Function: Maximize total VORP, with a bonus for starting players
    #TODO: Specify different types of VORP based on the spot selected
    model += lpSum([vorp.loc[player]['VORP_FLEX'] * players_selected[player] for player in players]) \
            + lpSum([vorp.loc[player]['VORP'] * 2 * players_starting[player] for player in players]), "TotalVORP"
    
    # Constraints -- all of these roster constraints based on who's already on the roster??
    # Roster size constraint
    model += lpSum([players_selected[player] for player in players]) == roster_size
    
    # Positional constraints: Minimum and maximum number of players at each position
    model += lpSum([players_selected[player] for player in players if player_position[player] == "QB"]) >= roster_vorp['min_qbs']
    model += lpSum([players_selected[player] for player in players if player_position[player] == "QB"]) <= roster_vorp['max_qbs']
    model += lpSum([players_selected[player] for player in players if player_position[player] == "RB"]) >= roster_vorp['min_rbs']
    model += lpSum([players_selected[player] for player in players if player_position[player] == "RB"]) <= roster_vorp['max_rbs']
    model += lpSum([players_selected[player] for player in players if player_position[player] == "WR"]) >= roster_vorp['min_wrs']
    model += lpSum([players_selected[player] for player in players if player_position[player] == "WR"]) <= roster_vorp['max_wrs']
    model += lpSum([players_selected[player] for player in players if player_position[player] == "TE"]) >= roster_vorp['min_tes']
    model += lpSum([players_selected[player] for player in players if player_position[player] == "TE"]) <= roster_vorp['max_tes']
    
    
    # Starting lineup constraints: Number of players at each position
    model += lpSum([players_starting[player] for player in players if player_position[player] == "QB"]) >= roster_vorp['starting_qb']
    model += lpSum([players_starting[player] for player in players if player_position[player] == "RB"]) >= roster_vorp['starting_rb']
    model += lpSum([players_starting[player] for player in players if player_position[player] == "WR"]) >= roster_vorp['starting_wr']
    model += lpSum([players_starting[player] for player in players if player_position[player] == "TE"]) >= roster_vorp['starting_te']
    # Flex position constraint
    model += lpSum([players_starting[player] for player in players if player_position[player] in ["RB", "WR", "TE"]]) == roster_vorp['starting_flex']
    # Superflex position constraint
    model += lpSum([players_starting[player] for player in players if player_position[player] in ["QB", "RB", "WR", "TE"]]) == roster_vorp['starting_sflex']
    # Defense and Kicker constraints
    model += lpSum([players_selected[player] for player in players if player_position[player] == "DST"]) == roster_vorp['starting_dst']
    model += lpSum([players_selected[player] for player in players if player_position[player] == "K"]) == roster_vorp['starting_k']
    

    # Constraint: Any player starting must also be selected
    for player in players:
        model += (players_starting[player]) <= (players_selected[player])
    
    # Constraint: For current pick, we can only select players who are still available from parameter
    model += lpSum([players_selected[player] for player in players]) >= len(picks)

    # Constraint: For next pick, we can only select players who are still available based on reduced pool from preprocessing
    if len(avail) > 0:
        model += lpSum([players_selected[player] for player in avail]) >= len(picks) - 1
        print(picks[0], len(players), players)
        print(picks[1], len(avail), avail)
        for pick in picks[2:]:
            available_players = avail[pick-picks[1]:]
            print(pick, len(available_players), available_players)
            model += lpSum([players_selected[player] for player in available_players]) >= len(picks) - picks.index(pick)
    
#     for pick in picks[1:]:
#             available_players = players[pick-picks[0]:]
#             model += lpSum([players_selected[player] for player in available_players]) >= len(picks) - picks.index(pick)

    # Constraint: For each pick, we can only select players who are still available based on reduced pool from ADP
    else:
        for pick in picks[1:]:
            available_players = players[pick-picks[0]:]
            model += lpSum([players_selected[player] for player in available_players]) >= len(picks) - picks.index(pick)
        
    # Solve the problem
    model.solve()
    
    # Extract results
    selected_players = [player for player in players if players_selected[player].value() == 1]
    starting_players = [player for player in players if players_starting[player].value() == 1]
    total_vorp = value(model.objective)
    
    #df of each player and whether they are selected or starting
    # player_df = pd.DataFrame(players, columns=['Player'])
    # player_df['Selected'] = player_df['Player'].apply(lambda x: players_selected[x].value())
    # player_df['Starting'] = player_df['Player'].apply(lambda x: players_starting[x].value())

    return selected_players, starting_players, total_vorp #, player_df

#create a class for the draft
class Draft:
    def __init__(self, draft_settings, qb_projections, rb_projections, wr_projections, te_projections, k_projections, dst_projections, adp):
        #number of teams
        #scoring settings
        #number of rounds
        #players available
        #current pick
        #class of each team

        #draft settings include number of teams, scoring settings, number of rounds
        
        self.num_teams = num_teams

        self.draft_settings = draft_settings


        self.qb_projections = qb_projections
        self.rb_projections = rb_projections
        self.wr_projections = wr_projections
        self.te_projections = te_projections
        self.k_projections = k_projections
        self.dst_projections = dst_projections

        self.adp = adp

        self.players_available = []

        #create a Team class for each team
        self.teams = []
        for i in range(self.num_teams):
            self.teams.append(Team(pick=i+1))


    def calculate_projections(self, dataset):
        #TODO
        #calculate projections for each player
        #return a list of players sorted by projections
        return dataset
    
    def calculate_vorp(self, dataset):
        #TODO
        #calculate vorp for each player
        #return a list of players sorted by vorp
        return dataset

        # dataset['VORP'] = dataset['VORP'] = dataset['Points'] - dataset['VORP']
        # return dataset.sort_values('VORP', ascending=False)



class Team:
    def __init__(self, pick):
        #list of picks
        #players drafted
        #position needs
        self.pick = pick
        