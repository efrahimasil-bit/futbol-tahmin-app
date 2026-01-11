"""
Streamlit Ana Uygulama
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# Custom imports
from api.matches import MatchAPI
from api.odds import OddsAPI
from utils.features import FeatureEngineer
from models.predictor import FootballPredictor
import config

# Sayfa yapılandırması
st.set_page_config(
    page_title="⚽ Futbol Tahminleme Sistemi",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1e40af;
        text-align: center;
        margin-bottom: 1rem;
    }
    .warning-box {
        background-color: #fef3c7;
        border-left: 5px solid #f59e0b;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
    }
    .match-card {
        background-color: #f9fafb;
        border: 2px solid #e5e7eb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
        cursor: pointer;
    }
    .match-card:hover {
        border-color: #3b82f6;
        background-color: #eff6ff;
    }
    .prediction-card {
        border: 2px solid #e5e7eb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem;
        text-align: center;
    }
    .confidence-high {
        background-color: #d1fae5;
        border-color: #10b981;
    }
    .confidence-medium {
        background-color: #fef3c7;
        border-color: #f59e0b;
    }
    .confidence-low {
        background-color: #fee2e2;
        border-color: #ef4444;
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
    match_api = MatchAPI()
    live_matches = match_api.get_live_matches()
    upcoming_matches = match_api.get_upcoming_matches()
    all_matches = pd.concat([live_matches, upcoming_matches], ignore_index=True)
    return all_matches.head(config.MAX_MATCHES_DISPLAY)

@st.cache_data(ttl=config.CACHE_TTL)
def load_odds(fixture_id):
    """Oranları yükle"""
    odds_api = OddsAPI()
    return odds_api.get_match_odds(fixture_id)

def get_match_predictions(match_row, odds_data):
    """Maç tahminlerini al"""
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
        <h3 style="font-size: 1.8rem; margin: 0;">{prediction['outcome']}</h3>
        <div style="margin: 0.5rem 0;">
            <strong>Olasılık:</strong> {prediction['probability']:.1f}%
        </div>
        <div style="margin: 0.5rem 0;">
            <strong>Oran:</strong> <span style="color: #2563eb; font-weight: bold;">{prediction['odds']:.2f}</span>
        </div>
        <div style="margin-top: 0.5rem;">
            {render_confidence_badge(prediction['confidence'])}
        </div>
        <div style="width: 100%; background-color: #e5e7eb; border-radius: 0.25rem; height: 0.5rem; margin-top: 0.5rem;">
            <div style="width: {min(prediction['probability'], 100):.0f}%; background-color: {config.CONFIDENCE_COLORS[prediction['confidence']]}; height: 100%; border-radius: 0.25rem;"></div>
        </div>
    </div>
    """
    return html

# Header
st.markdown('<p class="main-header">⚽ FUTBOL TAHMİNLEME SİSTEMİ</p>', unsafe_allow_html=True)

# Uyarı mesajı
st.markdown("""
<div class="warning-box">
    <strong>⚠️ UYARI:</strong> Bu uygulama yalnızca istatistiksel tahmin amaçlıdır. 
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
                
                if st.button(
                    f"{status_emoji} {match['home_team']} vs {match['away_team']}\n{match['league']} | {status_text} {score_text}",
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
        st.info("👈 Lütfen sol taraftan bir maç seçin")

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6b7280; font-size: 0.875rem;">
    💡 Bu uygulama eğitim ve demo amaçlıdır.
</div>
""", unsafe_allow_html=True)
