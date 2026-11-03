import pandas as pd

from europapark_crowd import features


def test_weekday_on_known_dates():
    # Monday 3 July 2023 to Sunday 9 July 2023.
    days = pd.DataFrame({"date": pd.date_range("2023-07-03", "2023-07-09")})
    assert features.weekday(days)["weekday"].tolist() == [0, 1, 2, 3, 4, 5, 6]


def test_add_features_keeps_rows_and_adds_columns():
    # A non-default index checks that the new columns line up with their rows.
    days = pd.DataFrame(
        {"date": pd.to_datetime(["2023-07-08", "2023-07-03"]), "season": "summer 2023"},
        index=[10, 20],
    )
    result = features.add_features(days)
    assert len(result) == 2
    assert result["weekday"].tolist() == [5, 0]
    assert result["days_since_opening"].tolist() == [5, 0]


def season(dates, label="summer 2024"):
    return pd.DataFrame({"date": pd.to_datetime(dates), "season": label})


def test_season_position_counts_from_opening_day():
    # Opening day is Saturday 16 March 2024; day 6 ends week 1 and day 7 starts week 2.
    days = season(["2024-03-16", "2024-03-22", "2024-03-23"])
    result = features.season_position(days)
    assert result["days_since_opening"].tolist() == [0, 6, 7]
    assert result["week_of_season"].tolist() == [1, 1, 2]


def test_season_position_counts_closed_days():
    # The park closed 18 to 22 March 2024, so the 23rd is still day 7.
    days = season(["2024-03-16", "2024-03-17", "2024-03-23"])
    assert features.season_position(days)["days_since_opening"].tolist() == [0, 1, 7]


def test_season_position_restarts_each_season():
    days = pd.concat(
        [season(["2023-03-25", "2023-04-01"], "summer 2023"), season(["2024-03-16", "2024-03-30"])],
        ignore_index=True,
    )
    result = features.season_position(days)
    assert result["days_since_opening"].tolist() == [0, 7, 0, 14]
    assert result["week_of_season"].tolist() == [1, 2, 1, 3]


def test_season_position_keeps_an_unsorted_index():
    days = season(["2024-03-30", "2024-03-16"])
    days.index = [10, 20]
    result = features.season_position(days)
    assert result.index.tolist() == [10, 20]
    assert result["days_since_opening"].tolist() == [14, 0]
