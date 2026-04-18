"""Tests for pipewatch.export."""
import json
import pytest
from pathlib import Path

from pipewatch.export import export_json, export_csv


@pytest.fixture()
def hist_file(tmp_path: Path) -> Path:
    return tmp_path / "history.jsonl"


def _write(hist_file: Path, records: list) -> None:
    with hist_file.open("w") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")


_RECORDS = [
    {"pipeline": "ingest", "timestamp": "2024-01-01T00:00:00Z", "success": True, "exit_code": 0, "duration_s": 1.2},
    {"pipeline": "transform", "timestamp": "2024-01-01T01:00:00Z", "success": False, "exit_code": 1, "duration_s": 0.5},
    {"pipeline": "ingest", "timestamp": "2024-01-01T02:00:00Z", "success": False, "exit_code": 2, "duration_s": 0.8},
]


def test_export_json_all(hist_file):
    _write(hist_file, _RECORDS)
    out = json.loads(export_json(str(hist_file)))
    assert len(out) == 3


def test_export_json_filtered(hist_file):
    _write(hist_file, _RECORDS)
    out = json.loads(export_json(str(hist_file), pipeline="ingest"))
    assert len(out) == 2
    assert all(r["pipeline"] == "ingest" for r in out)


def test_export_csv_headers(hist_file):
    _write(hist_file, _RECORDS)
    out = export_csv(str(hist_file))
    lines = out.strip().splitlines()
    assert lines[0] == "pipeline,timestamp,success,exit_code,duration_s"
    assert len(lines) == 4  # header + 3 rows


def test_export_csv_filtered(hist_file):
    _write(hist_file, _RECORDS)
    out = export_csv(str(hist_file), pipeline="transform")
    lines = out.strip().splitlines()
    assert len(lines) == 2  # header + 1 row
    assert "transform" in lines[1]


def test_export_csv_empty(hist_file):
    _write(hist_file, [])
    assert export_csv(str(hist_file)) == ""


def test_export_missing_file(hist_file):
    with pytest.raises(FileNotFoundError):
        export_json(str(hist_file))
