from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from abuse_detection.evaluation import evaluate_feature_rows
from abuse_detection.evaluation import ScoreSource
from abuse_detection.ml_baseline import load_ml_model, load_ml_model_metadata


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate a saved ML baseline artifact."
    )
    parser.add_argument(
        "--feature-rows",
        default="fixtures/feature_rows_sample.csv",
        help="Path to labeled feature rows CSV.",
    )
    parser.add_argument(
        "--artifact-dir",
        default="models/ml_baseline_v001",
        help="Directory containing model.joblib and metadata.json.",
    )
    parser.add_argument(
        "--validation-only",
        action="store_true",
        help="Evaluate the same deterministic validation split used by the training script.",
    )
    args = parser.parse_args()

    artifact_dir = Path(args.artifact_dir)
    model = load_ml_model(artifact_dir)
    metadata = load_ml_model_metadata(artifact_dir)
    feature_rows = pd.read_csv(args.feature_rows)
    if args.validation_only:
        from abuse_detection.ml_baseline import split_train_validation

        split = split_train_validation(feature_rows)
        feature_rows = split.validation_rows
    score_source = ScoreSource(
        name=str(metadata.get("model_name", "unknown_model")),
        version=str(metadata.get("model_version", "unknown_version")),
    )
    scored_rows, metrics = evaluate_feature_rows(
        feature_rows,
        score_fn=model.score_row,
        score_source=score_source,
    )

    metadata_path = artifact_dir / "metadata.json"
    if metadata_path.exists():
        print(
            "model:",
            metadata.get("model_name"),
            metadata.get("model_version"),
        )

    print(metrics.to_string(index=False))
    print()
    print(scored_rows[["user_id", "label_value", "risk_score"]].head().to_string(index=False))


if __name__ == "__main__":
    main()
