import argparse

import pytest


def parse(project, *argv):
    return project.cli.parser.parse_args(list(argv))

def test_validate_date_valid_and_invalid(project):
    assert project.cli.validate_date("2026-10-25") == "2026-10-25"
    with pytest.raises(argparse.ArgumentTypeError):
        project.cli.validate_date("2026-13-01")
    with pytest.raises(argparse.ArgumentTypeError):
        project.cli.validate_date("invalid-date")

def test_subcommand_parsing(project):
    args = parse(project, "addsub", "--name", "Math")
    assert args.command == "addsub" and args.name == "Math"
    
    args = parse(
        project, "addtask", "--topic_id", "1", "--name", "HW", "--due_date","2026-12-01"
        )
    assert args.due_date == "2026-12-01"

@pytest.fixture
def sf(project, monkeypatch, capsys):
    def _run(*argv):
        monkeypatch.setattr("sys.argv", ["sf", *argv])
        project.cli.main()
        return capsys.readouterr().out
    return _run

def test_cli_commands_workflow(sf):
    out = sf("addsub", "--name", "Math")
    assert "successfully added" in out
    out = sf("addtopic", "--name", "Algebra", "--subject_id", "1")
    assert "successfully added" in out
    out = sf("addtask", "--topic_id", "1", "--name", "HW", "--due_date", "2020-01-01")
    assert "successfully added" in out
    
    due_out = sf("list_due_tasks")
    assert "HW" in due_out

    upd_out = sf("updtaskstatus", "--task_id", "1", "--status", "done")
    assert "done applied" in upd_out

def test_end_to_end_subprocess(run_cli):
    r = run_cli("addsub", "--name", "Physics")
    assert r.returncode == 0
    r = run_cli("list_due_tasks")
    assert r.returncode == 0
    r = run_cli()
    assert r.returncode == 2