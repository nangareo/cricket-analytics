"""Team attribution — derived from the data, not a hand-maintained dict."""

from ingestion.data_loader import (
    CURRENT_TEAM_NAME, add_bowling_team, load_all_matches, resolve_player_teams,
)
from tests.conftest import ball_row, write_match


def test_batter_is_attributed_to_the_batting_side(match_folder):
    teams = resolve_player_teams(load_all_matches(match_folder))

    assert teams["A Batter"] == "Test XI"


def _two_sided_match(tmp_path):
    """Alpha bats, Beta bowls and takes the catch."""
    folder = tmp_path / "raw"
    folder.mkdir()
    write_match(
        str(folder), "9100005",
        [
            ball_row(batting_team="Alpha XI", batter="A Batter",
                     non_striker="A Partner", bowler="B Bowler"),
            ball_row(batting_team="Alpha XI", batter="A Batter",
                     non_striker="A Partner", bowler="B Bowler",
                     wicket_type="caught", player_dismissed="A Batter",
                     fielder_1="B Fielder"),
        ],
        teams=("Alpha XI", "Beta XI"),
    )
    return str(folder)


def test_bowler_is_attributed_to_the_fielding_side(tmp_path):
    """
    The bowler belongs to the side that is not batting. Reading batting_team
    off a bowler's delivery would put him on the opposition.
    """
    teams = resolve_player_teams(load_all_matches(_two_sided_match(tmp_path)))

    assert teams["B Bowler"] == "Beta XI"
    assert teams["A Batter"] == "Alpha XI"


def test_fielder_is_attributed_to_the_fielding_side(tmp_path):
    teams = resolve_player_teams(load_all_matches(_two_sided_match(tmp_path)))

    assert teams["B Fielder"] == "Beta XI"


def test_fielding_side_resolves_when_the_match_was_abandoned(tmp_path):
    """
    Only one team ever bats in an abandoned match, so the opposition has to
    come from the info block rather than from batting_team.
    """
    folder = tmp_path / "raw"
    folder.mkdir()
    write_match(
        str(folder), "9100006",
        [ball_row(batting_team="Alpha XI", batter="A1", bowler="Lone Bowler")],
        teams=("Alpha XI", "Beta XI"),
    )

    teams = resolve_player_teams(load_all_matches(str(folder)))

    assert teams["Lone Bowler"] == "Beta XI"


def test_bowling_team_is_the_other_side_in_the_match(tmp_path):
    folder = tmp_path / "raw"
    folder.mkdir()
    write_match(
        str(folder), "9100001",
        [
            ball_row(innings=1, batting_team="Alpha XI", batter="A1", bowler="B1"),
            ball_row(innings=2, batting_team="Beta XI", batter="B2", bowler="A2"),
        ],
        teams=("Alpha XI", "Beta XI"),
    )

    df = add_bowling_team(load_all_matches(str(folder)))

    first, second = df.iloc[0], df.iloc[1]
    assert first["batting_team"] == "Alpha XI"
    assert first["bowling_team"] == "Beta XI"
    assert second["bowling_team"] == "Alpha XI"


def test_player_is_placed_with_their_most_recent_team(tmp_path):
    """A player who moves franchise should show their current side."""
    folder = tmp_path / "raw"
    folder.mkdir()
    write_match(
        str(folder), "9100002",
        [ball_row(batting_team="Alpha XI", batter="Mover", bowler="X")],
        season="2019", date="2019/04/01", teams=("Alpha XI", "Beta XI"),
    )
    write_match(
        str(folder), "9100003",
        [ball_row(batting_team="Beta XI", batter="Mover", bowler="Y")],
        season="2026", date="2026/04/01", teams=("Alpha XI", "Beta XI"),
    )

    teams = resolve_player_teams(load_all_matches(str(folder)))

    assert teams["Mover"] == "Beta XI"


def test_legacy_franchise_names_map_to_the_current_one():
    assert CURRENT_TEAM_NAME["Royal Challengers Bangalore"] == "Royal Challengers Bengaluru"
    assert CURRENT_TEAM_NAME["Kings XI Punjab"] == "Punjab Kings"
    assert CURRENT_TEAM_NAME["Delhi Daredevils"] == "Delhi Capitals"


def test_renamed_franchise_is_reported_under_its_current_name(tmp_path):
    folder = tmp_path / "raw"
    folder.mkdir()
    write_match(
        str(folder), "9100004",
        [ball_row(batting_team="Kings XI Punjab", batter="Old Timer", bowler="Z")],
        season="2019", date="2019/04/01",
        teams=("Kings XI Punjab", "Delhi Daredevils"),
    )

    teams = resolve_player_teams(load_all_matches(str(folder)))

    assert teams["Old Timer"] == "Punjab Kings"


def test_every_player_in_the_real_data_resolves_to_a_team():
    """186 players used to render as 'Unknown' on the dashboard."""
    df = load_all_matches("data/raw")
    teams = resolve_player_teams(df)

    named = set(df["striker"].dropna()) | set(df["bowler"].dropna())
    unresolved = {p for p in named if not teams.get(p)}

    assert unresolved == set()


def test_suryavanshi_is_a_rajasthan_royal():
    df = load_all_matches("data/raw")
    teams = resolve_player_teams(df)

    assert teams["V Suryavanshi"] == "Rajasthan Royals"
