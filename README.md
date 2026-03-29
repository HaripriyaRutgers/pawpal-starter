# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

### Testing PawPal+


#### What the tests cover

| Test | File | What it checks |
|---|---|---|
| `test_mark_complete_changes_status` | `tests/test_pawpal.py` | `Task.mark_complete()` flips `is_completed` from `False` → `True` |
| `test_add_task_increases_count` | `tests/test_pawpal.py` | `Pet.add_task()` correctly appends to the pet's task list |

#### What is NOT yet tested

The following behaviours are implemented but have no automated coverage:

- `Task.next_occurrence()` — recurring task rescheduling with `timedelta`
- `Scheduler.complete_task()` — auto-appending the next recurrence on completion
- `Scheduler.conflict_warnings()` — same-pet and cross-pet conflict detection
- `Scheduler.get_pending_tasks()` — sort order and filtering by status
- `Owner.get_pet()` / `remove_pet()` — lookup and removal edge cases



### Features

#### Owner & Pet Management
- **Owner profile** — store name, email, and phone; register and remove multiple pets
- **Per-pet data** — track breed, age, gender, weight, walk history, reminders, and a full medical profile (medications, vaccinations, vet appointments)

#### Task Scheduling
- **Sorting by time** — all pending tasks are sorted chronologically using Python's Timsort via `Scheduler.get_pending_tasks()`, so the schedule always reads earliest-first
- **Daily recurrence** — completing a `daily` task auto-schedules the next one using `timedelta(days=1)`; `weekly` uses `timedelta(weeks=1)`; `monthly` uses `timedelta(days=30)` (`Task.next_occurrence()`)
- **Smart overdue rescheduling** — if a recurring task is overdue, the next occurrence anchors from `datetime.now()` rather than the past due date, guaranteeing the new task is always in the future
- **Snooze** — push any task or reminder forward in time without losing it (`Task.snooze()`, `Reminder.snooze()`)

#### Filtering & Querying
- **Filter by status** — retrieve only pending (`Scheduler.get_pending_tasks()`) or only completed tasks (`Scheduler.get_completed_tasks()`), both returned sorted by time
- **Filter by pet** — isolate all tasks for a single named pet across the schedule (`Scheduler.get_tasks_for_pet()`)
- **Filter by type** — pull every `walk`, `vet`, `medication`, etc. task across all pets at once (`Scheduler.get_tasks_by_type()`)

#### Conflict Detection
- **Same-pet conflict warnings** — flags when two tasks for the same pet are scheduled at the same time; displayed as a red `st.error` in the UI with a tip to snooze one
- **Cross-pet conflict warnings** — flags when tasks for different pets overlap, meaning the owner cannot attend both; displayed as a yellow `st.warning` with a suggestion to delegate
- **Non-crashing design** — `Scheduler.conflict_warnings()` always returns a plain list of strings and never raises an exception, so the app continues working regardless of conflicts

#### Streamlit UI
- **Sortable schedule table** — `st.dataframe` renders the full schedule with Pet / Due / Type / Task / Repeats / Status columns, sortable in the browser
- **Filterable task view** — dropdowns let the owner filter by pet and by status (Pending / Completed / All) before generating the schedule
- **Actionable conflict banners** — conflicts surface inside collapsible `st.expander` panels with colour-coded severity and a plain-English tip for each one

