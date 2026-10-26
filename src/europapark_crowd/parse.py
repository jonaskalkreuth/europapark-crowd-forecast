"""Parse cached Queue-Times month pages into a crowd table."""

from datetime import date
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup

from europapark_crowd.fetch import RAW_DIR


def parse_month(html: str, year: int, month: int) -> list[dict]:
    """Return one row per day of the month shown on one cached month page."""
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for cell in soup.select("div.cell.is-background"):
        # Padding cells belong to the neighbouring month and carry no data.
        if "is-outside-month" in cell["class"]:
            continue
        day = int(cell.select_one(".calendar-day-number").get_text())
        # Closed days have no percent or period element, so these are None.
        percent = cell.select_one(".calendar-day-percent")
        period = cell.select_one(".calendar-day-period")
        rows.append({
            # The cell shows only the day number, so year and month come from the caller.
            "date": date(year, month, day),
            # contents[0] is the "57" before the <small>%</small> tag.
            "crowd_level": int(percent.contents[0]) if percent else None,
            "is_open": percent is not None,
            # 2019 pages show a clock icon without a season label, so .get returns None.
            "season_label": period.span.get("aria-label") if period else None,
            "hours": period.span.next_sibling.strip() if period else None,
        })
    return rows


def load_crowd_table(raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    """Parse every cached month page into one crowd table, one row per date."""
    rows = []
    for path in sorted(raw_dir.glob("*.html")):
        # File names are "YYYY-MM.html", as written by fetch.fetch_month.
        year, month = map(int, path.stem.split("-"))
        rows += parse_month(path.read_text(encoding="utf-8"), year, month)
    table = pd.DataFrame(rows)
    table["date"] = pd.to_datetime(table["date"])
    # Int64 keeps whole numbers while allowing a missing value on closed days.
    table["crowd_level"] = table["crowd_level"].astype("Int64")
    return table
