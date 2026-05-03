import pandas as pd
import pytest

from abuse_detection.evaluation import (
    add_risk_scores,
    evaluate_feature_rows,
    false_negatives,
    false_positives,
    load_feature_rows,
)


def test_evaluation_pipeline_returns_scored_rows_and_metrics() -> None:
    feature_rows = pd.read_csv("fixtures/feature_rows_sample.csv")

    scored_rows, metrics = evaluate_feature_rows(feature_rows, thresholds=[50, 80])

    assert "risk_score" in scored_rows.columns
    assert list(metrics["threshold"]) == [50, 80]
    assert set(metrics.columns) == {"threshold", "precision", "recall", "tp", "fp", "fn"}


def test_load_feature_rows_validates_required_columns() -> None:
    feature_rows = load_feature_rows("fixtures/feature_rows_sample.csv")

    assert len(feature_rows) == 100


def test_add_risk_scores_rejects_missing_required_columns() -> None:
    with pytest.raises(ValueError, match="Missing required feature columns"):
        add_risk_scores(pd.DataFrame({"user_id": ["synthetic_user"]}))


def test_error_analysis_helpers_return_expected_rows() -> None:
    feature_rows = pd.read_csv("fixtures/feature_rows_sample.csv")
    scored_rows, _ = evaluate_feature_rows(feature_rows, thresholds=[80])

    fps = false_positives(scored_rows, threshold=80)
    fns = false_negatives(scored_rows, threshold=80)

    assert len(fps) > 0
    assert len(fns) > 0
    assert set(fps["label_value"]) == {0}
    assert set(fns["label_value"]) == {1}
