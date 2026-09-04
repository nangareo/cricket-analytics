# ============================================
# CRICKET ANALYTICS - CENTRAL CONFIG FILE
# ============================================

import os

# ---- DATA PATH ----
DATA_FOLDER = "data/raw"


# ---- LIVE SCORES API ----
def get_cricapi_key():
    """
    CricketData.org key used by the Live Scores tab.

    Resolved from the CRICAPI_KEY environment variable, falling back to
    .streamlit/secrets.toml when running under Streamlit.

    Never hardcode the key here. This repository is public, so any key
    committed to it must be treated as burned and rotated.
    """
    key = os.environ.get("CRICAPI_KEY", "").strip()
    if key:
        return key
    try:
        import streamlit as st

        return str(st.secrets.get("CRICAPI_KEY", "")).strip()
    except Exception:
        return ""

# ---- MINIMUM MATCHES ----
MIN_MATCHES = 20

# ---- ALL IPL SEASONS AVAILABLE ----
ALL_SEASONS = [
    "2008", "2009", "2010", "2011", "2012",
    "2013", "2014", "2015", "2016", "2017",
    "2018", "2019", "2020", "2021", "2022",
    "2023", "2024", "2025", "2026"
]

# ---- RETIRED PLAYERS ----
# MS Dhoni removed - still plays!
RETIRED_PLAYERS = [
    "SR Tendulkar", "SC Ganguly", "RT Ponting",
    "KC Sangakkara", "CH Gayle", "SR Watson",
    "G Gambhir", "V Sehwag", "BB McCullum",
    "MEK Hussey", "DR Smith", "AC Gilchrist",
    "SL Malinga", "Z Khan", "RP Singh",
    "DW Steyn", "SW Tait", "B Lee",
    "DE Bollinger", "DP Nannes",
    "Harbhajan Singh", "A Mishra",
    "IK Pathan", "YK Pathan", "AS Raina",
    "DJ Bravo", "DA Warner",
]

# ---- ACTIVE FILTER (set by terminal menu) ----
# Do not edit manually - controlled by filter_selector.py
SELECTED_SEASONS = None   # None = All time
SELECTED_YEARS   = None   # None = All time