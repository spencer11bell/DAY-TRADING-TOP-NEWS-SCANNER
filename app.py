import streamlit as st
import pandas as pd
import random
import time
from streamlit_autorefresh import st_autorefresh

# ===== CONFIG =====
st.set_page_config(page_title="🔥 Day Trading Scanner - COLORFUL", layout="wide")

PRICE_MIN = 2
PRICE_MAX = 20
FLOAT_MAX = 20_000_000
REFRESH_SECONDS = 10
DEFAULT_SYMBOLS = [
    "AAA","BBB","CCC","DDD","EEE","FFF","GGG","HHH",
    "III","JJJ","KKK","LLL","MMM","NNN","OOO","PPP",
    "QQQ","RRR","SSS","TTT"
]

# ===== FIRE EMOJI LOGIC (single emoji, colored) =====
def fire_display_colored(score: int) -> str:
    if score <= 0:
        return ""
    elif score <= 2:
        return '<span style="color:yellow;">🔥</span>'
    elif score <= 4:
        return '<span style="color:orange;">🔥</span>'
    else:
        return '<span style="color:red;">🔥</span>'

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
