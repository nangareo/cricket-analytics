import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os, sys, json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from ingestion.filter_selector import save_filter
from dashboard.ipl_teams import get_team_color, get_team_info, PLAYER_TEAMS

st.set_page_config(
    page_title="Cricket Analytics",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
dark   = st.session_state.dark_mode
BG     = "#0e1117" if dark else "#ffffff"
CARD   = "#1a1a2e" if dark else "#f0f2f6"
TEXT   = "#ffffff"  if dark else "#000000"
ACCENT = "#2ecc71"

st.markdown(f"""
<style>
.main-header{{font-size:2.8rem;font-weight:900;color:{ACCENT};
              text-align:center;padding:1rem 0;}}
.sub-header{{text-align:center;color:{TEXT};opacity:0.7;}}
.player-card{{background:{CARD};border-radius:12px;padding:1rem;
              text-align:center;border-left:4px solid {ACCENT};margin:0.5rem 0;}}
</style>""", unsafe_allow_html=True)

# ── SIDEBAR ──────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏏 Cricket Analytics")
    if st.button("☀️ Light Mode" if dark else "🌙 Dark Mode"):
        st.session_state.dark_mode = not dark
        st.rerun()
    st.markdown("---")
    st.markdown("### 📅 Filter Data")
    filter_type = st.radio("Select filter:", [
        "All Time","Last 3 Seasons","Last 5 Seasons",
        "Single Season","Custom Range","Multiple Seasons"
    ])
    selected_seasons = None
    filter_label     = "All Time"
    if filter_type == "All Time":
        selected_seasons = None
        filter_label     = "All Time (2008-2025)"
    elif filter_type == "Last 3 Seasons":
        selected_seasons = ["2023","2024","2025"]
        filter_label     = "Last 3 Seasons (2023-2025)"
    elif filter_type == "Last 5 Seasons":
        selected_seasons = ["2021","2022","2023","2024","2025"]
        filter_label     = "Last 5 Seasons (2021-2025)"
    elif filter_type == "Single Season":
        season           = st.selectbox("Pick season:", config.ALL_SEASONS)
        selected_seasons = [season]
        filter_label     = f"IPL {season}"
    elif filter_type == "Custom Range":
        start = st.selectbox("Start:", config.ALL_SEASONS, index=0)
        end   = st.selectbox("End:",   config.ALL_SEASONS,
                              index=len(config.ALL_SEASONS)-1)
        selected_seasons = [s for s in config.ALL_SEASONS
                            if int(start) <= int(s) <= int(end)]
        filter_label     = f"IPL {start} to {end}"
    elif filter_type == "Multiple Seasons":
        seasons          = st.multiselect("Pick seasons:",
                              config.ALL_SEASONS,
                              default=["2022","2023","2024"])
        selected_seasons = seasons or None
        filter_label     = f"IPL {', '.join(seasons)}" if seasons else "All Time"
    if st.button("🔄 Apply Filter"):
        save_filter("seasons",
                    selected_seasons if selected_seasons else "all")
        st.cache_data.clear()
        st.success("✅ Filter applied!")
        st.rerun()
    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    min_matches = st.slider("Min matches:", 5, 50, config.MIN_MATCHES)
    top_n       = st.slider("Players to show:", 5, 30, 10)

# ── HEADER ───────────────────────────────────────────
st.markdown("<p class='main-header'>🏏 Cricket Analytics Dashboard</p>",
            unsafe_allow_html=True)
st.markdown(f"<p class='sub-header'>Filter: {filter_label} | Min Matches: {min_matches}</p>",
            unsafe_allow_html=True)
st.markdown("---")

# ── LOAD DATA ────────────────────────────────────────
@st.cache_data
def load_scores():
    paths = {
        "batting":    "analytics/batting/batting_scores.csv",
        "bowling":    "analytics/bowling/bowling_scores.csv",
        "fielding":   "analytics/fielding/fielding_scores.csv",
        "allrounder": "analytics/allrounder/allrounder_scores.csv"
    }
    out = {}
    for k, p in paths.items():
        if os.path.exists(p):
            df = pd.read_csv(p)
            if "Unnamed: 0" in df.columns:
                df = df.drop("Unnamed: 0", axis=1)
            out[k] = df
        else:
            out[k] = None
    return out

@st.cache_data
def load_raw_sample():
    folder = config.DATA_FOLDER
    files  = [f for f in os.listdir(folder)
              if f.endswith(".csv") and "_info" not in f]
    data   = []
    for f in files[:200]:
        try:
            data.append(pd.read_csv(os.path.join(folder, f)))
        except:
            pass
    return pd.concat(data, ignore_index=True) if data else None

scores = load_scores()

def add_team_colors(df, col):
    df["team"]  = df[col].apply(lambda x: PLAYER_TEAMS.get(x, "Unknown"))
    df["color"] = df[col].apply(get_team_color)
    return df

# ── TABS ─────────────────────────────────────────────
tab1,tab2,tab3,tab4,tab5,tab6,tab7 = st.tabs([
    "🏏 Batting","🎯 Bowling","🤸 All-rounders",
    "⚔️ Head to Head","📈 Season Trends",
    "🌟 Best XI","🔍 Player Search"
])

# ── TAB 1 BATTING ─────────────────────────────────────
with tab1:
    st.markdown("## 🏏 Top Batsmen")
    if scores["batting"] is not None:
        df = scores["batting"].copy()
        if "striker" in df.columns:
            df = df.rename(columns={"striker":"player"})
        df = df[df["matches"] >= min_matches]
        df = add_team_colors(df, "player")
        df = df.sort_values("batting_score",
                ascending=False).head(top_n).reset_index(drop=True)
        df.index += 1
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("🥇 #1 Batsman",   df.iloc[0]["player"])
        c2.metric("📈 Best Average", f"{df['average'].max():.1f}")
        c3.metric("⚡ Best SR",      f"{df['strike_rate'].max():.1f}")
        c4.metric("🏏 Ranked",       len(df))
        st.markdown("---")
        fig = px.bar(df, x="player", y="batting_score", color="team",
                     title=f"Top {top_n} Batsmen",
                     text="batting_score",
                     labels={"batting_score":"Score","player":""})
        fig.update_traces(textposition="outside")
        fig.update_layout(xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)
        fig2 = px.scatter(df, x="average", y="strike_rate",
                          size="batting_score", color="team",
                          hover_name="player",
                          title="Average vs Strike Rate")
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("### 📋 Rankings — click headers to sort")
        st.dataframe(df[["player","team","matches","total_runs",
                          "average","strike_rate",
                          "boundary_pct","batting_score"]],
                     use_container_width=True)
    else:
        st.warning("⚠️ Run batting_scorer.py first!")

# ── TAB 2 BOWLING ─────────────────────────────────────
with tab2:
    st.markdown("## 🎯 Top Bowlers")
    if scores["bowling"] is not None:
        df = scores["bowling"].copy()
        if "bowler" in df.columns:
            df = df.rename(columns={"bowler":"player"})
        df = df[df["matches"] >= min_matches]
        df = add_team_colors(df, "player")
        df = df.sort_values("bowling_score",
                ascending=False).head(top_n).reset_index(drop=True)
        df.index += 1
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("🥇 #1 Bowler",    df.iloc[0]["player"])
        c2.metric("🎯 Best Economy", f"{df['economy'].min():.2f}")
        c3.metric("⚡ Most Wickets", f"{int(df['wickets'].max())}")
        c4.metric("🏏 Ranked",       len(df))
        st.markdown("---")
        fig = px.bar(df, x="player", y="bowling_score", color="team",
                     title=f"Top {top_n} Bowlers", text="bowling_score",
                     labels={"bowling_score":"Score","player":""})
        fig.update_traces(textposition="outside")
        fig.update_layout(xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)
        fig2 = px.scatter(df, x="economy", y="dot_ball_pct",
                          size="wickets", color="team",
                          hover_name="player",
                          title="Economy vs Dot Ball %")
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("### 📋 Rankings")
        st.dataframe(df[["player","team","matches","wickets",
                          "economy","bowling_sr",
                          "dot_ball_pct","bowling_score"]],
                     use_container_width=True)
    else:
        st.warning("⚠️ Run bowling_scorer.py first!")

# ── TAB 3 ALL-ROUNDERS ────────────────────────────────
with tab3:
    st.markdown("## 🤸 Top All-rounders")
    if scores["allrounder"] is not None:
        df = scores["allrounder"].copy()
        df = df[df["matches"] >= min_matches]
        df = add_team_colors(df, "player")
        df = df.sort_values("allrounder_score",
                ascending=False).head(top_n).reset_index(drop=True)
        df.index += 1
        c1,c2,c3 = st.columns(3)
        c1.metric("🥇 #1 All-rounder", df.iloc[0]["player"])
        c2.metric("🏏 Best Batting",   f"{df['batting_score'].max():.1f}")
        c3.metric("🎯 Best Bowling",   f"{df['bowling_score'].max():.1f}")
        st.markdown("---")
        top5 = df.head(5)
        fig  = go.Figure()
        cats = ["batting_score","bowling_score","fielding_score","allrounder_score"]
        labs = ["Batting","Bowling","Fielding","Overall"]
        for _,row in top5.iterrows():
            fig.add_trace(go.Scatterpolar(
                r=[row[c] for c in cats], theta=labs,
                fill="toself", name=row["player"]))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0,100])),
            title="Top 5 All-rounders Radar")
        st.plotly_chart(fig, use_container_width=True)
        fig2 = px.bar(df, x="player",
                      y=["batting_score","bowling_score","fielding_score"],
                      title="Score Breakdown", barmode="stack",
                      labels={"value":"Score","player":""})
        fig2.update_layout(xaxis_tickangle=-30)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("### 📋 Rankings")
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("⚠️ Run all scorers first!")

