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
    prev_close = round(pri_
