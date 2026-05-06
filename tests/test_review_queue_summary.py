from pathlib import Path

from abuse_detection.local_log_store import write_jsonl_partition
from scripts.review_queue_summary import (
    format_summary,
    load_action_candidates,
    summarize_review_queue,
)


def _candidates() -> list[dict[str, object]]:
    return [
        {
            "action_candidate_id": "candidate_001",
            "score_result_id": "score_001",
            "user_id": "user_standard_high_score",
            "risk_score": 91.0,
            "decision": "action_candidate",
            "decision_reason": "risk_score >= candidate_threshold",
            "candidate_priority": "standard",
            "candidate_status": "open",
        },
        {
            "action_candidate_id": "candidate_002",
            "score_result_id": "score_002",
            "user_id": "user_high_priority",
            "risk_score": 96.0,
            "decision": "action_candidate",
            "decision_reason": "risk_score >= high_priority_threshold",
            "candidate_priority": "high",
            "candidate_status": "open",
        },
        {
            "action_candidate_id": "candidate_003",
            "score_result_id": "score_003",
            "user_id": "user_processed",
            "risk_score": 99.0,
            "decision": "action_candidate",
            "decision_reason": "risk_score >= high_priority_threshold",
            "candidate_priority": "high",
            "candidate_status": "processed",
        },
    ]


def test_summarize_review_queue_filters_open_candidates_and_sorts_priority_first() -> None:
    rows = summarize_review_queue(
        _candidates(),
        review_base_url="https://review.example.local/accounts",
    )

    assert [row["user_id"] for row in rows] == [
        "user_high_priority",
        "user_standard_high_score",
    ]
    assert rows[0]["review_link"] == "https://review.example.local/accounts/user_high_priority"


def test_summarize_review_queue_can_disable_status_filter() -> None:
    rows = summarize_review_queue(_candidates(), candidate_status=None)

    assert [row["user_id"] for row in rows] == [
        "user_high_priority",
        "user_processed",
        "user_standard_high_score",
    ]


def test_load_action_candidates_reads_jsonl_records(tmp_path: Path) -> None:
    output_dir = write_jsonl_partition(
        _candidates(),
        root_dir=tmp_path,
        dataset="action_candidates",
        run_id="run_001",
    )

    rows = load_action_candidates(output_dir / "part-000.jsonl")

    assert len(rows) == 3
    assert rows[0]["action_candidate_id"] == "candidate_001"


def test_format_summary_outputs_pipe_table() -> None:
    rows = summarize_review_queue(_candidates())

    output = format_summary(rows, limit=1)

    assert "user_id | risk_score | candidate_priority" in output
    assert "user_high_priority" in output
    assert "user_standard_high_score" not in output
