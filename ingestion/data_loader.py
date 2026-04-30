"""
Updated Data Loader — Supabase first, CSV fallback
File: ingestion/data_loader.py  (replace existing)
"""

import os, json, urllib.request, urllib.error
import pandas as pd

SUPABASE_URL = "https://gruiqljiokngvxscjlkj.supabase.co"
# Using service role key for full access
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdydWlxbGppb2tuZ3Z4c2NqbGtqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NzM3MjQwMSwiZXhwIjoyMDkyOTQ4NDAxfQ.JBF7v0h0eR9SOIJI2BdhoQgNwn8SAVeC-voAzY4esW8"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

CSV_PATHS = {
    "batting":    "analytics/batting/batting_scores.csv",
    "bowling":    "analytics/bowling/bowling_scores.csv",
    "fielding":   "analytics/fielding/fielding_scores.csv",
    "allrounder": "analytics/allrounder/allrounder_scores.csv",
}

PLAYER_COL_MAP = {
    "batting_scores":    "batter",
    "bowling_scores":    "bowler",
    "fielding_scores":   "fielder",
    "allrounder_scores": "player",
}

def _fetch_supabase(table, limit=2000):
    """Fetch data from Supabase REST API"""
    url = f"{SUPABASE_URL}/rest/v1/{table}?limit={limit}&order=id.asc"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode("utf-8"))
            if not data:
                return None
            df = pd.DataFrame(data)
            # Rename player → original col name
            if "player" in df.columns and table in PLAYER_COL_MAP:
                df = df.rename(columns={"player": PLAYER_COL_MAP[table]})
            # Drop DB-only columns
            for col in ["id", "created_at", "season"]:
                if col in df.columns:
                    df = df.drop(columns=[col])
            return df
    except Exception as e:
        print(f"  ⚠️  Supabase fetch failed for {table}: {e}")
        return None

def _load_csv(key):
    path = CSV_PATHS.get(key, "")
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

def load_batting_scores():
    df = _fetch_supabase("batting_scores")
    if df is not None and not df.empty:
        print("✅ Batting → Supabase"); return df
    print("⚠️  Batting → CSV fallback"); return _load_csv("batting")

def load_bowling_scores():
    df = _fetch_supabase("bowling_scores")
    if df is not None and not df.empty:
        print("✅ Bowling → Supabase"); return df
    print("⚠️  Bowling → CSV fallback"); return _load_csv("bowling")

def load_fielding_scores():
    df = _fetch_supabase("fielding_scores")
    if df is not None and not df.empty:
        print("✅ Fielding → Supabase"); return df
    print("⚠️  Fielding → CSV fallback"); return _load_csv("fielding")

def load_allrounder_scores():
    df = _fetch_supabase("allrounder_scores")
    if df is not None and not df.empty:
        print("✅ Allrounder → Supabase"); return df
    print("⚠️  Allrounder → CSV fallback"); return _load_csv("allrounder")

def get_data_source():
    df = _fetch_supabase("batting_scores")
    return "supabase" if (df is not None and not df.empty) else "csv"
