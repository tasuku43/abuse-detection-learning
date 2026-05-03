from __future__ import annotations

import pandas as pd


REQUIRED_ERROR_ANALYSIS_COLUMNS: tuple[str, ...] = ("label_value", "risk_score")


def _validate_scored_rows(scored_rows: pd.DataFrame) -> None:
    missing = [
        column
        for column in REQUIRED_ERROR_ANALYSIS_COLUMNS
        if column not in scored_rows.columns
    ]
    if missing:
        raise ValueError(f"Missing scored row columns: {', '.join(missing)}")


def false_positives(scored_rows: pd.DataFrame, threshold: float) -> pd.DataFrame:
    """Return rows predicted as abuse while the label is negative."""
    _validate_scored_rows(scored_rows)
    predicted_abuse = scored_rows["risk_score"] >= threshold
    actual_negative = scored_rows["label_value"] == 0
    return scored_rows[predicted_abuse & actual_negative].copy()


def false_negatives(scored_rows: pd.DataFrame, threshold: float) -> pd.DataFrame:
    """Return rows predicted as non-abuse while the label is positive."""
    _validate_scored_rows(scored_rows)
    predicted_non_abuse = scored_rows["risk_score"] < threshold
    actual_positive = scored_rows["label_value"] == 1
    return scored_rows[predicted_non_abuse & actual_positive].copy()


def score_bucket_summary(
    scored_rows: pd.DataFrame,
    bucket_size: int = 20,
    threshold: float | None = None,
) -> pd.DataFrame:
    """Summarize labels and optional errors by score bucket."""
    _validate_scored_rows(scored_rows)
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
    summary["negative_count"] = summary["row_count"] - summary["positive_count"]
    summary = summary[
        [
            "score_bucket_start",
            "score_bucket_end",
            "row_count",
            "positive_count",
            "negative_count",
            "average_score",
        ]
    ]

    if threshold is None:
        return summary

    bucketed["is_false_positive"] = (
        (bucketed["risk_score"] >= threshold) & (bucketed["label_value"] == 0)
    )
    bucketed["is_false_negative"] = (
        (bucketed["risk_score"] < threshold) & (bucketed["label_value"] == 1)
    )
    errors = (
        bucketed.groupby(["score_bucket_start", "score_bucket_end"], as_index=False)
        .agg(
            false_positive_count=("is_false_positive", "sum"),
            false_negative_count=("is_false_negative", "sum"),
        )
        .sort_values("score_bucket_start")
        .reset_index(drop=True)
    )
    return summary.merge(errors, on=["score_bucket_start", "score_bucket_end"])
