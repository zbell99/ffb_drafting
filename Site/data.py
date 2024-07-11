import pandas as pd
from fuzzywuzzy import process

def calculate_projections(raw_data,
                          pp_pass = 0, pp_passyd = 0.04, pp_passtd = 4, pp_pick = -2, pp_fum = -2,
                            pp_rushyd = 0.1, pp_rushtd = 6, 
                            pp_rec = 0.5, pp_recyd = 0.1, pp_rectd = 6, te_premium = 0,
                            pp_fg = 3, pp_fg40 = 1, pp_fg50 = 2, pp_xp = 1, pp_missfg = -1, pp_missxp = -1,
                            pp_defint = 2, pp_deffum = 2, pp_deftd = 6, pp_defpa = -1, pp_defya = -0.1, pp_defsack = 1, pp_defsafe = 2, pp_defblock = 2,
                            ):
    #not factoring in potential pts per rush or pass
    #not factoring in custom kicking or defense scoring

    # df from csv
    qb_data = pd.read_csv(raw_data['qb_data'])
    rb_data = pd.read_csv(raw_data['rb_data'])
    wr_data = pd.read_csv(raw_data['wr_data'])
    te_data = pd.read_csv(raw_data['te_data'])
    defense_data = pd.read_csv(raw_data['dst_data'])
    kicker_data = pd.read_csv(raw_data['k_data'])

    #drop na rows
    qb_data = qb_data.dropna()
    rb_data = rb_data.dropna()
    wr_data = wr_data.dropna()
    te_data = te_data.dropna()
    defense_data['Team'] = defense_data['Team'].fillna(defense_data['Player'])
    defense_data = defense_data.dropna()
    kicker_data = kicker_data.dropna()

    qb_data = qb_data.rename(columns={'YDS':'PASSYDS', 'TDS':'PASSTD', 'YDS.1': 'RUSHYDS', 'TDS.1': 'RUSHTD', 'FL': 'FUM', 'INTS': 'INT'})
    rb_data = rb_data.rename(columns={'ATT': 'RUSH', 'YDS':'RUSHYDS', 'TDS':'RUSHTD', 'YDS.1': 'RECYDS', 'TDS.1': 'RECTD', 'FL': 'FUM'})
    wr_data = wr_data.rename(columns={'YDS':'RECYDS', 'TDS':'RECTD', 'ATT': 'RUSH', 'YDS.1': 'RUSHYDS', 'TDS.1': 'RUSHTD', 'FL': 'FUM'})
    te_data = te_data.rename(columns={'YDS':'RECYDS', 'TDS':'RECTD', 'FL': 'FUM'})

    #convert all columns to numeric and remove commas
    for df in [qb_data, rb_data, wr_data, te_data, defense_data, kicker_data]:
        for col in df.columns:
            if col != 'Player' and col != 'Team' and col != 'POS':
                df[col] = df[col].astype(str)
                df[col] = pd.to_numeric(df[col].str.replace(',', ''))
                df[col] = df[col].astype(int)


    #calculate projections (just take kicker and DST at face value)
    qb_data['FPTS'] = qb_data['PASSYDS']*pp_passyd + qb_data['PASSTD']*pp_passtd + qb_data['INT']*pp_pick + qb_data['FUM']*pp_fum + qb_data['RUSHYDS']*pp_rushyd + qb_data['RUSHTD']*pp_rushtd
    rb_data['FPTS'] = rb_data['RUSHYDS']*pp_rushyd + rb_data['RUSHTD']*pp_rushtd + rb_data['FUM']*pp_fum + rb_data['REC']*pp_rec + rb_data['RECYDS']*pp_recyd + rb_data['RECTD']*pp_rectd
    wr_data['FPTS'] = wr_data['RUSHYDS']*pp_rushyd + wr_data['RUSHTD']*pp_rushtd + wr_data['FUM']*pp_fum + wr_data['REC']*pp_rec + wr_data['RECYDS']*pp_recyd + wr_data['RECTD']*pp_rectd
    te_data['FPTS'] = te_data['FUM']*pp_fum + te_data['REC']*(pp_rec+te_premium) + te_data['RECYDS']*pp_recyd + te_data['RECTD']*pp_rec

    #subtract replacement level from each player
    qb_data['POS'] = 'QB'
    rb_data['POS'] = 'RB'
    wr_data['POS'] = 'WR'
    te_data['POS'] = 'TE'
    kicker_data['POS'] = 'K'
    defense_data['POS'] = 'DST'

    position_data = pd.concat([qb_data[['Player', 'Team', 'POS', 'FPTS']],
                              rb_data[['Player', 'Team', 'POS', 'FPTS']],
                              wr_data[['Player', 'Team', 'POS', 'FPTS']],
                              te_data[['Player', 'Team', 'POS', 'FPTS']],
                              kicker_data[['Player', 'Team', 'POS', 'FPTS']],
                              defense_data[['Player', 'Team', 'POS', 'FPTS']]])
    
    return position_data



