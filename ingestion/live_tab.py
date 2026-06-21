"""
Live Scores Tab Code — add to dashboard_main.py
This is the content of tab9 (LIVE SCORES)
"""

LIVE_TAB_CODE = '''
# ── TAB 9 — LIVE SCORES ───────────────────────────────
with tab9:
    import urllib.request, json, time

    API_KEY = "c83bbc46-e3c7-4a77-8b28-a9e4d7785183"

    st.markdown("""
    <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1.5rem;">
        <div style="width:12px;height:12px;background:#ff4444;border-radius:50%;
                    box-shadow:0 0 10px #ff4444;animation:pulse 1s infinite;"></div>
        <div class="section-title" style="margin:0;border:none;">LIVE CRICKET SCORES</div>
    </div>
    <style>
    @keyframes pulse {
        0%,100%{opacity:1;transform:scale(1);}
        50%{opacity:0.5;transform:scale(1.3);}
    }
    </style>
    """, unsafe_allow_html=True)

    # Auto refresh toggle
    col_r1, col_r2, col_r3 = st.columns([2,1,1])
    with col_r1:
        st.markdown("<div style='color:var(--muted);font-size:0.8rem;'>Data from CricketData.org — updates every 60s</div>",
                    unsafe_allow_html=True)
    with col_r2:
        auto_refresh = st.toggle("Auto Refresh", value=False)
    with col_r3:
        manual_refresh = st.button("🔄 Refresh Now")

    if auto_refresh:
        time.sleep(60)
        st.rerun()

    # Fetch matches
    @st.cache_data(ttl=60)
    def fetch_live_matches():
        url = f"https://api.cricapi.com/v1/currentMatches?apikey={API_KEY}&offset=0"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read())
                if data.get("status") == "success":
                    return data.get("data", []), None
                return [], data.get("reason", "Unknown error")
        except Exception as e:
            return [], str(e)

    if manual_refresh:
        st.cache_data.clear()

    matches, error = fetch_live_matches()

    if error:
        st.error(f"⚠️ Could not fetch live scores: {error}")
    elif not matches:
        st.markdown("""
        <div style="text-align:center;padding:3rem;background:rgba(22,27,34,0.8);
                    border-radius:16px;border:1px solid rgba(255,255,255,0.06);">
            <div style="font-size:3rem;">🏏</div>
            <div style="font-family:'Rajdhani',sans-serif;font-size:1.5rem;color:#f0f6ff;margin:1rem 0;">
                No Live Matches Right Now
            </div>
            <div style="color:#8b949e;font-size:0.9rem;">
                Check back during IPL match hours (typically 3:30 PM & 7:30 PM IST)
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Show match count
        live = [m for m in matches if m.get("matchStarted") and not m.get("matchEnded")]
        upcoming = [m for m in matches if not m.get("matchStarted")]
        completed = [m for m in matches if m.get("matchEnded")]

        # Stats strip
        st.markdown(f"""
        <div style="display:flex;gap:1rem;margin-bottom:1.5rem;">
            <div class="stat-card" style="flex:1;padding:1rem;">
                <div class="stat-value" style="color:#ff4444;">{len(live)}</div>
                <div class="stat-label">🔴 Live Now</div>
            </div>
            <div class="stat-card" style="flex:1;padding:1rem;">
                <div class="stat-value" style="color:#ffd700;">{len(upcoming)}</div>
                <div class="stat-label">⏳ Upcoming</div>
            </div>
            <div class="stat-card" style="flex:1;padding:1rem;">
                <div class="stat-value" style="color:#1db954;">{len(completed)}</div>
                <div class="stat-label">✅ Completed</div>
            </div>
            <div class="stat-card" style="flex:1;padding:1rem;">
                <div class="stat-value">{len(matches)}</div>
                <div class="stat-label">📋 Total</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Filter tabs
        filter_opt = st.radio("Show:", ["🔴 Live", "⏳ Upcoming", "✅ Completed", "📋 All"],
                               horizontal=True)

        if filter_opt == "🔴 Live":       show = live
        elif filter_opt == "⏳ Upcoming": show = upcoming
        elif filter_opt == "✅ Completed": show = completed
        else:                              show = matches

        if not show:
            st.info(f"No matches in this category right now.")
        else:
            for match in show:
                name     = match.get("name", "Unknown Match")
                status   = match.get("status", "")
                match_type = match.get("matchType", "").upper()
                venue    = match.get("venue", "")
                date     = match.get("date", "")
                teams    = match.get("teams", [])
                score    = match.get("score", [])
                started  = match.get("matchStarted", False)
                ended    = match.get("matchEnded", False)

                # Color indicator
                if started and not ended:
                    indicator = '<span style="display:inline-block;width:10px;height:10px;background:#ff4444;border-radius:50%;margin-right:8px;box-shadow:0 0 8px #ff4444;"></span>'
                    border_color = "rgba(255,68,68,0.4)"
                elif ended:
                    indicator = '<span style="display:inline-block;width:10px;height:10px;background:#1db954;border-radius:50%;margin-right:8px;"></span>'
                    border_color = "rgba(29,185,84,0.3)"
                else:
                    indicator = '<span style="display:inline-block;width:10px;height:10px;background:#ffd700;border-radius:50%;margin-right:8px;"></span>'
                    border_color = "rgba(255,215,0,0.3)"

                # Format scores
                score_html = ""
                if score:
                    for s in score:
                        inning = s.get("inning", "")
                        runs   = s.get("r", "-")
                        wkts   = s.get("w", "-")
                        overs  = s.get("o", "-")
                        score_html += f"""
                        <div style="display:flex;justify-content:space-between;
                                    padding:0.4rem 0;border-bottom:1px solid rgba(255,255,255,0.04);">
                            <span style="color:#8b949e;font-size:0.8rem;">{inning}</span>
                            <span style="font-family:'Rajdhani',sans-serif;font-size:1.1rem;
                                         font-weight:700;color:#f0f6ff;">{runs}/{wkts}
                                <span style="font-size:0.8rem;color:#8b949e;">({overs} ov)</span>
                            </span>
                        </div>"""

                st.markdown(f"""
                <div style="background:rgba(22,27,34,0.9);border:1px solid {border_color};
                            border-radius:16px;padding:1.2rem 1.5rem;margin-bottom:1rem;
                            box-shadow:0 4px 20px rgba(0,0,0,0.3);">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.8rem;">
                        <div>
                            <div style="font-family:'Rajdhani',sans-serif;font-size:1.15rem;
                                        font-weight:700;color:#f0f6ff;">
                                {indicator}{name}
                            </div>
                            <div style="font-size:0.75rem;color:#8b949e;margin-top:0.2rem;">
                                📍 {venue} &nbsp;•&nbsp; 📅 {date}
                            </div>
                        </div>
                        <div style="background:rgba(29,185,84,0.15);color:#1db954;
                                    font-size:0.7rem;font-weight:700;letter-spacing:1px;
                                    padding:3px 10px;border-radius:20px;border:1px solid rgba(29,185,84,0.3);">
                            {match_type}
                        </div>
                    </div>
                    {score_html if score_html else ""}
                    <div style="margin-top:0.8rem;padding:0.5rem 0.8rem;
                                background:rgba(255,255,255,0.03);border-radius:8px;
                                font-size:0.8rem;color:#8b949e;">
                        {status}
                    </div>
                </div>
                """, unsafe_allow_html=True)
'''

print(LIVE_TAB_CODE[:100], "...")
print("Lines:", len(LIVE_TAB_CODE.split("\\n")))
