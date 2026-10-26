# Design tree: europapark-crowd-forecast

Settled input: [GLOSSARY.md](GLOSSARY.md) and [docs/adr/](docs/adr/). Read both before working on any leaf.

## Key decisions
- **Top-level shape** → walking skeleton first, then branches that plug into it. _Why: every later leaf inherits a running pipeline and a score to beat, so each one ends with a measurable result._

- **Leaf handoff** → every leaf carries a four-line brief here: goal, inputs, outputs, done when. "Done when" names a passing test or a harness metric. _Why: a fresh agent can build any leaf from this file plus the glossary and ADRs, without guessing._
- **Feature interface** → one pure function per feature family, taking the open-day table and returning new columns, assembled by a single list. _Why: feature leaves never touch each other's code and each one is tested on its own._

## Tree
Before the first leaf, the user renames the repo to `europapark-crowd-forecast` and recreates `.venv`. Each branch ends with a leaf that writes its thin narrative notebook.

- Europa-Park crowd forecast
  - 1 Skeleton
    - [x] **1.1 Setup and page fetcher** — _why leaf: the source, cache rule and year range are settled in ADR 0002 and ADR 0003._
      - Goal: set up the uv project (Python 3.11) with package `src/europapark_crowd/` and pytest. Write a polite fetcher for Queue-Times month pages (`https://queue-times.com/parks/51/calendar/YYYY/MM`).
      - Inputs: none.
      - Outputs: raw HTML for the season months of 2019 and 2022–2025 cached in git-ignored `data/raw/`. Each page is fetched once, with a delay between requests. 2026 is refused.
      - Done when: tests pass for "a cached page is not re-fetched" and "2026 is refused"; the raw pages are on disk.
      - Decisions: season months are March–November (45 pages); the guard refuses 2026 months 3–11 only, so 6.1 can fetch January 2026 and 7.1 adds a deliberate override; tests use `monkeypatch` on `requests.get` and `tmp_path` as the cache folder; run with `uv run python -m europapark_crowd.fetch`, 5 s delay after each real fetch, project User-Agent.
    - [x] **1.2 Parse month pages into a crowd table** — _why leaf: the columns are fixed below; handling of odd values follows from the inspection._ (needs 1.1)
      - Goal: turn each cached month page into rows of one date each, then inspect the result and report findings before handling them.
      - Inputs: cached HTML from 1.1.
      - Outputs: a crowd table with date, crowd level, open or closed, season icon (summer, Halloween, winter) and raw opening hours. Inspection findings on duplicates, gaps and odd values go into this brief as notes.
      - Done when: parser tests pass on a small hand-made HTML snippet; the findings are noted here.
      - Decisions: parse with BeautifulSoup in `src/europapark_crowd/parse.py`; skip `is-outside-month` padding cells; `load_crowd_table()` rebuilds the DataFrame from `data/raw/` on each call, nothing saved; closed days get a missing crowd value, not 0; the season label is kept as raw text (four labels seen: Summer Season, Halloween, HALLOWinter, Winter Season), handling deferred to inspection; the inspection lives in a committed notebook with saved outputs.
      - Findings (evidence: [notebooks/inspection/1.2_crowd_table.ipynb](notebooks/inspection/1.2_crowd_table.ipynb)):
        - 1,375 rows = 275 days (March–November) × 5 years: 1,230 open, 145 closed. No duplicate dates. Every open day has a crowd level and hours.
        - 2019 pages carry no season label (a clock icon instead), so all 220 open days of 2019 have a missing label. 2022–2025 use four labels: Summer Season, Halloween, HALLOWinter, Winter Season.
        - In 2022–2025 the Halloween phase is always the 37 days ending on the first Sunday of November. Leaf 2.2 uses this date rule, so 2019 gets a Halloween phase (28 Sep – 3 Nov, start still to verify against an official source). The 2019 summer season also ended on Sunday 3 Nov.
        - From 2022 the park never closes between Halloween and winter: the HALLOWinter phase (November, median crowd level 17) bridges them. Leaf 1.3 cannot split seasons on a closure gap and must decide where HALLOWinter days belong. In 2019 the park closed 4–22 Nov and winter opened on 23 Nov.
        - 2024 opened 16–17 Mar, closed 18–22 Mar, then reopened on 23 Mar.
        - 2022–2025 hours are one fixed value per label (09:00-18:00 summer and Halloween, 11:00-19:00 HALLOWinter and winter), so they look like a template rather than real hours. 2019 hours vary (09:00-18:00 to 09:00-20:00, plus two event nights).
        - The crowd level saturates: 23 open days sit at 99 or 100. Early 2022 (28 Mar – 8 Apr) and HALLOWinter 2022–2023 hold several 1–2% days. All are left as they are.
    - [x] **1.3 Open-day table and feature list** — _why leaf: the feature interface is fixed by the Key decisions._ (needs 1.2)
      - Goal: keep open days only, label each with its season (for example "summer 2023"), keep summers 2019 and 2022–2025. Add the weekday feature function and the single feature list.
      - Inputs: the crowd table from 1.2.
      - Outputs: the open-day table; a weekday feature function; the feature list that assembles all feature functions.
      - Done when: tests pass for season labelling (including a winter season that crosses New Year) and for the weekday function.
      - Decisions: season labels always come from dates, never from the season label column (2019 has none). The summer season ends on the first Sunday of November, the last Halloween day; `summer_end(year)` holds this rule so 2.2 can reuse it. Every later day, including HALLOWinter, belongs to the winter season, labelled like "winter 2023/24"; January days belong to the previous year's winter. The 18–22 March 2024 closure is an exception: 16–17 March stay in summer 2024, and a short closure never splits a season. The weekday feature is one integer column, `weekday` (Monday = 0); one-hot encoding waits for the linear model in 1.7.
      - Plan:
        1. `src/europapark_crowd/open_days.py`: `summer_end(year)`, `season_of(day)`, and `load_open_days()`, which keeps open days, adds a `season` column and keeps summers 2019 and 2022–2025.
        2. `src/europapark_crowd/features.py`: `weekday(days)`, `FEATURES = [weekday]`, and `add_features(days)`, which concatenates the columns from every function in `FEATURES`.
        3. Tests on hand-made DataFrames. `tests/test_open_days.py`: mid-July is summer; the first Sunday of November is summer; the next Monday is winter; January is the previous year's winter; March 2024 days are summer 2024; closed days are dropped; an unlabelled 2019 day still gets a season. `tests/test_features.py`: weekday values on known dates; `add_features` keeps the row count.
        4. `GLOSSARY.md`: Season is defined by date rules, not an uninterrupted run, and a short closure does not split it; Summer season ends on the first Sunday of November; Winter season starts the next day and includes HALLOWinter; add a HALLOWinter entry.
        5. Run pytest; check that summer plus non-summer rows reconcile to the 1,230 open days; report open summer days per year.
      - Findings:
        - The 1,230 open days split into 1,118 summer days and 112 winter days. The open-day table keeps the 1,118, with no duplicate dates and no missing crowd levels.
        - Open days per summer: 2019 212, 2022 226, 2023 226, 2024 228, 2025 226.
        - Summer 2019 opened on 6 April, later than any other year (16–26 March).
        - All 96 HALLOWinter days fall into winter; the summer days carry only Summer Season, Halloween or no label (2019).
    - [ ] **1.4 Evaluation harness** — _why leaf: the metrics, runs and predictor shape are all defined here and in the glossary._ (needs 1.3)
      - Goal: implement quiet-day precision, Spearman and regret, and the two runs. A predictor is any function that takes the training days and the days to predict and returns a predicted crowd level per day.
      - Inputs: the open-day table from 1.3.
      - Outputs: metric functions; run definitions (run 1: train 2019 and 2022, validate 2023, predict 2024; run 2: add 2023, validate 2024, predict 2025); one printed score table per predictor.
      - Done when: metric tests on hand-made rankings with known answers pass; a dummy predictor produces a score table. If the leaf overruns, regret moves to 1.5.
    - [ ] **1.5 Visit windows** — _why leaf: the list of windows is settled; only the dates need typing in._ (needs 1.4)
      - Goal: write the fixed list of visit windows for 2024, 2025 and 2026 as a small hand-typed data file, using official holiday dates, and wire it into regret.
      - Inputs: the window list: spring, summer and autumn within the summer season; Saturdays of each month; Baden-Württemberg Easter, Whitsun, summer and autumn holidays; French zone B summer holidays; Basel-Stadt summer holidays.
      - Outputs: the window data file with a source link for each date range; a loader; regret in the score table.
      - Done when: a loader test passes; the harness prints regret.
    - [ ] **1.6 Baselines** — _why leaf: both rules are defined in the glossary._ (needs 1.4)
      - Goal: implement the savvy-visitor baseline (Baden-Württemberg school and public holidays from the `holidays` package) and the last-season baseline as predictors.
      - Inputs: the open-day table and the harness.
      - Outputs: two predictors and their score tables, recorded in this brief as "the bar to beat".
      - Done when: baseline tests pass; both score tables are noted here.
    - [ ] **1.7 First linear model** — _why leaf: weekday feature only, through existing pieces._ (needs 1.3, 1.4)
      - Goal: fit a regularised linear model on the weekday feature through the feature list and the harness, proving the full path works.
      - Inputs: the feature list and the harness.
      - Outputs: a linear predictor and its score table next to the baselines.
      - Done when: its score table prints next to the baselines.
    - [ ] **1.8 Skeleton notebook** — _why leaf: it narrates finished work._ (needs 1.2–1.7)
      - Goal: write the thin narrative notebook covering what the crowd data looks like, the COVID gap, how quiet days are defined, the baselines and the first model.
      - Inputs: the `src/` functions from 1.1–1.7.
      - Outputs: one notebook that only calls `src/` functions.
      - Done when: it runs top to bottom.
  - 2 Calendar features — the Rulantica flag moved to branch 6, because it is constant within every summer season and cannot change a within-season ranking.
    - [ ] **2.1 Season position** — _why leaf: both features are defined below._ (needs 1.7)
      - Goal: add week of the season and days since opening day as one feature function.
      - Inputs: the open-day table with season labels (1.3).
      - Outputs: one feature function with two columns, added to the feature list.
      - Done when: tests pass on a hand-made season; the harness prints the score change against the weekday-only model.
    - [ ] **2.2 Halloween phase** — _why leaf: the source column exists in the crowd table._ (needs 1.7)
      - Goal: add a flag for days in the Halloween phase, read from the season icon kept in 1.2.
      - Inputs: the open-day table with the season icon column.
      - Outputs: one feature function, added to the feature list.
      - Done when: tests pass; inspection confirms one uninterrupted Halloween run per season; the harness prints the score change.
    - [ ] **2.3 Calendar notebook** — _why leaf: it narrates finished work._ (needs 2.1, 2.2)
      - Goal: write the thin narrative notebook for the calendar features and their score changes.
      - Inputs: the `src/` functions from branch 2.
      - Outputs: one notebook that only calls `src/` functions.
      - Done when: it runs top to bottom.
  - 3 Holiday features
    - 3.1 Holiday data — covers summers 2019 and 2022–2026; holidays are advance information, so 2026 is allowed here.
      - [ ] **3.1.1 Holiday table format and German holidays** — _why leaf: the format and source are fixed below._ (needs 1.1)
        - Goal: define the shared holiday table (one row per date, region and kind, where kind is school or public; region codes like `DE-BW`, `FR-B`, `CH-BS`) and load all 16 German states.
        - Inputs: the `holidays` package (`categories='school'` for school holidays, default for public holidays).
        - Outputs: a German loader returning the shared table for 2019 and 2022–2026, with the date range as a parameter so branch 6 can extend it; inspection notes in this brief. Schools' own movable holiday days are a known limitation.
        - Done when: tests pass for the table format and for a known Baden-Württemberg summer holiday date.
      - [ ] **3.1.2 French holidays** — _why leaf: the source and the national public-holiday rule are fixed below._ (needs 3.1.1)
        - Goal: load school holidays for zones A, B and C, plus national public holidays applied to every zone.
        - Inputs: data.education.gouv.fr dataset `fr-en-calendrier-scolaire` (cached once); the `holidays` package for public holidays.
        - Outputs: a French loader returning the shared table. Inspection checks whether start dates mean the last school day or the first free day. Alsace-Moselle's two extra public holidays are ignored as a known limitation.
        - Done when: tests pass on a hand-made snippet of the source data.
      - [ ] **3.1.3 Swiss holidays and combined loader** — _why leaf: sources and cantons are fixed below._ (needs 3.1.1; the combined loader also needs 3.1.2)
        - Goal: load school and public holidays for cantons BS, BL, AG, ZH, BE and SO, then provide one function returning all three countries.
        - Inputs: OpenHolidays API (https://openholidaysapi.org) for 2022–2026, in queries of at most 1,095 days; a hand-typed 2019 file with a source link per date range; the `holidays` package for cantonal public holidays.
        - Outputs: a Swiss loader; the 2019 file; a combined loader.
        - Done when: tests pass for the 2019 file, the API parser and the combined loader; the combined table holds every region for every season. If the leaf overruns, the combined loader becomes its own leaf.
    - [ ] **3.2 Catchment weights** — _why leaf: regions, population source, distance and decay form are fixed below._ (needs 1.1)
      - Goal: build one row per catchment region: the 16 German states, the 13 metropolitan French régions (each mapped to its school-holiday zone), and cantons BS, BL, AG, ZH, BE and SO. Each row holds population, distance and weight.
      - Inputs: Eurostat regional population for one fixed year; coordinates of each region's capital; the park's coordinates (Rust).
      - Outputs: a catchment table with region code, holiday region code (for France, the zone), population, straight-line distance to the park in km, and a function giving the weight as population × exp(−distance / decay length). Verify that every French région lies in a single zone.
      - Done when: tests pass for the weight function (known answers at distance 0 and at one decay length) and for the région-to-zone mapping.
    - 3.3 Holiday feature functions — each leaf adds one function to the feature list and reports its score change against the weekday-only model from 1.7.
      - [ ] **3.3.1 Holiday pressure** — _why leaf: the definition is fixed below._ (needs 1.7, 3.1, 3.2)
        - Goal: add school-holiday pressure and public-holiday pressure as one feature function.
        - Inputs: the combined holiday table (3.1.3), the catchment table and weight function (3.2), a provisional decay length of 200 km until 3.4.
        - Outputs: for each open day, the summed catchment weight of regions on holiday divided by the total catchment weight, once for school and once for public holidays.
        - Done when: tests pass on a hand-made catchment of 2–3 regions with known answers; the harness prints the score change.
      - [ ] **3.3.2 Holiday block edges** — _why leaf: the 3-day window is fixed._ (needs 3.3.1)
        - Goal: add the weighted share of the catchment in the first 3 days of a holiday block, and in the last 3 days.
        - Inputs: as 3.3.1.
        - Outputs: one feature function with two columns.
        - Done when: tests pass on hand-made blocks (including a block shorter than 6 days); the harness prints the score change.
      - [ ] **3.3.3 Bridge days and long weekends** — _why leaf: both terms are defined in the glossary._ (needs 3.3.1)
        - Goal: add the weighted share of the catchment on a bridge day, and the weighted share on a long weekend.
        - Inputs: as 3.3.1, public holidays only.
        - Outputs: one feature function with two columns.
        - Done when: tests pass on a hand-made calendar with a Thursday holiday (Friday becomes a bridge day) and a Monday holiday (long weekend); the harness prints the score change.
    - [ ] **3.4 Decay tuning** — _why leaf: the grid and selection rule are fixed below._ (needs 3.3.1–3.3.3)
      - Goal: choose the decay length for each run by validation-season score only. Branch 4 holds it fixed afterwards.
      - Inputs: the linear model with all holiday features; the grid 50, 100, 200, 400 and 800 km plus "no decay" (population only).
      - Outputs: a table of validation scores per decay length and run; the chosen value per run, used by every later leaf.
      - Done when: the table is printed and the chosen values are noted in this brief.
    - [ ] **3.5 Holiday notebook** — _why leaf: it narrates finished work._ (needs 3.4)
      - Goal: write the thin narrative notebook covering how holiday pressure is built, the catchment weights as a map or table, and the score change from each feature.
      - Inputs: the `src/` functions from branch 3.
      - Outputs: one notebook that only calls `src/` functions.
      - Done when: it runs top to bottom.
  - 4 Models — every leaf holds the decay length from 3.4 fixed and makes choices on validation seasons only.
    - [ ] **4.1 Interaction features** — _why leaf: the list of four is fixed._ (needs 2.1, 2.2, 3.4)
      - Goal: add the hand-built interactions as one feature function: weekday × school-holiday pressure, weekday × public-holiday pressure, weekday × Halloween phase, week of the season × school-holiday pressure.
      - Inputs: the feature list with the calendar and holiday features.
      - Outputs: one feature function, added to the feature list. All four interactions are kept, and regularisation shrinks the useless ones.
      - Done when: tests pass on a hand-made table; the harness prints the score change.
    - [ ] **4.2 Linear model tuning** — _why leaf: the options and the selection rule are fixed._ (needs 4.1)
      - Goal: for each run, choose the regularisation type (ridge, lasso, elastic net) and strength on the validation season.
      - Inputs: the full feature list.
      - Outputs: the chosen settings per run, noted in this brief; the final linear score table.
      - Done when: the score table prints next to the baselines.
    - [ ] **4.3 LightGBM** — _why leaf: the feature sets and tuning rule are fixed._ (needs 3.4, 2.1, 2.2; the extra run needs 4.1)
      - Goal: run LightGBM through the harness on the base features without interactions (main comparison), plus one extra run with the interactions.
      - Inputs: the feature list; a small fixed tuning grid, chosen on the validation season.
      - Outputs: two score tables next to the linear model and the baselines.
      - Done when: both score tables print.
    - [ ] **4.4 Error analysis** — _why leaf: the scope and the leakage rule are fixed._ (needs 4.2, 4.3)
      - Goal: find which days each model ranks worst and look for patterns (weekdays, holiday edges, likely events missing from our data). Validation seasons only; test seasons never feed ideas back.
      - Inputs: predictions of the tuned models on the validation seasons.
      - Outputs: a short findings list, noted in this brief.
      - Done when: the findings are noted.
    - [ ] **4.5 Models notebook** — _why leaf: it narrates finished work._ (needs 4.4)
      - Goal: write the thin narrative notebook covering coefficients, LightGBM feature importance, the error analysis and the final score table.
      - Inputs: the `src/` functions from branch 4.
      - Outputs: one notebook that only calls `src/` functions.
      - Done when: it runs top to bottom.
  - 5 Upper-bound experiment
    - [ ] **5.1 Weather features** — _why leaf: source, variables and the separate list are fixed._ (needs 1.7)
      - Goal: fetch daily weather for Rust from the Open-Meteo archive (https://open-meteo.com/en/docs/historical-weather-api) for summers 2019 and 2022–2025, cached once, and add a weather feature function.
      - Inputs: Open-Meteo archive (no key; CC BY 4.0).
      - Outputs: a weather feature function with maximum temperature, precipitation and sunshine hours, placed in a separate upper-bound feature list and never in the main one (ADR 0001).
      - Done when: tests pass on a hand-made weather response; a test confirms the main feature list contains no weather column.
    - [ ] **5.2 Upper-bound run and notebook** — _why leaf: a rerun plus narrative._ (needs 5.1, 4.2, 4.3)
      - Goal: rerun the best model from branch 4 with weather added and compare against the main model.
      - Inputs: the upper-bound feature list; the tuned settings from branch 4.
      - Outputs: a score table; a thin notebook that repeats the caveat that the crowd level may already include weather (ADR 0002) and credits "Weather data by Open-Meteo.com".
      - Done when: the notebook runs top to bottom.
  - 6 Winter season — evaluation: train 2019/20 and 2022/23, validate 2023/24, test 2024/25, then 2025/26. Winter 2021/22 is left out (COVID rules). There is no winter holdout season.
    - [ ] **6.1 Winter data check** — _why leaf: it ends in one go/no-go finding._ (needs 1.2)
      - Goal: fetch the winter months of 2019/20 and 2022/23 to 2025/26 (November 2025 to January 2026 is allowed; nothing from the 2026 summer season) and inspect them, especially the 0–2% weekday values.
      - Inputs: the fetcher (1.1) and parser (1.2).
      - Outputs: inspection notes; the verified start date of winter 2019/20 and opening date of Rulantica. If Rulantica opened before that winter season started, the Rulantica flag is dropped for good.
      - Done when: this brief records whether winter data is usable and whether the Rulantica flag survives.
    - [ ] **6.2 Winter setup** — _why leaf: the runs and windows are fixed in this branch's header._ (needs 6.1, 1.5, 3.1.3)
      - Goal: add winter season labels and runs, extend the holiday data to November–January, add a winter visit-window file, and add the Rulantica flag if 6.1 kept it.
      - Inputs: winter windows: the Baden-Württemberg Christmas holidays, French zone B Christmas holidays, Basel-Stadt Christmas holidays, and Saturdays in each month.
      - Outputs: winter runs in the harness; the winter window file with source links; holiday data covering the winter seasons.
      - Done when: a dummy predictor produces a winter score table.
    - [ ] **6.3 Winter runs** — _why leaf: the same pipeline on new seasons._ (needs 6.2, 4.2, 4.3)
      - Goal: run both baselines, the linear model and LightGBM on winter, tuning on winter validation seasons only.
      - Inputs: the winter runs; the summer feature list.
      - Outputs: the winter score tables, noted in this brief.
      - Done when: all four score tables print.
    - [ ] **6.4 Winter notebook and README section** — _why leaf: it narrates finished work._ (needs 6.3, 7.2)
      - Goal: write the thin winter notebook and add a winter section to the README, including "no winter holdout" as a limitation.
      - Inputs: the `src/` functions from branch 6.
      - Outputs: one notebook that only calls `src/` functions; the README winter section.
      - Done when: the notebook runs top to bottom.
  - 7 Wrap-up
    - [ ] **7.1 Holdout season** — _why leaf: the protocol is fixed in ADR 0003._ (needs 4.2, 4.3, summer 2026 ended)
      - Goal: fetch summer 2026 once, tune on 2025 as the validation season, refit on 2019 and 2022–2025, predict 2026 and score it once.
      - Inputs: the full pipeline; holiday data and visit windows already cover 2026.
      - Outputs: the holdout score table for the baselines and both models, reported whatever it shows.
      - Done when: the score table is noted in this brief.
    - [ ] **7.2 README case study** — _why leaf: the sections are fixed below._ (needs 7.1, 5.2, 3.5, 2.3, 4.5)
      - Goal: write the README as a case study.
      - Inputs: all notebooks and score tables.
      - Outputs: sections on the problem, the data and its caveats, the approach, the feature story, a results table (baselines, models, upper bound, holdout), limitations, and credits ("Powered by Queue-Times.com" with a link; "Weather data by Open-Meteo.com").
      - Done when: the user has reviewed it.
    - [ ] **7.3 Dashboard: 2027 forecast calendar (optional)** — _why leaf: content and tool are fixed._ (needs 7.1)
      - Goal: build a Streamlit app that shows a predicted crowd calendar for summer 2027 with quiet days marked, plus a visit-window picker.
      - Inputs: the final model refit in 7.1; holiday data for 2027; assumed 2027 season dates, clearly labelled as assumed.
      - Outputs: the app, run locally.
      - Done when: the app runs locally and the picker ranks days within a chosen window.
    - [ ] **7.4 Dashboard: holdout tab and deploy (optional)** — _why leaf: one tab plus deployment._ (needs 7.3)
      - Goal: add a tab comparing predicted and actual crowd levels for summer 2026, then deploy to Streamlit Community Cloud.
      - Inputs: the holdout predictions from 7.1.
      - Outputs: the deployed app, credited to Queue-Times.com, linked from the README.
      - Done when: the public link works.

Cross-branch rules:
- The savvy-visitor baseline counts only Baden-Württemberg school and public holidays, from the `holidays` package. It never uses holiday pressure.
- The Skeleton gives the open-day table a weekday feature only. Branch 2 adds the other calendar features.
- No leaf fetches the 2026 summer season except the holdout leaf 7.1. Leaf 6.1 may fetch November 2025 to January 2026 for winter.
- Holiday loaders take the date range as a parameter.

## Next up

Work top to bottom. Each line respects the dependency notes in the tree. Before leaf 1, rename the repo and recreate `.venv`.

1. [x] 1.1 Setup and page fetcher — 2 tests pass; 45 pages (Mar–Nov of 2019, 2022–2025) cached in data/raw/
2. [x] 1.2 Parse month pages into a crowd table — 7 tests pass; 1,375 rows (1,230 open); 2019 has no season labels; HALLOWinter bridges Halloween and winter from 2022
3. [x] 1.3 Open-day table and feature list — 10 new tests pass (17 total); 1,118 open summer days in 5 seasons; summer ends on the first Sunday of November
4. [ ] 1.4 Evaluation harness
5. [ ] 1.5 Visit windows
6. [ ] 1.6 Baselines
7. [ ] 1.7 First linear model
8. [ ] 1.8 Skeleton notebook
9. [ ] 2.1 Season position
10. [ ] 2.2 Halloween phase
11. [ ] 2.3 Calendar notebook
12. [ ] 3.1.1 Holiday table format and German holidays
13. [ ] 3.1.2 French holidays
14. [ ] 3.1.3 Swiss holidays and combined loader
15. [ ] 3.2 Catchment weights
16. [ ] 3.3.1 Holiday pressure
17. [ ] 3.3.2 Holiday block edges
18. [ ] 3.3.3 Bridge days and long weekends
19. [ ] 3.4 Decay tuning
20. [ ] 3.5 Holiday notebook
21. [ ] 4.1 Interaction features
22. [ ] 4.2 Linear model tuning
23. [ ] 4.3 LightGBM
24. [ ] 4.4 Error analysis
25. [ ] 4.5 Models notebook
26. [ ] 5.1 Weather features
27. [ ] 5.2 Upper-bound run and notebook
28. [ ] 7.1 Holdout season
29. [ ] 7.2 README case study
30. [ ] 6.1 Winter data check
31. [ ] 6.2 Winter setup
32. [ ] 6.3 Winter runs
33. [ ] 6.4 Winter notebook and README section
34. [ ] 7.3 Dashboard: 2027 forecast calendar (optional)
35. [ ] 7.4 Dashboard: holdout tab and deploy (optional)
