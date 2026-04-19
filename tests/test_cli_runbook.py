import pytest
from pipewatch.cli_runbook import handle_runbook


class _Args:
    def __init__(self, **kw):
        self.__dict__.update(kw)


@pytest.fixture
def rf(tmp_path):
    return str(tmp_path / "runbooks.json")


def test_add_returns_zero(rf):
    args = _Args(runbook_cmd="add", pipeline="etl", url="https://wiki", note="", file=rf)
    assert handle_runbook(args) == 0


def test_show_empty(rf, capsys):
    args = _Args(runbook_cmd="show", pipeline="etl", file=rf)
    rc = handle_runbook(args)
    assert rc == 0
    assert "No runbooks" in capsys.readouterr().out


def test_show_with_entry(rf, capsys):
    from pipewatch.runbook import add_runbook
    add_runbook("etl", "https://wiki", note="guide", path=rf)
    args = _Args(runbook_cmd="show", pipeline="etl", file=rf)
    handle_runbook(args)
    out = capsys.readouterr().out
    assert "https://wiki" in out


def test_remove_returns_zero(rf):
    from pipewatch.runbook import add_runbook
    add_runbook("etl", "https://wiki", path=rf)
    args = _Args(runbook_cmd="remove", pipeline="etl", url="https://wiki", file=rf)
    assert handle_runbook(args) == 0


def test_remove_missing_returns_one(rf):
    args = _Args(runbook_cmd="remove", pipeline="etl", url="https://nope", file=rf)
    assert handle_runbook(args) == 1


def test_list_empty(rf, capsys):
    args = _Args(runbook_cmd="list", file=rf)
    rc = handle_runbook(args)
    assert rc == 0
    assert "No runbooks" in capsys.readouterr().out


def test_list_shows_pipelines(rf, capsys):
    from pipewatch.runbook import add_runbook
    add_runbook("etl", "https://wiki/etl", path=rf)
    add_runbook("ingest", "https://wiki/ingest", path=rf)
    args = _Args(runbook_cmd="list", file=rf)
    rc = handle_runbook(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "etl" in out
    assert "ingest" in out
