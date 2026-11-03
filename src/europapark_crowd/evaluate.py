"""Evaluation harness: metrics, runs and a score table per predictor."""

import numpy as np
import pandas as pd

from europapark_crowd.open_days import load_open_days
from europapark_crowd.windows import load_windows, season_windows

SEED = 0

RUNS = [
    {
        "run": "run 1",
        "train": ["summer 2019", "summer 2022"],
        "validate": "summer 2023",
        "test": "summer 2024",
    },
    {
        "run": "run 2",
        "train": ["summer 2019", "summer 2022", "summer 2023"],
        "validate": "summer 2024",
        "test": "summer 2025",
    },
]


def actual_quiet(crowd: pd.Series) -> pd.Series:
    """Mark days at or below the 25th-percentile crowd level; ties all count."""
    return crowd <= crowd.quantile(0.25)


def predicted_quiet(predicted: pd.Series) -> pd.Series:
    """Mark exactly n // 4 days with the lowest predictions."""
    # Shuffle before a stable sort, so tied predictions are picked in a seeded random order.
    shuffled = predicted.sample(frac=1, random_state=SEED)
    lowest = shuffled.sort_values(kind="stable").index[: len(predicted) // 4]
    return pd.Series(predicted.index.isin(lowest), index=predicted.index)


def quiet_day_precision(actual: pd.Series, predicted: pd.Series) -> float:
    """Return the share of predicted quiet days that were actual quiet days."""
    return actual_quiet(actual)[predicted_quiet(predicted)].mean()


def spearman(actual: pd.Series, predicted: pd.Series) -> float:
    """Return the Spearman correlation: the Pearson correlation of the ranks."""
    return actual.rank().corr(predicted.rank())


def regret(actual: pd.Series, predicted: pd.Series, window: pd.Series) -> float:
    """Return how far the predicted quietest day of a window sits above the actual quietest."""
    actual, predicted = actual[window], predicted[window]
    # Days tied for the lowest prediction are averaged: the expected pick of a visitor.
    picked = actual[predicted == predicted.min()].mean()
    return picked - actual.min()


def mean_regret(actual: pd.Series, predicted: pd.Series, windows: dict[str, pd.Series]) -> float:
    """Return the regret averaged over a season's visit windows."""
    return np.mean([regret(actual, predicted, window) for window in windows.values()])


def score(predictor, days: pd.DataFrame, holidays: pd.DataFrame) -> pd.DataFrame:
    """Return one row of scores per run and stage for a predictor."""
    rows = []
    for run in RUNS:
        stages = [
            ("validate", run["train"], run["validate"]),
            ("test", run["train"] + [run["validate"]], run["test"]),
        ]
        for stage, train_seasons, target_season in stages:
            train = days[days["season"].isin(train_seasons)]
            target = days[days["season"] == target_season]
            predicted = predictor(train, target.drop(columns="crowd_level"))
            actual = target["crowd_level"]
            rows.append(
                {
                    "run": run["run"],
                    "stage": stage,
                    "season": target_season,
                    "days": len(target),
                    "precision": quiet_day_precision(actual, predicted),
                    "spearman": spearman(actual, predicted),
                    "regret": mean_regret(actual, predicted, season_windows(target, holidays)),
                }
            )
    return pd.DataFrame(rows).set_index(["run", "stage"])


def random_predictor(train: pd.DataFrame, target: pd.DataFrame) -> pd.Series:
    """Predict a seeded random crowd level per day: the chance level to beat."""
    rng = np.random.default_rng(SEED)
    return pd.Series(rng.uniform(0, 100, len(target)), index=target.index)


if __name__ == "__main__":
    print(score(random_predictor, load_open_days(), load_windows()).round(3))
