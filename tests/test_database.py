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
    
    assert db.update_task_status(tid, "done") is True
    assert db.list_tasks(seeded.topic_id)[0][4] == "done"
    assert db.update_task_status(99999, "done") is False

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