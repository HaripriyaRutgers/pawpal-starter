from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Optional


# ---------------------------------------------------------------------------
# Task — a single schedulable activity for a pet
# ---------------------------------------------------------------------------

@dataclass
class Task:
    task_id: str
    description: str
    task_type: str          # "walk" | "grooming" | "vet" | "medication" | "vaccination"
    scheduled_time: datetime
    frequency: str          # "once" | "daily" | "weekly" | "monthly"
    is_completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.is_completed = True

    def is_due(self) -> bool:
        """Return True if the task is due now or overdue and not yet completed."""
        return not self.is_completed and self.scheduled_time <= datetime.now()

    def snooze(self, hours: int = 1) -> None:
        """Push the scheduled time forward by the given number of hours."""
        self.scheduled_time += timedelta(hours=hours)

    def __str__(self) -> str:
        """Return a human-readable summary string for the task."""
        status = "✓" if self.is_completed else "pending"
        return (
            f"[{self.task_type.upper()}] {self.description} "
            f"@ {self.scheduled_time:%Y-%m-%d %H:%M} | {self.frequency} | {status}"
        )


# ---------------------------------------------------------------------------
# Supporting data classes
# ---------------------------------------------------------------------------

@dataclass
class Medication:
    name: str
    dosage: str
    frequency: str
    start_date: date
    end_date: Optional[date] = None

    def is_active(self) -> bool:
        """Return True if the medication has no end date or hasn't expired yet."""
        if self.end_date is None:
            return True
        return date.today() <= self.end_date


@dataclass
class Vaccination:
    vaccine_name: str
    date_given: date
    next_due_date: date
    vet_administered: str

    def remind_for_vaccination(self) -> None:
        """Print a reminder if the vaccination is due within 30 days."""
        days_until = (self.next_due_date - date.today()).days
        if days_until <= 30:
            print(
                f"Reminder: {self.vaccine_name} vaccination is due in {days_until} day(s) "
                f"(on {self.next_due_date})."
            )

    def is_overdue(self) -> bool:
        """Return True if today is past the vaccination's next due date."""
        return date.today() > self.next_due_date


@dataclass
class VetAppointment:
    appointment_id: str
    date_time: datetime
    reason: str
    vet_name: str
    notes: str = ""

    def remind_for_appointment(self) -> None:
        """Print a reminder if the appointment is within 3 days."""
        days_until = (self.date_time.date() - date.today()).days
        if 0 <= days_until <= 3:
            print(
                f"Reminder: Vet appointment with {self.vet_name} in {days_until} day(s) "
                f"for '{self.reason}'."
            )

    def is_upcoming(self) -> bool:
        """Return True if the appointment is scheduled in the future."""
        return self.date_time > datetime.now()


@dataclass
class WalkRecord:
    walk_id: str
    date: date
    route: str
    duration_minutes: int
    distance_miles: float
    notes: str = ""

    def remind_for_walk(self) -> None:
        """Print a walk reminder message."""
        print(f"Time for a walk! Suggested route: {self.route} ({self.distance_miles} mi).")

    def summary(self) -> str:
        """Return a one-line summary of the walk's date, route, duration, and distance."""
        return (
            f"{self.date} | Route: {self.route} | "
            f"{self.duration_minutes} min | {self.distance_miles} mi"
        )


@dataclass
class Reminder:
    reminder_id: str
    type: str               # "grooming" | "walk" | "vet" | "medication"
    scheduled_date: datetime
    message: str
    is_recurring: bool = False
    recurring_interval: str = ""    # "daily" | "weekly" | "monthly"
    is_completed: bool = False

    def send_reminder(self) -> None:
        """Print the reminder message to the console."""
        print(f"[{self.type.upper()} REMINDER] {self.message} (due: {self.scheduled_date:%Y-%m-%d %H:%M})")

    def mark_complete(self) -> None:
        """Mark the reminder as completed."""
        self.is_completed = True

    def snooze(self, minutes: int = 30) -> None:
        """Delay the reminder by the given number of minutes."""
        self.scheduled_date += timedelta(minutes=minutes)
        print(f"Reminder snoozed by {minutes} min. New time: {self.scheduled_date:%H:%M}")

    def is_due(self) -> bool:
        """Return True if the reminder is not completed and its scheduled time has passed."""
        return not self.is_completed and self.scheduled_date <= datetime.now()


