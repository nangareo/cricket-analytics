"""
Shared fixtures — builds tiny synthetic Cricsheet csv2 match files so the
scorers can be tested against known ground truth instead of the 1244-file
production dataset.

Real csv2 ball rows carry 21 fields. Layout confirmed against data/raw:

    0  "ball"            11 byes
    1  innings           12 legbyes
    2  delivery          13 penalty
    3  batting_team      14 wicket_type       ("" when no wicket)
    4  batter            15 player_dismissed  ("" when no wicket)
    5  non_striker       16 ball  <- true over.legal_ball
    6  bowler            17 non_boundary
    7  runs_batter       18 fielder_1
    8  runs_extras       19 fielder_2
    9  wides             20 (unused, always empty)
    10 noballs

Field 2 (delivery) is a raw per-over counter that keeps climbing through
extras (0.7, 0.8, ...). Field 16 is the real over.ball and repeats when a
delivery is re-bowled. Phase filters must use field 16, never field 2.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

NO_WICKET = '""'  # csv2 writes a quoted empty string when nobody is out


def ball_row(
    innings=1,
    delivery="0.1",
    batting_team="Test XI",
    batter="A Batter",
    non_striker="B Batter",
    bowler="C Bowler",
    runs_batter=0,
    runs_extras=0,
    wides="",
    noballs="",
    byes="",
    legbyes="",
    penalty="",
    wicket_type=NO_WICKET,
    player_dismissed=NO_WICKET,
    ball=None,
    non_boundary="",
    fielder_1="",
    fielder_2="",
):
    """Render one csv2 'ball' line exactly as Cricsheet writes it."""
    return ",".join(
        str(v)
        for v in [
            "ball", innings, delivery, batting_team, batter, non_striker,
            bowler, runs_batter, runs_extras, wides, noballs, byes, legbyes,
            penalty, wicket_type, player_dismissed,
            ball if ball is not None else delivery,
            non_boundary, fielder_1, fielder_2, "",
        ]
    )


def write_match(folder, match_id, ball_rows, season="2026", date="2026/04/01",
                teams=("Test XI", "Rival XI")):
    path = os.path.join(folder, f"{match_id}.csv")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("version,1.8.0\n")
        fh.write("info,balls_per_over,6\n")
        fh.write(f"info,season,{season}\n")
        fh.write(f"info,date,{date}\n")
        for team in teams:
            fh.write(f"info,team,{team}\n")
        fh.write(f"info,match_id,{match_id}\n")
        for row in ball_rows:
            fh.write(row + "\n")
    return path


def _one_match_rows():
    """
    Hand-checked ground truth for match 9000001.

    A Batter   28 runs off 14 legal balls, out twice
               -> average 14.0, strike rate 200.0
               (a 15th delivery is a wide: conceded, but not a ball faced)
    C Bowler   14 legal balls, concedes 28 off the bat + 5 wide runs = 33
               -> 1 bowling wicket (the catch; the run out is not his)
               -> bowling strike rate 14.0 balls per wicket
    F Fielder  1 catch, 1 run out
    """
    rows = []

    # Over 0 — six legal balls, 4 runs each = 24.
    for i in range(1, 7):
        rows.append(ball_row(delivery=f"0.{i}", ball=f"0.{i}", runs_batter=4))

    # Over 1, first delivery is a wide worth 5. Not a ball faced.
    rows.append(ball_row(delivery="1.1", ball="1.1", runs_extras=5, wides=5))
    # Then six legal balls; the re-bowl is still legal ball 1.1.
    for i in range(1, 7):
        rows.append(
            ball_row(
                delivery=f"1.{i + 1}",
                ball=f"1.{i}",
                runs_batter=4 if i == 1 else 0,
            )
        )

    # Over 2 — the two dismissals, no runs.
    rows.append(
        ball_row(
            delivery="2.1", ball="2.1",
            wicket_type="caught", player_dismissed="A Batter",
            fielder_1="F Fielder",
        )
    )
    rows.append(
        ball_row(
            delivery="2.2", ball="2.2",
            wicket_type="run out", player_dismissed="A Batter",
            fielder_1="F Fielder",
        )
    )
    return rows


def _phase_rows():
    """
    A second match that straddles every phase boundary.

    D Finisher scores a different amount in each over so a mis-scoped filter
    shows up as a specific wrong number rather than a vague one:

        over  5  ->  6 runs   powerplay (overs 0-5)
        over  6  -> 12 runs   middle    (must NOT count as powerplay)
        over 15  -> 18 runs   middle    (must NOT count as death)
        over 16  -> 24 runs   death     (overs 16-19)
        over 17  -> 30 runs   death

    powerplay_runs = 6, death_runs = 54, total = 90 off 30 balls.
    E Yorker concedes 54 off 12 balls at the death -> economy 27.0.
    """
    per_over = {5: 1, 6: 2, 15: 3, 16: 4, 17: 5}
    rows = []
    for over, runs in per_over.items():
        for i in range(1, 7):
            rows.append(
                ball_row(
                    delivery=f"{over}.{i}", ball=f"{over}.{i}",
                    batter="D Finisher", bowler="E Yorker", runs_batter=runs,
                )
            )
    return rows


@pytest.fixture
def match_folder(tmp_path):
    """Folder holding the single ground-truth match."""
    folder = tmp_path / "raw"
    folder.mkdir()
    write_match(str(folder), "9000001", _one_match_rows())
    return str(folder)


@pytest.fixture
def two_match_folder(tmp_path):
    """Ground-truth match plus a match spanning every phase boundary."""
    folder = tmp_path / "raw"
    folder.mkdir()
    write_match(str(folder), "9000001", _one_match_rows())
    write_match(str(folder), "9000002", _phase_rows())
    return str(folder)
