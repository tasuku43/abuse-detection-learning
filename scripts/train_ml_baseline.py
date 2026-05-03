from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from abuse_detection.ml_baseline import (
    build_ml_model_metadata,
    save_ml_model,
    split_train_validation,
    split_train_validation_by_time,
    train_ml_baseline,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Train and save the logistic-regression ML baseline."
    )
    parser.add_argument(
        "--feature-rows",
        default="fixtures/feature_rows_sample.csv",
        help="Path to labeled feature rows CSV.",
    )
    parser.add_argument(
        "--artifact-dir",
        default="models/ml_baseline_v001",
        help="Directory where model.joblib and metadata.json are saved.",
    )
    parser.add_argument(
        "--model-version",
        default="v001",
        help="Human-readable model version recorded in metadata.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=80,
        help="Threshold used for metadata precision/recall.",
    )
    parser.add_argument(
        "--validation-size",
        type=float,
        default=0.3,
        help="Fraction of rows held out for validation metadata.",
    )
    parser.add_argument(
        "--split-strategy",
        choices=["random", "time"],
        default="random",
        help="Use random stratified split or past/future time split.",
    )
    parser.add_argument(
        "--validation-start",
        default=None,
        help="Start timestamp for validation rows when --split-strategy=time.",
    )
    parser.add_argument(
        "--random-state",
        type=int,
        default=0,
        help="Random seed used for the train/validation split.",
    )
    args = parser.parse_args()

    feature_rows_path = Path(args.feature_rows)
    feature_rows = pd.read_csv(feature_rows_path)
    if args.split_strategy == "time":
        if args.validation_start is None:
            raise ValueError("--validation-start is required for --split-strategy=time")
        split = split_train_validation_by_time(
            feature_rows,
            validation_start=args.validation_start,
        )
    else:
        split = split_train_validation(
            feature_rows,
            validation_size=args.validation_size,
            random_state=args.random_state,
        )
    model = train_ml_baseline(split.train_rows)
    metadata = build_ml_model_metadata(
        split.train_rows,
        model,
        training_data_path=str(feature_rows_path),
        model_version=args.model_version,
        threshold=args.threshold,
        validation_rows=split.validation_rows,
        validation_size=args.validation_size if args.split_strategy == "random" else None,
        random_state=args.random_state if args.split_strategy == "random" else None,
    )
    metadata["split_strategy"] = args.split_strategy
    if args.validation_start is not None:
        metadata["validation_start"] = args.validation_start
    artifact = save_ml_model(model, args.artifact_dir, metadata=metadata)

    print(f"saved model: {artifact.model_path}")
    print(f"saved metadata: {artifact.metadata_path}")
    print(f"train rows: {len(split.train_rows)}")
    print(f"validation rows: {len(split.validation_rows)}")


if __name__ == "__main__":
    main()
