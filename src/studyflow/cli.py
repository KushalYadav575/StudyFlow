import argparse

from .database import add_subject, make_tables

parser = argparse.ArgumentParser(
    prog="sf",
    description="StudyFlow"
)

subparsers = parser.add_subparsers(
    dest="command",
    required=True,
)

add_sub_parser = subparsers.add_parser(
    "add",
    help="Add a subject",
)

add_sub_parser.add_argument(
    "--name",
    required=True,
    help="name of the subject",
)

def add_sub_command(args):
    subject_id = add_subject(args.name)
    print(f"Subject {args.name} successfully added.")
    print(f"ID: {subject_id}")

add_sub_parser.set_defaults(func=add_sub_command)

def main():
     args = parser.parse_args()
     make_tables()
     args.func(args)

if __name__ == "__main__":
    main()