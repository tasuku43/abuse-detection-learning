from datetime import datetime, timezone

from fastapi.testclient import TestClient

from abuse_detection.scoring_api import app, score_request, ScoreRequest


def _request() -> ScoreRequest:
    return ScoreRequest(
        user_id="synthetic_user_001",
        as_of_time=datetime(2026, 5, 6, 10, 0, tzinfo=timezone.utc),
        account_age_minutes=30,
        contacts_24h=90,
        messages_1h=70,
        profile_updates_24h=5,
        device_count_24h=1,
        failed_login_count_24h=0,
        login_country_changes_24h=0,
        password_reset_24h=0,
        recipient_block_rate_24h=0.1,
        message_link_ratio_1h=0.2,
        plan="free",
    )


def test_score_request_returns_score_result_without_action_candidate_fields() -> None:
    scored_at = datetime(2026, 5, 6, 10, 1, tzinfo=timezone.utc)

    score_result = score_request(_request(), scored_at=scored_at)

    assert score_result.user_id == "synthetic_user_001"
    assert 0.0 <= score_result.risk_score <= 100.0
    assert score_result.score_source == "rule_based"
    assert not hasattr(score_result, "candidate_status")


def test_http_score_endpoint_returns_score_result() -> None:
    client = TestClient(app)

    response = client.post("/score", json=_request().model_dump(mode="json"))

    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == "synthetic_user_001"
    assert body["score_source"] == "rule_based"
    assert "risk_score" in body
    assert "candidate_status" not in body
