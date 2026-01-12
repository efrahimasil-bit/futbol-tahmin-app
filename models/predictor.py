"""Futbol Maç Tahmin Modeli"""
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import config

class FootballPredictor:
    def __init__(self):
        self.rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.lr_model = LogisticRegression(random_state=42)
        self.is_trained = False
    
    def train(self, X, y):
        """Modeli eğit"""
        if X is None or y is None or len(X) == 0:
            return False
        
        try:
            self.rf_model.fit(X, y)
            self.lr_model.fit(X, y)
            self.is_trained = True
            return True
        except Exception as e:
            print(f"Eğitim hatası: {e}")
            return False
    
    def predict_halftime_fulltime(self, home_stats, away_stats, odds_data):
        """İlk yarı / Maç sonucu tahminleri"""
        # Olası kombinasyonlar
        outcomes = [
            'H/H', 'H/D', 'H/A',  # Ev sahibi önde
            'D/H', 'D/D', 'D/A',  # Berabere
            'A/H', 'A/D', 'A/A'   # Deplasman önde
        ]
        
        # Temel olasılıklar hesapla
        base_probs = self._calculate_ht_ft_probabilities(home_stats, away_stats)
        
        predictions = []
        
        for outcome in outcomes:
            # Oran verisinden al veya varsayılan kullan
            odds_key = outcome.replace('/', '/')
            
            if 'halftime_fulltime' in odds_data and outcome in odds_data['halftime_fulltime']:
                odds = odds_data['halftime_fulltime'][outcome]
            else:
                odds = self._get_default_ht_ft_odds(outcome)
            
            probability = base_probs.get(outcome, 5.0)
            expected_value = (probability / 100) * odds
            
            # Güven seviyesi
            if probability > 20:
                confidence = 'high'
            elif probability > 10:
                confidence = 'medium'
            else:
                confidence = 'low'
            
            # Outcome'u açıklamalı hale getir
            outcome_text = self._format_ht_ft_outcome(outcome)
            
            predictions.append({
                'outcome': outcome_text,
                'probability': probability,
                'odds': odds,
                'expected_value': expected_value,
                'confidence': confidence
            })
        
        # Expected value'ya göre sırala
        predictions.sort(key=lambda x: x['expected_value'], reverse=True)
        
        return predictions
    
    def predict_halftime_score(self, home_stats, away_stats, odds_data):
        """İlk yarı skor tahminleri"""
        # İlk yarı gol ortalamaları (genelde daha düşük)
        home_ht_avg = home_stats.get('first_half_goals_avg', 0.7)
        away_ht_avg = away_stats.get('first_half_goals_avg', 0.6)
        
        # Poisson ile olasılıklar
        score_probs = self._poisson_probabilities(home_ht_avg, away_ht_avg, max_goals=3)
        
        predictions = []
        
        for score, probability in score_probs.items():
            if probability < 2.0:  # Çok düşük olasılıkları atla
                continue
            
            # Oran verisinden al veya hesapla
            if 'correct_score' in odds_data and score in odds_data['correct_score']:
                odds = odds_data['correct_score'][score]
            else:
                odds = self._estimate_score_odds(probability)
            
            expected_value = (probability / 100) * odds
            
            # Güven seviyesi
            if probability > 20:
                confidence = 'high'
            elif probability > 10:
                confidence = 'medium'
            else:
                confidence = 'low'
            
            predictions.append({
                'outcome': score,
                'probability': probability,
                'odds': odds,
                'expected_value': expected_value,
                'confidence': confidence
            })
        
        predictions.sort(key=lambda x: x['expected_value'], reverse=True)
        
        return predictions[:15]  # İlk 15 tahmini döndür
    
    def predict_fulltime_score(self, home_stats, away_stats, odds_data):
        """Maç sonu skor tahminleri"""
        # Tam maç gol ortalamaları
        home_avg = home_stats.get('goals_scored_avg', 1.5)
        away_avg = away_stats.get('goals_scored_avg', 1.3)
        
        # Ev sahibi avantajını ekle
        home_avg = home_avg * (1 + home_stats.get('home_advantage', 0.15))
        
        # Poisson ile olasılıklar
        score_probs = self._poisson_probabilities(home_avg, away_avg, max_goals=5)
        
        predictions = []
        
        for score, probability in score_probs.items():
            if probability < 1.5:  # Çok düşük olasılıkları atla
                continue
            
            # Oran verisinden al veya hesapla
            if 'correct_score' in odds_data and score in odds_data['correct_score']:
                odds = odds_data['correct_score'][score]
            else:
                odds = self._estimate_score_odds(probability)
            
            expected_value = (probability / 100) * odds
            
            # Güven seviyesi
            if probability > 15:
                confidence = 'high'
            elif probability > 8:
                confidence = 'medium'
            else:
                confidence = 'low'
            
            predictions.append({
                'outcome': score,
                'probability': probability,
                'odds': odds,
                'expected_value': expected_value,
                'confidence': confidence
            })
        
        predictions.sort(key=lambda x: x['expected_value'], reverse=True)
        
        return predictions[:20]  # İlk 20 tahmini döndür
    
    def _calculate_ht_ft_probabilities(self, home_stats, away_stats):
        """İlk yarı / Maç sonucu olasılıkları hesapla"""
        # Basitleştirilmiş model
        home_strength = home_stats.get('form', 0.5) + home_stats.get('home_advantage', 0.15)
        away_strength = away_stats.get('form', 0.5)
        
        probs = {
            'H/H': 18 + home_strength * 10,  # Ev önde başlar, ev kazanır
            'H/D': 8 + home_strength * 5,    # Ev önde başlar, berabere
            'H/A': 4,                          # Ev önde başlar, deplasman kazanır
            'D/H': 15 + home_strength * 8,   # Berabere başlar, ev kazanır
            'D/D': 20,                         # Berabere başlar, berabere biter
            'D/A': 12 + away_strength * 8,   # Berabere başlar, deplasman kazanır
            'A/H': 3,                          # Deplasman önde, ev kazanır
            'A/D': 7 + away_strength * 5,    # Deplasman önde, berabere
            'A/A': 13 + away_strength * 10   # Deplasman önde, deplasman kazanır
        }
        
        # Normalize et
        total = sum(probs.values())
        for key in probs:
            probs[key] = (probs[key] / total) * 100
        
        return probs
    
    def _poisson_probabilities(self, home_avg, away_avg, max_goals=5):
        """Poisson dağılımı ile skor olasılıkları"""
        from math import exp, factorial
        
        def poisson(expected, actual):
            return (expected ** actual * exp(-expected)) / factorial(actual)
        
        probabilities = {}
        
        for home_goals in range(max_goals + 1):
            for away_goals in range(max_goals + 1):
                prob = poisson(home_avg, home_goals) * poisson(away_avg, away_goals)
                score = f"{home_goals}-{away_goals}"
                probabilities[score] = prob * 100
        
        return probabilities
    
    def _get_default_ht_ft_odds(self, outcome):
        """Varsayılan İY/MS oranları"""
        default_odds = {
            'H/H': 3.5, 'H/D': 8.0, 'H/A': 15.0,
            'D/H': 4.5, 'D/D': 3.2, 'D/A': 4.5,
            'A/H': 15.0, 'A/D': 8.0, 'A/A': 3.8
        }
        return default_odds.get(outcome, 10.0)
    
    def _estimate_score_odds(self, probability):
        """Olasılıktan oran tahmini"""
        if probability <= 0:
            return 50.0
        
        # Basit oran hesaplama: 100 / olasılık
        odds = 100 / probability
        
        # Bahis sitesi marjı ekle (%10)
        odds = odds * 0.9
        
        return max(1.01, round(odds, 2))
    
    def _format_ht_ft_outcome(self, outcome):
        """İY/MS sonucunu formatla"""
        mapping = {
            'H/H': '1/1 (Ev Sahibi/Ev Sahibi)',
            'H/D': '1/X (Ev Sahibi/Beraberlik)',
            'H/A': '1/2 (Ev Sahibi/Deplasman)',
            'D/H': 'X/1 (Beraberlik/Ev Sahibi)',
            'D/D': 'X/X (Beraberlik/Beraberlik)',
            'D/A': 'X/2 (Beraberlik/Deplasman)',
            'A/H': '2/1 (Deplasman/Ev Sahibi)',
            'A/D': '2/X (Deplasman/Beraberlik)',
            'A/A': '2/2 (Deplasman/Deplasman)'
        }
        return mapping.get(outcome, outcome)
    
    def predict_match_winner(self, home_stats, away_stats, odds_data):
        """Maç sonucu tahmini"""
        # Güç hesapla
        home_strength = (
            home_stats['goals_scored_avg'] * 0.3 +
            (3 - home_stats['goals_conceded_avg']) * 0.3 +
            home_stats['form'] * 0.2 +
            home_stats['home_advantage'] * 0.2
        )
        
        away_strength = (
            away_stats['goals_scored_avg'] * 0.3 +
            (3 - away_stats['goals_conceded_avg']) * 0.3 +
            away_stats['form'] * 0.3
        )
        
        total = home_strength + away_strength
        
        home_win_prob = (home_strength / total) * 55  # Ev avantajı
        away_win_prob = (away_strength / total) * 45
        draw_prob = 100 - home_win_prob - away_win_prob
        
        predictions = []
        
        outcomes = {
            'home_win': ('Ev Sahibi Kazanır', home_win_prob),
            'draw': ('Beraberlik', draw_prob),
            'away_win': ('Deplasman Kazanır', away_win_prob)
        }
        
        for key, (label, prob) in outcomes.items():
            odds = odds_data.get(key, 2.5)
            ev = (prob / 100) * odds
            
            predictions.append({
                'outcome': label,
                'probability': prob,
                'odds': odds,
                'expected_value': ev,
                'confidence': 'high' if prob > 40 else 'medium' if prob > 25 else 'low'
            })
        
        predictions.sort(key=lambda x: x['probability'], reverse=True)
        
        return predictions
