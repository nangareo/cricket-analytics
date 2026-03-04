# ============================================
# STEP 6B - All-rounder Analytics Scorer (Updated)
# Cricket Analytics DevOps Project
# ============================================

import pandas as pd
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

from ingestion.data_loader import get_filter_summary
import config

def load_scores():
    """Load all three scorer outputs"""
    print("📂 Loading batting, bowling and fielding scores...")

    # Check all three files exist first
    files = {
        "batting":  "analytics/batting/batting_scores.csv",
        "bowling":  "analytics/bowling/bowling_scores.csv",
        "fielding": "analytics/fielding/fielding_scores.csv"
    }

    for name, path in files.items():
        if not os.path.exists(path):
            print(f"❌ Missing: {path}")
            print(f"   Please run {name}_scorer.py first!")
            sys.exit(1)

    batting = pd.read_csv(
        files["batting"]
    ).rename(columns={'striker': 'player'})

    bowling = pd.read_csv(
        files["bowling"]
    ).rename(columns={'bowler': 'player'})

    fielding = pd.read_csv(files["fielding"])

    print(f"✅ Batting:  {len(batting)} players loaded")
    print(f"✅ Bowling:  {len(bowling)} players loaded")
    print(f"✅ Fielding: {len(fielding)} players loaded")

    return batting, bowling, fielding

def calculate_allrounder_score(batting, bowling, fielding):
    """Combine batting + bowling + fielding into one score"""
    print("\n🧮 Calculating all-rounder scores...")

    # Must have BOTH batting AND bowling records
    allrounder = batting[[
        'player', 'batting_score', 'matches',
        'total_runs', 'average', 'strike_rate'
    ]].merge(
        bowling[[
            'player', 'bowling_score',
            'wickets', 'economy', 'dot_ball_pct'
        ]],
        on='player', how='inner'
    ).merge(
        fielding[['player', 'fielding_score', 'catches', 'run_outs']],
        on='player', how='left'
    ).fillna(0)

    # ---- ALL-ROUNDER FORMULA ----
    # Batting 45% + Bowling 45% + Fielding 10%
    allrounder['allrounder_score'] = (
        allrounder['batting_score']  * 0.45 +
        allrounder['bowling_score']  * 0.45 +
        allrounder['fielding_score'] * 0.10
    ).round(2)

    return allrounder

def show_results(allrounder):
    """Print top all-rounders ranking"""

    qualified = allrounder[
        allrounder['matches'] >= config.MIN_MATCHES
    ].sort_values(
        'allrounder_score', ascending=False
    ).reset_index(drop=True)
    qualified.index += 1

    print("\n" + "=" * 80)
    print(f"🏆 TOP ALL-ROUNDERS — {get_filter_summary()}")
    print("=" * 80)

    display_cols = [
        'player', 'matches',
        'total_runs', 'average', 'strike_rate',
        'wickets', 'economy',
        'batting_score', 'bowling_score',
        'fielding_score', 'allrounder_score'
    ]
    print(qualified.head(20)[display_cols].to_string())

    print("\n" + "=" * 80)
    print(f"📊 Total qualified all-rounders: {len(qualified)}")
    print("=" * 80)

    os.makedirs("analytics/allrounder", exist_ok=True)
    output_path = "analytics/allrounder/allrounder_scores.csv"
    qualified[display_cols].to_csv(output_path, index=True)
    print(f"\n💾 Saved to: {output_path}")

if __name__ == "__main__":
    print("=" * 80)
    print("🏏 CRICKET ANALYTICS — ALL-ROUNDER SCORER")
    print("=" * 80)
    batting, bowling, fielding = load_scores()
    allrounder = calculate_allrounder_score(batting, bowling, fielding)
    show_results(allrounder)