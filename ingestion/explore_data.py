# ============================================
# STEP 3 - Explore Cricket Data
# Cricket Analytics DevOps Project
# ============================================

import pandas as pd
import os

# ---- CHANGE THIS to any csv filename in your data/raw folder ----
MATCH_FILE = "data/raw/335982.csv"

def explore_match(filepath):
    print("=" * 60)
    print("🏏 CRICKET ANALYTICS - DATA EXPLORER")
    print("=" * 60)

    # Load the CSV file into a table (called DataFrame)
    df = pd.read_csv(filepath)

    # Basic info
    print(f"\n📁 File: {filepath}")
    print(f"📊 Total balls bowled: {len(df)}")
    print(f"📋 Columns available: {len(df.columns)}")

    # Show all column names
    print("\n📌 DATA COLUMNS:")
    for col in df.columns:
        print(f"   → {col}")

    # Show first 5 balls of the match
    print("\n🔍 FIRST 5 BALLS OF THE MATCH:")
    print(df[['innings', 'ball', 'striker', 
               'bowler', 'runs_off_bat', 
               'extras', 'wicket_type']].head())

    # Show teams playing
    print("\n🏟️  TEAMS IN THIS MATCH:")
    teams = df['batting_team'].unique()
    for team in teams:
        print(f"   → {team}")

    # Show all batsmen who played
    print("\n🏏 BATSMEN WHO PLAYED:")
    batsmen = df['striker'].unique()
    for b in batsmen:
        print(f"   → {b}")

    # Show all bowlers who played
    print("\n⚾ BOWLERS WHO BOWLED:")
    bowlers = df['bowler'].unique()
    for b in bowlers:
        print(f"   → {b}")

    # Quick batting summary
    print("\n📈 QUICK BATTING SUMMARY (runs per batsman):")
    batting = df.groupby('striker')['runs_off_bat'].sum()
    batting = batting.sort_values(ascending=False)
    print(batting.to_string())

    print("\n" + "=" * 60)
    print("✅ Data loaded successfully! Ready for analytics.")
    print("=" * 60)

if __name__ == "__main__":
    explore_match(MATCH_FILE)