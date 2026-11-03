import pandas as pd
import pytest

from europapark_crowd import features
from europapark_crowd.linear import linear_predictor


@pytest.fixture(autouse=True)
def weekday_only(monkeypatch):
    # These tests check the weekday pattern, so later features stay out.
    monkeypatch.setattr(features, "FEATURES", [features.weekday])


def two_weeks(saturday=90, other=30):
    # Monday 3 July 2023 to Sunday 16 July 2023; the crowd level is the nullable Int64 of the open-day table.
    dates = pd.date_range("2023-07-03", "2023-07-16")
    crowd = [saturday if d.day_of_week == 5 else other for d in dates]
    return pd.DataFrame({"date": dates, "crowd_level": pd.array(crowd, dtype="Int64")})


def test_learns_weekday_pattern():
    target = pd.DataFrame({"date": pd.date_range("2024-07-01", "2024-07-07")})
    predicted = linear_predictor(two_weeks(), target)
    saturday = predicted.iloc[5]
    others = predicted.drop(predicted.index[5])
    assert (others < saturday).all()
    assert others.round(6).nunique() == 1


def test_keeps_target_index_without_crowd_level():
    target = pd.DataFrame(
        {"date": pd.to_datetime(["2024-07-06", "2024-07-01"])}, index=[10, 20]
    )
    predicted = linear_predictor(two_weeks(), target)
    assert predicted.index.tolist() == [10, 20]
    assert predicted[10] > predicted[20]


def test_ridge_shrinks_towards_the_mean():
    target = pd.DataFrame({"date": pd.to_datetime(["2024-07-06"])})
    predicted = linear_predictor(two_weeks(), target)
    train_mean = (90 * 2 + 30 * 12) / 14
    assert train_mean < predicted.iloc[0] < 90
