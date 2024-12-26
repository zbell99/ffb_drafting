from pydantic import BaseModel

class RosterSettings(BaseModel):
    slots_wr: int
    slots_te: int
    slots_rb: int
    slots_qb: int
    slots_k: int
    slots_flex: int
    slots_sflex: int
    slots_def: int
    slots_bn: int
    max_wr: int
    max_te: int
    max_rb: int
    max_qb: int
    max_k: int
    max_flex: int
    max_sflex: int
    max_def: int
    max_bn: int
    min_wr: int
    min_te: int
    min_rb: int
    min_qb: int
    min_k: int
    min_flex: int
    min_sflex: int
    min_def: int
    min_bn: int


class ScoringSettings(BaseModel):
    scoring_settings: dict # fill this in


class Team(BaseModel):
    id: int
    name: str
    pick: int #first pick -- maybe make all picks
    roster: [Player]


class Player(BaseModel):
    id: int
    name: str
    position: str
    team: int
    adp: float
    pass_attempts: float
    pass_yards: float
    pass_tds: float
    interceptions: float
    fumbles: float
    rush_attempts: float
    rush_yards: float
    rush_tds: float
    receptions: float
    rec_yards: float
    rec_tds: float
    kicker_pts: float
    def_pts: float


class OptiModel(BaseModel):
    id: int
    name: str
    team: int
    #vorp_ranks: dict #each position the cutoff of replacement level
    model: dict # fill this in



class Draft(BaseModel):
    id: int
    name: str
    num_teams: int
    rounds: int
    roster_settings: [RosterSettings]
    scoring_settings: [ScoringSettings]
    teams: [Team]
    players: [Player]
    drafted_players: {Player}
    remaining_players: {Player}
    opti_model: [OptiModel]