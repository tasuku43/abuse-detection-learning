from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

from abuse_detection.production_schema import ScoreResult, new_id
from abuse_detection.schema import ScoringFeatureRow
from abuse_detection.scoring import SCORING_FN_VERSION, scoring_fn


SCORE_SOURCE = "rule_based"
FEATURE_VERSION = "feature_v001"


class ScoreRequest(BaseModel):
    """HTTP request body for scoring one feature row."""

    model_config = ConfigDict(extra="allow")

    user_id: str
    as_of_time: datetime
    account_age_minutes: float
    contacts_24h: float
    messages_1h: float
    profile_updates_24h: float
    device_count_24h: float
    failed_login_count_24h: float
    login_country_changes_24h: float
    password_reset_24h: float
    recipient_block_rate_24h: float
    message_link_ratio_1h: float
    plan: str


class ScoreResponse(BaseModel):
    """HTTP response body for one score result."""

    score_result_id: str
    user_id: str
    as_of_time: datetime
    risk_score: float = Field(ge=0.0, le=100.0)
    score_source: str
    score_version: str
    feature_version: str
    scored_at: datetime


def score_request(request: ScoreRequest, scored_at: datetime | None = None) -> ScoreResult:
    """Score one request and return a ScoreResult."""
    feature_row: ScoringFeatureRow = {
        "account_age_minutes": request.account_age_minutes,
        "contacts_24h": request.contacts_24h,
        "messages_1h": request.messages_1h,
        "profile_updates_24h": request.profile_updates_24h,
        "device_count_24h": request.device_count_24h,
        "failed_login_count_24h": request.failed_login_count_24h,
        "login_country_changes_24h": request.login_country_changes_24h,
        "password_reset_24h": request.password_reset_24h,
        "recipient_block_rate_24h": request.recipient_block_rate_24h,
        "message_link_ratio_1h": request.message_link_ratio_1h,
        "plan": request.plan,
    }
    return ScoreResult(
        score_result_id=new_id("score_result"),
        user_id=request.user_id,
        as_of_time=request.as_of_time,
        risk_score=scoring_fn(feature_row),
        score_source=SCORE_SOURCE,
        score_version=SCORING_FN_VERSION,
        feature_version=FEATURE_VERSION,
        scored_at=scored_at or datetime.now(timezone.utc),
    )


def score_response(score_result: ScoreResult) -> ScoreResponse:
    """Convert internal ScoreResult into HTTP response schema."""
    return ScoreResponse(
        score_result_id=score_result.score_result_id,
        user_id=score_result.user_id,
        as_of_time=score_result.as_of_time,
        risk_score=score_result.risk_score,
        score_source=score_result.score_source,
        score_version=score_result.score_version,
        feature_version=score_result.feature_version,
        scored_at=score_result.scored_at,
    )


app = FastAPI(
    title="Abuse Detection Scoring API",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/score", response_model=ScoreResponse)
def score(request: ScoreRequest) -> ScoreResponse:
    return score_response(score_request(request))


def request_from_feature_row(row: dict[str, Any]) -> ScoreRequest:
    """Build a ScoreRequest from a local feature row record."""
    return ScoreRequest(**row)
