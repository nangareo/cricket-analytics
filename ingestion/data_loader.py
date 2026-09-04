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

import csv
import json
import os

import numpy as np
import pandas as pd

import config

# ── RAW MATCH DATA LOADING (for scorer scripts) ──────────────

# Cricsheet csv2 "ball" rows carry exactly 21 fields. Two of them are easy to
# get wrong and both have caused bad numbers here before:
#
#   delivery — a per-over counter that keeps incrementing through extras, so a
#              single over can run 0.1 … 0.7 … 0.8. Useless for phase filters.
#   ball     — the real over.legal_ball, which repeats when a delivery is
#              re-bowled. This is the one to filter and group on.
BALL_COLUMNS = [
    "type", "innings", "delivery", "batting_team", "batter", "non_striker",
    "bowler", "runs_batter", "runs_extras", "wides", "noballs", "byes",
    "legbyes", "penalty", "wicket_type", "player_dismissed", "ball",
    "non_boundary", "fielder_1", "fielder_2", "unused",
]

NUMERIC_COLUMNS = [
    "innings", "delivery", "ball", "runs_batter", "runs_extras",
    "wides", "noballs", "byes", "legbyes", "penalty",
]

# csv2 leaves these blank when they do not apply. Blank must become NA — if it
# stays as an empty string, .notna() is True on every single delivery and the
# dismissal/wicket counts silently become "number of balls".
NULLABLE_TEXT_COLUMNS = [
    "wicket_type", "player_dismissed", "fielder_1", "fielder_2",
]

# Dismissals the bowler gets credit for. Run outs, retirements and obstruction
# are dismissals but they are not the bowler's wickets.
BOWLER_WICKET_TYPES = {
    "bowled", "caught", "caught and bowled", "lbw", "stumped", "hit wicket",
}

POWERPLAY_LAST_OVER = 5   # overs 0-5
DEATH_FIRST_OVER = 16     # overs 16-19


def _season_from_info(info):
    """
    Which IPL season a match belongs to.

    Derived from the match date, not the 'season' label. Cricsheet writes
    '2020/21' for IPL 2020 because it straddles the cricket year, so reading
    the label would file that whole season one year late.
    """
    for value in info.get("date", []):
        try:
            return int(str(value)[:4])
        except (TypeError, ValueError):
            continue
    for value in info.get("season", []):
        try:
            return int(str(value)[:4])
        except (TypeError, ValueError):
            continue
    return 0


def _load_single_match(filepath):
    """Parse one Cricsheet csv2 combined file, return only ball rows."""
    rows = []
    info = {}
    with open(filepath, newline="", encoding="utf-8") as fh:
        for record in csv.reader(fh):
            if not record:
                continue
            if record[0] == "ball":
                rows.append(record)
            elif record[0] == "info" and len(record) >= 3:
                info.setdefault(record[1], []).append(record[2])

    if not rows:
        return None

    width = len(BALL_COLUMNS)
    normalised = [
        (r + [""] * (width - len(r))) if len(r) < width else r[:width]
        for r in rows
    ]

    df = pd.DataFrame(normalised, columns=BALL_COLUMNS)

    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    for col in ["runs_batter", "runs_extras", "wides", "noballs", "byes",
                "legbyes", "penalty"]:
        df[col] = df[col].fillna(0)

    for col in NULLABLE_TEXT_COLUMNS:
        df[col] = df[col].replace({"": None, '""': None})

    # Whole-over number, for powerplay / death filters.
    df["over"] = np.floor(df["ball"]).astype("int64")

    # A wide is not a ball faced by the batter. A wide or a no-ball does not
    # count towards the over.
    df["is_ball_faced"] = df["wides"] == 0
    df["is_legal_ball"] = (df["wides"] == 0) & (df["noballs"] == 0)

    df["match_id"] = os.path.basename(filepath).replace(".csv", "")
    df["season"] = _season_from_info(info)
    df["season"] = df["season"].astype("int64")

    # Both sides, straight from the info block. Needed to identify the fielding
    # team in matches that were abandoned before the second innings, where only
    # one team ever appears as batting_team.
    sides = info.get("team", [])
    df["team_1"] = sides[0] if len(sides) > 0 else None
    df["team_2"] = sides[1] if len(sides) > 1 else None

    # Names the scorer scripts expect.
    df = df.rename(columns={"batter": "striker", "runs_batter": "runs_off_bat"})
    return df.drop(columns=["type", "unused"])


def load_all_matches(folder=None):
    """Load all Cricsheet csv2 match files in a folder."""
    folder = folder or getattr(config, "DATA_FOLDER", "data/raw")
    all_files = [f for f in os.listdir(folder)
                 if f.endswith(".csv") and "_info" not in f]
    print(f"📂 Found {len(all_files)} match files...")

    all_data = []
    skipped = 0
    for file in sorted(all_files):
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
    print(f"✅ Loaded {len(combined)} total balls across "
          f"{len(all_data)} matches! (skipped {skipped})")
    return combined


