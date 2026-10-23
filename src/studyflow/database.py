import sqlite3
from pathlib import Path


def get_connection():

    cur_dir = Path(__file__).parent.parent.parent

    db_path = cur_dir / 'data' / 'studyflow.db'
    con = sqlite3.connect(db_path)
    con.execute("PRAGMA foreign_keys = ON;")

    return con


def make_tables():
    try:
        con = get_connection()

        con.execute("""
        CREATE TABLE IF NOT EXISTS subjects (id integer PRIMARY KEY,
        name TEXT NOT NULL UNIQUE);
        """)

        con.execute("""
        CREATE TABLE IF NOT EXISTS topics (
        id integer PRIMARY KEY,
        subject_id integer NOT NULL,
        topic_name TEXT NOT NULL ,
        UNIQUE (subject_id, topic_name),
        FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
        );
        """)

        con.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
        id integer PRIMARY KEY,
        topic_id integer NOT NULL,
        title text NOT NULL,
        due_date text,
        status text NOT NULL DEFAULT 'not_started' 
        CHECK(status IN ('not_started', 'in_progress', 'done')),
        FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE);
        """)

        con.commit()

    finally:
        con.close()