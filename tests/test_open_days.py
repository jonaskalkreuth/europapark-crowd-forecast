from datetime import date

import pandas as pd

from europapark_crowd import open_days


def crowd_table(rows):
    """Build a small crowd table shaped like parse.load_crowd_table's output."""
    table = pd.DataFrame(rows, columns=["date", "crowd_level", "is_open", "season_label"])
    table["date"] = pd.to_datetime(table["date"])
    return table


def test_mid_july_is_summer():
    assert open_days.season_of(date(2023, 7, 15)) == "summer 2023"


def test_first_sunday_of_november_is_last_summer_day():
    assert open_days.summer_end(2023) == date(2023, 11, 5)
    assert open_days.season_of(date(2023, 11, 5)) == "summer 2023"


def test_day_after_summer_end_is_winter():
    # HALLOWinter starts here, so it lands in the winter season.
    assert open_days.season_of(date(2023, 11, 6)) == "winter 2023/24"


def test_january_belongs_to_previous_winter():
    assert open_days.season_of(date(2024, 1, 6)) == "winter 2023/24"


def test_days_before_2024_march_closure_are_summer_2024():
    # The park closed 18–22 March 2024; days on both sides stay in the same summer.
    assert open_days.season_of(date(2024, 3, 16)) == "summer 2024"
    assert open_days.season_of(date(2024, 3, 23)) == "summer 2024"


def test_closed_days_are_dropped(monkeypatch):
    table = crowd_table([
        ("2023-07-01", 57, True, "Summer Season"),
        ("2023-07-02", None, False, None),
    ])
    monkeypatch.setattr(open_days, "load_crowd_table", lambda raw_dir: table)
    days = open_days.load_open_days()
    assert list(days["date"]) == [pd.Timestamp("2023-07-01")]


def test_unlabelled_2019_day_gets_a_season(monkeypatch):
    table = crowd_table([("2019-07-01", 40, True, None)])
    monkeypatch.setattr(open_days, "load_crowd_table", lambda raw_dir: table)
    days = open_days.load_open_days()
    assert list(days["season"]) == ["summer 2019"]


def test_only_listed_summers_are_kept(monkeypatch):
    table = crowd_table([
        ("2023-07-01", 57, True, "Summer Season"),
        ("2023-11-20", 17, True, "HALLOWinter"),
        ("2026-07-01", 60, True, "Summer Season"),
    ])
    monkeypatch.setattr(open_days, "load_crowd_table", lambda raw_dir: table)
    days = open_days.load_open_days()
    assert list(days["season"]) == ["summer 2023"]