def count_dismissals(df):
    """
    Dismissals per batter, keyed on who actually got out.

    Grouping on 'striker' would misfile every non-striker run out.
    """
    out = df[df["player_dismissed"].notna()]
    return (
        out.groupby("player_dismissed").size()
        .rename("dismissals").rename_axis("striker").reset_index()
    )


def player_match_counts(df):
    """Matches played, counting every role a player can appear in."""
    frames = []
    for col in ["striker", "non_striker", "bowler", "fielder_1", "fielder_2"]:
        frames.append(df[[col, "match_id"]].rename(columns={col: "player"}))
    appearances = pd.concat(frames, ignore_index=True).dropna(subset=["player"])
    return (
        appearances.groupby("player")["match_id"].nunique()
        .rename("matches").reset_index()
    )


# Franchises that were renamed. Defunct sides (Deccan Chargers, Pune Warriors,
# Gujarat Lions, Rising Pune Supergiant, Kochi Tuskers Kerala) keep their own
# names — they were never renamed, they stopped existing.
CURRENT_TEAM_NAME = {
    "Royal Challengers Bangalore": "Royal Challengers Bengaluru",
    "Kings XI Punjab": "Punjab Kings",
    "Delhi Daredevils": "Delhi Capitals",
    "Rising Pune Supergiants": "Rising Pune Supergiant",
}


def canonical_team(name):
    """Current name of a franchise."""
    return CURRENT_TEAM_NAME.get(name, name)


def add_bowling_team(df):
    """
    Add the fielding side for every delivery.

    csv2 records only batting_team. The bowler and the fielders belong to the
    other side in that match, so reading batting_team off a bowler's delivery
    would place him on the opposition.
    """
    df = df.copy()
    # Fall back to the sides seen batting, for any file with no info block.
    seen = df.groupby("match_id")["batting_team"].unique()

    def other(match_id, batting_team, team_1, team_2):
        for candidate in (team_1, team_2):
            if candidate and candidate != batting_team:
                return candidate
        opponents = [t for t in seen.get(match_id, []) if t != batting_team]
        return opponents[0] if len(opponents) == 1 else None

    df["bowling_team"] = [
        other(m, b, t1, t2)
        for m, b, t1, t2 in zip(
            df["match_id"], df["batting_team"], df["team_1"], df["team_2"]
        )
    ]
    return df


def resolve_player_teams(df):
    """
    Map every player to the franchise they most recently played for.

    Built from the deliveries themselves, so new players are picked up the
    moment their data lands. The previous hand-maintained dict left 186
    players rendering as "Unknown".
    """
    df = add_bowling_team(df)

    batting_side = [("striker", "batting_team"), ("non_striker", "batting_team")]
    fielding_side = [("bowler", "bowling_team"), ("fielder_1", "bowling_team"),
                     ("fielder_2", "bowling_team")]

    frames = []
    for player_col, team_col in batting_side + fielding_side:
        part = df[[player_col, team_col, "season"]].rename(
            columns={player_col: "player", team_col: "team"}
        )
        frames.append(part)

    appearances = pd.concat(frames, ignore_index=True).dropna(
        subset=["player", "team"]
    )
    appearances["team"] = appearances["team"].map(canonical_team)

    # Most recent season wins; within it, the side they appeared for most.
    counts = (
        appearances.groupby(["player", "season", "team"]).size()
        .reset_index(name="balls")
        .sort_values(["player", "season", "balls"], ascending=[True, False, False])
    )
    latest = counts.drop_duplicates(subset="player", keep="first")
    return dict(zip(latest["player"], latest["team"]))


def normalize(series):
    """Scale a metric to 0-100. Higher is better."""
    lo, hi = series.min(), series.max()
    if pd.isna(lo) or pd.isna(hi) or hi == lo:
        return series * 0
    return ((series - lo) / (hi - lo) * 100).round(2)


def normalize_inverse(series):
    """Scale a metric to 0-100. Lower is better."""
    lo, hi = series.min(), series.max()
    if pd.isna(lo) or pd.isna(hi) or hi == lo:
        return series * 0
    return ((hi - series) / (hi - lo) * 100).round(2)


def load_filtered_data():
    """Load raw match data, optionally filtered by season/team per config."""
    folder = getattr(config, "DATA_FOLDER", "data/raw")
    try:
        return load_all_matches(folder)
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None


def get_filter_summary():
    """Returns a human-readable string describing the active filter."""
    filter_path = "data/selected_filter.json"
    if os.path.exists(filter_path):
        with open(filter_path, "r") as f:
            filt = json.load(f)
        return filt.get("season", "All Time")
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
