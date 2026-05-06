from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from abuse_detection.local_log_store import read_jsonl
from scripts.build_score_results import build_score_result_logs


def test_build_score_result_logs_writes_score_results_without_candidates(
    tmp_path: Path,
) -> None:
    feature_rows_path = tmp_path / "feature_rows.csv"
    pd.DataFrame(
        [
            {
                "user_id": "synthetic_user_001",
                "as_of_time": "2026-05-06T10:00:00+00:00",
                "label_value": 1,
                "account_age_minutes": 30,
                "contacts_24h": 90,
                "messages_1h": 70,
                "profile_updates_24h": 5,
                "device_count_24h": 1,
                "failed_login_count_24h": 0,
                "login_country_changes_24h": 0,
                "password_reset_24h": 0,
                "recipient_block_rate_24h": 0.1,
                "message_link_ratio_1h": 0.2,
                "plan": "free",
            }
        ]
    ).to_csv(feature_rows_path, index=False)

    score_results_dir = build_score_result_logs(
        feature_rows_path=feature_rows_path,
        data_lake_dir=tmp_path,
        run_id="score_run_001",
        scored_at=datetime(2026, 5, 6, 10, 0, tzinfo=timezone.utc),
    )

    score_results = read_jsonl(score_results_dir / "part-000.jsonl")

    assert len(score_results) == 1
    assert score_results[0]["user_id"] == "synthetic_user_001"
    assert "risk_score" in score_results[0]
    assert "candidate_status" not in score_results[0]
