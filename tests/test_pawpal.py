import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime, timedelta
from pawpal_system import Task, Pet


def make_task(task_id: str = "t1", hours_from_now: float = 1.0) -> Task:
    """Helper to create a Task without repeating boilerplate in every test."""
    return Task(
        task_id=task_id,
        description="Test task",
        task_type="walk",
        scheduled_time=datetime.now() + timedelta(hours=hours_from_now),
        frequency="daily",
    )


def make_pet() -> Pet:
    """Helper to create a minimal Pet."""
    return Pet(name="Buddy", breed="Labrador", age=2, gender="Male", weight=60.0)


# ---------------------------------------------------------------------------
# Test 1 — Task completion changes status
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    task = make_task()

    assert task.is_completed is False, "Task should start incomplete"

    task.mark_complete()

    assert task.is_completed is True, "Task should be completed after mark_complete()"


# ---------------------------------------------------------------------------
# Test 2 — Adding a task increases the pet's task count
# ---------------------------------------------------------------------------

def test_add_task_increases_count():
    pet = make_pet()

    assert len(pet.tasks) == 0, "Pet should start with no tasks"

    pet.add_task(make_task("t1"))
    assert len(pet.tasks) == 1, "Pet should have 1 task after first add"

    pet.add_task(make_task("t2"))
    assert len(pet.tasks) == 2, "Pet should have 2 tasks after second add"


# ---------------------------------------------------------------------------
# Run with:  python -m pytest tests/test_pawpal.py -v
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    test_mark_complete_changes_status()
    print("PASS  test_mark_complete_changes_status")

    test_add_task_increases_count()
    print("PASS  test_add_task_increases_count")
