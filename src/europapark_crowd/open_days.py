"""Build the open-day table: open days only, each labelled with its season."""

from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from europapark_crowd.fetch import RAW_DIR
from europapark_crowd.parse import load_crowd_table

# Listed explicitly so the 2026 holdout season never slips in once 7.1 caches it.
SUMMERS = ["summer 2019", "summer 2022", "summer 2023", "summer 2024", "summer 2025"]


def summer_end(year: int) -> date:
    """Return the last day of the summer season: the first Sunday of November."""
    first = date(year, 11, 1)
    # weekday() is 6 on Sunday, so this steps forward 0 to 6 days.
    return first + timedelta(days=(6 - first.weekday()) % 7)


def season_of(day: date) -> str:
    """Return the season label of a day, from its date alone."""
    # January and February days belong to the winter that started the year before.
    if day.month <= 2:
        return f"winter {day.year - 1}/{day.year % 100:02d}"
    if day <= summer_end(day.year):
        return f"summer {day.year}"
    # Everything after the summer season, HALLOWinter included, is winter.
    return f"winter {day.year}/{(day.year + 1) % 100:02d}"


def load_open_days(raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    """Return the open days of the modelled summers, with a season column."""
    table = load_crowd_table(raw_dir)
    days = table[table["is_open"]].copy()
    # .dt.date gives plain dates, which compare cleanly with summer_end().
    days["season"] = days["date"].dt.date.map(season_of)
    return days[days["season"].isin(SUMMERS)].reset_index(drop=True)
