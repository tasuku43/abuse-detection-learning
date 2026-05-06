from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from abuse_detection.decision_policy import DecisionPolicy
from abuse_detection.evaluation import ScoreSource, add_risk_scores
from abuse_detection.local_log_store import write_jsonl_partition
from abuse_detection.production_schema import ScoreResult, new_id
from abuse_detection.scoring import SCORING_FN_VERSION


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_FEATURE_ROWS_PATH = ROOT_DIR / "fixtures" / "feature_rows_sample.csv"
DEFAULT_DATA_LAKE_DIR = ROOT_DIR / "data_lake"
DEFAULT_FEATURE_VERSION = "feature_v001"


def score_results_from_feature_rows(
    feature_rows: pd.DataFrame,
    scored_at: datetime,
) -> list[ScoreResult]:
    """Score feature rows and convert them to ScoreResult records."""
    scored_rows = add_risk_scores(
        feature_rows,
        score_source=ScoreSource(name="rule_based", version=SCORING_FN_VERSION),
    )
    score_results: list[ScoreResult] = []
    for row in scored_rows.to_dict(orient="records"):
        score_results.append(
            ScoreResult(
                score_result_id=new_id("score_result"),
                user_id=str(row["user_id"]),
                as_of_time=pd.Timestamp(row["as_of_time"]).to_pydatetime(),
                risk_score=float(row["risk_score"]),
                score_source=str(row["score_source"]),
                score_version=str(row["score_version"]),
                feature_version=DEFAULT_FEATURE_VERSION,
                scored_at=scored_at,
            )
        )
    return score_results


def build_action_candidate_logs(
    feature_rows_path: Path = DEFAULT_FEATURE_ROWS_PATH,
    data_lake_dir: Path = DEFAULT_DATA_LAKE_DIR,
    run_id: str | None = None,
    scored_at: datetime | None = None,
    policy: DecisionPolicy | None = None,
) -> tuple[Path, Path]:
    """Build score_results and action_candidates JSONL partitions."""
    effective_scored_at = scored_at or datetime.now(timezone.utc)
    effective_run_id = run_id or new_id("run")
    effective_policy = policy or DecisionPolicy()

    feature_rows = pd.read_csv(feature_rows_path)
    score_results = score_results_from_feature_rows(feature_rows, scored_at=effective_scored_at)
    action_candidates = [
        candidate
        for score_result in score_results
        if (candidate := effective_policy.build_candidate(score_result)) is not None
    ]

    score_results_dir = write_jsonl_partition(
        score_results,
        root_dir=data_lake_dir,
        dataset="score_results",
        run_id=effective_run_id,
        created_at=effective_scored_at,
    )
    action_candidates_dir = write_jsonl_partition(
        action_candidates,
        root_dir=data_lake_dir,
        dataset="action_candidates",
        run_id=effective_run_id,
        created_at=effective_scored_at,
    )
    return score_results_dir, action_candidates_dir


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build local score_results and action_candidates JSONL logs."
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

    score_results_dir, action_candidates_dir = build_action_candidate_logs(
        feature_rows_path=args.feature_rows,
        data_lake_dir=args.data_lake_dir,
        run_id=args.run_id,
    )
    print(f"score_results: {score_results_dir}")
    print(f"action_candidates: {action_candidates_dir}")


if __name__ == "__main__":
    main()
