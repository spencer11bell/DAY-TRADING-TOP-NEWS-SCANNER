import streamlit as st
import pandas as pd
import random
import time
from streamlit_autorefresh import st_autorefresh

# ===== CONFIG =====
st.set_page_config(page_title="Day Trading Scanner - Watchlist UP10%", layout="wide")

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

# ===== STAR DISPLAY LOGIC =====
def star_display(score: int) -> str:
    score = min(max(score, 0), 5)
    return f'<span style="font-size:20px; color:#FFD700;">{"⭐" * score}</span>'

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

# ===== CHIME FUNCTION =====
def play_chime_html():
    st.markdown("""
    <audio autoplay>
        <source src="https://actions.google.com/sounds/v1/cash/coin_tap.ogg" type="audio/ogg">
    </audio>
    """, unsafe_allow_html=True)

# ===== COPY-TO-CLIPBOARD JS =====
st.markdown("""
<script>
function copySymbol(symbol, id){
    navigator.clipboard.writeText(symbol);
    let indicator = document.getElementById(id);
    indicator.style.display='inline';
    setTimeout(()=>{indicator.style.display='none';}, 1000);
}
</script>
""", unsafe_allow_html=True)

# ===== MAIN DASHBOARD =====
st.title("Day Trading Scanner")
st.caption(f"Auto-refresh every {REFRESH_SECONDS}s")

# Toggle for chime alerts
if 'alerts_enabled' not in st.session_state:
    st.session_state.alerts_enabled = False
if st.button("🔔 Enable Watchlist Chimes"):
    st.session_state.alerts_enabled = True

# Generate Data
df = get_fake_stock_data(DEFAULT_SYMBOLS, count)
df_sorted = df.sort_values(by="UP10%", ascending=False).reset_index(drop=True)

# ===== WATCHLIST LOGIC =====
watchlist_df = df[
    (df['UP10%'] >= 10) &
    (df['Price'].between(PRICE_MIN, PRICE_MAX)) &
    (df['Volume'] >= 5*df['AvgVol']) &
    (df['Float'] < FLOAT_MAX)
].sort_values(by="UP10%", ascending=False).head(WATCHLIST_TOP_N)

# Play chime if new stock enters watchlist
if 'prev_watchlist_symbols' not in st.session_state:
    st.session_state.prev_watchlist_symbols = []
current_symbols = watchlist_df['Symbol'].tolist()
if st.session_state.alerts_enabled:
    for sym in current_symbols:
        if sym not in st.session_state.prev_watchlist_symbols:
            play_chime_html()
            break
st.session_state.prev_watchlist_symbols = current_symbols

# ===== WATCHLIST DISPLAY =====
st.markdown('<div style="background-color:#2a2a3a; padding:12px; border-radius:12px; margin-bottom:20px;">', unsafe_allow_html=True)
st.markdown('<h4 style="color:#00ffff;">📋 Watchlist - Strict UP10% Rules</h4>', unsafe_allow_html=True)

# Column description above Watchlist
st.markdown("""
<div style="display:flex; flex-direction:row; font-weight:bold; color:#ffffff; padding:6px; margin-bottom:4px; border-bottom:1px solid #00ffff; position:sticky; top:0; background-color:#2a2a3a; z-index:1;">
    <div style="width:5%;">UP10%</div>
    <div style="width:5%;">#</div>
    <div style="width:10%;">SYMBOL</div>
    <div style="width:10%;">PRICE</div>
    <div style="width:12%;">VOLUME</div>
    <div style="width:12%;">FLOAT</div>
    <div style="width:24%;">HEADLINE</div>
    <div style="width:15%;">NEWS</div>
</div>
""", unsafe_allow_html=True)

