"""
MASTER FILE WRITER
Writes all 3 files needed for the upgraded dashboard
Run from: Desktop/cricket-analytics
"""
import os, sys

# ── 1. Write ipl_teams.py ────────────────────────────
print("Writing dashboard/ipl_teams.py ...")
ipl_code = open(os.path.join(os.path.dirname(__file__),
                             "ipl_teams_content.py"), encoding="utf-8").read()
os.makedirs("dashboard", exist_ok=True)
with open("dashboard/ipl_teams.py", "w", encoding="utf-8") as f:
    f.write(ipl_code)
print(f"  ✅ ipl_teams.py — {ipl_code.count(chr(10))} lines")

# ── 2. Write team_analytics.py ───────────────────────
print("Writing analytics/team_analytics.py ...")
# inline content
ta_code = '''
import pandas as pd, os, sys
sys.path.insert(0, os.getcwd())
from dashboard.ipl_teams import PLAYER_TEAMS, IPL_TEAMS, RETIRED_PLAYERS, get_team_color, get_team_info, avatar_html

def get_team_players(team_name, scores):
    players = {"batting":[], "bowling":[], "allrounder":[]}
    for dtype, sc in [("batting","batting_score"),("bowling","bowling_score"),("allrounder","allrounder_score")]:
        if scores[dtype] is None: continue
        df   = scores[dtype].copy()
        pcol = "striker" if "striker" in df.columns else "bowler" if "bowler" in df.columns else "player"
        df   = df.rename(columns={pcol:"player"})
        players[dtype] = df[df["player"].apply(lambda x: PLAYER_TEAMS.get(x)==team_name and x not in RETIRED_PLAYERS)].sort_values(sc, ascending=False).to_dict("records")
    return players

def calculate_team_stats(team_name, scores, min_matches=10):
    players = get_team_players(team_name, scores)
    stats   = {}
    if players["batting"]:
        df = pd.DataFrame(players["batting"])
        df = df[df["matches"] >= min_matches]
        if not df.empty:
            stats.update({"avg_batting_score":df["batting_score"].mean().round(1),
                "avg_strike_rate":df["strike_rate"].mean().round(1),
                "avg_average":df["average"].mean().round(1),
                "total_runs":int(df["total_runs"].sum()),
                "top_scorer":df.iloc[0]["player"],
                "top_bat_score":df.iloc[0]["batting_score"],
                "bat_depth":len(df)})
    if players["bowling"]:
        df = pd.DataFrame(players["bowling"])
        df = df[df["matches"] >= min_matches]
        if not df.empty:
            stats.update({"avg_bowling_score":df["bowling_score"].mean().round(1),
                "avg_economy":df["economy"].mean().round(2),
                "avg_dot_ball_pct":df["dot_ball_pct"].mean().round(1),
                "total_wickets":int(df["wickets"].sum()),
                "top_bowler":df.iloc[0]["player"],
                "top_bowl_score":df.iloc[0]["bowling_score"],
                "bowl_depth":len(df)})
    if players["allrounder"]:
        df = pd.DataFrame(players["allrounder"])
        df = df[df["matches"] >= min_matches]
        if not df.empty:
            stats.update({"avg_ar_score":df["allrounder_score"].mean().round(1),
                "top_allrounder":df.iloc[0]["player"],"ar_depth":len(df)})
    return stats

def generate_swot(team_name, stats, opp_stats):
    swot = {"strengths":[],"weaknesses":[],"opportunities":[],"threats":[]}
    if stats.get("avg_batting_score",0) > opp_stats.get("avg_batting_score",0):
        swot["strengths"].append(f"Superior batting — avg {stats.get(\'avg_batting_score\',0)} vs opp {opp_stats.get(\'avg_batting_score\',0)}")
    if stats.get("avg_economy",999) < opp_stats.get("avg_economy",999):
        swot["strengths"].append(f"Better bowling economy — {stats.get(\'avg_economy\',0)} vs opp {opp_stats.get(\'avg_economy\',0)}")
    if stats.get("avg_dot_ball_pct",0) > opp_stats.get("avg_dot_ball_pct",0):
        swot["strengths"].append(f"Higher dot ball % — {stats.get(\'avg_dot_ball_pct\',0)}% vs {opp_stats.get(\'avg_dot_ball_pct\',0)}%")
    if stats.get("avg_strike_rate",0) > opp_stats.get("avg_strike_rate",0):
        swot["strengths"].append(f"Faster scoring — SR {stats.get(\'avg_strike_rate\',0)} vs {opp_stats.get(\'avg_strike_rate\',0)}")
    if stats.get("ar_depth",0) > opp_stats.get("ar_depth",0):
        swot["strengths"].append(f"More all-rounders — {stats.get(\'ar_depth\',0)} vs {opp_stats.get(\'ar_depth\',0)}")
    if stats.get("avg_batting_score",0) < opp_stats.get("avg_batting_score",0):
        swot["weaknesses"].append(f"Weaker batting — avg score {stats.get(\'avg_batting_score\',0)}")
    if stats.get("avg_economy",0) > opp_stats.get("avg_economy",0):
        swot["weaknesses"].append(f"Higher economy — {stats.get(\'avg_economy\',0)}")
    if stats.get("bat_depth",0) < opp_stats.get("bat_depth",0):
        swot["weaknesses"].append(f"Thin batting depth — {stats.get(\'bat_depth\',0)} qualified batters")
    if stats.get("bowl_depth",0) < opp_stats.get("bowl_depth",0):
        swot["weaknesses"].append(f"Limited bowling options — {stats.get(\'bowl_depth\',0)} bowlers")
    if stats.get("avg_strike_rate",0) > 140:
        swot["opportunities"].append("Explosive batting — ideal for powerplay dominance")
    if stats.get("avg_dot_ball_pct",0) > 40:
        swot["opportunities"].append("High dot ball % — can strangle middle-over scoring")
    if stats.get("ar_depth",0) >= 2:
        swot["opportunities"].append(f"Multiple all-rounders provide tactical flexibility")
    if opp_stats.get("avg_batting_score",0) < 30:
        swot["opportunities"].append("Opponent batting is vulnerable to aggressive bowling")
    swot["opportunities"].append(f"Top scorer {stats.get(\'top_scorer\',\'\')} can be match-winning")
    if opp_stats.get("avg_bowling_score",0) > stats.get("avg_batting_score",0):
        swot["threats"].append(f"Opponent bowling attack is superior")
    if opp_stats.get("avg_strike_rate",0) > 140:
        swot["threats"].append(f"Opponent scores at SR {opp_stats.get(\'avg_strike_rate\',0)} — difficult to contain")
    if opp_stats.get("top_scorer",""):
        swot["threats"].append(f"{opp_stats.get(\'top_scorer\',\'\')} is a match-winner — dismiss early")
    if opp_stats.get("ar_depth",0) >= 2:
        swot["threats"].append("Opponent all-rounders provide extra bowling cover")
    defaults = {
        "strengths":["Home advantage can boost morale","Squad experience in pressure matches"],
        "weaknesses":["Consistency across departments needs work","Middle-order reliability is a concern"],
        "opportunities":["Early wickets in powerplay can shift momentum","High fielding intensity can create run-outs"],
        "threats":["Opponent captain has strong tactical awareness","Dew factor may aid opponent in 2nd innings"]
    }
    for key in swot:
        while len(swot[key]) < 2:
            idx = len(swot[key])
            if idx < len(defaults[key]): swot[key].append(defaults[key][idx])
            else: break
    return swot

def get_player_matchups(team1, team2, scores):
    matchups = []
    if scores["batting"] is None or scores["bowling"] is None: return []
    bat_df  = scores["batting"].copy()
    bowl_df = scores["bowling"].copy()
    bpc = "striker" if "striker" in bat_df.columns else "player"
    wpc = "bowler"  if "bowler"  in bowl_df.columns else "player"
    t1b = bat_df[bat_df[bpc].apply(lambda x: PLAYER_TEAMS.get(x)==team1 and x not in RETIRED_PLAYERS)].sort_values("batting_score",ascending=False).head(5)
    t2w = bowl_df[bowl_df[wpc].apply(lambda x: PLAYER_TEAMS.get(x)==team2 and x not in RETIRED_PLAYERS)].sort_values("bowling_score",ascending=False).head(5)
    for _,bat in t1b.iterrows():
        for _,bowl in t2w.iterrows():
            bn,wn = bat[bpc],bowl[wpc]
            sr,ec = bat.get("strike_rate",0),bowl.get("economy",0)
            if sr>140 and ec>8: adv,edge="batter",f"SR {sr:.0f} vs Econ {ec:.2f}"
            elif sr<120 and ec<7: adv,edge="bowler",f"Econ {ec:.2f} vs SR {sr:.0f}"
            else: adv,edge="neutral",f"SR {sr:.0f} vs Econ {ec:.2f}"
            matchups.append({"batter":bn,"bowler":wn,"bat_score":bat.get("batting_score",0),
                "bowl_score":bowl.get("bowling_score",0),"bat_sr":sr,"bowl_econ":ec,
                "advantage":adv,"edge":edge})
    return matchups[:10]

def get_best_xi_vs_opponent(team_name, opp_name, scores, min_matches=10):
    players   = get_team_players(team_name, scores)
    opp_stats = calculate_team_stats(opp_name, scores, min_matches)
    xi, added = [], set()
    opp_bowl_strong = opp_stats.get("avg_bowling_score",50) > 50
    sort_col = "average" if opp_bowl_strong else "strike_rate"
    if players["batting"]:
        bat_df = pd.DataFrame(players["batting"])
        bat_df = bat_df[bat_df["matches"]>=min_matches]
        if not bat_df.empty and sort_col in bat_df.columns:
            bat_df = bat_df.sort_values(sort_col, ascending=False)
        wk_opts = ["MS Dhoni","RR Pant","SV Samson","Sanju Samson","Q de Kock","Quinton de Kock","KD Karthik","Dinesh Karthik","PA Patel"]
        for wk in wk_opts:
            if wk in bat_df["player"].values and wk not in added:
                row = bat_df[bat_df["player"]==wk].iloc[0]
                xi.append({"role":"🧤 Wicketkeeper","player":wk,"score":row.get("batting_score",0),"reason":f"Avg {row.get(\'average\',0):.1f} • SR {row.get(\'strike_rate\',0):.1f}"})
                added.add(wk); break
        count = 0
        for _,row in bat_df.iterrows():
            if row["player"] not in added and count < 4:
                xi.append({"role":f"🏏 Batsman {count+1}","player":row["player"],"score":row.get("batting_score",0),"reason":f"Avg {row.get(\'average\',0):.1f} • SR {row.get(\'strike_rate\',0):.1f}"})
                added.add(row["player"]); count+=1
    if players["allrounder"]:
        ar_df = pd.DataFrame(players["allrounder"])
        ar_df = ar_df[ar_df["matches"]>=min_matches]
        count = 0
        for _,row in ar_df.iterrows():
            if row["player"] not in added and count < 3:
                xi.append({"role":f"🤸 All-rounder {count+1}","player":row["player"],"score":row.get("allrounder_score",0),"reason":f"Bat {row.get(\'batting_score\',0):.0f} • Bowl {row.get(\'bowling_score\',0):.0f}"})
                added.add(row["player"]); count+=1
    if players["bowling"]:
        bowl_df = pd.DataFrame(players["bowling"])
        bowl_df = bowl_df[bowl_df["matches"]>=min_matches]
        opp_bat_strong = opp_stats.get("avg_batting_score",30) > 35
        bowl_df = bowl_df.sort_values("economy" if opp_bat_strong else "bowling_score", ascending=opp_bat_strong)
        count = 0
        for _,row in bowl_df.iterrows():
            if row["player"] not in added and count < 3:
                xi.append({"role":f"🎯 Bowler {count+1}","player":row["player"],"score":row.get("bowling_score",0),"reason":f"Econ {row.get(\'economy\',0):.2f} • {int(row.get(\'wickets\',0))} wkts"})
                added.add(row["player"]); count+=1
    return xi
'''
os.makedirs("analytics", exist_ok=True)
with open("analytics/team_analytics.py", "w", encoding="utf-8") as f:
    f.write(ta_code.strip())
