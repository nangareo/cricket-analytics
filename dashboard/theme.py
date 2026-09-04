"""
Design tokens for the dashboard.

One place defines colour, type and spacing for both themes. Plotly takes its
colours in Python rather than CSS, so the palette has to exist on both sides —
`css()` emits it as custom properties, `chart_layout()` hands the same values
to the charts.

Colour choices were validated against the surfaces they actually render on
(dark #0E1116, light #FAFAF8): every series colour clears the lightness band,
the chroma floor and adjacent-pair colour-vision separation. Light-mode aqua
sits at 2.69:1, which is fine for a chart mark carrying a direct label but not
for text — hence the separate `accent_text` step at 5.11:1.
"""

THEMES = ("dark", "light")
DEFAULT_THEME = "dark"

TOKENS = {
    "dark": {
        "bg":            "#0E1116",
        "surface":       "#151A21",
        "surface_2":     "#1B212A",
        "surface_hover": "#202834",
        "border":        "rgba(255,255,255,0.09)",
        "border_strong": "rgba(255,255,255,0.16)",
        "grid":          "#232A34",
        "text":          "#E8EDF4",   # 16.1:1
        "text_muted":    "#AAB4C2",   #  9.0:1
        "text_faint":    "#8A94A3",   #  6.2:1  — readable, not decorative
        "accent":        "#E8EDF4",   # 16.1:1 — ink. The UI carries no hue.
        "accent_mark":   "#AAB4C2",   #  9.0:1 — graphite fills and meters
        "accent_soft":   "rgba(255,255,255,0.06)",
        "seam":          "#D9564A",   #  4.9:1  — cricket-ball seam, reserved
        "seam_soft":     "rgba(217,86,74,0.16)",
        "leather":       "#8C2F26",   # ball body, decorative motifs only
        "turf":          "rgba(47,190,140,0.06)",   # pitch strip only
        "gold":          "#D9A441",
        "silver":        "#A8B0BC",
        "bronze":        "#B87A4B",
        "negative":      "#E06B6B",
        "shadow":        "0 1px 2px rgba(0,0,0,0.4)",
    },
    "light": {
        "bg":            "#FAFAF8",
        "surface":       "#FFFFFF",
        "surface_2":     "#F4F5F2",
        "surface_hover": "#EFF1ED",
        "border":        "rgba(11,11,11,0.11)",
        "border_strong": "rgba(11,11,11,0.20)",
        "grid":          "#E6E7E1",
        "text":          "#12161C",   # 17.4:1
        "text_muted":    "#5A6472",   #  5.7:1
        "text_faint":    "#68727F",   #  4.7:1  — readable, not decorative
        "accent":        "#12161C",   # 17.4:1 — ink. The UI carries no hue.
        "accent_mark":   "#5A6472",   #  5.7:1 — graphite fills and meters
        "accent_soft":   "rgba(11,11,11,0.05)",
        "seam":          "#C1443A",   #  4.8:1  — cricket-ball seam, reserved
        "seam_soft":     "rgba(193,68,58,0.10)",
        "leather":       "#8C2F26",   # ball body, decorative motifs only
        "turf":          "rgba(15,122,85,0.05)",    # pitch strip only
        "gold":          "#9A6F12",
        "silver":        "#6B7280",
        "bronze":        "#8A5626",
        "negative":      "#C0392F",
        "shadow":        "0 1px 2px rgba(11,11,11,0.06)",
    },
}

# ── CHART COLOUR ──────────────────────────────────────
# Drawn from cricket's own materials rather than a generic chart palette:
# turf (the outfield), leather (the ball), willow (the bat), sightscreen sky.
#
# Every value below was checked with the palette validator against the real
# surfaces (#0E1116 / #FAFAF8), not chosen by eye.

