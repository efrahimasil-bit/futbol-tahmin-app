"""Konfigürasyon Ayarları"""
import os

# API Ayarları
API_FOOTBALL_KEY = os.getenv('API_FOOTBALL_KEY', 'YOUR_API_KEY_HERE')
API_FOOTBALL_BASE_URL = 'https://v3.football.api-sports.io'

# Cache Ayarları
CACHE_TTL = 300  # 5 dakika

# Uygulama Ayarları
MAX_MATCHES_DISPLAY = 20
DEFAULT_TIMEZONE = 'Europe/Istanbul'

# Tahmin Parametreleri
CONFIDENCE_THRESHOLDS = {
    'high': 0.70,
    'medium': 0.50,
    'low': 0.30
}

# Model Ayarları
MODEL_FEATURES = [
    'home_goals_avg',
    'away_goals_avg',
    'home_conceded_avg',
    'away_conceded_avg',
    'home_advantage',
    'recent_form'
]

# Desteklenen Ligler
SUPPORTED_LEAGUES = [
    39,   # Premier League
    140,  # La Liga
    78,   # Bundesliga
    135,  # Serie A
    61,   # Ligue 1
    203,  # Süper Lig
    88,   # Eredivisie
    94,   # Primeira Liga
]

# Oran Tipleri
ODDS_MARKETS = {
    'match_winner': 1,
    'halftime_fulltime': 6,
    'correct_score': 9,
    'goals_over_under': 5,
    'both_teams_score': 8
}
