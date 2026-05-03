import pandas as pd
import pytest

from abuse_detection.evaluation import evaluate_feature_rows
from abuse_detection.rolling_window import rolling_window_metrics
from abuse_detection.scoring import scoring_fn


def test_rolling_window_metrics_calculates_metrics_per_window() -> None:
    scored_rows = pd.DataFrame(
        {
            "as_of_time": [
                "2026-05-01T10:00:00Z",
                "2026-05-01T11:00:00Z",
                "2026-05-08T10:00:00Z",
                "2026-05-08T11:00:00Z",
            ],
            "label_value": [1, 0, 1, 0],
            "risk_score": [90, 70, 40, 30],
        }
    )

    metrics = rolling_window_metrics(scored_rows, threshold=80, window="7D")

    assert list(metrics["row_count"]) == [2, 2]
    assert list(metrics["tp"]) == [1, 0]
    assert list(metrics["fn"]) == [0, 1]
    assert list(metrics["precision"]) == [1.0, 0.0]
    assert list(metrics["recall"]) == [1.0, 0.0]


def test_rolling_window_metrics_rejects_missing_columns() -> None:
    with pytest.raises(ValueError, match="Missing scored row columns"):
        rolling_window_metrics(pd.DataFrame({"label_value": [1]}), threshold=80)


def test_timeseries_fixture_has_multiple_rolling_windows() -> None:
    feature_rows = pd.read_csv("fixtures/feature_rows_timeseries.csv")
    scored_rows = feature_rows.assign(risk_score=feature_rows["label_value"] * 100)

    metrics = rolling_window_metrics(scored_rows, threshold=80, window="7D")

    assert len(metrics) == 4
    assert list(metrics["row_count"]) == [100, 100, 100, 100]


def test_timeseries_fixture_reveals_late_window_precision_drop() -> None:
    feature_rows = pd.read_csv("fixtures/feature_rows_timeseries.csv")
    scored_rows, _ = evaluate_feature_rows(
        feature_rows,
        thresholds=[80],
        score_fn=scoring_fn,
    )

    metrics = rolling_window_metrics(scored_rows, threshold=80, window="7D")

    assert metrics.iloc[-1]["fp"] > metrics.iloc[0]["fp"]
    assert metrics.iloc[-1]["precision"] < metrics.iloc[0]["precision"]
