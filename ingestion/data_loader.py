"""
Data Loader — Cricket Analytics
File: ingestion/data_loader.py

Two responsibilities:
1. load_filtered_data() / get_filter_summary() — used by scorer scripts
   (batting_scorer.py, bowling_scorer.py, fielding_scorer.py, allrounder_scorer.py)
   to load RAW ball-by-ball match data from data/raw
2. load_batting_scores() etc — used by the Streamlit dashboard
   to load already-computed score CSVs from analytics/*/  
"""

import os
import pandas as pd
import config

# ── RAW MATCH DATA LOADING (for scorer scripts) ──────────────

BALL_COLUMNS = [
    "type", "innings", "ball", "batting_team", "batter", "non_striker",
    "bowler", "runs_batter", "runs_extras", "wides", "noballs", "byes",
    "legbyes", "penalty", "wicket_type", "player_dismissed", "other_wicket_type",
    "other_player_dismissed", "extra_1", "extra_2", "extra_3", "extra_4"
]

def _load_single_match(filepath):
    """Parse one Cricsheet csv2 combined file, return only ball rows"""
    rows = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("ball,"):
                rows.append(line.split(","))
    if not rows:
        return None

    max_len = len(BALL_COLUMNS)
    fixed_rows = []
    for r in rows:
        if len(r) < max_len:
            r = r + [""] * (max_len - len(r))
        elif len(r) > max_len:
            r = r[:max_len]
        fixed_rows.append(r)

    df = pd.DataFrame(fixed_rows, columns=BALL_COLUMNS)
    df["innings"]     = pd.to_numeric(df["innings"], errors="coerce")
    df["ball"]        = pd.to_numeric(df["ball"], errors="coerce")
    df["runs_batter"] = pd.to_numeric(df["runs_batter"], errors="coerce").fillna(0)
    df["runs_extras"] = pd.to_numeric(df["runs_extras"], errors="coerce").fillna(0)
    df["wides"]       = pd.to_numeric(df["wides"], errors="coerce").fillna(0)
    df["noballs"]     = pd.to_numeric(df["noballs"], errors="coerce").fillna(0)
    df["match_id"]    = os.path.basename(filepath).replace(".csv", "")

    # Rename to match scorer script expectations
    df = df.rename(columns={
        "batter": "striker",
        "runs_batter": "runs_off_bat"
    })
    return df

def load_all_matches(folder=None):
    """Load all Cricsheet csv2 match files in a folder"""
    folder = folder or getattr(config, "DATA_FOLDER", "data/raw")
    all_files = [f for f in os.listdir(folder) if f.endswith(".csv") and "_info" not in f]
    print(f"📂 Found {len(all_files)} match files...")

    all_data = []
    skipped = 0
    for file in all_files:
        filepath = os.path.join(folder, file)
        try:
            df = _load_single_match(filepath)
            if df is not None and not df.empty:
                all_data.append(df)
            else:
                skipped += 1
        except Exception as e:
            print(f"⚠️  Skipping {file}: {e}")
            skipped += 1

    if not all_data:
        raise ValueError("No objects to concatenate — check data folder path")

    combined = pd.concat(all_data, ignore_index=True)
    print(f"✅ Loaded {len(combined)} total balls across {len(all_data)} matches! (skipped {skipped})")
    return combined

def load_filtered_data():
    """Load raw match data, optionally filtered by season/team per config or saved filter"""
    folder = getattr(config, "DATA_FOLDER", "data/raw")
    try:
        df = load_all_matches(folder)
        return df
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None

def get_filter_summary():
    """Returns a human-readable string describing the active filter"""
    filter_path = "data/selected_filter.json"
    if os.path.exists(filter_path):
        import json
        with open(filter_path, "r") as f:
            filt = json.load(f)
        season = filt.get("season", "All Time")
        return f"{season}"
    return "All Time · 2008-2026"


# ── SCORE CSV LOADING (for dashboard) ──────────────

CSV_PATHS = {
    "batting":    "analytics/batting/batting_scores.csv",
    "bowling":    "analytics/bowling/bowling_scores.csv",
    "fielding":   "analytics/fielding/fielding_scores.csv",
    "allrounder": "analytics/allrounder/allrounder_scores.csv",
}

def _load_csv(key):
    path = CSV_PATHS.get(key, "")
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

def load_batting_scores():
    return _load_csv("batting")

def load_bowling_scores():
    return _load_csv("bowling")

def load_fielding_scores():
    return _load_csv("fielding")

def load_allrounder_scores():
    return _load_csv("allrounder")