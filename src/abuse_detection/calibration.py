from __future__ import annotations

import pandas as pd


REQUIRED_CALIBRATION_COLUMNS: tuple[str, ...] = ("label_value", "risk_score")


def calibration_by_score_bucket(
    scored_rows: pd.DataFrame,
    *,
    bucket_size: int = 20,
) -> pd.DataFrame:
    """Compare average score probability with observed positive rate by bucket."""
    missing = [
        column
        for column in REQUIRED_CALIBRATION_COLUMNS
        if column not in scored_rows.columns
    ]
    if missing:
        raise ValueError(f"Missing scored row columns: {', '.join(missing)}")
    if bucket_size <= 0 or 100 % bucket_size != 0:
        raise ValueError("bucket_size must be a positive divisor of 100")

    bucketed = scored_rows.copy()
    bucketed["score_bucket_start"] = (
        (bucketed["risk_score"].clip(lower=0, upper=100) // bucket_size)
        * bucket_size
    ).astype(int)
    bucketed.loc[bucketed["score_bucket_start"] == 100, "score_bucket_start"] = (
        100 - bucket_size
    )
    bucketed["score_bucket_end"] = bucketed["score_bucket_start"] + bucket_size

    summary = (
        bucketed.groupby(["score_bucket_start", "score_bucket_end"], as_index=False)
        .agg(
            row_count=("label_value", "size"),
            positive_count=("label_value", "sum"),
            average_score=("risk_score", "mean"),
        )
        .sort_values("score_bucket_start")
        .reset_index(drop=True)
    )
    summary["positive_rate"] = summary["positive_count"] / summary["row_count"]
    summary["average_score_probability"] = summary["average_score"] / 100.0
    summary["calibration_gap"] = (
        summary["average_score_probability"] - summary["positive_rate"]
    )
    return summary[
        [
            "score_bucket_start",
            "score_bucket_end",
            "row_count",
            "positive_count",
            "positive_rate",
            "average_score",
            "average_score_probability",
            "calibration_gap",
        ]
    ]
