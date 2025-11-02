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
    """Gradually scale stars from 1-5 but keep centered and row height fixed"""
    score = min(max(score, 0), 5)
    sizes = [16, 18, 20, 22, 24]  # Gradual increase
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
function copySymbol(symbol, id){
    navigator.clipboard.writeText(symbol);
    let indicator = document.getElementById(id);
    indicator.style.display='inline';
    setTimeout(()=>{indicator.style.display='none';}, 1000);
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
        # default chime
        st.markdown("""
        <audio autoplay>
            <source src="https://actions.google.com/sounds/v1/cash/coin_tap.ogg" type="audio/ogg">
        </audio>
        """, unsafe_allow_html=True)

# ===== CHIME TOGGLE =====
if 'alerts_enabled' not in st.session_state:
    st.session_state.alerts_enabled = False
if st.sidebar.button("🔔 Toggle Watchlist Chimes"):
    st.session_state.alerts_enabled = not st.session_state.alerts_enabled

# ===== MAIN DASHBOARD =====
st.title("Spencer Kyle's Scanner")
st.caption(f"Auto-refresh every {REFRESH_SECONDS}s")

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

# ===== PLAY CHIME IF NEW STOCK ENTERS WATCHLIST =====
if 'prev_watchlist_symbols' not in st.session_state:
    st.session_state.prev_watchlist_symbols = []

current_symbols = watchlist_df['Symbol'].tolist()
if st.session_state.alerts_enabled:
    for sym in current_symbols:
        if sym not in st.session_state.prev_watchlist_symbols:
            play_chime()
            break
st.session_state.prev_watchlist_symbols = current_symbols

# ===== WATCHLIST DISPLAY =====
st.markdown('<div style="background-color:#111122; padding:12px; border-radius:12px; box-shadow:0 0 15px #00ffff;">', unsafe_allow_html=True)
st.markdown('<h3 style="color:#00ffff; text-shadow: 2px 2px 5px #000;">📋 WATCHLIST</h3>', unsafe_allow_html=True)

st.markdown("""
<div style="display:flex; flex-direction:row; font-weight:bold; color:#ffffff; padding:6px; margin-bottom:4px; border-bottom:2px solid #00ffff; text-align:center;">
    <div style="width:5%;">📈 UP10%</div>
    <div style="width:5%;">#️⃣</div>
    <div style="width:10%;">💠 SYMBOL</div>
    <div style="width:10%;">💲 PRICE</div>
    <div style="width:12%;">📊 VOLUME</div>
    <div style="width:12%;">📦 FLOAT</div>
    <div style="width:24%;">📰 HEADLINE</div>
    <div style="width:15%;">⭐ NEWS</div>
</div>
""", unsafe_allow_html=True)

for idx, row in watchlist_df.iterrows():
    symbol_id = f"watchlist-{idx}"
    stars_html = star_display(row['News Score'])
    up10 = f"📈 {row['UP10%']}%"
    st.markdown(f"""
    <div class="row-hover" style="display:flex; flex-direction:row; align-items:center; justify-content:center; background-color:#222244; border-radius:8px; padding:8px; margin-bottom:5px; box-shadow: 2px 2px 8px #000;">
        <div style="width:5%; text-align:center; color:#00ff00;">{up10}</div>
        <div style="width:5%; text-align:center; color:#ffffff;">{idx+1}</div>
        <div style="width:10%; text-align:center; color:#00ffff; cursor:pointer;" onclick="copySymbol('{row['Symbol']}', '{symbol_id}')">{row['Symbol']}<span id='{symbol_id}' style='color:#00ff00; display:none;'>COPIED</span></div>
        <div style="width:10%; text-align:center; color:#00ff00;">${row['Price']}</div>
        <div style="width:12%; text-align:center; color:#ffcc00;">{row['Volume']}</div>
        <div style="width:12%; text-align:center; color:#ff99ff;">{row['Float']}</div>
        <div style="width:24%; text-align:center; color:#ffffff;">{row['Headline']}</div>
        <div style="width:15%; text-align:center;">{stars_html}</div>
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ===== DIVIDER =====
st.markdown("<hr style='border:2px solid #00ffff; margin:20px 0;'>", unsafe_allow_html=True)

# ===== SCANNER =====
st.markdown('<h3 style="color:#ff9900; text-shadow: 2px 2px 5px #000;">SPENCER KYLE\'S SCANNER</h3>', unsafe_allow_html=True)

st.markdown("""
<div style="display:flex; flex-direction:row; font-weight:bold; color:#ffffff; padding:6px; margin-bottom:4px; border-bottom:2px solid #ff9900; text-align:center;">
    <div style="width:5%;">📈 UP10%</div>
    <div style="width:5%;">#️⃣</div>
    <div style="width:10%;">💠 SYMBOL</div>
    <div style="width:10%;">💲 PRICE</div>
    <div style="width:12%;">📊 VOLUME</div>
    <div style="width:12%;">📦 FLOAT</div>
    <div style="width:24%;">📰 HEADLINE</div>
    <div style="width:15%;">⭐ NEWS</div>
</div>
""", unsafe_allow_html=True)

for idx, row in df_sorted.iterrows():
    symbol_id = f"scanner-{idx}"
    stars_html = star_display(row['News Score'])
    up10 = f"📈 {row['UP10%']}%" if row['UP10%'] >= 10 else ""
    bg_color = "#222222" if idx % 2 == 0 else "#111111"
    st.markdown(f"""
    <div class="row-hover" style="display:flex; flex-direction:row; align-items:center; justify-content:center; background-color:{bg_color}; border-radius:8px; padding:8px; margin-bottom:5px; box-shadow: 1px 1px 6px #000;">
        <div style="width:5%; text-align:center; color:#00ff00;">{up10}</div>
        <div style="width:5%; text-align:center; color:#ffffff;">{idx+1}</div>
        <div style="width:10%; text-align:center; color:#00ffff; cursor:pointer;" onclick="copySymbol('{row['Symbol']}', '{symbol_id}')">{row['Symbol']}<span id='{symbol_id}' style='color:#00ff00; display:none;'>COPIED</span></div>
        <div style="width:10%; text-align:center; color:#00ff00;">${row['Price']}</div>
        <div style="width:12%; text-align:center; color:#ffcc00;">{row['Volume']}</div>
        <div style="width:12%; text-align:center; color:#ff99ff;">{row['Float']}</div>
        <div style="width:24%; text-align:center; color:#ffffff;">{row['Headline']}</div>
        <div style="width:15%; text-align:center;">{stars_html}</div>
    </div>
    """, unsafe_allow_html=True)

st.caption(f"🔄 Last updated: {time.strftime('%H:%M:%S')} | Iteration: {count}")

# ===== ROW HOVER EFFECT =====
st.markdown("""
<style>
.row-hover:hover {
    background: linear-gradient(90deg, #3333ff55, #ff33ff55);
    transform: scale(1.01);
    transition: all 0.2s ease-in-out;
}
</style>
""", unsafe_allow_html=True)
