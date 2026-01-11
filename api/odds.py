"""
Bahis oranlarını çekmek için API modülü
"""

import requests
import pandas as pd
import config
import random

class OddsAPI:
    def __init__(self):
        self.api_key = config.API_FOOTBALL_KEY
        self.base_url = config.API_FOOTBALL_BASE
        self.headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': 'v3.football.api-sports.io'
        }
    
    def get_match_odds(self, fixture_id):
        """Belirli bir maç için oranları getir"""
        try:
            endpoint = f"{self.base_url}/odds"
            params = {'fixture': fixture_id}
            
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_odds(data.get('response', []))
            else:
                return self._get_demo_odds()
        except Exception as e:
            print(f"Odds API Error: {e}")
            return self._get_demo_odds()
    
    def _parse_odds(self, odds_data):
        """Oran verilerini parse et"""
        parsed_odds = {
            'match_result': {},
            'halftime_result': {},
            'halftime_fulltime': {},
            'correct_score': {}
        }
        
        if not odds_data:
            return self._get_demo_odds()
        
        for bookmaker_data in odds_data:
            for bet in bookmaker_data.get('bookmakers', [{}])[0].get('bets', []):
                bet_name = bet.get('name', '')
                
                if 'Match Winner' in bet_name:
                    for value in bet.get('values', []):
                        parsed_odds['match_result'][value['value']] = float(value['odd'])
                
                elif 'First Half Winner' in bet_name:
                    for value in bet.get('values', []):
                        parsed_odds['halftime_result'][value['value']] = float(value['odd'])
                
                elif 'Halftime/Fulltime' in bet_name:
                    for value in bet.get('values', []):
                        parsed_odds['halftime_fulltime'][value['value']] = float(value['odd'])
                
                elif 'Exact Score' in bet_name:
                    for value in bet.get('values', []):
                        parsed_odds['correct_score'][value['value']] = float(value['odd'])
        
        return parsed_odds
    
    def _get_demo_odds(self):
        """Demo oranlar"""
        return {
            'match_result': {
                '1': 2.10,
                'X': 3.40,
                '2': 3.60
            },
            'halftime_result': {
                '1': 2.50,
                'X': 2.20,
                '2': 4.00
            },
            'halftime_fulltime': {
                '1/1': 3.50, '1/X': 8.50, '1/2': 15.00,
                'X/1': 6.50, 'X/X': 5.00, 'X/2': 7.00,
                '2/1': 18.00, '2/X': 12.00, '2/2': 6.00,
                '1/0': 25.00, '2/0': 30.00,
                '0/1': 10.00, '0/2': 12.00, '0/0': 15.00
            },
            'correct_score': {
                '0-0': 9.00, '1-0': 7.00, '0-1': 7.50,
                '2-0': 8.50, '0-2': 9.50, '2-1': 6.50,
                '1-2': 7.00, '3-0': 15.00, '0-3': 18.00,
                '3-1': 12.00, '1-3': 14.00, '2-2': 11.00,
                '3-2': 16.00, '2-3': 20.00
            }
        }