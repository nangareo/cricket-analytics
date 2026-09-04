"""Bowling metrics — ground truth in tests/conftest.py."""

from analytics.bowling.bowling_scorer import calculate_bowling_scores
from ingestion.data_loader import load_all_matches


def _bowler(match_folder, name="C Bowler"):
    df = load_all_matches(match_folder)
    bowling = calculate_bowling_scores(df)
    return bowling[bowling["bowler"] == name].iloc[0]


def test_wickets_counts_dismissals_not_balls(match_folder):
    """The '\"\"' bug made wickets equal the number of deliveries bowled."""
    assert _bowler(match_folder)["wickets"] == 1


def test_run_out_is_not_credited_to_the_bowler(match_folder):
    """Two dismissals happened, but only the catch belongs to the bowler."""
    row = _bowler(match_folder)

    assert row["wickets"] == 1, "the run out must not count"


def test_balls_bowled_excludes_the_wide(match_folder):
    assert _bowler(match_folder)["balls_bowled"] == 14


def test_runs_conceded_counts_extra_runs_not_extra_deliveries(match_folder):
    """A 5-run wide adds 5, not 1. The old code summed delivery counts."""
    assert _bowler(match_folder)["total_runs_given"] == 33


def test_economy_is_runs_per_over(match_folder):
    row = _bowler(match_folder)

    assert round(row["economy"], 2) == round(33 / 14 * 6, 2)


def test_bowling_strike_rate_is_balls_per_wicket(match_folder):
    """Every bowler used to come out at exactly 1.0."""
    row = _bowler(match_folder)

    assert row["bowling_sr"] == 14.0


def test_bowling_average_is_runs_per_wicket(match_folder):
    assert _bowler(match_folder)["bowling_average"] == 33.0


def test_death_economy_counts_only_overs_sixteen_onwards(two_match_folder):
    df = load_all_matches(two_match_folder)
    bowling = calculate_bowling_scores(df)
    row = bowling[bowling["bowler"] == "E Yorker"].iloc[0]

    assert row["death_economy"] == 27.0, "54 runs off 12 balls in overs 16-17"


def test_wicketless_bowler_keeps_a_finite_strike_rate(two_match_folder):
    """E Yorker never took a wicket — must not produce NaN or crash."""
    df = load_all_matches(two_match_folder)
    bowling = calculate_bowling_scores(df)
    row = bowling[bowling["bowler"] == "E Yorker"].iloc[0]

    assert row["wickets"] == 0
    assert row["bowling_sr"] == 999
