import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import time

st.set_page_config(page_title="🔥 Auto Day Trading Scanner", layout="wide")

# ===== CONFIG =====
PRICE_MIN = 2
PRICE_MAX = 20
FLOAT_MAX = 20_000_000  # 20 million
VOLUME_MULTIPLIER = 5
REFRESH_SECONDS = 20  # how often to refresh
DEFAULT_SYMBOLS = [
    "TSLA", "AAPL", "NVDA", "AMD", "PLTR", "SOFI", "MARA", "RIOT",
    "BABA", "TQQQ", "AMZN", "META", "NFLX", "LCID", "NIO", "COIN",
    "AI", "UPST", "GME", "HOOD"
]

# ===== FIRE EMOJI COLOR LOGIC =====
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

# ===== GET NEWS =====
def get_news_headline(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v1/finance/search?q={symbol}"
        res = requests.get(url).json()
        news_items = [i["title"] for i in res.get("news", []) if "title" in i]
        return news_items[0] if news_items else "—"
    except Exception:
        return "—"

# ===== GET STOCK DATA =====
def get_stock_data(symbols):
    data = []
    for sym in symbols:
        try:
            info = yf.Ticker(sym).info
            price = info.get("regularMarketPrice")
            prev_close = info.get("previousClose")
            if not price or not prev_close:
                continue
            change_pct = ((price - prev_close) / prev_close) * 100
            volume = info.get("volume", 0)
            avg_vol = info.get("averageVolume", 1)
            float_shares = info.get("floatShares", 0)
            vol_ratio = volume / avg_vol if avg_vol else 0

            if (
                PRICE_MIN <= price <= PRICE_MAX
                and float_shares <= FLOAT_MAX
                and vol_ratio >= VOLUME_MULTIPLIER
            ):
                data.append({
                    "Symbol": sym,
                    "Price": round(price, 2),
                    "Change %": round(change_pct, 2),
                    "Volume": volume,
                    "Float": float_shares,
                    "🔥 Score": fire_display_colored(int(min(vol_ratio // 2, 5))),
                    "Headline": get_news_headline(sym),
                    "SortScore": vol_ratio + abs(change_pct)
                })
        except Exception:
            continue

    df = pd.DataFrame(data)
    if not df.empty:
        df = df.sort_values(by="SortScore", ascending=False)
    return df

# ===== MAIN DASHBOARD =====
st.title("🔥 Auto-Updating Day Trading Scanner")
st.caption(f"Auto-refreshes every {REFRESH_SECONDS} seconds | Filters: $2–$20 | Float <20M | ≥5× Avg Volume | Breaking News")

placeholder = st.empty()

while True:
    with placeholder.container():
        df = get_stock_data(DEFAULT_SYMBOLS)
        if df.empty:
            st.warning("No qualifying stocks found right now.")
        else:
            st.dataframe(df.drop(columns=["SortScore"]), use_container_width=True)

        st.caption(f"🔄 Last updated: {time.strftime('%H:%M:%S')}")

    time.sleep(REFRESH_SECONDS)
    st.rerun()
