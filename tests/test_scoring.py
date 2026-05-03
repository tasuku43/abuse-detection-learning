from abuse_detection.scoring import scoring_fn


def test_scoring_fn_returns_score_between_0_and_100() -> None:
    score = scoring_fn(
        {
            "account_age_minutes": 1,
            "contacts_24h": 999,
            "messages_1h": 999,
            "profile_updates_24h": 99,
            "plan": "free",
        }
    )

    assert 0 <= score <= 100


def test_suspicious_row_scores_higher_than_normal_row() -> None:
    suspicious = {
        "account_age_minutes": 10,
        "contacts_24h": 100,
        "messages_1h": 80,
        "profile_updates_24h": 6,
        "plan": "free",
    }
    normal = {
        "account_age_minutes": 60 * 24 * 60,
        "contacts_24h": 2,
        "messages_1h": 1,
        "profile_updates_24h": 0,
        "plan": "paid",
    }

    assert scoring_fn(suspicious) > scoring_fn(normal)

