import streamlit as st
import pandas as pd
import random
import time
from streamlit_autorefresh import st_autorefresh

# ===== CONFIG =====
st.set_page_config(page_title="🔥 Day Trading Scanner - COLOR-CODED CHANGE %", layout="wide")

PRICE_MIN = 2
PRICE_MAX = 20
FLOAT_MAX = 20_000_000
REFRESH_SECONDS = 10
TOP_N = 20
DEFAULT_SYMBOLS = [
    "AAA","BBB","CCC","DDD","EEE","FFF","GGG","HHH",
    "III","JJJ","KKK","LLL","MMM","NNN","OOO","PPP",
    "QQQ","RRR","SSS","TTT"
]

# ===== FIRE EMOJI LOGIC MULTI-FIRE =====
def fire_display_multi(score: int) -> str:
    """Returns multiple fire emojis depending on popularity score (1-5)"""
    if score <= 0:
        return ""
    score = min(score,5)
    color = "red" if score >=4 else "orange" if score>=2 else "yellow"
    return f'<span style="color:{color}; text-shadow: 0 0 {score*2}px {color};">{"🔥"*score}</span>'

# ===== COLOR LOGIC FOR CHANGE % =====
def change_pct_color(change):
    if change > 5:
        return "#00ff00"  # green
    elif 1 <= change <= 4:
        return "#ffff00"  # yellow
    else:
        return "#ff4d4d"  # red

# ===== AUTO REFRESH =====
count = st_autorefresh(interval=REFRESH_SECONDS*1000, limit=None, key="autorefresh")

# ===== FAKE DATA GENERATOR =====
random.seed(42)

def generate_fake_for_symbol(sym, seed):
    r = random.Random(f"{sym}-{seed}")
    price = round(r.uniform(PRICE_MIN, PRICE_MAX), 2)
    prev_close = round(price / (1 + r.uniform(-0.15, 0.15)), 2)
    change_pct = round((price - prev_close) / prev_close * 100, 2) if prev_close !=0 else 0
    avg_vol = int(r.uniform(10000, 5000000))
    volume = int(avg_vol * r.uniform(1, 15))
    float_shares = int(r.uniform(500_000, FLOAT_MAX))
    fire_score = r.randint(1,5)  # popularity 1-5
    headline_prefix = "BREAKING: " if r.random() < 0.25 else ""
    headline = f"{headline_prefix}{sym} {r.choice(['announces','reports','launches','files'])} {r.choice(['earnings','partnership','product'])}"
    return {
        "Change %": change_pct,
        "Symbol": sym,
        "🔥 News": fire_display_multi(fire_score),
        "Price": price,
        "Volume": volume,
        "Float": float_shares,
        "Headline": headline
    }

def get_fake_stock_data(symbols, seed):
    # Generate data for all symbols (top 20 fixed)
    df = pd.DataFrame([generate_fake_for_symbol(s, seed) for s in symbols[:TOP_N]])
    return df

# ===== MAIN DASHBOARD =====
st.title("🔥 Fixed Top 20 Day Trading Scanner - COLOR-CODED CHANGE %")
st.caption(f"Auto-refresh every {REFRESH_SECONDS}s | Columns: Change %, Symbol, 🔥 News, Price, Volume, Float, Headline")

# Container for list to prevent blank page
with st.container():
    df = get_fake_stock_data(DEFAULT_SYMBOLS, count)

    # Sort by Change % descending to update ranking dynamically
    df_sorted = df.sort_values(by="Change %", ascending=False).reset_index(drop=True)

    # Column headers
    st.markdown(
        """
        <div style="display:flex; flex-direction:row; align-items:center; background-color:#2f2f2f; border-radius:10px; padding:8px; margin-bottom:2px;">
            <div style="width:5%; font-weight:bold; color:#ffffff;">#</div>
            <div style="width:12%; font-weight:bold; color:#00ffff;">Change %</div>
            <div style="width:10%; font-weight:bold; color:#ffffff;">Symbol</div>
            <div style="width:15%; font-weight:bold; color:#ff9900;">🔥 News</div>
            <div style="width:10%; font-weight:bold; color:#00ffff;">Price</div>
            <div style="width:12%; font-weight:bold; color:#ffcc00;">Volume</div>
            <div style="width:12%; font-weight:bold; color:#ff99ff;">Float</div>
            <div style="width:24%; font-weight:bold; color:#ffffff;">Headline</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Display each stock (top 20 fixed)
    for idx, row in df_sorted.iterrows():
        color = change_pct_color(row['Change %'])
        st.markdown(
            f"""
            <div style="display:flex; flex-direction:row; align-items:center; background-color:#1f1f1f; border-radius:10px; padding:8px; margin-bottom:3px;">
                <div style="width:5%; font-weight:bold; color:#ffffff;">{idx+1}</div>
                <div style="width:12%; font-weight:bold; color:{color};">{row['Change %']}%</div>
                <div style="width:10%; font-weight:bold; color:#ffffff;">{row['Symbol']}</div>
                <div style="width:15%; font-weight:bold;">{row['🔥 News']}</div>
                <div style="width:10%; font-weight:bold; color:#00ffff;">${row['Price']}</div>
                <div style="width:12%; font-weight:bold; color:#ffcc00;">{row['Volume']}</div>
                <div style="width:12%; font-weight:bold; color:#ff99ff;">{row['Float']}</div>
                <div style="width:24%; font-weight:bold; color:#ffffff;">{row['Headline']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.caption(f"🔄 Last updated: {time.strftime('%H:%M:%S')} | Iteration: {count}")
