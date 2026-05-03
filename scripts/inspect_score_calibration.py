from __future__ import annotations

import argparse

import pandas as pd

from abuse_detection.calibration import calibration_by_score_bucket
from abuse_detection.evaluation import evaluate_feature_rows
from abuse_detection.ml_baseline import load_ml_model
from abuse_detection.scoring import scoring_fn


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Inspect observed positive rate by score bucket."
    )
    parser.add_argument(
        "--feature-rows",
        default="fixtures/feature_rows_sample.csv",
        help="Path to labeled feature rows CSV.",
    )
    parser.add_argument(
        "--score-source",
        choices=["rule", "ml"],
        default="ml",
        help="Scoring function to inspect.",
    )
    parser.add_argument(
        "--artifact-dir",
        default="models/ml_baseline_v001",
        help="Saved ML model artifact directory when --score-source=ml.",
    )
    parser.add_argument(
        "--bucket-size",
        type=int,
        default=20,
        help="Score bucket size.",
    )
    args = parser.parse_args()

    feature_rows = pd.read_csv(args.feature_rows)
    score_fn = scoring_fn
    if args.score_source == "ml":
        score_fn = load_ml_model(args.artifact_dir).score_row

    scored_rows, _ = evaluate_feature_rows(feature_rows, score_fn=score_fn)
    calibration = calibration_by_score_bucket(
        scored_rows,
        bucket_size=args.bucket_size,
    )
    print(calibration.to_string(index=False))


if __name__ == "__main__":
    main()
