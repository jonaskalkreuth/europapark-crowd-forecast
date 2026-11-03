"""Visit windows: hand-typed holiday ranges plus calendar-season and Saturday rules."""

from pathlib import Path

import pandas as pd

WINDOWS_FILE = Path(__file__).resolve().parents[2] / "data" / "visit_windows.csv"

# Meteorological seasons; autumn runs on until the summer season ends in November.
CALENDAR_SEASONS = {"spring": [3, 4, 5], "summer": [6, 7, 8], "autumn": [9, 10, 11]}


def load_windows(path: Path = WINDOWS_FILE) -> pd.DataFrame:
    """Return the holiday windows: one row per range, both end dates included."""
    return pd.read_csv(path, parse_dates=["start", "end"])


def season_windows(days: pd.DataFrame, holidays: pd.DataFrame) -> dict[str, pd.Series]:
    """Return a mask over one season's open days for each visit window in it."""
    dates = days["date"]
    windows = {}
    for row in holidays.itertuples():
        mask = dates.between(row.start, row.end)
        # Each name repeats once per year, so keep only the range that falls in this season.
        if mask.any():
            windows[row.window] = mask
    for name, months in CALENDAR_SEASONS.items():
        windows[name] = dates.dt.month.isin(months)
    saturdays = dates.dt.day_of_week == 5
    for month in dates.dt.month.unique():
        windows[f"Saturdays in {pd.Timestamp(2000, month, 1):%B}"] = saturdays & (
            dates.dt.month == month
        )
    # A window with one open day has nothing to choose from, so its regret is always 0.
    return {name: mask for name, mask in windows.items() if mask.sum() >= 2}
