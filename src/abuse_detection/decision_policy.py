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

    review_threshold: float = 80.0
    auto_action_threshold: float = 95.0
    version: str = "decision_policy_v001"
    dry_run: bool = True

    def __post_init__(self) -> None:
        if not 0.0 <= self.review_threshold <= 100.0:
            raise ValueError("review_threshold must be between 0 and 100")
        if not 0.0 <= self.auto_action_threshold <= 100.0:
            raise ValueError("auto_action_threshold must be between 0 and 100")
        if self.review_threshold > self.auto_action_threshold:
            raise ValueError("review_threshold must be <= auto_action_threshold")

    def decide(self, score_result: ScoreResult) -> DecisionResult:
        """Return the policy decision for one score result."""
        if score_result.risk_score >= self.auto_action_threshold:
            return DecisionResult(
                decision="auto_action_candidate",
                decision_reason=(
                    f"risk_score >= auto_action_threshold "
                    f"({score_result.risk_score:.1f} >= {self.auto_action_threshold:.1f})"
                ),
                decision_policy_version=self.version,
                dry_run=self.dry_run,
            )
        if score_result.risk_score >= self.review_threshold:
            return DecisionResult(
                decision="review_required",
                decision_reason=(
                    f"risk_score >= review_threshold "
                    f"({score_result.risk_score:.1f} >= {self.review_threshold:.1f})"
                ),
                decision_policy_version=self.version,
                dry_run=self.dry_run,
            )
        return DecisionResult(
            decision="no_action",
            decision_reason=(
                f"risk_score < review_threshold "
                f"({score_result.risk_score:.1f} < {self.review_threshold:.1f})"
            ),
            decision_policy_version=self.version,
            dry_run=self.dry_run,
        )

    def build_candidate(self, score_result: ScoreResult) -> ActionCandidate | None:
        """Create an ActionCandidate unless the policy decides no_action."""
        decision_result = self.decide(score_result)
        if decision_result.decision == "no_action":
            return None
        return build_action_candidate(score_result, decision_result)
