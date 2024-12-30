from typing import List, Dict, Set
from pydantic import BaseModel

class Player(BaseModel):
    id: str
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


class Team(BaseModel):
    id: int
    name: str
    pick: int #first pick -- maybe make all picks
    roster: List[Player]


class OptiModel(BaseModel):
    team_id: str
    name: str
    picks: List[int]
    current_pick: int
    score: float
    optimal_roster: Team


class Model(BaseModel):
    models: Dict[str, OptiModel]
    projected_picks: Dict[int, Player]
    #function: optimize_draft


class RosterSettings(BaseModel):
    slots_qb: int
    slots_rb: int
    slots_wr: int
    slots_te: int
    slots_k: int
    slots_flex: int
    slots_sflex: int
    slots_def: int
    slots_bn: int
    max_qb: int
    max_rb: int
    max_wr: int
    max_te: int
    max_k: int
    max_def: int
    max_bn: int
    min_qb: int
    min_rb: int
    min_wr: int
    min_te: int
    min_k: int
    min_def: int
    min_bn: int


class ScoringSettings(BaseModel):
    scoring_settings: dict # fill this in


class Draft(BaseModel):
    host: str
    id: str
    name: str
    num_teams: int
    rounds: int
    roster_settings: List[RosterSettings]
    scoring_settings: List[ScoringSettings]
    rosters: Set[Team]
    players: Set[Player]
    drafted_players: Set[Player]
    remaining_players: Set[Player]
    model: Model