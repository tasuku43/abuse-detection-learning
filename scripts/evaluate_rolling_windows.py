from __future__ import annotations

import argparse

import pandas as pd

from abuse_detection.evaluation import evaluate_feature_rows
from abuse_detection.ml_baseline import load_ml_model
from abuse_detection.rolling_window import rolling_window_metrics
from abuse_detection.scoring import scoring_fn


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate precision/recall by as_of_time window."
    )
    parser.add_argument(
        "--feature-rows",
        default="fixtures/feature_rows_sample.csv",
        help="Path to labeled feature rows CSV.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=80,
        help="Threshold used for each window.",
    )
    parser.add_argument(
        "--window",
        default="7D",
        help="Pandas time window such as 1D, 7D, or 30D.",
    )
    parser.add_argument(
        "--score-source",
        choices=["rule", "ml"],
        default="ml",
        help="Scoring function used before window metrics.",
    )
    parser.add_argument(
        "--artifact-dir",
        default="models/ml_baseline_v001",
        help="Saved ML model artifact directory when --score-source=ml.",
    )
    args = parser.parse_args()

    feature_rows = pd.read_csv(args.feature_rows)
    score_fn = scoring_fn
    if args.score_source == "ml":
        score_fn = load_ml_model(args.artifact_dir).score_row

    scored_rows, _ = evaluate_feature_rows(
        feature_rows,
        thresholds=[args.threshold],
        score_fn=score_fn,
    )
    metrics = rolling_window_metrics(
        scored_rows,
        threshold=args.threshold,
        window=args.window,
    )
    print(metrics.to_string(index=False))


if __name__ == "__main__":
    main()
