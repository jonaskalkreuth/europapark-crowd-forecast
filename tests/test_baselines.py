from datetime import date

import pandas as pd

from europapark_crowd import baselines


def make_days(dates, crowd_levels=None, season=None):
    days = pd.DataFrame({"date": pd.to_datetime(dates)})
    if crowd_levels is not None:
        days["crowd_level"] = pd.array(crowd_levels, dtype="Int64")
    if season is not None:
        days["season"] = season
    return days


def test_savvy_weekend_busy_plain_weekday_quiet():
    # Sat 15 and Sun 16 June 2024 are busy; Tue 18 June 2024 is no BW holiday.
    target = make_days(["2024-06-15", "2024-06-16", "2024-06-18"])
    assert baselines.savvy_visitor_predictor(None, target).tolist() == [1, 1, 0]


def test_savvy_bw_public_holiday_busy():
    # Corpus Christi is a public holiday in BW but not in every German state.
    target = make_days(["2024-05-30"])
    assert baselines.savvy_visitor_predictor(None, target).tolist() == [1]


def test_savvy_bw_school_holiday_weekday_busy():
    # Thu 1 August 2024 falls in the BW summer school holidays.
    target = make_days(["2024-08-01"])
    assert baselines.savvy_visitor_predictor(None, target).tolist() == [1]


def test_savvy_ignores_train():
    target = make_days(["2024-06-15", "2024-06-18"])
    train = make_days(["2023-06-17"], [100], "summer 2023")
    assert baselines.savvy_visitor_predictor(train, target).equals(
        baselines.savvy_visitor_predictor(None, target)
    )


def test_holidays_package_covers_every_modelled_year():
    for year in [2019, 2022, 2023, 2024, 2025]:
        found = baselines.bw_holidays([year])
        assert any(day.year == year and day.month in (7, 8) for day in found), year


def test_last_season_matches_iso_week_and_weekday():
    # Mon 11 Jul 2022 and Mon 10 Jul 2023 are both Monday of ISO week 28.
    train = make_days(["2022-07-11", "2022-07-12"], [40, 70], "summer 2022")
    target = make_days(["2023-07-10", "2023-07-11"])
    assert baselines.last_season_predictor(train, target).tolist() == [40, 70]


def test_last_season_uses_latest_training_season():
    # Mon 8 Jul 2019 is also Monday of week 28, but 2022 is the last season.
    train = pd.concat(
        [
            make_days(["2019-07-08"], [90], "summer 2019"),
            make_days(["2022-07-11"], [40], "summer 2022"),
        ]
    )
    target = make_days(["2023-07-10"])
    assert baselines.last_season_predictor(train, target).tolist() == [40]


def test_last_season_unmatched_day_takes_weekday_mean():
    # Week 29 has no 2022 day, so Mon 17 Jul 2023 takes the mean of 2022 Mondays.
    train = make_days(["2022-07-04", "2022-07-11", "2022-07-12"], [20, 40, 70], "summer 2022")
    target = make_days(["2023-07-17"])
    assert baselines.last_season_predictor(train, target).tolist() == [30]
    assert date(2023, 7, 17).isocalendar().week == 29
