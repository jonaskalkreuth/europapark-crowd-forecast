import pandas as pd

from europapark_crowd import features


def test_weekday_on_known_dates():
    # Monday 3 July 2023 to Sunday 9 July 2023.
    days = pd.DataFrame({"date": pd.date_range("2023-07-03", "2023-07-09")})
    assert features.weekday(days)["weekday"].tolist() == [0, 1, 2, 3, 4, 5, 6]


def test_add_features_keeps_rows_and_adds_columns():
    # A non-default index checks that the new columns line up with their rows.
    days = pd.DataFrame(
        {"date": pd.to_datetime(["2023-07-08", "2023-07-03"])}, index=[10, 20]
    )
    result = features.add_features(days)
    assert len(result) == 2
    assert result["weekday"].tolist() == [5, 0]
