# ============================================
# STEP 6A - Fielding Analytics Scorer (Fixed)
# Cricket Analytics DevOps Project
# ============================================

import os
import sys
import warnings

import pandas as pd

warnings.filterwarnings('ignore')

sys.path.append(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

from ingestion.data_loader import (get_filter_summary, load_filtered_data,
                                   normalize, player_match_counts)
import config


def _credit_fielders(df, wicket_type):
    """
    Count dismissals of one type per fielder.

    csv2 records who took the catch or effected the run out in fielder_1 /
    fielder_2 — a run out often involves two players and both get credit.
    Grouping on 'bowler' instead, as this script used to, hands every catch
    to whoever was bowling.
    """
    rows = df[df['wicket_type'] == wicket_type]
    if rows.empty:
        return pd.DataFrame(columns=['player', 'count'])

    fielders = pd.concat(
        [rows['fielder_1'], rows['fielder_2']], ignore_index=True
    ).dropna()
    if fielders.empty:
        return pd.DataFrame(columns=['player', 'count'])

    return (
        fielders.value_counts()
        .rename_axis('player').reset_index(name='count')
    )


def calculate_fielding_scores(df):
    print("\n⚙️  Calculating fielding scores...")

    # Every player who appeared in any role, so specialist bowlers and
    # fielders are not dropped for never having batted.
    fielding = player_match_counts(df)

    # ---- CATCHES ---- credited to the fielder who took it
    catches = _credit_fielders(df, 'caught').rename(
        columns={'count': 'catches'})

    # ---- RUN OUTS ---- credited to the fielder(s) involved
    runouts = _credit_fielders(df, 'run out').rename(
        columns={'count': 'run_outs'})

    # ---- BOWLED ---- the one credit that genuinely belongs to the bowler
    bowled = (
        df[df['wicket_type'] == 'bowled']
        .groupby('bowler').size()
        .rename('bowled_wickets').rename_axis('player').reset_index()
    )

    for part in (catches, runouts, bowled):
        fielding = fielding.merge(part, on='player', how='left')

    for col in ['catches', 'run_outs', 'bowled_wickets']:
        fielding[col] = fielding[col].fillna(0).astype('int64')

    fielding['total_contributions'] = (
        fielding['catches'] +
        fielding['run_outs'] +
        fielding['bowled_wickets']
    )

    fielding['contributions_per_match'] = (
        fielding['total_contributions'] /
        fielding['matches'].replace(0, 1)
    ).round(3)

    return fielding


def calculate_final_score(fielding, min_matches=None):
    print("🧮 Calculating final fielding scores...")

    min_matches = config.MIN_MATCHES if min_matches is None else min_matches
    fielding = fielding[fielding['matches'] >= min_matches].copy()

    fielding['catch_score']  = normalize(fielding['catches'])
    fielding['runout_score'] = normalize(fielding['run_outs'])
    fielding['bowled_score'] = normalize(fielding['bowled_wickets'])

    # Catches 50% + Run outs 30% + Bowled 20%
    fielding['fielding_score'] = (
        fielding['catch_score']  * 0.50 +
        fielding['runout_score'] * 0.30 +
        fielding['bowled_score'] * 0.20
    ).round(2)

    return fielding


def show_results(fielding):
    qualified = fielding.sort_values(
        'fielding_score', ascending=False
    ).reset_index(drop=True)
    qualified.index += 1

    print("\n" + "=" * 70)
    print(f"🏆 TOP FIELDERS — {get_filter_summary()}")
    print("=" * 70)

    display_cols = [
        'player', 'matches', 'catches',
        'run_outs', 'bowled_wickets',
        'contributions_per_match', 'fielding_score'
    ]
    print(qualified.head(20)[display_cols].to_string())
    print("\n" + "=" * 70)
    print(f"📊 Total qualified players: {len(qualified)}")
    print("=" * 70)

    os.makedirs("analytics/fielding", exist_ok=True)
    output_path = "analytics/fielding/fielding_scores.csv"
    qualified[display_cols].to_csv(output_path, index=True)
    print(f"\n💾 Saved to: {output_path}")


if __name__ == "__main__":
    print("=" * 70)
    print("🏏 CRICKET ANALYTICS — FIELDING SCORER")
    print("=" * 70)
    df = load_filtered_data()
    if df is not None:
        fielding = calculate_fielding_scores(df)
        fielding = calculate_final_score(fielding)
        show_results(fielding)
