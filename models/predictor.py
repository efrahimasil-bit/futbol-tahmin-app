"""
Tahmin modeli - İstatistiksel + ML kombinasyonu
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import config

class FootballPredictor:
    def __init__(self):
        self.rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.lr_model = LogisticRegression(max_iter=1000, random_state=42)
        self.is_trained = False
    
    def predict_halftime_fulltime(self, home_stats, away_stats, odds_data):
        """İlk yarı / Maç sonucu tahmini"""
        predictions = []
        
        # İstatistiksel yaklaşım
        for outcome in config.HALFTIME_FULLTIME_OUTCOMES:
            probability = self._calculate_ht_ft_probability(
                outcome, home_stats, away_stats, odds_data
            )
            
            odds = odds_data.get('halftime_fulltime', {}).get(outcome, 10.0)
            confidence = self._determine_confidence(probability)
            
            predictions.append({
                'outcome': outcome,
                'probability': probability * 100,
                'odds': odds,
                'confidence': confidence
            })
        
        # Normalize probabilities
        total_prob = sum(p['probability'] for p in predictions)
        for p in predictions:
            p['probability'] = (p['probability'] / total_prob) * 100
        
        return sorted(predictions, key=lambda x: x['probability'], reverse=True)
    
    def predict_halftime_score(self, home_stats, away_stats, odds_data):
        """İlk yarı skor tahmini"""
        predictions = []
        
        for score in config.HALFTIME_SCORES:
            probability = self._calculate_score_probability(
                score, home_stats, away_stats, is_halftime=True
            )
            
            odds = odds_data.get('correct_score', {}).get(score, 15.0)
            confidence = self._determine_confidence(probability)
            
            predictions.append({
                'outcome': score,
                'probability': probability * 100,
                'odds': odds,
                'confidence': confidence
            })
        
        # Normalize
        total_prob = sum(p['probability'] for p in predictions)
        for p in predictions:
            p['probability'] = (p['probability'] / total_prob) * 100
        
        return sorted(predictions, key=lambda x: x['probability'], reverse=True)
    
    def predict_fulltime_score(self, home_stats, away_stats, odds_data):
        """Maç sonu skor tahmini"""
        predictions = []
        
        for score in config.FULLTIME_SCORES:
            probability = self._calculate_score_probability(
                score, home_stats, away_stats, is_halftime=False
            )
            
            odds = odds_data.get('correct_score', {}).get(score, 12.0)
            confidence = self._determine_confidence(probability)
            
            predictions.append({
                'outcome': score,
                'probability': probability * 100,
                'odds': odds,
                'confidence': confidence
            })
        
        # Normalize
        total_prob = sum(p['probability'] for p in predictions)
        for p in predictions:
            p['probability'] = (p['probability'] / total_prob) * 100
        
        return sorted(predictions, key=lambda x: x['probability'], reverse=True)
    
    def _calculate_ht_ft_probability(self, outcome, home_stats, away_stats, odds_data):
        """İY/MS olasılık hesaplama"""
        # Outcome parse et (örn: "1/1", "X/2", "0/0")
        if '/' not in outcome:
            return 0.05
        
        ht, ft = outcome.split('/')
        
        # İlk yarı analizi
        ht_home_goal_avg = home_stats.get('ht_goals_scored_5', 0.6)
        ht_away_goal_avg = away_stats.get('ht_goals_scored_5', 0.5)
        
        # Maç sonu analizi
        ft_home_goal_avg = home_stats.get('goals_scored_5', 1.2)
        ft_away_goal_avg = away_stats.get('goals_scored_5', 1.1)
        
        # Rule-based probability
        base_prob = 0.05
        
        if ht == '1':  # İY Ev sahibi önde
            base_prob += home_stats.get('ht_lead_pct', 0.3)
        elif ht == 'X':  # İY Berabere
            base_prob += home_stats.get('ht_draw_pct', 0.35) * 0.5
            base_prob += away_stats.get('ht_draw_pct', 0.35) * 0.5
        elif ht == '2':  # İY Deplasman önde
            base_prob += away_stats.get('ht_lead_pct', 0.25)
        elif ht == '0':  # İY Berabere (0-0 özel durum)
            ht_draw_pct = (home_stats.get('ht_draw_pct', 0.35) + away_stats.get('ht_draw_pct', 0.35)) / 2
            base_prob += ht_draw_pct * 0.8
        
        # Maç sonu
        if ft == '1':  # MS Ev sahibi kazanır
            if ft_home_goal_avg > ft_away_goal_avg:
                base_prob += 0.15
        elif ft == 'X':  # MS Berabere
            if abs(ft_home_goal_avg - ft_away_goal_avg) < 0.3:
                base_prob += 0.10
        elif ft == '2':  # MS Deplasman kazanır
            if ft_away_goal_avg > ft_home_goal_avg:
                base_prob += 0.12
        elif ft == '0':  # MS Berabere (0-0 özel)
            if ft_home_goal_avg < 1.0 and ft_away_goal_avg < 1.0:
                base_prob += 0.08
        
        # Oran etkisi
        current_odds = odds_data.get('halftime_fulltime', {}).get(outcome)
        if current_odds:
            implied_prob = 1.0 / current_odds
            base_prob = (base_prob * 0.7) + (implied_prob * 0.3)
        
        return max(0.01, min(base_prob, 0.95))
    
    def _calculate_score_probability(self, score, home_stats, away_stats, is_halftime=False):
        """Skor olasılık hesaplama (Poisson dağılımı yaklaşımı)"""
        if '-' not in score:
            return 0.02
        
        home_goals, away_goals = map(int, score.split('-'))
        
        if is_halftime:
            lambda_home = home_stats.get('ht_goals_scored_5', 0.6)
            lambda_away = away_stats.get('ht_goals_scored_5', 0.5)
        else:
            lambda_home = home_stats.get('goals_scored_5', 1.2)
            lambda_away = away_stats.get('goals_scored_5', 1.1)
        
        # Poisson olasılığı
        prob_home = self._poisson_probability(home_goals, lambda_home)
        prob_away = self._poisson_probability(away_goals, lambda_away)
        
        return prob_home * prob_away
    
    def _poisson_probability(self, k, lambda_):
        """Poisson dağılımı"""
        from math import exp, factorial
        return (lambda_ ** k) * exp(-lambda_) / factorial(k)
    
    def _determine_confidence(self, probability):
        """Güven seviyesi belirle"""
        if probability >= config.HIGH_CONFIDENCE_THRESHOLD:
            return 'high'
        elif probability >= config.MEDIUM_CONFIDENCE_THRESHOLD:
            return 'medium'
        else:
            return 'low'