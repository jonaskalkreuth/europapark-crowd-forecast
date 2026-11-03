"""Feature functions: each takes the open-day table and returns new columns."""

from datetime import timedelta

import pandas as pd

from europapark_crowd.open_days import summer_end

# In 2022–2025 the Halloween label always covers the 37 days ending on summer_end().
HALLOWEEN_DAYS = 37


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


def halloween(days: pd.DataFrame) -> pd.DataFrame:
    """Return 1 for days in the Halloween phase, else 0, from the date alone."""
    # The date rule, not the season label, because 2019 pages carry no label.
    last = days["date"].dt.year.map(summer_end)
    first = last - timedelta(days=HALLOWEEN_DAYS - 1)
    dates = days["date"].dt.date
    return pd.DataFrame(
        {"halloween": ((dates >= first) & (dates <= last)).astype(int)}, index=days.index
    )


FEATURES = [weekday, season_position, halloween]


def add_features(days: pd.DataFrame) -> pd.DataFrame:
    """Return the open-day table with the columns of every feature in FEATURES."""
    return pd.concat([days] + [feature(days) for feature in FEATURES], axis=1)
