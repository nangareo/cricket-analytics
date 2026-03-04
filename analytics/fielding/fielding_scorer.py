# ============================================
# STEP 6A - Fielding Analytics Scorer (Fixed)
# Cricket Analytics DevOps Project
# ============================================

import pandas as pd
import os
import sys
import warnings
warnings.filterwarnings('ignore')

sys.path.append(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

from ingestion.data_loader import load_filtered_data, get_filter_summary
import config

def calculate_fielding_scores(df):
    print("\n⚙️  Calculating fielding scores...")

    # ---- All players who batted (to get match counts) ----
    matches_played = df.groupby(
        'striker')['match_id'].nunique().reset_index()
    matches_played.columns = ['player', 'matches']

    # ---- CATCHES ----
    # When wicket_type is 'caught', bowler's team fielded
    # We use bowling_team as proxy for fielding
    catches = df[df['wicket_type'] == 'caught']
    catch_counts = catches.groupby(
        'bowler')['match_id'].count().reset_index()
    catch_counts.columns = ['player', 'catches']

    # ---- RUN OUTS ----
    runouts = df[df['wicket_type'] == 'run out']
    runout_counts = runouts.groupby(
        'bowler')['match_id'].count().reset_index()
    runout_counts.columns = ['player', 'run_outs']

    # ---- BOWLED (direct wicket credit) ----
    bowled = df[df['wicket_type'] == 'bowled']
    bowled_counts = bowled.groupby(
        'bowler')['match_id'].count().reset_index()
    bowled_counts.columns = ['player', 'bowled_wickets']

    # ---- Combine all fielding stats ----
    fielding = catch_counts.merge(
        runout_counts,  on='player', how='outer'
    ).merge(
        bowled_counts,  on='player', how='outer'
    ).merge(
        matches_played, on='player', how='left'
    ).fillna(0)

    # ---- Total fielding contributions ----
    fielding['total_contributions'] = (
        fielding['catches'] +
        fielding['run_outs'] +
        fielding['bowled_wickets']
    )

    # ---- Contributions per match ----
    fielding['contributions_per_match'] = (
        fielding['total_contributions'] /
        fielding['matches'].replace(0, 1)
    ).round(3)

    return fielding

def calculate_final_score(fielding):
    print("🧮 Calculating final fielding scores...")

    def normalize(series):
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val:
            return series * 0
        return ((series - min_val) /
                (max_val - min_val) * 100).round(2)

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
    qualified = fielding[
        fielding['matches'] >= config.MIN_MATCHES
    ].copy()
    qualified = qualified.sort_values(
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