# ── TAB 4 HEAD TO HEAD ────────────────────────────────
with tab4:
    st.markdown("## ⚔️ Head to Head Comparison")
    all_players = []
    if scores["batting"] is not None:
        col = "striker" if "striker" in scores["batting"].columns else "player"
        all_players = sorted(scores["batting"][col].tolist())
    if all_players:
        c1,c2 = st.columns(2)
        p1 = c1.selectbox("🔵 Player 1:", all_players, index=0)
        p2 = c2.selectbox("🔴 Player 2:", all_players, index=1)
        def get_stats(name):
            s = {"player":name,
                 "team": PLAYER_TEAMS.get(name,"Unknown")}
            ti = get_team_info(name)
            s["team_color"] = ti["color"]
            s["team_emoji"] = ti["emoji"]
            if scores["batting"] is not None:
                col = "striker" if "striker" in scores["batting"].columns else "player"
                row = scores["batting"][scores["batting"][col]==name]
                if not row.empty:
                    s["batting_score"] = float(row["batting_score"].values[0])
                    s["average"]       = float(row["average"].values[0])
                    s["strike_rate"]   = float(row["strike_rate"].values[0])
                    s["boundary_pct"]  = float(row["boundary_pct"].values[0])
                    s["matches"]       = int(row["matches"].values[0])
                    s["total_runs"]    = int(row["total_runs"].values[0])
            if scores["bowling"] is not None:
                col = "bowler" if "bowler" in scores["bowling"].columns else "player"
                row = scores["bowling"][scores["bowling"][col]==name]
                if not row.empty:
                    s["bowling_score"] = float(row["bowling_score"].values[0])
                    s["economy"]       = float(row["economy"].values[0])
                    s["wickets"]       = int(row["wickets"].values[0])
                    s["dot_ball_pct"]  = float(row["dot_ball_pct"].values[0])
            if scores["allrounder"] is not None:
                row = scores["allrounder"][scores["allrounder"]["player"]==name]
                if not row.empty:
                    s["allrounder_score"] = float(row["allrounder_score"].values[0])
            return s
        s1 = get_stats(p1)
        s2 = get_stats(p2)
        c1,c2 = st.columns(2)
        with c1:
            st.markdown(f"""<div class="player-card"
                style="border-left:4px solid {s1.get("team_color","#2ecc71")}">
                <div style="font-size:3rem">🏏</div>
                <div style="font-size:1.5rem;font-weight:bold">
                    {s1["team_emoji"]} {p1}</div>
                <div style="opacity:0.7">{s1.get("team","Unknown")}</div>
                <div style="font-size:2rem;color:{s1.get("team_color","#2ecc71")};font-weight:bold">
                    {s1.get("batting_score","N/A")}</div>
                <div>Batting Score</div></div>""",
                unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="player-card"
                style="border-left:4px solid {s2.get("team_color","#e74c3c")}">
                <div style="font-size:3rem">🏏</div>
                <div style="font-size:1.5rem;font-weight:bold">
                    {s2["team_emoji"]} {p2}</div>
                <div style="opacity:0.7">{s2.get("team","Unknown")}</div>
                <div style="font-size:2rem;color:{s2.get("team_color","#e74c3c")};font-weight:bold">
                    {s2.get("batting_score","N/A")}</div>
                <div>Batting Score</div></div>""",
                unsafe_allow_html=True)
        st.markdown("---")
        metrics = []
        for key,label in [
            ("batting_score","Batting Score"),
            ("bowling_score","Bowling Score"),
            ("average","Average"),
            ("strike_rate","Strike Rate"),
            ("boundary_pct","Boundary %")]:
            if key in s1 or key in s2:
                metrics.append({"Metric":label,
                                 p1:s1.get(key,0),
                                 p2:s2.get(key,0)})
        if metrics:
            cdf = pd.DataFrame(metrics).melt(
                id_vars="Metric", var_name="Player", value_name="Value")
            fig = px.bar(cdf, x="Metric", y="Value",
                         color="Player", barmode="group",
                         title=f"⚔️ {p1} vs {p2}",
                         color_discrete_map={
                             p1:s1.get("team_color","#1f77b4"),
                             p2:s2.get("team_color","#ff7f0e")})
            st.plotly_chart(fig, use_container_width=True)
        skip = {"player","team","team_color","team_emoji"}
        rows = []
        for k in sorted(set(s1)|set(s2)-skip):
            v1,v2 = s1.get(k,"—"),s2.get(k,"—")
            winner = ""
            if isinstance(v1,(int,float)) and isinstance(v2,(int,float)):
                winner = (f"✅ {p1}" if (v1<v2 if k=="economy" else v1>v2)
                          else f"✅ {p2}")
            rows.append({"Stat":k.replace("_"," ").title(),
                         p1:v1, p2:v2, "Winner":winner})
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

# ── TAB 5 SEASON TRENDS ───────────────────────────────
with tab5:
    st.markdown("## 📈 Season by Season Trends")
    raw = load_raw_sample()
    if raw is not None and "season" in raw.columns:
        sr = raw.groupby("season").agg(
            total_runs  =("runs_off_bat","sum"),
            total_balls =("runs_off_bat","count"),
            matches     =("match_id","nunique")
        ).reset_index()
        sr["avg_score"] = (sr["total_runs"]/sr["matches"]).round(1)
        sr["run_rate"]  = (sr["total_runs"]/sr["total_balls"]*6).round(2)
        sr = sr.sort_values("season")
        fig = px.line(sr, x="season", y="avg_score", markers=True,
                      title="Average Team Score per Match by Season",
                      labels={"avg_score":"Avg Score","season":"Season"})
        fig.update_traces(line_color=ACCENT, line_width=3)
        st.plotly_chart(fig, use_container_width=True)
        fig2 = px.bar(sr, x="season", y="run_rate",
                      color="run_rate", color_continuous_scale="Greens",
                      title="Overall Run Rate by Season",
                      labels={"run_rate":"Run Rate","season":"Season"})
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("### 📋 Season Summary")
        st.dataframe(sr, use_container_width=True)
    else:
        st.warning("⚠️ Raw data needed for season trends!")

# ── TAB 6 BEST XI ─────────────────────────────────────
with tab6:
    st.markdown("## 🌟 Predicted Best XI")
    st.markdown("*Based on analytics scores — updated for IPL 2025*")
    if (scores["batting"] is not None and
        scores["bowling"] is not None and
        scores["allrounder"] is not None):
        bat_df  = scores["batting"].copy()
        if "striker" in bat_df.columns:
            bat_df = bat_df.rename(columns={"striker":"player"})
        bat_df  = bat_df[bat_df["matches"] >= min_matches]
        bowl_df = scores["bowling"].copy()
        if "bowler" in bowl_df.columns:
            bowl_df = bowl_df.rename(columns={"bowler":"player"})
        bowl_df = bowl_df[bowl_df["matches"] >= min_matches]
        ar_df   = scores["allrounder"].copy()
        ar_df   = ar_df[ar_df["matches"] >= min_matches]
        top_bat  = bat_df.sort_values("batting_score",  ascending=False).head(20)
        top_bowl = bowl_df.sort_values("bowling_score", ascending=False).head(20)
        top_ar   = ar_df.sort_values("allrounder_score",ascending=False).head(10)
        best_xi  = []
        added    = set()
        wk_list  = ["MS Dhoni","RR Pant","Sanju Samson",
                    "Q de Kock","Ishan Kishan","KL Rahul"]
        wk = next((p for p in wk_list
                   if p in top_bat["player"].values), None)
        if wk:
            row = top_bat[top_bat["player"]==wk].iloc[0]
            best_xi.append({"Role":"🧤 Wicketkeeper","Player":wk,
                "Team":PLAYER_TEAMS.get(wk,"Unknown"),
                "Score":f"{row['batting_score']:.1f}",
                "Key Stat":f"Avg: {row['average']:.1f}"})
            added.add(wk)
        count = 0
        for _,row in top_bat.iterrows():
            if row["player"] not in added and count < 4:
                best_xi.append({"Role":f"🏏 Batsman {count+1}",
                    "Player":row["player"],
                    "Team":PLAYER_TEAMS.get(row["player"],"Unknown"),
                    "Score":f"{row['batting_score']:.1f}",
                    "Key Stat":f"SR: {row['strike_rate']:.1f}"})
                added.add(row["player"]); count += 1
        count = 0
        for _,row in top_ar.iterrows():
            if row["player"] not in added and count < 3:
                best_xi.append({"Role":f"🤸 All-rounder {count+1}",
                    "Player":row["player"],
                    "Team":PLAYER_TEAMS.get(row["player"],"Unknown"),
                    "Score":f"{row['allrounder_score']:.1f}",
                    "Key Stat":f"AR: {row['allrounder_score']:.1f}"})
                added.add(row["player"]); count += 1
        count = 0
        for _,row in top_bowl.iterrows():
            if row["player"] not in added and count < 3:
                best_xi.append({"Role":f"🎯 Bowler {count+1}",
                    "Player":row["player"],
                    "Team":PLAYER_TEAMS.get(row["player"],"Unknown"),
                    "Score":f"{row['bowling_score']:.1f}",
                    "Key Stat":f"Econ: {row['economy']:.2f}"})
                added.add(row["player"]); count += 1
        st.markdown(f"### 🏆 Best XI — {filter_label}")
        for row in best_xi:
            color = get_team_color(row["Player"])
            st.markdown(f"""<div class="player-card"
                style="border-left:4px solid {color}">
                <b>{row["Role"]}</b> &nbsp;|&nbsp;
                <b style="color:{color}">{row["Player"]}</b>
                &nbsp;|&nbsp; {row["Team"]}
                &nbsp;|&nbsp; Score: <b>{row["Score"]}</b>
                &nbsp;|&nbsp; {row["Key Stat"]}
                </div>""", unsafe_allow_html=True)
        st.markdown("---")
        st.dataframe(pd.DataFrame(best_xi), use_container_width=True)
    else:
        st.warning("⚠️ Run all scorers first!")

# ── TAB 7 PLAYER SEARCH ───────────────────────────────
with tab7:
    st.markdown("## 🔍 Player Search")
    search = st.text_input("Search player:",
                           placeholder="e.g. Kohli, Rohit, Bumrah...")
    if search:
        found = False
        if scores["batting"] is not None:
            col    = "striker" if "striker" in scores["batting"].columns else "player"
            result = scores["batting"][
                scores["batting"][col].str.contains(search,case=False,na=False)]
            if not result.empty:
                found = True
                name  = result.iloc[0][col]
                ti    = get_team_info(name)
                st.markdown(f"""<div class="player-card"
                    style="border-left:4px solid {ti["color"]}">
                    <b style="font-size:1.3rem">{ti["emoji"]} {name}</b><br>
                    <span style="opacity:0.7">{ti["team_name"]}</span>
                    </div>""", unsafe_allow_html=True)
                st.markdown("**🏏 Batting Stats:**")
                st.dataframe(result, use_container_width=True)
        if scores["bowling"] is not None:
            col    = "bowler" if "bowler" in scores["bowling"].columns else "player"
            result = scores["bowling"][
                scores["bowling"][col].str.contains(search,case=False,na=False)]
            if not result.empty:
                found = True
                st.markdown("**🎯 Bowling Stats:**")
                st.dataframe(result, use_container_width=True)
        if scores["allrounder"] is not None:
            result = scores["allrounder"][
                scores["allrounder"]["player"].str.contains(
                    search,case=False,na=False)]
            if not result.empty:
                found = True
                st.markdown("**🤸 All-rounder Stats:**")
                st.dataframe(result, use_container_width=True)
        if not found:
            st.info(f"No results for '{search}'. Try different spelling.")

# ── FOOTER ────────────────────────────────────────────
st.markdown("---")
c1,c2,c3 = st.columns(3)
c1.markdown("🏏 **Cricket Analytics**")
c2.markdown("Python · Streamlit · Docker · GitHub Actions")
c3.markdown("📊 Data: Cricsheet.org")