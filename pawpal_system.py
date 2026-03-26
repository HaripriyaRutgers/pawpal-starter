from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


# ---------------------------------------------------------------------------
# Simple data-holding classes — use @dataclass for clean, boilerplate-free code
# ---------------------------------------------------------------------------

@dataclass
class Medication:
    name: str
    dosage: str
    frequency: str
    start_date: date
    end_date: Optional[date] = None


@dataclass
class Vaccination:
    vaccine_name: str
    date_given: date
    next_due_date: date
    vet_administered: str

    def remind_for_vaccination(self) -> None:
        pass


@dataclass
class VetAppointment:
    appointment_id: str
    date_time: datetime
    reason: str
    vet_name: str
    notes: str = ""

    def remind_for_appointment(self) -> None:
        pass


@dataclass
class WalkRecord:
    walk_id: str
    date: date
    route: str
    duration_minutes: int
    distance_miles: float
    notes: str = ""

    def remind_for_walk(self) -> None:
        pass


@dataclass
class Reminder:
    reminder_id: str
    type: str                        # e.g. "grooming", "walk", "vet"
    scheduled_date: datetime
    message: str
    is_recurring: bool = False
    recurring_interval: str = ""     # e.g. "weekly", "monthly"
    is_completed: bool = False

    def send_reminder(self) -> None:
        pass

    def mark_complete(self) -> None:
        pass

    def snooze(self, minutes: int) -> None:
        pass


# ---------------------------------------------------------------------------
# MedicalProfile — owns all health-related records for a pet
# ---------------------------------------------------------------------------

class MedicalProfile:
    def __init__(self, vet_name: str = "", vet_phone: str = "") -> None:
        self.vet_name: str = vet_name
        self.vet_phone: str = vet_phone
        self.medications: list[Medication] = []
        self.vaccinations: list[Vaccination] = []
        self.appointments: list[VetAppointment] = []

    def add_medication(self, medication: Medication) -> None:
        pass

    def add_vaccination(self, vaccination: Vaccination) -> None:
        pass

    def schedule_appointment(self, appointment: VetAppointment) -> None:
        pass

    def remind_for_vet_appointment(self) -> None:
        pass


# ---------------------------------------------------------------------------
# Pet — the central class that ties everything together
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    breed: str
    age: int
    gender: str
    weight: float
    photo_url: str = ""
    walk_history: list[WalkRecord] = field(default_factory=list)
    medical_profile: MedicalProfile = field(default_factory=MedicalProfile)
    reminders: list[Reminder] = field(default_factory=list)

    def add_walk(self, walk: WalkRecord) -> None:
        pass

    def add_reminder(self, reminder: Reminder) -> None:
        pass

    def get_upcoming_reminders(self) -> list[Reminder]:
        pass
