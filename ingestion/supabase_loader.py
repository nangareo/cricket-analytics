"""
ETL Script — Load Cricket Analytics CSV data into Supabase PostgreSQL
Run: python ingestion/supabase_loader.py
"""

import os, json, urllib.request, urllib.error
import pandas as pd

SUPABASE_URL = "https://gruiqljiokngvxscjlkj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdydWlxbGppb2tuZ3Z4c2NqbGtqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NzM3MjQwMSwiZXhwIjoyMDkyOTQ4NDAxfQ.JBF7v0h0eR9SOIJI2BdhoQgNwn8SAVeC-voAzY4esW8"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}
BATCH_SIZE = 200

BATTING_CSV    = "analytics/batting/batting_scores.csv"
BOWLING_CSV    = "analytics/bowling/bowling_scores.csv"
FIELDING_CSV   = "analytics/fielding/fielding_scores.csv"
ALLROUNDER_CSV = "analytics/allrounder/allrounder_scores.csv"

def http_req(method, endpoint, data=None):
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, r.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")

def clear_table(table):
    s, _ = http_req("DELETE", f"{table}?id=gte.0")
    print(f"  🗑️  Cleared {table} ({s})")

def insert_batch(table, records):
    s, b = http_req("POST", table, records)
    if s in [200, 201, 204]: return True
    print(f"  ❌ Error ({s}): {b[:200]}")
    return False

def to_int(v):
    try:
        if v is None or (isinstance(v, float) and v != v): return 0
        return int(float(v))
    except: return 0

def to_float(v):
    try:
        if v is None or (isinstance(v, float) and v != v): return None
        return float(v)
    except: return None

def find_player_col(df):
    """Auto-detect the player name column"""
    for col in ["player", "batter", "bowler", "fielder", "name", "Player", "Batter", "Bowler"]:
        if col in df.columns:
            return col
    # fallback: first text column
    for col in df.columns:
        if df[col].dtype == object:
            return col
    return None

def load_table(csv_path, table, col_map, int_cols=None, float_cols=None):
    print(f"\n📂 {csv_path} → {table}")
    if not os.path.exists(csv_path):
        print(f"  ⚠️  Not found — skipping"); return 0

    df = pd.read_csv(csv_path)
    print(f"  📋 Columns found: {df.columns.tolist()}")

    # Auto-detect player column and add to map
    player_col = find_player_col(df)
    if player_col and player_col not in col_map:
        col_map[player_col] = "player"
        print(f"  🔍 Auto-detected player col: '{player_col}'")

    df = df.rename(columns=col_map)

    # Keep only mapped columns that exist
    keep = [v for v in col_map.values() if v in df.columns]
    df = df[keep]
    df["season"] = "All Time"

    # Type casting
    for col in (int_cols or []):
        if col in df.columns:
            df[col] = df[col].apply(to_int)
    for col in (float_cols or []):
        if col in df.columns:
            df[col] = df[col].apply(to_float)

    # Final clean — NaN to None
    records = []
    for r in df.to_dict(orient="records"):
        clean = {}
        for k, v in r.items():
            if isinstance(v, float) and v != v:
                clean[k] = None
            else:
                clean[k] = v
        records.append(clean)

    total = len(records)
    print(f"  📊 {total} records to insert")
    clear_table(table)

    loaded = 0
    for i in range(0, total, BATCH_SIZE):
        batch = records[i:i+BATCH_SIZE]
        if insert_batch(table, batch):
            loaded += len(batch)
            print(f"  ✅ {loaded}/{total} rows...")
    print(f"  🎉 {loaded} rows loaded into '{table}'!")
    return loaded

# Column maps — comprehensive, covers all possible CSV column names
BATTING_COLS = {
    "player":"player","batter":"player","name":"player","Player":"player","Batter":"player",
    "matches":"matches","innings":"innings","runs":"runs",
    "avg":"avg","average":"avg","batting_avg":"avg",
    "strike_rate":"strike_rate","sr":"strike_rate",
    "hundreds":"hundreds","100s":"hundreds",
    "fifties":"fifties","50s":"fifties",
    "fours":"fours","4s":"fours",
    "sixes":"sixes","6s":"sixes",
    "batting_score":"batting_score","score":"batting_score",
}
BOWLING_COLS = {
    "player":"player","bowler":"player","name":"player","Player":"player","Bowler":"player",
    "matches":"matches","innings":"innings","wickets":"wickets",
    "economy":"economy","econ":"economy",
    "avg":"avg","bowling_avg":"avg","average":"avg",
    "strike_rate":"strike_rate","sr":"strike_rate",
    "dot_ball_pct":"dot_ball_pct","dot_pct":"dot_ball_pct",
    "bowling_score":"bowling_score","score":"bowling_score",
}
FIELDING_COLS = {
    "player":"player","fielder":"player","name":"player","Player":"player","Fielder":"player",
    "matches":"matches","catches":"catches","runouts":"runouts",
    "stumpings":"stumpings","fielding_score":"fielding_score","score":"fielding_score",
}
ALLROUNDER_COLS = {
    "player":"player","name":"player","Player":"player",
    "matches":"matches",
    "batting_score":"batting_score","bowling_score":"bowling_score",
    "allrounder_score":"allrounder_score","score":"allrounder_score",
}

if __name__ == "__main__":
    print("="*55)
    print("🏏 Cricket Analytics — Supabase ETL Loader")
    print("="*55)

    print("\n🔌 Testing connection...")
    s, b = http_req("GET", "batting_scores?limit=1")
    if s == 200: print("✅ Connected!\n")
    else: print(f"❌ Failed ({s}): {b}"); exit(1)

    total  = load_table(BATTING_CSV,    "batting_scores",    BATTING_COLS,
                        int_cols=["matches","innings","runs","hundreds","fifties","fours","sixes"],
                        float_cols=["avg","strike_rate","batting_score"])
    total += load_table(BOWLING_CSV,    "bowling_scores",    BOWLING_COLS,
                        int_cols=["matches","innings","wickets"],
                        float_cols=["economy","avg","strike_rate","dot_ball_pct","bowling_score"])
    total += load_table(FIELDING_CSV,   "fielding_scores",   FIELDING_COLS,
                        int_cols=["matches","catches","runouts","stumpings"],
                        float_cols=["fielding_score"])
    total += load_table(ALLROUNDER_CSV, "allrounder_scores", ALLROUNDER_COLS,
                        int_cols=["matches"],
                        float_cols=["batting_score","bowling_score","allrounder_score"])

    print(f"\n{'='*55}")
    print(f"✅ ETL Complete! Total rows loaded: {total}")
    print(f"{'='*55}")
    print("\nVerify in Supabase → Table Editor ✅")
