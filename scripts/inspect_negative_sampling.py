from __future__ import annotations

import argparse

import pandas as pd

from abuse_detection.negative_sampling import (
    NegativeSamplingConfig,
    annotate_negative_candidates,
    sample_training_rows_with_negatives,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Inspect simple negative sampling choices."
    )
    parser.add_argument(
        "--feature-rows",
        default="fixtures/feature_rows_sample.csv",
        help="Path to labeled feature rows CSV.",
    )
    args = parser.parse_args()

    feature_rows = pd.read_csv(args.feature_rows)
    config = NegativeSamplingConfig()
    annotated = annotate_negative_candidates(feature_rows, config=config)
    sampled = sample_training_rows_with_negatives(feature_rows, config=config)

    print("label counts:")
    print(feature_rows["label_value"].value_counts().sort_index().to_string())
    print()
    print("negative sampling decisions:")
    print(annotated["negative_exclusion_reason"].value_counts().to_string())
    print()
    print("sampled training label counts:")
    print(sampled["label_value"].value_counts().sort_index().to_string())
    print()
    print("selected negative examples:")
    columns = [
        "user_id",
        "label_value",
        "account_age_minutes",
        "contacts_24h",
        "messages_1h",
        "plan",
        "negative_exclusion_reason",
    ]
    print(
        annotated[annotated["negative_candidate"]][columns]
        .head(10)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
