from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from abuse_detection.decision_policy import DecisionPolicy
from abuse_detection.local_log_store import read_jsonl, write_jsonl_partition
from abuse_detection.production_schema import ScoreResult, new_id


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DATA_LAKE_DIR = ROOT_DIR / "data_lake"


def score_result_from_record(record: dict[str, object]) -> ScoreResult:
    """Convert a persisted score_result JSON record back into a ScoreResult."""
    return ScoreResult(
        score_result_id=str(record["score_result_id"]),
        user_id=str(record["user_id"]),
        as_of_time=datetime.fromisoformat(str(record["as_of_time"])),
        risk_score=float(record["risk_score"]),
        score_source=str(record["score_source"]),
        score_version=str(record["score_version"]),
        feature_version=str(record["feature_version"]),
        scored_at=datetime.fromisoformat(str(record["scored_at"])),
    )


def build_action_candidate_logs(
    score_results_path: Path,
    data_lake_dir: Path = DEFAULT_DATA_LAKE_DIR,
    run_id: str | None = None,
    created_at: datetime | None = None,
    policy: DecisionPolicy | None = None,
) -> Path:
    """Build action_candidates JSONL partition from score_results JSONL."""
    effective_created_at = created_at or datetime.now(timezone.utc)
    effective_run_id = run_id or new_id("run")
    effective_policy = policy or DecisionPolicy()

    score_results = [
        score_result_from_record(record)
        for record in read_jsonl(score_results_path)
    ]
    action_candidates = [
        candidate
        for score_result in score_results
        if (candidate := effective_policy.build_candidate(score_result)) is not None
    ]
    return write_jsonl_partition(
        action_candidates,
        root_dir=data_lake_dir,
        dataset="action_candidates",
        run_id=effective_run_id,
        created_at=effective_created_at,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build local action_candidates JSONL logs from score_results."
    )
    parser.add_argument(
        "score_results_path",
        type=Path,
        help="Path to score_results part-000.jsonl.",
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

    action_candidates_dir = build_action_candidate_logs(
        score_results_path=args.score_results_path,
        data_lake_dir=args.data_lake_dir,
        run_id=args.run_id,
    )
    print(f"action_candidates: {action_candidates_dir}")


if __name__ == "__main__":
    main()
