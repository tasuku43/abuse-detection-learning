from __future__ import annotations

from dataclasses import dataclass

from abuse_detection.production_schema import (
    ActionCandidate,
    DecisionResult,
    ScoreResult,
    build_action_candidate,
)


@dataclass(frozen=True)
class DecisionPolicy:
    """Toy policy that turns ScoreResult records into action candidates."""

    candidate_threshold: float = 80.0
    high_priority_threshold: float = 95.0
    version: str = "decision_policy_v001"

    def __post_init__(self) -> None:
        if not 0.0 <= self.candidate_threshold <= 100.0:
            raise ValueError("candidate_threshold must be between 0 and 100")
        if not 0.0 <= self.high_priority_threshold <= 100.0:
            raise ValueError("high_priority_threshold must be between 0 and 100")
        if self.candidate_threshold > self.high_priority_threshold:
            raise ValueError("candidate_threshold must be <= high_priority_threshold")

    def decide(self, score_result: ScoreResult) -> DecisionResult:
        """Return the policy decision for one score result."""
        if score_result.risk_score >= self.high_priority_threshold:
            return DecisionResult(
                decision="action_candidate",
                decision_reason=(
                    f"risk_score >= high_priority_threshold "
                    f"({score_result.risk_score:.1f} >= {self.high_priority_threshold:.1f})"
                ),
                decision_policy_version=self.version,
                candidate_priority="high",
            )
        if score_result.risk_score >= self.candidate_threshold:
            return DecisionResult(
                decision="action_candidate",
                decision_reason=(
                    f"risk_score >= candidate_threshold "
                    f"({score_result.risk_score:.1f} >= {self.candidate_threshold:.1f})"
                ),
                decision_policy_version=self.version,
                candidate_priority="standard",
            )
        return DecisionResult(
            decision="no_action",
            decision_reason=(
                f"risk_score < candidate_threshold "
                f"({score_result.risk_score:.1f} < {self.candidate_threshold:.1f})"
            ),
            decision_policy_version=self.version,
        )

    def build_candidate(self, score_result: ScoreResult) -> ActionCandidate | None:
        """Create an ActionCandidate unless the policy decides no_action."""
        decision_result = self.decide(score_result)
        if decision_result.decision == "no_action":
            return None
        return build_action_candidate(score_result, decision_result)
