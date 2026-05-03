import pandas as pd
import pytest

from abuse_detection.error_analysis import (
    false_negatives,
    false_positives,
    score_bucket_summary,
)


def test_false_positive_and_false_negative_helpers_return_expected_rows() -> None:
    scored_rows = pd.DataFrame(
        {
            "user_id": ["positive_hit", "negative_miss", "negative_fp", "positive_fn"],
            "label_value": [1, 0, 0, 1],
            "risk_score": [95, 10, 85, 40],
        }
    )

    fps = false_positives(scored_rows, threshold=80)
    fns = false_negatives(scored_rows, threshold=80)

    assert list(fps["user_id"]) == ["negative_fp"]
    assert list(fns["user_id"]) == ["positive_fn"]


def test_score_bucket_summary_counts_labels_and_errors() -> None:
    scored_rows = pd.DataFrame(
        {
            "label_value": [0, 1, 0, 1, 1],
            "risk_score": [5, 25, 45, 85, 100],
        }
    )

    summary = score_bucket_summary(scored_rows, bucket_size=20, threshold=80)

    assert list(summary["score_bucket_start"]) == [0, 20, 40, 80]
    assert list(summary["score_bucket_end"]) == [20, 40, 60, 100]
    assert list(summary["row_count"]) == [1, 1, 1, 2]
    assert list(summary["positive_count"]) == [0, 1, 0, 2]
    assert list(summary["negative_count"]) == [1, 0, 1, 0]
    assert list(summary["false_positive_count"]) == [0, 0, 0, 0]
    assert list(summary["false_negative_count"]) == [0, 1, 0, 0]


def test_score_bucket_summary_rejects_invalid_bucket_size() -> None:
    scored_rows = pd.DataFrame({"label_value": [1], "risk_score": [80]})

    with pytest.raises(ValueError, match="positive divisor of 100"):
        score_bucket_summary(scored_rows, bucket_size=30)


def test_error_analysis_rejects_unscored_rows() -> None:
    with pytest.raises(ValueError, match="Missing scored row columns"):
        false_positives(pd.DataFrame({"label_value": [0]}), threshold=80)
