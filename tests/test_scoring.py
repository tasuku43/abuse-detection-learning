from abuse_detection.scoring import (
    scoring_fn,
    scoring_fn_conservative,
    scoring_fn_recall_heavy,
)


def _feature_row(**overrides: int | float | str) -> dict[str, int | float | str]:
    row: dict[str, int | float | str] = {
        "account_age_minutes": 1440,
        "contacts_24h": 0,
        "messages_1h": 0,
        "profile_updates_24h": 0,
        "device_count_24h": 1,
        "failed_login_count_24h": 0,
        "login_country_changes_24h": 0,
        "password_reset_24h": 0,
        "recipient_block_rate_24h": 0.0,
        "message_link_ratio_1h": 0.0,
        "plan": "free",
    }
    row.update(overrides)
    return row


def test_scoring_fn_returns_score_between_0_and_100() -> None:
    score = scoring_fn(
        _feature_row(
            account_age_minutes=1,
            contacts_24h=999,
            messages_1h=999,
            profile_updates_24h=99,
            device_count_24h=99,
            failed_login_count_24h=99,
            login_country_changes_24h=9,
            password_reset_24h=1,
            recipient_block_rate_24h=0.9,
            message_link_ratio_1h=0.9,
        )
    )

    assert 0 <= score <= 100


def test_suspicious_row_scores_higher_than_normal_row() -> None:
    suspicious = _feature_row(
        account_age_minutes=10,
        contacts_24h=100,
        messages_1h=80,
        profile_updates_24h=6,
        device_count_24h=5,
        failed_login_count_24h=8,
        login_country_changes_24h=2,
        password_reset_24h=1,
        recipient_block_rate_24h=0.4,
        message_link_ratio_1h=0.6,
    )
    normal = _feature_row(
        account_age_minutes=60 * 24 * 60,
        contacts_24h=2,
        messages_1h=1,
        profile_updates_24h=0,
        device_count_24h=1,
        failed_login_count_24h=0,
        login_country_changes_24h=0,
        password_reset_24h=0,
        plan="paid",
    )

    assert scoring_fn(suspicious) > scoring_fn(normal)


def test_scoring_variants_return_scores_between_0_and_100() -> None:
    row = _feature_row(
        account_age_minutes=30,
        contacts_24h=120,
        messages_1h=90,
        profile_updates_24h=6,
        device_count_24h=7,
        failed_login_count_24h=12,
        login_country_changes_24h=3,
        password_reset_24h=1,
        recipient_block_rate_24h=0.5,
        message_link_ratio_1h=0.7,
    )

    for score_fn in [scoring_fn, scoring_fn_conservative, scoring_fn_recall_heavy]:
        assert 0 <= score_fn(row) <= 100


def test_recall_heavy_scores_borderline_abuse_higher_than_conservative() -> None:
    borderline_abuse = _feature_row(
        account_age_minutes=20,
        contacts_24h=18,
        messages_1h=12,
        profile_updates_24h=4,
        device_count_24h=3,
        failed_login_count_24h=2,
        login_country_changes_24h=1,
    )

    assert scoring_fn_recall_heavy(borderline_abuse) > scoring_fn_conservative(
        borderline_abuse
    )
