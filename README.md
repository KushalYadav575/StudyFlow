# StudyFlow

StudyFlow is a local study planner built with Python and SQLite. It lets you organize subjects into topics, manage tasks and due dates, track task status, view progress, filter tasks, and import or export your planner data as CSV.

## Requirements

- Python 3.11 or later

## Setup

From the project root, install StudyFlow in editable mode:

    python -m pip install -e .

The command-line app is called `sf`.

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

### Update a task

Change one field at a time. Valid fields are `title`, `status`, and `due_date`.

    sf updtask --task_id 1 --field title --value "Practice equations"
    sf updtask --task_id 1 --field status --value done
    sf updtask --task_id 1 --field due_date --value 2026-10-30

Clear a task’s due date by leaving out `--value`:

    sf updtask --task_id 1 --field due_date

### Update a topic name

    sf updtitle --topic_id 1 --title "Geometry"

### Update a subject name

    sf updsubject --subject_id 1 --title "Physics"

### Delete a task

Use the task’s ID to delete it:

    sf deltask --task_id 1

### Delete a topic

Use the topic’s ID to delete it. Its tasks are deleted with it.

    sf deltopic --topic_id 1

### Delete a subject

Use the subject’s ID to delete it. Its topics and tasks are deleted with it.

    sf delsub --subject_id 1

### List due tasks

This lists unfinished tasks due today or earlier:

    sf list_due_tasks

### View all tasks

Show every task with its subject, topic, due date, and status:

    sf listalltasks

Filter the list by status:

    sf listalltasks --status in_progress

Available statuses are `not_started`, `in_progress`, and `done`.

### View subject progress

    sf subject_progress --subject_id 1

This displays the subject’s name and the percentage of its tasks marked as done.

### Export tasks to CSV

    sf export --file studyflow_tasks.csv

The CSV includes task ID, subject, topic, title, due date, and status. Exporting with no tasks creates a CSV containing the headers.

### Import tasks from CSV

    sf import --file studyflow_tasks.csv

The import expects the CSV headers produced by the export command. It creates subjects and topics as needed, then adds the tasks. Existing subjects and topics are reused; imported tasks are added as new tasks.

## Data storage

StudyFlow stores its data in a local SQLite database. Subjects, topics, and tasks are saved between runs.