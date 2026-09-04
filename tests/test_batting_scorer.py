"""Batting metrics — ground truth in tests/conftest.py."""

from analytics.batting.batting_scorer import calculate_batting_scores
from ingestion.data_loader import load_all_matches


def _batter(match_folder, name="A Batter"):
    df = load_all_matches(match_folder)
    batting = calculate_batting_scores(df)
    return batting[batting["striker"] == name].iloc[0]


def test_dismissals_counts_wickets_not_balls_faced(match_folder):
    """The '\"\"' bug made dismissals equal the number of deliveries."""
    assert _batter(match_folder)["dismissals"] == 2


def test_balls_faced_excludes_wides(match_folder):
    assert _batter(match_folder)["balls_faced"] == 14


def test_average_is_runs_per_dismissal(match_folder):
    row = _batter(match_folder)

    assert row["total_runs"] == 28
    assert row["average"] == 14.0


def test_average_is_not_just_strike_rate_over_one_hundred(match_folder):
    """The signature of the old bug: average == strike_rate / 100."""
    row = _batter(match_folder)

    assert row["strike_rate"] == 200.0
    assert abs(row["average"] - row["strike_rate"] / 100) > 1


def test_a_batter_who_is_never_out_averages_their_run_total(two_match_folder):
    """Guard the divide-by-zero branch. D Finisher is never dismissed."""
    row = _batter(two_match_folder, "D Finisher")

    assert row["dismissals"] == 0
    assert row["average"] == row["total_runs"] == 90


def _finisher(two_match_folder):
    df = load_all_matches(two_match_folder)
    batting = calculate_batting_scores(df)
    return batting[batting["striker"] == "D Finisher"].iloc[0]


def test_powerplay_is_overs_zero_to_five(two_match_folder):
    """'ball <= 6.6' swept over 6 into the powerplay as well."""
    assert _finisher(two_match_folder)["powerplay_runs"] == 6


def test_death_is_overs_sixteen_onwards(two_match_folder):
    row = _finisher(two_match_folder)

    assert row["death_runs"] == 54, "overs 16 and 17 only, never over 15"


def test_phase_runs_never_exceed_total_runs(two_match_folder):
    row = _finisher(two_match_folder)

    assert row["total_runs"] == 90
    assert row["powerplay_runs"] + row["death_runs"] <= row["total_runs"]