def calculate_vorp(position_data, roster_settings):
    num_teams = roster_settings['teams']
    num_qb = roster_settings['slots_qb']
    num_rb = roster_settings['slots_rb']
    num_wr = roster_settings['slots_wr']
    num_te = roster_settings['slots_te']
    num_flex = roster_settings['slots_flex']
    num_sflex = 0
    if ('slots_super_flex' in roster_settings):
        num_sflex = roster_settings['slots_super_flex']
    num_k = roster_settings['slots_k']
    num_def = roster_settings['slots_def']
    roster_size = roster_settings['rounds']
    
    bench_size = roster_size - num_qb - num_rb - num_wr - num_te - num_flex - num_sflex - num_k - num_def
    # replacement levels (projected num rostered)
    qb_replacement = int((num_teams * (num_qb + num_sflex + 0.25))//1 + 1)
    rb_replacement = int((num_teams * (num_rb + 0.5*num_flex + bench_size*0.3))//1 + 1)
    wr_replacement = int(num_teams * (num_wr + 0.5*num_flex + bench_size*0.3)//1 + 1)
    te_replacement = int(num_teams * (num_te + 0*num_flex + 0.75)//1 + 1)
    te_replacement = num_teams
    k_replacement = num_teams * num_k
    def_replacement = num_teams * num_def
    flex_replacement = num_teams * (roster_size-num_k-num_def-num_qb)
    sflex_replacement = num_teams * (roster_size-num_k-num_def)
    
    position_data['VORP'] = 0
    position_data.loc[position_data['POS'] == 'QB', 'VORP'] = position_data.loc[position_data['POS'] == 'QB', 'FPTS'] - position_data.loc[position_data['POS'] == 'QB', 'FPTS'].nlargest(qb_replacement).min()
    position_data.loc[position_data['POS'] == 'RB', 'VORP'] = position_data.loc[position_data['POS'] == 'RB', 'FPTS'] - position_data.loc[position_data['POS'] == 'RB', 'FPTS'].nlargest(rb_replacement).min()
    position_data.loc[position_data['POS'] == 'WR', 'VORP'] = position_data.loc[position_data['POS'] == 'WR', 'FPTS'] - position_data.loc[position_data['POS'] == 'WR', 'FPTS'].nlargest(wr_replacement).min()
    position_data.loc[position_data['POS'] == 'TE', 'VORP'] = position_data.loc[position_data['POS'] == 'TE', 'FPTS'] - position_data.loc[position_data['POS'] == 'TE', 'FPTS'].nlargest(te_replacement).min()
    position_data.loc[position_data['POS'] == 'K', 'VORP'] = position_data.loc[position_data['POS'] == 'K', 'FPTS'] - position_data.loc[position_data['POS'] == 'K', 'FPTS'].nlargest(k_replacement).min()
    position_data.loc[position_data['POS'] == 'DST', 'VORP'] = position_data.loc[position_data['POS'] == 'DST', 'FPTS'] - position_data.loc[position_data['POS'] == 'DST', 'FPTS'].nlargest(def_replacement).min()

    #flex is rb, wr, te
    position_data['VORP_FLEX'] = position_data['VORP']
    position_data.loc[position_data['POS'].isin(['RB', 'WR', 'TE']), 'VORP_FLEX'] = position_data.loc[position_data['POS'].isin(['RB', 'WR', 'TE']), 'FPTS'] - position_data.loc[position_data['POS'].isin(['RB', 'WR', 'TE']), 'FPTS'].nlargest(flex_replacement).min()

    #superflex is qb, rb, wr, te
    position_data['VORP_SFLEX'] =  position_data['VORP_FLEX']
    position_data.loc[position_data['POS'].isin(['QB', 'RB', 'WR', 'TE']), 'VORP_SFLEX'] = position_data.loc[position_data['POS'].isin(['QB', 'RB', 'WR', 'TE']), 'FPTS'] - position_data.loc[position_data['POS'].isin(['QB', 'RB', 'WR', 'TE']), 'FPTS'].nlargest(sflex_replacement).min()

    #round to 2 decimal places
    position_data['VORP'] = position_data['VORP'].round(2)
    position_data['VORP_FLEX'] = position_data['VORP_FLEX'].round(2)
    position_data['VORP_SFLEX'] = position_data['VORP_SFLEX'].round(2)

    return position_data



def assign_adp(df, adp, draft_type, num_teams, num_roster):

    adp['Player'] = adp['Player First Name'] + ' ' + adp['Player Last Name']

    # Create a dictionary to store the matches
    matches = {}

    # For each player in df, find the best match in adp
    for player in df['Player'].unique():
        match = process.extractOne(player, adp['Player'].unique())
        # If the match score is above 95, store it in the dictionary
        if match[1] >= 95:
            matches[player] = match[0]

    # Replace the player names in df with the matches
    df['Player'] = df['Player'].replace(matches)
    #replace JAC with JAX
    df['Team'] = df['Team'].replace('JAC', 'JAX')

    # Merge df and adp on player and team
    df = df.merge(adp[['Player', 'Player First Name', 'Player Last Name', 'Player Team', draft_type]], how='left', left_on=['Player', 'Team'], right_on=['Player', 'Player Team'])
    #rename columns
    df = df.rename(columns={draft_type: 'ADP'})
    df['ADP'].fillna(2*num_roster*num_teams, inplace=True)

    #drop periods in player name
    df['Player'] = df['Player'].str.replace('.', '', regex=False)

    return df, matches