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
from dashboard.ipl_teams import get_team_color, get_team_info, PLAYER_TEAMS, IPL_TEAMS, avatar_html, RETIRED_PLAYERS
from analytics.team_analytics import (get_team_players, calculate_team_stats,
    generate_swot, get_player_matchups, get_best_xi_vs_opponent)

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
    /* Dark side */
    --dark:      #0d1117;
    --dark2:     #161b22;
    --dark3:     #21262d;
    /* Light accents */
    --light:     #f0f6ff;
    --light2:    #e8f4f8;
    /* Brand colors */
    --accent:    #1db954;
    --accent2:   #17a844;
    --gold:      #ffd700;
    --gold2:     #ffaa00;
    --red:       #ff4444;
    --blue:      #4fc3f7;
    /* Text */
    --text:      #f0f6ff;
    --text-dark: #0d1117;
    --muted:     #8b949e;
    /* Effects */
    --glow-green: 0 0 30px rgba(29,185,84,0.4);
    --glow-gold:  0 0 30px rgba(255,215,0,0.3);
    --card-bg:    rgba(22,27,34,0.9);
    --card-light: rgba(240,246,255,0.95);
}

html, body, [data-testid="stAppViewContainer"] {
    background: #0d1117 !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif;
}

[data-testid="stSidebar"] { display: none !important; }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── HERO ── */
.hero {
    background: linear-gradient(160deg, #0d1117 0%, #1a2332 40%, #0d2137 100%);
    border: 1px solid rgba(29,185,84,0.3);
    border-radius: 20px;
    padding: 3rem 2rem 2.5rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
    text-align: center;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.05);
}
.hero::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: 
        radial-gradient(ellipse 60% 50% at 20% 50%, rgba(29,185,84,0.08) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 80% 50%, rgba(255,215,0,0.06) 0%, transparent 60%);
    pointer-events: none;
}
.hero-eyebrow {
    font-size: 0.7rem;
    letter-spacing: 6px;
    text-transform: uppercase;
    color: var(--accent);
    font-weight: 600;
    margin-bottom: 0.8rem;
}
.hero-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 4rem;
    font-weight: 700;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: #ffffff;
    margin: 0;
    line-height: 1;
    text-shadow: 0 0 40px rgba(29,185,84,0.3);
}
.hero-title span {
    background: linear-gradient(135deg, #1db954 0%, #ffd700 50%, #1db954 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: gradientShift 4s linear infinite;
}
.hero-sub {
    color: var(--muted);
    font-size: 0.85rem;
    letter-spacing: 5px;
    text-transform: uppercase;
    margin-top: 0.8rem;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: linear-gradient(135deg, #ffd700, #ffaa00);
    color: #000;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
    font-size: 0.78rem;
    letter-spacing: 2px;
    padding: 5px 16px;
    border-radius: 30px;
    margin-top: 1rem;
    text-transform: uppercase;
    box-shadow: 0 4px 15px rgba(255,215,0,0.4);
}
.hero-stats-strip {
    display: flex;
    justify-content: center;
    gap: 3rem;
    margin-top: 1.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid rgba(255,255,255,0.06);
}
.hero-stat-item { text-align: center; }
.hero-stat-num {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--accent);
    line-height: 1;
}
.hero-stat-lbl {
    font-size: 0.65rem;
    letter-spacing: 2px;
    color: var(--muted);
    text-transform: uppercase;
    margin-top: 0.2rem;
}
@keyframes gradientShift {
    0%   { background-position: 0% center; }
    100% { background-position: 200% center; }
}

/* ── LIGHT CARDS (stat summary) ── */
.stat-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin: 1rem 0;
}
.stat-card {
    background: linear-gradient(145deg, #f8faff, #eef4ff);
    border: none;
    border-radius: 16px;
    padding: 1.2rem 1rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: transform 0.25s, box-shadow 0.25s;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15), 0 1px 0 rgba(255,255,255,0.8) inset;
    color: #0d1117;
}
.stat-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 40px rgba(29,185,84,0.25), 0 1px 0 rgba(255,255,255,0.8) inset;
}
.stat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #1db954, #ffd700, #1db954);
    background-size: 200% auto;
    animation: gradientShift 3s linear infinite;
}
.stat-value {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: #1db954;
    line-height: 1;
}
.stat-label {
    font-size: 0.68rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #64748b;
    margin-top: 0.3rem;
}
.stat-name {
    font-size: 0.82rem;
    color: #1e293b;
    margin-top: 0.3rem;
    font-weight: 600;
}

