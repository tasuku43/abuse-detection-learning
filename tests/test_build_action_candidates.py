from datetime import datetime, timezone
from pathlib import Path

from abuse_detection.local_log_store import read_jsonl
from scripts.build_action_candidates import build_action_candidate_logs


def test_build_action_candidate_logs_writes_score_results_and_candidates(
    tmp_path: Path,
) -> None:
    scored_at = datetime(2026, 5, 6, 10, 0, tzinfo=timezone.utc)

    score_results_dir, action_candidates_dir = build_action_candidate_logs(
        data_lake_dir=tmp_path,
        run_id="run_001",
        scored_at=scored_at,
    )

    score_results = read_jsonl(score_results_dir / "part-000.jsonl")
    action_candidates = read_jsonl(action_candidates_dir / "part-000.jsonl")

    assert len(score_results) == 100
    assert len(action_candidates) > 0
    assert (score_results_dir / "manifest.json").exists()
    assert (action_candidates_dir / "manifest.json").exists()
    assert set(action_candidates[0]) >= {
        "action_candidate_id",
        "score_result_id",
        "user_id",
        "risk_score",
        "decision",
        "candidate_priority",
        "candidate_status",
    }
    assert {candidate["decision"] for candidate in action_candidates} == {"action_candidate"}
