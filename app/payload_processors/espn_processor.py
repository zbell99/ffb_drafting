#TODO : AUTO GENERATED
from payload_processor import PayloadProcessor

class ESPNProcessor(PayloadProcessor):
    def get_payload(self, draft_id: str) -> dict:
        # Process the payload specific to ESPN
        return {
            'teams': 10,
            'draft_rounds': 16,
            'roster': {
                'QB': 1,
                'RB': 2,
                'WR': 2,
                'TE': 1,
                'FLEX': 1,
                'S-FLEX': 1,
                'BENCH': 6,
            },
            'scoring': {
                'passing': {
                    'TD': 4,
                    'YDS': 1/25,
                    'INT': -2,
                },
                'rushing': {
                    'TD': 6,
                    'YDS': 1/10,
                },
                'receiving': {
                    'TD': 6,
                    'YDS': 1/10,
                },
            }
        }
    
    def process(self, draft_id: str) -> dict:
        # Process the payload specific to ESPN
        payload = self.get_payload(draft_id)
        return {
            'num_teams': payload['teams'],
            'rounds': payload['draft_rounds'],
            'roster_settings': payload['roster'],
            'scoring_settings': payload['scoring'],
        }