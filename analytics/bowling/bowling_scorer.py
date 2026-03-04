# ============================================
# STEP 5 - Bowling Analytics Scorer (Updated)
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

def calculate_bowling_scores(df):
    """Calculate bowling metrics for every bowler"""
    print("\n⚙️  Calculating bowling scores...")

    bowling = df.groupby('bowler').agg(
        balls_bowled  = ('runs_off_bat', 'count'),
        runs_given    = ('runs_off_bat', 'sum'),
        wickets       = ('wicket_type', lambda x: x.notna().sum()),
        dot_balls     = ('runs_off_bat', lambda x: (x == 0).sum()),
        matches       = ('match_id', 'nunique'),
        wides         = ('wides', lambda x: (x > 0).sum()),
        noballs       = ('noballs', lambda x: (x > 0).sum())
    ).reset_index()

    bowling['total_runs_given'] = (
        bowling['runs_given'] +
        bowling['wides'] +
        bowling['noballs']
    )

    bowling['economy'] = (
        bowling['total_runs_given'] /
        bowling['balls_bowled'] * 6
    ).round(2)

    bowling['bowling_average'] = bowling.apply(
        lambda x: x['total_runs_given'] / x['wickets']
        if x['wickets'] > 0 else 999, axis=1
    ).round(2)

    bowling['bowling_sr'] = bowling.apply(
        lambda x: x['balls_bowled'] / x['wickets']
        if x['wickets'] > 0 else 999, axis=1
    ).round(2)

    bowling['dot_ball_pct'] = (
        bowling['dot_balls'] / bowling['balls_bowled'] * 100
    ).round(2)

    # Death over economy
    death = df[df['ball'] >= 16.1]
    death_bowling = death.groupby('bowler').agg(
        death_balls = ('runs_off_bat', 'count'),
        death_runs  = ('runs_off_bat', 'sum')
    ).reset_index()
    death_bowling['death_economy'] = (
        death_bowling['death_runs'] /
        death_bowling['death_balls'] * 6
    ).round(2)

    bowling = bowling.merge(
        death_bowling[['bowler', 'death_economy']],
        on='bowler', how='left'
    ).fillna(bowling['economy'])

    # Consistency
    match_wickets = df.groupby(
        ['bowler', 'match_id']
    )['wicket_type'].apply(
        lambda x: x.notna().sum()
    ).reset_index()
    match_wickets.columns = ['bowler', 'match_id', 'wickets_in_match']
    consistency = match_wickets.groupby(
        'bowler')['wickets_in_match'].std().fillna(0)
    bowling = bowling.merge(
        consistency.rename('wicket_consistency'),
        on='bowler', how='left'
    )
    bowling['consistency_score'] = (
        100 / (1 + bowling['wicket_consistency'])
    ).round(2)

    return bowling

def calculate_final_score(bowling):
    print("🧮 Calculating final bowling scores...")

    def normalize_inverse(series):
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val:
            return series * 0
        return ((max_val - series) / (max_val - min_val) * 100).round(2)

    def normalize(series):
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val:
            return series * 0
        return ((series - min_val) / (max_val - min_val) * 100).round(2)

    bowling['economy_score']  = normalize_inverse(bowling['economy'])
    bowling['sr_score']       = normalize_inverse(bowling['bowling_sr'])
    bowling['dot_score']      = normalize(bowling['dot_ball_pct'])
    bowling['death_score']    = normalize_inverse(bowling['death_economy'])

    bowling['bowling_score'] = (
        bowling['economy_score']      * 0.30 +
        bowling['sr_score']           * 0.25 +
        bowling['dot_score']          * 0.20 +
        bowling['death_score']        * 0.15 +
        bowling['consistency_score']  * 0.10
    ).round(2)

    return bowling

def show_results(bowling):
    qualified = bowling[
        bowling['matches'] >= config.MIN_MATCHES
    ].copy()
    qualified = qualified.sort_values(
        'bowling_score', ascending=False
    ).reset_index(drop=True)
    qualified.index += 1

    print("\n" + "=" * 75)
    print(f"🏆 TOP BOWLERS — {get_filter_summary()}")
    print("=" * 75)

    display_cols = [
        'bowler', 'matches', 'wickets',
        'economy', 'bowling_sr',
        'dot_ball_pct', 'bowling_score'
    ]
    print(qualified.head(20)[display_cols].to_string())
    print("\n" + "=" * 75)
    print(f"📊 Total qualified bowlers: {len(qualified)}")
    print("=" * 75)

    os.makedirs("analytics/bowling", exist_ok=True)
    output_path = "analytics/bowling/bowling_scores.csv"
    qualified[display_cols].to_csv(output_path, index=True)
    print(f"\n💾 Saved to: {output_path}")

if __name__ == "__main__":
    print("=" * 75)
    print("🏏 CRICKET ANALYTICS — BOWLING SCORER")
    print("=" * 75)
    df = load_filtered_data()
    if df is not None:
        bowling = calculate_bowling_scores(df)
        bowling = calculate_final_score(bowling)
        show_results(bowling)