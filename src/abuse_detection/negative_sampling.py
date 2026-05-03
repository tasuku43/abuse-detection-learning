from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from abuse_detection.schema import validate_feature_rows


@dataclass(frozen=True)
class NegativeSamplingConfig:
    """Simple rules for choosing stable negative examples."""

    min_account_age_minutes: int = 24 * 60
    max_contacts_24h: int = 80
    max_messages_1h: int = 60
    max_failed_login_count_24h: int = 5
    max_recipient_block_rate_24h: float = 0.25
    negative_to_positive_ratio: float = 1.0
    random_state: int = 0


def annotate_negative_candidates(
    feature_rows: pd.DataFrame,
    config: NegativeSamplingConfig = NegativeSamplingConfig(),
) -> pd.DataFrame:
    """Add negative sampling decision columns to labeled feature rows."""
    validate_feature_rows(feature_rows)
    annotated = feature_rows.copy()
    is_labeled_negative = annotated["label_value"] == 0

    too_new = annotated["account_age_minutes"] < config.min_account_age_minutes
    high_contact_volume = annotated["contacts_24h"] >= config.max_contacts_24h
    high_message_volume = annotated["messages_1h"] >= config.max_messages_1h
    high_failed_logins = (
        annotated["failed_login_count_24h"] >= config.max_failed_login_count_24h
    )
    high_block_rate = (
        annotated["recipient_block_rate_24h"] >= config.max_recipient_block_rate_24h
    )

    annotated["negative_candidate"] = (
        is_labeled_negative
        & ~too_new
        & ~high_contact_volume
        & ~high_message_volume
        & ~high_failed_logins
        & ~high_block_rate
    )

    annotated["negative_exclusion_reason"] = ""
    annotated.loc[~is_labeled_negative, "negative_exclusion_reason"] = "positive_label"
    annotated.loc[
        is_labeled_negative & too_new,
        "negative_exclusion_reason",
    ] = "too_new"
    annotated.loc[
        is_labeled_negative & high_contact_volume,
        "negative_exclusion_reason",
    ] = "high_contact_volume"
    annotated.loc[
        is_labeled_negative & high_message_volume,
        "negative_exclusion_reason",
    ] = "high_message_volume"
    annotated.loc[
        is_labeled_negative & high_failed_logins,
        "negative_exclusion_reason",
    ] = "high_failed_logins"
    annotated.loc[
        is_labeled_negative & high_block_rate,
        "negative_exclusion_reason",
    ] = "high_block_rate"
    annotated.loc[
        annotated["negative_candidate"],
        "negative_exclusion_reason",
    ] = "selected_candidate"

    return annotated


def sample_training_rows_with_negatives(
    feature_rows: pd.DataFrame,
    config: NegativeSamplingConfig = NegativeSamplingConfig(),
) -> pd.DataFrame:
    """Return positives plus a sampled set of stable negative candidates."""
    annotated = annotate_negative_candidates(feature_rows, config=config)
    positives = annotated[annotated["label_value"] == 1]
    negative_candidates = annotated[annotated["negative_candidate"]]
    target_negative_count = min(
        len(negative_candidates),
        int(round(len(positives) * config.negative_to_positive_ratio)),
    )
    sampled_negatives = negative_candidates.sample(
        n=target_negative_count,
        random_state=config.random_state,
    )
    return (
        pd.concat([positives, sampled_negatives])
        .sample(frac=1.0, random_state=config.random_state)
        .reset_index(drop=True)
    )
