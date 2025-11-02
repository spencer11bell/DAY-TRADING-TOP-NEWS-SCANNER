import streamlit as st
import pandas as pd
import random
import time
from streamlit_autorefresh import st_autorefresh

# ===== CONFIG =====
st.set_page_config(page_title="🔥 Day Trading Scanner - Watchlist + UP10%", layout="wide")

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

# ===== FIRE EMOJI LOGIC =====
def fire_display_multi(score: int, is_top_mover=False) -> str:
    if score <= 0:
        return ""
    score = min(score,5)
    color = "red" if score >=4 else "orange" if score>=2 else "yellow"
    if is_top_mover:
        return f'''
        <span style="
            color:{color};
            text-shadow: 0 0 {score*5}px {color},0 0 {score*10}px {color};
            font-size:28px;
            font-weight:bold;">
            {'🔥'*score}
        </span>
        '''
    else:
        if score == 5:
            animation = "big-bounce"
        elif score == 4:
            animation = "small-bounce"
        else:
            animation = "pulse"
        return f'''
        <span class="{animation}" style="
            color:{color};
            text-shadow:0 0 {score*2}px {color};
            font-size:18px;">
            {'🔥'*score}
        </span>
        '''

# ===== CSS Animations =====
st.markdown("""
<style>
@keyframes pulse {0% {transform: scale(1);}50% {transform: scale(1.2);}100% {transform: scale(1);}}
@keyframes small-bounce {0%,100%{transform: translateY(0);}50%{transform: translateY(-5px);}}
@keyframes big-bounce {0%,100%{transform: translateY(0);}50%{transform: translateY(-15px);}}
.pulse {animation: pulse 1.2s infinite alternate;}
.small-bounce {animation: small-bounce 0.8s infinite;}
.big-bounce {animation: big-bounce 0.6s infinite;}
</style>
""", unsafe_allow_html=True)

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
    fire_score = r.randint(1,5)
    headline_prefix = "BREAKING: " if r.random()<0.25 else ""
    headline = f"{headline_prefix}{sym} {r.choice(['announces','reports','launches','files'])} {r.choice(['earnings','partnership','product'])}"
    return {
        "Change %": change_pct,
        "Symbol": sym,
        "🔥 News Score": fire_score,
        "Price": price,
        "Volume": volume,
        "AvgVol": avg_vol,
        "Float": float_shares,
        "Headline": headline
    }

def get_fake_stock_data(symbols, seed):
    df = pd.DataFrame([generate_fake_for_symbol(s, seed) for s in symbols[:TOP_N]])
    return df

# ===== MAIN DASHBOARD =====
st.title("🔥 Day Trading Scanner - Watchlist + UP 10%")
st.caption(f"Auto-refresh every {REFRESH_SECONDS}s")

# Generate Data
df = get_fake_stock_data(DEFAULT_SYMBOLS, count)
df_sorted = df.sort_values(by="Change %", ascending=False).reset_index(drop=True)

# ===== WATCHLIST BOX =====
watchlist_df = df[
    (df['Price'].between(PRICE_MIN,PRICE_MAX)) &
    (df['🔥 News Score']>=4) &
    (df['Volume'] >= 5*df['AvgVol']) &
    (df['Float']<FLOAT_MAX)
].sort_values(by="🔥 News Score", ascending=False).head(WATCHLIST_TOP_N)

st.markdown('<div style="background-color:#111111; padding:12px; border-radius:12px; margin-bottom:12px;">', unsafe_allow_html=True)
st.markdown('<h4 style="color:#00ffff;">📋 Watchlist - Top 5 Stocks Meeting Criteria</h4>', unsafe_allow_html=True)
for idx, row in watchlist_df.iterrows():
    fire_html = fire_display_multi(row['🔥 News Score'])
    st.markdown(f'''
    <div style="display:flex; flex-direction:row; justify-content:space-between; color:#ffffff; padding:4px;">
        <div style="width:15%; font-weight:bold;">{row['Symbol']}</div>
        <div style="width:15%;">${row['Price']}</div>
        <div style="width:50%;">{row['Headline']}</div>
        <div style="width:20%;">{fire_html}</div>
    </div>
    ''', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ===== COLUMN HEADERS =====
st.markdown("""
<div style="display:flex; flex-direction:row; align-items:center; background-color:#2f2f2f; border-radius:10px; padding:8px; margin-bottom:2px;">
    <div style="width:5%; font-weight:bold; color:#ffffff;">UP 10%</div>
    <div style="width:5%; font-weight:bold; color:#ffffff;">#</div>
    <div style="width:12%; font-weight:bold; color:#00ffff;">Change %</div>
    <div style="width:10%; font-weight:bold; color:#ffffff;">Symbol</div>
    <div style="width:15%; font-weight:bold; color:#ff9900;">🔥 News</div>
    <div style="width:10%; font-weight:bold; color:#00ffff;">Price</div>
    <div style="width:12%; font-weight:bold; color:#ffcc00;">Volume</div>
    <div style="width:12%; font-weight:bold; color:#ff99ff;">Float</div>
    <div style="width:24%; font-weight:bold; color:#ffffff;">Headline</div>
</div>
""", unsafe_allow_html=True)

# ===== DISPLAY TOP 20 =====
for idx, row in df_sorted.iterrows():
    color = change_pct_color(row['Change %'])
    bg_color = "#2a2a2a" if idx%2==0 else "#1f1f1f"
    is_top_mover = idx<3
    fire_html = fire_display_multi(row['🔥 News Score'], is_top_mover)
    up10 = "🔺" if row['Change %']>=10 else ""
    st.markdown(f"""
    <div style="display:flex; flex-direction:row; align-items:center; background-color:{bg_color}; border-radius:10px; padding:8px; margin-bottom:3px;">
        <div style="width:5%; font-weight:bold; color:#00ff00;">{up10}</div>
        <div style="width:5%; font-weight:bold; color:#ffffff;">{idx+1}</div>
        <div style="width:12%; font-weight:bold; color:{color};">{row['Change %']}%</div>
        <div style="width:10%; font-weight:bold; color:#ffffff;">{row['Symbol']}</div>
        <div style="width:15%; font-weight:bold;">{fire_html}</div>
        <div style="width:10%; font-weight:bold; color:#00ffff;">${row['Price']}</div>
        <div style="width:12%; font-weight:bold; color:#ffcc00;">{row['Volume']}</div>
        <div style="width:12%; font-weight:bold; color:#ff99ff;">{row['Float']}</div>
        <div style="width:24%; font-weight:bold; color:#ffffff;">{row['Headline']}</div>
    </div>
    """, unsafe_allow_html=True)

st.caption(f"🔄 Last updated: {time.strftime('%H:%M:%S')} | Iteration: {count}")
