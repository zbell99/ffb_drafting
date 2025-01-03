# app/payload_processor_factory.py
from payload_processors.sleeper_processor import SleeperProcessor
from payload_processors.espn_processor import ESPNProcessor

def get_payload_processor(host: str):
    if host == 'sleeper':
        return SleeperProcessor()
    elif host == 'espn':
        return ESPNProcessor()
    else:
        raise ValueError(f"Unsupported host: {host}")
    

# app/adp_file_factory.py
import pandas as pd
def get_adp_file(host: str, scoring_format: str):
    if host == 'sleeper':
        league_type = {'ppr': 'Redraft PPR ADP', 'half_ppr': 'Redraft Half PPR ADP', 'std': 'Redraft Half PPR ADP', '2qb': 'Redraft SF ADP'}
        file = pd.read_csv(f"adp/ADP2024.csv")
        #file = pd.read_csv(f"app/adp_files/{host}/ADP2024.csv")

        file['Player'] = file['Player First Name'] + ' ' + file['Player Last Name']
        file = file.rename(columns={league_type[scoring_format]: 'ADP'})
        return file[["Player", "Player First Name", "Player Last Name", "Player Team", "ADP"]]
    
    elif host == 'espn':
        raise NotImplementedError("ESPN ADP file not found")
    else:
        raise ValueError(f"Unsupported host: {host}")