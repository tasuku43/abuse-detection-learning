from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

import pandas as pd

from abuse_detection.error_analysis import false_negatives, false_positives
from abuse_detection.metrics import threshold_sweep
from abuse_detection.schema import ScoringFeatureRow, validate_feature_rows
from abuse_detection.scoring import scoring_fn


DEFAULT_THRESHOLDS: tuple[float, ...] = tuple(range(0, 101, 10))


@dataclass(frozen=True)
class ScoreSource:
    """Human-readable identity for a scoring function or model."""

    name: str
    version: str


def add_risk_scores(
    feature_rows: pd.DataFrame,
    score_fn: Callable[[ScoringFeatureRow], float] = scoring_fn,
    score_source: ScoreSource | None = None,
) -> pd.DataFrame:
    """Return feature rows with a risk_score column added."""
    validate_feature_rows(feature_rows)
    scored = feature_rows.copy()
    scored["risk_score"] = scored.apply(lambda row: score_fn(row.to_dict()), axis=1)
    if score_source is not None:
        scored["score_source"] = score_source.name
        scored["score_version"] = score_source.version
    return scored


def evaluate_feature_rows(
    feature_rows: pd.DataFrame,
    thresholds: Sequence[float] = DEFAULT_THRESHOLDS,
    score_fn: Callable[[ScoringFeatureRow], float] = scoring_fn,
    score_source: ScoreSource | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Score feature rows and return the scored rows plus threshold metrics."""
    scored = add_risk_scores(
        feature_rows,
        score_fn=score_fn,
        score_source=score_source,
    )
    metrics = threshold_sweep(
        labels=scored["label_value"],
        scores=scored["risk_score"],
        thresholds=list(thresholds),
    )
    if score_source is not None:
        metrics["score_source"] = score_source.name
        metrics["score_version"] = score_source.version
    return scored, metrics


def load_feature_rows(path: str) -> pd.DataFrame:
    """Load feature rows from a CSV file and validate the required columns."""
    feature_rows = pd.read_csv(path)
    validate_feature_rows(feature_rows)
    return feature_rows
