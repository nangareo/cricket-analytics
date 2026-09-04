"""Fielding metrics — catches belong to the fielder, not the bowler."""

from analytics.fielding.fielding_scorer import calculate_fielding_scores
from ingestion.data_loader import load_all_matches


def _fielding(match_folder):
    df = load_all_matches(match_folder)
    return calculate_fielding_scores(df).set_index("player")


def test_catch_is_credited_to_the_fielder(match_folder):
    """The old code grouped by 'bowler', so it credited the wrong player."""
    fielding = _fielding(match_folder)

    assert fielding.loc["F Fielder", "catches"] == 1


def test_bowler_is_not_credited_with_the_catch(match_folder):
    fielding = _fielding(match_folder)

    assert fielding.loc["C Bowler", "catches"] == 0


def test_run_out_is_credited_to_the_fielder(match_folder):
    fielding = _fielding(match_folder)

    assert fielding.loc["F Fielder", "run_outs"] == 1


def test_bowled_wicket_stays_with_the_bowler(two_match_folder):
    """'bowled' is the one credit that genuinely belongs to the bowler."""
    df = load_all_matches(two_match_folder)
    fielding = calculate_fielding_scores(df).set_index("player")

    assert fielding.loc["C Bowler", "bowled_wickets"] == 0


def test_match_count_includes_players_who_only_fielded(match_folder):
    """Counting matches off 'striker' alone left pure bowlers/fielders at 0."""
    fielding = _fielding(match_folder)

    assert fielding.loc["F Fielder", "matches"] == 1
    assert fielding.loc["C Bowler", "matches"] == 1


def test_match_count_is_a_whole_number(match_folder):
    fielding = _fielding(match_folder)

    assert fielding["matches"].dtype.kind in "iu"
