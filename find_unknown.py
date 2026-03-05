import sys, os
sys.path.insert(0, os.getcwd())

import pandas as pd

# Paste PLAYER_TEAMS directly - no import needed
from dashboard.ipl_teams import PLAYER_TEAMS

files = {
    "batting":    "analytics/batting/batting_scores.csv",
    "bowling":    "analytics/bowling/bowling_scores.csv",
    "allrounder": "analytics/allrounder/allrounder_scores.csv"
}

unknown = set()
for key, path in files.items():
    df  = pd.read_csv(path)
    col = "striker" if "striker" in df.columns else \
          "bowler"  if "bowler"  in df.columns else "player"
    for name in df[col].tolist():
        if name not in PLAYER_TEAMS:
            unknown.add(name)

print(f"\nTotal unknown players: {len(unknown)}")
for p in sorted(unknown):
    print(f"  '{p}'")