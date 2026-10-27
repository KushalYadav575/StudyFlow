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

    upd_out = sf("updtask", "--task_id", "1", "--field", "status", "--value", "done")
    assert "done" in upd_out

def test_end_to_end_subprocess(run_cli):
    r = run_cli("addsub", "--name", "Physics")
    assert r.returncode == 0
    r = run_cli("list_due_tasks")
    assert r.returncode == 0
    r = run_cli()
    assert r.returncode == 2

def test_cli_update_commands(sf):
    out = sf("addsub", "--name", "Math")
    assert "successfully added" in out

    out = sf("addtopic", "--name", "Algebra", "--subject_id", "1")
    assert "successfully added" in out

    out = sf("addtask", "--topic_id", "1", "--name", "HW1")
    assert "successfully added" in out

    out = sf("updtask", "--task_id", "1", "--field", "title", "--value", "HW2")
    assert "HW2" in out

    out = sf("updtask", "--task_id", "1", "--field", "status", "--value", "done")
    assert "done" in out

    out = sf("updtask", "--task_id", "1", "--field", "due_date", "--value", "2026-11-01")
    assert "2026-11-01" in out

    out = sf("updtask", "--task_id", "1", "--field", "due_date")
    assert "Due date cleared" in out

    out = sf("updtitle", "--topic_id", "1", "--title", "Geometry")
    assert "topic name updated" in out

    out = sf("updsubject", "--subject_id", "1", "--title", "Science")
    assert "subject name updated" in out


def test_cli_update_missing_ids(sf):
    out = sf("updtask", "--task_id", "99999", "--field", "title", "--value", "Missing")
    assert "No task with that id" in out

    out = sf("updtitle", "--topic_id", "99999", "--title", "Missing")
    assert "doesnot exist" in out

    out = sf("updsubject", "--subject_id", "99999", "--title", "Missing")
    assert "doesnot exist" in out