from datetime import datetime, timezone

import pytest

from abuse_detection.production_schema import (
    DecisionResult,
    ScoreResult,
    build_action_candidate,
)


def _score_result(risk_score: float = 91.0) -> ScoreResult:
    now = datetime(2026, 5, 6, 10, 0, tzinfo=timezone.utc)
    return ScoreResult(
        score_result_id="score_result_001",
        user_id="synthetic_user_001",
        as_of_time=now,
        risk_score=risk_score,
        score_source="rule_based",
        score_version="rule_baseline_v001",
        feature_version="feature_v001",
        scored_at=now,
    )


def test_score_result_accepts_valid_score() -> None:
    score_result = _score_result(risk_score=80.0)

    assert score_result.risk_score == 80.0
    assert score_result.score_source == "rule_based"


def test_score_result_rejects_score_outside_zero_to_one_hundred() -> None:
    with pytest.raises(ValueError, match="risk_score must be between 0 and 100"):
        _score_result(risk_score=101.0)


def test_build_action_candidate_copies_score_and_decision_context() -> None:
    score_result = _score_result(risk_score=91.0)
    decision_result = DecisionResult(
        decision="review_required",
        decision_reason="risk_score >= review_threshold",
        decision_policy_version="decision_policy_v001",
        dry_run=True,
    )
    created_at = datetime(2026, 5, 6, 10, 5, tzinfo=timezone.utc)

    candidate = build_action_candidate(
        score_result,
        decision_result,
        created_at=created_at,
    )

    assert candidate.action_candidate_id.startswith("action_candidate_")
    assert candidate.score_result_id == score_result.score_result_id
    assert candidate.user_id == score_result.user_id
    assert candidate.risk_score == 91.0
    assert candidate.decision == "review_required"
    assert candidate.candidate_status == "open"
    assert candidate.dry_run is True
    assert candidate.created_at == created_at
