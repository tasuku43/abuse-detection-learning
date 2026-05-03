from __future__ import annotations

from collections.abc import Iterable
from typing import TypedDict

import pandas as pd


class ScoringFeatureRow(TypedDict):
    """Feature values that scoring_fn is allowed to read."""

    account_age_minutes: int | float
    contacts_24h: int | float
    messages_1h: int | float
    profile_updates_24h: int | float
    plan: str


class LabeledFeatureRow(ScoringFeatureRow):
    """Feature row shape used by the evaluation harness."""

    user_id: str
    as_of_time: str
    label_value: int


REQUIRED_FEATURE_COLUMNS: tuple[str, ...] = (
    "user_id",
    "as_of_time",
    "label_value",
    "account_age_minutes",
    "contacts_24h",
    "messages_1h",
    "profile_updates_24h",
    "plan",
)


def missing_required_columns(columns: Iterable[str]) -> list[str]:
    """Return required feature columns that are absent from an input table."""
    available = set(columns)
    return [column for column in REQUIRED_FEATURE_COLUMNS if column not in available]


def validate_feature_rows(feature_rows: pd.DataFrame) -> None:
    """Validate that a feature row table has the minimum columns for evaluation."""
    missing = missing_required_columns(feature_rows.columns)
    if missing:
        raise ValueError(f"Missing required feature columns: {', '.join(missing)}")
