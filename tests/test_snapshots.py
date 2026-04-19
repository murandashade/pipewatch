import pytest
from pipewatch.snapshots import save_snapshot, load_snapshot, has_changed, diff_summary


@pytest.fixture
def snap_dir(tmp_path):
    return str(tmp_path / "snaps")


def test_save_creates_snapshot(snap_dir):
    rec = save_snapshot("pipe1", "hello", base_dir=snap_dir)
    assert rec["name"] == "pipe1"
    assert rec["output"] == "hello"
    assert "checksum" in rec
    assert "timestamp" in rec


def test_load_returns_none_when_missing(snap_dir):
    assert load_snapshot("nonexistent", base_dir=snap_dir) is None


def test_load_returns_saved_snapshot(snap_dir):
    save_snapshot("pipe2", "data", base_dir=snap_dir)
    snap = load_snapshot("pipe2", base_dir=snap_dir)
    assert snap is not None
    assert snap["output"] == "data"


def test_has_changed_true_when_no_snapshot(snap_dir):
    assert has_changed("pipe3", "anything", base_dir=snap_dir) is True


def test_has_changed_false_when_same(snap_dir):
    save_snapshot("pipe4", "stable", base_dir=snap_dir)
    assert has_changed("pipe4", "stable", base_dir=snap_dir) is False


def test_has_changed_true_when_different(snap_dir):
    save_snapshot("pipe5", "old", base_dir=snap_dir)
    assert has_changed("pipe5", "new", base_dir=snap_dir) is True


def test_diff_summary_no_snapshot(snap_dir):
    result = diff_summary("pipe6", "x", base_dir=snap_dir)
    assert "no previous snapshot" in result


def test_diff_summary_unchanged(snap_dir):
    save_snapshot("pipe7", "same", base_dir=snap_dir)
    result = diff_summary("pipe7", "same", base_dir=snap_dir)
    assert "unchanged" in result


def test_diff_summary_changed(snap_dir):
    save_snapshot("pipe8", "before", base_dir=snap_dir)
    result = diff_summary("pipe8", "after", base_dir=snap_dir)
    assert "changed" in result
