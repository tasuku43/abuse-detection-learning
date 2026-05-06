from datetime import datetime, timezone

import pytest

from abuse_detection.decision_policy import DecisionPolicy
from abuse_detection.production_schema import ScoreResult


def _score_result(risk_score: float) -> ScoreResult:
    now = datetime(2026, 5, 6, 10, 0, tzinfo=timezone.utc)
    return ScoreResult(
        score_result_id=f"score_result_{int(risk_score)}",
        user_id="synthetic_user_001",
        as_of_time=now,
        risk_score=risk_score,
        score_source="rule_based",
        score_version="rule_baseline_v001",
        feature_version="feature_v001",
        scored_at=now,
    )


def test_policy_decides_no_action_for_low_score() -> None:
    policy = DecisionPolicy(review_threshold=80.0, auto_action_threshold=95.0)

    decision = policy.decide(_score_result(42.0))

    assert decision.decision == "no_action"
    assert decision.dry_run is True
    assert decision.decision_policy_version == "decision_policy_v001"


def test_policy_decides_review_required_for_medium_high_score() -> None:
    policy = DecisionPolicy(review_threshold=80.0, auto_action_threshold=95.0)

    decision = policy.decide(_score_result(88.0))

    assert decision.decision == "review_required"
    assert "review_threshold" in decision.decision_reason


def test_policy_decides_auto_action_candidate_for_high_score() -> None:
    policy = DecisionPolicy(review_threshold=80.0, auto_action_threshold=95.0)

    decision = policy.decide(_score_result(98.0))

    assert decision.decision == "auto_action_candidate"
    assert "auto_action_threshold" in decision.decision_reason


def test_policy_builds_no_candidate_for_no_action() -> None:
    policy = DecisionPolicy(review_threshold=80.0, auto_action_threshold=95.0)

    candidate = policy.build_candidate(_score_result(42.0))

    assert candidate is None


def test_policy_builds_candidate_for_review_required() -> None:
    policy = DecisionPolicy(review_threshold=80.0, auto_action_threshold=95.0)
    score_result = _score_result(88.0)

    candidate = policy.build_candidate(score_result)

    assert candidate is not None
    assert candidate.score_result_id == score_result.score_result_id
    assert candidate.decision == "review_required"
    assert candidate.dry_run is True


def test_policy_can_disable_dry_run_flag() -> None:
    policy = DecisionPolicy(
        review_threshold=80.0,
        auto_action_threshold=95.0,
        dry_run=False,
    )

    decision = policy.decide(_score_result(98.0))

    assert decision.decision == "auto_action_candidate"
    assert decision.dry_run is False


def test_policy_rejects_thresholds_in_wrong_order() -> None:
    with pytest.raises(ValueError, match="review_threshold must be <= auto_action_threshold"):
        DecisionPolicy(review_threshold=95.0, auto_action_threshold=80.0)
