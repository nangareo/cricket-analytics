
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
