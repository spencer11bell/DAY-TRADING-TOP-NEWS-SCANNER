import streamlit as st
import pandas as pd
import random
import time
from streamlit_autorefresh import st_autorefresh
import base64

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

# ===== EMBED YOUR PNG BASE64 =====
DIAMOND_BASE64 = "<PASTE-YOUR-UPLOADED-PNG-BASE64-HERE>"

# ===== OPTIONAL UPLOAD PNG (Overrides default) =====
uploaded_file = st.sidebar.file_uploader("Upload PNG to replace default", type=["png"])
if uploaded_file:
    DIAMOND_BASE64 = base64.b64encode(uploaded_file.read()).decode()

# ===== IMAGE LOGIC =====
def diamond_display_image(score: int) -> str:
    if not DIAMOND_BASE64 or score <= 0:
        return ""
    score = min(score, 5)
    size_map = {1: 20, 2: 28, 3: 36, 4: 44, 5: 56}
    size = size_map[score]
    return f'<img src="data:image/png;base64,{DIAMOND_BASE64}" width="{size}" style="margin-right:2px;">' * score

# ===== COLOR LOGIC =====
def change_pct_color(change):
    if change > 5:
        return "#00ff00"
    elif 1 <= change <= 4:
        return "#ffff00"
    else:
        return "#ff4d4d"

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
    diamond_score = r.randint(1,5)
    headline_prefix = "BREAKING: " if r.random()<0.25 else ""
    headline = f"{headline_prefix}{sym} {r.choice(['announces','reports','launches','files'])} {r.choice(['earnings','partnership','product'])}"
    return {
        "Change %": change_pct,
        "Symbol": sym,
        "Price": price,
        "Volume": volume,
        "AvgVol": avg_vol,
        "Float": float_shares,
        "Headline": headline,
        "💎 News Score": diamond_score
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
st.title("Day Trading Scanner - Watchlist UP10%")
st.caption(f"Auto-refresh every {REFRESH_SECONDS}s")

# Toggle for chime alerts
if 'alerts_enabled' not in st.session_state:
    st.session_state.alerts_enabled = False
if st.button("🔔 Enable Watchlist Chimes"):
    st.session_state.alerts_enabled = True

# Generate Data
df = get_fake_stock_data(DEFAULT_SYMBOLS, count)
df_sorted = df.sort_values(by="Change %", ascending=False).reset_index(drop=True)

# ===== WATCHLIST LOGIC =====
if 'prev_watchlist_symbols' not in st.session_state:
    st.session_state.prev_watchlist_symbols = []

watchlist_df = df[
    (df['Change %']>=10) &
    (df['Price'].between(PRICE_MIN,PRICE_MAX)) &
    (df['💎 News Score']>=4) &
    (df['Volume'] >= 5*df['AvgVol']) &
    (df['Float']<FLOAT_MAX)
].sort_values(by="💎 News Score", ascending=False).head(WATCHLIST_TOP_N)

# Play chime if new stock enters watchlist
current_symbols = watchlist_df['Symbol'].tolist()
if st.session_state.alerts_enabled:
    for sym in current_symbols:
        if sym not in st.session_state.prev_watchlist_symbols:
            play_chime_html()
            break
st.session_state.prev_watchlist_symbols = current_symbols

# ===== WATCHLIST DISPLAY =====
st.markdown('<div style="background-color:#1a1a1a; padding:12px; border-radius:12px; margin-bottom:12px;">', unsafe_allow_html=True)
st.markdown('<h4 style="color:#00ffff;">📋 Watchlist - Top 5 UP10% Stocks</h4>', unsafe_allow_html=True)

# Column headers
st.markdown("""
<div style="display:flex; flex-direction:row; font-weight:bold; color:#ffffff; padding:4px; margin-bottom:2px;">
    <div style="width:5%;">UP10%</div>
    <div style="width:5%;">#</div>
    <div style="width:12%;">Change %</div>
    <div style="width:10%;">Symbol</div>
    <div style="width:10%;">Price</div>
    <div style="width:12%;">Volume</div>
    <div style="width:12%;">Float</div>
    <div style="width:24%;">Headline</div>
    <div style="width:15%;">News</div>
</div>
""", unsafe_allow_html=True)

# Display rows
for idx, row in watchlist_df.iterrows():
    color = change_pct_color(row['Change %'])
    diamond_html = diamond_display_image(row['💎 News Score'])
    up10 = f"🔺 {row['Change %']}%" if row['Change %']>=10 else ""
    symbol_id = f"symbol-{idx}"
    st.markdown(f"""
    <div style="display:flex; flex-direction:row; align-items:center; background-color:#2a2a2a; border-radius:8px; padding:6px; margin-bottom:3px;">
        <div style="width:5%; font-weight:bold; color:#00ff00;">{up10}</div>
        <div style="width:5%; font-weight:bold; color:#ffffff;">{idx+1}</div>
        <div style="width:12%; font-weight:bold; color:{color};">{row['Change %']}%</div>
        <div style="width:10%; font-weight:bold; color:#00ffff; cursor:pointer;" onclick="copySymbol('{row['Symbol']}', '{symbol_id}')">{row['Symbol']} <span id='{symbol_id}' style='color:#00ff00; font-weight:bold; display:none;'>COPIED</span></div>
        <div style="width:10%; font-weight:bold; color:#00ff00;">${row['Price']}</div>
        <div style="width:12%; font-weight:bold; color:#ffcc00;">{row['Volume']}</div>
        <div style="width:12%; font-weight:bold; color:#ff99ff;">{row['Float']}</div>
        <div style="width:24%; font-weight:bold; color:#ffffff;">{row['Headline']}</div>
        <div style="width:15%; font-weight:bold;">{diamond_html}</div>
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ===== MAIN TABLE =====
st.markdown("""
<div style="display:flex; flex-direction:row; align-items:center; background-color:#2f2f2f; border-radius:10px; padding:8px; margin-bottom:2px;">
    <div style="width:5%; font-weight:bold; color:#ffffff;">UP 10%</div>
    <div style="width:5%; font-weight:bold; color:#ffffff;">#</div>
    <div style="width:12%; font-weight:bold; color:#00ffff;">Change %</div>
    <div style="width:10%; font-weight:bold; color:#ffffff;">Symbol</div>
    <div style="width:10%; font-weight:bold; color:#00ffff;">Price</div>
    <div style="width:12%; font-weight:bold; color:#ffcc00;">Volume</div>
    <div style="width:12%; font-weight:bold; color:#ff99ff;">Float</div>
    <div style="width:24%; font-weight:bold; color:#ffffff;">Headline</div>
    <div style="width:15%; font-weight:bold; color:#ff33ff;">News</div>
</div>
""", unsafe_allow_html=True)

# Display top 20 main table
for idx, row in df_sorted.iterrows():
    color = change_pct_color(row['Change %'])
    bg_color = "#2a2a2a" if idx % 2 == 0 else "#1f1f1f"
    diamond_html = diamond_display_image(row['💎 News Score'])
    up10 = f"🔺 {row['Change %']}%" if row['Change %'] >= 10 else ""
    symbol_id = f"symbol-main-{idx}"
    st.markdown(f"""
    <div style="display:flex; flex-direction:row; align-items:center; background-color:{bg_color}; border-radius:10px; padding:8px; margin-bottom:3px;">
        <div style="width:5%; font-weight:bold; color:#00ff00;">{up10}</div>
        <div style="width:5%; font-weight:bold; color:#ffffff;">{idx+1}</div>
        <div style="width:12%; font-weight:bold; color:{color};">{row['Change %']}%</div>
        <div style="width:10%; font-weight:bold; color:#00ffff; cursor:pointer;" onclick="copySymbol('{row['Symbol']}', '{symbol_id}')">{row['Symbol']} <span id='{symbol_id}' style='color:#00ff00; font-weight:bold; display:none;'>COPIED</span></div>
        <div style="width:10%; font-weight:bold; color:#00ff00;">${row['Price']}</div>
        <div style="width:12%; font-weight:bold; color:#ffcc00;">{row['Volume']}</div>
        <div style="width:12%; font-weight:bold; color:#ff99ff;">{row['Float']}</div>
        <div style="width:24%; font-weight:bold; color:#ffffff;">{row['Headline']}</div>
        <div style="width:15%; font-weight:bold;">{diamond_html}</div>
    </div>
    """, unsafe_allow_html=True)

st.caption(f"🔄 Last updated: {time.strftime('%H:%M:%S')} | Iteration: {count}")
