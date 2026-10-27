import argparse
import sqlite3
from datetime import datetime

from .database import (
    add_subject,
    add_task,
    add_topic,
    delete_task,
    list_due_tasks,
    list_subjects,
    list_tasks,
    list_topics,
    make_tables,
    upd_subject,
    upd_tasks,
    upd_topic,
)

parser = argparse.ArgumentParser(
    prog="sf",
    description="StudyFlow"
)

subparsers = parser.add_subparsers(
    dest="command",
    required=True,
)


add_sub_parser = subparsers.add_parser(
    "addsub",
    help="Add a subject",
)

add_sub_parser.add_argument(
    "--name",
    required=True,
    help="name of the subject",
)


add_topic_parser = subparsers.add_parser(
    "addtopic",
    help="Add a topic",
)

add_topic_parser.add_argument(
    "--name",
    required=True,
    help="name of the topic",
)

add_topic_parser.add_argument(
    "--subject_id",
    required=True,
    type=int,
    help="id of the related subject",
)


add_task_parser = subparsers.add_parser(
    "addtask",
    help="Add a task",
)

add_task_parser.add_argument(
    "--topic_id",
    required=True,
    type=int,
    help="id of the respective topic"
)

add_task_parser.add_argument(
    "--name",
    required=True,
    help="Name of the task"
)

list_due_tasks_parser = subparsers.add_parser(
    "list_due_tasks",
    help="lists all due tasks till today"
)

def validate_date(date_string):
    try:
        if (
            len(date_string) != 10
            or date_string[4] != "-"
            or date_string[7] != "-"
        ):
            raise ValueError

        datetime.strptime(date_string, "%Y-%m-%d").date()
        return date_string

    except ValueError:
        raise argparse.ArgumentTypeError(
            "Invalid format or date. "
            "Must be YYYY-MM-DD and a real calendar date (e.g., 2026-10-25)."
        )


add_task_parser.add_argument(
    "--due_date",
    type = validate_date,
    help="date of when the task is due"
)


list_sub_parser = subparsers.add_parser(
    "listsubs",
    help="list all the subjects",
)


list_topics_parser = subparsers.add_parser(
    "listtopics",
    help="list all the topics",
)

list_topics_parser.add_argument(
    "--sub_id",
    required=True,
    type=int,
    help="id of the respective subject",
)


list_task_parser = subparsers.add_parser(
    "listtasks",
    help="list all the tasks",
)

list_task_parser.add_argument(
    "--topic_id",
    required=True,
    type=int,
    help="id of the respective topic",
)

update_subject_parser = subparsers.add_parser(
    "updsubject",
    help="Update the title of a subject"
)

update_subject_parser.add_argument(
    "--subject_id",
    required=True,
    type=int,
    help="id of the subject"
)

update_subject_parser.add_argument(
    "--title",
    required=True,
    help="title of the subject"
)

update_topic_parser = subparsers.add_parser(
    "updtitle",
    help="Update the title of a topic"
)

update_topic_parser.add_argument(
    "--topic_id",
    required=True,
    type=int,
    help="id of the topic"
)

update_topic_parser.add_argument(
    "--title",
    required=True,
    help="title of the topic"
)

update_task_parser = subparsers.add_parser(
    "updtask",
    help="Updatethe fields of the task"
)

update_task_parser.add_argument(
    "--task_id",
    required=True,
    type=int,
    help="id of the respective task"
)

update_task_parser.add_argument(
    "--field",
    required=True,
    choices=["due_date", "title", "status"],
    help="field needed to be changed of the respective task"
)

update_task_parser.add_argument(
    "--value",
    help="value the field has to be changed to"
)

delete_task_parser = subparsers.add_parser(
    "deltask",
    help="delete a specific task"
)

delete_task_parser.add_argument(
    "--task_id",
    required=True,
    type=int,
    help="id of the task"
)

def add_sub_command(args):
    try:
        subject_id = add_subject(args.name)
    except sqlite3.IntegrityError as error:
        if error.sqlite_errorname == "SQLITE_CONSTRAINT_UNIQUE":
            print(f"The subject {args.name} already exists")
        else:
            raise
    else:
        print(f"Subject {args.name} successfully added.")
        print(f"ID: {subject_id}")


