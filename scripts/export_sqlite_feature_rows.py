from __future__ import annotations

import sqlite3
import csv
from pathlib import Path

try:
    from scripts.build_sqlite_warehouse import DEFAULT_DB_PATH, build_warehouse
except ModuleNotFoundError:
    from build_sqlite_warehouse import DEFAULT_DB_PATH, build_warehouse


ROOT_DIR = Path(__file__).resolve().parents[1]
LABELED_FEATURE_ROWS_SQL = ROOT_DIR / "sql" / "sqlite" / "labeled_feature_rows.sql"
DEFAULT_OUTPUT_PATH = ROOT_DIR / "fixtures" / "feature_rows_from_sqlite.csv"


def export_feature_rows(
    db_path: Path = DEFAULT_DB_PATH,
    output_path: Path = DEFAULT_OUTPUT_PATH,
) -> Path:
    """Export point-in-time feature rows from the local SQLite warehouse."""
    if not db_path.exists():
        build_warehouse(db_path)

    sql = LABELED_FEATURE_ROWS_SQL.read_text()
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(sql)
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(columns)
        writer.writerows(rows)
    return output_path


if __name__ == "__main__":
    path = export_feature_rows()
    print(f"exported {path}")
