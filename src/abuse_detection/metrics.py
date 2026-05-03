from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class ClassificationMetrics:
    threshold: float
    precision: float
    recall: float
    tp: int
    fp: int
    fn: int


def precision_recall_at_threshold(
    labels: pd.Series,
    scores: pd.Series,
    threshold: float,
) -> ClassificationMetrics:
    """Calculate precision and recall for one threshold."""
    predicted_abuse = scores >= threshold
    actual_abuse = labels.astype(bool)

    tp = int((predicted_abuse & actual_abuse).sum())
    fp = int((predicted_abuse & ~actual_abuse).sum())
    fn = int((~predicted_abuse & actual_abuse).sum())

    precision = tp / (tp + fp) if tp + fp > 0 else 0.0
    recall = tp / (tp + fn) if tp + fn > 0 else 0.0

    return ClassificationMetrics(
        threshold=threshold,
        precision=precision,
        recall=recall,
        tp=tp,
        fp=fp,
        fn=fn,
    )


def threshold_sweep(
    labels: pd.Series,
    scores: pd.Series,
    thresholds: list[float],
) -> pd.DataFrame:
    """Calculate metrics for multiple thresholds."""
    rows = [
        precision_recall_at_threshold(labels, scores, threshold).__dict__
        for threshold in thresholds
    ]
    return pd.DataFrame(rows)