def add_topic_command(args):
    try:
        topic_id = add_topic(args.subject_id, args.name)
    except sqlite3.IntegrityError as error:
        if error.sqlite_errorname == "SQLITE_CONSTRAINT_UNIQUE":
            print(
                f"Topic {args.name} already exists within subject id {args.subject_id}"
            )
        elif error.sqlite_errorname == "SQLITE_CONSTRAINT_FOREIGNKEY":
            print(f"the subject id {args.subject_id} does not exist")
        else:
            raise
    else:
        print(f"topic {args.name} successfully added.")
        print(f"ID: {topic_id}")


def add_task_command(args):
    try:
        task_id = add_task(args.topic_id, args.name, args.due_date)
    except sqlite3.IntegrityError as error:
        if error.sqlite_errorname == "SQLITE_CONSTRAINT_FOREIGNKEY":
            print(f"the topic id {args.topic_id} does not exist")
        else:
            raise
    else:
        print(f"task {args.name} successfully added.")
        print(f"ID: {task_id}")


def list_sub_command(args):
    for row in list_subjects():
        print(f"ID:{row[0]} Name:{row[1]}")


def list_topics_command(args):
    for row in list_topics(args.sub_id):
        print(f"ID:{row[0]} Name:{row[2]}")


def list_tasks_command(args):
    for row in list_tasks(args.topic_id):
        print(f"ID:{row[0]} Name:{row[2]} Due Date:{row[3]} Status:{row[4]}")


def update_task_command(args):
    if args.field != "due_date" and args.value is None:
        update_task_parser.error("--value is required for this field")

    if args.field == "status":
        if args.value not in ["not_started", "in_progress", "done"]:
            update_task_parser.error(
                "status must be one of: not_started, in_progress, done"
            )

    elif args.field == "due_date" and args.value is not None:
        try:
            validate_date(args.value)
        except argparse.ArgumentTypeError as error:
            update_task_parser.error(str(error))

    result = upd_tasks(args.task_id, args.field, args.value)

    if result:
        if args.field == "due_date" and args.value is None:
            print(f"Due date cleared for task id:{args.task_id}")
        else:
            print(f"{args.value} set as {args.field} for task id:{args.task_id}")
    else:
        print("No task with that id found")


def update_topic_command(args):
    try:
        result = upd_topic(args.title, args.topic_id)
        if result:
            print(f"topic name updated to {args.title}")
        else:
            print("that id doesnot exist in the database")
    except sqlite3.IntegrityError as e:
        if getattr(e, "sqlite_errorname", None) == "SQLITE_CONSTRAINT_UNIQUE":
            print("Error: A topic with that name already exists under this subject.")
        else:
            raise 


def update_subject_command(args):
    try:
        result = upd_subject(args.title, args.subject_id)
        if result:
            print(f"subject name updated to {args.title}")
        else:
            print("that id doesnot exist in the database")
    except sqlite3.IntegrityError as e:
        if getattr(e, "sqlite_errorname", None) == "SQLITE_CONSTRAINT_UNIQUE":
            print("Error: A subject with that name already exists under this database.")
        else:
            raise 


def list_due_tasks_command(args):
    tasks = list_due_tasks()
    
    if not tasks:
        print("No due tasks found.")

    for item in tasks:
        print(
            f"task id:{item[0]}, subject name:{item[1]}, "
            f"topic name:{item[2]}, title:{item[3]}, "
            f"due date:{item[4]}, status:{item[5]}"
        )


def delete_task_command(args):
    result = delete_task(args.task_id)
    if result:
        print(f"task with id:{args.task_id} deleted")
    else:
        print("No task with that id exists")


add_sub_parser.set_defaults(func=add_sub_command)
add_topic_parser.set_defaults(func=add_topic_command)
add_task_parser.set_defaults(func=add_task_command)
list_sub_parser.set_defaults(func=list_sub_command)
list_topics_parser.set_defaults(func=list_topics_command)
list_task_parser.set_defaults(func=list_tasks_command)
update_task_parser.set_defaults(func=update_task_command)
list_due_tasks_parser.set_defaults(func=list_due_tasks_command)
update_topic_parser.set_defaults(func=update_topic_command)
update_subject_parser.set_defaults(func=update_subject_command)
delete_task_parser.set_defaults(func=delete_task_command)

def main():
    args = parser.parse_args()
    make_tables()
    args.func(args)


if __name__ == "__main__":
    main()