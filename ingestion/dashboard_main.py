# ============================================
# CRICKET ANALYTICS DASHBOARD - PREMIUM UI
# ============================================
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os, sys, json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from ingestion.filter_selector import save_filter
from dashboard.ipl_teams import get_team_color, get_team_info, PLAYER_TEAMS, IPL_TEAMS, avatar_html

st.set_page_config(
    page_title="Cricket Analytics | IPL 2025",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── PREMIUM CSS ───────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');

:root {
    --bg:       #050a0e;
    --surface:  #0d1117;
    --card:     #111820;
    --border:   #1e2d3d;
    --accent:   #00d4aa;
    --gold:     #f0b429;
    --red:      #e63946;
    --text:     #e6edf3;
    --muted:    #7d8590;
    --glow:     0 0 20px rgba(0,212,170,0.3);
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif;
}

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Hide default streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* HERO HEADER */
.hero {
    background: linear-gradient(135deg, #050a0e 0%, #0a1628 50%, #050a0e 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2.5rem 2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
    text-align: center;
}
.hero::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(ellipse at center,
        rgba(0,212,170,0.06) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 3.2rem;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    background: linear-gradient(135deg, #00d4aa, #f0b429, #00d4aa);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shine 3s linear infinite;
    margin: 0;
    line-height: 1.1;
}
.hero-sub {
    color: var(--muted);
    font-size: 0.9rem;
    letter-spacing: 4px;
    text-transform: uppercase;
    margin-top: 0.5rem;
}
.hero-badge {
    display: inline-block;
    background: linear-gradient(135deg, #f0b429, #e07b00);
    color: #000;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
    font-size: 0.75rem;
    letter-spacing: 2px;
    padding: 3px 12px;
    border-radius: 20px;
    margin-top: 0.8rem;
    text-transform: uppercase;
}
@keyframes shine {
    to { background-position: 200% center; }
}

/* STAT CARDS */
.stat-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin: 1rem 0;
}
.stat-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s, border-color 0.2s;
}
.stat-card:hover {
    transform: translateY(-2px);
    border-color: var(--accent);
}
.stat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent), var(--gold));
}
.stat-value {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: var(--accent);
    line-height: 1;
}
.stat-label {
    font-size: 0.7rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--muted);
    margin-top: 0.3rem;
}
.stat-name {
    font-size: 0.85rem;
    color: var(--text);
    margin-top: 0.2rem;
    font-weight: 500;
}

/* PLAYER CARDS */
.player-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
    margin: 1rem 0;
}
.player-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
}
.player-card:hover {
    transform: translateY(-3px);
    box-shadow: var(--glow);
}
.player-rank {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--border);
    position: absolute;
    top: 0.5rem;
    right: 0.8rem;
    line-height: 1;
}
.player-name {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 0.2rem;
}
.player-team {
    font-size: 0.7rem;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 0.8rem;
}
.player-score {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    line-height: 1;
}
.player-stats {
    display: flex;
    gap: 0.8rem;
    margin-top: 0.5rem;
}
.mini-stat { font-size: 0.72rem; color: var(--muted); }
.mini-val  { font-weight: 600; color: var(--text); }

/* TEAM BADGE */
.team-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
}

