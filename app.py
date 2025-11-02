# app.py - FAKE DATA MODE (for testing UI)
# ------------------------------------------------------------------
# Replace this file with your real scanner code when ready.
# To switch back: remove the section marked "FAKE DATA BLOCK" and
# re-insert your yfinance/news calls (see previous version).
# ------------------------------------------------------------------

import streamlit as st
import pandas as pd
import time
import random

st.set_page_config(page_title="🔥 Auto Day Trading Scanner - FAKE DATA", layout="wide")

# ===== CONFIG =====
PRICE_MIN = 2
PRICE_MAX = 20
FLOAT_MAX = 20_000_000  # 20 million
VOLUME_MULTIPLIER = 5
REFRESH_SECONDS = 10  # faster for testing
DEFAULT_SYMBOLS = [
    "AAA", "BBB", "CCC", "DDD", "EEE", "FFF", "GGG", "HHH",
    "III", "JJJ", "KKK", "LLL", "MMM", "NNN", "OOO", "PPP",
    "QQQ", "RRR", "SSS", "TTT"
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

# ===== FAKE DATA GENERATOR =====
# Deterministic randomness so reloading shows consistent results during testing
random.seed(42)

def generate_fake_for_symbol(sym: str, iteration_seed: int):
    """
    Returns a dict matching the expected columns:
    Change %, Symbol, 🔥 News (emoji), Price, Volume, Float, Headline, SortScore
    Some symbols will meet filters, others will not. This simulates a real run.
    """
    # create pseudo-random deterministic values using symbol + iteration_seed
    r = random.Random(f"{sym}-{iteration_seed}")

    # price intentionally usually between 1 and 30, so filter will exclude some
    price = round(r.uniform(1.0, 30.0), 2)
    prev_close = round(price / (1 + r.uniform(-0.15, 0.15)), 2)  # +/-15% variation
    if prev_close == 0:
        change_pct = 0.0
    else:
        change_pct = round((price - prev_close) / prev_close * 100, 2)

    # average volume between 10k and 5M, volume sometimes spikes to simulate movers
    avg_vol = int(r.uniform(10_000, 5_000_000))
    # make volume often >= 5x avg for a subset (appro