# Sequential ramps for magnitude. One hue each, pale→deep on light and
# deep→bright on dark, so "more" is always the more prominent end.
# Batting charts wear willow, bowling charts wear leather — the bat and the
# ball. Everything else uses turf.
#
# The ranges are deliberately compressed. These bars are *discrete ordered
# marks*, one per player, not a continuous field, so the ordinal rule applies:
# every step has to stay visible against the surface. The full range ran the
# quiet end down to 1.2:1, which left the shortest bars all but invisible.
# Each ramp is validated as an ordinal scale in both modes.
SEQUENTIAL_RAMPS = {
    "willow": {
        "light": [[0.0, "#C2A25C"], [0.5, "#A48441"], [1.0, "#7E5F16"]],
        "dark":  [[0.0, "#75591F"], [0.5, "#AA8232"], [1.0, "#DFB05A"]],
    },
    "leather": {
        "light": [[0.0, "#CE8E7C"], [0.5, "#B26857"], [1.0, "#8E3524"]],
        "dark":  [[0.0, "#803824"], [0.5, "#AF5340"], [1.0, "#DE7460"]],
    },
    "turf": {
        "light": [[0.0, "#7FAE91"], [0.5, "#5A9070"], [1.0, "#26663F"]],
        "dark":  [[0.0, "#2A6B45"], [0.5, "#449566"], [1.0, "#5FBE8A"]],
    },
    "indigo": {
        "light": [[0.0, "#93A3D8"], [0.5, "#4E63AE"], [1.0, "#26377A"]],
        "dark":  [[0.0, "#38508F"], [0.5, "#5B74BE"], [1.0, "#8098DE"]],
    },
}

def ramp(name, theme):
    """A sequential colour scale by material name."""
    return SEQUENTIAL_RAMPS.get(name, SEQUENTIAL_RAMPS["turf"])[
        theme if theme in THEMES else DEFAULT_THEME
    ]


# Back-compat default for any chart that has not picked a material.
SEQUENTIAL = {t: SEQUENTIAL_RAMPS["turf"][t] for t in THEMES}

# Fixed categorical order: willow, indigo, leather. Never cycled.
# Green is deliberately absent here — it survives only where it means grass.
# Indigo sits in the middle so willow never touches leather: amber beside red
# measures ΔE 13.9 to normal vision, under the 15 floor.
SERIES = {
    "light": ["#9C7526", "#4E63AE", "#B0432F"],
    "dark":  ["#B08830", "#5B74BE", "#CE5A46"],
}
MAX_SERIES = len(SERIES["dark"])

# Ordinal steps of a single hue, for a small set of ordered-but-labelled
# categories (the Best XI composition donut). Every slice carries its own
# label, so shade can do the work instead of four competing hues — which
# would exceed the three-slot categorical cap. Validated as an ordinal ramp:
# monotone lightness, visible step gaps, palest step clear of the surface.
ORDINAL_INDIGO = {
    "light": ["#26377A", "#3E51A0", "#6377C4", "#93A3D8"],
    "dark":  ["#8098DE", "#6478C6", "#485AA6", "#334A85"],
}


def ordinal(theme, n=4):
    steps = ORDINAL_INDIGO[theme if theme in THEMES else DEFAULT_THEME]
    return steps[:n]

FONT_STACK = ("system-ui, -apple-system, 'Segoe UI', Roboto, "
              "'Helvetica Neue', Arial, sans-serif")


def tokens(theme):
    return TOKENS.get(theme, TOKENS[DEFAULT_THEME])


def chart_layout(theme):
    """Plotly layout matching the active theme. Recessive grid, quiet ink."""
    t = tokens(theme)
    axis = dict(
        gridcolor=t["grid"],
        linecolor=t["grid"],
        zerolinecolor=t["grid"],
        color=t["text_muted"],
        tickfont=dict(size=11, color=t["text_muted"]),
        title_font=dict(size=11, color=t["text_faint"]),
    )
    return dict(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT_STACK, size=12, color=t["text_muted"]),
        title_font=dict(family=FONT_STACK, size=13, color=t["text"]),
        title_x=0,
        title_xanchor="left",
        margin=dict(l=8, r=8, t=44, b=8),
        hoverlabel=dict(
            bgcolor=t["surface_2"],
            bordercolor=t["border_strong"],
            font=dict(family=FONT_STACK, size=12, color=t["text"]),
        ),
        legend=dict(
            font=dict(size=11, color=t["text_muted"]),
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
        ),
        xaxis=axis,
        yaxis=axis,
    )


