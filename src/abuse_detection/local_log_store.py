from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _json_default(value: Any) -> str:
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def to_json_record(record: Any) -> dict[str, Any]:
    """Convert a dataclass or dict into a JSON-ready record."""
    if is_dataclass(record) and not isinstance(record, type):
        return asdict(record)
    if isinstance(record, dict):
        return dict(record)
    raise TypeError("record must be a dataclass instance or dict")


def partition_path(
    root_dir: Path,
    dataset: str,
    run_id: str,
    created_at: datetime,
) -> Path:
    """Return a local object-storage-like partition path."""
    dt = created_at.date().isoformat()
    hour = f"{created_at.hour:02d}"
    return root_dir / dataset / f"dt={dt}" / f"hour={hour}" / f"run_id={run_id}"


def write_jsonl_partition(
    records: list[Any],
    root_dir: Path,
    dataset: str,
    run_id: str,
    created_at: datetime | None = None,
) -> Path:
    """Write one append-only JSONL partition and a manifest marker."""
    partition_created_at = created_at or datetime.now(timezone.utc)
    output_dir = partition_path(root_dir, dataset, run_id, partition_created_at)
    part_path = output_dir / "part-000.jsonl"
    manifest_path = output_dir / "manifest.json"

    if part_path.exists() or manifest_path.exists():
        raise FileExistsError(f"partition already exists: {output_dir}")

    output_dir.mkdir(parents=True, exist_ok=False)
    with part_path.open("w", encoding="utf-8") as jsonl_file:
        for record in records:
            json_record = to_json_record(record)
            jsonl_file.write(json.dumps(json_record, default=_json_default, sort_keys=True))
            jsonl_file.write("\n")

    manifest = {
        "dataset": dataset,
        "run_id": run_id,
        "record_count": len(records),
        "part_file": part_path.name,
        "created_at": partition_created_at.isoformat(),
    }
    manifest_path.write_text(
        json.dumps(manifest, default=_json_default, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output_dir


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Read JSONL records from a local log file."""
    with path.open(encoding="utf-8") as jsonl_file:
        return [json.loads(line) for line in jsonl_file if line.strip()]
