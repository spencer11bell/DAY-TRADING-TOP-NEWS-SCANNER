import streamlit as st
import pandas as pd
import random
import time
from streamlit_autorefresh import st_autorefresh

# ===== CONFIG =====
st.set_page_config(page_title="🔥 Auto Day Trading Scanner - FAKE DATA", layout="wide")

PRICE_MIN = 2
PRICE_MAX = 20
FLOAT_MAX = 20_000_000  # 20 million
VOLUME_MULTIPLIER = 5
REFRESH_SECONDS = 10  # refresh interval in seconds

DEFAULT_SYMBOLS = [
    "AAA","BBB","CCC","DDD","EEE","FFF","GGG","HHH",
    "III","JJJ","KKK","LLL","MMM","NNN","OOO","PPP",
    "QQQ","RRR","SSS","TTT"
]

# ===== FIRE EMOJI LOGIC =====
def fire_display_colored(score: int) -> str:
    if score <= 0:
        return ""
    elif score == 1:
        return "🟡🔥"
    elif score == 2:
        return "🟠🔥🔥"
    elif score == 3:
        return "🔴🔥🔥🔥"
    elif score == 4:
        return "🔴🔥🔥🔥🔥"
    else:
        return "❤️‍🔥🔥🔥🔥🔥"

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
    volume = int(avg_vol * r.uniform(1, 15))  # ensures some rows always pass
    float_shares = int(r.uniform(500_000, 50_000_000))
    fire_score = r.randint(0, 5)
    headline_prefix = "BREAKING: " if r.random() < 0.25 else ""
    headline = f"{headline_prefix}{sym} {r.choice(['announces','reports','launches','files'])} {r.choice(['earnings','partnership','product'])}"
    sort_score = volume / avg_vol + abs(change_pct) + fire_score * 2
    return {
        "Change %": change_pct,
        "Symbol": sym,
        "🔥 News": fire_display_colored(fire_score),
        "Price": price,
        "Volume": volume,
        "Float": float_shares,
        "Headline": headline,
        "SortScore": sort_score,
        "AvgVol": avg_vol
    }

def get_fake_stock_data(symbols, seed):
    df = pd.DataFrame([generate_fake_for_symbol(s, seed) for s in symbols])
    # SAFEGUARD: loosen filters so at least some rows always pass
    df_filtered = df[
        (df["Price"] >= 1) &
        (df["Price"] <= 30) &
        (df["Float"] <= 50_000_000) &
        (df["Volume"] >= 1)
    ]
    if not df_filtered.empty:
        df_filtered = df_filtered.sort_values(by="SortScore", ascending=False)
    return df_filtered

# ===== MAIN DASHBOARD =====
st.title("🔥 Auto-Updating Day Trading Scanner - FAKE DATA TEST")
st.success("TEST MODE: Using synthetic data. Replace with real feeds for production.")
st.caption(f"Auto-refresh every {REFRESH_SECONDS}s | Columns: Change %, Symbol, 🔥 News, Price, Volume, Float, Headline")

# DEBUG: show sample data
st.write("DEBUG: Sample fake data (first 5 rows)")
df_debug = get_fake_stock_data(DEFAULT_SYMBOLS, count)
st.write(df_debug.head(5))

placeholder = st.empty()
df = get_fake_stock_data(DEFAULT_SYMBOLS, count)

if df.empty:
    st.warning("No qualifying fake stocks matched filters right now.")
else:
    # --- Top 10 Movers ---
    st.subheader("🏆 Top 10 Movers")
    top10 = df.head(10).copy()
    top10.insert(0, "#", range(1, len(top10) + 1))
    st.dataframe(
        top10[["#", "Change %", "Symbol", "🔥 News", "Price", "Volume", "Float", "Headline"]],
        use_container_width=True,
        hide_index=True
    )

    st.divider()
    st.subheader("📊 Full Scanner Results")
    st.dataframe(
        df[["Change %", "Symbol", "🔥 News", "Price", "Volume", "Float", "Headline"]],
        use_container_width=True,
        hide_index=True
    )

st.caption(f"🔄 Last updated: {time.strftime('%H:%M:%S')} | Iteration: {count}")
