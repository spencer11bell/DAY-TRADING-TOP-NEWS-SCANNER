import streamlit as st
import pandas as pd
import random
import time
from streamlit_autorefresh import st_autorefresh

# ===== CONFIG =====
st.set_page_config(page_title="🔥 Day Trading Scanner - COLORFUL + GLOW", layout="wide")

PRICE_MIN = 2
PRICE_MAX = 20
FLOAT_MAX = 20_000_000
REFRESH_SECONDS = 10
DEFAULT_SYMBOLS = [
    "AAA","BBB","CCC","DDD","EEE","FFF","GGG","HHH",
    "III","JJJ","KKK","LLL","MMM","NNN","OOO","PPP",
    "QQQ","RRR","SSS","TTT"
]

# ===== FIRE EMOJI LOGIC WITH COLOR & GLOW =====
def fire_display_glow(score: int) -> str:
    if score <= 0:
        return ""
    elif score <= 2:
        return '<span style="color:yellow; text-shadow: 0 0 5px yellow;">🔥</span>'
    elif score <= 4:
        return '<span style="color:orange; text-shadow: 0 0 8px orange;">🔥</span>'
    else:
        return '<span style="color:red; text-shadow: 0 0 12px red;">🔥</span>'

# ===== AUTO REFRESH =====
count = st_autorefresh(interval=REFRESH_SECONDS*1000, limit=None, key="autorefresh")

# ===== FAKE DATA GENERATOR =====
random.seed(42)

def generate_fake_for_symbol(sym, seed):
    r = random.Random(f"{sym}-{seed}")
    price = round(r.uniform(1, 30), 2)
    prev_close = round(price / (1 + r.uniform(-0.15, 0.15)), 2)
    change_pct = round((price - prev_close) / prev_close * 100, 2) if prev_close != 0 else 0
    avg_vol = int(r.uniform(10000, 5000000))
    volume = int(avg_vol * r.uniform(1, 15))
    float_shares = int(r.uniform(500_000, 50_000_000))
    fire_score = r.randint(0, 5)
    headline_prefix = "BREAKING: " if r.random() < 0.25 else ""
    headline = f"{headline_prefix}{sym} {r.choice(['announces','reports','launches','files'])} {r.choice(['earnings','partnership','product'])}"
    sort_score = volume / avg_vol + abs(change_pct) + fire_score * 2
    return {
        "Change %": change_pct,
        "Symbol": sym,
        "🔥 News": fire_display_glow(fire_score),
        "Price": price,
        "Volume": volume,
        "Float": float_shares,
        "Headline": headline,
        "SortScore": sort_score
    }

def get_fake_stock_data(symbols, seed):
    df = pd.DataFrame([generate_fake_for_symbol(s, seed) for s in symbols])
    df_filtered = df[
        (df["Price"] >= PRICE_MIN) &
        (df["Price"] <= PRICE_MAX) &
        (df["Float"] <= FLOAT_MAX) &
        (df["Volume"] >= 1)
    ]
    if not df_filtered.empty:
        df_filtered = df_filtered.sort_values(by="SortScore", ascending=False)
    return df_filtered

# ===== MAIN DASHBOARD =====
st.title("🔥 Auto-Updating Day Trading Scanner - COLORFUL + GLOW")
st.caption(f"Auto-refresh every {REFRESH_SECONDS}s | Columns: Change %, Symbol, 🔥 News, Price, Volume, Float, Headline")

# Use container to prevent blank page
with st.container():
    df = get_fake_stock_data(DEFAULT_SYMBOLS, count)

    if df.empty:
        st.warning("No qualifying fake stocks matched filters right now.")
    else:
        # Display each stock as a horizontal, colorful box
        for idx, row in df.head(10).iterrows():
            st.markdown(
                f"""
                <div style="display:flex; flex-direction:row; align-items:center; background-color:#1f1f1f; border-radius:10px; padding:10px; margin-bottom:5px;">
                    <div style="width:8%; font-weight:bold; color:#ffffff;">{idx+1}</div>
                    <div style="width:12%; font-weight:bold; color:{'#00ff00' if row['Change %']>=0 else '#ff4d4d'};">{row['Change %']}%</div>
                    <div style="width:12%; font-weight:bold; color:#ffffff;">{row['Symbol']}</div>
                    <div style="width:12%; font-weight:bold;">{row['🔥 News']}</div>
                    <div style="width:10%; font-weight:bold; color:#00ffff;">${row['Price']}</div>
                    <div style="width:12%; font-weight:bold; color:#ffcc00;">{row['Volume']}</div>
                    <div style="width:12%; font-weight:bold; color:#ff99ff;">{row['Float']}</div>
                    <div style="width:30%; font-weight:bold; color:#ffffff;">{row['Headline']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

st.caption(f"🔄 Last updated: {time.strftime('%H:%M:%S')} | Iteration: {count}")
