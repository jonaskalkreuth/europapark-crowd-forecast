import pandas as pd

from europapark_crowd import windows


def season_days(start, end):
    """Build a season's open-day table with one row per day from start to end."""
    return pd.DataFrame({"date": pd.date_range(start, end)})


def holidays(rows):
    return pd.DataFrame(rows, columns=["window", "start", "end"]).astype(
        {"start": "datetime64[ns]", "end": "datetime64[ns]"}
    )


def test_loader_parses_dates(tmp_path):
    path = tmp_path / "windows.csv"
    path.write_text("window,start,end,source\nBW summer holidays,2024-07-25,2024-09-07,https://x\n")
    table = windows.load_windows(path)
    assert table["start"].iloc[0] == pd.Timestamp(2024, 7, 25)
    assert table["end"].iloc[0] == pd.Timestamp(2024, 9, 7)


def test_real_file_every_row_has_a_source_link():
    assert windows.load_windows()["source"].str.startswith("https://").all()


def test_real_file_ranges_run_forward():
    table = windows.load_windows()
    assert (table["start"] <= table["end"]).all()


def test_real_file_has_each_window_once_per_year_2023_to_2026():
    table = windows.load_windows()
    counts = table.groupby(["window", table["start"].dt.year]).size()
    assert (counts == 1).all()
    assert counts.unstack().notna().all().all()
    assert sorted(table["start"].dt.year.unique()) == [2023, 2024, 2025, 2026]


def test_real_file_ranges_stay_in_one_year():
    # season_windows matches a range to a season by date, so no range may span New Year.
    table = windows.load_windows()
    assert (table["start"].dt.year == table["end"].dt.year).all()


def test_holiday_range_includes_both_end_days():
    days = season_days("2024-07-01", "2024-07-31")
    found = windows.season_windows(days, holidays([("BW holidays", "2024-07-10", "2024-07-12")]))
    assert days["date"][found["BW holidays"]].dt.day.tolist() == [10, 11, 12]


def test_other_years_range_does_not_replace_this_season():
    days = season_days("2024-07-01", "2024-07-31")
    rows = [("BW holidays", "2024-07-10", "2024-07-12"), ("BW holidays", "2025-07-10", "2025-07-12")]
    found = windows.season_windows(days, holidays(rows))
    assert found["BW holidays"].sum() == 3


def test_range_outside_season_gives_no_window():
    days = season_days("2024-07-01", "2024-07-31")
    found = windows.season_windows(days, holidays([("BW holidays", "2025-07-10", "2025-07-12")]))
    assert "BW holidays" not in found


def test_calendar_seasons_split_by_month():
    days = season_days("2024-05-30", "2024-06-02")
    found = windows.season_windows(days, holidays([]))
    assert found["spring"].tolist() == [True, True, False, False]
    assert found["summer"].tolist() == [False, False, True, True]
    assert "autumn" not in found


def test_saturday_windows_hold_only_saturdays_of_their_month():
    # August 2024 has five Saturdays: 3, 10, 17, 24 and 31.
    days = season_days("2024-07-25", "2024-09-10")
    found = windows.season_windows(days, holidays([]))
    august = days["date"][found["Saturdays in August"]]
    assert august.dt.day.tolist() == [3, 10, 17, 24, 31]
    assert (august.dt.day_of_week == 5).all()


def test_window_with_one_day_is_dropped():
    # The season ends on Sunday 3 November 2024, so November has one Saturday.
    days = season_days("2024-10-12", "2024-11-03")
    found = windows.season_windows(days, holidays([("BW holidays", "2024-11-03", "2024-11-05")]))
    assert "Saturdays in November" not in found
    assert "BW holidays" not in found
    assert "Saturdays in October" in found
