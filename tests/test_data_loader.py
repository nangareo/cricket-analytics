"""Parser-level tests — the csv2 reader is the root of every scoring number."""

import pandas as pd

from ingestion.data_loader import load_all_matches


def test_no_wicket_rows_are_null_not_the_literal_quote_string(match_folder):
    """csv2 writes '""' when nobody is out; it must land as NA, not a string."""
    df = load_all_matches(match_folder)

    no_wicket = df[df["player_dismissed"].isna()]

    assert len(no_wicket) == 13, "13 of 15 deliveries produced no dismissal"
    assert not (df["wicket_type"] == '""').any(), "raw '\"\"' token leaked through"


def test_dismissal_rows_keep_their_wicket_type(match_folder):
    df = load_all_matches(match_folder)

    wickets = df[df["wicket_type"].notna()]

    assert sorted(wickets["wicket_type"]) == ["caught", "run out"]
    assert set(wickets["player_dismissed"]) == {"A Batter"}


def test_fielder_is_extracted_from_the_catch(match_folder):
    df = load_all_matches(match_folder)

    caught = df[df["wicket_type"] == "caught"].iloc[0]

    assert caught["fielder_1"] == "F Fielder"


def test_ball_column_is_the_true_over_ball_not_the_delivery_counter(match_folder):
    """Over 1 has a wide, so it holds 7 deliveries but only 6 legal ball numbers."""
    df = load_all_matches(match_folder)

    over_one = df[df["over"] == 1]

    assert len(over_one) == 7, "7 deliveries were bowled in over 1"
    assert sorted(over_one["ball"].round(1).unique()) == [1.1, 1.2, 1.3, 1.4, 1.5, 1.6]


def test_over_column_is_available_for_phase_filters(match_folder):
    df = load_all_matches(match_folder)

    assert sorted(df["over"].unique()) == [0, 1, 2]
    assert df["over"].dtype.kind in "iu", "over should be a whole number"


def test_wide_delivery_is_not_a_legal_ball(match_folder):
    df = load_all_matches(match_folder)

    assert len(df) == 15, "15 deliveries in the fixture"
    assert df["is_legal_ball"].sum() == 14, "one of them was a wide"


def test_parser_does_not_invent_phantom_columns(match_folder):
    """BALL_COLUMNS used to declare 23 names for 21 fields."""
    df = load_all_matches(match_folder)

    assert "extra_4" not in df.columns
    assert "other_wicket_type" not in df.columns


def test_quoted_field_containing_a_comma_is_not_split(tmp_path):
    """A naive line.split(',') would tear this row apart."""
    from tests.conftest import ball_row, write_match

    folder = tmp_path / "raw"
    folder.mkdir()
    write_match(
        str(folder),
        "9000003",
        [ball_row(batting_team='"Team, With Comma"', runs_batter=1)],
    )

    df = load_all_matches(str(folder))

    assert df.iloc[0]["batting_team"] == "Team, With Comma"
    assert df.iloc[0]["runs_off_bat"] == 1


def test_runs_columns_are_numeric(match_folder):
    df = load_all_matches(match_folder)

    assert pd.api.types.is_numeric_dtype(df["runs_off_bat"])
    assert pd.api.types.is_numeric_dtype(df["wides"])
    assert df["runs_off_bat"].sum() == 28
    assert df["wides"].sum() == 5


def test_season_is_attached_to_every_ball(match_folder):
    """The Season Trends tab groups on this column."""
    df = load_all_matches(match_folder)

    assert set(df["season"].unique()) == {2026}


def test_season_comes_from_the_match_date_not_the_season_label(tmp_path):
    """
    Cricsheet labels IPL 2020 as season '2020/21' because it straddles the
    cricket year, but it was played in 2020. Taking the later half of the
    label would file the whole season under the wrong year.
    """
    from tests.conftest import ball_row, write_match

    folder = tmp_path / "raw"
    folder.mkdir()
    write_match(
        str(folder), "9000004", [ball_row(runs_batter=1)],
        season="2020/21", date="2020/09/19",
    )

    df = load_all_matches(str(folder))

    assert df["season"].iloc[0] == 2020


def test_season_is_a_whole_number(match_folder):
    df = load_all_matches(match_folder)

    assert df["season"].dtype.kind in "iu"
