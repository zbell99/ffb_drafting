FANTASYPROS_FILES = {
    "qb_data": "projections/FantasyPros_Fantasy_Football_Projections_QB.csv",
    "rb_data": "projections/FantasyPros_Fantasy_Football_Projections_RB.csv",
    "wr_data": "projections/FantasyPros_Fantasy_Football_Projections_WR.csv",
    "te_data": "projections/FantasyPros_Fantasy_Football_Projections_TE.csv",
    "k_data": "projections/FantasyPros_Fantasy_Football_Projections_K.csv",
    "def_data": "projections/FantasyPros_Fantasy_Football_Projections_DST.csv",
}

FANTASYPROS_RENAMING = {
    "qb_data": {'YDS':'PASSYDS', 'TDS':'PASSTDS', 'YDS.1': 'RUSHYDS', 'TDS.1': 'RUSHTDS', 'FL': 'FUM', 'INTS': 'INT'},
    "rb_data": {'ATT': 'RUSH', 'YDS':'RUSHYDS', 'TDS':'RUSHTDS', 'YDS.1': 'RECYDS', 'TDS.1': 'RECTDS', 'FL': 'FUM_LOST'},
    "wr_data": {'YDS':'RECYDS', 'TDS':'RECTDS', 'ATT': 'RUSH', 'YDS.1': 'RUSHYDS', 'TDS.1': 'RUSHTDS', 'FL': 'FUM_LOST'},
    "te_data": {'YDS':'RECYDS', 'TDS':'RECTDS', 'FL': 'FUM_LOST'},
    "k_data": {'FPTS': 'KICKER_PTS'},
    "def_data": {'FPTS': 'DEF_PTS'}
}

FANTASYPROS_POSITIONS = {
    "qb_data": "QB",
    "rb_data": "RB",
    "wr_data": "WR",
    "te_data": "TE",
    "k_data": "K",
    "def_data": "DEF"
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

FLEX_POSITIONS = ['RB', 'WR', 'TE']

SUPERFLEX_POSITIONS = ['QB', 'RB', 'WR', 'TE']