import argparse
import sqlite3
from datetime import datetime

from .database import (
    add_subject,
    add_task,
    add_topic,
    delete_subject,
    delete_task,
    delete_topic,
    list_all_tasks,
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
    description="StudyFlow: a local study planner",
)

subparsers = parser.add_subparsers(
    dest="command",
    required=True,
)


# Add commands

add_sub_parser = subparsers.add_parser(
    "addsub",
    help="Add a subject",
)
add_sub_parser.add_argument(
    "--name",
    required=True,
    help="Name of the subject",
)


add_topic_parser = subparsers.add_parser(
    "addtopic",
    help="Add a topic to a subject",
)
add_topic_parser.add_argument(
    "--name",
    required=True,
    help="Name of the topic",
)
add_topic_parser.add_argument(
    "--subject_id",
    required=True,
    type=int,
    help="ID of the subject the topic belongs to",
)


add_task_parser = subparsers.add_parser(
    "addtask",
    help="Add a task to a topic",
)
add_task_parser.add_argument(
    "--topic_id",
    required=True,
    type=int,
    help="ID of the topic the task belongs to",
)
add_task_parser.add_argument(
    "--name",
    required=True,
    help="Name of the task",
)


# Date validation

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
            "Invalid date. Use YYYY-MM-DD and enter a real calendar date "
            "(for example, 2026-10-25)."
        )


add_task_parser.add_argument(
    "--due_date",
    type=validate_date,
    help="Optional due date in YYYY-MM-DD format",
)


# List commands

list_sub_parser = subparsers.add_parser(
    "listsubs",
    help="List all subjects",
)


list_topics_parser = subparsers.add_parser(
    "listtopics",
    help="List topics belonging to a subject",
)
list_topics_parser.add_argument(
    "--sub_id",
    required=True,
    type=int,
    help="ID of the subject",
)


list_task_parser = subparsers.add_parser(
    "listtasks",
    help="List tasks belonging to a topic",
)
list_task_parser.add_argument(
    "--topic_id",
    required=True,
    type=int,
    help="ID of the topic",
)


list_due_tasks_parser = subparsers.add_parser(
    "list_due_tasks",
    help="List unfinished tasks due today or earlier",
)


# Update commands

update_subject_parser = subparsers.add_parser(
    "updsubject",
    help="Rename a subject",
)
update_subject_parser.add_argument(
    "--subject_id",
    required=True,
    type=int,
    help="ID of the subject to rename",
)
update_subject_parser.add_argument(
    "--title",
    required=True,
    help="New subject name",
)


update_topic_parser = subparsers.add_parser(
    "updtitle",
    help="Rename a topic",
)
update_topic_parser.add_argument(
    "--topic_id",
    required=True,
    type=int,
    help="ID of the topic to rename",
)
update_topic_parser.add_argument(
    "--title",
    required=True,
    help="New topic name",
)


update_task_parser = subparsers.add_parser(
    "updtask",
    help="Change a task's title, status, or due date",
)
update_task_parser.add_argument(
    "--task_id",
    required=True,
    type=int,
    help="ID of the task to update",
)
update_task_parser.add_argument(
    "--field",
    required=True,
    choices=["due_date", "title", "status"],
    help="Task field to update",
)
update_task_parser.add_argument(
    "--value",
    help=(
        "New field value. Omit this only to clear a task's due date."
    ),
)


# Delete commands

delete_task_parser = subparsers.add_parser(
    "deltask",
    help="Delete a task",
)
delete_task_parser.add_argument(
    "--task_id",
    required=True,
    type=int,
    help="ID of the task to delete",
)


delete_topic_parser = subparsers.add_parser(
    "deltopic",
    help="Delete a topic and all tasks belonging to it",
)
delete_topic_parser.add_argument(
    "--topic_id",
    required=True,
    type=int,
    help="ID of the topic to delete; its tasks will also be deleted",
)


delete_subject_parser = subparsers.add_parser(
    "delsub",
    help="Delete a subject, its topics, and their tasks",
)
delete_subject_parser.add_argument(
    "--subject_id",
    required=True,
    type=int,
    help=(
        "ID of the subject to delete; its topics and their tasks "
        "will also be deleted"
    ),
)

list_all_tasks_parser = subparsers.add_parser(
    "listalltasks",
    help="List all tasks",
)
# Command handlers

def add_sub_command(args):
    try:
        subject_id = add_subject(args.name)
    except sqlite3.IntegrityError as error:
        if error.sqlite_errorname == "SQLITE_CONSTRAINT_UNIQUE":
            print(f"The subject {args.name} already exists.")
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
                f"Topic {args.name} already exists under subject "
                f"ID {args.subject_id}."
            )
        elif error.sqlite_errorname == "SQLITE_CONSTRAINT_FOREIGNKEY":
            print(f"Subject ID {args.subject_id} does not exist.")
        else:
            raise
    else:
        print(f"Topic {args.name} successfully added.")
        print(f"ID: {topic_id}")


