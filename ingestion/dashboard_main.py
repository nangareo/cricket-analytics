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
    page_title="Cricket Analytics | IPL 2026",
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
    <div class="hero-sub">IPL Intelligence Platform &nbsp;·&nbsp; 2008 – 2026</div>
    <div style="margin-top:0.8rem;"><span class="hero-badge">🏆 IPL 2026 — RCB Back-to-Back Champions</span></div>
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
    st.session_state.filter_label     = "All Time  •  2008–2026"
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
        sel, lbl = ["2024","2025","2026"], "Last 3 Seasons"
    elif filter_type == "Last 5 Seasons":
        sel, lbl = ["2022","2023","2024","2025","2026"], "Last 5 Seasons"
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
tab1,tab2,tab3,tab4,tab5,tab6,tab7,tab8,tab9 = st.tabs([
    "🏏 BATTING", "🎯 BOWLING", "⚡ ALL-ROUNDERS",
    "⚔️ HEAD TO HEAD", "📈 SEASON TRENDS",
    "👑 BEST XI", "🔎 PLAYER SEARCH", "🏟️ TEAM INTEL",
    "🔴 LIVE SCORES"
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
        st.markdown('<div class="section-title"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" style="vertical-align:middle;margin-right:8px"><rect x="10" y="2" width="5" height="14" rx="1" fill="white"/><rect x="9" y="14" width="7" height="8" rx="2" fill="#c8a96e"/><line x1="12" y1="2" x2="12" y2="22" stroke="rgba(0,0,0,0.15)" stroke-width="0.5"/></svg>Batting Rankings</div>', unsafe_allow_html=True)        
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
    🏆 IPL 2026 — RCB Back-to-Back Champions
</div>
""", unsafe_allow_html=True)
# ── TAB 9 — LIVE SCORES (Cricbuzz Style) ──────────────
with tab9:
    import urllib.request as _ur, json as _json

    API_KEY = "c83bbc46-e3c7-4a77-8b28-a9e4d7785183"

    # ── CSS ──
    st.markdown("""
<style>
@keyframes livepulse{0%,100%{opacity:1;}50%{opacity:0.3;}}
.live-hdr{display:flex;align-items:center;gap:10px;padding-bottom:14px;border-bottom:1px solid rgba(255,255,255,0.06);margin-bottom:14px;}
.live-dot{width:11px;height:11px;background:#ff4444;border-radius:50%;animation:livepulse 1.2s infinite;flex-shrink:0;}
.live-title{font-family:'Rajdhani',sans-serif;font-size:1.3rem;font-weight:700;letter-spacing:2px;color:#f0f6ff;}
.live-src{font-size:0.68rem;color:#8b949e;margin-left:auto;}
.ipl-badge-s{display:inline-block;background:#1a73e8;color:#fff;font-size:0.62rem;font-weight:700;padding:2px 7px;border-radius:8px;letter-spacing:1px;}
.result-badge-s{display:inline-block;background:rgba(29,185,84,0.15);color:#1db954;font-size:0.62rem;font-weight:700;padding:2px 7px;border-radius:8px;}
.live-badge-s{display:inline-block;background:rgba(255,68,68,0.15);color:#ff4444;font-size:0.62rem;font-weight:700;padding:2px 7px;border-radius:8px;}
.m-card{background:rgba(22,27,34,0.95);border:0.5px solid rgba(255,255,255,0.07);border-radius:14px;margin-bottom:10px;overflow:hidden;}
.m-card-ipl{background:rgba(22,27,34,0.95);border:0.5px solid rgba(255,255,255,0.07);border-left:3px solid #1a73e8;border-radius:14px;margin-bottom:10px;overflow:hidden;}
.m-card-live{background:rgba(22,27,34,0.95);border:0.5px solid rgba(255,255,255,0.07);border-left:3px solid #ff4444;border-radius:14px;margin-bottom:10px;overflow:hidden;}
.m-top{display:flex;justify-content:space-between;align-items:center;padding:9px 14px;border-bottom:0.5px solid rgba(255,255,255,0.06);}
.m-top-name{font-size:0.7rem;color:#8b949e;}
.m-body{padding:12px 14px;}
.t-row{display:flex;align-items:center;gap:10px;margin-bottom:8px;}
.t-icon{width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:0.62rem;font-weight:700;flex-shrink:0;}
.t-name{font-size:0.88rem;font-weight:500;color:#f0f6ff;flex:1;}
.t-score{font-size:1rem;font-weight:600;color:#f0f6ff;text-align:right;}
.t-score-dim{font-size:1rem;font-weight:600;color:#8b949e;text-align:right;}
.t-overs{font-size:0.68rem;color:#8b949e;text-align:right;}
.m-divider{height:0.5px;background:rgba(255,255,255,0.06);margin:8px 0;}
.m-status-won{font-size:0.75rem;color:#1db954;font-weight:600;}
.m-status-live{font-size:0.75rem;color:#ff4444;font-weight:600;}
.m-status-norm{font-size:0.75rem;color:#8b949e;}
.section-sep{font-size:0.68rem;font-weight:600;color:#8b949e;letter-spacing:2px;text-transform:uppercase;margin:14px 0 8px;padding-left:2px;}
.no-ipl-msg{text-align:center;padding:2.5rem 1rem;background:rgba(22,27,34,0.8);border-radius:14px;border:0.5px solid rgba(255,255,255,0.06);}
.innings-hdr{font-size:0.7rem;font-weight:600;color:#8b949e;letter-spacing:1.5px;text-transform:uppercase;padding:6px 8px;background:rgba(255,255,255,0.03);border-radius:6px;margin-bottom:6px;margin-top:8px;}
.sc-tbl{width:100%;border-collapse:collapse;font-size:0.72rem;margin-bottom:10px;}
.sc-tbl th{color:#8b949e;font-weight:500;padding:5px 6px;text-align:right;border-bottom:0.5px solid rgba(255,255,255,0.06);}
.sc-tbl th:first-child,.sc-tbl th:nth-child(2){text-align:left;}
.sc-tbl td{padding:6px 6px;text-align:right;color:#c9d1d9;border-bottom:0.5px solid rgba(255,255,255,0.04);}
.sc-tbl td:first-child{text-align:left;color:#f0f6ff;font-weight:500;}
.sc-tbl td:nth-child(2){text-align:left;color:#8b949e;font-size:0.65rem;}
.sc-tbl tr:last-child td{border-bottom:none;}
.sc-hl{color:#1db954 !important;font-weight:600 !important;}
.sc-total-row{display:flex;justify-content:space-between;padding:6px 8px;background:rgba(29,185,84,0.06);border-radius:6px;margin-bottom:6px;}
.sc-total-row span{font-size:0.75rem;font-weight:600;color:#f0f6ff;}
</style>
<div class="live-hdr">
    <div class="live-dot"></div>
    <span class="live-title">LIVE CRICKET SCORES</span>
    <span class="live-src">CricketData.org · 60s cache</span>
</div>
""", unsafe_allow_html=True)

    if st.button("Refresh Now", key="live_refresh_v3"):
        st.cache_data.clear()
        st.rerun()

    @st.cache_data(ttl=60)
    def _fetch_matches():
        import time as _time
        for attempt in range(3):
            try:
                req = _ur.Request(
                    "https://api.cricapi.com/v1/currentMatches?apikey=" + API_KEY + "&offset=0",
                    headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
                )
                with _ur.urlopen(req, timeout=20) as r:
                    d = _json.loads(r.read())
                    if d.get("status") == "success":
                        return d.get("data", []), None
                    return [], d.get("reason", "error")
            except Exception as e:
                if attempt == 2:
                    return [], str(e)
                _time.sleep(2)
        return [], "Failed after 3 attempts"

    @st.cache_data(ttl=60)
    def _fetch_scorecard(match_id):
        try:
            req = _ur.Request(
                "https://api.cricapi.com/v1/match_info?apikey=" + API_KEY + "&id=" + match_id,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with _ur.urlopen(req, timeout=20) as r:
                d = _json.loads(r.read())
                if d.get("status") == "success":
                    return d.get("data", {})
                return {}
        except:
            return {}

    def _team_color(name):
        c = {
            "Mumbai Indians":("#dbeafe","#1d4ed8"),
            "Chennai Super Kings":("#fef9c3","#854d0e"),
            "Royal Challengers":("#fee2e2","#991b1b"),
            "Kolkata Knight Riders":("#ede9fe","#5b21b6"),
            "Delhi Capitals":("#dbeafe","#1e3a5f"),
            "Sunrisers Hyderabad":("#ffedd5","#9a3412"),
            "Rajasthan Royals":("#fce7f3","#9d174d"),
            "Punjab Kings":("#fee2e2","#7f1d1d"),
            "Lucknow Super Giants":("#e0f2fe","#075985"),
            "Gujarat Titans":("#f0fdf4","#14532d"),
        }
        for k,(bg,fg) in c.items():
            if k.lower() in name.lower():
                return bg, fg
        return "rgba(255,255,255,0.06)","#8b949e"

    def _abbr(name):
        a = {
            "Mumbai Indians":"MI","Chennai Super Kings":"CSK",
            "Royal Challengers Bengaluru":"RCB","Royal Challengers Bangalore":"RCB",
            "Kolkata Knight Riders":"KKR","Delhi Capitals":"DC",
            "Sunrisers Hyderabad":"SRH","Rajasthan Royals":"RR",
            "Punjab Kings":"PBKS","Lucknow Super Giants":"LSG","Gujarat Titans":"GT"
        }
        for k,v in a.items():
            if k.lower() in name.lower():
                return v
        return name[:3].upper()

    def _render_scorecard(match_id):
        sc = _fetch_scorecard(match_id)
        if not sc:
            st.markdown(
                '<div style="text-align:center;padding:1.5rem;background:rgba(255,255,255,0.02);'
                'border-radius:10px;border:0.5px solid rgba(255,255,255,0.06);">'
                '<div style="font-size:1.5rem;margin-bottom:8px;">🏏</div>'
                '<div style="font-size:0.82rem;color:#8b949e;">Scorecard unavailable</div>'
                '</div>',
                unsafe_allow_html=True
            )
            return
        _render_full_scorecard(sc)

    def _render_full_scorecard(sc):

        score_arr  = sc.get("score", [])
        teams      = sc.get("teams", [])
        team_info  = sc.get("teamInfo", [])
        toss_w     = sc.get("tossWinner","")
        toss_c     = sc.get("tossChoice","")
        winner     = sc.get("matchWinner","")
        status     = sc.get("status","")
        venue      = sc.get("venue","")
        date_str   = sc.get("date","")
        started    = sc.get("matchStarted", False)
        ended      = sc.get("matchEnded", False)
        mtype      = sc.get("matchType","t20").lower()
        total_overs = 20 if mtype == "t20" else (50 if mtype == "odi" else 90)

        # Team logo map
        logo_map = {}
        for ti in team_info:
            logo_map[ti.get("name","")] = ti.get("img","")

        # ── Match summary header ──
        toss_html = ""
        if toss_w:
            toss_html = (
                '<div style="display:flex;align-items:center;gap:6px;margin-bottom:10px;'
                'padding:6px 10px;background:rgba(255,255,255,0.03);border-radius:8px;">'
                '<span style="font-size:0.68rem;color:#8b949e;">🪙 Toss:</span>'
                '<span style="font-size:0.72rem;color:#c9d1d9;">'
                + toss_w.title() + " won & chose to " + toss_c +
                '</span></div>'
            )

        st.markdown(
            '<div style="padding:10px 0 6px;">'
            '<div style="font-size:0.68rem;color:#8b949e;margin-bottom:6px;">📍 ' + venue + ' &nbsp;·&nbsp; 📅 ' + date_str + '</div>'
            + toss_html +
            '</div>',
            unsafe_allow_html=True
        )

        # ── Innings cards ──
        if not score_arr:
            st.markdown(
                '<div style="text-align:center;padding:2rem;background:rgba(255,255,255,0.02);'
                'border-radius:12px;border:0.5px dashed rgba(255,255,255,0.1);">'
                '<div style="font-size:2rem;margin-bottom:10px;">📊</div>'
                '<div style="font-size:0.85rem;font-weight:600;color:#f0f6ff;margin-bottom:4px;">Scorecard Coming Soon</div>'
                '<div style="font-size:0.75rem;color:#8b949e;">Ball-by-ball data will appear here once the match progresses</div>'
                '</div>',
                unsafe_allow_html=True
            )
            return

        # ── Innings cards ──
        for idx, s in enumerate(score_arr):
            inning  = s.get("inning","")
            runs    = s.get("r",0)
            wkts    = s.get("w",0)
            overs   = float(s.get("o",0))
            rr      = round(runs / overs, 2) if overs else 0
            t_name  = inning.replace(" Inning 1","").replace(" Inning 2","").strip()
            logo    = logo_map.get(t_name,"")
            is_win  = t_name == winner
            inn_num = "2nd Innings" if "Inning 2" in inning else "1st Innings"
            is_live_inn = (idx == len(score_arr)-1) and started and not ended

            # Overs progress bar
            overs_int   = int(overs)
            balls_extra = round((overs - overs_int) * 10)
            total_balls = overs_int * 6 + balls_extra
            max_balls   = total_overs * 6
            pct         = min(100, round(total_balls / max_balls * 100))

            # Projected score for live innings
            proj = ""
            if is_live_inn and overs > 0:
                projected = round(rr * total_overs)
                proj = "Proj: ~" + str(projected)

            # Required RR for 2nd innings live
            rrr_html = ""
            if is_live_inn and idx == 1 and len(score_arr) >= 2:
                first_inn_runs = score_arr[0].get("r",0)
                target = first_inn_runs + 1
                balls_left = max_balls - total_balls
                overs_left = round(balls_left / 6, 1)
                needed = target - runs
                if overs_left > 0 and needed > 0:
                    rrr = round(needed / overs_left, 2)
                    rrr_html = (
                        '<div style="background:rgba(255,215,0,0.08);border:0.5px solid rgba(255,215,0,0.2);'
                        'border-radius:8px;padding:6px 10px;margin-top:8px;display:flex;justify-content:space-between;">'
                        '<span style="font-size:0.72rem;color:#8b949e;">Need ' + str(needed) + ' off ' + str(balls_left) + ' balls</span>'
                        '<span style="font-size:0.72rem;font-weight:600;color:#ffd700;">RRR: ' + str(rrr) + '</span>'
                        '</div>'
                    )

            # Win probability (simple)
            win_prob = ""
            if is_live_inn and idx == 1 and len(score_arr) >= 2:
                first_runs = score_arr[0].get("r",0)
                if first_runs > 0:
                    chase_prob = min(95, max(5, round((runs / first_runs) * 100 + (pct / 10))))
                    bat_prob   = 100 - chase_prob
                    bar_w      = chase_prob
                    win_prob = (
                        '<div style="margin-top:8px;">'
                        '<div style="display:flex;justify-content:space-between;font-size:0.65rem;color:#8b949e;margin-bottom:4px;">'
                        '<span>' + t_name[:15] + ' ' + str(chase_prob) + '%</span>'
                        '<span>' + str(bat_prob) + '% ' + score_arr[0].get("inning","").replace(" Inning 1","")[:15] + '</span>'
                        '</div>'
                        '<div style="height:5px;background:rgba(255,255,255,0.08);border-radius:3px;overflow:hidden;">'
                        '<div style="height:100%;width:' + str(bar_w) + '%;background:linear-gradient(90deg,#1db954,#ffd700);border-radius:3px;"></div>'
                        '</div>'
                        '</div>'
                    )

            logo_html = ""
            if logo:
                logo_html = '<img src="' + logo + '" width="30" height="30" style="border-radius:50%;object-fit:contain;background:#fff;padding:2px;">'

            win_tag = ""
            if is_win and ended:
                win_tag = ' <span style="background:rgba(29,185,84,0.2);color:#1db954;font-size:0.6rem;font-weight:700;padding:2px 7px;border-radius:8px;">WON</span>'

            border = "rgba(29,185,84,0.4)" if is_win and ended else ("rgba(255,68,68,0.3)" if is_live_inn else "rgba(255,255,255,0.07)")
            bg     = "rgba(29,185,84,0.04)" if is_win and ended else ("rgba(255,68,68,0.03)" if is_live_inn else "rgba(255,255,255,0.02)")
            live_dot = '<span style="display:inline-block;width:7px;height:7px;background:#ff4444;border-radius:50%;margin-right:5px;"></span>' if is_live_inn else ""

            st.markdown(
                '<div style="background:' + bg + ';border:0.5px solid ' + border + ';border-radius:12px;padding:12px 14px;margin-bottom:10px;">'
                # Header row
                '<div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">'
                + logo_html +
                '<div style="flex:1;">'
                '<div style="font-size:0.68rem;color:#8b949e;margin-bottom:1px;">' + live_dot + inn_num + '</div>'
                '<div style="font-size:0.88rem;font-weight:600;color:#f0f6ff;">' + t_name + win_tag + '</div>'
                '</div>'
                '<div style="text-align:right;">'
                '<div style="font-family:Rajdhani,sans-serif;font-size:1.7rem;font-weight:700;color:#f0f6ff;line-height:1;">'
                + str(runs) + '<span style="font-size:0.95rem;color:#8b949e;font-weight:400;">/' + str(wkts) + '</span></div>'
                '<div style="font-size:0.65rem;color:#8b949e;">' + str(overs) + ' ov</div>'
                '</div></div>'
                # Overs progress bar
                '<div style="margin-bottom:8px;">'
                '<div style="display:flex;justify-content:space-between;font-size:0.62rem;color:#8b949e;margin-bottom:3px;">'
                '<span>Overs: ' + str(overs) + ' / ' + str(total_overs) + '</span>'
                '<span>' + proj + '</span>'
                '</div>'
                '<div style="height:4px;background:rgba(255,255,255,0.08);border-radius:2px;overflow:hidden;">'
                '<div style="height:100%;width:' + str(pct) + '%;background:linear-gradient(90deg,#1db954,#4fc3f7);border-radius:2px;"></div>'
                '</div></div>'
                # Stats strip
                '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:5px;">'
                '<div style="background:rgba(255,255,255,0.03);border-radius:6px;padding:5px;text-align:center;">'
                '<div style="font-size:0.6rem;color:#8b949e;">Runs</div>'
                '<div style="font-size:0.85rem;font-weight:600;color:#f0f6ff;">' + str(runs) + '</div>'
                '</div>'
                '<div style="background:rgba(255,255,255,0.03);border-radius:6px;padding:5px;text-align:center;">'
                '<div style="font-size:0.6rem;color:#8b949e;">Wkts</div>'
                '<div style="font-size:0.85rem;font-weight:600;color:#f0f6ff;">' + str(wkts) + '</div>'
                '</div>'
                '<div style="background:rgba(255,255,255,0.03);border-radius:6px;padding:5px;text-align:center;">'
                '<div style="font-size:0.6rem;color:#8b949e;">CRR</div>'
                '<div style="font-size:0.85rem;font-weight:600;color:#1db954;">' + str(rr) + '</div>'
                '</div>'
                '<div style="background:rgba(255,255,255,0.03);border-radius:6px;padding:5px;text-align:center;">'
                '<div style="font-size:0.6rem;color:#8b949e;">Balls</div>'
                '<div style="font-size:0.85rem;font-weight:600;color:#f0f6ff;">' + str(total_balls) + '</div>'
                '</div>'
                '</div>'
                + rrr_html + win_prob +
                '</div>',
                unsafe_allow_html=True
            )

        # ── Result banner ──
        if ended and status:
            st.markdown(
                '<div style="background:rgba(29,185,84,0.08);border:0.5px solid rgba(29,185,84,0.3);'
                'border-radius:10px;padding:10px 14px;text-align:center;margin-top:4px;">'
                '<span style="font-size:0.85rem;font-weight:600;color:#1db954;">🏆 ' + status + '</span>'
                '</div>',
                unsafe_allow_html=True
            )
        elif started and not ended:
            st.markdown(
                '<div style="background:rgba(255,68,68,0.06);border:0.5px solid rgba(255,68,68,0.2);'
                'border-radius:10px;padding:8px 14px;text-align:center;margin-top:4px;">'
                '<span style="font-size:0.78rem;color:#ff4444;">🔴 Match in Progress · Ball-by-ball data requires premium API plan</span>'
                '</div>',
                unsafe_allow_html=True
            )

    def _render_match(m, is_ipl=False):
        mid     = m.get("id","")
        name    = m.get("name","")
        status  = m.get("status","")
        mtype   = m.get("matchType","").upper()
        venue   = m.get("venue","")
        date    = m.get("date","")
        started = m.get("matchStarted",False)
        ended   = m.get("matchEnded",False)
        teams   = m.get("teams",[])
        scores  = m.get("score",[])

        card_cls = "m-card-ipl" if is_ipl else ("m-card-live" if (started and not ended) else "m-card")
        status_cls = "m-status-won" if ended else ("m-status-live" if (started and not ended) else "m-status-norm")
        badges = ""
        if is_ipl:
            badges += '<span class="ipl-badge-s">IPL 2026</span> '
        if started and not ended:
            badges += '<span class="live-badge-s">LIVE</span>'
        elif ended:
            badges += '<span class="result-badge-s">RESULT</span>'

        score_map = {}
        for s in scores:
            inn = s.get("inning","")
            for t in teams:
                if t.lower().split()[0] in inn.lower():
                    score_map[t] = (str(s.get("r","-")), str(s.get("w","-")), str(s.get("o","-")))

        team_rows = ""
        for i, t in enumerate(teams[:2]):
            bg, fg = _team_color(t)
            abbr   = _abbr(t)
            sc     = score_map.get(t)
            if sc:
                sc_cls = "t-score" if i == 0 or ended else "t-score-dim"
                sc_html = '<div class="' + sc_cls + '">' + sc[0] + "/" + sc[1] + '</div><div class="t-overs">(' + sc[2] + ' ov)</div>'
            else:
                sc_html = '<div class="t-score-dim" style="font-size:0.75rem;">Yet to bat</div>'
            team_rows += (
                '<div class="t-row">'
                '<div class="t-icon" style="background:' + bg + ';color:' + fg + ';">' + abbr + '</div>'
                '<span class="t-name">' + t + '</span>'
                '<div>' + sc_html + '</div>'
                '</div>'
            )

        match_title = name.split(",")[0] if "," in name else name
        venue_safe  = venue.replace("&","&amp;")

        html = (
            '<div class="' + card_cls + '">'
            '<div class="m-top">'
            '<span class="m-top-name">📍 ' + venue_safe + ' &nbsp;·&nbsp; 📅 ' + date + '</span>'
            '<div style="display:flex;gap:6px;align-items:center;">'
            '<span style="font-size:0.65rem;color:#8b949e;">' + mtype + '</span>'
            + badges +
            '</div></div>'
            '<div class="m-body">'
            '<div style="font-size:0.78rem;font-weight:600;color:#f0f6ff;margin-bottom:8px;">' + match_title + '</div>'
            + team_rows +
            '<div class="m-divider"></div>'
            '<span class="' + status_cls + '">' + status + '</span>'
            '</div></div>'
        )
        st.markdown(html, unsafe_allow_html=True)

        with st.expander("📋 Full Scorecard", expanded=False):
            if mid:
                _render_scorecard(mid)
            else:
                st.caption("Match ID not available")

    # ── Main render ──
    matches, err = _fetch_matches()

    if err:
        st.error("Could not fetch scores: " + str(err))
    elif not matches:
        st.info("No matches right now. Check back during match hours!")
    else:
        ipl      = [m for m in matches if "Indian Premier League" in m.get("name","")]
        others   = [m for m in matches if "Indian Premier League" not in m.get("name","")]
        live_now = [m for m in matches if m.get("matchStarted") and not m.get("matchEnded")]
        upcoming = [m for m in matches if not m.get("matchStarted")]

        st.markdown(
            '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:14px;">'
            '<div class="stat-card"><div class="stat-value" style="color:#1a73e8;">' + str(len(ipl)) + '</div><div class="stat-label">IPL 2026</div></div>'
            '<div class="stat-card"><div class="stat-value" style="color:#ff4444;">' + str(len(live_now)) + '</div><div class="stat-label">Live Now</div></div>'
            '<div class="stat-card"><div class="stat-value" style="color:#ffd700;">' + str(len(upcoming)) + '</div><div class="stat-label">Upcoming</div></div>'
            '<div class="stat-card"><div class="stat-value">' + str(len(matches)) + '</div><div class="stat-label">Total</div></div>'
            '</div>',
            unsafe_allow_html=True
        )

        filt = st.radio("Show:", ["IPL 2026", "All Matches", "Live Only"],
                        horizontal=True, key="live_filter_v3")

        if filt == "IPL 2026":
            if not ipl:
                st.markdown(
                    '<div class="no-ipl-msg">'
                    '<div style="font-size:2.5rem;">🏏</div>'
                    '<div style="font-family:Rajdhani,sans-serif;font-size:1.3rem;color:#f0f6ff;margin:0.8rem 0;font-weight:700;">No IPL Matches Right Now</div>'
                    '<div style="color:#8b949e;font-size:0.82rem;">IPL 2026 playoffs · Matches at 3:30 PM &amp; 7:30 PM IST</div>'
                    '</div>',
                    unsafe_allow_html=True
                )
            else:
                for m in ipl:
                    _render_match(m, is_ipl=True)
        elif filt == "Live Only":
            if not live_now:
                st.info("No live matches at the moment.")
            else:
                for m in live_now:
                    _render_match(m, is_ipl="Indian Premier League" in m.get("name",""))
        else:
            if ipl:
                st.markdown('<div class="section-sep">🏆 IPL 2026</div>', unsafe_allow_html=True)
                for m in ipl:
                    _render_match(m, is_ipl=True)
            if others:
                st.markdown('<div class="section-sep">🌍 Other Matches</div>', unsafe_allow_html=True)
                for m in others:
                    _render_match(m, is_ipl=False)