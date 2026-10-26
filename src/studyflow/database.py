import sqlite3
from datetime import datetime
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


def add_subject(name):
    con = get_connection()

    try:
        cursor = con.execute(
        "INSERT INTO subjects (name) VALUES (?);",
        (name,),
        )
        con.commit()
        subject_id = cursor.lastrowid
        return subject_id
    finally:
        con.close()


def list_subjects():
    con = get_connection()
    cursor = con.cursor()
    try:
        cursor.execute("SELECT id, name FROM subjects ORDER BY name;")
        return cursor.fetchall()
    finally:
        con.close()


def add_topic(subject_id, topic_name):

    con = get_connection()
    cursor = con.cursor()

    try:
        cursor.execute("INSERT INTO topics (subject_id, topic_name) values(?, ?);",
        (subject_id, topic_name))
        con.commit()
        topic_id = cursor.lastrowid
        return topic_id
    finally:
        con.close()


def list_topics(subject_id):
    con = get_connection()
    cursor = con.cursor()
    try:
        cursor.execute("""
        SELECT id, subject_id, topic_name FROM topics WHERE subject_id = ?
        ORDER BY topic_name;
        """, (subject_id,))
        return cursor.fetchall()
    finally:
        con.close()


def add_task(topic_id, title, due_date=None):

    con = get_connection()
    cursor = con.cursor()

    try:
        cursor.execute("INSERT INTO tasks (topic_id, title, due_date) values(?, ?, ?);",
        (topic_id, title, due_date))
        con.commit()
        task_id = cursor.lastrowid
        return task_id
    finally:
        con.close()


def list_tasks(topic_id):
    con = get_connection()
    cursor = con.cursor()
    try:
        cursor.execute("""
        SELECT id, topic_id, title, due_date, status FROM tasks WHERE topic_id = ?
        ORDER BY due_date;
        """, (topic_id,))
        return cursor.fetchall()
    finally:
        con.close()


def update_task_status(task_id, new_status):

    con = get_connection()
    cursor = con.cursor()
    try:
        cursor.execute("""
        UPDATE tasks set status = ? WHERE id = ?
        """,
        (new_status, task_id,))
        con.commit()
        return cursor.rowcount == 1
    finally:
        con.close()

def list_due_tasks():
    con = get_connection()
    cursor = con.cursor()
    todays_date = datetime.today().isoformat()
    try:
        cursor.execute("""
        SELECT tasks.id,
        subjects.name,
        topics.topic_name,
        tasks.title,
        tasks.due_date,
        tasks.status
        FROM tasks 
        JOIN topics ON topics.id = tasks.topic_id
        JOIN subjects ON subjects.id = topics.subject_id
        WHERE tasks.due_date <= ? AND tasks.status != 'done'
        ORDER BY tasks.due_date
        """,(todays_date,))
        return cursor.fetchall()
    finally:
        con.close()