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