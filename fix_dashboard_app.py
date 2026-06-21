from pathlib import Path


APP_PATH = Path(__file__).parent / "dashboard" / "app.py"

START_MARKER = "        def render_match(m, is_ipl=False):"
END_MARKER = "        # \u2500\u2500 Render based on filter \u2500\u2500"

REPLACEMENT = r'''        def html_escape(value):
            value = "" if value is None else str(value)
            return (
                value.replace("&", "&amp;")
                     .replace("<", "&lt;")
                     .replace(">", "&gt;")
            )

        def safe_match_title(value):
            safe = html_escape(value)
            title = safe.split(",")[0].strip()
            return title if title else "Match"

        def render_match(m, is_ipl=False):
            mid = m.get("id") or ""
            name = m.get("name") or ""
            status = m.get("status") or ""
            mtype = str(m.get("matchType") or "").upper()
            venue = m.get("venue") or ""
            date = m.get("date") or ""
            started = bool(m.get("matchStarted", False))
            ended = bool(m.get("matchEnded", False))
            teams = m.get("teams") or []
            scores = m.get("score") or []

            if not isinstance(teams, list):
                teams = []

            border_cls = "ipl-card" if is_ipl else ("live-now" if started and not ended else "")
            status_cls = "live-s" if started and not ended else ("won" if ended else "")

            score_map = {}
            for s in scores:
                inn = str(s.get("inning") or "")
                for t in teams:
                    team_name = str(t or "")
                    if team_name and team_name.lower() in inn.lower():
                        score_map[team_name] = (
                            s.get("r", "-"),
                            s.get("w", "-"),
                            s.get("o", "-")
                        )

            team_rows = []
            for i, t in enumerate(teams[:2]):
                t = str(t or "Team")
                safe_team = html_escape(t)
                bg, fg = team_color(t)
                abbr = html_escape(get_abbr(t))
                sc = score_map.get(t)

                if sc:
                    score_color = "#8b949e" if i == 1 and not ended else "#f0f6ff"
                    sc_html = (
                        f'<div class="t-score" style="color:{score_color};">'
                        f'{html_escape(sc[0])}/{html_escape(sc[1])}</div>'
                        f'<div class="t-overs">({html_escape(sc[2])} ov)</div>'
                    )
                else:
                    sc_html = '<div class="t-score" style="color:#8b949e;font-size:0.75rem;">Yet to bat</div>'

                team_rows.append(
                    f'<div class="t-row">'
                    f'<div class="t-icon" style="background:{bg};color:{fg};">{abbr}</div>'
                    f'<span class="t-name">{safe_team}</span>'
                    f'<div>{sc_html}</div>'
                    f'</div>'
                )

            batting_html = ""
            if started and not ended:
                batting_html = (
                    '<div class="now-batting">'
                    '<div class="nb-stat">'
                    '<div class="nb-name">Batting</div>'
                    '<div class="nb-val">Live</div>'
                    '<div class="nb-sub">CRR updating</div>'
                    '</div>'
                    '</div>'
                )

            card_title = safe_match_title(name)
            safe_status = html_escape(status) or "Status unavailable"
            safe_venue = html_escape(venue) or "Venue unavailable"
            safe_date = html_escape(date)
            safe_mtype = html_escape(mtype)

            ipl_badge = '<span class="ipl-badge">IPL 2026</span>' if is_ipl else ""
            live_badge = '<span class="live-badge">LIVE</span>' if started and not ended else ""
            result_badge = '<span class="result-badge">RESULT</span>' if ended else ""
            team_rows_html = "".join(team_rows)

            card_html = (
                f'<div class="m-card {border_cls}">'
                f'<div class="m-top">'
                f'<span class="m-top-name">📍 {safe_venue} · 📅 {safe_date}</span>'
                f'<div style="display:flex;gap:6px;align-items:center;">'
                f'<span style="font-size:0.65rem;color:#8b949e;">{safe_mtype}</span>'
                f'{ipl_badge}{live_badge}{result_badge}'
                f'</div>'
                f'</div>'
                f'<div class="m-body">'
                f'<div style="font-size:0.75rem;font-weight:600;color:#f0f6ff;margin-bottom:8px;">{card_title}</div>'
                f'{team_rows_html}'
                f'<div class="m-divider"></div>'
                f'<span class="m-status {status_cls}">{safe_status}</span>'
                f'{batting_html}'
                f'</div>'
                f'</div>'
            )

            st.markdown(card_html, unsafe_allow_html=True)

            with st.expander(f"📋 Full Scorecard — {card_title}", expanded=False):
                if not mid:
                    st.caption("Match ID not available")
                else:
                    sc_data = _fetch_scorecard(mid)
                    render_scorecard(sc_data)

'''


def main():
    text = APP_PATH.read_text(encoding="utf-8")
    start = text.find(START_MARKER)
    if start == -1:
        raise SystemExit(f"Could not find start marker: {START_MARKER!r}")

    end = text.find(END_MARKER, start)
    if end == -1:
        raise SystemExit(f"Could not find end marker after render_match: {END_MARKER!r}")

    fixed = text[:start] + REPLACEMENT + text[end:]
    APP_PATH.write_text(fixed, encoding="utf-8")
    print(f"Fixed {APP_PATH}")


if __name__ == "__main__":
    main()
