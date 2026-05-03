from __future__ import annotations

from abuse_detection.schema import ScoringFeatureRow


def _num(features: ScoringFeatureRow, name: str) -> float:
    return float(features[name])  # type: ignore[literal-required]


def _clamp_score(score: float) -> float:
    return max(0.0, min(100.0, score))


def scoring_fn(features: ScoringFeatureRow) -> float:
    """Baseline rule-based score for one feature row."""
    account_age_minutes = _num(features, "account_age_minutes")
    contacts_24h = _num(features, "contacts_24h")
    messages_1h = _num(features, "messages_1h")
    profile_updates_24h = _num(features, "profile_updates_24h")
    device_count_24h = _num(features, "device_count_24h")
    failed_login_count_24h = _num(features, "failed_login_count_24h")
    login_country_changes_24h = _num(features, "login_country_changes_24h")
    password_reset_24h = _num(features, "password_reset_24h")
    recipient_block_rate_24h = _num(features, "recipient_block_rate_24h")
    message_link_ratio_1h = _num(features, "message_link_ratio_1h")
    plan = str(features["plan"]).lower()

    score = 0.0

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

    if device_count_24h >= 5:
        score += 15
    elif device_count_24h >= 3:
        score += 5

    if failed_login_count_24h >= 8:
        score += 15
    elif failed_login_count_24h >= 3:
        score += 5

    if login_country_changes_24h >= 2:
        score += 20

    if password_reset_24h >= 1:
        score += 10

    if recipient_block_rate_24h >= 0.25:
        score += 20
    elif recipient_block_rate_24h >= 0.10:
        score += 10

    if message_link_ratio_1h >= 0.50:
        score += 15
    elif message_link_ratio_1h >= 0.25:
        score += 5

    if plan in {"paid", "enterprise"}:
        score -= 10

    return _clamp_score(score)


def scoring_fn_conservative(features: ScoringFeatureRow) -> float:
    """Score variant that tries to reduce false positives."""
    account_age_minutes = _num(features, "account_age_minutes")
    contacts_24h = _num(features, "contacts_24h")
    messages_1h = _num(features, "messages_1h")
    profile_updates_24h = _num(features, "profile_updates_24h")
    device_count_24h = _num(features, "device_count_24h")
    failed_login_count_24h = _num(features, "failed_login_count_24h")
    login_country_changes_24h = _num(features, "login_country_changes_24h")
    password_reset_24h = _num(features, "password_reset_24h")
    recipient_block_rate_24h = _num(features, "recipient_block_rate_24h")
    message_link_ratio_1h = _num(features, "message_link_ratio_1h")
    plan = str(features["plan"]).lower()

    score = 0.0

    if account_age_minutes <= 60:
        score += 15
    elif account_age_minutes <= 24 * 60:
        score += 5

    if contacts_24h >= 100:
        score += 25
    elif contacts_24h >= 60:
        score += 10

    if messages_1h >= 80:
        score += 25
    elif messages_1h >= 40:
        score += 10

    if profile_updates_24h >= 6:
        score += 10

    if contacts_24h >= 80 and messages_1h >= 60:
        score += 20

    if device_count_24h >= 6:
        score += 10

    if failed_login_count_24h >= 10:
        score += 10

    if login_country_changes_24h >= 2 and failed_login_count_24h >= 3:
        score += 25

    if password_reset_24h >= 1 and login_country_changes_24h >= 1:
        score += 15

    if recipient_block_rate_24h >= 0.35:
        score += 20

    if message_link_ratio_1h >= 0.60 and messages_1h >= 40:
        score += 15

    if plan in {"paid", "enterprise"}:
        score -= 15

    return _clamp_score(score)


def scoring_fn_recall_heavy(features: ScoringFeatureRow) -> float:
    """Score variant that tries to reduce false negatives."""
    account_age_minutes = _num(features, "account_age_minutes")
    contacts_24h = _num(features, "contacts_24h")
    messages_1h = _num(features, "messages_1h")
    profile_updates_24h = _num(features, "profile_updates_24h")
    device_count_24h = _num(features, "device_count_24h")
    failed_login_count_24h = _num(features, "failed_login_count_24h")
    login_country_changes_24h = _num(features, "login_country_changes_24h")
    password_reset_24h = _num(features, "password_reset_24h")
    recipient_block_rate_24h = _num(features, "recipient_block_rate_24h")
    message_link_ratio_1h = _num(features, "message_link_ratio_1h")
    plan = str(features["plan"]).lower()

    score = 0.0

    if account_age_minutes <= 60:
        score += 35
    elif account_age_minutes <= 24 * 60:
        score += 20

    if contacts_24h >= 70:
        score += 35
    elif contacts_24h >= 20:
        score += 20

    if messages_1h >= 50:
        score += 30
    elif messages_1h >= 10:
        score += 15

    if profile_updates_24h >= 4:
        score += 20
    elif profile_updates_24h >= 2:
        score += 10

    if device_count_24h >= 4:
        score += 20
    elif device_count_24h >= 2:
        score += 10

    if failed_login_count_24h >= 5:
        score += 20
    elif failed_login_count_24h >= 2:
        score += 10

    if login_country_changes_24h >= 1:
        score += 20

    if password_reset_24h >= 1:
        score += 15

    if recipient_block_rate_24h >= 0.15:
        score += 20
    elif recipient_block_rate_24h >= 0.05:
        score += 10

    if message_link_ratio_1h >= 0.35:
        score += 15
    elif message_link_ratio_1h >= 0.15:
        score += 5

    if plan in {"paid", "enterprise"}:
        score -= 5

    return _clamp_score(score)