print(f"  ✅ team_analytics.py — {ta_code.count(chr(10))} lines")

# ── 3. Write full app.py ─────────────────────────────
print("Writing dashboard/app.py ...")

# Read main dashboard content
main_dash = open(os.path.join(os.path.dirname(__file__),
                              "dashboard_main.py"), encoding="utf-8").read()
team_tab  = open(os.path.join(os.path.dirname(__file__),
                              "team_tab_code.py"), encoding="utf-8").read()

# Combine: add imports, team tab
full_app = main_dash.replace(
    "from dashboard.ipl_teams import get_team_color, get_team_info, PLAYER_TEAMS, IPL_TEAMS, avatar_html",
    "from dashboard.ipl_teams import get_team_color, get_team_info, PLAYER_TEAMS, IPL_TEAMS, avatar_html, RETIRED_PLAYERS\n"
    "from analytics.team_analytics import (get_team_players, calculate_team_stats,\n"
    "    generate_swot, get_player_matchups, get_best_xi_vs_opponent)"
)

# Add retired player filter to prep_df
full_app = full_app.replace(
    'df = df[df["matches"] >= min_m].copy()',
    'df = df[df["matches"] >= min_m].copy()\n'
    '    # Remove retired players\n'
    '    pcol2 = "player" if "player" in df.columns else df.columns[0]\n'
    '    df = df[~df[pcol2].isin(RETIRED_PLAYERS)]'
)

full_app += "\n\n" + team_tab

with open("dashboard/app.py", "w", encoding="utf-8") as f:
    f.write(full_app)
lines = full_app.count("\n") + 1
print(f"  ✅ app.py — {lines} lines")
print("\n🎉 ALL FILES WRITTEN SUCCESSFULLY!")
print("Run: streamlit run dashboard\\app.py")
