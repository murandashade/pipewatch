import pytest
from pipewatch.cli_oncall import handle_oncall


class _Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture
def oc_file(tmp_path):
    return str(tmp_path / "oncall.json")


def test_set_returns_zero(oc_file, capsys):
    args = _Args(oncall_cmd="set", pipeline="etl", contact="alice@example.com", file=oc_file)
    assert handle_oncall(args) == 0
    out = capsys.readouterr().out
    assert "alice@example.com" in out


def test_show_no_contact(oc_file, capsys):
    args = _Args(oncall_cmd="show", pipeline="etl", file=oc_file)
    assert handle_oncall(args) == 0
    out = capsys.readouterr().out
    assert "No on-call" in out


def test_show_after_set(oc_file, capsys):
    set_args = _Args(oncall_cmd="set", pipeline="etl", contact="bob@example.com", file=oc_file)
    handle_oncall(set_args)
    show_args = _Args(oncall_cmd="show", pipeline="etl", file=oc_file)
    assert handle_oncall(show_args) == 0
    out = capsys.readouterr().out
    assert "bob@example.com" in out


def test_remove_existing(oc_file, capsys):
    set_args = _Args(oncall_cmd="set", pipeline="etl", contact="carol", file=oc_file)
    handle_oncall(set_args)
    rm_args = _Args(oncall_cmd="remove", pipeline="etl", file=oc_file)
    assert handle_oncall(rm_args) == 0
    out = capsys.readouterr().out
    assert "Removed" in out


def test_remove_missing(oc_file, capsys):
    args = _Args(oncall_cmd="remove", pipeline="ghost", file=oc_file)
    assert handle_oncall(args) == 0
    out = capsys.readouterr().out
    assert "No on-call contact found" in out


def test_list_empty(oc_file, capsys):
    args = _Args(oncall_cmd="list", file=oc_file)
    assert handle_oncall(args) == 0
    out = capsys.readouterr().out
    assert "No on-call" in out
