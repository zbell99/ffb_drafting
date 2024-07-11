import pandas as pd
import copy
from pulp import LpProblem, LpVariable, lpSum, value, LpMaximize
from itertools import chain
import helpers

def maximize_vorp(players, roster_size, vorp, remaining_settings, picks, player_position, full_team_settings, avail=[]):
    # Initialize model
    start_alpha = 2
    model = LpProblem("FantasyFootballOptimization", LpMaximize)
    
    # Decision Variables: Binary variables indicating if a player is selected and/or starting
    players_selected_v = LpVariable.dicts("PlayerSelectedV", players, cat='Binary')
    players_starting_v = LpVariable.dicts("PlayerStartingV", players, cat='Binary')
    players_selected_fv = LpVariable.dicts("PlayerSelectedFV", players, cat='Binary')
    players_starting_fv = LpVariable.dicts("PlayerStartingFV", players, cat='Binary')
    players_selected_sf = LpVariable.dicts("PlayerSelectedSF", players, cat='Binary')
    players_starting_sf = LpVariable.dicts("PlayerStartingSF", players, cat='Binary')
    
    # Objective Function: Maximize total VORP, with a bonus for starting players
    model += lpSum([vorp.loc[player]['VORP'] * players_selected_v[player] for player in players]) \
            + lpSum([vorp.loc[player]['VORP_FLEX'] * players_selected_fv[player] for player in players]) \
            + lpSum([vorp.loc[player]['VORP_SFLEX'] * players_selected_sf[player] for player in players]) \
            + lpSum([vorp.loc[player]['VORP'] * start_alpha * players_starting_v[player] for player in players]) \
            + lpSum([vorp.loc[player]['VORP_FLEX'] * start_alpha * players_starting_fv[player] for player in players]) \
            + lpSum([vorp.loc[player]['VORP_SFLEX'] * start_alpha * players_starting_sf[player] for player in players]), "TotalVORP"
    
    # Constraints -- all of these roster constraints based on who's already on the roster??
    # Roster size constraint
    model += lpSum([(players_selected_v[player]+players_selected_fv[player]+players_selected_sf[player]) for player in players]) == roster_size
    model += lpSum([(players_starting_v[player]+players_starting_fv[player]+players_starting_sf[player]) for player in players]) == remaining_settings['starting_sflex'] + remaining_settings['starting_k'] + remaining_settings['starting_dst']
    
    # Positional constraints: Minimum and maximum number of players at each position
    model += lpSum([(players_selected_v[player]+players_selected_fv[player]+players_selected_sf[player]) for player in players if player_position[player] == "QB"]) >= remaining_settings['min_qbs']
    model += lpSum([(players_selected_v[player]+players_selected_fv[player]+players_selected_sf[player]) for player in players if player_position[player] == "QB"]) <= remaining_settings['max_qbs']
    model += lpSum([(players_selected_v[player]+players_selected_fv[player]+players_selected_sf[player]) for player in players if player_position[player] == "RB"]) >= remaining_settings['min_rbs']
    model += lpSum([(players_selected_v[player]+players_selected_fv[player]+players_selected_sf[player]) for player in players if player_position[player] == "RB"]) <= remaining_settings['max_rbs']
    model += lpSum([(players_selected_v[player]+players_selected_fv[player]+players_selected_sf[player]) for player in players if player_position[player] == "WR"]) >= remaining_settings['min_wrs']
    model += lpSum([(players_selected_v[player]+players_selected_fv[player]+players_selected_sf[player]) for player in players if player_position[player] == "WR"]) <= remaining_settings['max_wrs']
    model += lpSum([(players_selected_v[player]+players_selected_fv[player]+players_selected_sf[player]) for player in players if player_position[player] == "TE"]) >= remaining_settings['min_tes']
    model += lpSum([(players_selected_v[player]+players_selected_fv[player]+players_selected_sf[player]) for player in players if player_position[player] == "TE"]) <= remaining_settings['max_tes']
    model += lpSum([(players_selected_v[player]+players_selected_fv[player]+players_selected_sf[player]) for player in players if player_position[player] == "K"]) == remaining_settings['starting_k']
    model += lpSum([(players_selected_v[player]+players_selected_fv[player]+players_selected_sf[player]) for player in players if player_position[player] == "DST"]) == remaining_settings['starting_dst']
    
    # Starting lineup constraints: Number of players at each position
    model += lpSum([players_starting_v[player] for player in players if player_position[player] == "QB"]) == remaining_settings['starting_qb']
    model += lpSum([players_starting_v[player] for player in players if player_position[player] == "RB"]) == remaining_settings['starting_rb']
    model += lpSum([players_starting_v[player] for player in players if player_position[player] == "WR"]) == remaining_settings['starting_wr']
    model += lpSum([players_starting_v[player] for player in players if player_position[player] == "TE"]) == remaining_settings['starting_te']
    # Flex position constraint
    model += lpSum([players_starting_fv[player] for player in players if player_position[player] in ["RB", "WR", "TE"]]) == remaining_settings['num_flex']
    # Superflex position constraint
    model += lpSum([players_starting_sf[player] for player in players if player_position[player] in ["QB", "RB", "WR", "TE"]]) == remaining_settings['num_sflex']
    # Defense and Kicker constraints
    model += lpSum([players_starting_v[player] for player in players if player_position[player] == "DST"]) == remaining_settings['starting_dst']
    model += lpSum([players_starting_v[player] for player in players if player_position[player] == "K"]) == remaining_settings['starting_k']
    #Bench constraints for type of player value (vorp vs flex vs superflex)
    # superflex bench spots == superflex start spots
    if full_team_settings['num_sflex'] > 0:
        model += lpSum([players_selected_sf[player] for player in players]) == remaining_settings['num_sflex'] + full_team_settings['num_sflex'] - remaining_settings['extra_sflex']
    else: #vorp qb bench spot = 1
        model += lpSum(players_selected_sf[player] for player in players) == 0
        model += lpSum([players_selected_v[player] for player in players if player_position[player] == "QB"]) <= remaining_settings['starting_qb'] + 1 - remaining_settings['extra_qb']
    # vorp bench spot for RB = 1
    model += lpSum([players_selected_v[player] for player in players if player_position[player] == "RB"]) == remaining_settings['starting_rb'] + 1 - remaining_settings['extra_rb']
    # vorp bench spot for WR = 1
    model += lpSum([players_selected_v[player] for player in players if player_position[player] == "WR"]) == remaining_settings['starting_wr'] + 1 - remaining_settings['extra_wr']
    # vorp bench spot for QB + TE = 1
    model += lpSum([players_selected_v[player] for player in players if player_position[player] == "TE"]) <= remaining_settings['starting_te'] + 1 - remaining_settings['extra_te']
    

    # Constraint: Any player starting must also be selected
    for player in players:
        model += (players_starting_v[player]) <= (players_selected_v[player])
        model += (players_starting_fv[player]) <= (players_selected_fv[player])
        model += (players_starting_sf[player]) <= (players_selected_sf[player])
        model += (players_selected_v[player]) + (players_selected_fv[player]) + (players_selected_sf[player]) <= 1
    
    # Constraint: For current pick, we can only select players who are still available from parameter
    model += lpSum([(players_selected_v[player]+players_selected_fv[player]+players_selected_sf[player]) for player in players]) >= len(picks)

    # Constraint: For next pick, we can only select players who are still available based on reduced pool from preprocessing
    if roster_size>1:
        if len(avail) > 0: #true if we're projecting an extra round (used for the main optimization)
            model += lpSum([(players_selected_v[player]+players_selected_fv[player]+players_selected_sf[player]) for player in avail]) >= len(picks) - 1
            if roster_size>2:
                for pick in picks[2:]:
                    available_players = avail[pick-picks[1]:]
                    model += lpSum([(players_selected_v[player]+players_selected_fv[player]+players_selected_sf[player]) for player in available_players]) >= len(picks) - picks.index(pick)

        # Constraint: For each pick, we can only select players who are still available based on reduced pool from ADP
        else: #true for the greedy algorithm used to set up the main optimization
            for pick in picks[1:]:
                available_players = players[pick-picks[0]:]
                model += lpSum([(players_selected_v[player]+players_selected_fv[player]+players_selected_sf[player]) for player in available_players]) >= len(picks) - picks.index(pick)
        
    # Solve the problem
    model.solve()
    
    # Extract results
    selected_players = [player for player in players if (players_selected_v[player].value() + players_selected_fv[player].value() + players_selected_sf[player].value()) == 1]
    starting_players = [player for player in players if (players_starting_v[player].value() + players_starting_fv[player].value() + players_starting_sf[player].value())  == 1]
    total_vorp = value(model.objective)

    sel_vorp = [player for player in players if players_selected_v[player].value() == 1]
    sel_flex = [player for player in players if players_selected_fv[player].value() == 1]
    sel_sflex = [player for player in players if players_selected_sf[player].value() == 1]
    print(f"Selected VORP: {sel_vorp}")
    print(f"Selected Flex: {sel_flex}")
    print(f"Selected SFlex: {sel_sflex}")

    start_vorp = [player for player in players if players_starting_v[player].value() == 1]
    start_flex = [player for player in players if players_starting_fv[player].value() == 1]
    start_sflex = [player for player in players if players_starting_sf[player].value() == 1]
    print(f"Starting VORP: {start_vorp}")
    print(f"Starting Flex: {start_flex}")
    print(f"Starting SFlex: {start_sflex}")
    print(f"Selected Players: {selected_players}")
    return selected_players, starting_players, total_vorp

