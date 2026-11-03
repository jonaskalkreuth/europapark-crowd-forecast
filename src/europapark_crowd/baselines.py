"""Baseline predictors: the bar every model must beat."""

import holidays
import pandas as pd

from europapark_crowd.evaluate import score
from europapark_crowd.open_days import load_open_days


def bw_holidays(years: list[int]) -> set:
    """Return the dates of Baden-Württemberg school and public holidays."""
    school = holidays.Germany(subdiv="BW", years=years, categories="school")
    public = holidays.Germany(subdiv="BW", years=years)
    return set(school) | set(public)


def savvy_visitor_predictor(train: pd.DataFrame, target: pd.DataFrame) -> pd.Series:
    """Predict 1 on weekends and BW holidays, 0 on every other open day."""
    dates = target["date"].dt
    holiday = dates.date.isin(bw_holidays(sorted(dates.year.unique())))
    busy = (dates.day_of_week >= 5) | holiday
    return busy.astype(float)


def _week_and_weekday(days: pd.DataFrame) -> pd.MultiIndex:
    dates = days["date"].dt
    return pd.MultiIndex.from_arrays([dates.isocalendar().week, dates.day_of_week])


def last_season_predictor(train: pd.DataFrame, target: pd.DataFrame) -> pd.Series:
    """Copy last season's crowd level on the day with the same ISO week and weekday."""
    last = train[train["season"] == train.sort_values("date")["season"].iloc[-1]]
    levels = pd.Series(last["crowd_level"].astype(float).values, index=_week_and_weekday(last))
    predicted = pd.Series(levels.reindex(_week_and_weekday(target)).values, index=target.index)
    # A day without a match takes last season's mean for its weekday.
    weekday_mean = last.groupby(last["date"].dt.day_of_week)["crowd_level"].mean().astype(float)
    return predicted.fillna(target["date"].dt.day_of_week.map(weekday_mean))


if __name__ == "__main__":
    days = load_open_days()
    for predictor in [savvy_visitor_predictor, last_season_predictor]:
        print(predictor.__name__)
        print(score(predictor, days).round(3))
