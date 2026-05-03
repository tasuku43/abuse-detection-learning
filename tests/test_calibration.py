import pandas as pd
import pytest

from abuse_detection.calibration import calibration_by_score_bucket


def test_calibration_by_score_bucket_compares_score_to_positive_rate() -> None:
    scored_rows = pd.DataFrame(
        {
            "label_value": [0, 1, 1, 1],
            "risk_score": [10, 30, 70, 90],
        }
    )

    summary = calibration_by_score_bucket(scored_rows, bucket_size=50)

    assert list(summary["score_bucket_start"]) == [0, 50]
    assert list(summary["row_count"]) == [2, 2]
    assert list(summary["positive_count"]) == [1, 2]
    assert list(summary["positive_rate"]) == [0.5, 1.0]
    assert list(summary["average_score_probability"].round(2)) == [0.2, 0.8]


def test_calibration_by_score_bucket_rejects_missing_columns() -> None:
    with pytest.raises(ValueError, match="Missing scored row columns"):
        calibration_by_score_bucket(pd.DataFrame({"label_value": [1]}))


def test_calibration_by_score_bucket_rejects_bad_bucket_size() -> None:
    with pytest.raises(ValueError, match="bucket_size"):
        calibration_by_score_bucket(
            pd.DataFrame({"label_value": [1], "risk_score": [90]}),
            bucket_size=30,
        )
