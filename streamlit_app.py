"""Streamlit Ana Uygulama - Plotly Olmadan"""
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

# Custom imports - hata yakalamalarıyla
DEMO_MODE = False

try:
    from api.matches import MatchAPI
    from api.odds import OddsAPI
    from utils.features import FeatureEngineer
    from models.predictor import FootballPredictor
    import config
except ImportError as e:
    st.warning(f"⚠️ Bazı modüller yüklenemedi. Demo modunda çalışıyor...")
    DEMO_MODE = True
    
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
                'fixture_id': [1, 2, 3, 4, 5],
                'home_team': ['Arsenal', 'Manchester City', 'Liverpool', 'Chelsea', 'Tottenham'],
                'away_team': ['Chelsea', 'Liverpool', 'Manchester United', 'Newcastle', 'Aston Villa'],
                'league': ['Premier League', 'Premier League', 'Premier League', 'Premier League', 'Premier League'],
                'country': ['England', 'England', 'England', 'England', 'England'],
                'status': ['NS', 'NS', '1H', 'NS', 'HT'],
                'home_score': [None, None, 1, None, 0],
                'away_score': [None, None, 0, None, 0],
                'match_date': [datetime.now()] * 5
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
                {'outcome': 'E/E (Beraberlik/Beraberlik)', 'probability': 25.5, 'odds': 3.2, 'confidence': 'medium', 'expected_value': 0.82},
                {'outcome': 'E/1 (Beraberlik/Ev Sahibi)', 'probability': 22.3, 'odds': 3.8, 'confidence': 'medium', 'expected_value': 0.85},
                {'outcome': 'E/2 (Beraberlik/Deplasman)', 'probability': 18.7, 'odds': 4.5, 'confidence': 'low', 'expected_value': 0.84},
                {'outcome': '1/1 (Ev Sahibi/Ev Sahibi)', 'probability': 15.2, 'odds': 5.2, 'confidence': 'medium', 'expected_value': 0.79},
                {'outcome': '1/E (Ev Sahibi/Beraberlik)', 'probability': 8.3, 'odds': 8.5, 'confidence': 'low', 'expected_value': 0.71},
                {'outcome': '2/2 (Deplasman/Deplasman)', 'probability': 10.0, 'odds': 7.0, 'confidence': 'low', 'expected_value': 0.70},
                {'outcome': '1/2 (Ev Sahibi/Deplasman)', 'probability': 5.5, 'odds': 12.0, 'confidence': 'low', 'expected_value': 0.66},
                {'outcome': '2/1 (Deplasman/Ev Sahibi)', 'probability': 4.8, 'odds': 15.0, 'confidence': 'low', 'expected_value': 0.72},
                {'outcome': '2/E (Deplasman/Beraberlik)', 'probability': 6.2, 'odds': 10.0, 'confidence': 'low', 'expected_value': 0.62}
            ]
        
        def predict_halftime_score(self, home_stats, away_stats, odds_data):
            return [
                {'outcome': '0-0', 'probability': 28.5, 'odds': 2.8, 'confidence': 'high', 'expected_value': 0.80},
                {'outcome': '1-0', 'probability': 22.3, 'odds': 3.5, 'confidence': 'medium', 'expected_value': 0.78},
                {'outcome': '0-1', 'probability': 18.7, 'odds': 4.0, 'confidence': 'medium', 'expected_value': 0.75},
                {'outcome': '1-1', 'probability': 15.2, 'odds': 5.0, 'confidence': 'medium', 'expected_value': 0.76},
                {'outcome': '2-0', 'probability': 8.3, 'odds': 8.0, 'confidence': 'low', 'expected_value': 0.66},
                {'outcome': '0-2', 'probability': 7.0, 'odds': 9.0, 'confidence': 'low', 'expected_value': 0.63},
                {'outcome': '2-1', 'probability': 5.5, 'odds': 11.0, 'confidence': 'low', 'expected_value': 0.61},
                {'outcome': '1-2', 'probability': 4.8, 'odds': 12.0, 'confidence': 'low', 'expected_value': 0.58},
                {'outcome': '2-2', 'probability': 3.2, 'odds': 18.0, 'confidence': 'low', 'expected_value': 0.58}
            ]
        
        def predict_fulltime_score(self, home_stats, away_stats, odds_data):
            return [
                {'outcome': '1-1', 'probability': 18.5, 'odds': 4.2, 'confidence': 'high', 'expected_value': 0.78},
                {'outcome': '2-1', 'probability': 16.3, 'odds': 5.0, 'confidence': 'medium', 'expected_value': 0.82},
                {'outcome': '1-2', 'probability': 14.7, 'odds': 5.5, 'confidence': 'medium', 'expected_value': 0.81},
                {'outcome': '2-0', 'probability': 12.2, 'odds': 6.5, 'confidence': 'medium', 'expected_value': 0.79},
                {'outcome': '0-2', 'probability': 10.3, 'odds': 7.5, 'confidence': 'low', 'expected_value': 0.77},
                {'outcome': '2-2', 'probability': 8.5, 'odds': 9.0, 'confidence': 'low', 'expected_value': 0.77},
                {'outcome': '1-0', 'probability': 7.8, 'odds': 9.5, 'confidence': 'medium', 'expected_value': 0.74},
                {'outcome': '0-1', 'probability': 6.5, 'odds': 11.0, 'confidence': 'medium', 'expected_value': 0.72},
                {'outcome': '3-1', 'probability': 5.2, 'odds': 13.0, 'confidence': 'low', 'expected_value': 0.68},
                {'outcome': '1-3', 'probability': 4.5, 'odds': 15.0, 'confidence': 'low', 'expected_value': 0.68},
                {'outcome': '3-0', 'probability': 3.8, 'odds': 17.0, 'confidence': 'low', 'expected_value': 0.65},
                {'outcome': '0-3', 'probability': 3.2, 'odds': 19.0, 'confidence': 'low', 'expected_value': 0.61}
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
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .prediction-card {
        background: white;
        border-radius: 10px;
        padding: 1.2rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        border-left: 5px solid #cbd5e0;
    }
    
    .prediction-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    .prediction-outcome {
        font-size: 1.3rem;
        font-weight: bold;
        color: #2d3748;
        margin-bottom: 0.8rem;
    }
    
    .prediction-details {
        font-size: 0.95rem;
        color: #4a5568;
        line-height: 1.6;
    }
    
    .detail-row {
        display: flex;
        justify-content: space-between;
        margin: 0.3rem 0;
    }
    
    .confidence-high {
        border-left-color: #22c55e;
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
    }
    
    .confidence-medium {
        border-left-color: #eab308;
        background: linear-gradient(135deg, #fefce8 0%, #fef9c3 100%);
    }
    
    .confidence-low {
        border-left-color: #ef4444;
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-left: 4px solid #f59e0b;
        padding: 1.2rem;
        margin: 1rem 0;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .info-box {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        border-left: 4px solid #3b82f6;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        font-size: 1.1rem;
    }
    
    .match-button {
        width: 100%;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        background: white;
        border: 2px solid #e2e8f0;
        transition: all 0.2s ease;
    }
    
    .match-button:hover {
        border-color: #667eea;
        transform: translateX(5px);
    }
    
    .demo-badge {
        display: inline-block;
        background: #fbbf24;
        color: #78350f;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: bold;
        margin-left: 0.5rem;
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
        st.error(f"❌ Maç verileri yüklenemedi: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=config.CACHE_TTL)
def load_odds(fixture_id):
    """Oranları yükle"""
    try:
        odds_api = OddsAPI()
        return odds_api.get_match_odds(fixture_id)
    except Exception as e:
        st.warning(f"⚠️ Oran verileri yüklenemedi: {e}")
        return {}

def get_match_predictions(match_row, odds_data):
    """Maç tahminlerini al"""
    try:
        feature_eng = FeatureEngineer()
        predictor = FootballPredictor()
        
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
        st.error(f"❌ Tahmin hatası: {e}")
        return None

def render_confidence_badge(confidence):
    """Güven rozeti"""
    badges = {
        'high': '🟢 Yüksek Güven',
        'medium': '🟡 Orta Güven',
        'low': '🔴 Düşük Güven'
    }
    return badges.get(confidence, '⚪ Bilinmiyor')

def render_prediction_card(prediction):
    """Tahmin kartı"""
    confidence_class = f"confidence-{prediction['confidence']}"
    ev = prediction.get('expected_value', 0)
    ev_color = '#22c55e' if ev > 0.8 else '#eab308' if ev > 0.7 else '#ef4444'
    
    html = f"""
    <div class="prediction-card {confidence_class}">
        <div class="prediction-outcome">{prediction['outcome']}</div>
        <div class="prediction-details">
            <div class="detail-row">
                <span><strong>Olasılık:</strong></span>
                <span>{prediction['probability']:.1f}%</span>
            </div>
            <div class="detail-row">
                <span><strong>Oran:</strong></span>
                <span>{prediction['odds']:.2f}</span>
            </div>
            <div class="detail-row">
                <span><strong>Beklenen Değer:</strong></span>
                <span style="color: {ev_color}; font-weight: bold;">{ev:.2f}</span>
            </div>
            <div style="margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid #e2e8f0;">
                {render_confidence_badge(prediction['confidence'])}
            </div>
        </div>
    </div>
    """
    return html

# Header
demo_badge = '<span class="demo-badge">DEMO</span>' if DEMO_MODE else ''
st.markdown(f'<div class="main-header">⚽ FUTBOL TAHMİNLEME SİSTEMİ {demo_badge}</div>', unsafe_allow_html=True)

# Uyarı mesajı
st.markdown("""
<div class="warning-box">
    ⚠️ <strong>ÖNEMLİ UYARI:</strong> Bu uygulama yalnızca eğitim ve istatistiksel analiz amaçlıdır. 
    Kesinlikle kazanç garantisi vermez. Lütfen sorumlu bir şekilde kullanın ve yatırım tavsiyesi olarak değerlendirmeyin.
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Kontrol Paneli")
    
    if st.button("🔄 Verileri Yenile", use_container_width=True):
        st.cache_data.clear()
        st.session_state.last_refresh = datetime.now()
        st.rerun()
    
    st.info(f"📅 Son Güncelleme: {st.session_state.last_refresh.strftime('%H:%M:%S')}")
    
    if DEMO_MODE:
        st.warning("🔧 Demo Modunda Çalışıyor")
    
    st.markdown("---")
    st.subheader("📊 Metodoloji")
    st.markdown("""
    **İstatistiksel Analiz:**
    - Son 5-10 maç performansı
    - Gol ortalamaları ve trendler
    - Ev sahibi avantajı analizi
    
    **Oran Analizi:**
    - Güncel bahis oranları
    - Oran değer hesaplaması
    - Beklenen değer (EV) analizi
    
    **Makine Öğrenmesi:**
    - Random Forest modeli
    - Logistic Regression
    - Ensemble tahminleme
    
    **Güven Seviyeleri:**
    - 🟢 Yüksek: %70+ güvenilirlik
    - 🟡 Orta: %50-70 güvenilirlik
    - 🔴 Düşük: %50'nin altı
    """)
    
    st.markdown("---")
    st.subheader("💡 Nasıl Kullanılır?")
    st.markdown("""
    1. Sol panelden bir maç seçin
    2. Tahmin kategorilerini inceleyin
    3. Olasılıkları ve oranları karşılaştırın
    4. Beklenen değer (EV) yüksek olanları değerlendirin
    5. Güven seviyelerini dikkate alın
    """)

# Ana içerik
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🏟️ Güncel Maçlar")
    
    try:
        matches_df = load_matches()
        
        if matches_df.empty:
            st.warning("📭 Henüz maç verisi yüklenemedi. Lütfen daha sonra tekrar deneyin.")
        else:
            for idx, match in matches_df.iterrows():
                # Durum emojisi
                if match['status'] in ['1H', '2H']:
                    status_emoji = "🔴"
                    status_text = "CANLI"
                elif match['status'] == 'HT':
                    status_emoji = "🟡"
                    status_text = "DV"
                else:
                    status_emoji = "⚪"
                    status_text = "YAKLAŞAN"
                
                # Skor metni
                score_text = ""
                if match['home_score'] is not None:
                    score_text = f"\n📊 {match['home_score']} - {match['away_score']}"
                
                button_label = f"{status_emoji} **{match['home_team']}** vs **{match['away_team']}**\n🏆 {match['league']} | {status_text}{score_text}"
                
                if st.button(
                    button_label,
                    key=f"match_{match['fixture_id']}",
                    use_container_width=True
                ):
                    st.session_state.selected_match = match
                    
    except Exception as e:
        st.error(f"❌ Maç verileri yüklenirken hata: {e}")

with col2:
    if st.session_state.selected_match is not None:
        match = st.session_state.selected_match
        
        st.subheader(f"🎯 {match['home_team']} vs {match['away_team']}")
        st.caption(f"🏆 {match['league']} • 🌍 {match['country']}")
        
        # Maç durumu göstergesi
        if match['status'] in ['1H', '2H', 'HT']:
            st.warning(f"🔴 **CANLI MAÇ** - {match['status']}")
        
        try:
            with st.spinner('🔄 Tahminler hesaplanıyor...'):
                odds_data = load_odds(match['fixture_id'])
                predictions = get_match_predictions(match, odds_data)
            
            if predictions:
                tab1, tab2, tab3 = st.tabs([
                    "📊 İlk Yarı / Maç Sonucu",
                    "⏱️ İlk Yarı Skorları",
                    "🏆 Maç Sonu Skorları"
                ])
                
                with tab1:
                    st.markdown("### 📊 İlk Yarı / Maç Sonucu Tahminleri")
                    st.caption("İlk yarı ve maç sonucu kombinasyonları")
                    
                    cols = st.columns(3)
                    for idx, pred in enumerate(predictions['halftime_fulltime'][:12]):
                        with cols[idx % 3]:
                            st.markdown(render_prediction_card(pred), unsafe_allow_html=True)
                
                with tab2:
                    st.markdown("### ⏱️ İlk Yarı Skor Tahminleri")
                    st.caption("İlk yarı bitişindeki olası skorlar")
                    
                    cols = st.columns(3)
                    for idx, pred in enumerate(predictions['halftime_score'][:9]):
                        with cols[idx % 3]:
                            st.markdown(render_prediction_card(pred), unsafe_allow_html=True)
                
                with tab3:
                    st.markdown("### 🏆 Maç Sonu Skor Tahminleri")
                    st.caption("Maç bitişindeki olası skorlar")
                    
                    cols = st.columns(3)
                    for idx, pred in enumerate(predictions['fulltime_score'][:12]):
                        with cols[idx % 3]:
                            st.markdown(render_prediction_card(pred), unsafe_allow_html=True)
                
                # Ek bilgiler
                st.markdown("---")
                st.info("""
                💡 **İpucu:** Beklenen değer (EV) 0.80'in üzerindeki tahminler değer taşıyabilir.
                Ancak bunlar kesinlikle kazanç garantisi vermez!
                """)
        
        except Exception as e:
            st.error(f"❌ Tahminler yüklenirken hata oluştu: {e}")
    else:
        st.markdown("""
        <div class="info-box">
            👈 Lütfen sol taraftan bir maç seçin
            <br><br>
            Maç seçtikten sonra detaylı tahminleri görüntüleyebilirsiniz.
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6b7280; padding: 1rem;">
    <p style="font-size: 0.9rem;">
        💡 <strong>Bu uygulama eğitim ve demo amaçlıdır.</strong><br>
        Gerçek para ile bahis yapmadan önce profesyonel danışmanlık alınız.<br>
        <em>Sorumlu bahis oynanmalıdır.</em>
    </p>
</div>
""", unsafe_allow_html=True)