def css(theme):
    """The full stylesheet, with the active theme's tokens on :root."""
    t = tokens(theme)
    return f"""
<style>
:root {{
  --bg:{t['bg']}; --surface:{t['surface']}; --surface-2:{t['surface_2']};
  --surface-hover:{t['surface_hover']};
  --border:{t['border']}; --border-strong:{t['border_strong']}; --grid:{t['grid']};
  --text:{t['text']}; --muted:{t['text_muted']}; --faint:{t['text_faint']};
  --accent:{t['accent']}; --accent-mark:{t['accent_mark']}; --accent-soft:{t['accent_soft']};
  --gold:{t['gold']}; --silver:{t['silver']}; --bronze:{t['bronze']};
  --negative:{t['negative']}; --shadow:{t['shadow']};
  --seam:{t['seam']}; --seam-soft:{t['seam_soft']};
  --leather:{t['leather']}; --turf:{t['turf']};

  /* 4-point spacing scale */
  --s1:4px; --s2:8px; --s3:12px; --s4:16px; --s5:24px; --s6:32px; --s7:48px;
  --radius:10px; --radius-sm:6px;
}}

/* ── BASE ───────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"], .stApp {{
  background:var(--bg) !important;
  color:var(--text) !important;
  font-family:{FONT_STACK};
  -webkit-font-smoothing:antialiased;
}}
[data-testid="stHeader"], [data-testid="stDecoration"] {{ background:transparent !important; }}
[data-testid="stSidebar"], [data-testid="collapsedControl"] {{ display:none !important; }}
[data-testid="stToolbar"], [data-testid="stStatusWidget"] ~ div,
.stDeployButton, #MainMenu, footer {{ display:none !important; }}
.block-container {{ padding:var(--s5) var(--s5) var(--s7); max-width:1240px; }}

/* Numerals line up in columns. The single biggest win on a stats table. */
.lb-stat, .lb-score, .lb-rank, .stat-value, .player-score, .xi-score,
.h2h-score, .mini-val, .hero-stat-num, .t-score, .t-overs, .sc-tbl td {{
  font-variant-numeric:tabular-nums;
  font-feature-settings:"tnum" 1;
}}

/* ── TABS ───────────────────────────────────────── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {{
  gap:var(--s1); background:transparent;
  border-bottom:1px solid var(--border);
  margin-bottom:var(--s5);
}}
[data-testid="stTabs"] [data-baseweb="tab"] {{
  background:transparent !important; border:none !important;
  padding:10px var(--s3); color:var(--muted) !important;
  font-size:12px; font-weight:500; letter-spacing:0.06em; text-transform:uppercase;
  border-bottom:2px solid transparent !important; border-radius:0 !important;
  transition:color .15s ease, border-color .15s ease;
}}
[data-testid="stTabs"] [data-baseweb="tab"]:hover {{ color:var(--text) !important; }}
[data-testid="stTabs"] [aria-selected="true"] {{
  color:var(--text) !important; border-bottom-color:var(--accent) !important;
}}
[data-testid="stTabs"] [data-baseweb="tab-highlight"],
[data-testid="stTabs"] [data-baseweb="tab-border"] {{ display:none !important; }}

/* ── HEADER ─────────────────────────────────────── */
/* The header sits on a cricket pitch: a pale strip of turf with the two
   creases marked out, and a ball-seam arc drifting behind the title. Both
   are drawn in tokens, so they follow the theme and stay quiet. */
.hero {{
  position:relative; overflow:hidden;
  display:flex; align-items:flex-end; justify-content:space-between;
  gap:var(--s5);
  padding:var(--s5) var(--s5) var(--s4);
  margin-bottom:var(--s4);
  border:1px solid var(--border); border-radius:var(--radius);
  background:
    /* popping creases */
    linear-gradient(90deg, transparent 0 11%, var(--border) 11% calc(11% + 1px), transparent calc(11% + 1px)),
    linear-gradient(90deg, transparent 0 89%, var(--border) 89% calc(89% + 1px), transparent calc(89% + 1px)),
    /* the strip itself */
    linear-gradient(180deg, var(--turf), transparent 70%),
    var(--surface);
}}
/* Ball seam: two arcs of stitching, low enough to read as texture. */
.hero::after {{
  content:""; position:absolute; right:-70px; top:-70px;
  width:260px; height:260px; border-radius:50%;
  border:1px solid var(--seam-soft);
  box-shadow:inset 0 0 0 26px transparent, inset 0 0 0 27px var(--seam-soft);
  opacity:.9; pointer-events:none;
}}
.hero > * {{ position:relative; z-index:1; }}
.hero-eyebrow {{
  font-size:10px; font-weight:600; letter-spacing:0.18em; text-transform:uppercase;
  color:var(--faint); margin-bottom:var(--s2);
}}
.hero-title {{
  font-size:28px; font-weight:600; letter-spacing:-0.02em;
  color:var(--text); line-height:1.1; margin:0;
}}
.hero-sub {{ font-size:13px; color:var(--muted); margin-top:var(--s2); }}
.hero-badge {{
  display:inline-flex; align-items:center; gap:6px;
  background:var(--accent-soft); color:var(--accent);
  border:1px solid var(--border); border-radius:100px;
  padding:4px 10px; font-size:11px; font-weight:600; letter-spacing:0.04em;
}}
/* A struck-ball mark for the trophy line. */
.hero-badge::before {{
  content:""; width:7px; height:7px; border-radius:50%;
  background:var(--seam); flex-shrink:0;
}}
.hero-stats-strip {{ display:flex; gap:var(--s5); }}
.hero-stat-item {{ text-align:right; }}
.hero-stat-num {{ font-size:20px; font-weight:600; color:var(--text); line-height:1.2; }}
.hero-stat-lbl {{
  font-size:10px; letter-spacing:0.12em; text-transform:uppercase; color:var(--faint);
}}

/* ── SECTION TITLES ─────────────────────────────── */
.section-title {{
  display:flex; align-items:center;
  font-size:11px; font-weight:600; letter-spacing:0.14em; text-transform:uppercase;
  color:var(--muted); margin:var(--s6) 0 var(--s3);
  gap:var(--s2);
}}
.section-title svg {{ opacity:.7; }}
/* A seam stitch, borrowed from the ball, standing in for a plain rule. */
.section-title::after {{
  content:""; flex:1; height:1px; margin-left:var(--s3);
  background:repeating-linear-gradient(90deg,
    var(--border) 0 6px, transparent 6px 12px);
}}
.section-sep {{
  height:1px; border:0; margin:var(--s5) 0;
  background:repeating-linear-gradient(90deg,
    var(--border) 0 6px, transparent 6px 12px);
}}

/* ── STAT CARDS ─────────────────────────────────── */
.stat-row {{
  display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
  gap:var(--s3); margin-bottom:var(--s5);
}}
.stat-card {{
  background:var(--surface); border:1px solid var(--border);
  border-radius:var(--radius); padding:var(--s4);
  transition:border-color .15s ease;
}}
.stat-card:hover {{ border-color:var(--border-strong); }}
.stat-value {{
  font-size:26px; font-weight:600; color:var(--text);
  letter-spacing:-0.02em; line-height:1.15;
}}
.stat-name {{
  font-size:13px; color:var(--muted); margin-top:2px;
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
}}
.stat-label {{
  font-size:10px; letter-spacing:0.12em; text-transform:uppercase;
  color:var(--faint); margin-top:var(--s2);
}}

/* ── LEADERBOARD ────────────────────────────────── */
.lb-row {{
  display:grid;
  grid-template-columns:30px minmax(0,1fr) 88px 88px 88px 76px;
  align-items:center; gap:var(--s3);
  padding:10px var(--s3);
  border-bottom:1px solid var(--border);
  transition:background .12s ease;
}}
.lb-row:hover {{ background:var(--surface); }}
.lb-rank {{
  font-size:12px; color:var(--faint); font-weight:500;
  display:flex; align-items:center; gap:5px;
}}
/* The top three carry a seamed ball; everyone else is a plain numeral.
   rank_cls() emits r1/r2/r3; medal() puts gold/silver/bronze on the row. */
.lb-rank.r1, .lb-rank.r2, .lb-rank.r3 {{ font-weight:600; }}
.lb-rank.r1 {{ color:var(--gold); }}
.lb-rank.r2 {{ color:var(--silver); }}
.lb-rank.r3 {{ color:var(--bronze); }}
.lb-rank.r1::before, .lb-rank.r2::before, .lb-rank.r3::before {{
  content:""; width:8px; height:8px; border-radius:50%; flex-shrink:0;
  background:currentColor;
  /* the ball's seam, cut through the middle */
  box-shadow:inset 0 2px 0 -1px var(--surface), inset 0 -2px 0 -1px var(--surface);
}}
.lb-row.gold {{ background:linear-gradient(90deg, var(--accent-soft), transparent 40%); }}
.lb-name {{
  display:flex; align-items:center; gap:var(--s2);
  font-size:14px; font-weight:500; color:var(--text);
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
}}
.lb-team {{
  display:flex; align-items:center; gap:5px;
  font-size:11px; color:var(--muted); margin-top:1px; font-weight:400;
}}
.lb-stat {{ text-align:right; font-size:13px; color:var(--muted); }}
.lb-score {{ text-align:right; font-size:14px; font-weight:600; color:var(--text); }}

/* The team colour reads as a quiet dot rather than tinted text. */
.team-dot {{
  width:7px; height:7px; border-radius:50%; flex-shrink:0;
  display:inline-block; position:relative;
  margin-right:7px; vertical-align:middle;
}}
/* Hairline across the middle — the ball's seam at 7px. */
.team-dot::after {{
  content:""; position:absolute; left:0; right:0; top:50%;
  height:1px; background:rgba(255,255,255,0.45); transform:translateY(-0.5px);
}}

/* ── PLAYER CARDS ───────────────────────────────── */
.player-grid {{
  display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:var(--s3);
}}
.player-card {{
  background:var(--surface); border:1px solid var(--border);
  border-radius:var(--radius); padding:var(--s4); margin-bottom:var(--s3);
}}
.player-rank {{ font-size:11px; color:var(--faint); font-weight:500; }}
.player-name {{
  display:flex; align-items:center; gap:var(--s2);
  font-size:15px; font-weight:600; color:var(--text); margin-top:var(--s1);
}}
.player-team {{ display:flex; align-items:center; gap:5px; font-size:11px; color:var(--muted); }}
.player-score {{
  font-size:24px; font-weight:600; color:var(--text);
  letter-spacing:-0.02em; margin:var(--s3) 0 var(--s2);
}}
.player-stats {{ font-size:12px; color:var(--muted); }}
.progress-wrap {{ margin-top:var(--s2); }}
.progress-label {{
  display:flex; justify-content:space-between;
  font-size:10px; letter-spacing:0.08em; text-transform:uppercase;
  color:var(--faint); margin-bottom:4px;
}}
.progress-bar {{
  height:3px; background:var(--surface-2); border-radius:100px; overflow:hidden;
}}
.progress-fill {{
  height:100%; border-radius:100px;
  background:var(--accent-mark);
}}

/* ── COMPARISON / BEST XI ───────────────────────── */
.h2h-card, .xi-card {{
  background:var(--surface); border:1px solid var(--border);
  border-radius:var(--radius); padding:var(--s4); margin-bottom:var(--s2);
}}
.h2h-name, .xi-name {{ font-size:14px; font-weight:500; color:var(--text); }}
.h2h-score, .xi-score {{ font-size:18px; font-weight:600; color:var(--text); }}
.xi-role {{
  font-size:10px; letter-spacing:0.12em; text-transform:uppercase; color:var(--faint);
}}
.vs-badge {{
  display:inline-flex; align-items:center; justify-content:center;
  width:34px; height:34px; border-radius:50%;
  background:var(--surface-2); border:1px solid var(--border);
  font-size:11px; font-weight:600; color:var(--muted);
}}
.team-badge {{
  display:inline-flex; align-items:center; gap:6px;
  padding:3px 9px; border-radius:100px;
  border:1px solid var(--border); background:var(--surface-2);
  font-size:11px; font-weight:600; color:var(--text);
}}
.mini-stat {{ text-align:center; padding:var(--s2); }}
.mini-val {{ font-size:17px; font-weight:600; color:var(--text); }}

/* ── LIVE SCORES ────────────────────────────────── */
@keyframes livepulse {{ 0%,100% {{opacity:1;}} 50% {{opacity:.25;}} }}
.live-hdr {{
  display:flex; align-items:center; gap:var(--s2);
  padding-bottom:var(--s3); margin-bottom:var(--s3);
  border-bottom:1px solid var(--border);
}}
.live-dot {{
  width:7px; height:7px; border-radius:50%; background:var(--negative);
  animation:livepulse 1.6s ease-in-out infinite; flex-shrink:0;
}}
.live-title {{
  font-size:11px; font-weight:600; letter-spacing:0.14em;
  text-transform:uppercase; color:var(--text);
}}
.live-src {{ font-size:11px; color:var(--faint); margin-left:auto; }}
.m-card, .m-card-ipl, .m-card-live {{
  background:var(--surface); border:1px solid var(--border);
  border-radius:var(--radius); margin-bottom:var(--s2); overflow:hidden;
}}
.m-card-ipl {{ border-left:2px solid var(--accent-mark); }}
.m-card-live {{ border-left:2px solid var(--negative); }}
.m-top {{
  display:flex; justify-content:space-between; align-items:center;
  padding:var(--s2) var(--s4); border-bottom:1px solid var(--border);
}}
.m-top-name {{ font-size:11px; color:var(--muted); }}
.m-body {{ padding:var(--s3) var(--s4); }}
.m-divider {{ height:1px; background:var(--border); margin:var(--s2) 0; }}
.t-row {{ display:flex; align-items:center; gap:var(--s2); margin-bottom:6px; }}
.t-icon {{
  width:26px; height:26px; border-radius:50%; flex-shrink:0;
  display:flex; align-items:center; justify-content:center;
  font-size:10px; font-weight:600; color:#fff;
}}
.t-name {{ font-size:13px; color:var(--text); }}
.t-score {{ margin-left:auto; font-size:14px; font-weight:600; color:var(--text); }}
.t-score-dim {{ margin-left:auto; font-size:14px; color:var(--faint); }}
.t-overs {{ font-size:11px; color:var(--faint); }}
.ipl-badge-s, .result-badge-s, .live-badge-s {{
  display:inline-block; padding:2px 8px; border-radius:100px;
  font-size:10px; font-weight:600; letter-spacing:0.05em;
  border:1px solid var(--border);
}}
.ipl-badge-s {{ background:var(--accent-soft); color:var(--accent); }}
.result-badge-s {{ background:var(--surface-2); color:var(--muted); }}
.live-badge-s {{ background:var(--surface-2); color:var(--negative); }}
.m-status-live {{ color:var(--negative); font-size:12px; }}
.m-status-won {{ color:var(--accent); font-size:12px; }}
.m-status-norm {{ color:var(--muted); font-size:12px; }}
.no-ipl-msg {{
  padding:var(--s5); text-align:center; color:var(--faint); font-size:13px;
  border:1px dashed var(--border); border-radius:var(--radius);
}}
.innings-hdr {{
  font-size:11px; font-weight:600; letter-spacing:0.1em; text-transform:uppercase;
  color:var(--muted); margin:var(--s3) 0 var(--s2);
}}
.sc-tbl {{ width:100%; border-collapse:collapse; font-size:12px; }}
.sc-tbl th {{
  text-align:left; font-size:10px; letter-spacing:0.1em; text-transform:uppercase;
  color:var(--faint); font-weight:600; padding:6px 8px;
  border-bottom:1px solid var(--border);
}}
.sc-tbl td {{ padding:6px 8px; border-bottom:1px solid var(--border); color:var(--muted); }}
.sc-hl {{ color:var(--text); font-weight:500; }}
.sc-total-row td {{ color:var(--text); font-weight:600; }}

/* ── STREAMLIT WIDGETS ──────────────────────────── */
[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
[data-testid="stNumberInput"] input,
[data-testid="stNumberInput"] div[data-baseweb="input"] {{
  background:var(--surface) !important; border:1px solid var(--border) !important;
  color:var(--text) !important; border-radius:var(--radius-sm) !important;
  font-size:13px !important;
}}
[data-baseweb="popover"] li {{
  background:var(--surface) !important; color:var(--text) !important; font-size:13px !important;
}}
[data-baseweb="popover"] li:hover {{ background:var(--surface-hover) !important; }}
/* Streamlit paints widget labels with its own config.toml textColor, which is
   the dark token and vanished on the light ground. Reclaim every one of them. */
label, .stMarkdown p {{ color:var(--muted); }}
[data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] *,
[data-testid="stSelectbox"] label, [data-testid="stSelectbox"] label *,
[data-testid="stNumberInput"] label, [data-testid="stNumberInput"] label *,
[data-testid="stRadio"] label, [data-testid="stRadio"] label * {{
  color:var(--muted) !important;
}}
[data-testid="stRadio"] div[role="radiogroup"] label * {{
  color:var(--text) !important; font-size:12px !important;
}}
[data-testid="stSelectbox"] label, [data-testid="stNumberInput"] label {{
  font-size:10px !important; letter-spacing:0.12em !important;
  text-transform:uppercase !important;
}}
.stButton > button {{
  background:var(--surface) !important; color:var(--text) !important;
  border:1px solid var(--border) !important; border-radius:var(--radius-sm) !important;
  font-size:12px !important; font-weight:500 !important; padding:6px 14px !important;
  box-shadow:none !important; transition:border-color .15s ease, background .15s ease;
}}
.stButton > button:hover {{
  border-color:var(--border-strong) !important; background:var(--surface-hover) !important;
}}
[data-testid="stDataFrame"] {{ border:1px solid var(--border); border-radius:var(--radius); }}
/* Plotly paints its modebar with Streamlit's primaryColor. Keep it neutral
   and quiet — it is chart chrome, not data. */
.modebar-btn, .modebar-btn.active, .modebar-btn:hover {{
  color:var(--faint) !important; fill:var(--faint) !important;
}}
.modebar {{ background:transparent !important; }}

/* The transient "Running..." chip also wears Streamlit's own text colour. */
[data-testid="stStatusWidget"], [data-testid="stStatusWidget"] * {{
  color:var(--muted) !important;
}}
hr {{ border-color:var(--border); }}
::-webkit-scrollbar {{ width:9px; height:9px; }}
::-webkit-scrollbar-track {{ background:transparent; }}
::-webkit-scrollbar-thumb {{ background:var(--border-strong); border-radius:100px; }}
</style>
"""
