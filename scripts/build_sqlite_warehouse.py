from __future__ import annotations

import sqlite3
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = ROOT_DIR / "data" / "local_warehouse.sqlite"
SQL_DIR = ROOT_DIR / "sql" / "sqlite"


APP_USERS = [
    ("user_001", "2026-05-01 08:00:00", "email", "US"),
    ("user_002", "2026-04-20 09:30:00", "sso", "JP"),
    ("user_003", "2026-05-01 23:30:00", "email", "US"),
    ("user_004", "2026-03-15 12:00:00", "sso", "GB"),
    ("user_005", "2026-05-02 09:45:00", "email", "DE"),
    ("user_006", "2026-04-28 18:20:00", "email", "JP"),
    ("user_007", "2026-05-02 10:30:00", "email", "US"),
    ("user_008", "2026-04-01 07:10:00", "invite", "AU"),
]

APP_USER_PROFILES = [
    ("user_001", "2026-05-01 08:05:00", 8, 12, None),
    ("user_002", "2026-04-20 10:00:00", 11, 80, "2026-04-20 10:05:00"),
    ("user_003", "2026-05-01 23:35:00", 6, 0, None),
    ("user_004", "2026-03-15 12:20:00", 14, 120, "2026-03-15 12:30:00"),
    ("user_005", "2026-05-02 09:50:00", 5, 8, None),
    ("user_006", "2026-04-28 18:30:00", 10, 40, "2026-04-28 18:35:00"),
    ("user_007", "2026-05-02 10:35:00", 4, 0, None),
    ("user_008", "2026-04-01 07:20:00", 12, 60, "2026-04-01 07:40:00"),
]

APP_USER_STATUS_SNAPSHOTS = [
    ("user_001", "2026-05-01 08:00:00", "active", "free", 0, 0, 20),
    ("user_001", "2026-05-02 09:35:00", "active", "free", 1, 0, 40),
    ("user_001", "2026-05-02 10:05:00", "suspended", "free", 1, 0, 40),
    ("user_002", "2026-04-20 09:30:00", "active", "paid", 1, 1, 100),
    ("user_003", "2026-05-01 23:30:00", "active", "free", 0, 0, 10),
    ("user_003", "2026-05-02 01:05:00", "suspended", "free", 0, 0, 10),
    ("user_004", "2026-03-15 12:00:00", "active", "enterprise", 1, 1, 100),
    ("user_005", "2026-05-02 09:45:00", "active", "free", 0, 0, 20),
    ("user_005", "2026-05-02 11:35:00", "suspended", "free", 1, 0, 40),
    ("user_006", "2026-04-28 18:20:00", "active", "paid", 1, 1, 80),
    ("user_007", "2026-05-02 10:30:00", "active", "free", 0, 0, 10),
    ("user_007", "2026-05-02 11:25:00", "suspended", "free", 0, 0, 10),
    ("user_008", "2026-04-01 07:10:00", "active", "free", 1, 0, 80),
]

WAREHOUSE_USER_BEHAVIOR_LOGS = [
    ("user_001", "2026-05-02 08:10:00", "contact_created", None),
    ("user_001", "2026-05-02 08:20:00", "contact_created", None),
    ("user_001", "2026-05-02 08:25:00", "message_sent", "link"),
    ("user_001", "2026-05-02 08:35:00", "message_sent", "link"),
    ("user_001", "2026-05-02 08:50:00", "recipient_blocked", None),
    ("user_001", "2026-05-02 09:00:00", "profile_updated", None),
    ("user_001", "2026-05-02 09:10:00", "new_device_login", None),
    ("user_001", "2026-05-02 09:15:00", "failed_login", None),
    ("user_001", "2026-05-02 09:20:00", "country_changed", None),
    ("user_001", "2026-05-02 09:30:00", "password_reset", None),
    ("user_002", "2026-05-02 06:00:00", "message_sent", "text"),
    ("user_002", "2026-05-02 07:00:00", "contact_created", None),
    ("user_002", "2026-05-02 08:30:00", "profile_updated", None),
    ("user_003", "2026-05-02 00:05:00", "contact_created", None),
    ("user_003", "2026-05-02 00:10:00", "contact_created", None),
    ("user_003", "2026-05-02 00:15:00", "contact_created", None),
    ("user_003", "2026-05-02 00:20:00", "message_sent", "link"),
    ("user_003", "2026-05-02 00:25:00", "message_sent", "link"),
    ("user_003", "2026-05-02 00:30:00", "recipient_blocked", None),
    ("user_003", "2026-05-02 00:35:00", "recipient_blocked", None),
    ("user_004", "2026-05-02 05:00:00", "message_sent", "text"),
    ("user_004", "2026-05-02 08:00:00", "contact_created", None),
    ("user_005", "2026-05-02 10:00:00", "new_device_login", None),
    ("user_005", "2026-05-02 10:05:00", "new_device_login", None),
    ("user_005", "2026-05-02 10:10:00", "failed_login", None),
    ("user_005", "2026-05-02 10:20:00", "failed_login", None),
    ("user_005", "2026-05-02 10:30:00", "country_changed", None),
    ("user_005", "2026-05-02 10:40:00", "password_reset", None),
    ("user_006", "2026-05-02 10:00:00", "message_sent", "link"),
    ("user_006", "2026-05-02 10:05:00", "message_sent", "text"),
    ("user_006", "2026-05-02 10:10:00", "recipient_blocked", None),
    ("user_007", "2026-05-02 10:45:00", "contact_created", None),
    ("user_007", "2026-05-02 10:50:00", "message_sent", "text"),
    ("user_007", "2026-05-02 10:55:00", "message_sent", "text"),
    ("user_008", "2026-05-02 09:00:00", "message_sent", "text"),
]