def add_task_command(args):
    try:
        task_id = add_task(args.topic_id, args.name, args.due_date)
    except sqlite3.IntegrityError as error:
        if error.sqlite_errorname == "SQLITE_CONSTRAINT_FOREIGNKEY":
            print(f"Topic ID {args.topic_id} does not exist.")
        else:
            raise
    else:
        print(f"Task {args.name} successfully added.")
        print(f"ID: {task_id}")


def list_sub_command(args):
    for row in list_subjects():
        print(f"ID: {row[0]}  Name: {row[1]}")


def list_topics_command(args):
    for row in list_topics(args.sub_id):
        print(f"ID: {row[0]}  Name: {row[2]}")


def list_tasks_command(args):
    for row in list_tasks(args.topic_id):
        print(
            f"ID: {row[0]}  Name: {row[2]}  "
            f"Due date: {row[3]}  Status: {row[4]}"
        )


def list_due_tasks_command(args):
    tasks = list_due_tasks()

    if not tasks:
        print("No due tasks found.")
        return

    for item in tasks:
        print(
            f"Task ID: {item[0]}, Subject: {item[1]}, "
            f"Topic: {item[2]}, Title: {item[3]}, "
            f"Due date: {item[4]}, Status: {item[5]}"
        )


def update_task_command(args):
    if args.field != "due_date" and args.value is None:
        update_task_parser.error("--value is required for this field")

    if args.field == "status":
        if args.value not in ["not_started", "in_progress", "done"]:
            update_task_parser.error(
                "Status must be one of: not_started, in_progress, done"
            )

    elif args.field == "due_date" and args.value is not None:
        try:
            validate_date(args.value)
        except argparse.ArgumentTypeError as error:
            update_task_parser.error(str(error))

    result = upd_tasks(args.task_id, args.field, args.value)

    if result:
        if args.field == "due_date" and args.value is None:
            print(f"Due date cleared for task ID {args.task_id}.")
        else:
            print(
                f"{args.field} updated to {args.value} "
                f"for task ID {args.task_id}."
            )
    else:
        print("No task with that ID was found.")


def update_topic_command(args):
    try:
        result = upd_topic(args.title, args.topic_id)
    except sqlite3.IntegrityError as error:
        if getattr(error, "sqlite_errorname", None) == "SQLITE_CONSTRAINT_UNIQUE":
            print("A topic with that name already exists under this subject.")
        else:
            raise
    else:
        if result:
            print(f"Topic name updated to {args.title}.")
        else:
            print("No topic with that ID was found.")


def update_subject_command(args):
    try:
        result = upd_subject(args.title, args.subject_id)
    except sqlite3.IntegrityError as error:
        if getattr(error, "sqlite_errorname", None) == "SQLITE_CONSTRAINT_UNIQUE":
            print("A subject with that name already exists.")
        else:
            raise
    else:
        if result:
            print(f"Subject name updated to {args.title}.")
        else:
            print("No subject with that ID was found.")


def delete_task_command(args):
    result = delete_task(args.task_id)

    if result:
        print(f"Task with ID {args.task_id} deleted.")
    else:
        print("No task with that ID exists.")


def delete_topic_command(args):
    result = delete_topic(args.topic_id)

    if result:
        print(
            f"Topic with ID {args.topic_id} and its tasks were deleted."
        )
    else:
        print("No topic with that ID exists.")


def delete_subject_command(args):
    result = delete_subject(args.subject_id)

    if result:
        print(
            f"Subject with ID {args.subject_id}, its topics, "
            "and their tasks were deleted."
        )
    else:
        print("No subject with that ID exists.")


def list_all_tasks_command(args):
    tasks = list_all_tasks()

    if not tasks:
        print("No tasks found.")
        return

    for item in tasks:
        print(
            f"Task ID: {item[0]}, Subject: {item[1]}, "
            f"Topic: {item[2]}, Title: {item[3]}, "
            f"Due date: {item[4]}, Status: {item[5]}"
        )
# Connect each subcommand to its handler

add_sub_parser.set_defaults(func=add_sub_command)
add_topic_parser.set_defaults(func=add_topic_command)
add_task_parser.set_defaults(func=add_task_command)

list_sub_parser.set_defaults(func=list_sub_command)
list_topics_parser.set_defaults(func=list_topics_command)
list_task_parser.set_defaults(func=list_tasks_command)
list_due_tasks_parser.set_defaults(func=list_due_tasks_command)
list_all_tasks_parser.set_defaults(func=list_all_tasks_command)

update_task_parser.set_defaults(func=update_task_command)
update_topic_parser.set_defaults(func=update_topic_command)
update_subject_parser.set_defaults(func=update_subject_command)

delete_task_parser.set_defaults(func=delete_task_command)
delete_topic_parser.set_defaults(func=delete_topic_command)
delete_subject_parser.set_defaults(func=delete_subject_command)


def main():
    args = parser.parse_args()
    make_tables()
    args.func(args)


if __name__ == "__main__":
    main()