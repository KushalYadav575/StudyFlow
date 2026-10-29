import csv
import sqlite3
from datetime import datetime
from pathlib import Path


def get_connection():

    cur_dir = Path(__file__).parent.parent.parent

    db_path = cur_dir / 'data' / 'studyflow.db'
    db_path.parent.mkdir(parents=True, exist_ok=True)
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


def upd_tasks(task_id, field, value):

    con = get_connection()
    cursor = con.cursor()
    try:
        if field in ("status", "title", "due_date"):
            cursor.execute(f"""
            UPDATE tasks SET {field} = ? WHERE id = ?;
            """,(value, task_id))
            con.commit()
            return cursor.rowcount == 1
        else:
            raise ValueError(
                f"Invalid field name:'{field}'.Must be 'status', 'title', or 'due_date'"
                )
    finally:
        con.close()


def upd_topic(new_topic_name, topic_id):
    con = get_connection()
    cursor = con.cursor()
    try:
        cursor.execute(
            "UPDATE topics SET topic_name = ? WHERE id = ?", (new_topic_name, topic_id)
            )
        con.commit()
        return cursor.rowcount == 1
    finally:
        con.close()


def upd_subject(new_subject_name, subject_id):
    con = get_connection()
    cursor = con.cursor()
    try:
        cursor.execute(
            "UPDATE subjects SET name = ? WHERE id = ?", (new_subject_name, subject_id)
            )
        con.commit()
        return cursor.rowcount == 1
    finally:
        con.close()


def delete_task(task_id):
    con = get_connection()
    cursor = con.cursor()
    try:
        cursor.execute(
            "DELETE FROM tasks WHERE id = ?", (task_id,)
            )
        con.commit()
        return cursor.rowcount == 1
    finally:
        con.close()

def delete_topic(topic_id):
    con = get_connection()
    cursor = con.cursor()
    try:
        cursor.execute(
        "DELETE FROM topics WHERE id = ?", (topic_id,)
        )
        con.commit()

        return cursor.rowcount == 1
    finally:
        con.close()


def delete_subject(subject_id):
    con = get_connection()
    cursor = con.cursor()
    try:
        cursor.execute(
            "DELETE FROM subjects WHERE id = ?", (subject_id,)
            )
        con.commit()
        return cursor.rowcount == 1
    finally:
        con.close()


def list_all_tasks(status=None):
    con = get_connection()
    cursor = con.cursor()
    try:
        if status in ["not_started", "in_progress", "done"]:
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
            WHERE tasks.status = ?
            ORDER BY subjects.name, topics.topic_name,
            tasks.due_date IS NULL, tasks.due_date;
            """, (status,))
            return cursor.fetchall()
        elif  status is None:
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
            ORDER BY subjects.name, topics.topic_name,
            tasks.due_date IS NULL, tasks.due_date;
            """)
            return cursor.fetchall()
        else:
            raise ValueError(
                f"""Invalid status value: '{status}'.
                Must be 'not_started', 'in_progress', 'done', or None."""
                )
    finally:
        con.close()


def subject_progress(subject_id):
    con = get_connection()
    cursor = con.cursor()
    try:
        cursor.execute("SELECT 1 FROM subjects WHERE id = ?", (subject_id,))
        if cursor.fetchone() is None:
            raise ValueError(f"No subject with ID {subject_id} exists.")
        cursor.execute("""
        SELECT COUNT(*) FROM tasks
        JOIN topics ON topics.id = tasks.topic_id
        WHERE topics.subject_id = ? AND tasks.status = 'done';
        """, (subject_id,))
        done_count = cursor.fetchone()[0]

        cursor.execute("""
        SELECT COUNT(*) FROM tasks
        JOIN topics ON topics.id = tasks.topic_id
        WHERE topics.subject_id = ?;
        """, (subject_id,))
        total_count = cursor.fetchone()[0]

        if total_count == 0:
            return 0.0

        return done_count / total_count * 100
    finally:
        con.close()


def subject_name(subject_id):
    con = get_connection()
    cursor = con.cursor()
    try:
        cursor.execute("SELECT name FROM subjects WHERE id = ?", (subject_id,))
        result = cursor.fetchone()
        if result is None:
            raise ValueError(f"No subject with ID {subject_id} exists.")
        return result[0]
    finally:
        con.close()


def import_file(file_path):
    required_columns = {"Subject", "Topic", "Title", "Due date", "Status"}
    valid_statuses = {"not_started", "in_progress", "done"}

    con = get_connection()

    try:
        with open(file_path, "r", newline="", encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile)

            if reader.fieldnames is None:
                raise ValueError("The CSV file is empty or has no header row.")

            missing_columns = required_columns - set(reader.fieldnames)
            if missing_columns:
                missing = ", ".join(sorted(missing_columns))
                raise ValueError(f"CSV is missing required columns: {missing}")

            cursor = con.cursor()
            imported_count = 0

            for row_number, row in enumerate(reader, start=2):
                subject_name = (row.get("Subject") or "").strip()
                topic_name = (row.get("Topic") or "").strip()
                task_title = (row.get("Title") or "").strip()
                due_date_text = (row.get("Due date") or "").strip()
                status = (row.get("Status") or "").strip()

                if not subject_name or not topic_name or not task_title:
                    raise ValueError(
                        f"CSV row {row_number}: subject, topic, and title "
                        "must not be empty."
                    )

                if status not in valid_statuses:
                    raise ValueError(
                        f"CSV row {row_number}: invalid status '{status}'. "
                        "Use not_started, in_progress, or done."
                    )

                due_date = due_date_text or None
                if due_date is not None:
                    if (
                        len(due_date) != 10
                        or due_date[4] != "-"
                        or due_date[7] != "-"
                    ):
                        raise ValueError(
                            f"CSV row {row_number}: invalid due date "
                            f"'{due_date}'. Use YYYY-MM-DD."
                        )

                    try:
                        datetime.strptime(due_date, "%Y-%m-%d")
                    except ValueError as error:
                        raise ValueError(
                            f"CSV row {row_number}: invalid due date "
                            f"'{due_date}'. Use a real date in YYYY-MM-DD format."
                        ) from error

                cursor.execute(
                    "INSERT OR IGNORE INTO subjects (name) VALUES (?);",
                    (subject_name,),
                )
                cursor.execute(
                    "SELECT id FROM subjects WHERE name = ?;",
                    (subject_name,),
                )
                subject_id = cursor.fetchone()[0]

                cursor.execute(
                    "INSERT OR IGNORE INTO topics (subject_id, topic_name) "
                    "VALUES (?, ?);",
                    (subject_id, topic_name),
                )
                cursor.execute(
                    "SELECT id FROM topics "
                    "WHERE subject_id = ? AND topic_name = ?;",
                    (subject_id, topic_name),
                )
                topic_id = cursor.fetchone()[0]

                cursor.execute(
                    "INSERT INTO tasks (topic_id, title, due_date, status) "
                    "VALUES (?, ?, ?, ?);",
                    (topic_id, task_title, due_date, status),
                )

                imported_count += 1

        con.commit()
        return imported_count

    except Exception:
        con.rollback()
        raise

    finally:
        con.close()