/* ── DARK PLAYER CARDS ── */
.player-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
    margin: 1rem 0;
}
.player-card {
    background: var(--card-bg);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 1.2rem;
    position: relative;
    overflow: hidden;
    transition: transform 0.25s, box-shadow 0.25s, border-color 0.25s;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
.player-card:hover {
    transform: translateY(-4px);
    border-color: rgba(29,185,84,0.4);
    box-shadow: var(--glow-green), 0 8px 30px rgba(0,0,0,0.4);
}
.player-rank {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.5rem;
    font-weight: 700;
    color: rgba(255,255,255,0.06);
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
.player-stats { display: flex; gap: 0.8rem; margin-top: 0.5rem; }
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

/* ── LEADERBOARD — alternating light/dark ── */
.lb-row {
    display: grid;
    grid-template-columns: 40px 1fr 80px 80px 80px 90px;
    align-items: center;
    padding: 0.75rem 1rem;
    border-radius: 10px;
    margin-bottom: 0.4rem;
    background: rgba(22,27,34,0.8);
    border: 1px solid rgba(255,255,255,0.05);
    transition: all 0.2s;
}
.lb-row:hover {
    background: rgba(29,185,84,0.08);
    border-color: rgba(29,185,84,0.25);
    transform: translateX(4px);
    box-shadow: -3px 0 0 #1db954;
}
.lb-row.gold   { border-left: 3px solid #ffd700; background: rgba(255,215,0,0.04); }
.lb-row.silver { border-left: 3px solid #94a3b8; }
.lb-row.bronze { border-left: 3px solid #cd7f32; }
.lb-rank { font-family:'Rajdhani',sans-serif; font-size:1.3rem; font-weight:700; color:var(--muted); }
.lb-rank.r1 { color:#ffd700; }
.lb-rank.r2 { color:#94a3b8; }
.lb-rank.r3 { color:#cd7f32; }
.lb-name  { font-weight:600; font-size:0.92rem; color:var(--text); }
.lb-team  { font-size:0.68rem; color:var(--muted); }
.lb-stat  { text-align:right; font-size:0.82rem; color:var(--muted); }
.lb-score { text-align:right; font-family:'Rajdhani',sans-serif;
            font-size:1.3rem; font-weight:700; color:#1db954; }

/* ── SECTION TITLES ── */
.section-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.4rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--text);
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 1.8rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid rgba(29,185,84,0.3);
}
.section-title::before {
    content: '';
    display: inline-block;
    width: 4px;
    height: 1.4rem;
    background: linear-gradient(180deg, #1db954, #ffd700);
    border-radius: 2px;
    flex-shrink: 0;
}

/* ── TABS ── */
[data-testid="stTabs"] {
    background: rgba(13,17,23,0.8);
    border-radius: 12px;
    padding: 4px;
}
[data-testid="stTabs"] button {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
    border-radius: 8px !important;
    padding: 6px 12px !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #ffffff !important;
    background: rgba(29,185,84,0.15) !important;
    border-bottom-color: #1db954 !important;
}

/* H2H cards */
.h2h-card {
    background: var(--card-bg);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 30px rgba(0,0,0,0.3);
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
    background: var(--card-bg);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 0.8rem 1rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 0.5rem;
    transition: all 0.2s;
}
.xi-card:hover {
    transform: translateX(5px);
    border-color: rgba(29,185,84,0.3);
    box-shadow: -3px 0 0 #1db954;
}
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
    color: var(--text);
}
.xi-score {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: #1db954;
}

/* Progress bars */
.progress-wrap { margin: 0.3rem 0; }
.progress-label {
    display:flex; justify-content:space-between;
    font-size:0.72rem; color:var(--muted); margin-bottom:3px;
}
.progress-bar { height: 5px; background: rgba(255,255,255,0.08); border-radius: 3px; overflow: hidden; }
.progress-fill {
    height: 100%;
    border-radius: 3px;
    background: linear-gradient(90deg, #1db954, #ffd700);
}

/* Filter bar */
[data-testid="stSelectbox"] > div, [data-testid="stNumberInput"] > div {
    background: rgba(22,27,34,0.9) !important;
    border-color: rgba(255,255,255,0.1) !important;
    color: var(--text) !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--dark); }
::-webkit-scrollbar-thumb { background: #1db954; border-radius: 2px; }

/* Sidebar hidden */
.sidebar-logo { display: none; }
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
    # Remove retired players
    pcol2 = "player" if "player" in df.columns else df.columns[0]
    df = df[~df[pcol2].isin(RETIRED_PLAYERS)]
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
    <div style="text-align:center;margin-bottom:1rem;">
        <svg width="110" height="110" viewBox="0 0 447.983 447.983" xmlns="http://www.w3.org/2000/svg">
            <g transform="translate(0 -1020.36)">
                <circle cx="223.947" cy="1244.292" r="210.113" fill="#1db954" opacity="0.12"/>
                <circle cx="223.947" cy="1244.292" r="187.992" fill="#0a1628" stroke="#1db954" stroke-width="3" opacity="0.9"/>
                <circle cx="223.947" cy="1244.292" r="143.976" fill="none" stroke="#4fc3f7" stroke-width="3" opacity="0.5"/>
                <circle cx="223.947" cy="1244.292" r="130.855" fill="none" stroke="#4fc3f7" stroke-width="1.5" opacity="0.25"/>
                <rect x="191.939" y="1180.276" width="64.016" height="128.031" rx="3" fill="#c8a96e" opacity="0.9"/>
                <rect x="208.003" y="1196.339" width="32.007" height="96.023" rx="2" fill="rgba(255,255,255,0.85)"/>
                <rect x="175.995" y="1204.253" width="96.024" height="8" rx="2" fill="#ffd700"/>
                <rect x="175.995" y="1276.269" width="96.024" height="8" rx="2" fill="#ffd700"/>
                <path d="M250.986,1021.998c-51.666-6.268-105.523,5.381-151.531,36.157c-3.676,2.459-4.663,7.434-2.203,11.109s7.433,4.662,11.109,2.203c85.537-57.216,199.905-43.352,269.281,32.658c69.376,76.008,72.768,191.152,8,271.125c-64.768,79.971-178.109,100.598-266.875,48.531s-126.1-161.066-87.906-256.625c1.814-4.029,0.017-8.766-4.012-10.58c-4.029-1.813-8.766-0.018-10.58,4.012c-0.093,0.207-0.177,0.418-0.252,0.631c-41.087,102.799-0.834,220.332,94.656,276.344s217.732,33.811,287.406-52.219c69.674-86.031,66.007-210.232-8.625-292c-37.316-40.883-86.803-65.077-138.469-71.344V1021.998z" fill="#1db954" opacity="0.9"/>
                <path d="M242.392,1085.343c-58.03-6.693-117.219,18.84-151.438,70c-45.625,68.215-32.155,160.059,31.125,212.314c63.28,52.252,156.022,48.111,214.375-9.594c3.187-3.061,3.288-8.125,0.227-11.313c-3.061-3.188-8.126-3.289-11.313-0.227c-0.056,0.053-0.111,0.107-0.165,0.162c-52.61,52.025-135.885,55.768-192.938,8.656s-69.135-129.592-28-191.094s121.955-81.836,187.281-47.094c65.326,34.74,93.683,113.137,65.688,181.625c-1.674,4.09,0.285,8.764,4.375,10.438s8.763-0.285,10.438-4.375c31.051-75.965-0.512-163.279-72.969-201.813C280.965,1093.397,261.735,1087.575,242.392,1085.343z" fill="#ffd700" opacity="0.8"/>
                <path d="M73.173,1081.624c-2.078,0.033-4.062,0.873-5.531,2.344c-13.77,13.426-25.755,28.574-35.656,45.063c-2.278,3.789-1.054,8.707,2.734,10.984s8.706,1.055,10.984-2.734c9.194-15.309,20.307-29.377,33.094-41.844c3.21-3.037,3.351-8.1,0.315-11.311C77.572,1082.497,75.417,1081.589,73.173,1081.624z" fill="#1db954" opacity="0.8"/>
            </g>
        </svg>
    </div>
    <div class="hero-title">CRICKET <span>ANALYTICS</span></div>
    <div class="hero-sub">IPL Intelligence Platform &nbsp;·&nbsp; 2008 – 2025</div>
    <div style="margin-top:0.8rem;"><span class="hero-badge">🏆 IPL 2025 — RCB Champions</span></div>
    <div class="hero-stats-strip">
        <div class="hero-stat-item"><div class="hero-stat-num">18</div><div class="hero-stat-lbl">Seasons</div></div>
        <div class="hero-stat-item"><div class="hero-stat-num">1000+</div><div class="hero-stat-lbl">Players</div></div>
        <div class="hero-stat-item"><div class="hero-stat-num">10</div><div class="hero-stat-lbl">Teams</div></div>
        <div class="hero-stat-item"><div class="hero-stat-num">4</div><div class="hero-stat-lbl">Analytics</div></div>
    </div>
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
tab1,tab2,tab3,tab4,tab5,tab6,tab7,tab8 = st.tabs([
    "🏏 BATTING", "🎯 BOWLING", "⚡ ALL-ROUNDERS",
    "⚔️ HEAD TO HEAD", "📈 SEASON TRENDS",
    "👑 BEST XI", "🔎 PLAYER SEARCH", "🏟️ TEAM INTEL"
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
        st.markdown('<div class="section-title"><svg width="20" height="20" viewBox="0 0 465 465" style="vertical-align:middle;margin-right:8px;flex-shrink:0" xmlns="http://www.w3.org/2000/svg"><g transform="translate(0 -540.36)"><path fill="#ffffff" d="M396.7,608.16c-43.9-43.7-102.2-67.8-164.2-67.8c-62.5,0-120.9,24.1-164.7,67.8C24.1,651.86,0,710.36,0,772.86c0,62,24.1,120.3,67.8,164.2c43.9,44,102.4,68.3,164.7,68.3c61.9,0,120.2-24.3,164.2-68.3s68.3-102.4,68.3-164.2C465,710.56,440.7,652.06,396.7,608.16z M15,772.86c0-119.9,97.6-217.5,217.5-217.5c35.5,0,69,8.5,98.6,23.7L38.7,871.46C23.6,841.86,15,808.36,15,772.86z M106.8,950.26l19-19l-10.6-10.6l-20.4,20.4c-11.4-9.3-21.8-19.8-31.1-31.1l19.7-19.7l-10.6-10.6l-18.3,18.3c-2.9-4.1-5.7-8.4-8.3-12.8l298.5-298.5c4.4,2.6,8.6,5.4,12.8,8.3l-10.8,10.8l10.6,10.6l12.3-12.3c11.3,9.2,21.6,19.4,30.8,30.6l-11.6,12.3l10.9,10.3l9.9-10.5c2.9,4,5.6,8.1,8.2,12.3l-299.1,299.1C114.6,955.66,110.6,953.06,106.8,950.26z M232.5,990.36c-36.1,0-70.2-8.9-100.2-24.5l293.2-293.2c15.7,30,24.5,64.1,24.5,100.2C450,892.76,352.4,990.36,232.5,990.36z"/><rect fill="#111111" x="287.32" y="734.124" transform="matrix(-0.7071 -0.7071 0.7071 -0.7071 -28.2602 1491.7417)" width="15" height="35.2"/><rect fill="#111111" x="95.693" y="842.467" transform="matrix(-0.7071 -0.7071 0.7071 -0.7071 -431.998 1541.1948)" width="15" height="35.2"/><rect fill="#111111" x="132.844" y="804.948" transform="matrix(0.7071 0.7071 -0.7071 0.7071 622.735 141.6802)" width="15" height="35.2"/><rect fill="#111111" x="207.692" y="730.454" transform="matrix(0.7071 0.7071 -0.7071 0.7071 591.9841 66.9372)" width="15" height="35.2"/><rect fill="#111111" x="170.342" y="767.733" transform="matrix(0.7071 0.7071 -0.7071 0.7071 607.4029 104.265)" width="15" height="35.2"/><rect fill="#111111" x="244.844" y="692.963" transform="matrix(0.7071 0.7071 -0.7071 0.7071 576.3555 29.6861)" width="15" height="35.2"/><rect fill="#111111" x="282.335" y="655.712" transform="matrix(0.7071 0.7071 -0.7071 0.7071 560.9943 -7.7354)" width="15" height="35.2"/><rect fill="#111111" x="319.557" y="618.292" transform="matrix(0.7071 0.7071 -0.7071 0.7071 545.4363 -45.0157)" width="15" height="35.2"/><rect fill="#111111" x="137.964" y="883.536" transform="matrix(-0.7071 -0.7071 0.7071 -0.7071 -388.8769 1641.194)" width="15" height="35.2"/><rect fill="#111111" x="175.328" y="846.13" transform="matrix(-0.7071 -0.7071 0.7071 -0.7071 -298.643 1603.7579)" width="15" height="35.2"/><rect fill="#111111" x="249.97" y="771.53" transform="matrix(-0.7071 -0.7071 0.7071 -0.7071 -118.47 1529.1877)" width="15" height="35.2"/><rect fill="#111111" x="212.677" y="808.865" transform="matrix(-0.7071 -0.7071 0.7071 -0.7071 -208.5332 1566.5532)" width="15" height="35.2"/><rect fill="#111111" x="324.683" y="696.859" transform="matrix(-0.7071 -0.7071 0.7071 -0.7071 61.8737 1454.547)" width="15" height="35.2"/><rect fill="#111111" x="361.962" y="659.524" transform="matrix(-0.7071 -0.7071 0.7071 -0.7071 151.9128 1417.1716)" width="15" height="35.2"/><circle fill="#111111" cx="357" cy="904.358" r="7.5"/></g></svg>Bowling Rankings</div>', unsafe_allow_html=True)
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

        st.markdown('<div class="section-title"><svg width="20" height="20" viewBox="0 0 465 465" style="vertical-align:middle;margin-right:8px;flex-shrink:0" xmlns="http://www.w3.org/2000/svg"><g transform="translate(0 -540.36)"><path fill="#ffffff" d="M396.7,608.16c-43.9-43.7-102.2-67.8-164.2-67.8c-62.5,0-120.9,24.1-164.7,67.8C24.1,651.86,0,710.36,0,772.86c0,62,24.1,120.3,67.8,164.2c43.9,44,102.4,68.3,164.7,68.3c61.9,0,120.2-24.3,164.2-68.3s68.3-102.4,68.3-164.2C465,710.56,440.7,652.06,396.7,608.16z M15,772.86c0-119.9,97.6-217.5,217.5-217.5c35.5,0,69,8.5,98.6,23.7L38.7,871.46C23.6,841.86,15,808.36,15,772.86z M106.8,950.26l19-19l-10.6-10.6l-20.4,20.4c-11.4-9.3-21.8-19.8-31.1-31.1l19.7-19.7l-10.6-10.6l-18.3,18.3c-2.9-4.1-5.7-8.4-8.3-12.8l298.5-298.5c4.4,2.6,8.6,5.4,12.8,8.3l-10.8,10.8l10.6,10.6l12.3-12.3c11.3,9.2,21.6,19.4,30.8,30.6l-11.6,12.3l10.9,10.3l9.9-10.5c2.9,4,5.6,8.1,8.2,12.3l-299.1,299.1C114.6,955.66,110.6,953.06,106.8,950.26z M232.5,990.36c-36.1,0-70.2-8.9-100.2-24.5l293.2-293.2c15.7,30,24.5,64.1,24.5,100.2C450,892.76,352.4,990.36,232.5,990.36z"/><rect fill="#111111" x="287.32" y="734.124" transform="matrix(-0.7071 -0.7071 0.7071 -0.7071 -28.2602 1491.7417)" width="15" height="35.2"/><rect fill="#111111" x="95.693" y="842.467" transform="matrix(-0.7071 -0.7071 0.7071 -0.7071 -431.998 1541.1948)" width="15" height="35.2"/><rect fill="#111111" x="132.844" y="804.948" transform="matrix(0.7071 0.7071 -0.7071 0.7071 622.735 141.6802)" width="15" height="35.2"/><rect fill="#111111" x="207.692" y="730.454" transform="matrix(0.7071 0.7071 -0.7071 0.7071 591.9841 66.9372)" width="15" height="35.2"/><rect fill="#111111" x="170.342" y="767.733" transform="matrix(0.7071 0.7071 -0.7071 0.7071 607.4029 104.265)" width="15" height="35.2"/><rect fill="#111111" x="244.844" y="692.963" transform="matrix(0.7071 0.7071 -0.7071 0.7071 576.3555 29.6861)" width="15" height="35.2"/><rect fill="#111111" x="282.335" y="655.712" transform="matrix(0.7071 0.7071 -0.7071 0.7071 560.9943 -7.7354)" width="15" height="35.2"/><rect fill="#111111" x="319.557" y="618.292" transform="matrix(0.7071 0.7071 -0.7071 0.7071 545.4363 -45.0157)" width="15" height="35.2"/><rect fill="#111111" x="137.964" y="883.536" transform="matrix(-0.7071 -0.7071 0.7071 -0.7071 -388.8769 1641.194)" width="15" height="35.2"/><rect fill="#111111" x="175.328" y="846.13" transform="matrix(-0.7071 -0.7071 0.7071 -0.7071 -298.643 1603.7579)" width="15" height="35.2"/><rect fill="#111111" x="249.97" y="771.53" transform="matrix(-0.7071 -0.7071 0.7071 -0.7071 -118.47 1529.1877)" width="15" height="35.2"/><rect fill="#111111" x="212.677" y="808.865" transform="matrix(-0.7071 -0.7071 0.7071 -0.7071 -208.5332 1566.5532)" width="15" height="35.2"/><rect fill="#111111" x="324.683" y="696.859" transform="matrix(-0.7071 -0.7071 0.7071 -0.7071 61.8737 1454.547)" width="15" height="35.2"/><rect fill="#111111" x="361.962" y="659.524" transform="matrix(-0.7071 -0.7071 0.7071 -0.7071 151.9128 1417.1716)" width="15" height="35.2"/><circle fill="#111111" cx="357" cy="904.358" r="7.5"/></g></svg>Bowling Rankings</div>', unsafe_allow_html=True)
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
            st.markdown('<div class="section-title"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" style="vertical-align:middle;margin-right:8px"><line x1="7" y1="4" x2="7" y2="20" stroke="white" stroke-width="2.5" stroke-linecap="round"/><line x1="12" y1="4" x2="12" y2="20" stroke="white" stroke-width="2.5" stroke-linecap="round"/><line x1="17" y1="4" x2="17" y2="20" stroke="white" stroke-width="2.5" stroke-linecap="round"/><line x1="5" y1="5" x2="9.5" y2="3.5" stroke="#f0b429" stroke-width="1.5" stroke-linecap="round"/><line x1="9.5" y1="3.5" x2="14.5" y2="3.5" stroke="#f0b429" stroke-width="1.5" stroke-linecap="round"/><line x1="14.5" y1="3.5" x2="19" y2="5" stroke="#f0b429" stroke-width="1.5" stroke-linecap="round"/></svg>All-Rounder Rankings</div>',
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
    st.markdown('<div class="section-title"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" style="vertical-align:middle;margin-right:8px"><line x1="4" y1="20" x2="20" y2="4" stroke="white" stroke-width="2.5" stroke-linecap="round"/><line x1="4" y1="4" x2="20" y2="20" stroke="#00d4aa" stroke-width="2.5" stroke-linecap="round"/></svg>Head to Head Comparison</div>',
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
    st.markdown('<div class="section-title"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" style="vertical-align:middle;margin-right:8px"><polyline points="3,17 9,11 13,15 21,7" stroke="#00d4aa" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/><polyline points="17,7 21,7 21,11" stroke="#00d4aa" stroke-width="2" fill="none" stroke-linecap="round"/></svg>Season by Season Trends</div>',
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

        st.markdown('<div class="section-title"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" style="vertical-align:middle;margin-right:8px"><line x1="7" y1="4" x2="7" y2="20" stroke="white" stroke-width="2.5" stroke-linecap="round"/><line x1="12" y1="4" x2="12" y2="20" stroke="white" stroke-width="2.5" stroke-linecap="round"/><line x1="17" y1="4" x2="17" y2="20" stroke="white" stroke-width="2.5" stroke-linecap="round"/><line x1="5" y1="5" x2="9.5" y2="3.5" stroke="#f0b429" stroke-width="1.5" stroke-linecap="round"/><line x1="9.5" y1="3.5" x2="14.5" y2="3.5" stroke="#f0b429" stroke-width="1.5" stroke-linecap="round"/><line x1="14.5" y1="3.5" x2="19" y2="5" stroke="#f0b429" stroke-width="1.5" stroke-linecap="round"/></svg>Season Data Table</div>',
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
    st.markdown('<div class="section-title"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" style="vertical-align:middle;margin-right:8px"><path d="M2 17L5 7l5 5 4-8 4 8 5-5 3 10H2z" fill="#f0b429" stroke="#d4990a" stroke-width="0.5"/><rect x="2" y="17" width="20" height="3" rx="1" fill="#f0b429"/></svg>Predicted Best XI — IPL 2025</div>',
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
            st.markdown('<div class="section-title" style="font-size:1rem"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" style="vertical-align:middle;margin-right:8px"><polyline points="3,17 9,11 13,15 21,7" stroke="#00d4aa" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/><polyline points="17,7 21,7 21,11" stroke="#00d4aa" stroke-width="2" fill="none" stroke-linecap="round"/></svg>Score Breakdown</div>',
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
    st.markdown('<div class="section-title"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" style="vertical-align:middle;margin-right:8px"><circle cx="11" cy="11" r="7" stroke="white" stroke-width="2"/><line x1="16.5" y1="16.5" x2="22" y2="22" stroke="white" stroke-width="2" stroke-linecap="round"/></svg>Player Search</div>',
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


def hex_to_rgba(hex_color, alpha=0.3):
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c*2 for c in hex_color)
    r, g, b = int(hex_color[0:2],16), int(hex_color[2:4],16), int(hex_color[4:6],16)
    return f"rgba({r},{g},{b},{alpha})"

# ──────────────────────────────────────────────────────
# TAB 8 — TEAM INTELLIGENCE
# ──────────────────────────────────────────────────────
with tab8:
    st.markdown('''<div class="section-title">
        🏟️ Team Intelligence — Opposition Analysis
    </div>''', unsafe_allow_html=True)

    team_list = list(IPL_TEAMS.keys())
    col1, mid, col2 = st.columns([5,1,5])
    with col1:
        team1 = st.selectbox("🔵 Your Team", team_list, index=0)
    with mid:
        st.markdown('<div class="vs-badge">VS</div>', unsafe_allow_html=True)
    with col2:
        team2 = st.selectbox("🔴 Opponent", team_list, index=1)

    if team1 == team2:
        st.warning("⚠️ Please select two different teams!")
    else:
        ti1 = IPL_TEAMS[team1]
        ti2 = IPL_TEAMS[team2]

        # Team header cards
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'''
            <div class="h2h-card" style="border-top:3px solid {ti1["color"]}">
                <div style="font-size:0.7rem;letter-spacing:2px;color:#7d8590;
                     text-transform:uppercase">Your Team</div>
                <div class="h2h-name" style="color:{ti1["color"]}">
                    {ti1["emoji"]} {team1}</div>
                <div style="font-size:2rem;font-family:'Rajdhani',sans-serif;
                     font-weight:700;color:{ti1["color"]};margin-top:0.5rem">
                    {ti1["short"]}</div>
            </div>''', unsafe_allow_html=True)
        with c2:
            st.markdown(f'''
            <div class="h2h-card" style="border-top:3px solid {ti2["color"]}">
                <div style="font-size:0.7rem;letter-spacing:2px;color:#7d8590;
                     text-transform:uppercase">Opponent</div>
                <div class="h2h-name" style="color:{ti2["color"]}">
                    {ti2["emoji"]} {team2}</div>
                <div style="font-size:2rem;font-family:'Rajdhani',sans-serif;
                     font-weight:700;color:{ti2["color"]};margin-top:0.5rem">
                    {ti2["short"]}</div>
            </div>''', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Load team stats
        stats1 = calculate_team_stats(team1, scores, min_matches)
        stats2 = calculate_team_stats(team2, scores, min_matches)

        # ── INTELLIGENCE SUBTABS ──────────────
        it1,it2,it3,it4,it5,it6 = st.tabs([
            "📊 SWOT","⚔️ Stats Comparison",
            "🏏 Batting","🎯 Bowling",
            "🌟 Best XI vs Opponent","🎯 Player Matchups"
        ])

        # SWOT
        with it1:
            swot1 = generate_swot(team1, stats1, stats2)
            swot2 = generate_swot(team2, stats2, stats1)

            st.markdown(f'<div class="section-title" style="font-size:1.1rem">'
                        f'{ti1["emoji"]} {team1} — SWOT Analysis</div>',
                        unsafe_allow_html=True)

            sc1,sc2,sc3,sc4 = st.columns(4)
            swot_styles = {
                "strengths":    ("#00d4aa","💪","STRENGTHS"),
                "weaknesses":   ("#e63946","⚠️","WEAKNESSES"),
                "opportunities":("#f0b429","🎯","OPPORTUNITIES"),
                "threats":      ("#8b5cf6","🚨","THREATS"),
            }
            for col_widget, (key, (color, icon, label)) in zip(
                [sc1,sc2,sc3,sc4], swot_styles.items()):
                with col_widget:
                    items_html = "".join(
                        f'<div style="padding:0.4rem 0;border-bottom:1px solid #1e2d3d;'
                        f'font-size:0.82rem;color:#e6edf3">{item}</div>'
                        for item in swot1[key]
                    )
                    st.markdown(f'''
                    <div style="background:#111820;border:1px solid {color}33;
                         border-top:3px solid {color};border-radius:10px;
                         padding:1rem;height:280px;overflow-y:auto">
                        <div style="font-size:0.7rem;letter-spacing:2px;
                             text-transform:uppercase;color:{color};
                             margin-bottom:0.8rem;font-weight:700">
                            {icon} {label}</div>
                        {items_html}
                    </div>''', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f'<div class="section-title" style="font-size:1.1rem">'
                        f'{ti2["emoji"]} {team2} — SWOT Analysis</div>',
                        unsafe_allow_html=True)

            sc1,sc2,sc3,sc4 = st.columns(4)
            for col_widget, (key, (color, icon, label)) in zip(
                [sc1,sc2,sc3,sc4], swot_styles.items()):
                with col_widget:
                    items_html = "".join(
                        f'<div style="padding:0.4rem 0;border-bottom:1px solid #1e2d3d;'
                        f'font-size:0.82rem;color:#e6edf3">{item}</div>'
                        for item in swot2[key]
                    )
                    st.markdown(f'''
                    <div style="background:#111820;border:1px solid {color}33;
                         border-top:3px solid {color};border-radius:10px;
                         padding:1rem;height:280px;overflow-y:auto">
                        <div style="font-size:0.7rem;letter-spacing:2px;
                             text-transform:uppercase;color:{color};
                             margin-bottom:0.8rem;font-weight:700">
                            {icon} {label}</div>
                        {items_html}
                    </div>''', unsafe_allow_html=True)

        # Stats Comparison
        with it2:
            stat_rows = [
                ("Avg Batting Score",   "avg_batting_score",  False),
                ("Avg Strike Rate",     "avg_strike_rate",    False),
                ("Avg Batting Average", "avg_average",        False),
                ("Avg Economy Rate",    "avg_economy",        True),
                ("Avg Dot Ball %",      "avg_dot_ball_pct",   False),
                ("Avg Bowling Score",   "avg_bowling_score",  False),
                ("Total Runs",          "total_runs",         False),
                ("Total Wickets",       "total_wickets",      False),
                ("Batting Depth",       "bat_depth",          False),
                ("Bowling Depth",       "bowl_depth",         False),
                ("All-rounder Depth",   "ar_depth",           False),
            ]
            rows = []
            for label, key, lower_better in stat_rows:
                v1 = stats1.get(key, "—")
                v2 = stats2.get(key, "—")
                if isinstance(v1,(int,float)) and isinstance(v2,(int,float)):
                    if lower_better:
                        winner = f"✅ {team1}" if v1 < v2 else f"✅ {team2}" if v2 < v1 else "🤝"
                    else:
                        winner = f"✅ {team1}" if v1 > v2 else f"✅ {team2}" if v2 > v1 else "🤝"
                else:
                    winner = "—"
                rows.append({"Metric":label, team1:v1, team2:v2, "Edge":winner})

            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            # Radar comparison
            radar_keys = ["avg_batting_score","avg_bowling_score",
                          "avg_strike_rate","avg_dot_ball_pct","ar_depth"]
            radar_labs  = ["Batting","Bowling","Strike Rate","Dot Ball%","All-rounders"]

            def normalize_val(v, vmin=0, vmax=100):
                if not isinstance(v,(int,float)): return 0
                return min(max((v - vmin)/(vmax - vmin)*100, 0), 100)

            norms = {"avg_batting_score":(0,80),"avg_bowling_score":(0,80),
                     "avg_strike_rate":(100,160),"avg_dot_ball_pct":(30,55),
                     "ar_depth":(0,5)}

            r1 = [normalize_val(stats1.get(k,0),*norms[k]) for k in radar_keys]
            r2 = [normalize_val(stats2.get(k,0),*norms[k]) for k in radar_keys]

            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=r1, theta=radar_labs, fill="toself", name=team1,
                line_color=ti1["color"],
                fillcolor=hex_to_rgba(ti1["color"], 0.25)))
            fig.add_trace(go.Scatterpolar(
                r=r2, theta=radar_labs, fill="toself", name=team2,
                line_color=ti2["color"],
                fillcolor=hex_to_rgba(ti2["color"], 0.25)))
            fig.update_layout(
                polar=dict(bgcolor="rgba(0,0,0,0)",
                    radialaxis=dict(visible=True,range=[0,100],
                        gridcolor="#1e2d3d",color="#7d8590"),
                    angularaxis=dict(gridcolor="#1e2d3d",color="#7d8590")),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#7d8590",
                title=f"{team1} vs {team2} — Team Radar",
                title_font_color="#e6edf3",
                legend=dict(font_color="#e6edf3",bgcolor="rgba(0,0,0,0)")
            )
            st.plotly_chart(fig, use_container_width=True)

        # Batting breakdown
        with it3:
            c1, c2 = st.columns(2)
            for col_w, tname, tinfo in [(c1,team1,ti1),(c2,team2,ti2)]:
                with col_w:
                    st.markdown(f'<div class="section-title" style="font-size:1rem">'
                                f'{tinfo["emoji"]} {tname}</div>',
                                unsafe_allow_html=True)
                    players = get_team_players(tname, scores)
                    if players["batting"]:
                        df = pd.DataFrame(players["batting"])
                        df = df[df["matches"] >= min_matches].head(8)
                        if "striker" in df.columns:
                            df = df.rename(columns={"striker":"player"})
                        for _, row in df.iterrows():
                            pname = row["player"]
                            st.markdown(f'''
                            <div class="lb-row">
                                <div></div>
                                <div><div class="lb-name">
                                    {avatar_html(pname,28)}{pname}</div>
                                </div>
                                <div class="lb-stat">{row.get("average",0):.1f}</div>
                                <div class="lb-stat">{row.get("strike_rate",0):.1f}</div>
                                <div class="lb-stat">{int(row.get("total_runs",0))}</div>
                                <div class="lb-score" style="color:{tinfo["color"]}">
                                    {row.get("batting_score",0):.1f}</div>
                            </div>''', unsafe_allow_html=True)
                    else:
                        st.info("No batting data available")

        # Bowling breakdown
        with it4:
            c1, c2 = st.columns(2)
            for col_w, tname, tinfo in [(c1,team1,ti1),(c2,team2,ti2)]:
                with col_w:
                    st.markdown(f'<div class="section-title" style="font-size:1rem">'
                                f'{tinfo["emoji"]} {tname}</div>',
                                unsafe_allow_html=True)
                    players = get_team_players(tname, scores)
                    if players["bowling"]:
                        df = pd.DataFrame(players["bowling"])
                        df = df[df["matches"] >= min_matches].head(8)
                        if "bowler" in df.columns:
                            df = df.rename(columns={"bowler":"player"})
                        for _, row in df.iterrows():
                            pname = row["player"]
                            st.markdown(f'''
                            <div class="lb-row">
                                <div></div>
                                <div><div class="lb-name">
                                    {avatar_html(pname,28)}{pname}</div>
                                </div>
                                <div class="lb-stat">{row.get("economy",0):.2f}</div>
                                <div class="lb-stat">{row.get("dot_ball_pct",0):.1f}%</div>
                                <div class="lb-stat">{int(row.get("wickets",0))}</div>
                                <div class="lb-score" style="color:{tinfo["color"]}">
                                    {row.get("bowling_score",0):.1f}</div>
                            </div>''', unsafe_allow_html=True)
                    else:
                        st.info("No bowling data available")

        # Best XI vs opponent
        with it5:
            c1, c2 = st.columns(2)
            for col_w, tname, opp_name, tinfo in [
                (c1, team1, team2, ti1),
                (c2, team2, team1, ti2)
            ]:
                with col_w:
                    st.markdown(f'<div class="section-title" style="font-size:1rem">'
                                f'{tinfo["emoji"]} {tname} — Best XI vs {opp_name}</div>',
                                unsafe_allow_html=True)
                    xi = get_best_xi_vs_opponent(tname, opp_name, scores, min_matches)
                    if xi:
                        for item in xi:
                            color = get_team_color(item["player"])
                            st.markdown(f'''
                            <div class="xi-card" style="border-left:3px solid {color}">
                                <div class="xi-role">{item["role"]}</div>
                                <div style="flex:1">
                                    <div class="xi-name">
                                        {avatar_html(item["player"],30)}
                                        {item["player"]}</div>
                                    <div style="font-size:0.7rem;color:#7d8590">
                                        {item["reason"]}</div>
                                </div>
                                <div class="xi-score" style="color:{color}">
                                    {item["score"]:.1f}</div>
                            </div>''', unsafe_allow_html=True)
                    else:
                        st.info(f"Not enough data for {tname}")

        # Player matchups
        with it6:
            st.markdown(f'<div class="section-title">⚔️ Key Matchups — {team1} Batters vs {team2} Bowlers</div>',
                        unsafe_allow_html=True)
            matchups = get_player_matchups(team1, team2, scores)

            if matchups:
                adv_colors = {"batter":"#00d4aa","bowler":"#e63946","neutral":"#f0b429"}
                adv_icons  = {"batter":"🏏","bowler":"🎯","neutral":"⚖️"}

                for m in matchups:
                    adv   = m["advantage"]
                    color = adv_colors[adv]
                    icon  = adv_icons[adv]
                    b1c   = get_team_color(m["batter"])
                    b2c   = get_team_color(m["bowler"])
                    st.markdown(f'''
                    <div style="background:#111820;border:1px solid #1e2d3d;
                         border-left:3px solid {color};border-radius:10px;
                         padding:0.8rem 1rem;margin-bottom:0.5rem;
                         display:flex;align-items:center;gap:1rem">
                        <div style="flex:1">
                            <span style="color:{b1c};font-weight:700">
                                {avatar_html(m["batter"],28)}{m["batter"]}</span>
                            <span style="color:#7d8590;font-size:0.8rem">
                                &nbsp;SR {m["bat_sr"]:.0f}</span>
                        </div>
                        <div style="text-align:center;font-size:1.2rem">{icon}</div>
                        <div style="flex:1;text-align:right">
                            <span style="color:#7d8590;font-size:0.8rem">
                                Econ {m["bowl_econ"]:.2f}&nbsp;</span>
                            <span style="color:{b2c};font-weight:700">
                                {m["bowler"]}{avatar_html(m["bowler"],28)}</span>
                        </div>
                        <div style="width:90px;text-align:center">
                            <div style="color:{color};font-size:0.75rem;font-weight:700">
                                {adv.upper()} EDGE</div>
                            <div style="color:#7d8590;font-size:0.7rem">{m["edge"]}</div>
                        </div>
                    </div>''', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f'<div class="section-title">⚔️ {team2} Batters vs {team1} Bowlers</div>',
                            unsafe_allow_html=True)
                reverse = get_player_matchups(team2, team1, scores)
                for m in reverse:
                    adv   = m["advantage"]
                    color = adv_colors[adv]
                    icon  = adv_icons[adv]
                    b1c   = get_team_color(m["batter"])
                    b2c   = get_team_color(m["bowler"])
                    st.markdown(f'''
                    <div style="background:#111820;border:1px solid #1e2d3d;
                         border-left:3px solid {color};border-radius:10px;
                         padding:0.8rem 1rem;margin-bottom:0.5rem;
                         display:flex;align-items:center;gap:1rem">
                        <div style="flex:1">
                            <span style="color:{b1c};font-weight:700">
                                {avatar_html(m["batter"],28)}{m["batter"]}</span>
                            <span style="color:#7d8590;font-size:0.8rem">
                                &nbsp;SR {m["bat_sr"]:.0f}</span>
                        </div>
                        <div style="text-align:center;font-size:1.2rem">{icon}</div>
                        <div style="flex:1;text-align:right">
                            <span style="color:#7d8590;font-size:0.8rem">
                                Econ {m["bowl_econ"]:.2f}&nbsp;</span>
                            <span style="color:{b2c};font-weight:700">
                                {m["bowler"]}{avatar_html(m["bowler"],28)}</span>
                        </div>
                        <div style="width:90px;text-align:center">
                            <div style="color:{color};font-size:0.75rem;font-weight:700">
                                {adv.upper()} EDGE</div>
                            <div style="color:#7d8590;font-size:0.7rem">{m["edge"]}</div>
                        </div>
                    </div>''', unsafe_allow_html=True)
            else:
                st.info("Not enough data for matchup analysis")
