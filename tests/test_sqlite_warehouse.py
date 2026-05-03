from __future__ import annotations

from pathlib import Path

import pandas as pd
import sqlite3

from abuse_detection.evaluation import evaluate_feature_rows
from abuse_detection.schema import REQUIRED_FEATURE_COLUMNS
from scripts.build_sqlite_warehouse import build_warehouse
from scripts.export_sqlite_feature_rows import export_feature_rows


def test_export_sqlite_feature_rows_has_required_columns(tmp_path: Path) -> None:
    db_path = tmp_path / "warehouse.sqlite"
    csv_path = tmp_path / "feature_rows.csv"

    build_warehouse(db_path)
    export_feature_rows(db_path=db_path, output_path=csv_path)

    feature_rows = pd.read_csv(csv_path)

    for column in REQUIRED_FEATURE_COLUMNS:
        assert column in feature_rows.columns

    for column in [
        "signup_method",
        "initial_country",
        "account_status_as_of",
        "email_verified",
        "phone_verified",
        "profile_completeness",
        "bio_length",
        "avatar_uploaded",
    ]:
        assert column in feature_rows.columns

    assert len(feature_rows) == 4
    assert set(feature_rows["label_value"]) == {0, 1}


def test_sqlite_feature_rows_work_with_evaluation_harness(tmp_path: Path) -> None:
    db_path = tmp_path / "warehouse.sqlite"
    csv_path = tmp_path / "feature_rows.csv"

    build_warehouse(db_path)
    export_feature_rows(db_path=db_path, output_path=csv_path)

    feature_rows = pd.read_csv(csv_path)
    scored_rows, metrics = evaluate_feature_rows(feature_rows, thresholds=[50, 80])

    assert "risk_score" in scored_rows.columns
    assert list(metrics["threshold"]) == [50, 80]
    assert set(metrics.columns) == {"threshold", "precision", "recall", "tp", "fp", "fn"}


def test_sqlite_feature_rows_use_events_before_as_of_time(tmp_path: Path) -> None:
    db_path = tmp_path / "warehouse.sqlite"
    csv_path = tmp_path / "feature_rows.csv"

    build_warehouse(db_path)
    with sqlite3.connect(db_path) as conn:
        feature_rows = pd.read_sql_query("select * from eval_feature_rows", conn).set_index("user_id")

    assert feature_rows.loc["user_007", "messages_1h"] == 0
    assert feature_rows.loc["user_007", "contacts_24h"] == 0


def test_sqlite_feature_rows_use_status_snapshot_before_as_of_time(tmp_path: Path) -> None:
    db_path = tmp_path / "warehouse.sqlite"
    csv_path = tmp_path / "feature_rows.csv"

    build_warehouse(db_path)
    with sqlite3.connect(db_path) as conn:
        feature_rows = pd.read_sql_query("select * from eval_feature_rows", conn).set_index("user_id")

    assert feature_rows.loc["user_001", "account_status_as_of"] == "active"
    assert feature_rows.loc["user_001", "email_verified"] == 0

    with sqlite3.connect(db_path) as conn:
        future_status = conn.execute(
            """
            select account_status
            from app_user_status_snapshots
            where user_id = 'user_001'
              and snapshot_time = '2026-05-02 10:05:00'
            """
        ).fetchone()[0]

    assert future_status == "suspended"


def test_sqlite_keeps_feature_rows_and_labels_in_separate_tables(tmp_path: Path) -> None:
    db_path = tmp_path / "warehouse.sqlite"

    build_warehouse(db_path)

    with sqlite3.connect(db_path) as conn:
        feature_columns = [row[1] for row in conn.execute("pragma table_info(eval_feature_rows)")]
        label_columns = [row[1] for row in conn.execute("pragma table_info(eval_labels)")]
        feature_count = conn.execute("select count(*) from eval_feature_rows").fetchone()[0]
        label_count = conn.execute("select count(*) from eval_labels").fetchone()[0]

    assert "label_value" not in feature_columns
    assert label_columns == ["user_id", "label_time", "as_of_time", "label_value"]
    assert feature_count == 8
    assert label_count == 4