# ---------------------------------------------------------------------------
# MedicalProfile — owns all health-related records for a pet
# ---------------------------------------------------------------------------

class MedicalProfile:
    def __init__(self, vet_name: str = "", vet_phone: str = "") -> None:
        """Initialize an empty medical profile with optional vet contact details."""
        self.vet_name: str = vet_name
        self.vet_phone: str = vet_phone
        self.medications: list[Medication] = []
        self.vaccinations: list[Vaccination] = []
        self.appointments: list[VetAppointment] = []

    def add_medication(self, medication: Medication) -> None:
        """Add a medication to the pet's profile."""
        self.medications.append(medication)

    def add_vaccination(self, vaccination: Vaccination) -> None:
        """Record a vaccination, keeping the list sorted by date given."""
        self.vaccinations.append(vaccination)
        self.vaccinations.sort(key=lambda v: v.date_given)

    def schedule_appointment(self, appointment: VetAppointment) -> None:
        """Add a vet appointment, keeping the list sorted chronologically."""
        self.appointments.append(appointment)
        self.appointments.sort(key=lambda a: a.date_time)

    def next_appointment(self) -> Optional[VetAppointment]:
        """Return the next upcoming vet appointment, or None if there are none."""
        upcoming = [a for a in self.appointments if a.is_upcoming()]
        return upcoming[0] if upcoming else None

    def remind_for_vet_appointment(self) -> None:
        """Trigger a reminder for the next upcoming appointment."""
        appt = self.next_appointment()
        if appt:
            appt.remind_for_appointment()
        else:
            print("No upcoming vet appointments scheduled.")

    def active_medications(self) -> list[Medication]:
        """Return all medications that are currently active (not expired)."""
        return [m for m in self.medications if m.is_active()]

    def overdue_vaccinations(self) -> list[Vaccination]:
        """Return all vaccinations whose next due date has already passed."""
        return [v for v in self.vaccinations if v.is_overdue()]


# ---------------------------------------------------------------------------
# Pet — stores pet details and a list of tasks
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    breed: str
    age: int
    gender: str
    weight: float
    photo_url: str = ""
    tasks: list[Task] = field(default_factory=list)
    walk_history: list[WalkRecord] = field(default_factory=list)
    medical_profile: MedicalProfile = field(default_factory=MedicalProfile)
    reminders: list[Reminder] = field(default_factory=list)

    # --- Task management ---

    def add_task(self, task: Task) -> None:
        """Add a schedulable task for this pet."""
        self.tasks.append(task)

    def get_pending_tasks(self) -> list[Task]:
        """Return all tasks that are not yet completed."""
        return [t for t in self.tasks if not t.is_completed]

    def get_due_tasks(self) -> list[Task]:
        """Return tasks that are currently due or overdue."""
        return [t for t in self.tasks if t.is_due()]

    def get_tasks_by_type(self, task_type: str) -> list[Task]:
        """Return all tasks matching a given type (e.g. 'walk', 'grooming')."""
        return [t for t in self.tasks if t.task_type == task_type]

    # --- Walk tracking ---

    def add_walk(self, walk: WalkRecord) -> None:
        """Log a completed walk for this pet."""
        self.walk_history.append(walk)

    def last_walk(self) -> Optional[WalkRecord]:
        """Return the most recently logged walk."""
        return self.walk_history[-1] if self.walk_history else None

    # --- Reminders ---

    def add_reminder(self, reminder: Reminder) -> None:
        """Attach a reminder to this pet."""
        self.reminders.append(reminder)

    def get_upcoming_reminders(self) -> list[Reminder]:
        """Return reminders that are not completed and scheduled in the future."""
        now = datetime.now()
        return [
            r for r in self.reminders
            if not r.is_completed and r.scheduled_date >= now
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.breed}, {self.age} yr, {self.weight} lbs)"


