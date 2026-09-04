# ============================================
# STEP 4 - Batting Analytics Scorer
# Cricket Analytics DevOps Project
# ============================================

import os
import sys
import warnings

import pandas as pd

warnings.filterwarnings('ignore')

sys.path.append(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

from ingestion.data_loader import (DEATH_FIRST_OVER, POWERPLAY_LAST_OVER,
                                   count_dismissals, get_filter_summary,
                                   load_filtered_data, normalize,
                                   normalize_inverse)
import config


def calculate_batting_scores(df):
    """Calculate batting metrics for every batsman"""
    print("\n⚙️  Calculating batting scores...")

    faced = df[df['is_ball_faced']]

    # ---- METRIC 1: Basic runs and balls ----
    batting = faced.groupby('striker').agg(
        total_runs  = ('runs_off_bat', 'sum'),
        balls_faced = ('runs_off_bat', 'count'),
        fours       = ('runs_off_bat', lambda x: (x == 4).sum()),
        sixes       = ('runs_off_bat', lambda x: (x == 6).sum()),
        matches     = ('match_id', 'nunique'),
    ).reset_index()

    # ---- METRIC 2: Dismissals ----
    # Keyed on who actually got out, so a non-striker run out is filed
    # against the right player.
    batting = batting.merge(
        count_dismissals(df), on='striker', how='left'
    )
    batting['dismissals'] = batting['dismissals'].fillna(0).astype('int64')

    # ---- METRIC 3: Batting Average ----
    # Runs scored divided by number of times out
    batting['average'] = batting.apply(
        lambda x: x['total_runs'] / x['dismissals']
        if x['dismissals'] > 0 else x['total_runs'], axis=1
    ).round(2)

    # ---- METRIC 4: Strike Rate ----
    # Runs per 100 balls
    batting['strike_rate'] = (
        batting['total_runs'] / batting['balls_faced'] * 100
    ).round(2)

    # ---- METRIC 5: Boundary % ----
    batting['boundary_pct'] = (
        (batting['fours'] + batting['sixes']) /
        batting['balls_faced'] * 100
    ).round(2)

    # ---- METRIC 6: Consistency ----
    # Spread of per-match scores. Lower is steadier; inverted at scoring time.
    match_runs = faced.groupby(
        ['striker', 'match_id'])['runs_off_bat'].sum().reset_index()
    consistency = match_runs.groupby('striker')['runs_off_bat'].std().fillna(0)
    batting = batting.merge(
        consistency.rename('std_dev'), on='striker', how='left'
    )

    # ---- METRIC 7: Powerplay Performance (overs 0-5) ----
    powerplay = faced[faced['over'] <= POWERPLAY_LAST_OVER]
    pp_runs = powerplay.groupby('striker')['runs_off_bat'].sum()
    batting = batting.merge(
        pp_runs.rename('powerplay_runs'), on='striker', how='left'
    )
    batting['powerplay_runs'] = batting['powerplay_runs'].fillna(0)

    # ---- METRIC 8: Death Over Performance (overs 16-19) ----
    death = faced[faced['over'] >= DEATH_FIRST_OVER]
    death_runs = death.groupby('striker')['runs_off_bat'].sum()
    batting = batting.merge(
        death_runs.rename('death_runs'), on='striker', how='left'
    )
    batting['death_runs'] = batting['death_runs'].fillna(0)

    return batting


def calculate_final_score(batting, min_matches=None):
    """Combine all metrics into one batting score out of 100"""
    print("🧮 Calculating final batting scores...")

    min_matches = config.MIN_MATCHES if min_matches is None else min_matches

    # Normalise across the qualified pool only. Scaling against one-match
    # cameos would compress every real career into the bottom of the range.
    batting = batting[batting['matches'] >= min_matches].copy()

    batting['avg_score']         = normalize(batting['average'])
    batting['sr_score']          = normalize(batting['strike_rate'])
    batting['boundary_score']    = normalize(batting['boundary_pct'])
    batting['consistency_score'] = normalize_inverse(batting['std_dev'])
    batting['pp_score']          = normalize(batting['powerplay_runs'])
    batting['death_score']       = normalize(batting['death_runs'])

    # ---- FINAL SCORE: Weighted combination ----
    # Average and Strike Rate matter most
    batting['batting_score'] = (
        batting['avg_score']         * 0.30 +
        batting['sr_score']          * 0.25 +
        batting['boundary_score']    * 0.15 +
        batting['consistency_score'] * 0.15 +
        batting['pp_score']          * 0.075 +
        batting['death_score']       * 0.075
    ).round(2)

    return batting


def show_results(batting):
    """Print the top batsmen rankings"""

    qualified = batting.sort_values(
        'batting_score', ascending=False
    ).reset_index(drop=True)
    qualified.index += 1

    print("\n" + "=" * 70)
    print(f"🏆 TOP BATSMEN — {get_filter_summary()}")
    print("=" * 70)

    display_cols = [
        'striker', 'matches', 'total_runs',
        'average', 'strike_rate',
        'boundary_pct', 'batting_score'
    ]
    print(qualified.head(20)[display_cols].to_string())

    print("\n" + "=" * 70)
    print(f"📊 Total qualified batsmen: {len(qualified)}")
    print("=" * 70)

    os.makedirs("analytics/batting", exist_ok=True)
    output_path = "analytics/batting/batting_scores.csv"
    qualified[display_cols].to_csv(output_path, index=True)
    print(f"\n💾 Full results saved to: {output_path}")


if __name__ == "__main__":
    print("=" * 70)
    print("🏏 CRICKET ANALYTICS — BATTING SCORER")
    print("=" * 70)

    df = load_filtered_data()
    if df is not None:
        batting = calculate_batting_scores(df)
        batting = calculate_final_score(batting)
        show_results(batting)