# Watchlist rows
for idx, row in watchlist_df.iterrows():
    up10 = f"🔺 {row['UP10%']}%"
    symbol_id = f"watchlist-{idx}"
    stars_html = star_display(row['News Score'])
    st.markdown(f"""
    <div style="display:flex; flex-direction:row; align-items:center; background-color:#3a3a5a; border-radius:6px; padding:6px; margin-bottom:4px;">
        <div style="width:5%; font-weight:bold; color:#00ff00;">{up10}</div>
        <div style="width:5%; font-weight:bold; color:#ffffff;">{idx+1}</div>
        <div style="width:10%; font-weight:bold; color:#00ffff; cursor:pointer;" onclick="copySymbol('{row['Symbol']}', '{symbol_id}')">{row['Symbol']} <span id='{symbol_id}' style='color:#00ff00; font-weight:bold; display:none;'>COPIED</span></div>
        <div style="width:10%; font-weight:bold; color:#00ff00;">${row['Price']}</div>
        <div style="width:12%; font-weight:bold; color:#ffcc00;">{row['Volume']}</div>
        <div style="width:12%; font-weight:bold; color:#ff99ff;">{row['Float']}</div>
        <div style="width:24%; font-weight:bold; color:#ffffff;">{row['Headline']}</div>
        <div style="width:15%; font-weight:bold;">{stars_html}</div>
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ===== DIVIDER BETWEEN WATCHLIST AND SCANNER =====
st.markdown("<hr style='border:2px solid #00ffff; margin:20px 0;'>", unsafe_allow_html=True)

# ===== MAIN SCANNER TABLE =====
st.markdown('<h4 style="color:#ff9900;">📊 Scanner - Top 20 Stocks</h4>', unsafe_allow_html=True)

# Column description above Scanner
st.markdown("""
<div style="display:flex; flex-direction:row; font-weight:bold; color:#ffffff; padding:6px; margin-bottom:4px; border-bottom:1px solid #ff9900; position:sticky; top:0; background-color:#1f1f1f; z-index:1;">
    <div style="width:5%;">UP10%</div>
    <div style="width:5%;">#</div>
    <div style="width:10%;">SYMBOL</div>
    <div style="width:10%;">PRICE</div>
    <div style="width:12%;">VOLUME</div>
    <div style="width:12%;">FLOAT</div>
    <div style="width:24%;">HEADLINE</div>
    <div style="width:15%;">NEWS</div>
</div>
""", unsafe_allow_html=True)

# Scanner rows
for idx, row in df_sorted.iterrows():
    up10 = f"🔺 {row['UP10%']}%" if row['UP10%'] >= 10 else ""
    symbol_id = f"scanner-{idx}"
    stars_html = star_display(row['News Score'])
    bg_color = "#2a2a2a" if idx % 2 == 0 else "#1f1f1f"
    st.markdown(f"""
    <div style="display:flex; flex-direction:row; align-items:center; background-color:{bg_color}; border-radius:6px; padding:6px; margin-bottom:4px;">
        <div style="width:5%; font-weight:bold; color:#00ff00;">{up10}</div>
        <div style="width:5%; font-weight:bold; color:#ffffff;">{idx+1}</div>
        <div style="width:10%; font-weight:bold; color:#00ffff; cursor:pointer;" onclick="copySymbol('{row['Symbol']}', '{symbol_id}')">{row['Symbol']} <span id='{symbol_id}' style='color:#00ff00; font-weight:bold; display:none;'>COPIED</span></div>
        <div style="width:10%; font-weight:bold; color:#00ff00;">${row['Price']}</div>
        <div style="width:12%; font-weight:bold; color:#ffcc00;">{row['Volume']}</div>
        <div style="width:12%; font-weight:bold; color:#ff99ff;">{row['Float']}</div>
        <div style="width:24%; font-weight:bold; color:#ffffff;">{row['Headline']}</div>
        <div style="width:15%; font-weight:bold;">{stars_html}</div>
    </div>
    """, unsafe_allow_html=True)

st.caption(f"🔄 Last updated: {time.strftime('%H:%M:%S')} | Iteration: {count}")
