"""Polite fetcher for the Queue-Times month calendar pages of Europa-Park."""

import time
from pathlib import Path

import requests

URL = "https://queue-times.com/parks/51/calendar/{year}/{month:02d}"
RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"
HEADERS = {"User-Agent": "europapark-crowd-forecast (portfolio research project)"}
DELAY_SECONDS = 5
SEASON_MONTHS = range(3, 12)  # March to November
YEARS = [2019, 2022, 2023, 2024, 2025]  # 2019 and 2022 to 2025, as a list
HOLDOUT_YEAR = 2026  # ADR 0003: summer 2026 is opened once, in leaf 7.1


def fetch_month(year: int, month: int, raw_dir: Path = RAW_DIR) -> str:
    """Return the raw HTML of one month page, fetching it only if it is not cached."""
    if year == HOLDOUT_YEAR and month in SEASON_MONTHS:
        raise ValueError(f"{year}-{month:02d} is in the holdout season and may not be fetched")

    path = raw_dir / f"{year}-{month:02d}.html"
    if path.exists():
        return path.read_text(encoding="utf-8")

    response = requests.get(URL.format(year=year, month=month), headers=HEADERS, timeout=30)
    response.raise_for_status()
    raw_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(response.text, encoding="utf-8")
    # Sleep only after a real request: cached reads cost Queue-Times nothing.
    time.sleep(DELAY_SECONDS)
    return response.text




def fetch_all() -> None:
    """Fetch every season month of every year in YEARS."""
    for year in YEARS:
        for month in SEASON_MONTHS:  
            fetch_month(year, month)
            print(f"done {year}-{month:02d}")


if __name__ == "__main__":
    fetch_all()