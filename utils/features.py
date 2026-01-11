"""
Feature engineering - Tahmin için özellik üretimi
"""

import pandas as pd
import numpy as np

class FeatureEngineer:
    def __init__(self):
        pass
    
    def calculate_team_stats(self, team_matches, team_name, is_home=True):
        """Takım istatistiklerini hesapla"""
        if team_matches.empty:
            return self._get_default_stats()
        
        recent_5 = team_matches.head(5)
        recent_10 = team_matches.head(10)
        
        stats = {
            # Son 5 maç
            'goals_scored_5': self._calculate_avg_goals(recent_5, team_name, is_home, scored=True),
            'goals_conceded_5': self._calculate_avg_goals(recent_5, team_name, is_home, scored=False),
            'ht_goals_scored_5': self._calculate_avg_ht_goals(recent_5, team_name, is_home, scored=True),
            'ht_goals_conceded_5': self._calculate_avg_ht_goals(recent_5, team_name, is_home, scored=False),
            
            # Son 10 maç
            'goals_scored_10': self._calculate_avg_goals(recent_10, team_name, is_home, scored=True),
            'goals_conceded_10': self._calculate_avg_goals(recent_10, team_name, is_home, scored=False),
            
            # İlk yarı performans oranları
            'ht_lead_pct': self._calculate_ht_lead_percentage(recent_10, team_name, is_home),
            'ht_draw_pct': self._calculate_ht_draw_percentage(recent_10, team_name, is_home),
            
            # Ev sahibi / Deplasman farkı
            'home_advantage': 0.15 if is_home else -0.10
        }
        
        return stats
    
    def _calculate_avg_goals(self, matches, team_name, is_home, scored=True):
        """Ortalama gol hesapla"""
        if matches.empty:
            return 1.2
        
        if is_home:
            goals = matches['home_score'] if scored else matches['away_score']
        else:
            goals = matches['away_score'] if scored else matches['home_score']
        
        return goals.mean() if not goals.isna().all() else 1.2
    
    def _calculate_avg_ht_goals(self, matches, team_name, is_home, scored=True):
        """İlk yarı ortalama gol hesapla"""
        if matches.empty:
            return 0.6
        
        if is_home:
            goals = matches['halftime_home'] if scored else matches['halftime_away']
        else:
            goals = matches['halftime_away'] if scored else matches['halftime_home']
        
        valid_goals = goals.dropna()
        return valid_goals.mean() if not valid_goals.empty else 0.6
    
    def _calculate_ht_lead_percentage(self, matches, team_name, is_home):
        """İlk yarıyı önde kapatma yüzdesi"""
        if matches.empty:
            return 0.3
        
        if is_home:
            leads = (matches['halftime_home'] > matches['halftime_away']).sum()
        else:
            leads = (matches['halftime_away'] > matches['halftime_home']).sum()
        
        return leads / len(matches) if len(matches) > 0 else 0.3
    
    def _calculate_ht_draw_percentage(self, matches, team_name, is_home):
        """İlk yarı beraberlik yüzdesi"""
        if matches.empty:
            return 0.35
        
        draws = (matches['halftime_home'] == matches['halftime_away']).sum()
        return draws / len(matches) if len(matches) > 0 else 0.35
    
    def _get_default_stats(self):
        """Varsayılan istatistikler"""
        return {
            'goals_scored_5': 1.2,
            'goals_conceded_5': 1.1,
            'ht_goals_scored_5': 0.6,
            'ht_goals_conceded_5': 0.5,
            'goals_scored_10': 1.3,
            'goals_conceded_10': 1.2,
            'ht_lead_pct': 0.3,
            'ht_draw_pct': 0.35,
            'home_advantage': 0.15
        }
    
    def calculate_odds_features(self, current_odds, opening_odds=None):
        """Oran bazlı özellikler"""
        features = {
            'current_odds': current_odds,
            'odds_movement': 0,
            'sharp_money_signal': False
        }
        
        if opening_odds:
            movement = ((opening_odds - current_odds) / opening_odds) * 100
            features['odds_movement'] = movement
            features['sharp_money_signal'] = abs(movement) > 10
        
        return features