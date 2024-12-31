FANTASYPROS_FILES = {
    "qb_data": "projections/FantasyPros_Fantasy_Football_Projections_QB.csv",
    "rb_data": "projections/FantasyPros_Fantasy_Football_Projections_RB.csv",
    "wr_data": "projections/FantasyPros_Fantasy_Football_Projections_WR.csv",
    "te_data": "projections/FantasyPros_Fantasy_Football_Projections_TE.csv",
    "k_data": "projections/FantasyPros_Fantasy_Football_Projections_K.csv",
    "def_data": "projections/FantasyPros_Fantasy_Football_Projections_DST.csv",
}

FANTASYPROS_RENAMING = {
    "qb_data": {'YDS':'PASSYDS', 'TDS':'PASSTD', 'YDS.1': 'RUSHYDS', 'TDS.1': 'RUSHTD', 'FL': 'FUM', 'INTS': 'INT'},
    "rb_data": {'ATT': 'RUSH', 'YDS':'RUSHYDS', 'TDS':'RUSHTD', 'YDS.1': 'RECYDS', 'TDS.1': 'RECTD', 'FL': 'FUM_LOST'},
    "wr_data": {'YDS':'RECYDS', 'TDS':'RECTD', 'ATT': 'RUSH', 'YDS.1': 'RUSHYDS', 'TDS.1': 'RUSHTD', 'FL': 'FUM_LOST'},
    "te_data": {'YDS':'RECYDS', 'TDS':'RECTD', 'FL': 'FUM_LOST'},
    "kicker_data": {'FPTS': 'KICKER_PTS'},
    "defense_data": {'FPTS': 'DEF_PTS'}
}

FANTASYPROS_POSITIONS = {
    "qb_data": "QB",
    "rb_data": "RB",
    "wr_data": "WR",
    "te_data": "TE",
    "kicker_data": "K",
    "defense_data": "DEF"
}

FANTASYPROS_COLS = [
    'Player',
    'Team',
    'POS',
    'PASSYDS',
    'PASSTDS',
    'RUSHYDS',
    'RUSHTDS',
    'REC',
    'RECYDS',
    'RECTDS',
    'INT',
    'FUM',
    'FUM_LOST',
    'KICKER_PTS',
    'DEF_PTS'
]