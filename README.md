# Europa-Park crowd forecast

Which open days of a Europa-Park season will be quiet? This project predicts that before the season starts, so a visitor can pick a quiet day.

> **Work in progress** (status 2026-11-04). The pipeline, baselines and calendar features are done. Holiday features are next.

## Data

- **Crowd level:** the daily crowd percentage from the [Queue-Times.com](https://queue-times.com/) month calendar for Europa-Park. It ranks a day against all of the park's days; it is not an attendance count ([ADR 0002](docs/adr/0002-queue-times-crowd-percentage.md)). Raw pages are cached locally and not committed.
- **Seasons:** summers 2019 and 2022–2025. 2020 and 2021 are left out because of COVID. Summer 2026 is the holdout season, scored once at the end ([ADR 0003](docs/adr/0003-evaluation-seasons.md)).
- **Advance information only:** the model may use only what is known before the season starts, such as calendars and holidays ([ADR 0001](docs/adr/0001-advance-information-only.md)).
- **Visit windows:** school-holiday date ranges in [`data/visit_windows.csv`](data/visit_windows.csv), with a source link on every row.

## How it is scored

Each season is ranked by predicted crowd level. Three metrics compare the ranking with the actual crowd levels ([glossary](GLOSSARY.md)):

- **Quiet-day precision:** the share of predicted quiet days that were actually in the season's quietest quarter.
- **Spearman:** the rank correlation between predicted and actual crowd levels.
- **Regret:** how many crowd-level points the predicted quietest day of a visit window sits above its actual quietest day. Lower is better.

Each test season is predicted from all earlier seasons.

## Current result

Test seasons, precision / Spearman / regret:

| Predictor | Summer 2024 | Summer 2025 |
|---|---|---|
| Random guesser | 0.298 / 0.045 / 15.0 | 0.339 / 0.006 / 35.1 |
| Savvy visitor (weekends and Baden-Württemberg holidays are busy) | 0.368 / 0.355 / 28.5 | 0.429 / 0.352 / 23.8 |
| Last season (same ISO week and weekday) | 0.386 / 0.404 / 23.3 | 0.429 / 0.435 / 19.1 |
| Ridge model: weekday, season position, Halloween phase | **0.491** / 0.366 / **21.6** | **0.464** / 0.302 / **8.0** |

The calendar model beats both baselines on quiet-day precision and regret in both test seasons. It still trails the last-season baseline on Spearman. Most of its gain comes from days since opening, used as a straight-line trend through the season. Details and validation scores are in the [design tree](design-tree.md).

## What is next

1. Holiday pressure: the weighted share of the German, French and Swiss catchment on school or public holiday.
2. Interaction features, a tuned linear model and LightGBM.
3. An upper-bound experiment with actual weather.
4. The 2026 holdout season, then the winter season.

## How to run it

Requires [uv](https://docs.astral.sh/uv/) and Python 3.11.

```bash
uv sync
uv run pytest
uv run python -m europapark_crowd.fetch    # caches 45 month pages, 5 s apart
uv run python -m europapark_crowd.linear   # prints the score table
```

## Credits and licences

- Crowd data: Powered by [Queue-Times.com](https://queue-times.com/).
- Baden-Württemberg school holidays: [KMK Ferienregelung](https://www.kmk.org/service/ferienregelung.html) and the [Kultusministerium Baden-Württemberg](https://km.baden-wuerttemberg.de/de/service/ferien).
- French zone B school holidays: Ministère de l'Éducation nationale, [Calendrier scolaire](https://data.education.gouv.fr/explore/dataset/fr-en-calendrier-scolaire/), Licence Ouverte / Etalab 2.0, accessed 2026-11.
- Basel-Stadt school holidays 2025–2026: Kanton Basel-Stadt, Generalsekretariat, [Schulferien Kanton Basel-Stadt](https://data.bs.ch/explore/dataset/100397/), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- Basel-Stadt school holidays 2023–2024: [schulferien.org](https://www.schulferien.org/schweiz/ferien/sommer/basel-stadt/).

Only start and end dates are taken from these sources. None of them endorses this project.

The code is MIT-licensed; see [LICENSE](LICENSE). The licence covers the code only, not the data sources above.
