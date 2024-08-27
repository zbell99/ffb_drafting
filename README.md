# ffb_drafting

Currently developed for Sleeper's API.

To format a different host's settings similarly, create the following dictionaries:

-----
roster_settings = {
    'slots_qb': Number of starting QB slots,
    'slots_rb': Number of starting RB slots,
    'slots_wr': Number of starting WR slots,
    'slots_te': Number of starting TE slots,
    'slots_flex': Number of starting RB/WR/TE slots,
    'slots_super_flex': Number of starting QB/RB/WR/TE slots,
    'slots_k': Number of starting K slots,
    'slots_dst': Number of starting DST slots,
    'teams': Number of teams,
    'rounds': Number of rounds in draft (roster spots)
}

scoring_format = "ppr" or "half_ppr" or "std" or "2qb"

These dictionaries come from setup.league_settings().
-----
drafted: Dictionary containing the players already drafted to each roster
    example -- drafted[1] = ["Justin Jefferson", "Josh Allen"]
drafted_pos = Dictionary containing the positions filled on each roster
    example -- drafted_pos[1] = {"QB":1, "RB":0, "WR":1, "TE":0, "DEF":0, "K":0}

These dictionaries come from setup.update_draft().

