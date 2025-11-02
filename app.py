import streamlit as st
import pandas as pd
import random
import time
from streamlit_autorefresh import st_autorefresh
import base64

# ===== CONFIG =====
st.set_page_config(page_title="Spencer Kyle Scanner", layout="wide")

PRICE_MIN = 2
PRICE_MAX = 20
FLOAT_MAX = 20_000_000
REFRESH_SECONDS = 10
TOP_N = 20
WATCHLIST_TOP_N = 5
DEFAULT_SYMBOLS = [
    "AAA","BBB","CCC","DDD","EEE","FFF","GGG","HHH",
    "III","JJJ","KKK","LLL","MMM","NNN","OOO","PPP",
    "QQQ","RRR","SSS","TTT"
]

# ===== STAR LOGIC =====
def star_display(score: int) -> str:
    score = min(max(score, 0), 5)
    sizes = [16,18,20,22,24]  # Gradually increasing
    stars_html = "".join([f'<span style="font-size:{sizes[i]}px; color:#FFD700;">⭐</span>' for i in range(score)])
    return f'<div style="height:24px; text-align:center;">{stars_html}</div>'

# ===== AUTO REFRESH =====
count = st_autorefresh(interval=REFRESH_SECONDS*1000, limit=None, key="autorefresh")

# ===== FAKE DATA GENERATOR =====
random.seed(42)
def generate_fake_for_symbol(sym, seed):
    r = random.Random(f"{sym}-{seed}")
    price = round(r.uniform(PRICE_MIN, PRICE_MAX), 2)
    prev_close = round(price / (1 + r.uniform(-0.15,0.15)),2)
    change_pct = round((price - prev_close)/prev_close*100,2) if prev_close!=0 else 0
    avg_vol = int(r.uniform(10000,5000000))
    volume = int(avg_vol * r.uniform(1,15))
    float_shares = int(r.uniform(500_000,FLOAT_MAX))
    news_score = r.randint(1,5)
    headline_prefix = "BREAKING: " if r.random()<0.25 else ""
    headline = f"{headline_prefix}{sym} {r.choice(['announces','reports','launches','files'])} {r.choice(['earnings','partnership','product'])}"
    return {
        "UP10%": change_pct,
        "Symbol": sym,
        "Price": price,
        "Volume": volume,
        "AvgVol": avg_vol,
        "Float": float_shares,
        "Headline": headline,
        "News Score": news_score
    }

def get_fake_stock_data(symbols, seed):
    return pd.DataFrame([generate_fake_for_symbol(s, seed) for s in symbols[:TOP_N]])

# ===== COPY TO CLIPBOARD =====
st.markdown("""
<script>
function copySymbol(symbol){
    navigator.clipboard.writeText(symbol);
}
</script>
""", unsafe_allow_html=True)

# ===== UPLOAD CHIME FEATURE =====
uploaded_chime = st.sidebar.file_uploader("Upload your own alert audio (.mp3 or .ogg)", type=["mp3","ogg"])
if uploaded_chime:
    chime_data = uploaded_chime.read()
    chime_base64 = base64.b64encode(chime_data).decode()

def play_chime():
    if uploaded_chime:
        st.markdown(f"""
        <audio autoplay>
            <source src="data:audio/ogg;base64,{chime_base64}" type="audio/ogg">
            <source src="data:audio/mpeg;base64,{chime_base64}" type="audio/mpeg">
        </audio>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <audio autoplay>
            <source src="https://actions.google.com/sounds/v1/cash/coin_tap.ogg" type="audio/ogg">
        </audio>
        """, unsafe_allow_html=True)

# ===== CHIME TOGGLE =====
if 'alerts_enabled' not in st.session_state:
    st.session_state.alerts_enabled = True
st.sidebar.checkbox("🔔 Enable Watchlist Chimes", value=st.session_state.alerts_enabled, key="alerts_enabled")

# ===== DATA GENERATION =====
df = get_fake_stock_data(DEFAULT_SYMBOLS, count)
df_sorted = df.sort_values(by="UP10%", ascending=False).reset_index(drop=True)

