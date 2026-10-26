"""Feature functions: each takes the open-day table and returns new columns."""

import pandas as pd


def weekday(days: pd.DataFrame) -> pd.DataFrame:
    """Return the day of the week as an integer, Monday = 0."""
    return pd.DataFrame({"weekday": days["date"].dt.day_of_week}, index=days.index)


FEATURES = [weekday]


def add_features(days: pd.DataFrame) -> pd.DataFrame:
    """Return the open-day table with the columns of every feature in FEATURES."""
    return pd.concat([days] + [feature(days) for feature in FEATURES], axis=1)
