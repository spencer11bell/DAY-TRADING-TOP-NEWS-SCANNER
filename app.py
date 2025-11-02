import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="🔥 Custom Day Trading Scanner", layout="wide")

# ===== CONFIG =====
PRICE_MIN = 2
PRICE_MAX = 20
FLOAT_MAX = 20_000_000  # 20 million
VOLUME_MULTIPLIER = 5
NEWS_LOOKBACK_HOURS = 3

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

# ===== GET STOCK DATA =====
def get_stock_data(symbols):
    data = []
    for sym in symbols:
        try:
            info = yf.Ticker(sym).info
            price = info.get("regularMarketPrice")
            prev_close = info.get("previousClose")
            change_pct = ((price - prev_close) / prev_close) * 100 if price and prev_close else 0
            volume = info.get("volume", 0)
            avg_vol = info.get("averageVolume", 1)
            float_shares = info.get("floatShares", 0)
            vol_ratio = volume / avg_vol if avg_vol else 0
            if (
                price and PRICE_MIN <= price <= PRICE_MAX
                and float_shares and float_shares <= FLOAT_MAX
                and vol_ratio >= VOLUME_MULTIPLIER
            ):
                data.append({
                    "Symbol": sym,
                    "Price": price,
                    "Change %": round(change_pct, 2),
                    "Volume": volume,
                    "Float": float_shares,
                    "🔥 Score": fire_display_colored(int(min(vol_ratio // 2, 5))),
                    "Headline": get_news_headline(sym)
                })
        except Exception:
            pass
    return pd.DataFrame(data)

# ===== GET NEWS HEADLINES =====
def get_news_headline(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v1/finance/search?q={symbol}"
        res = requests.get(url).json()
        news_items = [i["title"] for i in res.get("news", []) if "title" in i]
        if news_items:
            return news_items[0]
        return "—"
    except Exception:
        return "—"

# ===== MAIN DASHBOARD =====
st.title("🔥 Real-Time Day Trading Scanner")
st.caption("Filters: $2–$20 | Float < 20M | ≥5× Avg Volume | Breaking News")

symbols_input = st.text_area(
    "Enter symbols (comma separated):",
    "TSLA, AAPL, NVDA, AMD, PLTR, SOFI, MARA, RIOT"
)
symbols = [s.strip().upper() for s in symbols_input.split(",") if s.strip()]

if st.button("🔍 Scan Now"):
    df = get_stock_data(symbols)
    if df.empty:
        st.warning("No stocks matched your filters.")
    else:
        st.dataframe(df, use_container_width=True)