def model_preprocess(df, roster_settings, personal_team, drafted_teams, drafted_pos):
    # Load data -- WONT NEED THIS
    df = pd.read_csv('vorp2024.csv')
    # get into the right format
    players = df['Player'].tolist()

    #vorp dictionary player as key, 3 vorps as tuple value
    vorp_df = df.set_index('Player')[['VORP', 'VORP_FLEX', 'VORP_SFLEX']]
    #player_position = df.set_index('Player')['Position'].to_dict()
    player_position = df.set_index('Player')['POS'].to_dict()
    #ADP = df.set_index('Player')['RedraftHalfPPR'].to_dict()
    ADP = df.set_index('Player')['ADP'].to_dict()

    #sort players by adp
    players = sorted(players, key=lambda x: ADP[x])

    #update draft in sleeper - WON'T NEED THIS
    # draft_id = "1084322358149611520"
    # draft_id = "1114593191476572160"
    # draft_id = "1114624923101650944"
    # roster_settings, scoring_type = setup.league_settings(draft_id)
    # data, player_to_index, qbs, rbs, wrs, tes, flex, names = setup.initialize_data()
    # drafted_teams, drafted_pos = setup.update_draft(draft_id, names, teams)


    roster_size = roster_settings['rounds']
    teams = roster_settings['teams']

    full_team_settings = helpers.full_position_constraints(roster_settings)

    drafted_players = list(chain(*drafted_teams.values()))

    drafted_teams_preprocess = copy.deepcopy(drafted_teams)
    drafted_pos_preprocess = copy.deepcopy(drafted_pos)
    drafted_players_preprocess = copy.deepcopy(drafted_players)

    #remove drafted players from available players
    available = [player for player in players if player not in drafted_players]
    sorted(available, key=lambda x: ADP[x])
  
    personal_picks = helpers.get_picks(personal_team, roster_size, teams)
    current_pick = len(drafted_players) + 1 #needs to be based on progress of the draft

    #personal picks remaining
    personal_picks = [pick for pick in personal_picks if pick >= current_pick]

    #project picks before your current pick
    if not personal_picks:
        print('Draft is over')
        return drafted_teams[personal_team]

    while current_pick < personal_picks[0]:
        cur_team = helpers.get_team_from_pick(current_pick, teams)
        picks = helpers.get_picks(cur_team, roster_size, teams)
        picks = [pick for pick in picks if pick >= current_pick]

        #get players drafted by current team
        drafted_cur = drafted_teams[cur_team]
        #adjust the roster size based on the number of players drafted
        roster_size = roster_settings['rounds'] - len(drafted_cur)
        print("Roster Size:", roster_size, len(drafted_cur))

        remaining_settings = helpers.remaining_position_constraints(drafted_pos, full_team_settings, cur_team)

        selected_players_temp, starting_players_temp, total_vorp_temp = maximize_vorp(available, roster_size, vorp_df, remaining_settings, picks, player_position, full_team_settings)

        #POST-PROCESS PICKED PLAYER
        new_pick = selected_players_temp[0]
        drafted_teams_preprocess[cur_team].append(new_pick)
        drafted_pos_preprocess[cur_team][player_position[new_pick]] += 1
        drafted_players_preprocess.append(new_pick)

        print("^^", current_pick, cur_team, new_pick, ADP[new_pick])
        print("")
        print("")

        #TODO: update available players
        available.remove(new_pick)
        current_pick += 1

    #project picks/players available for next round's pick
    available1 = copy.deepcopy(available)
    current_pick1 = current_pick
    print('Current Pick:', current_pick1)
    if len(personal_picks) <= 1:
        print('Only one pick left')
    else:
        while current_pick1 < personal_picks[1]:
            cur_team = helpers.get_team_from_pick(current_pick1, teams)
            picks = helpers.get_picks(cur_team, roster_size, teams)
            picks = [pick for pick in picks if pick >= current_pick1]

            #get players drafted by current team
            drafted_cur = drafted_teams[cur_team]
            #adjust the roster size based on the number of players drafted
            roster_size = roster_settings['rounds'] - len(drafted_cur)
            print("Roster Size:", roster_size, len(drafted_cur))
            remaining_settings = helpers.remaining_position_constraints(drafted_pos_preprocess, full_team_settings, cur_team)
            
            selected_players_temp, starting_players_temp, total_vorp_temp = maximize_vorp(available1, roster_size, vorp_df, remaining_settings, picks, player_position, full_team_settings)

            new_pick = selected_players_temp[0]
            drafted_teams_preprocess[cur_team].append(new_pick)
            drafted_pos_preprocess[cur_team][player_position[new_pick]] += 1
            drafted_players_preprocess.append(new_pick)
            print("^^", current_pick1, cur_team, new_pick, ADP[new_pick])
            print("")
            print("")

            available1.remove(new_pick)
            current_pick1 += 1

    #REAL PICK
    roster_size = roster_settings['rounds'] - len(drafted_teams[personal_team])

    remaining_settings = helpers.remaining_position_constraints(drafted_pos, full_team_settings, personal_team)

    # max_qbs = max(0, max_qbs - drafted_pos[personal_team]['QB'])
    # max_rbs = max(0, max_rbs - drafted_pos[personal_team]['RB'])
    # max_wrs = max(0, max_wrs - drafted_pos[personal_team]['WR'])
    # max_tes = max(0, max_tes - drafted_pos[personal_team]['TE'])

    # min_qbs = max(0, min_qbs - drafted_pos[personal_team]['QB'])
    # min_rbs = max(0, min_rbs - drafted_pos[personal_team]['RB'])
    # min_wrs = max(0, min_wrs - drafted_pos[personal_team]['WR'])
    # min_tes = max(0, min_tes - drafted_pos[personal_team]['TE'])

    # extra_rb = max(0, drafted_pos[personal_team]['RB'] - starting_rb)
    # extra_wr = max(0, drafted_pos[personal_team]['WR'] - starting_wr)
    # extra_te = max(0, drafted_pos[personal_team]['TE'] - starting_te)
    # extra_qb = max(0, drafted_pos[personal_team]['QB'] - starting_qb)
    # extra_flex = extra_rb + extra_wr + extra_te
    # #between 0, number of sflex spots - for model contsraint 
    # extra_sflex = min(roster_settings['slots_super_flex'], max(0, extra_rb + extra_wr + extra_te + extra_qb - num_flex))


    # starting_flex = max(0, starting_flex - (min(starting_rb, drafted_pos[personal_team]['RB']) + min(starting_wr, drafted_pos[personal_team]['WR']) + min(starting_te, drafted_pos[personal_team]['TE']) + min(num_flex, extra_flex)))
    # starting_sflex = max(0, starting_sflex - (min(starting_qb, drafted_pos[personal_team]['QB']) + min(starting_rb, drafted_pos[personal_team]['RB']) + min(starting_wr, drafted_pos[personal_team]['WR']) + min(starting_te, drafted_pos[personal_team]['TE']) + min(num_flex, extra_flex) + min(num_sflex, max(0, extra_flex-num_flex)+extra_qb)))
    # starting_qb = max(0, starting_qb - drafted_pos[personal_team]['QB'])
    # starting_rb = max(0, starting_rb - drafted_pos[personal_team]['RB'])
    # starting_wr = max(0, starting_wr - drafted_pos[personal_team]['WR'])
    # starting_te = max(0, starting_te - drafted_pos[personal_team]['TE'])
    # starting_k = max(0, starting_k - drafted_pos[personal_team]['K'])
    # starting_dst = max(0, starting_dst - drafted_pos[personal_team]['DST'])
    # num_flex = starting_flex - (starting_rb + starting_wr + starting_te)
    # num_sflex = starting_sflex - (starting_qb + starting_rb + starting_wr + starting_te + num_flex)

    # #binary extras - for model constraint
    # extra_rb = 1*(extra_rb > 0)
    # extra_wr = 1*(extra_wr > 0)
    # extra_te = 1*(extra_te > 0)
    # extra_qb = 1*(extra_qb > 0)

    # remaining_settings = {'min_qbs': min_qbs, 'max_qbs': max_qbs, 'min_rbs': min_rbs, 'max_rbs': max_rbs, 'min_wrs': min_wrs, 'max_wrs': max_wrs, 'min_tes': min_tes, 'max_tes': max_tes, 'starting_qb': starting_qb, 'starting_rb': starting_rb, 'starting_wr': starting_wr, 'starting_te': starting_te, 'starting_flex': starting_flex, 'num_flex': num_flex, 'starting_sflex': starting_sflex, 'num_sflex': num_sflex, 'starting_k': starting_k, 'starting_dst': starting_dst, 'extra_rb': extra_rb, 'extra_wr': extra_wr, 'extra_te': extra_te, 'extra_qb': extra_qb, 'extra_flex': extra_flex, 'extra_sflex': extra_sflex}
    
    # print('Roster Size:', roster_size)
    # print('QB:', min_qbs, max_qbs, starting_qb, 'current', drafted_pos[personal_team]['QB'])
    # print('RB:', min_rbs, max_rbs, starting_rb, 'current', drafted_pos[personal_team]['RB'])
    # print('WR:', min_wrs, max_wrs, starting_wr, 'current', drafted_pos[personal_team]['WR'])
    # print('TE:', min_tes, max_tes, starting_te, 'current', drafted_pos[personal_team]['TE'])
    # print('Flex:', starting_flex, 'current', drafted_pos[personal_team]['RB'] + drafted_pos[personal_team]['WR'] + drafted_pos[personal_team]['TE'])
    # print('Superflex:', starting_sflex, 'current', drafted_pos[personal_team]['QB'] + drafted_pos[personal_team]['RB'] + drafted_pos[personal_team]['WR'] + drafted_pos[personal_team]['TE'])
    print('Remaining Settings:', remaining_settings)
    print(available, roster_size, vorp_df, remaining_settings, personal_picks, player_position, full_team_settings, available1)
    return available, roster_size, vorp_df, remaining_settings, personal_picks, player_position, full_team_settings, available1

    # Run optimization with projections through first two picks
    selected_players, starting_players, total_vorp = maximize_vorp(available, roster_size, vorp_df, remaining_settings, personal_picks, player_position, full_team_settings, avail=available1)
    # Run optimization with projections through first pick
    # selected_players, starting_players, total_vorp = maximize_vorp(available, roster_size, vorp_df, remaining_settings, personal_picks)
    
    # Output results, showing each pos, player, vorp, and adp sorted by adp
    selected_players = sorted(selected_players, key=lambda x: ADP[x])
    # print('Selected Players')
    # for player in selected_players:
    #     print(player, player_position[player], ADP[player], vorp_df.loc[player]['VORP_FLEX'])
        
    # print('\nStarting Players')
    # starting_players = sorted(starting_players, key=lambda x: ADP[x])
    # for player in starting_players:
    #     print(player, player_position[player], ADP[player], vorp_df.loc[player]['VORP'], vorp_df.loc[player]['VORP_FLEX'], vorp_df.loc[player]['VORP_SFLEX'])