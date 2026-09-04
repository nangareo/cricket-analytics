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
from ingestion.data_loader import load_all_matches
from dashboard.ipl_teams import (get_team_color, get_team_info, get_player_team,
                                 PLAYER_TEAMS, IPL_TEAMS, avatar_html, RETIRED_PLAYERS)
from dashboard import theme
from analytics.team_analytics import (get_team_players, calculate_team_stats,
    generate_swot, get_player_matchups, get_best_xi_vs_opponent)

st.set_page_config(
    page_title="Cricket Analytics | IPL 2026",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── THEME ────────────────────────────────────────────
# All colour, type and spacing live in dashboard/theme.py so the dark and
# light palettes stay in one place and the charts can read the same values.
if "theme" not in st.session_state:
    st.session_state.theme = theme.DEFAULT_THEME

THEME = st.session_state.theme
T     = theme.tokens(THEME)

st.markdown(theme.css(THEME), unsafe_allow_html=True)

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
def load_season_data():
    """
    Per-delivery season totals, for the Season Trends tab.

    pd.read_csv cannot read these files — csv2 interleaves version/info/ball
    rows of different widths in a single file. Reading them directly produced
    a frame with no 'season' and no 'runs_off_bat', so Season Trends only ever
    rendered its "raw data needed" warning.

    Only the columns that tab actually groups on are kept; the full frame is
    176 MB and would sit in the cache for the life of the process. 'innings'
    is among them because a team score is per innings, not per match.
    """
    try:
        df = load_all_matches(config.DATA_FOLDER)
        return df[["season", "runs_off_bat", "runs_extras", "match_id",
                   "innings", "is_legal_ball"]]
    except Exception:
        return None

scores = load_scores()

def team_dot(info):
    """The small team-coloured ball used beside a name."""
    colour = info.get("color", "var(--muted)") if hasattr(info, "get") else info
    return f'<span class="team-dot" style="background:{colour}"></span>'


def _readable_on(hex_color):
    """Black or white text, whichever has more contrast on this background."""
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    chan = [(v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4)
            for v in (r, g, b)]
    lum = 0.2126 * chan[0] + 0.7152 * chan[1] + 0.0722 * chan[2]
    return "#11151A" if lum > 0.42 else "#FFFFFF"


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
    df["team"]  = df["player"].apply(lambda x: get_player_team(x) or "Unknown")
    df["color"] = df["player"].apply(get_team_color)
    df = df.sort_values(score_col, ascending=False).head(top).reset_index(drop=True)
    df.index += 1
    return df

def plotly_dark():
    """Plotly layout for the active theme. Name kept; the palette moved to theme.py."""
    return theme.chart_layout(THEME)

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

# ── HEADER ───────────────────────────────────────────
_hl, _hr = st.columns([5, 1])
with _hl:
    st.markdown(f"""
<div class="hero">
  <div>
    <div class="hero-eyebrow">Indian Premier League &middot; 2008&ndash;2026</div>
    <h1 class="hero-title">Cricket Analytics</h1>
    <div class="hero-sub">
      Ball-by-ball analysis of {{matches_played}} matches &middot;
      <span class="hero-badge">IPL 2026 &mdash; RCB back-to-back champions</span>
    </div>
  </div>
  <div class="hero-stats-strip">
    <div class="hero-stat-item"><div class="hero-stat-num">19</div>
         <div class="hero-stat-lbl">Seasons</div></div>
    <div class="hero-stat-item"><div class="hero-stat-num">818</div>
         <div class="hero-stat-lbl">Players</div></div>
    <div class="hero-stat-item"><div class="hero-stat-num">10</div>
         <div class="hero-stat-lbl">Teams</div></div>
  </div>
</div>
""".replace("{matches_played}", "1,243"), unsafe_allow_html=True)
with _hr:
    st.radio(
        "Theme", options=["dark", "light"], key="theme",
        horizontal=True, label_visibility="collapsed",
        format_func=lambda v: "Dark" if v == "dark" else "Light",
    )

# ── FILTER BAR ───────────────────────────────────────
# (styling now lives in dashboard/theme.py)

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
        f'<div style="padding-top:16px;border-left:2px solid var(--border);padding-left:12px">'        f'<div style="font-size:0.6rem;letter-spacing:2px;text-transform:uppercase;color:var(--faint)">ACTIVE FILTER</div>'        f'<div style="font-family:Rajdhani,sans-serif;font-size:0.95rem;font-weight:600;color:var(--accent)">'        f'{st.session_state.filter_label}</div></div>',
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

st.markdown("<hr style='border:none;border-top:1px solid var(--border);margin:0.5rem 0'>",
            unsafe_allow_html=True)

# ── TABS ─────────────────────────────────────────────
tab1,tab2,tab3,tab4,tab5,tab6,tab7,tab8,tab9 = st.tabs([
    "BATTING", "BOWLING", "ALL-ROUNDERS",
    "HEAD TO HEAD", "SEASON TRENDS",
    "BEST XI", "PLAYER SEARCH", "TEAM INTEL",
    "LIVE SCORES"
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
                <div class="stat-label">Top Batsman</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{df["average"].max():.1f}</div>
                <div class="stat-name">{df.loc[df["average"].idxmax(),"player"]}</div>
                <div class="stat-label">Best Average</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{df["strike_rate"].max():.0f}</div>
                <div class="stat-name">{df.loc[df["strike_rate"].idxmax(),"player"]}</div>
                <div class="stat-label">Best Strike Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{int(df["total_runs"].max())}</div>
                <div class="stat-name">{df.loc[df["total_runs"].idxmax(),"player"]}</div>
                <div class="stat-label">Most Runs</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Leaderboard
        st.markdown('<div class="section-title"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" style="vertical-align:middle;margin-right:8px"><rect x="10" y="2" width="5" height="14" rx="1" fill="currentColor"/><rect x="9" y="14" width="7" height="8" rx="2" fill="currentColor"/><line x1="12" y1="2" x2="12" y2="22" stroke="rgba(0,0,0,0.15)" stroke-width="0.5"/></svg>Batting Rankings</div>', unsafe_allow_html=True)        
        st.markdown("""
        <div class="lb-row" style="background:transparent;border-color:transparent;
             color:var(--faint);font-size:0.7rem;letter-spacing:1px;text-transform:uppercase;">
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
                    <div class="lb-team">
                        <span class="team-dot" style="background:{color}"></span>{row["team"]}</div>
                </div>
                <div class="lb-stat">{int(row["total_runs"])}</div>
                <div class="lb-stat">{row["average"]:.1f}</div>
                <div class="lb-stat">{row["strike_rate"]:.1f}</div>
                <div class="lb-score">{row["batting_score"]:.1f}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown('<div class="section-title">Analytics</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(df, x="player", y="batting_score",
                         color="batting_score",
                         color_continuous_scale=theme.ramp("willow", THEME),
                         title="Batting Score Comparison",
                         text=df["batting_score"].round(1))
            fig.update_traces(textposition="outside", textfont_color=T["text_muted"])
            fig.update_layout(**plotly_dark(), showlegend=False,
                              coloraxis_showscale=False,
                              xaxis_tickangle=-35)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig2 = px.scatter(df, x="average", y="strike_rate",
                              size="total_runs", color="batting_score",
                              hover_name="player",
                              color_continuous_scale=theme.ramp("willow", THEME),
                              title="Average vs Strike Rate",
                              labels={"average":"Batting Average",
                                      "strike_rate":"Strike Rate"})
            fig2.update_layout(**plotly_dark(), coloraxis_showscale=False)
            st.plotly_chart(fig2, use_container_width=True)

        # Boundary % chart
        fig3 = px.bar(df, x="player", y="boundary_pct",
                      color="boundary_pct",
                      color_continuous_scale=theme.ramp("willow", THEME),
                      title="Boundary % — Hitting Aggression",
                      text=df["boundary_pct"].round(1))
        fig3.update_traces(textposition="outside", textfont_color=T["text_muted"])
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
                <div class="stat-label">Top Bowler</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{df["economy"].min():.2f}</div>
                <div class="stat-name">{df.loc[df["economy"].idxmin(),"player"]}</div>
                <div class="stat-label">Best Economy</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{int(df["wickets"].max())}</div>
                <div class="stat-name">{df.loc[df["wickets"].idxmax(),"player"]}</div>
                <div class="stat-label">Most Wickets</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{df["dot_ball_pct"].max():.1f}%</div>
                <div class="stat-name">{df.loc[df["dot_ball_pct"].idxmax(),"player"]}</div>
                <div class="stat-label">Best Dot Ball %</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-title"><svg width="20" height="20" viewBox="0 0 465 465" style="vertical-align:middle;margin-right:8px;flex-shrink:0" xmlns="http://www.w3.org/2000/svg"><g transform="translate(0 -540.36)"><path fill="currentColor" d="M396.7,608.16c-43.9-43.7-102.2-67.8-164.2-67.8c-62.5,0-120.9,24.1-164.7,67.8C24.1,651.86,0,710.36,0,772.86c0,62,24.1,120.3,67.8,164.2c43.9,44,102.4,68.3,164.7,68.3c61.9,0,120.2-24.3,164.2-68.3s68.3-102.4,68.3-164.2C465,710.56,440.7,652.06,396.7,608.16z M15,772.86c0-119.9,97.6-217.5,217.5-217.5c35.5,0,69,8.5,98.6,23.7L38.7,871.46C23.6,841.86,15,808.36,15,772.86z M106.8,950.26l19-19l-10.6-10.6l-20.4,20.4c-11.4-9.3-21.8-19.8-31.1-31.1l19.7-19.7l-10.6-10.6l-18.3,18.3c-2.9-4.1-5.7-8.4-8.3-12.8l298.5-298.5c4.4,2.6,8.6,5.4,12.8,8.3l-10.8,10.8l10.6,10.6l12.3-12.3c11.3,9.2,21.6,19.4,30.8,30.6l-11.6,12.3l10.9,10.3l9.9-10.5c2.9,4,5.6,8.1,8.2,12.3l-299.1,299.1C114.6,955.66,110.6,953.06,106.8,950.26z M232.5,990.36c-36.1,0-70.2-8.9-100.2-24.5l293.2-293.2c15.7,30,24.5,64.1,24.5,100.2C450,892.76,352.4,990.36,232.5,990.36z"/><rect fill="var(--bg)" x="287.32" y="734.124" transform="matrix(-0.7071 -0.7071 0.7071 -0.7071 -28.2602 1491.7417)" width="15" height="35.2"/><rect fill="var(--bg)" x="95.693" y="842.467" transform="matrix(-0.7071 -0.7071 0.7071 -0.7071 -431.998 1541.1948)" width="15" height="35.2"/><rect fill="var(--bg)" x="132.844" y="804.948" transform="matrix(0.7071 0.7071 -0.7071 0.7071 622.735 141.6802)" width="15" height="35.2"/><rect fill="var(--bg)" x="207.692" y="730.454" transform="matrix(0.7071 0.7071 -0.7071 0.7071 591.9841 66.9372)" width="15" height="35.2"/><rect fill="var(--bg)" x="170.342" y="767.733" transform="matrix(0.7071 0.7071 -0.7071 0.7071 607.4029 104.265)" width="15" height="35.2"/><rect fill="var(--bg)" x="244.844" y="692.963" transform="matrix(0.7071 0.7071 -0.7071 0.7071 576.3555 29.6861)" width="15" height="35.2"/><rect fill="var(--bg)" x="282.335" y="655.712" transform="matrix(0.7071 0.7071 -0.7071 0.7071 560.9943 -7.7354)" width="15" height="35.2"/><rect fill="var(--bg)" x="319.557" y="618.292" transform="matrix(0.7071 0.7071 -0.7071 0.7071 545.4363 -45.0157)" width="15" height="35.2"/><rect fill="var(--bg)" x="137.964" y="883.536" transform="matrix(-0.7071 -0.7071 0.7071 -0.7071 -388.8769 1641.194)" width="15" height="35.2"/><rect fill="var(--bg)" x="175.328" y="846.13" transform="matrix(-0.7071 -0.7071 0.7071 -0.7071 -298.643 1603.7579)" width="15" height="35.2"/><rect fill="var(--bg)" x="249.97" y="771.53" transform="matrix(-0.7071 -0.7071 0.7071 -0.7071 -118.47 1529.1877)" width="15" height="35.2"/><rect fill="var(--bg)" x="212.677" y="808.865" transform="matrix(-0.7071 -0.7071 0.7071 -0.7071 -208.5332 1566.5532)" width="15" height="35.2"/><rect fill="var(--bg)" x="324.683" y="696.859" transform="matrix(-0.7071 -0.7071 0.7071 -0.7071 61.8737 1454.547)" width="15" height="35.2"/><rect fill="var(--bg)" x="361.962" y="659.524" transform="matrix(-0.7071 -0.7071 0.7071 -0.7071 151.9128 1417.1716)" width="15" height="35.2"/><circle fill="var(--bg)" cx="357" cy="904.358" r="7.5"/></g></svg>Bowling Rankings</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="lb-row" style="background:transparent;border-color:transparent;
             color:var(--faint);font-size:0.7rem;letter-spacing:1px;text-transform:uppercase;">
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
                    <div class="lb-team">
                        <span class="team-dot" style="background:{color}"></span>{row["team"]}</div>
                </div>
                <div class="lb-stat">{int(row["wickets"])}</div>
                <div class="lb-stat">{row["economy"]:.2f}</div>
                <div class="lb-stat">{row["dot_ball_pct"]:.1f}%</div>
                <div class="lb-score">{row["bowling_score"]:.1f}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown('<div class="section-title">Analytics</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(df, x="player", y="bowling_score",
                         color="bowling_score",
                         color_continuous_scale=theme.ramp("leather", THEME),
                         title="Bowling Score Comparison",
                         text=df["bowling_score"].round(1))
            fig.update_traces(textposition="outside", textfont_color=T["text_muted"])
            fig.update_layout(**plotly_dark(), showlegend=False,
                              coloraxis_showscale=False, xaxis_tickangle=-35)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig2 = px.scatter(df, x="economy", y="dot_ball_pct",
                              size="wickets", color="bowling_score",
                              hover_name="player",
                              color_continuous_scale=theme.ramp("leather", THEME),
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
                <div class="stat-label">Top All-rounder</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{df["batting_score"].max():.1f}</div>
                <div class="stat-name">{df.loc[df["batting_score"].idxmax(),"player"]}</div>
                <div class="stat-label">Best Batting</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{df["bowling_score"].max():.1f}</div>
                <div class="stat-name">{df.loc[df["bowling_score"].idxmax(),"player"]}</div>
                <div class="stat-label">Best Bowling</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{int(df["matches"].max())}</div>
                <div class="stat-name">{df.loc[df["matches"].idxmax(),"player"]}</div>
                <div class="stat-label">Most Matches</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown('<div class="section-title"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" style="vertical-align:middle;margin-right:8px"><line x1="7" y1="4" x2="7" y2="20" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/><line x1="12" y1="4" x2="12" y2="20" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/><line x1="17" y1="4" x2="17" y2="20" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/><line x1="5" y1="5" x2="9.5" y2="3.5" stroke="var(--gold)" stroke-width="1.5" stroke-linecap="round"/><line x1="9.5" y1="3.5" x2="14.5" y2="3.5" stroke="var(--gold)" stroke-width="1.5" stroke-linecap="round"/><line x1="14.5" y1="3.5" x2="19" y2="5" stroke="var(--gold)" stroke-width="1.5" stroke-linecap="round"/></svg>All-Rounder Rankings</div>',
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
                    <div class="player-team">
                        <span class="team-dot" style="background:{color}"></span>{row["team"]}</div>
                    <div class="player-score">
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
                                 style="width:{w_pct}%;background:var(--accent-mark)">
                            </div>
                        </div>
                    </div>
                    <div class="progress-wrap">
                        <div class="progress-label">
                            <span>Field</span><span>{f_pct:.0f}</span></div>
                        <div class="progress-bar">
                            <div class="progress-fill"
                                 style="width:{f_pct}%;background:var(--accent-mark)">
                            </div>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)

        with col2:
            # Radar chart
            top_n_radar = df.head(theme.MAX_SERIES)
            fig  = go.Figure()
            cats = ["batting_score","bowling_score",
                    "fielding_score","allrounder_score"]
            labs = ["Batting","Bowling","Fielding","Overall"]
            colors_radar = theme.SERIES[THEME]
            for idx, (_, row) in enumerate(top_n_radar.iterrows()):
                fig.add_trace(go.Scatterpolar(
                    r=[row[c] for c in cats], theta=labs,
                    fill="toself", name=row["player"],
                    line_color=colors_radar[idx],
                    fillcolor=hex_to_rgba(colors_radar[idx], 0.15)
                ))
            fig.update_layout(
                **{**plotly_dark(), "margin": dict(l=70, r=70, t=56, b=40)},
                polar=dict(
                    bgcolor="rgba(0,0,0,0)",
                    radialaxis=dict(visible=True, range=[0,100],
                                   gridcolor=T["grid"], color=T["text_muted"]),
                    angularaxis=dict(gridcolor=T["grid"], color=T["text_muted"])
                ),
                title="Top 3 All-rounders — Profile",
            )
            st.plotly_chart(fig, use_container_width=True)

            # Stacked bar
            fig2 = px.bar(df, x="player",
                          y=["batting_score","bowling_score","fielding_score"],
                          title="Score breakdown",
                          barmode="stack",
                          color_discrete_sequence=theme.SERIES[THEME],
                          labels={"player": "", "value": "", "variable": ""})
            # px names series after the dataframe columns; the reader should
            # see "Batting", not "batting_score".
            fig2.for_each_trace(lambda t: t.update(
                name=t.name.replace("_score", "").title(),
                hovertemplate=t.hovertemplate.replace("variable=", "")
                                             .replace("_score", "")))
            fig2.update_layout(**plotly_dark(), xaxis_tickangle=-35,
                               legend_title_text="")
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("⚠️ Run all scorers first!")

# ──────────────────────────────────────────────────────
# TAB 4 — HEAD TO HEAD
# ──────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="section-title"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" style="vertical-align:middle;margin-right:8px"><line x1="4" y1="20" x2="20" y2="4" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/><line x1="4" y1="4" x2="20" y2="20" stroke="var(--accent)" stroke-width="2.5" stroke-linecap="round"/></svg>Head to Head Comparison</div>',
                unsafe_allow_html=True)
    all_players = []
    if scores["batting"] is not None:
        pcol = get_player_col(scores["batting"])
        all_players = sorted(scores["batting"][pcol].tolist())

    if all_players:
        col1, mid, col2 = st.columns([5, 1, 5])
        with col1:
            p1 = st.selectbox("Player 1", all_players, index=0)
        with mid:
            st.markdown('<div class="vs-badge">VS</div>', unsafe_allow_html=True)
        with col2:
            p2 = st.selectbox("Player 2", all_players, index=1)

        def get_stats(name):
            s  = {"player": name, "team": get_player_team(name) or "Unknown"}
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
                 style="border-top:3px solid {s1.get("color","var(--accent)")}">
                <div style="font-size:0.7rem;letter-spacing:2px;color:var(--faint);
                     text-transform:uppercase">Player 1</div>
                <div class="h2h-name" style="color:{s1.get("color","var(--accent)")}">
                    {team_dot(s1)}{p1}</div>
                <div style="font-size:0.75rem;color:var(--faint);margin-bottom:1rem">
                    {s1.get("team","Unknown")}</div>
                <div class="h2h-score">
                    {s1.get("batting_score", s1.get("allrounder_score", "—")):.1f}
                </div>
                <div style="font-size:0.7rem;color:var(--faint);
                     letter-spacing:1px;text-transform:uppercase">
                     Batting Score</div>
                <div style="margin-top:1rem;font-size:0.85rem;color:var(--text)">
                    🏏 {int(s1.get("total_runs",0))} runs &nbsp;|&nbsp;
                    SR {s1.get("strike_rate",0):.1f} &nbsp;|&nbsp;
                    Avg {s1.get("average",0):.1f}
                </div>
            </div>""", unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="h2h-card"
                 style="border-top:3px solid {s2.get("color","var(--negative)")}">
                <div style="font-size:0.7rem;letter-spacing:2px;color:var(--faint);
                     text-transform:uppercase">Player 2</div>
                <div class="h2h-name" style="color:{s2.get("color","var(--negative)")}">
                    {team_dot(s2)}{p2}</div>
                <div style="font-size:0.75rem;color:var(--faint);margin-bottom:1rem">
                    {s2.get("team","Unknown")}</div>
                <div class="h2h-score">
                    {s2.get("batting_score", s2.get("allrounder_score", "—")):.1f}
                </div>
                <div style="font-size:0.7rem;color:var(--faint);
                     letter-spacing:1px;text-transform:uppercase">
                     Batting Score</div>
                <div style="margin-top:1rem;font-size:0.85rem;color:var(--text)">
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
                         title=f"{p1} vs {p2}",
                         color_discrete_map={
                             p1: s1.get("color", theme.SERIES[THEME][0]),
                             p2: s2.get("color", theme.SERIES[THEME][1])})
            fig.update_layout(**plotly_dark())
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
    st.markdown('<div class="section-title"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" style="vertical-align:middle;margin-right:8px"><polyline points="3,17 9,11 13,15 21,7" stroke="var(--accent)" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/><polyline points="17,7 21,7 21,11" stroke="var(--accent)" stroke-width="2" fill="none" stroke-linecap="round"/></svg>Season by Season Trends</div>',
                unsafe_allow_html=True)
    raw = load_season_data()
    if raw is not None and "season" in raw.columns:
        # Super overs are innings 3 and 4; they would distort a per-innings
        # average, so the team-score metric uses the two real innings only.
        main = raw[raw["innings"] <= 2].copy()
        # A team's score is runs off the bat plus every extra conceded to it.
        main["team_runs"] = main["runs_off_bat"] + main["runs_extras"]
        sr = main.groupby("season").agg(
            total_runs  =("team_runs", "sum"),
            legal_balls =("is_legal_ball", "sum"),
            matches     =("match_id", "nunique"),
        ).reset_index()

        # An innings is one team batting once — that is what "team score"
        # means. Dividing by matches counted both sides together and put the
        # figure at roughly twice a real T20 score.
        innings_per_season = (
            main.groupby("season")[["match_id", "innings"]]
            .apply(lambda g: g.drop_duplicates().shape[0])
            .rename("innings_count").reset_index()
        )
        sr = sr.merge(innings_per_season, on="season", how="left")

        sr["avg_score"] = (sr["total_runs"] / sr["innings_count"]).round(1)
        sr["run_rate"]  = (sr["total_runs"] / sr["legal_balls"] * 6).round(2)
        sr["season"]    = sr["season"].astype(str)
        sr = sr.sort_values("season")

        turf_line = theme.ramp("turf", THEME)[-1][1]
        turf_bar  = theme.ramp("turf", THEME)[1][1]

        def season_line(y, title, suffix=""):
            """
            A trend over time is a line, not a bar.

            Labels ride only the first, last and peak points — a number on
            every one of nineteen seasons is chaos and goes unread. The table
            underneath carries every value.
            """
            fig = px.line(sr, x="season", y=y, markers=True, title=title)
            fig.update_traces(
                line_color=turf_line, line_width=2,
                marker=dict(size=6, color=turf_line),
                hovertemplate="%{x}<br>%{y}" + suffix + "<extra></extra>",
            )
            peak = sr[y].idxmax()
            marked = {sr.index[0], sr.index[-1], peak}
            pts = sr.loc[sorted(marked)]
            fig.add_scatter(
                x=pts["season"], y=pts[y], mode="text",
                text=[f"{v}{suffix}" for v in pts[y]],
                textposition="top center",
                textfont=dict(size=11, color=T["text"]),
                hoverinfo="skip", showlegend=False,
            )
            # A fitted range on a line makes a real trend visible. (Never do
            # this to a bar — there the length is the value.)
            lo, hi = sr[y].min(), sr[y].max()
            pad = (hi - lo) * 0.35 or 1
            fig.update_layout(**plotly_dark(), showlegend=False)
            fig.update_yaxes(range=[lo - pad, hi + pad], title="")
            fig.update_xaxes(title="")
            return fig

        st.plotly_chart(
            season_line("run_rate", "Run rate by season — scoring has climbed"),
            use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(season_line("avg_score", "Average team score per innings"),
                            use_container_width=True)

        with col2:
            # Matches per season is context, not a trend: one flat colour, no
            # per-bar labels, and a real zero baseline because bar length is
            # the value.
            fig3 = px.bar(sr, x="season", y="matches",
                          title="Matches per season")
            fig3.update_traces(marker_color=turf_bar,
                               hovertemplate="%{x}<br>%{y} matches<extra></extra>")
            fig3.update_layout(**plotly_dark(), showlegend=False)
            fig3.update_yaxes(title="", rangemode="tozero")
            fig3.update_xaxes(title="")
            st.plotly_chart(fig3, use_container_width=True)

        st.markdown('<div class="section-title"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" style="vertical-align:middle;margin-right:8px"><line x1="7" y1="4" x2="7" y2="20" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/><line x1="12" y1="4" x2="12" y2="20" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/><line x1="17" y1="4" x2="17" y2="20" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/><line x1="5" y1="5" x2="9.5" y2="3.5" stroke="var(--gold)" stroke-width="1.5" stroke-linecap="round"/><line x1="9.5" y1="3.5" x2="14.5" y2="3.5" stroke="var(--gold)" stroke-width="1.5" stroke-linecap="round"/><line x1="14.5" y1="3.5" x2="19" y2="5" stroke="var(--gold)" stroke-width="1.5" stroke-linecap="round"/></svg>Season Data Table</div>',
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
    st.markdown('<div class="section-title"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" style="vertical-align:middle;margin-right:8px"><path d="M2 17L5 7l5 5 4-8 4 8 5-5 3 10H2z" fill="var(--gold)" stroke="none"/><rect x="2" y="17" width="20" height="3" rx="1" fill="var(--gold)"/></svg>Predicted Best XI &mdash; IPL 2026</div>',
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
            best_xi.append({"role":"Wicketkeeper", "player": wk,
                "score": row["batting_score"],
                "stat": f"Avg {row['average']:.1f}  •  SR {row['strike_rate']:.1f}"})
            added.add(wk)

        # 4 Batsmen
        count = 0
        for _, row in bat_df.iterrows():
            if row["player"] not in added and count < 4:
                best_xi.append({"role": f"Batsman {count+1}",
                    "player": row["player"],
                    "score": row["batting_score"],
                    "stat": f"Avg {row['average']:.1f}  •  SR {row['strike_rate']:.1f}"})
                added.add(row["player"]); count += 1

        # 3 All-rounders
        count = 0
        for _, row in ar_df.iterrows():
            if row["player"] not in added and count < 3:
                best_xi.append({"role": f"All-rounder {count+1}",
                    "player": row["player"],
                    "score": row["allrounder_score"],
                    "stat": f"Bat {row['batting_score']:.0f}  •  Bowl {row['bowling_score']:.0f}"})
                added.add(row["player"]); count += 1

        # 3 Bowlers
        count = 0
        for _, row in bowl_df.iterrows():
            if row["player"] not in added and count < 3:
                best_xi.append({"role": f"Bowler {count+1}",
                    "player": row["player"],
                    "score": row["bowling_score"],
                    "stat": f"Econ {row['economy']:.2f}  •  {int(row['wickets'])} wkts"})
                added.add(row["player"]); count += 1

        # Display XI in cricket formation style
        col1, col2 = st.columns([2, 1])
        with col1:
            for item in best_xi:
                color = get_team_color(item["player"])
                team  = get_player_team(item["player"]) or "Unknown"
                ti    = get_team_info(item["player"])
                st.markdown(f"""
                <div class="xi-card" style="border-left:3px solid {color}">
                    <div class="xi-role">{item["role"]}</div>
                    <div>
                        <div class="xi-name">{avatar_html(item["player"], 36)}{item["player"]}</div>
                        <div style="font-size:0.7rem;color:var(--faint)">{team}</div>
                        <div style="font-size:0.75rem;color:var(--text);margin-top:2px">
                            {item["stat"]}</div>
                    </div>
                    <div class="xi-score">
                        {item["score"]:.1f}</div>
                </div>""", unsafe_allow_html=True)

        with col2:
            # Donut chart of XI composition
            roles   = ["Wicketkeeper","Batsmen","All-rounders","Bowlers"]
            values  = [1, 4, 3, 3]
            # Four labelled slices, so shade carries the order and the label
            # carries the identity — three categorical hues would not stretch
            # to four without repeating one.
            colors  = theme.ordinal(THEME, len(roles))
            fig = go.Figure(go.Pie(
                labels=roles, values=values,
                hole=0.6,
                marker_colors=colors,
                textinfo="label+value",
                insidetextorientation="horizontal",
                textfont_color=T["text_muted"]
            ))
            fig.update_layout(
                **plotly_dark(),
                title="Team Composition",
                showlegend=False,
                annotations=[dict(text="Best<br>XI",
                                  x=0.5, y=0.5, font_size=16,
                                  font_color=T["text"],
                                  showarrow=False)]
            )
            st.plotly_chart(fig, use_container_width=True)

            # Score bars
            st.markdown('<div class="section-title" style="font-size:1rem"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" style="vertical-align:middle;margin-right:8px"><polyline points="3,17 9,11 13,15 21,7" stroke="var(--accent)" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/><polyline points="17,7 21,7 21,11" stroke="var(--accent)" stroke-width="2" fill="none" stroke-linecap="round"/></svg>Score Breakdown</div>',
                        unsafe_allow_html=True)
            xi_df = pd.DataFrame(best_xi)
            fig2  = px.bar(xi_df, x="score", y="player",
                           orientation="h",
                           color="score",
                           color_continuous_scale=theme.ramp("indigo", THEME),
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
    st.markdown('<div class="section-title"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" style="vertical-align:middle;margin-right:8px"><circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="2"/><line x1="16.5" y1="16.5" x2="22" y2="22" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>Player Search</div>',
                unsafe_allow_html=True)
    search = st.text_input("", placeholder="Search — e.g. Kohli, Bumrah, Narine...",
                           label_visibility="collapsed")

    if search:
        found = False

        for dtype, score_col, label, icon in [
            ("batting",  "batting_score",  "Batting",    ""),
            ("bowling",  "bowling_score",  "Bowling",    ""),
            ("allrounder","allrounder_score","All-rounder",""),
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
                                {team_dot(ti)}{name}</div>
                            <div style="font-size:0.75rem;color:var(--faint)">
                                {ti["team_name"]}</div>
                            <div class="h2h-score">
                                {result.iloc[0][score_col]:.1f}</div>
                            <div style="font-size:0.7rem;color:var(--faint);
                                 letter-spacing:1px;text-transform:uppercase">
                                 {label} Score</div>
                        </div>""", unsafe_allow_html=True)

                    st.markdown(f"**{icon} {label} Stats**")
                    st.dataframe(result, use_container_width=True,
                                 hide_index=True)

        if not found:
            st.markdown(f"""
            <div style="text-align:center;padding:3rem;color:var(--faint)">
                <div style="font-size:3rem">🔍</div>
                <div style="font-size:1.2rem;margin-top:0.5rem">
                    No results for "<b style="color:var(--text)">{search}</b>"
                </div>
                <div style="font-size:0.85rem;margin-top:0.3rem">
                    Try a different name or partial name</div>
            </div>""", unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:2rem 0 1rem;
     border-top:1px solid var(--border);margin-top:2rem;
     font-size:0.75rem;color:var(--faint);letter-spacing:1px">
    CRICKET ANALYTICS PLATFORM &nbsp; • &nbsp;
    Data: Cricsheet.org &nbsp; • &nbsp;
    Built with Python · Streamlit · Plotly &nbsp; • &nbsp;
    100% Free & Open Source &nbsp; • &nbsp;
    IPL 2026 — RCB back-to-back champions
</div>
""", unsafe_allow_html=True)
# ── TAB 9 — LIVE SCORES (Cricbuzz Style) ──────────────
with tab9:
    import urllib.request as _ur, json as _json

    API_KEY = config.get_cricapi_key()

    st.markdown("""
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
        """
        The team's own brand colour, plus a legible foreground for it.

        Replaces a set of pale-background/dark-text pairs that were built for a
        light surface and read badly on the dark one. IPL_TEAMS is the same
        source the leaderboards use, so a side is one colour everywhere.
        """
        for team, meta in IPL_TEAMS.items():
            if team.lower() in name.lower() or meta["short"].lower() == name.lower():
                return meta["color"], _readable_on(meta["color"])
        # Short forms Cricsheet writes differently to our canonical names.
        for fragment, team in [("royal challengers", "Royal Challengers Bengaluru"),
                               ("bangalore", "Royal Challengers Bengaluru"),
                               ("kings xi", "Punjab Kings"),
                               ("daredevils", "Delhi Capitals")]:
            if fragment in name.lower():
                c = IPL_TEAMS[team]["color"]
                return c, _readable_on(c)
        return T["surface_2"], T["text_muted"]

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
                '<div style="font-size:0.82rem;color:var(--faint);">Scorecard unavailable</div>'
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
                '<span style="font-size:0.68rem;color:var(--faint);">🪙 Toss:</span>'
                '<span style="font-size:0.72rem;color:var(--muted);">'
                + toss_w.title() + " won & chose to " + toss_c +
                '</span></div>'
            )

        st.markdown(
            '<div style="padding:10px 0 6px;">'
            '<div style="font-size:0.68rem;color:var(--faint);margin-bottom:6px;">📍 ' + venue + ' &nbsp;·&nbsp; 📅 ' + date_str + '</div>'
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
                '<div style="font-size:0.85rem;font-weight:600;color:var(--text);margin-bottom:4px;">Scorecard Coming Soon</div>'
                '<div style="font-size:0.75rem;color:var(--faint);">Ball-by-ball data will appear here once the match progresses</div>'
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
                        '<span style="font-size:0.72rem;color:var(--faint);">Need ' + str(needed) + ' off ' + str(balls_left) + ' balls</span>'
                        '<span style="font-size:0.72rem;font-weight:600;color:var(--gold);">RRR: ' + str(rrr) + '</span>'
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
                        '<div style="display:flex;justify-content:space-between;font-size:0.65rem;color:var(--faint);margin-bottom:4px;">'
                        '<span>' + t_name[:15] + ' ' + str(chase_prob) + '%</span>'
                        '<span>' + str(bat_prob) + '% ' + score_arr[0].get("inning","").replace(" Inning 1","")[:15] + '</span>'
                        '</div>'
                        '<div style="height:5px;background:rgba(255,255,255,0.08);border-radius:3px;overflow:hidden;">'
                        '<div style="height:100%;width:' + str(bar_w) + '%;background:var(--accent-mark);border-radius:3px;"></div>'
                        '</div>'
                        '</div>'
                    )

            logo_html = ""
            if logo:
                logo_html = '<img src="' + logo + '" width="30" height="30" style="border-radius:50%;object-fit:contain;background:#fff;padding:2px;">'

            win_tag = ""
            if is_win and ended:
                win_tag = ' <span style="background:var(--accent-soft);color:var(--text);font-size:0.6rem;font-weight:700;padding:2px 7px;border-radius:8px;">WON</span>'

            border = "var(--border-strong)" if is_win and ended else ("var(--seam)" if is_live_inn else "var(--border)")
            bg     = "var(--accent-soft)" if is_win and ended else ("var(--seam-soft)" if is_live_inn else "transparent")
            live_dot = '<span style="display:inline-block;width:7px;height:7px;background:var(--negative);border-radius:50%;margin-right:5px;"></span>' if is_live_inn else ""

            st.markdown(
                '<div style="background:' + bg + ';border:0.5px solid ' + border + ';border-radius:12px;padding:12px 14px;margin-bottom:10px;">'
                # Header row
                '<div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">'
                + logo_html +
                '<div style="flex:1;">'
                '<div style="font-size:0.68rem;color:var(--faint);margin-bottom:1px;">' + live_dot + inn_num + '</div>'
                '<div style="font-size:0.88rem;font-weight:600;color:var(--text);">' + t_name + win_tag + '</div>'
                '</div>'
                '<div style="text-align:right;">'
                '<div style="font-family:Rajdhani,sans-serif;font-size:1.7rem;font-weight:700;color:var(--text);line-height:1;">'
                + str(runs) + '<span style="font-size:0.95rem;color:var(--faint);font-weight:400;">/' + str(wkts) + '</span></div>'
                '<div style="font-size:0.65rem;color:var(--faint);">' + str(overs) + ' ov</div>'
                '</div></div>'
                # Overs progress bar
                '<div style="margin-bottom:8px;">'
                '<div style="display:flex;justify-content:space-between;font-size:0.62rem;color:var(--faint);margin-bottom:3px;">'
                '<span>Overs: ' + str(overs) + ' / ' + str(total_overs) + '</span>'
                '<span>' + proj + '</span>'
                '</div>'
                '<div style="height:4px;background:rgba(255,255,255,0.08);border-radius:2px;overflow:hidden;">'
                '<div style="height:100%;width:' + str(pct) + '%;background:var(--accent-mark);border-radius:2px;"></div>'
                '</div></div>'
                # Stats strip
                '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:5px;">'
                '<div style="background:rgba(255,255,255,0.03);border-radius:6px;padding:5px;text-align:center;">'
                '<div style="font-size:0.6rem;color:var(--faint);">Runs</div>'
                '<div style="font-size:0.85rem;font-weight:600;color:var(--text);">' + str(runs) + '</div>'
                '</div>'
                '<div style="background:rgba(255,255,255,0.03);border-radius:6px;padding:5px;text-align:center;">'
                '<div style="font-size:0.6rem;color:var(--faint);">Wkts</div>'
                '<div style="font-size:0.85rem;font-weight:600;color:var(--text);">' + str(wkts) + '</div>'
                '</div>'
                '<div style="background:rgba(255,255,255,0.03);border-radius:6px;padding:5px;text-align:center;">'
                '<div style="font-size:0.6rem;color:var(--faint);">CRR</div>'
                '<div style="font-size:0.85rem;font-weight:600;color:var(--accent);">' + str(rr) + '</div>'
                '</div>'
                '<div style="background:rgba(255,255,255,0.03);border-radius:6px;padding:5px;text-align:center;">'
                '<div style="font-size:0.6rem;color:var(--faint);">Balls</div>'
                '<div style="font-size:0.85rem;font-weight:600;color:var(--text);">' + str(total_balls) + '</div>'
                '</div>'
                '</div>'
                + rrr_html + win_prob +
                '</div>',
                unsafe_allow_html=True
            )

        # ── Result banner ──
        if ended and status:
            st.markdown(
                '<div style="background:var(--accent-soft);border:0.5px solid var(--border-strong);'
                'border-radius:10px;padding:10px 14px;text-align:center;margin-top:4px;">'
                '<span style="font-size:0.85rem;font-weight:600;color:var(--accent);">🏆 ' + status + '</span>'
                '</div>',
                unsafe_allow_html=True
            )
        elif started and not ended:
            st.markdown(
                '<div style="background:rgba(255,68,68,0.06);border:0.5px solid rgba(255,68,68,0.2);'
                'border-radius:10px;padding:8px 14px;text-align:center;margin-top:4px;">'
                '<span style="font-size:0.78rem;color:var(--negative);">🔴 Match in Progress · Ball-by-ball data requires premium API plan</span>'
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
            '<span style="font-size:0.65rem;color:var(--faint);">' + mtype + '</span>'
            + badges +
            '</div></div>'
            '<div class="m-body">'
            '<div style="font-size:0.78rem;font-weight:600;color:var(--text);margin-bottom:8px;">' + match_title + '</div>'
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
            '<div class="stat-card"><div class="stat-value" style="color:var(--accent);">' + str(len(ipl)) + '</div><div class="stat-label">IPL 2026</div></div>'
            '<div class="stat-card"><div class="stat-value" style="color:var(--negative);">' + str(len(live_now)) + '</div><div class="stat-label">Live Now</div></div>'
            '<div class="stat-card"><div class="stat-value" style="color:var(--gold);">' + str(len(upcoming)) + '</div><div class="stat-label">Upcoming</div></div>'
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
                    '<div style="font-family:Rajdhani,sans-serif;font-size:1.3rem;color:var(--text);margin:0.8rem 0;font-weight:700;">No IPL Matches Right Now</div>'
                    '<div style="color:var(--faint);font-size:0.82rem;">IPL 2026 playoffs · Matches at 3:30 PM &amp; 7:30 PM IST</div>'
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
        Team Intelligence — Opposition Analysis
    </div>''', unsafe_allow_html=True)

    team_list = list(IPL_TEAMS.keys())
    col1, mid, col2 = st.columns([5,1,5])
    with col1:
        team1 = st.selectbox("Your team", team_list, index=0)
    with mid:
        st.markdown('<div class="vs-badge">VS</div>', unsafe_allow_html=True)
    with col2:
        team2 = st.selectbox("Opponent", team_list, index=1)

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
                <div style="font-size:0.7rem;letter-spacing:2px;color:var(--faint);
                     text-transform:uppercase">Your Team</div>
                <div class="h2h-name" style="color:{ti1["color"]}">
                    {team_dot(ti1)}{team1}</div>
                <div style="font-size:2rem;font-family:'Rajdhani',sans-serif;
                     font-weight:700;color:{ti1["color"]};margin-top:0.5rem">
                    {ti1["short"]}</div>
            </div>''', unsafe_allow_html=True)
        with c2:
            st.markdown(f'''
            <div class="h2h-card" style="border-top:3px solid {ti2["color"]}">
                <div style="font-size:0.7rem;letter-spacing:2px;color:var(--faint);
                     text-transform:uppercase">Opponent</div>
                <div class="h2h-name" style="color:{ti2["color"]}">
                    {team_dot(ti2)}{team2}</div>
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
            "SWOT", "Stats Comparison",
            "Batting", "Bowling",
            "Best XI vs Opponent", "Player Matchups"
        ])

        # SWOT
        with it1:
            swot1 = generate_swot(team1, stats1, stats2)
            swot2 = generate_swot(team2, stats2, stats1)

            st.markdown(f'<div class="section-title" style="font-size:1.1rem">'
                        f'{team_dot(ti1)}{team1} — SWOT Analysis</div>',
                        unsafe_allow_html=True)

            sc1,sc2,sc3,sc4 = st.columns(4)
            swot_styles = {
                "strengths":    (T["accent"],"↑","STRENGTHS"),
                "weaknesses":   (T["negative"],"↓","WEAKNESSES"),
                "opportunities":(T["gold"],"→","OPPORTUNITIES"),
                "threats":      (T["text_muted"],"!","THREATS"),
            }
            for col_widget, (key, (color, icon, label)) in zip(
                [sc1,sc2,sc3,sc4], swot_styles.items()):
                with col_widget:
                    items_html = "".join(
                        f'<div style="padding:0.4rem 0;border-bottom:1px solid var(--border);'
                        f'font-size:0.82rem;color:var(--text)">{item}</div>'
                        for item in swot1[key]
                    )
                    st.markdown(f'''
                    <div style="background:var(--surface);border:1px solid {color}33;
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
                        f'{team_dot(ti2)}{team2} — SWOT Analysis</div>',
                        unsafe_allow_html=True)

            sc1,sc2,sc3,sc4 = st.columns(4)
            for col_widget, (key, (color, icon, label)) in zip(
                [sc1,sc2,sc3,sc4], swot_styles.items()):
                with col_widget:
                    items_html = "".join(
                        f'<div style="padding:0.4rem 0;border-bottom:1px solid var(--border);'
                        f'font-size:0.82rem;color:var(--text)">{item}</div>'
                        for item in swot2[key]
                    )
                    st.markdown(f'''
                    <div style="background:var(--surface);border:1px solid {color}33;
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
                        gridcolor=T["grid"],color=T["text_muted"]),
                    angularaxis=dict(gridcolor=T["grid"],color=T["text_muted"])),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color=T["text_muted"],
                title=f"{team1} vs {team2} — Team Radar",
                title_font_color=T["text"],
                legend=dict(font_color=T["text"],bgcolor="rgba(0,0,0,0)")
            )
            st.plotly_chart(fig, use_container_width=True)

        # Batting breakdown
        with it3:
            c1, c2 = st.columns(2)
            for col_w, tname, tinfo in [(c1,team1,ti1),(c2,team2,ti2)]:
                with col_w:
                    st.markdown(f'<div class="section-title" style="font-size:1rem">'
                                f'{team_dot(tinfo)}{tname}</div>',
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
                                <div class="lb-score">
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
                                f'{team_dot(tinfo)}{tname}</div>',
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
                                <div class="lb-score">
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
                                f'{team_dot(tinfo)}{tname} — Best XI vs {opp_name}</div>',
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
                                    <div style="font-size:0.7rem;color:var(--faint)">
                                        {item["reason"]}</div>
                                </div>
                                <div class="xi-score">
                                    {item["score"]:.1f}</div>
                            </div>''', unsafe_allow_html=True)
                    else:
                        st.info(f"Not enough data for {tname}")

        # Player matchups
        with it6:
            st.markdown(f'<div class="section-title">Key Matchups — {team1} Batters vs {team2} Bowlers</div>',
                        unsafe_allow_html=True)
            matchups = get_player_matchups(team1, team2, scores)

            if matchups:
                adv_colors = {"batter":T["accent"],"bowler":T["negative"],"neutral":T["text_muted"]}
                adv_icons  = {"batter":"🏏","bowler":"🎯","neutral":"⚖️"}

                for m in matchups:
                    adv   = m["advantage"]
                    color = adv_colors[adv]
                    icon  = adv_icons[adv]
                    b1c   = get_team_color(m["batter"])
                    b2c   = get_team_color(m["bowler"])
                    st.markdown(f'''
                    <div style="background:var(--surface);border:1px solid var(--border);
                         border-left:3px solid {color};border-radius:10px;
                         padding:0.8rem 1rem;margin-bottom:0.5rem;
                         display:flex;align-items:center;gap:1rem">
                        <div style="flex:1">
                            <span style="color:{b1c};font-weight:700">
                                {avatar_html(m["batter"],28)}{m["batter"]}</span>
                            <span style="color:var(--faint);font-size:0.8rem">
                                &nbsp;SR {m["bat_sr"]:.0f}</span>
                        </div>
                        <div style="text-align:center;font-size:1.2rem">{icon}</div>
                        <div style="flex:1;text-align:right">
                            <span style="color:var(--faint);font-size:0.8rem">
                                Econ {m["bowl_econ"]:.2f}&nbsp;</span>
                            <span style="color:{b2c};font-weight:700">
                                {m["bowler"]}{avatar_html(m["bowler"],28)}</span>
                        </div>
                        <div style="width:90px;text-align:center">
                            <div style="color:{color};font-size:0.75rem;font-weight:700">
                                {adv.upper()} EDGE</div>
                            <div style="color:var(--faint);font-size:0.7rem">{m["edge"]}</div>
                        </div>
                    </div>''', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f'<div class="section-title">{team2} Batters vs {team1} Bowlers</div>',
                            unsafe_allow_html=True)
                reverse = get_player_matchups(team2, team1, scores)
                for m in reverse:
                    adv   = m["advantage"]
                    color = adv_colors[adv]
                    icon  = adv_icons[adv]
                    b1c   = get_team_color(m["batter"])
                    b2c   = get_team_color(m["bowler"])
                    st.markdown(f'''
                    <div style="background:var(--surface);border:1px solid var(--border);
                         border-left:3px solid {color};border-radius:10px;
                         padding:0.8rem 1rem;margin-bottom:0.5rem;
                         display:flex;align-items:center;gap:1rem">
                        <div style="flex:1">
                            <span style="color:{b1c};font-weight:700">
                                {avatar_html(m["batter"],28)}{m["batter"]}</span>
                            <span style="color:var(--faint);font-size:0.8rem">
                                &nbsp;SR {m["bat_sr"]:.0f}</span>
                        </div>
                        <div style="text-align:center;font-size:1.2rem">{icon}</div>
                        <div style="flex:1;text-align:right">
                            <span style="color:var(--faint);font-size:0.8rem">
                                Econ {m["bowl_econ"]:.2f}&nbsp;</span>
                            <span style="color:{b2c};font-weight:700">
                                {m["bowler"]}{avatar_html(m["bowler"],28)}</span>
                        </div>
                        <div style="width:90px;text-align:center">
                            <div style="color:{color};font-size:0.75rem;font-weight:700">
                                {adv.upper()} EDGE</div>
                            <div style="color:var(--faint);font-size:0.7rem">{m["edge"]}</div>
                        </div>
                    </div>''', unsafe_allow_html=True)
            else:
                st.info("Not enough data for matchup analysis")
