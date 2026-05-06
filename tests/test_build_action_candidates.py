from datetime import datetime, timezone
from pathlib import Path

from abuse_detection.local_log_store import read_jsonl, write_jsonl_partition
from scripts.build_action_candidates import build_action_candidate_logs


def test_build_action_candidate_logs_reads_score_results_and_writes_candidates(
    tmp_path: Path,
) -> None:
    created_at = datetime(2026, 5, 6, 10, 0, tzinfo=timezone.utc)
    score_results_dir = write_jsonl_partition(
        [
            {
                "score_result_id": "score_result_001",
                "user_id": "synthetic_user_001",
                "as_of_time": "2026-05-06T10:00:00+00:00",
                "risk_score": 98.0,
                "score_source": "rule_based",
                "score_version": "rule_baseline_v001",
                "feature_version": "feature_v001",
                "scored_at": "2026-05-06T10:00:00+00:00",
            },
            {
                "score_result_id": "score_result_002",
                "user_id": "synthetic_user_002",
                "as_of_time": "2026-05-06T10:00:00+00:00",
                "risk_score": 20.0,
                "score_source": "rule_based",
                "score_version": "rule_baseline_v001",
                "feature_version": "feature_v001",
                "scored_at": "2026-05-06T10:00:00+00:00",
            },
        ],
        root_dir=tmp_path,
        dataset="score_results",
        run_id="score_run_001",
        created_at=created_at,
    )

    action_candidates_dir = build_action_candidate_logs(
        score_results_path=score_results_dir / "part-000.jsonl",
        data_lake_dir=tmp_path,
        run_id="candidate_run_001",
        created_at=created_at,
    )

    action_candidates = read_jsonl(action_candidates_dir / "part-000.jsonl")

    assert len(action_candidates) == 1
    assert action_candidates[0]["score_result_id"] == "score_result_001"
    assert action_candidates[0]["decision"] == "action_candidate"
    assert action_candidates[0]["candidate_priority"] == "high"
    assert (action_candidates_dir / "manifest.json").exists()
