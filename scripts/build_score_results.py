from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from abuse_detection.local_log_store import write_jsonl_partition
from abuse_detection.scoring_api import request_from_feature_row, score_request
from abuse_detection.production_schema import ScoreResult, new_id


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_FEATURE_ROWS_PATH = ROOT_DIR / "fixtures" / "feature_rows_sample.csv"
DEFAULT_DATA_LAKE_DIR = ROOT_DIR / "data_lake"


def score_results_from_feature_rows(
    feature_rows: pd.DataFrame,
    scored_at: datetime,
) -> list[ScoreResult]:
    """Call the local Scoring API implementation for each feature row."""
    score_results: list[ScoreResult] = []
    for row in feature_rows.to_dict(orient="records"):
        request = request_from_feature_row(row)
        score_results.append(score_request(request, scored_at=scored_at))
    return score_results


def build_score_result_logs(
    feature_rows_path: Path = DEFAULT_FEATURE_ROWS_PATH,
    data_lake_dir: Path = DEFAULT_DATA_LAKE_DIR,
    run_id: str | None = None,
    scored_at: datetime | None = None,
) -> Path:
    """Build score_results JSONL partition through the Scoring API boundary."""
    effective_scored_at = scored_at or datetime.now(timezone.utc)
    effective_run_id = run_id or new_id("run")

    feature_rows = pd.read_csv(feature_rows_path)
    score_results = score_results_from_feature_rows(feature_rows, scored_at=effective_scored_at)
    return write_jsonl_partition(
        score_results,
        root_dir=data_lake_dir,
        dataset="score_results",
        run_id=effective_run_id,
        created_at=effective_scored_at,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build local score_results JSONL logs through the Scoring API."
    )
    parser.add_argument(
        "--feature-rows",
        type=Path,
        default=DEFAULT_FEATURE_ROWS_PATH,
        help="Path to labeled feature rows CSV.",
    )
    parser.add_argument(
        "--data-lake-dir",
        type=Path,
        default=DEFAULT_DATA_LAKE_DIR,
        help="Local output directory for append-only logs.",
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Optional run id. Defaults to a generated id.",
    )
    args = parser.parse_args()

    score_results_dir = build_score_result_logs(
        feature_rows_path=args.feature_rows,
        data_lake_dir=args.data_lake_dir,
        run_id=args.run_id,
    )
    print(f"score_results: {score_results_dir}")


if __name__ == "__main__":
    main()