/* LEADERBOARD */
.lb-row {
    display: grid;
    grid-template-columns: 40px 1fr 80px 80px 80px 90px;
    align-items: center;
    padding: 0.7rem 1rem;
    border-radius: 8px;
    margin-bottom: 0.4rem;
    background: var(--card);
    border: 1px solid var(--border);
    transition: background 0.15s;
}
.lb-row:hover { background: #161f2a; }
.lb-row.gold   { border-left: 3px solid #f0b429; }
.lb-row.silver { border-left: 3px solid #8b9eb7; }
.lb-row.bronze { border-left: 3px solid #cd7f32; }
.lb-rank { font-family:'Rajdhani',sans-serif; font-size:1.3rem;
           font-weight:700; color:var(--muted); }
.lb-rank.r1 { color:#f0b429; }
.lb-rank.r2 { color:#8b9eb7; }
.lb-rank.r3 { color:#cd7f32; }
.lb-name  { font-weight:600; font-size:0.95rem; }
.lb-team  { font-size:0.7rem; color:var(--muted); }
.lb-stat  { text-align:right; font-size:0.85rem; color:var(--muted); }
.lb-score { text-align:right; font-family:'Rajdhani',sans-serif;
            font-size:1.3rem; font-weight:700; color:var(--accent); }

/* SECTION TITLES */
.section-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--text);
    border-left: 3px solid var(--accent);
    padding-left: 0.8rem;
    margin: 1.5rem 0 1rem 0;
}

/* TABS */
[data-testid="stTabs"] button {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom-color: var(--accent) !important;
}

/* SIDEBAR */
.sidebar-logo {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.4rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--accent);
    padding: 0.5rem 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1rem;
}

/* H2H cards */
.h2h-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.h2h-score {
    font-family: 'Rajdhani', sans-serif;
    font-size: 3rem;
    font-weight: 700;
    line-height: 1;
}
.h2h-name {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.4rem;
    font-weight: 600;
    margin: 0.5rem 0 0.2rem;
}
.vs-badge {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: var(--gold);
    text-align: center;
    padding-top: 3rem;
}

/* BEST XI */
.xi-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.8rem 1rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 0.5rem;
    transition: transform 0.15s;
}
.xi-card:hover { transform: translateX(4px); }
.xi-role {
    font-size: 0.65rem;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: var(--muted);
    width: 100px;
    flex-shrink: 0;
}
.xi-name {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.1rem;
    font-weight: 600;
    flex: 1;
}
.xi-score {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--accent);
}

/* Progress bars */
.progress-wrap { margin: 0.3rem 0; }
.progress-label {
    display:flex; justify-content:space-between;
    font-size:0.72rem; color:var(--muted); margin-bottom:3px;
}
.progress-bar {
    height: 4px;
    background: var(--border);
    border-radius: 2px;
    overflow: hidden;
}
.progress-fill {
    height: 100%;
    border-radius: 2px;
    background: linear-gradient(90deg, var(--accent), var(--gold));
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# ── LOAD DATA ─────────────────────────────────────────
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
    for f in files[:300]:
        try:
            data.append(pd.read_csv(os.path.join(folder, f)))
        except:
            pass
    return pd.concat(data, ignore_index=True) if data else None

scores = load_scores()

def hex_to_rgba(hex_color, alpha=0.3):
    """Convert #RRGGBB hex to rgba(r,g,b,alpha) string for Plotly"""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c*2 for c in hex_color)
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

def get_player_col(df, options=["striker","bowler","player"]):
    for o in options:
        if o in df.columns:
            return o
    return df.columns[0]

def prep_df(df, score_col, min_m, top):
    pcol = get_player_col(df)
    if pcol != "player":
        df = df.rename(columns={pcol: "player"})
    df = df[df["matches"] >= min_m].copy()
    df["team"]  = df["player"].apply(lambda x: PLAYER_TEAMS.get(x, "Unknown"))
    df["color"] = df["player"].apply(get_team_color)
    df = df.sort_values(score_col, ascending=False).head(top).reset_index(drop=True)
    df.index += 1
    return df

def plotly_dark():
    return dict(
        plot_bgcolor  = "rgba(0,0,0,0)",
        paper_bgcolor = "rgba(0,0,0,0)",
        font_color    = "#7d8590",
        title_font_color = "#e6edf3",
        title_font_family = "Rajdhani",
        xaxis = dict(gridcolor="#1e2d3d", color="#7d8590"),
        yaxis = dict(gridcolor="#1e2d3d", color="#7d8590"),
    )

def medal(i):
    if i == 1: return "gold"
    if i == 2: return "silver"
    if i == 3: return "bronze"
    return ""

def rank_cls(i):
    if i == 1: return "r1"
    if i == 2: return "r2"
    if i == 3: return "r3"
    return ""

# ── HERO ─────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-title">🏏 Cricket Analytics</div>
    <div class="hero-sub">IPL Intelligence Platform</div>
    <div class="hero-badge">🏆 IPL 2025 — RCB Champions</div>
</div>
""", unsafe_allow_html=True)

# ── FLOATING FILTER BAR ───────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebar"]        { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
.block-container { padding-left:1.5rem !important; padding-right:1.5rem !important; max-width:100% !important; }
[data-testid="stSelectbox"] > div > div {
    background:#111820 !important; border:1px solid #1e2d3d !important;
    border-radius:8px !important; font-size:0.8rem !important; }
[data-testid="stSelectbox"] label {
    font-size:0.62rem !important; letter-spacing:1px !important;
    text-transform:uppercase !important; color:#7d8590 !important; }
[data-testid="stNumberInput"] input {
    background:#111820 !important; border:1px solid #1e2d3d !important;
    border-radius:8px !important; font-size:0.8rem !important;
    color:#e6edf3 !important; }
[data-testid="stNumberInput"] label {
    font-size:0.62rem !important; letter-spacing:1px !important;
    text-transform:uppercase !important; color:#7d8590 !important; }
div[data-testid="stHorizontalBlock"] > div:nth-last-child(2) button {
    background:#00d4aa !important; color:#050a0e !important;
    border:none !important; border-radius:8px !important;
    font-family:'Rajdhani',sans-serif !important; font-weight:700 !important;
    font-size:0.75rem !important; letter-spacing:1px !important; }
</style>
""", unsafe_allow_html=True)

# Filter state defaults
if "filter_label"     not in st.session_state:
    st.session_state.filter_label     = "All Time  •  2008–2025"
    st.session_state.selected_seasons = None
    st.session_state.min_matches      = config.MIN_MATCHES
    st.session_state.top_n            = 10

# Compact filter row ─ 7 columns
fc1,fc2,fc3,fc4,fc5,fc6,fc7 = st.columns([2,1.2,1,0.8,0.8,0.7,1.2])
with fc1:
    filter_type = st.selectbox("SEASON FILTER",
        ["All Time","Last 3 Seasons","Last 5 Seasons","Single Season","Custom Range"],
        key="ft_sel")
with fc2:
    season_pick = (st.selectbox("SEASON", config.ALL_SEASONS,
                                index=len(config.ALL_SEASONS)-1, key="sp")
                   if filter_type == "Single Season"
                   else st.selectbox("FROM", config.ALL_SEASONS, index=0, key="sp")
                   if filter_type == "Custom Range"
                   else None)
with fc3:
    season_pick2 = (st.selectbox("TO", config.ALL_SEASONS,
                                 index=len(config.ALL_SEASONS)-1, key="sp2")
                    if filter_type == "Custom Range" else None)
with fc4:
    min_matches = st.number_input("MIN MATCHES", min_value=1, max_value=50,
                                  value=st.session_state.min_matches, key="mm")
with fc5:
    top_n = st.number_input("TOP N", min_value=3, max_value=30,
                            value=st.session_state.top_n, key="tn")
with fc6:
    st.markdown('<div style="height:22px"></div>', unsafe_allow_html=True)
    apply = st.button("▶ APPLY", use_container_width=True)
with fc7:
    st.markdown(
        f'<div style="padding-top:16px;border-left:2px solid #1e2d3d;padding-left:12px">'        f'<div style="font-size:0.6rem;letter-spacing:2px;text-transform:uppercase;color:#7d8590">ACTIVE FILTER</div>'        f'<div style="font-family:Rajdhani,sans-serif;font-size:0.95rem;font-weight:600;color:#00d4aa">'        f'{st.session_state.filter_label}</div></div>',
        unsafe_allow_html=True)

if apply:
    if filter_type == "All Time":
        sel, lbl = None, "All Time  •  2008–2025"
    elif filter_type == "Last 3 Seasons":
        sel, lbl = ["2023","2024","2025"], "Last 3 Seasons"
    elif filter_type == "Last 5 Seasons":
        sel, lbl = ["2021","2022","2023","2024","2025"], "Last 5 Seasons"
    elif filter_type == "Single Season":
        sel, lbl = [season_pick], f"IPL {season_pick}"
    elif filter_type == "Custom Range":
        sel = [x for x in config.ALL_SEASONS if int(season_pick) <= int(x) <= int(season_pick2)]
        lbl = f"IPL {season_pick}–{season_pick2}"
    else:
        sel, lbl = None, "All Time  •  2008–2025"
    st.session_state.selected_seasons = sel
    st.session_state.filter_label     = lbl
    st.session_state.min_matches      = int(min_matches)
    st.session_state.top_n            = int(top_n)
    save_filter("seasons", sel if sel else "all")
    st.cache_data.clear()
    st.rerun()

selected_seasons = st.session_state.selected_seasons
filter_label     = st.session_state.filter_label
min_matches      = st.session_state.min_matches
top_n            = st.session_state.top_n

st.markdown("<hr style='border:none;border-top:1px solid #1e2d3d;margin:0.5rem 0'>",
            unsafe_allow_html=True)

# ── TABS ─────────────────────────────────────────────
tab1,tab2,tab3,tab4,tab5,tab6,tab7 = st.tabs([
    "🏏  BATTING", "🎯  BOWLING", "🤸  ALL-ROUNDERS",
    "⚔️  HEAD TO HEAD", "📈  SEASON TRENDS",
    "🌟  BEST XI", "🔍  PLAYER SEARCH"
])

# ──────────────────────────────────────────────────────
# TAB 1 — BATTING
# ──────────────────────────────────────────────────────
with tab1:
    if scores["batting"] is not None:
        df = prep_df(scores["batting"].copy(), "batting_score", min_matches, top_n)

        # Stat cards
        st.markdown(f"""
        <div class="stat-row">
            <div class="stat-card">
                <div class="stat-value">{df.iloc[0]["player"].split()[-1]}</div>
                <div class="stat-name">{df.iloc[0]["player"]}</div>
                <div class="stat-label">🥇 Top Batsman</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{df["average"].max():.1f}</div>
                <div class="stat-name">{df.loc[df["average"].idxmax(),"player"]}</div>
                <div class="stat-label">📈 Best Average</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{df["strike_rate"].max():.0f}</div>
                <div class="stat-name">{df.loc[df["strike_rate"].idxmax(),"player"]}</div>
                <div class="stat-label">⚡ Best Strike Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{int(df["total_runs"].max())}</div>
                <div class="stat-name">{df.loc[df["total_runs"].idxmax(),"player"]}</div>
                <div class="stat-label">🏏 Most Runs</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Leaderboard
        st.markdown('<div class="section-title">Rankings</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="lb-row" style="background:transparent;border-color:transparent;
             color:#7d8590;font-size:0.7rem;letter-spacing:1px;text-transform:uppercase;">
            <div>#</div><div>Player</div>
            <div style="text-align:right">Runs</div>
            <div style="text-align:right">Avg</div>
            <div style="text-align:right">SR</div>
            <div style="text-align:right">Score</div>
        </div>""", unsafe_allow_html=True)

        for i, row in df.iterrows():
            color = row["color"]
            st.markdown(f"""
            <div class="lb-row {medal(i)}">
                <div class="lb-rank {rank_cls(i)}">{i}</div>
                <div>
                    <div class="lb-name">{avatar_html(row["player"], 32)}{row["player"]}</div>
                    <div class="lb-team" style="color:{color}">
                        ● {row["team"]}</div>
                </div>
                <div class="lb-stat">{int(row["total_runs"])}</div>
                <div class="lb-stat">{row["average"]:.1f}</div>
                <div class="lb-stat">{row["strike_rate"]:.1f}</div>
                <div class="lb-score" style="color:{color}">{row["batting_score"]:.1f}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown('<div class="section-title">Analytics</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(df, x="player", y="batting_score",
                         color="batting_score",
                         color_continuous_scale=[[0,"#1e2d3d"],[1,"#00d4aa"]],
                         title="Batting Score Comparison",
                         text=df["batting_score"].round(1))
            fig.update_traces(textposition="outside", textfont_color="#e6edf3")
            fig.update_layout(**plotly_dark(), showlegend=False,
                              coloraxis_showscale=False,
                              xaxis_tickangle=-35)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig2 = px.scatter(df, x="average", y="strike_rate",
                              size="total_runs", color="batting_score",
                              hover_name="player",
                              color_continuous_scale=[[0,"#1e2d3d"],[1,"#f0b429"]],
                              title="Average vs Strike Rate",
                              labels={"average":"Batting Average",
                                      "strike_rate":"Strike Rate"})
            fig2.update_layout(**plotly_dark(), coloraxis_showscale=False)
            st.plotly_chart(fig2, use_container_width=True)

        # Boundary % chart
        fig3 = px.bar(df, x="player", y="boundary_pct",
                      color="boundary_pct",
                      color_continuous_scale=[[0,"#1e2d3d"],[1,"#e63946"]],
                      title="Boundary % — Hitting Aggression",
                      text=df["boundary_pct"].round(1))
        fig3.update_traces(textposition="outside", textfont_color="#e6edf3")
        fig3.update_layout(**plotly_dark(), showlegend=False,
                           coloraxis_showscale=False, xaxis_tickangle=-35)
        st.plotly_chart(fig3, use_container_width=True)

    else:
        st.warning("⚠️ Run batting_scorer.py first!")

# ──────────────────────────────────────────────────────
# TAB 2 — BOWLING
# ──────────────────────────────────────────────────────
with tab2:
    if scores["bowling"] is not None:
        df = prep_df(scores["bowling"].copy(), "bowling_score", min_matches, top_n)

        st.markdown(f"""
        <div class="stat-row">
            <div class="stat-card">
                <div class="stat-value">{df.iloc[0]["player"].split()[-1]}</div>
                <div class="stat-name">{df.iloc[0]["player"]}</div>
                <div class="stat-label">🥇 Top Bowler</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{df["economy"].min():.2f}</div>
                <div class="stat-name">{df.loc[df["economy"].idxmin(),"player"]}</div>
                <div class="stat-label">🎯 Best Economy</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{int(df["wickets"].max())}</div>
                <div class="stat-name">{df.loc[df["wickets"].idxmax(),"player"]}</div>
                <div class="stat-label">💥 Most Wickets</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{df["dot_ball_pct"].max():.1f}%</div>
                <div class="stat-name">{df.loc[df["dot_ball_pct"].idxmax(),"player"]}</div>
                <div class="stat-label">⚫ Best Dot Ball %</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-title">Rankings</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="lb-row" style="background:transparent;border-color:transparent;
             color:#7d8590;font-size:0.7rem;letter-spacing:1px;text-transform:uppercase;">
            <div>#</div><div>Player</div>
            <div style="text-align:right">Wkts</div>
            <div style="text-align:right">Econ</div>
            <div style="text-align:right">Dot%</div>
            <div style="text-align:right">Score</div>
        </div>""", unsafe_allow_html=True)

        for i, row in df.iterrows():
            color = row["color"]
            st.markdown(f"""
            <div class="lb-row {medal(i)}">
                <div class="lb-rank {rank_cls(i)}">{i}</div>
                <div>
                    <div class="lb-name">{avatar_html(row["player"], 32)}{row["player"]}</div>
                    <div class="lb-team" style="color:{color}">● {row["team"]}</div>
                </div>
                <div class="lb-stat">{int(row["wickets"])}</div>
                <div class="lb-stat">{row["economy"]:.2f}</div>
                <div class="lb-stat">{row["dot_ball_pct"]:.1f}%</div>
                <div class="lb-score" style="color:{color}">{row["bowling_score"]:.1f}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown('<div class="section-title">Analytics</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(df, x="player", y="bowling_score",
                         color="bowling_score",
                         color_continuous_scale=[[0,"#1e2d3d"],[1,"#e63946"]],
                         title="Bowling Score Comparison",
                         text=df["bowling_score"].round(1))
            fig.update_traces(textposition="outside", textfont_color="#e6edf3")
            fig.update_layout(**plotly_dark(), showlegend=False,
                              coloraxis_showscale=False, xaxis_tickangle=-35)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig2 = px.scatter(df, x="economy", y="dot_ball_pct",
                              size="wickets", color="bowling_score",
                              hover_name="player",
                              color_continuous_scale=[[0,"#1e2d3d"],[1,"#e63946"]],
                              title="Economy vs Dot Ball %",
                              labels={"economy":"Economy Rate",
                                      "dot_ball_pct":"Dot Ball %"})
            fig2.update_layout(**plotly_dark(), coloraxis_showscale=False)
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("⚠️ Run bowling_scorer.py first!")

# ──────────────────────────────────────────────────────
# TAB 3 — ALL-ROUNDERS
# ──────────────────────────────────────────────────────
with tab3:
    if scores["allrounder"] is not None:
        df = prep_df(scores["allrounder"].copy(), "allrounder_score", min_matches, top_n)

        st.markdown(f"""
        <div class="stat-row">
            <div class="stat-card">
                <div class="stat-value">{df.iloc[0]["player"].split()[-1]}</div>
                <div class="stat-name">{df.iloc[0]["player"]}</div>
                <div class="stat-label">🥇 Top All-rounder</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{df["batting_score"].max():.1f}</div>
                <div class="stat-name">{df.loc[df["batting_score"].idxmax(),"player"]}</div>
                <div class="stat-label">🏏 Best Batting</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{df["bowling_score"].max():.1f}</div>
                <div class="stat-name">{df.loc[df["bowling_score"].idxmax(),"player"]}</div>
                <div class="stat-label">🎯 Best Bowling</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{int(df["matches"].max())}</div>
                <div class="stat-name">{df.loc[df["matches"].idxmax(),"player"]}</div>
                <div class="stat-label">📅 Most Matches</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown('<div class="section-title">Rankings</div>',
                        unsafe_allow_html=True)
            for i, row in df.head(10).iterrows():
                color = row["color"]
                b_pct = min(row["batting_score"], 100)
                w_pct = min(row["bowling_score"], 100)
                f_pct = min(row.get("fielding_score", 0), 100)
                st.markdown(f"""
                <div class="player-card" style="border-top:2px solid {color}">
                    <div class="player-rank">{i}</div>
                    <div class="player-name">{avatar_html(row["player"], 36)}{row["player"]}</div>
                    <div class="player-team" style="color:{color}">
                        ● {row["team"]}</div>
                    <div class="player-score" style="color:{color}">
                        {row["allrounder_score"]:.1f}</div>
                    <div class="progress-wrap">
                        <div class="progress-label">
                            <span>Bat</span><span>{b_pct:.0f}</span></div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width:{b_pct}%"></div>
                        </div>
                    </div>
                    <div class="progress-wrap">
                        <div class="progress-label">
                            <span>Bowl</span><span>{w_pct:.0f}</span></div>
                        <div class="progress-bar">
                            <div class="progress-fill"
                                 style="width:{w_pct}%;background:linear-gradient(90deg,#e63946,#f0b429)">
                            </div>
                        </div>
                    </div>
                    <div class="progress-wrap">
                        <div class="progress-label">
                            <span>Field</span><span>{f_pct:.0f}</span></div>
                        <div class="progress-bar">
                            <div class="progress-fill"
                                 style="width:{f_pct}%;background:linear-gradient(90deg,#3a86ff,#00d4aa)">
                            </div>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)

        with col2:
            # Radar chart
            top5 = df.head(5)
            fig  = go.Figure()
            cats = ["batting_score","bowling_score",
                    "fielding_score","allrounder_score"]
            labs = ["Batting","Bowling","Fielding","Overall"]
            colors_radar = ["#00d4aa","#f0b429","#e63946","#3a86ff","#8b5cf6"]
            for idx, (_, row) in enumerate(top5.iterrows()):
                fig.add_trace(go.Scatterpolar(
                    r=[row[c] for c in cats], theta=labs,
                    fill="toself", name=row["player"],
                    line_color=colors_radar[idx % len(colors_radar)],
                    fillcolor=hex_to_rgba(colors_radar[idx % len(colors_radar)], 0.15)
                ))
            fig.update_layout(
                **plotly_dark(),
                polar=dict(
                    bgcolor="rgba(0,0,0,0)",
                    radialaxis=dict(visible=True, range=[0,100],
                                   gridcolor="#1e2d3d", color="#7d8590"),
                    angularaxis=dict(gridcolor="#1e2d3d", color="#7d8590")
                ),
                title="Top 5 All-rounders — Radar",
                legend=dict(font_color="#e6edf3", bgcolor="rgba(0,0,0,0)")
            )
            st.plotly_chart(fig, use_container_width=True)

            # Stacked bar
            fig2 = px.bar(df, x="player",
                          y=["batting_score","bowling_score","fielding_score"],
                          title="Score Breakdown",
                          barmode="stack",
                          color_discrete_sequence=["#00d4aa","#e63946","#3a86ff"])
            fig2.update_layout(**plotly_dark(), xaxis_tickangle=-35,
                               legend=dict(font_color="#e6edf3",
                                           bgcolor="rgba(0,0,0,0)"))
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("⚠️ Run all scorers first!")

# ──────────────────────────────────────────────────────
# TAB 4 — HEAD TO HEAD
# ──────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="section-title">Head to Head Comparison</div>',
                unsafe_allow_html=True)
    all_players = []
    if scores["batting"] is not None:
        pcol = get_player_col(scores["batting"])
        all_players = sorted(scores["batting"][pcol].tolist())

    if all_players:
        col1, mid, col2 = st.columns([5, 1, 5])
        with col1:
            p1 = st.selectbox("🔵 Select Player 1", all_players, index=0)
        with mid:
            st.markdown('<div class="vs-badge">VS</div>', unsafe_allow_html=True)
        with col2:
            p2 = st.selectbox("🔴 Select Player 2", all_players, index=1)

        def get_stats(name):
            s  = {"player": name, "team": PLAYER_TEAMS.get(name, "Unknown")}
            ti = get_team_info(name)
            s["color"] = ti["color"]
            s["emoji"] = ti["emoji"]
            if scores["batting"] is not None:
                pcol = get_player_col(scores["batting"])
                row  = scores["batting"][scores["batting"][pcol] == name]
                if not row.empty:
                    for col in ["batting_score","average","strike_rate",
                                "boundary_pct","matches","total_runs"]:
                        if col in row.columns:
                            s[col] = float(row[col].values[0])
            if scores["bowling"] is not None:
                pcol = get_player_col(scores["bowling"])
                row  = scores["bowling"][scores["bowling"][pcol] == name]
                if not row.empty:
                    for col in ["bowling_score","economy","wickets","dot_ball_pct"]:
                        if col in row.columns:
                            s[col] = float(row[col].values[0])
            if scores["allrounder"] is not None:
                row = scores["allrounder"][
                    scores["allrounder"]["player"] == name]
                if not row.empty and "allrounder_score" in row.columns:
                    s["allrounder_score"] = float(
                        row["allrounder_score"].values[0])
            return s

        s1 = get_stats(p1)
        s2 = get_stats(p2)

        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="h2h-card"
                 style="border-top:3px solid {s1.get("color","#00d4aa")}">
                <div style="font-size:0.7rem;letter-spacing:2px;color:#7d8590;
                     text-transform:uppercase">Player 1</div>
                <div class="h2h-name" style="color:{s1.get("color","#00d4aa")}">
                    {s1["emoji"]} {p1}</div>
                <div style="font-size:0.75rem;color:#7d8590;margin-bottom:1rem">
                    {s1.get("team","Unknown")}</div>
                <div class="h2h-score" style="color:{s1.get("color","#00d4aa")}">
                    {s1.get("batting_score", s1.get("allrounder_score", "—")):.1f}
                </div>
                <div style="font-size:0.7rem;color:#7d8590;
                     letter-spacing:1px;text-transform:uppercase">
                     Batting Score</div>
                <div style="margin-top:1rem;font-size:0.85rem;color:#e6edf3">
                    🏏 {int(s1.get("total_runs",0))} runs &nbsp;|&nbsp;
                    SR {s1.get("strike_rate",0):.1f} &nbsp;|&nbsp;
                    Avg {s1.get("average",0):.1f}
                </div>
            </div>""", unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="h2h-card"
                 style="border-top:3px solid {s2.get("color","#e63946")}">
                <div style="font-size:0.7rem;letter-spacing:2px;color:#7d8590;
                     text-transform:uppercase">Player 2</div>
                <div class="h2h-name" style="color:{s2.get("color","#e63946")}">
                    {s2["emoji"]} {p2}</div>
                <div style="font-size:0.75rem;color:#7d8590;margin-bottom:1rem">
                    {s2.get("team","Unknown")}</div>
                <div class="h2h-score" style="color:{s2.get("color","#e63946")}">
                    {s2.get("batting_score", s2.get("allrounder_score", "—")):.1f}
                </div>
                <div style="font-size:0.7rem;color:#7d8590;
                     letter-spacing:1px;text-transform:uppercase">
                     Batting Score</div>
                <div style="margin-top:1rem;font-size:0.85rem;color:#e6edf3">
                    🏏 {int(s2.get("total_runs",0))} runs &nbsp;|&nbsp;
                    SR {s2.get("strike_rate",0):.1f} &nbsp;|&nbsp;
                    Avg {s2.get("average",0):.1f}
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Comparison bar chart
        metrics = []
        for key, label in [
            ("batting_score","Batting Score"),
            ("bowling_score","Bowling Score"),
            ("average","Average"),
            ("strike_rate","Strike Rate"),
            ("boundary_pct","Boundary %")]:
            if key in s1 or key in s2:
                metrics.append({"Metric": label,
                                 p1: s1.get(key, 0),
                                 p2: s2.get(key, 0)})
        if metrics:
            cdf = pd.DataFrame(metrics).melt(
                id_vars="Metric", var_name="Player", value_name="Value")
            fig = px.bar(cdf, x="Metric", y="Value",
                         color="Player", barmode="group",
                         title=f"⚔️  {p1}  vs  {p2}",
                         color_discrete_map={
                             p1: s1.get("color","#00d4aa"),
                             p2: s2.get("color","#e63946")})
            fig.update_layout(**plotly_dark(),
                              legend=dict(font_color="#e6edf3",
                                          bgcolor="rgba(0,0,0,0)"))
            st.plotly_chart(fig, use_container_width=True)

        # Winner table
        skip = {"player","team","color","emoji"}
        rows = []
        for k in sorted((set(s1) | set(s2)) - skip):
            v1, v2 = s1.get(k, "—"), s2.get(k, "—")
            winner = ""
            if isinstance(v1,(int,float)) and isinstance(v2,(int,float)):
                winner = (f"✅ {p1}" if (v1 < v2 if k == "economy" else v1 > v2)
                          else f"✅ {p2}" if (v2 < v1 if k == "economy" else v2 > v1)
                          else "🤝 Tie")
            rows.append({"Stat": k.replace("_"," ").title(),
                         p1: round(v1,2) if isinstance(v1,float) else v1,
                         p2: round(v2,2) if isinstance(v2,float) else v2,
                         "Winner": winner})
        st.dataframe(pd.DataFrame(rows), use_container_width=True,
                     hide_index=True)

# ──────────────────────────────────────────────────────
# TAB 5 — SEASON TRENDS
# ──────────────────────────────────────────────────────
with tab5:
    st.markdown('<div class="section-title">Season by Season Trends</div>',
                unsafe_allow_html=True)
    raw = load_raw_sample()
    if raw is not None and "season" in raw.columns:
        sr = raw.groupby("season").agg(
            total_runs  =("runs_off_bat","sum"),
            total_balls =("runs_off_bat","count"),
            matches     =("match_id","nunique")
        ).reset_index()
        sr["avg_score"] = (sr["total_runs"] / sr["matches"]).round(1)
        sr["run_rate"]  = (sr["total_runs"] / sr["total_balls"] * 6).round(2)
        sr["season"]    = sr["season"].astype(str)
        sr = sr.sort_values("season")

        col1, col2 = st.columns(2)
        with col1:
            fig = px.line(sr, x="season", y="avg_score", markers=True,
                          title="Average Team Score per Match",
                          labels={"avg_score":"Avg Score","season":"Season"})
            fig.update_traces(line_color="#00d4aa", line_width=3,
                              marker=dict(size=8, color="#f0b429",
                                          line=dict(color="#00d4aa", width=2)))
            fig.update_layout(**plotly_dark())
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig2 = px.bar(sr, x="season", y="run_rate",
                          color="run_rate",
                          color_continuous_scale=[[0,"#1e2d3d"],[1,"#00d4aa"]],
                          title="Run Rate by Season",
                          labels={"run_rate":"Run Rate","season":"Season"},
                          text=sr["run_rate"].round(2))
            fig2.update_traces(textposition="outside", textfont_color="#e6edf3")
            fig2.update_layout(**plotly_dark(), coloraxis_showscale=False)
            st.plotly_chart(fig2, use_container_width=True)

        # Matches per season
        fig3 = px.bar(sr, x="season", y="matches",
                      color="matches",
                      color_continuous_scale=[[0,"#1e2d3d"],[1,"#f0b429"]],
                      title="Number of Matches per Season",
                      text="matches")
        fig3.update_traces(textposition="outside", textfont_color="#e6edf3")
        fig3.update_layout(**plotly_dark(), coloraxis_showscale=False)
        st.plotly_chart(fig3, use_container_width=True)

        st.markdown('<div class="section-title">Season Data Table</div>',
                    unsafe_allow_html=True)
        st.dataframe(sr[["season","matches","total_runs",
                          "avg_score","run_rate"]].sort_values(
                              "season", ascending=False),
                     use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ Raw data needed for season trends!")

# ──────────────────────────────────────────────────────
# TAB 6 — BEST XI
# ──────────────────────────────────────────────────────
with tab6:
    st.markdown('<div class="section-title">🌟 Predicted Best XI — IPL 2025</div>',
                unsafe_allow_html=True)
    if (scores["batting"] is not None and
        scores["bowling"] is not None and
        scores["allrounder"] is not None):

        bat_df  = prep_df(scores["batting"].copy(),
                          "batting_score", min_matches, 30)
        bowl_df = prep_df(scores["bowling"].copy(),
                          "bowling_score", min_matches, 30)
        ar_df   = prep_df(scores["allrounder"].copy(),
                          "allrounder_score", min_matches, 20)

        best_xi = []
        added   = set()

        # WK
        wk_list = ["MS Dhoni","RR Pant","Sanju Samson",
                   "Q de Kock","Ishan Kishan","KL Rahul"]
        wk = next((p for p in wk_list
                   if p in bat_df["player"].values), None)
        if wk:
            row = bat_df[bat_df["player"] == wk].iloc[0]
            best_xi.append({"role":"🧤 Wicketkeeper", "player": wk,
                "score": row["batting_score"],
                "stat": f"Avg {row['average']:.1f}  •  SR {row['strike_rate']:.1f}"})
            added.add(wk)

        # 4 Batsmen
        count = 0
        for _, row in bat_df.iterrows():
            if row["player"] not in added and count < 4:
                best_xi.append({"role": f"🏏 Batsman {count+1}",
                    "player": row["player"],
                    "score": row["batting_score"],
                    "stat": f"Avg {row['average']:.1f}  •  SR {row['strike_rate']:.1f}"})
                added.add(row["player"]); count += 1

        # 3 All-rounders
        count = 0
        for _, row in ar_df.iterrows():
            if row["player"] not in added and count < 3:
                best_xi.append({"role": f"🤸 All-rounder {count+1}",
                    "player": row["player"],
                    "score": row["allrounder_score"],
                    "stat": f"Bat {row['batting_score']:.0f}  •  Bowl {row['bowling_score']:.0f}"})
                added.add(row["player"]); count += 1

        # 3 Bowlers
        count = 0
        for _, row in bowl_df.iterrows():
            if row["player"] not in added and count < 3:
                best_xi.append({"role": f"🎯 Bowler {count+1}",
                    "player": row["player"],
                    "score": row["bowling_score"],
                    "stat": f"Econ {row['economy']:.2f}  •  {int(row['wickets'])} wkts"})
                added.add(row["player"]); count += 1

        # Display XI in cricket formation style
        col1, col2 = st.columns([2, 1])
        with col1:
            for item in best_xi:
                color = get_team_color(item["player"])
                team  = PLAYER_TEAMS.get(item["player"], "Unknown")
                ti    = get_team_info(item["player"])
                st.markdown(f"""
                <div class="xi-card" style="border-left:3px solid {color}">
                    <div class="xi-role">{item["role"]}</div>
                    <div>
                        <div class="xi-name">{avatar_html(item["player"], 36)}{item["player"]}</div>
                        <div style="font-size:0.7rem;color:#7d8590">{team}</div>
                        <div style="font-size:0.75rem;color:#e6edf3;margin-top:2px">
                            {item["stat"]}</div>
                    </div>
                    <div class="xi-score" style="color:{color}">
                        {item["score"]:.1f}</div>
                </div>""", unsafe_allow_html=True)

        with col2:
            # Donut chart of XI composition
            roles   = ["Wicketkeeper","Batsmen","All-rounders","Bowlers"]
            values  = [1, 4, 3, 3]
            colors  = ["#3a86ff","#00d4aa","#f0b429","#e63946"]
            fig = go.Figure(go.Pie(
                labels=roles, values=values,
                hole=0.6,
                marker_colors=colors,
                textinfo="label+value",
                textfont_color="#e6edf3"
            ))
            fig.update_layout(
                **plotly_dark(),
                title="Team Composition",
                showlegend=False,
                annotations=[dict(text="Best<br>XI",
                                  x=0.5, y=0.5, font_size=16,
                                  font_color="#e6edf3",
                                  showarrow=False)]
            )
            st.plotly_chart(fig, use_container_width=True)

            # Score bars
            st.markdown('<div class="section-title" style="font-size:1rem">Score Breakdown</div>',
                        unsafe_allow_html=True)
            xi_df = pd.DataFrame(best_xi)
            fig2  = px.bar(xi_df, x="score", y="player",
                           orientation="h",
                           color="score",
                           color_continuous_scale=[[0,"#1e2d3d"],[1,"#00d4aa"]],
                           title="",
                           labels={"score":"Score","player":""})
            fig2.update_layout(**plotly_dark(), coloraxis_showscale=False,
                               height=400)
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("⚠️ Run all scorers first!")

# ──────────────────────────────────────────────────────
# TAB 7 — PLAYER SEARCH
# ──────────────────────────────────────────────────────
with tab7:
    st.markdown('<div class="section-title">Player Search</div>',
                unsafe_allow_html=True)
    search = st.text_input("", placeholder="🔍  Search — e.g. Kohli, Bumrah, Narine...",
                           label_visibility="collapsed")

    if search:
        found = False

        for dtype, score_col, label, icon in [
            ("batting",  "batting_score",  "Batting",    "🏏"),
            ("bowling",  "bowling_score",  "Bowling",    "🎯"),
            ("allrounder","allrounder_score","All-rounder","🤸"),
        ]:
            if scores[dtype] is not None:
                df    = scores[dtype].copy()
                pcol  = get_player_col(df)
                result= df[df[pcol].str.contains(search, case=False, na=False)]
                if not result.empty:
                    found = True
                    name  = result.iloc[0][pcol]
                    ti    = get_team_info(name)
                    if not found or dtype == "batting":
                        st.markdown(f"""
                        <div class="h2h-card"
                             style="border-top:3px solid {ti["color"]};
                                    max-width:400px;margin-bottom:1rem">
                            <div class="h2h-name" style="color:{ti["color"]}">
                                {ti["emoji"]} {name}</div>
                            <div style="font-size:0.75rem;color:#7d8590">
                                {ti["team_name"]}</div>
                            <div class="h2h-score" style="color:{ti["color"]}">
                                {result.iloc[0][score_col]:.1f}</div>
                            <div style="font-size:0.7rem;color:#7d8590;
                                 letter-spacing:1px;text-transform:uppercase">
                                 {label} Score</div>
                        </div>""", unsafe_allow_html=True)

                    st.markdown(f"**{icon} {label} Stats**")
                    st.dataframe(result, use_container_width=True,
                                 hide_index=True)

        if not found:
            st.markdown(f"""
            <div style="text-align:center;padding:3rem;color:#7d8590">
                <div style="font-size:3rem">🔍</div>
                <div style="font-size:1.2rem;margin-top:0.5rem">
                    No results for "<b style="color:#e6edf3">{search}</b>"
                </div>
                <div style="font-size:0.85rem;margin-top:0.3rem">
                    Try a different name or partial name</div>
            </div>""", unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:2rem 0 1rem;
     border-top:1px solid #1e2d3d;margin-top:2rem;
     font-size:0.75rem;color:#7d8590;letter-spacing:1px">
    🏏 &nbsp; CRICKET ANALYTICS PLATFORM &nbsp; • &nbsp;
    Data: Cricsheet.org &nbsp; • &nbsp;
    Built with Python · Streamlit · Plotly &nbsp; • &nbsp;
    100% Free & Open Source &nbsp; • &nbsp;
    🏆 IPL 2025 — RCB Champions
</div>
""", unsafe_allow_html=True)