"""
Fixed CSV loader for Cricsheet's new combined csv2 format.
Replace the load_all_matches() function in each scorer file with this.
"""

import pandas as pd
import glob
import os

BALL_COLUMNS = [
    "type", "innings", "ball", "batting_team", "batter", "non_striker",
    "bowler", "runs_batter", "runs_extras", "wides", "noballs", "byes",
    "legbyes", "penalty", "wicket_type", "player_dismissed", "other_wicket_type",
    "other_player_dismissed", "extra_1", "extra_2", "extra_3", "extra_4"
]

def load_single_match(filepath):
    """Load one Cricsheet csv2 file, return only ball-by-ball rows as DataFrame"""
    rows = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("ball,"):
                parts = line.split(",")
                rows.append(parts)
    if not rows:
        return None

    # Pad/truncate rows to consistent length
    max_len = len(BALL_COLUMNS)
    fixed_rows = []
    for r in rows:
        if len(r) < max_len:
            r = r + [""] * (max_len - len(r))
        elif len(r) > max_len:
            r = r[:max_len]
        fixed_rows.append(r)

    df = pd.DataFrame(fixed_rows, columns=BALL_COLUMNS)

    # Type conversions
    df["innings"]      = pd.to_numeric(df["innings"], errors="coerce")
    df["runs_batter"]  = pd.to_numeric(df["runs_batter"], errors="coerce").fillna(0)
    df["runs_extras"]  = pd.to_numeric(df["runs_extras"], errors="coerce").fillna(0)

    # Add match_id from filename
    match_id = os.path.basename(filepath).replace(".csv", "")
    df["match_id"] = match_id

    return df

def load_all_matches(data_folder):
    """Load all Cricsheet csv2 match files in a folder"""
    all_files = glob.glob(os.path.join(data_folder, "*.csv"))
    # Skip any _info.csv files if they exist separately
    all_files = [f for f in all_files if "_info" not in os.path.basename(f)]

    all_data = []
    skipped = 0
    for f in all_files:
        try:
            df = load_single_match(f)
            if df is not None and not df.empty:
                all_data.append(df)
            else:
                skipped += 1
        except Exception as e:
            print(f"⚠️  Skipping {os.path.basename(f)}: {e}")
            skipped += 1

    print(f"✅ Loaded {len(all_data)} matches, skipped {skipped}")

    if not all_data:
        raise ValueError("No objects to concatenate — check data folder path")

    combined = pd.concat(all_data, ignore_index=True)
    return combined

if __name__ == "__main__":
    import sys
    folder = sys.argv[1] if len(sys.argv) > 1 else "data"
    df = load_all_matches(folder)
    print(df.shape)
    print(df.head(10))
