import pandas as pd

from abuse_detection.metrics import precision_recall_at_threshold, threshold_sweep


def test_precision_recall_at_threshold_matches_known_example() -> None:
    labels = pd.Series([1, 0, 1, 0])
    scores = pd.Series([90, 80, 30, 10])

    metrics = precision_recall_at_threshold(labels, scores, threshold=50)

    assert metrics.tp == 1
    assert metrics.fp == 1
    assert metrics.fn == 1
    assert metrics.precision == 0.5
    assert metrics.recall == 0.5


def test_threshold_sweep_returns_one_row_per_threshold() -> None:
    labels = pd.Series([1, 0])
    scores = pd.Series([90, 10])

    metrics = threshold_sweep(labels, scores, thresholds=[0, 50, 100])

    assert list(metrics["threshold"]) == [0, 50, 100]
    assert list(metrics.columns) == ["threshold", "precision", "recall", "tp", "fp", "fn"]