# ---------------------------------------------------------------------------
# Owner — manages one or more pets
# ---------------------------------------------------------------------------

class Owner:
    def __init__(self, name: str, email: str = "", phone: str = "") -> None:
        """Initialize an owner with contact details and an empty pet list."""
        self.name: str = name
        self.email: str = email
        self.phone: str = phone
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove a pet by name. Raises ValueError if not found."""
        match = next((p for p in self.pets if p.name == pet_name), None)
        if match is None:
            raise ValueError(f"No pet named '{pet_name}' found.")
        self.pets.remove(match)

    def get_pet(self, pet_name: str) -> Optional[Pet]:
        """Look up a pet by name."""
        return next((p for p in self.pets if p.name == pet_name), None)

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return a flat list of (Pet, Task) pairs aggregated across all pets."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]

    def __str__(self) -> str:
        """Return a summary string showing the owner's name and their pets."""
        pet_names = ", ".join(p.name for p in self.pets) or "none"
        return f"Owner: {self.name} | Pets: {pet_names}"


# ---------------------------------------------------------------------------
# Scheduler — the "brain" that retrieves, organizes, and manages tasks
#
# How it retrieves tasks:
#   owner.get_all_tasks() returns a flat list of (Pet, Task) pairs by
#   iterating owner.pets and collecting each pet's task list. The Scheduler
#   never reaches into Pet directly — it always goes through Owner, keeping
#   the data flow:  Scheduler → Owner → [Pet, Pet, ...] → tasks
# ---------------------------------------------------------------------------

class Scheduler:
    def __init__(self, owner: Owner) -> None:
        """Initialize the Scheduler with the Owner whose pets' tasks it will manage."""
        self.owner: Owner = owner

    def _all_tasks(self) -> list[tuple[Pet, Task]]:
        """Delegate to Owner, which aggregates tasks from every pet."""
        return self.owner.get_all_tasks()

    def get_due_tasks(self) -> list[tuple[Pet, Task]]:
        """Return all (pet, task) pairs that are currently due or overdue."""
        return [(pet, task) for pet, task in self._all_tasks() if task.is_due()]

    def get_tasks_by_type(self, task_type: str) -> list[tuple[Pet, Task]]:
        """Filter tasks across all pets by type (e.g. 'grooming', 'vet')."""
        return [
            (pet, task) for pet, task in self._all_tasks()
            if task.task_type == task_type
        ]

    def get_pending_tasks(self) -> list[tuple[Pet, Task]]:
        """Return all incomplete tasks across every pet, sorted by due time."""
        pending = [
            (pet, task) for pet, task in self._all_tasks()
            if not task.is_completed
        ]
        return sorted(pending, key=lambda pair: pair[1].scheduled_time)

    def run_reminders(self) -> None:
        """Print reminders for every task that is currently due."""
        due = self.get_due_tasks()
        if not due:
            print("No tasks due right now.")
            return
        for pet, task in due:
            print(f"  [{pet.name}] {task}")

    def complete_task(self, task_id: str) -> bool:
        """Find a task by ID across all pets, mark it complete, and return True; False if not found."""
        for _, task in self._all_tasks():
            if task.task_id == task_id:
                task.mark_complete()
                return True
        return False

    def summary(self) -> None:
        """Print a full task summary grouped by pet."""
        print(f"=== Schedule for {self.owner.name}'s pets ===")
        for pet in self.owner.pets:
            print(f"\n{pet.name}:")
            if not pet.tasks:
                print("  No tasks scheduled.")
            for task in sorted(pet.tasks, key=lambda t: t.scheduled_time):
                print(f"  {task}")
