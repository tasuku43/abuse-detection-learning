from __future__ import annotations

from abuse_detection.schema import ScoringFeatureRow


def scoring_fn(features: ScoringFeatureRow) -> float:
    """Score one feature row without reading labels or external state."""
    score = 0.0

    account_age_minutes = float(features["account_age_minutes"])
    contacts_24h = float(features["contacts_24h"])
    messages_1h = float(features["messages_1h"])
    profile_updates_24h = float(features["profile_updates_24h"])
    plan = str(features["plan"]).lower()

    if account_age_minutes <= 60:
        score += 30
    elif account_age_minutes <= 24 * 60:
        score += 15

    if contacts_24h >= 80:
        score += 30
    elif contacts_24h >= 30:
        score += 15

    if messages_1h >= 60:
        score += 25
    elif messages_1h >= 20:
        score += 10

    if profile_updates_24h >= 5:
        score += 15
    elif profile_updates_24h >= 2:
        score += 5

    if plan in {"paid", "enterprise"}:
        score -= 10

    return max(0.0, min(100.0, score))
