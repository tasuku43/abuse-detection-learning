from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4


Decision = Literal["no_action", "action_candidate"]
CandidatePriority = Literal["standard", "high"]
CandidateStatus = Literal["open", "skipped", "processed"]


@dataclass(frozen=True)
class ScoreResult:
    """Append-only score history produced by a scorer."""

    score_result_id: str
    user_id: str
    as_of_time: datetime
    risk_score: float
    score_source: str
    score_version: str
    feature_version: str
    scored_at: datetime

    def __post_init__(self) -> None:
        if not 0.0 <= self.risk_score <= 100.0:
            raise ValueError("risk_score must be between 0 and 100")


@dataclass(frozen=True)
class DecisionResult:
    """Decision Policy output for one ScoreResult."""

    decision: Decision
    decision_reason: str
    decision_policy_version: str
    candidate_priority: CandidatePriority | None = None


@dataclass(frozen=True)
class ActionCandidate:
    """Follow-up candidate created from a ScoreResult and a decision."""

    action_candidate_id: str
    score_result_id: str
    user_id: str
    as_of_time: datetime
    risk_score: float
    decision: Decision
    decision_reason: str
    decision_policy_version: str
    candidate_priority: CandidatePriority
    score_source: str
    score_version: str
    feature_version: str
    candidate_status: CandidateStatus
    created_at: datetime


def utc_now() -> datetime:
    """Return a timezone-aware timestamp for local simulation records."""
    return datetime.now(timezone.utc)


def new_id(prefix: str) -> str:
    """Create a compact synthetic id for toy append-only records."""
    return f"{prefix}_{uuid4().hex}"


def build_action_candidate(
    score_result: ScoreResult,
    decision_result: DecisionResult,
    created_at: datetime | None = None,
) -> ActionCandidate:
    """Create an ActionCandidate from score and policy outputs."""
    if decision_result.decision != "action_candidate":
        raise ValueError("ActionCandidate can only be built from action_candidate decisions")
    if decision_result.candidate_priority is None:
        raise ValueError("action_candidate decisions must include candidate_priority")
    return ActionCandidate(
        action_candidate_id=new_id("action_candidate"),
        score_result_id=score_result.score_result_id,
        user_id=score_result.user_id,
        as_of_time=score_result.as_of_time,
        risk_score=score_result.risk_score,
        decision=decision_result.decision,
        decision_reason=decision_result.decision_reason,
        decision_policy_version=decision_result.decision_policy_version,
        candidate_priority=decision_result.candidate_priority,
        score_source=score_result.score_source,
        score_version=score_result.score_version,
        feature_version=score_result.feature_version,
        candidate_status="open",
        created_at=created_at or utc_now(),
    )
