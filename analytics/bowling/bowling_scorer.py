# ============================================
# STEP 5 - Bowling Analytics Scorer (Updated)
# Cricket Analytics DevOps Project
# ============================================

import os
import sys
import warnings

import pandas as pd

warnings.filterwarnings('ignore')

sys.path.append(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

from ingestion.data_loader import (BOWLER_WICKET_TYPES, DEATH_FIRST_OVER,
                                   get_filter_summary, load_filtered_data,
                                   normalize, normalize_inverse)
import config

NO_WICKETS_SENTINEL = 999


def calculate_bowling_scores(df):
    """Calculate bowling metrics for every bowler"""
    print("\n⚙️  Calculating bowling scores...")

    # Runs charged to the bowler: off the bat, plus wides and no-balls.
    # Byes and leg byes are the keeper's problem, not the bowler's.
    df = df.copy()
    df['runs_conceded'] = df['runs_off_bat'] + df['wides'] + df['noballs']

    # Only dismissals the bowler actually earns. A run out is not his wicket.
    df['is_bowler_wicket'] = df['wicket_type'].isin(BOWLER_WICKET_TYPES)

    # A dot ball is a legal delivery that costs nothing.
    df['is_dot'] = df['is_legal_ball'] & (
        df['runs_off_bat'] + df['runs_extras'] == 0
    )

    bowling = df.groupby('bowler').agg(
        balls_bowled     = ('is_legal_ball', 'sum'),
        total_runs_given = ('runs_conceded', 'sum'),
        wickets          = ('is_bowler_wicket', 'sum'),
        dot_balls        = ('is_dot', 'sum'),
        matches          = ('match_id', 'nunique'),
    ).reset_index()

    bowling['economy'] = (
        bowling['total_runs_given'] /
        bowling['balls_bowled'] * 6
    ).round(2)

    bowling['bowling_average'] = bowling.apply(
        lambda x: round(x['total_runs_given'] / x['wickets'], 2)
        if x['wickets'] > 0 else NO_WICKETS_SENTINEL, axis=1
    )

    bowling['bowling_sr'] = bowling.apply(
        lambda x: round(x['balls_bowled'] / x['wickets'], 2)
        if x['wickets'] > 0 else NO_WICKETS_SENTINEL, axis=1
    )

    bowling['dot_ball_pct'] = (
        bowling['dot_balls'] / bowling['balls_bowled'] * 100
    ).round(2)

    # ---- Death over economy (overs 16-19) ----
    death = df[df['over'] >= DEATH_FIRST_OVER]
    death_bowling = death.groupby('bowler').agg(
        death_balls = ('is_legal_ball', 'sum'),
        death_runs  = ('runs_conceded', 'sum'),
    ).reset_index()
    death_bowling['death_economy'] = (
        death_bowling['death_runs'] /
        death_bowling['death_balls'] * 6
    ).round(2)

    bowling = bowling.merge(
        death_bowling[['bowler', 'death_economy']], on='bowler', how='left'
    )
    # A bowler who never bowled at the death is judged on his overall economy.
    bowling['death_economy'] = bowling['death_economy'].fillna(
        bowling['economy']
    )

    # ---- Consistency: spread of wickets per match ----
    match_wickets = df.groupby(
        ['bowler', 'match_id']
    )['is_bowler_wicket'].sum().reset_index(name='wickets_in_match')
    consistency = match_wickets.groupby(
        'bowler')['wickets_in_match'].std().fillna(0)
    bowling = bowling.merge(
        consistency.rename('wicket_consistency'), on='bowler', how='left'
    )

    return bowling


def calculate_final_score(bowling, min_matches=None):
    print("🧮 Calculating final bowling scores...")

    min_matches = config.MIN_MATCHES if min_matches is None else min_matches

    # Rank within the qualified pool so the 999 sentinel and one-over cameos
    # cannot stretch the normalisation range.
    bowling = bowling[bowling['matches'] >= min_matches].copy()

    bowling['economy_score']     = normalize_inverse(bowling['economy'])
    bowling['sr_score']          = normalize_inverse(bowling['bowling_sr'])
    bowling['dot_score']         = normalize(bowling['dot_ball_pct'])
    bowling['death_score']       = normalize_inverse(bowling['death_economy'])
    bowling['consistency_score'] = normalize_inverse(
        bowling['wicket_consistency'])

    bowling['bowling_score'] = (
        bowling['economy_score']     * 0.30 +
        bowling['sr_score']          * 0.25 +
        bowling['dot_score']         * 0.20 +
        bowling['death_score']       * 0.15 +
        bowling['consistency_score'] * 0.10
    ).round(2)

    return bowling


def show_results(bowling):
    qualified = bowling.sort_values(
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
