# ============================================
# STEP 4 - Batting Analytics Scorer
# Cricket Analytics DevOps Project
# ============================================

import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

# ---- Path to your raw data folder ----
DATA_FOLDER = "data/raw"

def load_all_matches(folder):
    """Load all CSV match files into one big table"""
    all_files = [f for f in os.listdir(folder) if f.endswith('.csv') and '_info' not in f]
    print(f"📂 Found {len(all_files)} match files...")

    all_data = []
    for file in all_files:
        filepath = os.path.join(folder, file)
        try:
            df = pd.read_csv(filepath)
            all_data.append(df)
        except Exception as e:
            print(f"⚠️  Skipping {file}: {e}")

    combined = pd.concat(all_data, ignore_index=True)
    print(f"✅ Loaded {len(combined)} total balls across all matches!")
    return combined

def calculate_batting_scores(df):
    """Calculate batting metrics for every batsman"""
    print("\n⚙️  Calculating batting scores...")

    # ---- METRIC 1: Basic runs and balls ----
    batting = df.groupby('striker').agg(
        total_runs    = ('runs_off_bat', 'sum'),
        balls_faced   = ('runs_off_bat', 'count'),
        dismissals    = ('player_dismissed', lambda x: x.notna().sum()),
        fours         = ('runs_off_bat', lambda x: (x == 4).sum()),
        sixes         = ('runs_off_bat', lambda x: (x == 6).sum()),
        matches       = ('match_id', 'nunique')
    ).reset_index()

    # ---- METRIC 2: Batting Average ----
    # Runs scored divided by number of times out
    batting['average'] = batting.apply(
        lambda x: x['total_runs'] / x['dismissals'] 
        if x['dismissals'] > 0 else x['total_runs'], axis=1
    ).round(2)

    # ---- METRIC 3: Strike Rate ----
    # Runs per 100 balls
    batting['strike_rate'] = (
        batting['total_runs'] / batting['balls_faced'] * 100
    ).round(2)

    # ---- METRIC 4: Boundary % ----
    # How many balls went to boundary
    batting['boundary_pct'] = (
        (batting['fours'] + batting['sixes']) / 
        batting['balls_faced'] * 100
    ).round(2)

    # ---- METRIC 5: Consistency Score ----
    # How regularly they score across matches
    match_runs = df.groupby(
        ['striker', 'match_id'])['runs_off_bat'].sum().reset_index()
    consistency = match_runs.groupby('striker')['runs_off_bat'].std().fillna(0)
    batting = batting.merge(
        consistency.rename('std_dev'), 
        on='striker', how='left'
    )
    # Lower std_dev = more consistent. We invert it.
    batting['consistency_score'] = (
        100 / (1 + batting['std_dev'])
    ).round(2)

    # ---- METRIC 6: Powerplay Performance ----
    # Balls 0.1 to 6.6 = powerplay
    powerplay = df[df['ball'] <= 6.6]
    pp_runs = powerplay.groupby('striker')['runs_off_bat'].sum()
    batting = batting.merge(
        pp_runs.rename('powerplay_runs'),
        on='striker', how='left'
    ).fillna(0)

    # ---- METRIC 7: Death Over Performance ----
    # Balls 16.1 to 20.6 = death overs
    death = df[df['ball'] >= 16.1]
    death_runs = death.groupby('striker')['runs_off_bat'].sum()
    batting = batting.merge(
        death_runs.rename('death_runs'),
        on='striker', how='left'
    ).fillna(0)

    return batting

def calculate_final_score(batting):
    """Combine all metrics into one batting score out of 100"""
    print("🧮 Calculating final batting scores...")

    def normalize(series):
        """Scale any number to 0-100"""
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val:
            return series * 0
        return ((series - min_val) / (max_val - min_val) * 100).round(2)

    # Normalize each metric to 0-100
    batting['avg_score']      = normalize(batting['average'])
    batting['sr_score']       = normalize(batting['strike_rate'])
    batting['boundary_score'] = normalize(batting['boundary_pct'])
    batting['pp_score']       = normalize(batting['powerplay_runs'])
    batting['death_score']    = normalize(batting['death_runs'])

    # ---- FINAL SCORE: Weighted combination ----
    # Average and Strike Rate matter most
    batting['batting_score'] = (
        batting['avg_score']        * 0.30 +
        batting['sr_score']         * 0.25 +
        batting['boundary_score']   * 0.15 +
        batting['consistency_score']* 0.15 +
        batting['pp_score']         * 0.075 +
        batting['death_score']      * 0.075
    ).round(2)

    return batting

def show_results(batting):
    """Print the top batsmen rankings"""

    # Filter: minimum 10 matches to qualify
    qualified = batting[batting['matches'] >= 20].copy()
    qualified = qualified.sort_values(
        'batting_score', ascending=False
    ).reset_index(drop=True)
    qualified.index += 1

    print("\n" + "=" * 70)
    print("🏆 TOP BATSMEN RANKINGS — CRICKET ANALYTICS")
    print("=" * 70)

    # Show top 20
    top20 = qualified.head(20)
    display_cols = [
        'striker', 'matches', 'total_runs',
        'average', 'strike_rate', 
        'boundary_pct', 'batting_score'
    ]
    print(top20[display_cols].to_string())

    print("\n" + "=" * 70)
    print(f"📊 Total qualified batsmen: {len(qualified)}")
    print("=" * 70)

    # Save results to CSV
    output_path = "analytics/batting/batting_scores.csv"
    qualified[display_cols].to_csv(output_path, index=True)
    print(f"\n💾 Full results saved to: {output_path}")

if __name__ == "__main__":
    print("=" * 70)
    print("🏏 CRICKET ANALYTICS — BATTING SCORER")
    print("=" * 70)

    # Step 1: Load all match data
    df = load_all_matches(DATA_FOLDER)

    # Step 2: Calculate metrics
    batting = calculate_batting_scores(df)

    # Step 3: Calculate final score
    batting = calculate_final_score(batting)

    # Step 4: Show results
    show_results(batting)