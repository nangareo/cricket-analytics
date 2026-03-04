# ============================================
# CRICKET ANALYTICS - CENTRAL CONFIG FILE
# ============================================

# ---- DATA PATH ----
DATA_FOLDER = "data/raw"

# ---- MINIMUM MATCHES ----
MIN_MATCHES = 20

# ---- ALL IPL SEASONS AVAILABLE ----
ALL_SEASONS = [
    "2008", "2009", "2010", "2011", "2012",
    "2013", "2014", "2015", "2016", "2017",
    "2018", "2019", "2020", "2021", "2022",
    "2023", "2024", "2025"
]

# ---- RETIRED PLAYERS ----
# MS Dhoni removed - still plays!
RETIRED_PLAYERS = [
    # Batsmen
    "SR Tendulkar", "SC Ganguly", "RT Ponting",
    "KC Sangakkara", "CH Gayle", "SR Watson",
    "G Gambhir", "V Sehwag", "BB McCullum",
    "MEK Hussey", "DR Smith", "AC Gilchrist",
    "DR Martyn", "ML Hayden",
    # Bowlers
    "SL Malinga", "Z Khan", "RP Singh",
    "P Kumar", "PP Ojha", "AB Dinda",
    "DW Steyn", "SW Tait", "B Lee",
    "DE Bollinger", "DP Nannes",
    "Harbhajan Singh", "A Mishra",
    # All-rounders
    "IK Pathan", "YK Pathan", "AS Raina",
    "DJ Bravo", "DA Warner",
]

# ---- ACTIVE FILTER (set by terminal menu) ----
# Do not edit manually - controlled by filter_selector.py
SELECTED_SEASONS = None   # None = All time
SELECTED_YEARS   = None   # None = All time