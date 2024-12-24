from flask import Flask, request, jsonify
import pandas as pd
from flask_cors import CORS
import setup
import model
import data
import scraper
app = Flask(__name__)
CORS(app)  # Enable CORS for all origins

manager = None


@app.route('/process-info', methods=['POST'])
def process_info():
    params = request.json
    draft_id = params.get('draft_id')
    personal_team = params.get('personal_team')
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
    
    available, roster_size, vorp_df, remaining_settings, personal_picks, player_position, full_team_settings, available1 = model.model_preprocess(df, roster_settings, personal_team, drafted_teams, drafted_pos)
    selected_players, starting_players, total_vorp = model.maximize_vorp(available, roster_size, vorp_df, remaining_settings, personal_picks, player_position, full_team_settings, available1)
    # Call your Python function with the provided parameters
    return jsonify(selected_players[0])

@app.route('/process-info-ESPN', methods=['POST'])
def process_info_ESPN():
    data = request.json
    roster_settings = data.get('roster_settings')
    scoring_format = data.get('scoring_format')
    personal_team = data.get('personal_team')
    drafted_players = data.get('drafted_players')

    projection_amount=1
    next_pick_player=""

    league_type = {'ppr': 'Redraft PPR ADP', 'half_ppr': 'Redraft Half PPR ADP', 'std': 'Redraft Half PPR ADP', '2qb': 'Redraft SF ADP'}
    df = pd.read_csv('vorp2024.csv')
    adp = setup.adp()
    
    #If ADPs from previously processed data equal what they're supposed to be, don't recalculate
    if len(set(df['ADP'].dropna()) - set(adp[league_type[scoring_format]].dropna())) > 1: #1 = default ADP value from assign_adp function
        df = data.calculate_projections(setup.raw_data())
        df = data.calculate_vorp(df, roster_settings)
        df, matches = data.assign_adp(df, adp, league_type[scoring_format], roster_settings['teams'], roster_settings['rounds'])
        df.to_csv('vorp2024.csv', index=False)

    df, player_to_index, qbs, rbs, wrs, tes, flex, names = setup.initialize_data(df)
    #drafted_teams, drafted_pos = setup.update_draft(draft_id, names, roster_settings['teams']) #SLEEPER SPECIFIC
    
    # Initialize the desired format for players on each roster
    drafted_teams = {i+1: [] for i in range(len(drafted_players))}
    # Populate the drafted_teams dictionary
    for idx, (team, players) in enumerate(drafted_players.items()):
        for player_info in players:
            if player_info['Player'] != ' ':
                # split player on space and take first two elements, remove punctuation
                p = player_info['Player'].split(' ')[0] + ' ' + player_info['Player'].split(' ')[1]
                p = p.replace('.', '')
                # find where p matches in df and add to drafted_teams
                for i in range(len(df)):
                    if df['Player'][i].split(' ')[0] + ' ' + df['Player'][i].split(' ')[1] == p:
                        p = df['Player'][i]
                drafted_teams[idx + 1].append(p)
  
    # Initialize the desired format for position counts
    drafted_pos = {i+1: {'QB': 0, 'RB': 0, 'WR': 0, 'TE': 0, 'DST': 0, 'K': 0} for i in range(len(drafted_players))}

    # Populate the drafted_pos dictionary
    for idx, (team, players) in enumerate(drafted_players.items()):
        for player_info in players:
            if player_info['Player'] != ' ':
                pos = player_info['Pos']
                if pos in drafted_pos[idx + 1]:
                    drafted_pos[idx + 1][pos] += 1
    print(drafted_pos)
    available, roster_size, vorp_df, remaining_settings, personal_picks, player_position, full_team_settings, available1, cp = model.model_preprocess(df, roster_settings, personal_team, drafted_teams, drafted_pos, projection_amount, next_pick_player)
    selected_players, starting_players, total_vorp = model.maximize_vorp(available, roster_size, vorp_df, remaining_settings, personal_picks, player_position, full_team_settings, projection_amount, cp, available1, next_pick_player)
    return jsonify(selected_players[0])

@app.route('/launch-ESPN', methods=['POST'])
def launch_ESPN():
    global manager
    data = request.json
    browser = data.get('browser')
    manager = scraper.ESPNManager()
    return manager.launch_ESPN(browser)
    
@app.route('/scrape-ESPN', methods=['POST'])
def scrape_ESPN():
    global manager
    if manager:
        return manager.scrape_ESPN()
    else:
        return jsonify({"error": "Manager not initialized"}), 400

@app.route('/scrape-ESPN2', methods=['POST'])
def scrape_ESPN2():
    return pd.read_csv('roster2.csv').to_json()
    # global manager
    # if manager:
    #     return manager.scrape_ESPN2()
    # else:
    #     return jsonify({"error": "Manager not initialized"}), 400

if __name__ == '__main__':
    app.run(debug=True)