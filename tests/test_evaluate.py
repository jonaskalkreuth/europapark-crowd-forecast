import pandas as pd
import pytest

from europapark_crowd import evaluate


def test_ties_at_cutoff_are_all_actual_quiet():
    # 8 days: the bottom quarter is 2 days, but B, C and D tie at the cutoff of 20.
    crowd = pd.Series([10, 20, 20, 20, 50, 60, 70, 80])
    assert evaluate.actual_quiet(crowd).tolist() == [True] * 4 + [False] * 4


def test_predicted_quiet_picks_a_quarter_when_all_tie():
    # A yes/no predictor ties on most days; it must still flag exactly n // 4.
    predicted = pd.Series([1.0] * 12)
    first = evaluate.predicted_quiet(predicted)
    assert first.sum() == 3
    assert evaluate.predicted_quiet(predicted).equals(first)


def test_predicted_quiet_picks_lowest_without_ties():
    predicted = pd.Series([50, 10, 80, 30, 70, 20, 60, 40])
    flagged = evaluate.predicted_quiet(predicted)
    assert flagged[flagged].index.tolist() == [1, 5]


def test_quiet_day_precision_known_answer():
    # Days with actual 1 to 4 are quiet; the model picks actual 1, 2, 9 and 10.
    actual = pd.Series(range(1, 17))
    predicted = actual.astype(float)
    predicted[[2, 3]] = 100
    predicted[[8, 9]] = 0
    assert evaluate.quiet_day_precision(actual, predicted) == 0.5


def test_spearman_same_and_reversed_order():
    actual = pd.Series([10, 20, 30, 40])
    assert evaluate.spearman(actual, pd.Series([1, 2, 3, 4])) == pytest.approx(1)
    assert evaluate.spearman(actual, pd.Series([4, 3, 2, 1])) == pytest.approx(-1)


def test_spearman_with_ties():
    # Ranks 1, 2, 3, 4 against 1.5, 1.5, 3, 4 correlate at sqrt(0.9).
    actual = pd.Series([10, 20, 30, 40])
    predicted = pd.Series([1, 1, 2, 3])
    assert evaluate.spearman(actual, predicted) == pytest.approx(0.9**0.5)


def test_regret_known_answer():
    # The last day is outside the window, so its actual 0 must not count.
    actual = pd.Series([30, 50, 20, 40, 0])
    predicted = pd.Series([1, 2, 3, 4, 0])
    window = pd.Series([True, True, True, True, False])
    assert evaluate.regret(actual, predicted, window) == 10


def test_regret_averages_tied_predictions():
    actual = pd.Series([30, 50, 20, 40])
    predicted = pd.Series([1, 1, 3, 4])
    window = pd.Series([True] * 4)
    assert evaluate.regret(actual, predicted, window) == 20


def test_score_passes_right_seasons_and_hides_crowd_level():
    seasons = ["summer 2019", "summer 2022", "summer 2023", "summer 2024", "summer 2025"]
    days = pd.DataFrame(
        {
            "date": [pd.Timestamp(2019 + i, 7, 1 + j) for i in range(5) for j in range(4)],
            "season": [season for season in seasons for _ in range(4)],
            "crowd_level": list(range(20)),
        }
    )
    calls = []

    def recording_predictor(train, target):
        calls.append(
            (sorted(train["season"].unique()), target["season"].iloc[0], "crowd_level" in target)
        )
        return pd.Series(range(len(target)), index=target.index, dtype=float)

    table = evaluate.score(recording_predictor, days, no_holidays())
    assert calls == [
        (seasons[:2], "summer 2023", False),
        (seasons[:3], "summer 2024", False),
        (seasons[:3], "summer 2024", False),
        (seasons[:4], "summer 2025", False),
    ]
    assert len(table) == 4


def no_holidays():
    return pd.DataFrame(columns=["window", "start", "end"])


def test_mean_regret_averages_windows():
    # Window A regrets 10 (picks 30, best 20); window B regrets 0.
    actual = pd.Series([30, 50, 20, 40])
    predicted = pd.Series([1, 2, 3, 4])
    windows = {
        "A": pd.Series([True, True, True, False]),
        "B": pd.Series([False, False, True, True]),
    }
    assert evaluate.mean_regret(actual, predicted, windows) == 5


def test_score_reports_regret_over_season_windows():
    # Each season is Monday 3 to Saturday 15 June 2024: windows "summer" and "Saturdays in June".
    dates = pd.date_range("2024-06-03", "2024-06-15")
    seasons = ["summer 2019", "summer 2022", "summer 2023", "summer 2024", "summer 2025"]
    days = pd.DataFrame(
        {
            "date": list(dates) * 5,
            "season": [season for season in seasons for _ in dates],
            "crowd_level": list(range(len(dates))) * 5,
        }
    )

    def reversed_predictor(train, target):
        # Predicts the opposite order, so it always picks the busiest day.
        return pd.Series(-target["date"].dt.day.to_numpy(), index=target.index, dtype=float)

    table = evaluate.score(reversed_predictor, days, no_holidays())
    # "summer" regrets 12 (picks 12, best 0); Saturdays 8 and 15 June regret 7 (picks 12, best 5).
    assert table["regret"].tolist() == [9.5] * 4
