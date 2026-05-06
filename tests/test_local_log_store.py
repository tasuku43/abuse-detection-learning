from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import pytest

from abuse_detection.local_log_store import read_jsonl, write_jsonl_partition


@dataclass(frozen=True)
class ToyRecord:
    record_id: str
    created_at: datetime


def test_write_jsonl_partition_writes_records_and_manifest(tmp_path: Path) -> None:
    created_at = datetime(2026, 5, 6, 10, 0, tzinfo=timezone.utc)
    records = [ToyRecord(record_id="record_001", created_at=created_at)]

    output_dir = write_jsonl_partition(
        records,
        root_dir=tmp_path,
        dataset="score_results",
        run_id="run_001",
        created_at=created_at,
    )

    assert output_dir == tmp_path / "score_results" / "dt=2026-05-06" / "hour=10" / "run_id=run_001"
    assert (output_dir / "manifest.json").exists()
    rows = read_jsonl(output_dir / "part-000.jsonl")
    assert rows == [{"created_at": "2026-05-06T10:00:00+00:00", "record_id": "record_001"}]


def test_write_jsonl_partition_refuses_to_overwrite_existing_partition(tmp_path: Path) -> None:
    created_at = datetime(2026, 5, 6, 10, 0, tzinfo=timezone.utc)

    write_jsonl_partition(
        [{"record_id": "record_001"}],
        root_dir=tmp_path,
        dataset="score_results",
        run_id="run_001",
        created_at=created_at,
    )

    with pytest.raises(FileExistsError, match="partition already exists"):
        write_jsonl_partition(
            [{"record_id": "record_002"}],
            root_dir=tmp_path,
            dataset="score_results",
            run_id="run_001",
            created_at=created_at,
        )
