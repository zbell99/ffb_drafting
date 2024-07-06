import setup
import model
import data
import pandas as pd

if __name__ == '__main__':
    #SLEEPER SPECIFIC (lines 8,9,10)
    draft_id = "1114713116492824576"
    personal_team = 6 #first round draft pick
    next_pick_player = "Justin Jefferson"
    roster_settings, scoring_format = setup.league_settings(draft_id)
    
    league_type = {'ppr': 'Redraft PPR ADP', 'half_ppr': 'Redraft Half PPR ADP', 'std': 'Redraft Half PPR ADP', '2qb': 'Redraft SF ADP'}
    try:
        if roster_settings['slots_super_flex'] > 0:
            scoring_format = '2qb'
    except:
        pass

    df = pd.read_csv('vorp2024.csv')
    adp = setup.adp()
    
    #If ADPs from previously processed data equal what they're supposed to be, don't recalculate
    if len(set(df['ADP'].dropna()) - set(adp[league_type[scoring_format]].dropna())) > 1: #1 = default ADP value from assign_adp function
        print('Calculating Projections...')
        df = data.calculate_projections(setup.raw_data())
        df = data.calculate_vorp(df, roster_settings)
        df, matches = data.assign_adp(df, adp, league_type[scoring_format], roster_settings['teams'], roster_settings['rounds'])
        df.to_csv('vorp2024.csv', index=False)

    df, player_to_index, qbs, rbs, wrs, tes, flex, names = setup.initialize_data(df)
    drafted_teams, drafted_pos = setup.update_draft(draft_id, names, roster_settings['teams']) #SLEEPER SPECIFIC
    available, roster_size, vorp_df, remaining_settings, personal_picks, player_position, full_team_settings, available1 = model.model_preprocess(df, roster_settings, personal_team, drafted_teams, drafted_pos, next_pick_player)
    selected_players, starting_players, total_vorp = model.maximize_vorp(available, roster_size, vorp_df, remaining_settings, personal_picks, player_position, full_team_settings, available1, next_pick_player)
    