WAREHOUSE_OPERATOR_ACTION_LOGS = [
    ("user_001", "2026-05-02 10:00:00", "human_suspend_abuse", "human"),
    ("user_003", "2026-05-02 01:00:00", "human_suspend_abuse", "human"),
    ("user_005", "2026-05-02 11:30:00", "human_suspend_abuse", "human"),
    ("user_006", "2026-05-02 11:00:00", "human_review_clean", "human"),
    ("user_007", "2026-05-02 11:20:00", "auto_suspend_abuse", "system"),
]


def build_warehouse(db_path: Path = DEFAULT_DB_PATH) -> Path:
    """Create a local SQLite database with synthetic app and warehouse tables."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    with sqlite3.connect(db_path) as conn:
        conn.executescript(
            """
            create table app_users (
                user_id text primary key,
                created_at text not null,
                signup_method text not null,
                initial_country text not null
            );

            create table app_user_profiles (
                user_id text primary key,
                profile_created_at text not null,
                display_name_length integer not null,
                bio_length integer not null,
                avatar_uploaded_at text
            );

            create table app_user_status_snapshots (
                user_id text not null,
                snapshot_time text not null,
                account_status text not null,
                plan text not null,
                email_verified integer not null,
                phone_verified integer not null,
                profile_completeness integer not null
            );

            create table warehouse_user_behavior_logs (
                user_id text not null,
                event_time text not null,
                event_type text not null,
                event_detail text
            );

            create table warehouse_operator_action_logs (
                user_id text not null,
                action_time text not null,
                action_type text not null,
                actor_type text not null
            );
            """
        )
        conn.executemany("insert into app_users values (?, ?, ?, ?)", APP_USERS)
        conn.executemany("insert into app_user_profiles values (?, ?, ?, ?, ?)", APP_USER_PROFILES)
        conn.executemany(
            "insert into app_user_status_snapshots values (?, ?, ?, ?, ?, ?, ?)",
            APP_USER_STATUS_SNAPSHOTS,
        )
        conn.executemany(
            "insert into warehouse_user_behavior_logs values (?, ?, ?, ?)",
            WAREHOUSE_USER_BEHAVIOR_LOGS,
        )
        conn.executemany(
            "insert into warehouse_operator_action_logs values (?, ?, ?, ?)",
            WAREHOUSE_OPERATOR_ACTION_LOGS,
        )
        build_evaluation_tables(conn)

    return db_path


def build_evaluation_tables(conn: sqlite3.Connection) -> None:
    """Materialize evaluation tables from synthetic raw inputs."""
    conn.executescript(
        """
        drop table if exists eval_labels;
        drop table if exists eval_feature_rows;
        drop table if exists eval_targets;
        """
    )
    conn.execute(f"create table eval_labels as {read_sql('human_label_source.sql')}")
    conn.execute(f"create table eval_targets as {read_sql('evaluation_targets.sql')}")
    conn.execute(f"create table eval_feature_rows as {read_sql('feature_rows.sql')}")


def read_sql(filename: str) -> str:
    return (SQL_DIR / filename).read_text()


if __name__ == "__main__":
    path = build_warehouse()
    print(f"created {path}")
