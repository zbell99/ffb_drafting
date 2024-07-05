import pandas as pd
import requests
import json
import os

def initialize_data(data, scoring_format='ADP'):
    # fill missing with 500 in pandas
    data[scoring_format].fillna(500, inplace=True)
    data['Name'] = data['Player First Name'] + " " + data['Player Last Name']
    data['Name'] = data['Name'].str.replace('.', '')
    data.sort_values(by=scoring_format, inplace=True)

    player_to_index = {}
    # iterate through each row in the data
    for i in range(len(data)):
        # get the player name
        player = data.iloc[i]['Name']
        # if the player is not in the dictionary, add them
        player_to_index[player] = i

    qbs = set()
    rbs = set()
    wrs = set()
    tes = set()
    flex = set()
    sflex = set()
    names = set()

    for _, player in data.iterrows():
        names.add(player['Name'])
        if player['POS'] == 'QB':
            qbs.add(player['Name'])
            sflex.add(player['Name'])
        elif player['POS'] == 'RB':
            rbs.add(player['Name'])
            flex.add(player['Name'])
            sflex.add(player['Name'])
        elif player['POS'] == 'WR':
            wrs.add(player['Name'])
            flex.add(player['Name'])
            sflex.add(player['Name'])
        elif player['POS'] == 'TE':
            tes.add(player['Name'])
            flex.add(player['Name'])
            sflex.add(player['Name'])

    return data, player_to_index, qbs, rbs, wrs, tes, flex, names

def reset_draft(num_teams):
    drafted = {}
    for i in range(1, num_teams+1):
        drafted[i] = []
    
    return drafted

def league_settings(draft_id):
    url = "https://api.sleeper.app/v1/draft/" + draft_id
    response = requests.get(url)
    response_body = response.text
    parsed_json = json.loads(response_body)
    roster_settings = parsed_json["settings"]
    scoring_format = parsed_json["metadata"]["scoring_type"]
    return roster_settings, scoring_format

def update_draft(draft_id, names, teams):
    url = "https://api.sleeper.app/v1/draft/" + draft_id + "/picks"
    response = requests.get(url)
    response_body = response.text
    parsed_json = json.loads(response_body)
    drafted = reset_draft(teams)
    drafted_pos = reset_draft(teams)
    for team in drafted_pos.keys():
        drafted_pos[team] = {"QB": 0, "RB": 0, "WR": 0, "TE": 0, "DST": 0, "K": 0}

    for pick in parsed_json:
        team = pick["draft_slot"]
        position = pick["metadata"]["position"]
        name = pick["metadata"]["first_name"] + " " + pick["metadata"]["last_name"]
        name = name.replace(".", "")

        if name in names: ###DRAFT DATA MUST MATCH PROJECTION DATA FOR NAMES
            drafted[team].append(name)
        else:
            drafted[team].append(position)

        drafted_pos[team][position] += 1
        
    return drafted, drafted_pos

def raw_data():
    return {"qb_data": "projections/FantasyPros_Fantasy_Football_Projections_QB.csv",
            "rb_data": "projections/FantasyPros_Fantasy_Football_Projections_RB.csv",
            "wr_data": "projections/FantasyPros_Fantasy_Football_Projections_WR.csv",
            "te_data": "projections/FantasyPros_Fantasy_Football_Projections_TE.csv",
            "k_data": "projections/FantasyPros_Fantasy_Football_Projections_K.csv",
            "dst_data": "projections/FantasyPros_Fantasy_Football_Projections_DST.csv",}

def adp():
    return pd.read_csv("adp/ADP2024.csv")