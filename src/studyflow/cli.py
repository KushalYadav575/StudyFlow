import argparse

from .database import (
    add_subject,
    add_task,
    add_topic,
    list_subjects,
    list_tasks,
    list_topics,
    make_tables,
    update_task_status,
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

add_task_parser.add_argument(
    "--due_date",
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


update_task_status_parser = subparsers.add_parser(
    "updtaskstatus",
    help="Update the status of the task"
)

update_task_status_parser.add_argument(
    "--task_id",
    required=True,
    type=int,
    help="id of the respective task"
)

update_task_status_parser.add_argument(
    "--status",
    required=True,
    choices=['not_started', 'in_progress', 'done'],
    help="status of the respective task"
)


def add_sub_command(args):
    subject_id = add_subject(args.name)
    print(f"Subject {args.name} successfully added.")
    print(f"ID: {subject_id}")


def add_topic_command(args):
    topic_id = add_topic(args.subject_id, args.name)
    print(f"topic {args.name} successfully added.")
    print(f"ID: {topic_id}")


def add_task_command(args):
    task_id = add_task(args.topic_id, args.name, args.due_date)
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


def update_taskstatus_command(args):
    result = update_task_status(args.task_id, args.status)
    if result:
        print(f"{args.status} applied to task id:{args.task_id}")
    else:
        print("No task with that id found")


add_sub_parser.set_defaults(func=add_sub_command)
add_topic_parser.set_defaults(func=add_topic_command)
add_task_parser.set_defaults(func=add_task_command)
list_sub_parser.set_defaults(func=list_sub_command)
list_topics_parser.set_defaults(func=list_topics_command)
list_task_parser.set_defaults(func=list_tasks_command)
update_task_status_parser.set_defaults(func=update_taskstatus_command)


def main():
    args = parser.parse_args()
    make_tables()
    args.func(args)


if __name__ == "__main__":
    main()