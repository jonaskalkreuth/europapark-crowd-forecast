"""Feature functions: each takes the open-day table and returns new columns."""

import pandas as pd


def weekday(days: pd.DataFrame) -> pd.DataFrame:
    """Return the day of the week as an integer, Monday = 0."""
    return pd.DataFrame({"weekday": days["date"].dt.day_of_week}, index=days.index)


def season_position(days: pd.DataFrame) -> pd.DataFrame:
    """Return the week of the season (opening day in week 1) and calendar days since opening day."""
    opening_day = days.groupby("season")["date"].transform("min")
    # Calendar days, so a closure inside the season still counts.
    since = (days["date"] - opening_day).dt.days
    return pd.DataFrame(
        {"week_of_season": since // 7 + 1, "days_since_opening": since}, index=days.index
    )


FEATURES = [weekday, season_position]


def add_features(days: pd.DataFrame) -> pd.DataFrame:
    """Return the open-day table with the columns of every feature in FEATURES."""
    return pd.concat([days] + [feature(days) for feature in FEATURES], axis=1)
