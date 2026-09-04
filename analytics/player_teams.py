# ============================================
# Player -> Team resolver
# Cricket Analytics DevOps Project
# ============================================
"""
Writes analytics/player_teams.csv: every player mapped to the franchise they
most recently turned out for, derived from the deliveries themselves.

Replaces a hand-maintained dict that covered 250 names and left 186 players
rendering as "Unknown" on the dashboard. The dashboard reads the generated CSV,
so it keeps working inside the Docker image, where data/raw/ is not shipped.
"""

import os
import sys

import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestion.data_loader import (add_bowling_team, canonical_team,
                                   load_filtered_data)

OUTPUT_PATH = "analytics/player_teams.csv"


def build_player_teams(df):
    """One row per player: current team, span of seasons, matches played."""
    df = add_bowling_team(df)

    roles = [
        ("striker", "batting_team"),
        ("non_striker", "batting_team"),
        ("bowler", "bowling_team"),
        ("fielder_1", "bowling_team"),
        ("fielder_2", "bowling_team"),
    ]
    frames = [
        df[[player_col, team_col, "season", "match_id"]].rename(
            columns={player_col: "player", team_col: "team"}
        )
        for player_col, team_col in roles
    ]

    appearances = pd.concat(frames, ignore_index=True).dropna(
        subset=["player", "team"]
    )
    appearances["team"] = appearances["team"].map(canonical_team)

    # Most recent season wins; within it, the side they appeared for most.
    ranked = (
        appearances.groupby(["player", "season", "team"])
        .size().reset_index(name="balls")
        .sort_values(["player", "season", "balls"], ascending=[True, False, False])
    )
    current = ranked.drop_duplicates(subset="player", keep="first")[
        ["player", "team", "season"]
    ].rename(columns={"season": "last_season"})

    span = appearances.groupby("player").agg(
        first_season=("season", "min"),
        matches=("match_id", "nunique"),
    ).reset_index()

    out = current.merge(span, on="player", how="left")
    return out.sort_values(["team", "player"]).reset_index(drop=True)


def show_results(teams):
    print("\n" + "=" * 70)
    print("🏏 PLAYER → TEAM MAP")
    print("=" * 70)
    per_team = teams.groupby("team")["player"].count().sort_values(ascending=False)
    print(per_team.to_string())
    print("\n" + "=" * 70)
    print(f"📊 Players mapped: {len(teams)}  ·  Franchises: {teams['team'].nunique()}")
    print("=" * 70)

    teams.to_csv(OUTPUT_PATH, index=False)
    print(f"\n💾 Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    print("=" * 70)
    print("🏏 CRICKET ANALYTICS — PLAYER TEAM RESOLVER")
    print("=" * 70)
    df = load_filtered_data()
    if df is not None:
        show_results(build_player_teams(df))
