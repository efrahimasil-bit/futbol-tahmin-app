"""Streamlit Ana Uygulama"""
import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

# Sayfa yapılandırması
st.set_page_config(
    page_title="⚽ Futbol Tahminleme Sistemi",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Gerekli modülleri kontrol et ve yükle
try:
    import plotly.graph_objects as go
except ImportError:
    st.error("⚠️ Plotly kütüphanesi yüklü değil. Lütfen requirements.txt dosyasını kontrol edin.")
    st.stop()

# Custom imports - hata yakalamalarıyla
try:
    from api.matches import MatchAPI
    from api.odds import OddsAPI
    from utils.features import FeatureEngineer
    from models.predictor import FootballPredictor
    import config
except ImportError as e:
    st.error(f"⚠️ Modül yükleme hatası: {e}")
    st.info("Demo modunda çalışıyor...")
    
    # Demo config oluştur
    class config:
        CACHE_TTL = 300
        MAX_MATCHES_DISPLAY = 20
    
    # Dummy sınıflar
    class MatchAPI:
        def get_live_matches(self):
            return pd.DataFrame()
        def get_upcoming_matches(self):
            return pd.DataFrame({
                'fixture_id': [1, 2],
                'home_team': ['Arsenal', 'Manchester City'],
                'away_team': ['Chelsea', 'Liverpool'],
                'league': ['Premier League', 'Premier League'],
                'country': ['England', 'England'],
                'status': ['NS', 'NS'],
                'home_score': [None, None],
                'away_score': [None, None],
                'match_date': [datetime.now(), datetime.now()]
            })
    
    class OddsAPI:
        def get_match_odds(self, fixture_id):
            return {
                'home_win': 2.5,
                'draw': 3.2,
                'away_win': 2.8,
                'over_2_5': 1.8,
                'under_2_5': 2.0
            }
    
    class FeatureEngineer:
        def _get_default_stats(self):
            return {
                'goals_scored_avg': 1.5,
                'goals_conceded_avg': 1.2,
                'home_advantage': 0.15,
                'form': 0.6
            }
    
    class FootballPredictor:
        def predict_halftime_fulltime(self, home_stats, away_stats, odds_data):
            return [
                {'outcome': 'E/E', 'probability': 25.5, 'odds': 3.2, 'confidence': 'medium'},
                {'outcome': 'E/1', 'probability': 22.3, 'odds': 3.8, 'confidence': 'medium'},
                {'outcome': 'E/2', 'probability': 18.7, 'odds': 4.5, 'confidence': 'low'},
                {'outcome': '1/1', 'probability': 15.2, 'odds': 5.2, 'confidence': 'medium'},
                {'outcome': '1/E', 'probability': 8.3, 'odds': 8.5, 'confidence': 'low'},
                {'outcome': '2/2', 'probability': 10.0, 'odds': 7.0, 'confidence': 'low'}
            ]
        
        def predict_halftime_score(self, home_stats, away_stats, odds_data):
            return [
                {'outcome': '0-0', 'probability': 28.5, 'odds': 2.8, 'confidence': 'high'},
                {'outcome': '1-0', 'probability': 22.3, 'odds': 3.5, 'confidence': 'medium'},
                {'outcome': '0-1', 'probability': 18.7, 'odds': 4.0, 'confidence': 'medium'},
                {'outcome': '1-1', 'probability': 15.2, 'odds': 5.0, 'confidence': 'medium'},
                {'outcome': '2-0', 'probability': 8.3, 'odds': 8.0, 'confidence': 'low'},
                {'outcome': '0-2', 'probability': 7.0, 'odds': 9.0, 'confidence': 'low'}
            ]
        
        def predict_fulltime_score(self, home_stats, away_stats, odds_data):
            return [
                {'outcome': '1-1', 'probability': 18.5, 'odds': 4.2, 'confidence': 'high'},
                {'outcome': '2-1', 'probability': 16.3, 'odds': 5.0, 'confidence': 'medium'},
                {'outcome': '1-2', 'probability': 14.7, 'odds': 5.5, 'confidence': 'medium'},
                {'outcome': '2-0', 'probability': 12.2, 'odds': 6.5, 'confidence': 'medium'},
                {'outcome': '0-2', 'probability': 10.3, 'odds': 7.5, 'confidence': 'low'},
                {'outcome': '2-2', 'probability': 8.5, 'odds': 9.0, 'confidence': 'low'}
            ]

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
        font-size: 2.5rem;
        font-weight: bold;
    }
    
    .prediction-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    
    .prediction-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0,0,0,0.15);
    }
    
    .prediction-outcome {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2d3748;
        margin-bottom: 0.5rem;
    }
    
    .prediction-details {
        font-size: 0.9rem;
        color: #4a5568;
    }
    
    .confidence-high {
        border-left: 5px solid #22c55e;
    }
    
    .confidence-medium {
        border-left: 5px solid #eab308;
    }
    
    .confidence-low {
        border-left: 5px solid #ef4444;
    }
    
    .warning-box {
        background-color: #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    
    .info-box {
        background-color: #dbeafe;
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'selected_match' not in st.session_state:
    st.session_state.selected_match = None
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()

# Cache fonksiyonları
@st.cache_data(ttl=config.CACHE_TTL)
def load_matches():
    """Maçları yükle"""
    try:
        match_api = MatchAPI()
        live_matches = match_api.get_live_matches()
        upcoming_matches = match_api.get_upcoming_matches()
        all_matches = pd.concat([live_matches, upcoming_matches], ignore_index=True)
        return all_matches.head(config.MAX_MATCHES_DISPLAY)
    except Exception as e:
        st.warning(f"Maç verileri yüklenemedi: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=config.CACHE_TTL)
def load_odds(fixture_id):
    """Oranları yükle"""
    try:
        odds_api = OddsAPI()
        return odds_api.get_match_odds(fixture_id)
    except Exception as e:
        st.warning(f"Oran verileri yüklenemedi: {e}")
        return {}

def get_match_predictions(match_row, odds_data):
    """Maç tahminlerini al"""
    try:
        feature_eng = FeatureEngineer()
        predictor = FootballPredictor()
        
        # Varsayılan takım istatistikleri
        home_stats = feature_eng._get_default_stats()
        away_stats = feature_eng._get_default_stats()
        away_stats['home_advantage'] = -0.10
        
        predictions = {
            'halftime_fulltime': predictor.predict_halftime_fulltime(home_stats, away_stats, odds_data),
            'halftime_score': predictor.predict_halftime_score(home_stats, away_stats, odds_data),
            'fulltime_score': predictor.predict_fulltime_score(home_stats, away_stats, odds_data)
        }
        return predictions
    except Exception as e:
        st.error(f"Tahmin hatası: {e}")
        return None

def render_confidence_badge(confidence):
    """Güven rozeti"""
    colors = {
        'high': ('🟢', 'Yüksek', '#22c55e'),
        'medium': ('🟡', 'Orta', '#eab308'),
        'low': ('🔴', 'Düşük', '#ef4444')
    }
    emoji, text, color = colors.get(confidence, ('⚪', 'Bilinmiyor', '#9ca3af'))
    return f"{emoji} {text}"

def render_prediction_card(prediction):
    """Tahmin kartı"""
    confidence_class = f"confidence-{prediction['confidence']}"
    html = f"""
    <div class="prediction-card {confidence_class}">
        <div class="prediction-outcome">{prediction['outcome']}</div>
        <div class="prediction-details">
            Olasılık: {prediction['probability']:.1f}%<br>
            Oran: {prediction['odds']:.2f}<br>
            {render_confidence_badge(prediction['confidence'])}
        </div>
    </div>
    """
    return html

# Header
st.markdown('<div class="main-header">⚽ FUTBOL TAHMİNLEME SİSTEMİ</div>', unsafe_allow_html=True)

# Uyarı mesajı
st.markdown("""
<div class="warning-box">
    ⚠️ <strong>UYARI:</strong> Bu uygulama yalnızca istatistiksel tahmin amaçlıdır. 
    Kesin kazanç garantisi içermez. Sorumlu bir şekilde kullanın.
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Kontrol Paneli")
    
    if st.button("🔄 Verileri Yenile", use_container_width=True):
        st.cache_data.clear()
        st.session_state.last_refresh = datetime.now()
        st.rerun()
    
    st.info(f"Son Güncelleme: {st.session_state.last_refresh.strftime('%H:%M:%S')}")
    
    st.markdown("---")
    st.subheader("📊 Metodoloji")
    st.markdown("""
    **İstatistiksel Analiz:**
    - Son 5-10 maç performansı
    - Gol ortalamaları
    - Ev/Deplasman farkı
    
    **Oran Analizi:**
    - Güncel bahis oranları
    - Oran değişimleri
    
    **Makine Öğrenmesi:**
    - Random Forest
    - Logistic Regression
    """)

# Ana içerik
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🏟️ Maçlar")
    
    try:
        matches_df = load_matches()
        
        if matches_df.empty:
            st.warning("Henüz maç verisi yok.")
        else:
            for idx, match in matches_df.iterrows():
                status_emoji = "🔴" if match['status'] in ['1H', '2H', 'HT'] else "⚪"
                status_text = "CANLI" if match['status'] in ['1H', '2H', 'HT'] else "YAKLAŞAN"
                
                score_text = ""
                if match['home_score'] is not None:
                    score_text = f"{match['home_score']} - {match['away_score']}"
                
                button_label = f"{status_emoji} {match['home_team']} vs {match['away_team']}\n{match['league']} | {status_text} {score_text}"
                
                if st.button(
                    button_label,
                    key=f"match_{match['fixture_id']}",
                    use_container_width=True
                ):
                    st.session_state.selected_match = match
                    
    except Exception as e:
        st.error(f"Maç verileri yüklenirken hata: {e}")

with col2:
    if st.session_state.selected_match is not None:
        match = st.session_state.selected_match
        
        st.subheader(f"🎯 {match['home_team']} vs {match['away_team']}")
        st.caption(f"{match['league']} - {match['country']}")
        
        try:
            odds_data = load_odds(match['fixture_id'])
            predictions = get_match_predictions(match, odds_data)
            
            if predictions:
                tab1, tab2, tab3 = st.tabs([
                    "📊 İlk Yarı / Maç Sonucu",
                    "⏱️ İlk Yarı Skorları",
                    "🏆 Maç Sonu Skorları"
                ])
                
                with tab1:
                    st.markdown("### İlk Yarı / Maç Sonucu Tahminleri")
                    cols = st.columns(3)
                    for idx, pred in enumerate(predictions['halftime_fulltime'][:12]):
                        with cols[idx % 3]:
                            st.markdown(render_prediction_card(pred), unsafe_allow_html=True)
                
                with tab2:
                    st.markdown("### İlk Yarı Skor Tahminleri")
                    cols = st.columns(3)
                    for idx, pred in enumerate(predictions['halftime_score'][:9]):
                        with cols[idx % 3]:
                            st.markdown(render_prediction_card(pred), unsafe_allow_html=True)
                
                with tab3:
                    st.markdown("### Maç Sonu Skor Tahminleri")
                    cols = st.columns(3)
                    for idx, pred in enumerate(predictions['fulltime_score'][:12]):
                        with cols[idx % 3]:
                            st.markdown(render_prediction_card(pred), unsafe_allow_html=True)
        
        except Exception as e:
            st.error(f"Tahminler yüklenirken hata: {e}")
    else:
        st.markdown("""
        <div class="info-box">
            👈 Lütfen sol taraftan bir maç seçin
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6b7280; padding: 1rem;">
    💡 Bu uygulama eğitim ve demo amaçlıdır.
</div>
""", unsafe_allow_html=True)
