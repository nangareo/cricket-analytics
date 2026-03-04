# ============================================
# SHARED DATA LOADER
# Reads filter from selector and applies it
# ============================================

import pandas as pd
import os
import sys
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

FILTER_CACHE = "data/selected_filter.json"

def get_active_seasons():
    """Read the filter selected by user"""
    if os.path.exists(FILTER_CACHE):
        with open(FILTER_CACHE, 'r') as f:
            saved = json.load(f)
            value = saved.get('value')
            if value == 'all' or value is None:
                return None
            return value
    return None

def load_filtered_data():
    """Load all match data with active filters applied"""
    folder   = config.DATA_FOLDER
    seasons  = get_active_seasons()
    all_files = [f for f in os.listdir(folder)
                 if f.endswith('.csv') and '_info' not in f]

    print(f"\n📂 Found {len(all_files)} total match files")

    if seasons:
        print(f"🔍 Filtering to seasons: {', '.join(seasons)}")
    else:
        print(f"🔍 Loading All Time data (2008-2025)")

    all_data = []
    skipped  = 0

    for file in all_files:
        try:
            df = pd.read_csv(os.path.join(folder, file))

            # ---- Apply season filter ----
            if seasons and 'season' in df.columns:
                df['season'] = df['season'].astype(str)
                df = df[df['season'].isin(seasons)]

            elif seasons and 'start_date' in df.columns:
                df['year'] = pd.to_datetime(
                    df['start_date'], errors='coerce'
                ).dt.year.astype(str)
                df = df[df['year'].isin(seasons)]

            if len(df) == 0:
                skipped += 1
                continue

            all_data.append(df)

        except:
            skipped += 1

    if not all_data:
        print("❌ No data found for selected filter!")
        return None

    combined = pd.concat(all_data, ignore_index=True)

    # ---- Remove retired players ----
    retired = config.RETIRED_PLAYERS
    before  = len(combined)
    combined = combined[~combined['striker'].isin(retired)]
    combined = combined[~combined['bowler'].isin(retired)]
    after   = len(combined)

    print(f"✅ {after:,} balls loaded")
    print(f"   → {skipped} files skipped")
    print(f"   → {before - after:,} balls removed (retired players)")

    return combined

def get_filter_summary():
    """Returns active filter as readable string"""
    seasons = get_active_seasons()
    if not seasons:
        return "All Time (2008-2025)"
    if len(seasons) == 1:
        return f"IPL {seasons[0]}"
    return f"IPL {seasons[0]} to {seasons[-1]}"