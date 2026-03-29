from datetime import datetime, timedelta
from pawpal_system import (
    Owner, Pet, Task, WalkRecord, Reminder, MedicalProfile,
    Medication, Vaccination, VetAppointment,
)

# ---------------------------------------------------------------------------
# Helper — build a datetime relative to now so the demo always looks current
# ---------------------------------------------------------------------------

def in_hours(h: float) -> datetime:
    return datetime.now() + timedelta(hours=h)


# ---------------------------------------------------------------------------
# Create Owner
# ---------------------------------------------------------------------------

owner = Owner(name="Haripriya", email="haripriya@email.com", phone="555-1234")

# ---------------------------------------------------------------------------
# Create Pets
# ---------------------------------------------------------------------------

luna = Pet(
    name="Luna",
    breed="Golden Retriever",
    age=3,
    gender="Female",
    weight=55.0,
)

mochi = Pet(
    name="Mochi",
    breed="Shih Tzu",
    age=5,
    gender="Male",
    weight=12.5,
)

owner.add_pet(luna)
owner.add_pet(mochi)

# ---------------------------------------------------------------------------
# Add Tasks  (mix of types and times across both pets)
# ---------------------------------------------------------------------------

# Luna's tasks
luna.add_task(Task(
    task_id="t1",
    description="Morning walk around the park",
    task_type="walk",
    scheduled_time=in_hours(-1),        # 1 hour ago → already due
    frequency="daily",
))

# Pin shared times so conflict detection sees identical datetime values
SAME_PET_TIME  = in_hours(2)   # both Luna tasks → same-pet conflict
CROSS_PET_TIME = in_hours(6)   # one Luna + one Mochi task → cross-pet conflict

luna.add_task(Task(
    task_id="t2",
    description="Give heartworm medication",
    task_type="medication",
    scheduled_time=SAME_PET_TIME,       # 2 hours from now
    frequency="monthly",
))

luna.add_task(Task(
    task_id="t3",
    description="Grooming appointment — bath and trim",
    task_type="grooming",
    scheduled_time=in_hours(5),         # 5 hours from now
    frequency="weekly",
))

# Luna — same-pet conflict: pinned to the exact same datetime as t2
luna.add_task(Task(
    task_id="t6",
    description="Rabies booster shot",
    task_type="vaccination",
    scheduled_time=SAME_PET_TIME,       # identical to t2 → same-pet conflict
    frequency="once",
))

# Mochi's tasks
mochi.add_task(Task(
    task_id="t4",
    description="Evening walk around the block",
    task_type="walk",
    scheduled_time=CROSS_PET_TIME,      # 6 hours from now
    frequency="daily",
))

mochi.add_task(Task(
    task_id="t5",
    description="Vet check-up — annual wellness exam",
    task_type="vet",
    scheduled_time=in_hours(24),        # tomorrow
    frequency="once",
))

# Cross-pet conflict: Luna pinned to the same datetime as Mochi's t4
luna.add_task(Task(
    task_id="t7",
    description="Nail trim at the groomer",
    task_type="grooming",
    scheduled_time=CROSS_PET_TIME,      # identical to t4 → cross-pet conflict
    frequency="monthly",
))

# ---------------------------------------------------------------------------
# Add a Walk Record and a Reminder to show those features work too
# ---------------------------------------------------------------------------

luna.add_walk(WalkRecord(
    walk_id="w1",
    date=datetime.now().date(),
    route="Riverside Trail",
    duration_minutes=30,
    distance_miles=1.8,
    notes="Luna chased a squirrel but was a good girl overall.",
))

mochi.add_reminder(Reminder(
    reminder_id="r1",
    type="grooming",
    scheduled_date=in_hours(48),
    message="Book Mochi's next haircut",
    is_recurring=True,
    recurring_interval="monthly",
))

# ---------------------------------------------------------------------------
# Medical profile for Luna
# ---------------------------------------------------------------------------

luna.medical_profile = MedicalProfile(vet_name="Dr. Patel", vet_phone="555-9876")
luna.medical_profile.add_medication(Medication(
    name="Heartgard",
    dosage="1 chew",
    frequency="monthly",
    start_date=datetime.now().date(),
))
luna.medical_profile.add_vaccination(Vaccination(
    vaccine_name="Rabies",
    date_given=datetime(2025, 3, 1).date(),
    next_due_date=datetime(2026, 3, 1).date(),
    vet_administered="Dr. Patel",
))

# ---------------------------------------------------------------------------
# Print Today's Schedule
# ---------------------------------------------------------------------------

DIVIDER = "─" * 52

print()
print("=" * 52)
print("         PAWPAL+  —  TODAY'S SCHEDULE")
print(f"         Owner: {owner.name}")
print(f"         {datetime.now():%A, %B %d %Y  %I:%M %p}")
print("=" * 52)

for pet in owner.pets:
    print()
    print(f"  {pet.name}  ({pet.breed}, {pet.age} yrs, {pet.weight} lbs)")
    print(f"  {DIVIDER}")

    pending = sorted(pet.get_pending_tasks(), key=lambda t: t.scheduled_time)

    if not pending:
        print("  No pending tasks — all done for today!")
    else:
        for task in pending:
            due_label = "** OVERDUE **" if task.is_due() else task.scheduled_time.strftime("%I:%M %p")
            print(f"  [{due_label:>13}]  {task.task_type.upper():<12} {task.description}")

    # Show last walk if logged
    last = pet.last_walk()
    if last:
        print()
        print(f"  Last walk: {last.summary()}")

    # Show upcoming reminders
    upcoming = pet.get_upcoming_reminders()
    if upcoming:
        print()
        print("  Upcoming reminders:")
        for r in upcoming:
            print(f"    • [{r.type}] {r.message}  ({r.scheduled_date:%b %d, %I:%M %p})")

print()
print("=" * 52)
print("  OVERDUE TASKS ACROSS ALL PETS")
print("=" * 52)

from pawpal_system import Scheduler
scheduler = Scheduler(owner)
scheduler.run_reminders()

print()
print("=" * 52)
print("  CONFLICT DETECTION")
print("=" * 52)
# conflict_warnings() returns strings — never raises, safe to call always.
# window_minutes=0 flags tasks at the exact same scheduled time.
warnings = scheduler.conflict_warnings(window_minutes=0)
if warnings:
    for w in warnings:
        print(f"  {w}")
else:
    print("  No scheduling conflicts found.")

print()
print("=" * 52)
print("  FULL SCHEDULE (sorted by time)")
print("=" * 52)
scheduler.summary()
print()
