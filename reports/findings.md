# Findings

Findings per leaf of the [design tree](../design-tree.md). Scores read precision / Spearman / regret. Terms follow the [glossary](../GLOSSARY.md).

## 1.2 Crowd table

Evidence: [notebooks/inspection/1.2_crowd_table.ipynb](../notebooks/inspection/1.2_crowd_table.ipynb).

- The crowd table holds 1,375 rows: 275 days (March–November) × 5 years. 1,230 days are open and 145 closed.
- No date appears twice. Every open day has a crowd level and opening hours.
- 2019 pages carry no season label, so all 220 open days of 2019 lack one. 2022–2025 use four labels: Summer Season, Halloween, HALLOWinter, Winter Season.
- In 2022–2025 the Halloween phase is always the 37 days ending on the first Sunday of November. The same rule gives 2019 a Halloween phase of 28 Sep – 3 Nov, not yet checked against an official source.
- From 2022 the park never closes between Halloween and winter. HALLOWinter (median crowd level 17) bridges them, so seasons cannot be split on a closure gap. In 2019 the park closed 4–22 Nov.
- 2024 opened 16–17 Mar, closed 18–22 Mar, then reopened on 23 Mar.
- 2022–2025 hours are one fixed value per label, so they look like a template rather than real hours. 2019 hours vary.
- The crowd level saturates: 23 open days sit at 99 or 100. Early 2022 and HALLOWinter 2022–2023 hold several 1–2% days. All values stay as they are.

## 1.3 Open-day table

- The 1,230 open days split into 1,118 summer days and 112 winter days. The open-day table keeps the 1,118 summer days, with no duplicate dates and no missing crowd levels.
- Open days per summer: 2019 212, 2022 226, 2023 226, 2024 228, 2025 226.
- Summer 2019 opened on 6 April, later than any other year (16–26 March).
- All 96 HALLOWinter days fall into winter.

## 1.4 Evaluation harness

- Actual quiet days per summer: 2019 53 of 212, 2022 58 of 226, 2023 59 of 226, 2024 62 of 228, 2025 57 of 226. Ties at the cutoff lift the quiet share to 25–27%, so chance precision sits slightly above 0.25.
- The seeded random guesser scores precision 0.30–0.34 and Spearman −0.03 to 0.05. This is the chance level. Precision varies by about ±0.06 with only 56–57 picks per season.

## 1.5 Visit windows

- Basel-Stadt summer 2023 and 2024 come from schulferien.org, not an official source. Their rows in `data/visit_windows.csv` say "(unofficial)". These two ranges are probably one day short, because schulferien.org ends each range on the Saturday and the canton on the Sunday.
- Every holiday range falls fully on open days.
- Windows per scored season: 2023 16, 2024 17, 2025 17 (6 holiday, 3 calendar-season, 7–8 Saturday windows). Windows with only one open day are dropped.
- The random guesser's regret is 32.3 (2023), 15.0 (2024) and 35.1 (2025).
- The savvy visitor ties on most days inside a window, so its averaged pick is often worse than the random guesser's.

## 1.6 Baselines

- The `holidays` package gives Baden-Württemberg school holidays for every modelled year (83–88 days each) and 12 public holidays per year.
- The savvy-visitor rule calls 54–58% of each summer busy.
- The last-season baseline leaves only 2 target days unmatched (early summer 2024).

## 1.7 First linear model

- Saturday is the busiest day in every season (mean crowd level 71–80). The quietest weekday changes by season: Wednesday in 2019 and 2025, Friday in 2022 and 2024, Tuesday in 2023.
- Weekday alone gives only 7 distinct predictions per season, so the seeded tie-break chooses which days fill the predicted quiet quarter.

Score table. Run 1 test and run 2 validation both fit on 2019, 2022 and 2023 and score 2024, so they match.

| Predictor | run 1 validate 2023 | run 1 test 2024 | run 2 validate 2024 | run 2 test 2025 |
|---|---|---|---|---|
| Random | 0.339 / −0.033 / 32.3 | 0.298 / 0.045 / 15.0 | 0.298 / 0.045 / 15.0 | 0.339 / 0.006 / 35.1 |
| Savvy visitor | 0.429 / 0.450 / 26.0 | 0.368 / 0.355 / 28.5 | 0.368 / 0.355 / 28.5 | 0.429 / 0.352 / 23.8 |
| Last season | 0.625 / 0.515 / 14.9 | 0.386 / 0.404 / 23.3 | 0.386 / 0.404 / 23.3 | 0.429 / 0.435 / 19.1 |
| Linear (weekday) | 0.339 / 0.334 / 25.9 | 0.351 / 0.258 / 27.4 | 0.351 / 0.258 / 27.4 | 0.286 / 0.204 / 22.2 |

The weekday model ranks the season better than chance but stays below both baselines. Its precision is at chance level: weekday alone cannot find the quiet quarter.

## 2.1 Season position

- Every opening day is a Saturday: 2019-04-06, 2022-03-26, 2023-03-25, 2024-03-16, 2025-03-22.
- The last week of the season is 31 in 2019, 34 in 2024 and 33 in the other seasons.
- The mean crowd level by week of the season is not a straight line. It peaks around weeks 3–4 (Easter), 20–21 (summer holidays) and 32 (Halloween).

| Run / stage | Weekday only | + season position | Change |
|---|---|---|---|
| run 1 validate 2023 | 0.339 / 0.334 / 25.9 | 0.464 / 0.414 / 17.6 | +0.125 / +0.080 / −8.3 |
| run 1 test 2024 | 0.351 / 0.258 / 27.4 | 0.509 / 0.367 / 21.6 | +0.158 / +0.109 / −5.8 |
| run 2 validate 2024 | 0.351 / 0.258 / 27.4 | 0.509 / 0.367 / 21.6 | +0.158 / +0.109 / −5.8 |
| run 2 test 2025 | 0.286 / 0.204 / 22.2 | 0.464 / 0.305 / 8.0 | +0.179 / +0.101 / −14.2 |

Even as a straight-line trend, season position lifts precision from chance level to 0.46–0.51.

## 2.2 and 2.3 Halloween phase and calendar model

- Every summer has one uninterrupted run of 37 Halloween days ending on its last summer day: 185 of 1,118 days. The date rule matches the season label on all 906 labelled days.
- The Halloween phase is busier than the rest of the season by 11–15 points on most weekdays, but by less than 1 point on Tuesday.

On top of season position, the Halloween flag adds almost nothing. The trend in days since opening already absorbs most of the Halloween lift.

| Run and stage | Weekday + season position | All three | Change |
|---|---|---|---|
| run 1 validate 2023 | 0.464 / 0.414 / 17.6 | 0.482 / 0.414 / 17.6 | +0.018 / 0.000 / 0.0 |
| run 1 test 2024 | 0.509 / 0.367 / 21.6 | 0.491 / 0.366 / 21.6 | −0.018 / −0.001 / 0.0 |
| run 2 validate 2024 | 0.509 / 0.367 / 21.6 | 0.491 / 0.366 / 21.6 | −0.018 / −0.001 / 0.0 |
| run 2 test 2025 | 0.464 / 0.305 / 8.0 | 0.464 / 0.302 / 8.0 | 0.000 / −0.003 / 0.0 |

The full calendar model beats the last-season baseline on precision and regret in both test seasons. It still trails on Spearman, and on every metric for the 2023 validation season.
