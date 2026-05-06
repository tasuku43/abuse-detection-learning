from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from abuse_detection.local_log_store import read_jsonl


DEFAULT_REVIEW_BASE_URL = "https://review.example.local/users"
DISPLAY_COLUMNS: tuple[str, ...] = (
    "user_id",
    "risk_score",
    "candidate_priority",
    "decision",
    "candidate_status",
    "decision_reason",
    "review_link",
)


def review_link(user_id: str, base_url: str = DEFAULT_REVIEW_BASE_URL) -> str:
    """Build a placeholder link to an external review surface."""
    return f"{base_url.rstrip('/')}/{user_id}"


def load_action_candidates(path: Path) -> list[dict[str, Any]]:
    """Load action candidate JSONL records."""
    return read_jsonl(path)


def summarize_review_queue(
    candidates: list[dict[str, Any]],
    decision: str | None = "action_candidate",
    candidate_status: str | None = "open",
    review_base_url: str = DEFAULT_REVIEW_BASE_URL,
) -> list[dict[str, Any]]:
    """Filter and sort candidates for a review queue view."""
    filtered: list[dict[str, Any]] = []
    for candidate in candidates:
        if decision is not None and candidate.get("decision") != decision:
            continue
        if candidate_status is not None and candidate.get("candidate_status") != candidate_status:
            continue
        row = dict(candidate)
        row["review_link"] = review_link(str(row["user_id"]), base_url=review_base_url)
        filtered.append(row)

    priority_rank = {"high": 0, "standard": 1}
    return sorted(
        filtered,
        key=lambda row: (
            priority_rank.get(str(row.get("candidate_priority")), 99),
            -float(row["risk_score"]),
            str(row["user_id"]),
        ),
    )


def format_summary(rows: list[dict[str, Any]], limit: int | None = None) -> str:
    """Format review queue rows as a compact pipe-separated table."""
    selected_rows = rows[:limit] if limit is not None else rows
    lines = [" | ".join(DISPLAY_COLUMNS)]
    lines.append(" | ".join("---" for _ in DISPLAY_COLUMNS))
    for row in selected_rows:
        lines.append(" | ".join(str(row.get(column, "")) for column in DISPLAY_COLUMNS))
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Summarize open action candidates for manual review."
    )
    parser.add_argument(
        "path",
        type=Path,
        help="Path to action_candidates part-000.jsonl.",
    )
    parser.add_argument(
        "--decision",
        default="action_candidate",
        help="Decision filter. Use 'all' to disable.",
    )
    parser.add_argument(
        "--candidate-status",
        default="open",
        help="Candidate status filter. Use 'all' to disable.",
    )
    parser.add_argument(
        "--review-base-url",
        default=DEFAULT_REVIEW_BASE_URL,
        help="Placeholder base URL for external review links.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum rows to print.",
    )
    args = parser.parse_args()

    decision = None if args.decision == "all" else args.decision
    candidate_status = None if args.candidate_status == "all" else args.candidate_status
    candidates = load_action_candidates(args.path)
    rows = summarize_review_queue(
        candidates,
        decision=decision,
        candidate_status=candidate_status,
        review_base_url=args.review_base_url,
    )
    print(format_summary(rows, limit=args.limit))


if __name__ == "__main__":
    main()
