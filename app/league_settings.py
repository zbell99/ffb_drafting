class RosterSettings:
    def __init__(self, roster_settings: dict):
        self.slots_wr = roster_settings['slots_wr']
        self.slots_te = roster_settings['slots_te']
        self.slots_rb = roster_settings['slots_rb']
        self.slots_qb = roster_settings['slots_qb']
        self.slots_flex = roster_settings['slots_flex']
        self.slots_sflex = roster_settings['slots_super_flex']
        try: self.slots_k = roster_settings['slots_k'] 
        except: self.slots_k = 0
        try: self.slots_def = roster_settings['slots_def'] 
        except: self.slots_def = 0
        try: self.slots_bn = roster_settings['slots_bn'] 
        except: self.slots_bn = 5
        
        ## THIS IS MY OWN LOGIC
        self.min_qb = self.slots_qb + self.slots_sflex
        self.min_rb = self.slots_rb + self.slots_flex
        self.min_wr = self.slots_wr + self.slots_flex
        self.min_te = self.slots_te
        self.min_k = self.slots_k
        self.min_def = self.slots_def

        ## THIS IS MY OWN LOGIC
        self.max_qb = self.slots_qb + self.slots_sflex + self.slots_bn//4
        self.max_rb = self.slots_rb + self.slots_flex + self.slots_bn//2
        self.max_wr = self.slots_wr + self.slots_flex + self.slots_bn//2
        self.max_te = self.slots_te + 2
        self.max_k = self.slots_k
        self.max_def = self.slots_def



class ScoringSettings:
    def __init__(self, scoring_settings: dict):
        self.PASSTDS = scoring_settings['pass_td']
        self.PASSYDS = scoring_settings['pass_yd']
        self.RUSHTDS = scoring_settings['rush_td']
        self.RUSHYDS = scoring_settings['rush_yd']
        self.RECTDS = scoring_settings['rec_td']
        self.RECYDS = scoring_settings['rec_yd']
        self.REC = scoring_settings['rec']
        self.TE_PREM = scoring_settings['bonus_rec_te']
        self.INT = scoring_settings['pass_int']
        self.FUM = scoring_settings['fum']
        self.FUM_LOST = scoring_settings['fum_lost']
