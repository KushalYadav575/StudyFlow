import csv
import sqlite3
from datetime import datetime

import pytest


def test_schema_and_tables(db, project):
    con = db.get_connection()
    try:
        names = {
            row[0]
            for row in con.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        assert con.execute("PRAGMA foreign_keys;").fetchone()[0] == 1
    finally:
        con.close()

    assert {"subjects", "topics", "tasks"} <= names

def test_subject_crud_and_constraints(db):
    sid = db.add_subject("Math")
    assert isinstance(sid, int)
    assert db.list_subjects() == [(sid, "Math")]
    with pytest.raises(sqlite3.IntegrityError):
        db.add_subject("Math")
    with pytest.raises(sqlite3.IntegrityError):
        db.add_subject(None)

def test_topic_crud_and_constraints(db, seeded):
    topics = db.list_topics(seeded.subject_id)
    assert len(topics) == 1
    assert topics[0][2] == "Algebra"
    with pytest.raises(sqlite3.IntegrityError):
        db.add_topic(seeded.subject_id, "Algebra")
    with pytest.raises(sqlite3.IntegrityError):
        db.add_topic(9999, "Ghost")

def test_task_crud_and_status(db, seeded):
    tid = db.add_task(seeded.topic_id, "HW1", "2026-10-25")
    tasks = db.list_tasks(seeded.topic_id)
    assert len(tasks) == 1
    assert tasks[0][2] == "HW1"
    assert tasks[0][4] == "not_started"
    
    assert db.upd_tasks(tid, "status", "done") is True
    assert db.list_tasks(seeded.topic_id)[0][4] == "done"
    assert db.upd_tasks(99999, "status", "done") is False

def test_sql_injection_defense(db, seeded):
    evil = "'; DROP TABLE subjects; --"

    subject_id = db.add_subject(evil)
    assert (subject_id, evil) in db.list_subjects()

    db.add_task(seeded.topic_id, evil)
    assert db.list_tasks(seeded.topic_id)[0][2] == evil

class FrozenDateTime(datetime):
    FROZEN = datetime(2026, 10, 26, 22, 12, 30)
    @classmethod
    def today(cls):
        return cls.FROZEN

def test_list_due_tasks(db, seeded, project, monkeypatch):
    monkeypatch.setattr(project.database, "datetime", FrozenDateTime)
    overdue_id = db.add_task(seeded.topic_id, "overdue", "2020-01-01")
    db.add_task(seeded.topic_id, "future", "2030-01-01")
    due = db.list_due_tasks()
    assert len(due) == 1
    assert due[0][0] == overdue_id
    assert due[0][3] == "overdue"

def test_update_task_fields(db, seeded):
    task_id = db.add_task(seeded.topic_id, "HW1", "2026-10-30")

    assert db.upd_tasks(task_id, "title", "HW2") is True
    assert db.list_tasks(seeded.topic_id)[0][2] == "HW2"

    assert db.upd_tasks(task_id, "status", "in_progress") is True
    assert db.list_tasks(seeded.topic_id)[0][4] == "in_progress"

    assert db.upd_tasks(task_id, "due_date", "2026-11-01") is True
    assert db.list_tasks(seeded.topic_id)[0][3] == "2026-11-01"

    assert db.upd_tasks(task_id, "due_date", None) is True
    assert db.list_tasks(seeded.topic_id)[0][3] is None

    assert db.upd_tasks(99999, "title", "Missing task") is False

    with pytest.raises(ValueError):
        db.upd_tasks(task_id, "id", 100)


def test_update_topic(db, seeded):
    topic_id = seeded.topic_id

    assert db.upd_topic("Geometry", topic_id) is True
    assert db.list_topics(seeded.subject_id)[0][2] == "Geometry"
    assert db.upd_topic("Missing", 99999) is False

    other_topic_id = db.add_topic(seeded.subject_id, "Calculus")
    with pytest.raises(sqlite3.IntegrityError):
        db.upd_topic("Geometry", other_topic_id)


def test_update_subject(db, seeded):
    subject_id = seeded.subject_id

    assert db.upd_subject("Science", subject_id) is True
    assert (subject_id, "Science") in db.list_subjects()
    assert db.upd_subject("Missing", 99999) is False

    other_subject_id = db.add_subject("Physics")
    with pytest.raises(sqlite3.IntegrityError):
        db.upd_subject("Science", other_subject_id)

def test_delete_task(db, seeded):
    task_id = db.add_task(seeded.topic_id, "HW1")

    assert db.delete_task(task_id) is True
    assert db.list_tasks(seeded.topic_id) == []

    assert db.delete_task(99999) is False

def test_list_all_tasks_order_and_data(db):
    biology_id = db.add_subject("Biology")
    math_id = db.add_subject("Math")

    cells_id = db.add_topic(biology_id, "Cells")
    algebra_id = db.add_topic(math_id, "Algebra")
    geometry_id = db.add_topic(math_id, "Geometry")

    cells_dated_id = db.add_task(cells_id, "Review cells", "2026-10-29")
    cells_undated_id = db.add_task(cells_id, "Draw a cell")
    algebra_id_task = db.add_task(algebra_id, "Practice equations", "2026-10-28")
    geometry_id_task = db.add_task(geometry_id, "Review angles", "2026-10-30")

    assert db.list_all_tasks() == [
        (
            cells_dated_id,
            "Biology",
            "Cells",
            "Review cells",
            "2026-10-29",
            "not_started",
        ),
        (
            cells_undated_id,
            "Biology",
            "Cells",
            "Draw a cell",
            None,
            "not_started",
        ),
        (
            algebra_id_task,
            "Math",
            "Algebra",
            "Practice equations",
            "2026-10-28",
            "not_started",
        ),
        (
            geometry_id_task,
            "Math",
            "Geometry",
            "Review angles",
            "2026-10-30",
            "not_started",
        ),
    ]


def test_list_all_tasks_empty(db):
    assert db.list_all_tasks() == []

def test_subject_progress_and_name(db, seeded):
    task_one = db.add_task(seeded.topic_id, "HW1")
    task_two = db.add_task(seeded.topic_id, "HW2")

    assert db.subject_name(seeded.subject_id) == "Math"
    assert db.subject_progress(seeded.subject_id) == 0.0

    db.upd_tasks(task_one, "status", "done")
    assert db.subject_progress(seeded.subject_id) == 50.0

    db.upd_tasks(task_two, "status", "done")
    assert db.subject_progress(seeded.subject_id) == 100.0

    with pytest.raises(ValueError):
        db.subject_name(99999)

    with pytest.raises(ValueError):
        db.subject_progress(99999)


def test_subject_progress_with_no_tasks(db, seeded):
    assert db.subject_progress(seeded.subject_id) == 0.0


def test_list_all_tasks_status_filter(db, seeded):
    open_task_id = db.add_task(seeded.topic_id, "Open task")
    done_task_id = db.add_task(seeded.topic_id, "Done task")
    db.upd_tasks(done_task_id, "status", "done")

    all_tasks = db.list_all_tasks()
    done_tasks = db.list_all_tasks("done")
    open_tasks = db.list_all_tasks("not_started")

    assert {row[0] for row in all_tasks} == {open_task_id, done_task_id}
    assert [row[0] for row in done_tasks] == [done_task_id]
    assert [row[0] for row in open_tasks] == [open_task_id]

    with pytest.raises(ValueError):
        db.list_all_tasks("waiting")

def test_import_file_preserves_task_data_and_reuses_records(db, seeded, tmp_path):
    csv_path = tmp_path / "tasks.csv"

    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            ["Task ID", "Subject", "Topic", "Title", "Due date", "Status"]
        )
        writer.writerow(
            ["500", "Math", "Algebra", 'Review, "Chapter 2"', "2026-11-03", "done"]
        )

    imported_count = db.import_file(csv_path)

    assert imported_count == 1
    assert db.list_subjects() == [(seeded.subject_id, "Math")]
    assert len(db.list_topics(seeded.subject_id)) == 1

    task = db.list_tasks(seeded.topic_id)[0]
    assert task[2:] == ('Review, "Chapter 2"', "2026-11-03", "done")


def test_import_file_rolls_back_if_a_row_is_invalid(db, tmp_path):
    csv_path = tmp_path / "invalid_tasks.csv"

    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            ["Task ID", "Subject", "Topic", "Title", "Due date", "Status"]
        )
        writer.writerow(["1", "Math", "Algebra", "Valid task", "", "done"])
        writer.writerow(["2", "Science", "Cells", "Invalid task", "", "waiting"])

    with pytest.raises(ValueError):
        db.import_file(csv_path)

    assert db.list_subjects() == []
    assert db.list_all_tasks() == []