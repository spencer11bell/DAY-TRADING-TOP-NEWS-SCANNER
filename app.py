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
        ret
