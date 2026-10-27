# StudyFlow

StudyFlow is a local study planner built with Python and SQLite. It lets you organize subjects into topics, add tasks with optional due dates, track task status, and view tasks due today or earlier.

## Requirements

- Python 3.11 or later

## Setup

From the project root, install StudyFlow in editable mode:

    python -m pip install -e .

The command line app is called `sf`.

## Commands

### Add a subject

    sf addsub --name "Math"

### List subjects

    sf listsubs

### Add a topic to a subject

Use the subject’s ID from `sf listsubs`:

    sf addtopic --subject_id 1 --name "Algebra"

### List topics in a subject

    sf listtopics --sub_id 1

### Add a task to a topic

The due date is optional and must use the `YYYY-MM-DD` format:

    sf addtask --topic_id 1 --name "Practice equations" --due_date 2026-10-30

### List tasks in a topic

    sf listtasks --topic_id 1

### Update a task’s status

Choose `not_started`, `in_progress`, or `done`:

    sf updtaskstatus --task_id 1 --status in_progress

### List due tasks

This lists unfinished tasks due today or earlier:

    sf list_due_tasks

## Data storage

StudyFlow stores its data in a local SQLite database. Subjects, topics, and tasks are saved between runs.

### Update a task

Change one field at a time. Valid fields are `title`, `status`, and `due_date`.

    sf updtask --task_id 1 --field title --value "Practice equations"
    sf updtask --task_id 1 --field status --value done
    sf updtask --task_id 1 --field due_date --value 2026-10-30

Clear a task's due date by leaving out `--value`:

    sf updtask --task_id 1 --field due_date

### Update a topic name

    sf updtitle --topic_id 1 --title "Geometry"

### Update a subject name

    sf updsubject --subject_id 1 --title "Physics"

### Delete a task

Use the task’s ID to delete it:

    sf deltask --task_id 1