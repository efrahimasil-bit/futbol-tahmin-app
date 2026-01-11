"""
Konfigürasyon dosyası - API anahtarları ve ayarlar
"""

# API Anahtarları (Kendi anahtarlarınızı buraya ekleyin)
API_FOOTBALL_KEY = "YOUR_API_FOOTBALL_KEY_HERE"
SPORTMONKS_KEY = "YOUR_SPORTMONKS_KEY_HERE"

# API Endpoints
API_FOOTBALL_BASE = "https://v3.football.api-sports.io"
SPORTMONKS_BASE = "https://api.sportmonks.com/v3/football"

# Uygulama Ayarları
REFRESH_INTERVAL = 300  # 5 dakika (saniye)
MAX_MATCHES_DISPLAY = 20
CACHE_TTL = 300  # Cache süresi (saniye)

# Tahmin Ayarları
MIN_CONFIDENCE_THRESHOLD = 0.15
HIGH_CONFIDENCE_THRESHOLD = 0.25
MEDIUM_CONFIDENCE_THRESHOLD = 0.18

# Güven seviyeleri için renkler
CONFIDENCE_COLORS = {
    'high': '#22c55e',    # Yeşil
    'medium': '#eab308',  # Sarı
    'low': '#ef4444'      # Kırmızı
}

# İlk yarı/Maç sonucu kombinasyonları
HALFTIME_FULLTIME_OUTCOMES = [
    '1/1', '1/X', '1/2',
    'X/1', 'X/X', 'X/2',
    '2/1', '2/X', '2/2',
    '1/0', '2/0', '0/1', '0/2', '0/0'
]

# İlk yarı skor tahminleri
HALFTIME_SCORES = [
    '0-0', '1-0', '0-1', '1-1',
    '2-0', '0-2', '2-1', '1-2', '2-2'
]

# Maç sonu skor tahminleri
FULLTIME_SCORES = [
    '0-0', '1-0', '0-1', '2-0', '0-2',
    '2-1', '1-2', '3-0', '0-3', '3-1',
    '1-3', '2-2', '3-2', '2-3'
]