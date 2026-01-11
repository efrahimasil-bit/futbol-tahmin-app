"""
Maç verilerini çekmek için API modülü
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import config

class MatchAPI:
    def __init__(self):
        self.api_key = config.API_FOOTBALL_KEY
        self.base_url = config.API_FOOTBALL_BASE
        self.headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': 'v3.football.api-sports.io'
        }
    
    def get_live_matches(self):
        """Canlı maçları getir"""
        try:
            endpoint = f"{self.base_url}/fixtures"
            params = {'live': 'all'}
            
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_matches(data.get('response', []))
            else:
                return self._get_demo_matches()
        except Exception as e:
            print(f"API Error: {e}")
            return self._get_demo_matches()
    
    def get_upcoming_matches(self, days=1):
        """Yaklaşan maçları getir"""
        try:
            endpoint = f"{self.base_url}/fixtures"
            date = datetime.now().strftime('%Y-%m-%d')
            params = {'date': date}
            
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_matches(data.get('response', []))
            else:
                return self._get_demo_matches()
        except Exception as e:
            print(f"API Error: {e}")
            return self._get_demo_matches()
    
    def get_match_statistics(self, fixture_id):
        """Belirli bir maçın istatistiklerini getir"""
        try:
            endpoint = f"{self.base_url}/fixtures/statistics"
            params = {'fixture': fixture_id}
            
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', [])
            else:
                return []
        except Exception as e:
            print(f"Statistics Error: {e}")
            return []
    
    def _parse_matches(self, matches_data):
        """API yanıtını DataFrame'e çevir"""
        parsed_matches = []
        
        for match in matches_data:
            parsed_matches.append({
                'fixture_id': match['fixture']['id'],
                'date': match['fixture']['date'],
                'status': match['fixture']['status']['short'],
                'elapsed': match['fixture']['status'].get('elapsed', 0),
                'league': match['league']['name'],
                'country': match['league']['country'],
                'home_team': match['teams']['home']['name'],
                'away_team': match['teams']['away']['name'],
                'home_score': match['goals']['home'],
                'away_score': match['goals']['away'],
                'halftime_home': match['score']['halftime']['home'],
                'halftime_away': match['score']['halftime']['away']
            })
        
        return pd.DataFrame(parsed_matches)
    
    def _get_demo_matches(self):
        """Demo veriler (API çalışmazsa)"""
        demo_data = [
            {
                'fixture_id': 1, 'date': datetime.now().isoformat(),
                'status': '1H', 'elapsed': 35,
                'league': 'Premier League', 'country': 'England',
                'home_team': 'Manchester City', 'away_team': 'Liverpool',
                'home_score': 1, 'away_score': 0,
                'halftime_home': None, 'halftime_away': None
            },
            {
                'fixture_id': 2, 'date': datetime.now().isoformat(),
                'status': 'NS', 'elapsed': 0,
                'league': 'La Liga', 'country': 'Spain',
                'home_team': 'Barcelona', 'away_team': 'Real Madrid',
                'home_score': None, 'away_score': None,
                'halftime_home': None, 'halftime_away': None
            },
            {
                'fixture_id': 3, 'date': datetime.now().isoformat(),
                'status': '2H', 'elapsed': 67,
                'league': 'Serie A', 'country': 'Italy',
                'home_team': 'Inter Milan', 'away_team': 'AC Milan',
                'home_score': 2, 'away_score': 1,
                'halftime_home': 1, 'halftime_away': 0
            },
            {
                'fixture_id': 4, 'date': datetime.now().isoformat(),
                'status': 'NS', 'elapsed': 0,
                'league': 'Bundesliga', 'country': 'Germany',
                'home_team': 'Bayern Munich', 'away_team': 'Borussia Dortmund',
                'home_score': None, 'away_score': None,
                'halftime_home': None, 'halftime_away': None
            },
            {
                'fixture_id': 5, 'date': datetime.now().isoformat(),
                'status': '1H', 'elapsed': 23,
                'league': 'Ligue 1', 'country': 'France',
                'home_team': 'PSG', 'away_team': 'Marseille',
                'home_score': 0, 'away_score': 0,
                'halftime_home': None, 'halftime_away': None
            }
        ]
        
        return pd.DataFrame(demo_data)