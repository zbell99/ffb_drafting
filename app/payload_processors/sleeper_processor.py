from payload_processor import PayloadProcessor
import requests
import json

class SleeperProcessor(PayloadProcessor):
    def process(self, draft_id: str) -> dict:
        # Process the payload specific to Sleeper
        payload = self._get_league_payload(draft_id)
        if payload:
            print("League ID found: ", draft_id)
            draft_payload = self._get_draft_payload(payload['draft_id'])
            return {
                'num_teams': payload['total_rosters'],
                'rounds': len(payload['roster_positions']),
                'roster_settings': draft_payload['settings'],
                'scoring_settings': payload['scoring_settings'],
                'scoring_format': draft_payload['metadata']['scoring_type'],
                'rosters': draft_payload['draft_order'],
            }
        else:
            payload = self._get_draft_payload(draft_id)
            if payload:
                print("Draft ID found: ", draft_id)
                draft_type = payload['metadata']['scoring_type']
                return {
                    'num_teams': payload['settings']['teams'],
                    'rounds': payload['settings']['rounds'],
                    'roster_settings': payload['settings'],
                    'scoring_settings': self._scoring_settings_default(draft_type),
                    'scoring_format': draft_type,
                    'rosters': payload['draft_order'],
                }
            else:
                raise ValueError("Draft/League ID not found: ", draft_id)


    def _get_draft_payload(self, draft_id: str) -> dict:
        url = "https://api.sleeper.app/v1/draft/" + draft_id
        response = requests.get(url)
        response_body = response.text
        return json.loads(response_body)
    

    def _get_league_payload(self, league_id: str) -> dict:
        url = "https://api.sleeper.app/v1/league/" + league_id
        response = requests.get(url)
        response_body = response.text
        return json.loads(response_body)
    

    def _scoring_settings_default(self, draft_type: str) -> dict:
        scoring_settings = {'bonus_rec_te': 0,
            'pass_int': -2.0,
            'pass_2pt': 2.0,
            'rec_td': 6.0,
            'rush_td': 6.0,
            'rec_2pt': 2.0,
            'rec': 0,
            'fum_lost': -2.0,
            'rush_2pt': 2.0,
            'pass_yd': 0.04,
            'pass_td': 4.0,
            'rush_yd': 0.1,
            'fum': 0.0,
            'fum_rec_td': 6.0,
            'rec_yd': 0.1,}

        if draft_type == 'ppr':
            scoring_settings['rec'] = 1.0
        elif draft_type == 'half_ppr':
            scoring_settings['rec'] = 0.5
        elif draft_type == 'standard':
            scoring_settings['rec'] = 0.0
        return scoring_settings
    

    # def _process_sleeper_league_roster_settings(roster_positions: dict) -> dict:
    #     roster_settings = {"slots_qb": 0, "slots_rb": 0, "slots_wr": 0, "slots_te": 0, "slots_flex": 0, "slots_super_flex": 0}
    #     for pos in roster_positions:
    #         if pos == 'QB':
    #             roster_settings['slots_qb'] += 1
    #         elif pos == 'RB':
    #             roster_settings['slots_rb'] += 1
    #         elif pos == 'WR':
    #             roster_settings['slots_wr'] += 1
    #         elif pos == 'TE':
    #             roster_settings['slots_te'] += 1
    #         elif pos == 'FLEX':
    #             roster_settings['slots_flex'] += 1
    #         elif pos == 'SUPER_FLEX':
    #             roster_settings['slots_super_flex'] += 1
    #         elif pos == 'DEF':
    #             roster_settings['slots_def'] += 1
    #         elif pos == 'K':
    #             roster_settings['slots_k'] += 1
    #         elif pos == 'BN':
    #             roster_settings['slots_bn'] += 1
    #         else:
    #             pass
    #     return roster_settings