# ===== WATCHLIST LOGIC =====
watchlist_df = df[
    (df['UP10%'] >= 10) &
    (df['Price'].between(PRICE_MIN, PRICE_MAX)) &
    (df['Volume'] >= 5*df['AvgVol']) &
    (df['Float'] < FLOAT_MAX)
].sort_values(by="UP10%", ascending=False).head(WATCHLIST_TOP_N)

if 'prev_watchlist_symbols' not in st.session_state:
    st.session_state.prev_watchlist_symbols = []
current_symbols = watchlist_df['Symbol'].tolist()

# Play audio for each new stock
if st.session_state.alerts_enabled:
    new_symbols = [s for s in current_symbols if s not in st.session_state.prev_watchlist_symbols]
    for _ in new_symbols:
        play_chime()
st.session_state.prev_watchlist_symbols = current_symbols

# ===== STYLING =====
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Exo+2:wght@500&display=swap');

body {
    background: linear-gradient(-45deg, #0f0f1f, #1a1a2f, #0f0f1f, #1a1a2f);
    background-size: 400% 400%;
    animation: gradientBG 30s ease infinite;
}

@keyframes gradientBG {
    0% {background-position:0% 50%;}
    50% {background-position:100% 50%;}
    100% {background-position:0% 50%;}
}

h1 {
    font-family: 'Orbitron', sans-serif;
    padding: 6px;
    border-radius: 10px;
    display: inline-block;
    text-align:center;
}

.column-header {
    font-family: 'Exo 2', monospace;
    font-weight: 600;
    background-color: #1a1a3a; /* slightly different shade for headers */
}
.row-hover {
    transition: all 0.3s ease-in-out;
}
.row-hover:hover {
    transform: scale(1.02);
    box-shadow: 0 0 10px #0ff, 0 0 20px #0ff inset;
}
.ticker {
    overflow: hidden;
    white-space: nowrap;
    display: block;
    font-family: 'Exo 2', monospace;
    font-weight: 600;
    color: #ff33ff;
    animation: scroll 15s linear infinite;
}
@keyframes scroll {
    0% { transform: translateX(100%); }
    100% { transform: translateX(-100%); }
}
.pulse {
    display:inline-block;
    animation: pulse 1s infinite alternate;
}
@keyframes pulse {
    0% { text-shadow: 0 0 3px #ff3300,0 0 6px #ff3300; }
    50% { text-shadow: 0 0 6px #ff0000,0 0 12px #ff6600; }
    100% { text-shadow: 0 0 3px #ff3300,0 0 6px #ff3300; }
}
</style>
""", unsafe_allow_html=True)

# ===== WATCHLIST TITLE =====
st.markdown('<h1 style="color:#00ffff; text-shadow:0 0 6px #0ff,0 0 12px #0ff;">🏅 WATCHLIST</h1>', unsafe_allow_html=True)

# ===== WATCHLIST HEADERS =====
st.markdown("""
<div style="display:flex; flex-direction:row; font-weight:bold; color:#ffffff; padding:6px; margin-bottom:4px; text-align:center;">
    <div class="column-header" style="width:5%;">📈 UP10%</div>
    <div class="column-header" style="width:5%;">#️⃣</div>
    <div class="column-header" style="width:10%;">💠 SYMBOL</div>
    <div class="column-header" style="width:10%;">💲 PRICE</div>
    <div class="column-header" style="width:12%;">📊 VOLUME</div>
    <div class="column-header" style="width:12%;">📦 FLOAT</div>
    <div class="column-header" style="width:24%;">📰 NEWS</div>
    <div class="column-header" style="width:15%;">⭐ NEWS SCORE</div>
</div>
""", unsafe_allow_html=True)

# ===== WATCHLIST ROWS =====
for idx, row in watchlist_df.iterrows():
    symbol_id = f"watchlist-{idx}"
    stars_html = star_display(row['News Score'])
    up10 = f'<span class="pulse">📈 {row["UP10%"]}%</span>' if row['UP10%'] >= 10 else f'📈 {row["UP10%"]}%'
    st.markdown(f"""
    <div class="row-hover" style="display:flex; flex-direction:row; align-items:center; justify-content:center; background:linear-gradient(145deg, #111133, #222266); border-radius:12px; padding:8px; margin-bottom:5px;">
        <div style="width:5%; text-align:center; color:#00ff00;">{up10}</div>
        <div style="width:5%; text-align:center; color:#ffffff;">{idx+1}</div>
        <div style="width:10%; text-align:center; color:#00ffff; cursor:pointer;" onclick="copySymbol('{row['Symbol']}')">{row['Symbol']}</div>
        <div style="width:10%; text-align:center; color:#00ff00;">${row['Price']}</div>
        <div style="width:12%; text-align:center; color:#ffcc00;">{row['Volume']}</div>
        <div style="width:12%; text-align:center; color:#ff99ff;">{row['Float']}</div>
        <div style="width:24%; text-align:center;"><span class="ticker">{row['Headline']}</span></div>
        <div style="width:15%; text-align:center;">{stars_html}</div>
    </div>
    """, unsafe_allow_html=True)

# ===== DIVIDER =====
st.markdown("<hr style='border:2px solid #00ffff; margin:20px 0;'>", unsafe_allow_html=True)

# ===== SCANNER TITLE =====
st.markdown('<h1 style="color:#ff9900; text-shadow:0 0 6px #f90,0 0 12px #f90;">🛰️ SPENCER KYLE\'S SCANNER</h1>', unsafe_allow_html=True)

# ===== SCANNER HEADERS =====
st.markdown("""
<div style="display:flex; flex-direction:row; font-weight:bold; color:#ffffff; padding:6px; margin-bottom:4px; text-align:center;">
    <div class="column-header" style="width:5%;">📈 UP10%</div>
    <div class="column-header" style="width:5%;">#️⃣</div>
    <div class="column-header" style="width:10%;">💠 SYMBOL</div>
    <div class="column-header" style="width:10%;">💲 PRICE</div>
    <div class="column-header" style="width:12%;">📊 VOLUME</div>
    <div class="column-header" style="width:12%;">📦 FLOAT</div>
    <div class="column-header" style="width:24%;">📰 NEWS</div>
    <div class="column-header" style="width:15%;">⭐ NEWS SCORE</div>
</div>
""", unsafe_allow_html=True)

# ===== SCANNER ROWS =====
for idx, row in df_sorted.iterrows():
    symbol_id = f"scanner-{idx}"
    stars_html = star_display(row['News Score'])
    up10 = f'<span class="pulse">📈 {row["UP10%"]}%</span>' if row['UP10%'] >= 10 else f'📈 {row["UP10%"]}%'
    bg_color = "#111122" if idx%2==0 else "#222244"
    st.markdown(f"""
    <div class="row-hover" style="display:flex; flex-direction:row; align-items:center; justify-content:center; background:{bg_color}; border-radius:12px; padding:8px; margin-bottom:5px;">
        <div style="width:5%; text-align:center; color:#00ff00;">{up10}</div>
        <div style="width:5%; text-align:center; color:#ffffff;">{idx+1}</div>
        <div style="width:10%; text-align:center; color:#00ffff; cursor:pointer;" onclick="copySymbol('{row['Symbol']}')">{row['Symbol']}</div>
        <div style="width:10%; text-align:center; color:#00ff00;">${row['Price']}</div>
        <div style="width:12%; text-align:center; color:#ffcc00;">{row['Volume']}</div>
        <div style="width:12%; text-align:center; color:#ff99ff;">{row['Float']}</div>
        <div style="width:24%; text-align:center;"><span class="ticker">{row['Headline']}</span></div>
        <div style="width:15%; text-align:center;">{stars_html}</div>
    </div>
    """, unsafe_allow_html=True)

st.caption(f"🔄 Last updated: {time.strftime('%H:%M:%S')} | Iteration: {count}")
