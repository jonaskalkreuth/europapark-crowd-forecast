import pandas as pd

from europapark_crowd import parse

# One padding day from the previous month, one open day and one closed day,
# copied from the real page layout.
PAGE = """
<div class='cell is-background is-marginless is-paddingless is-flex is-outside-month'>
<article class='is-fullheight box has-background-grey-lighter is-hidden-touch calendar-day'>
<div class='calendar-day-date'>
<span class='calendar-day-weekday'>Fri</span>
<span class='calendar-day-number'>30</span>
</div>
</article>
</div>
<div class='cell is-background is-marginless is-paddingless is-flex'>
<a class="box is-fullheight calendar-day" href="/parks/51/calendar/2023/07/01"><div class='calendar-day-date'>
<span class='calendar-day-weekday'>Sat</span>
<span class='calendar-day-number'>1</span>
</div>
<div class='calendar-day-crowd'>
<span class='calendar-day-percent'>57<small>%</small></span>
<span class='calendar-day-level'>
Busy
</span>
</div>
<div class='calendar-day-hours'>
<div class='calendar-day-period'><span role="img" aria-label="Summer Season">🌸</span> 09:00-18:00</div>
</div>
</a></div>
<div class='cell is-background is-marginless is-paddingless is-flex'>
<article class='is-fullheight box calendar-day is-closed'>
<div class='calendar-day-date'>
<span class='calendar-day-weekday'>Sun</span>
<span class='calendar-day-number'>2</span>
</div>
<div class='calendar-day-hours'>
Closed
</div>
</article>
</div>
"""


def test_padding_days_are_skipped():
    rows = parse.parse_month(PAGE, 2023, 7)
    assert [row["date"].day for row in rows] == [1, 2]


def test_open_day_is_parsed():
    open_day = parse.parse_month(PAGE, 2023, 7)[0]
    assert open_day == {
        "date": pd.Timestamp("2023-07-01").date(),
        "crowd_level": 57,
        "is_open": True,
        "season_label": "Summer Season",
        "hours": "09:00-18:00",
    }


def test_closed_day_has_missing_crowd_level():
    closed_day = parse.parse_month(PAGE, 2023, 7)[1]
    assert closed_day["is_open"] is False
    assert closed_day["crowd_level"] is None
    assert closed_day["season_label"] is None


def test_2019_day_without_season_label_keeps_its_hours():
    page_2019 = PAGE.replace(
        '<span role="img" aria-label="Summer Season">🌸</span>',
        '<span aria-hidden="true">🕘</span>',
    )
    open_day = parse.parse_month(page_2019, 2019, 7)[0]
    assert open_day["season_label"] is None
    assert open_day["hours"] == "09:00-18:00"


def test_table_takes_year_and_month_from_file_name(tmp_path):
    (tmp_path / "2023-07.html").write_text(PAGE, encoding="utf-8")
    table = parse.load_crowd_table(raw_dir=tmp_path)
    assert list(table["date"]) == [pd.Timestamp("2023-07-01"), pd.Timestamp("2023-07-02")]
    assert table["crowd_level"].dtype == "Int64"
    assert table["crowd_level"].isna().tolist() == [False, True]
