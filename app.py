import uuid
from datetime import datetime, timedelta

import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session-state vault — initialise objects only once per session
# ---------------------------------------------------------------------------

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="", email="", phone="")

if "owner_saved" not in st.session_state:
    st.session_state.owner_saved = False

# Convenience alias — mutating this also mutates the vault
owner: Owner = st.session_state.owner

# ---------------------------------------------------------------------------
# Section 1 — Owner setup
# ---------------------------------------------------------------------------

st.subheader("1. Owner Profile")

with st.form("owner_form"):
    col1, col2 = st.columns(2)
    with col1:
        owner_name  = st.text_input("Your name",  value=owner.name)
        owner_email = st.text_input("Email",       value=owner.email)
    with col2:
        owner_phone = st.text_input("Phone",       value=owner.phone)

    if st.form_submit_button("Save owner"):
        # Mutate the object already in session_state — no re-creation needed
        owner.name  = owner_name
        owner.email = owner_email
        owner.phone = owner_phone
        st.session_state.owner_saved = True

if st.session_state.owner_saved:
    st.success(f"Owner saved: **{owner.name}**")

st.divider()

# ---------------------------------------------------------------------------
# Section 2 — Add a Pet
#
# Submitting the form calls owner.add_pet(Pet(...)), which appends the new
# Pet to owner.pets (stored in session_state). Streamlit reruns the script
# after every form submission, so the pet list below re-reads owner.pets
# and automatically shows the new entry — no extra state needed.
# ---------------------------------------------------------------------------

st.subheader("2. Add a Pet")

with st.form("add_pet_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        pet_name   = st.text_input("Pet name")
        pet_breed  = st.text_input("Breed")
        pet_age    = st.number_input("Age (years)", min_value=0, max_value=30, value=1)
    with col2:
        pet_gender = st.selectbox("Gender", ["Female", "Male"])
        pet_weight = st.number_input("Weight (lbs)", min_value=0.1, max_value=300.0, value=10.0)

    add_pet_btn = st.form_submit_button("Add pet")

if add_pet_btn:
    if not pet_name.strip():
        st.warning("Please enter a pet name.")
    else:
        new_pet = Pet(
            name=pet_name.strip(),
            breed=pet_breed.strip(),
            age=int(pet_age),
            gender=pet_gender,
            weight=float(pet_weight),
        )
        owner.add_pet(new_pet)          # <-- Phase 2 method
        st.success(f"Added **{new_pet.name}** to {owner.name or 'your'} profile!")

# Show all pets currently registered
if owner.pets:
    st.markdown("**Registered pets:**")
    for pet in owner.pets:
        st.markdown(f"- {pet.name} &nbsp;·&nbsp; {pet.breed} &nbsp;·&nbsp; {pet.age} yr &nbsp;·&nbsp; {pet.weight} lbs")
else:
    st.info("No pets added yet.")

st.divider()

# ---------------------------------------------------------------------------
# Section 3 — Schedule a Task
#
# Submitting this form calls pet.add_task(Task(...)) directly on the Pet
# object that already lives inside owner.pets (and therefore session_state).
# Because Pet is a mutable object, the task is appended in-place and
# persists for the rest of the session without any extra bookkeeping.
# ---------------------------------------------------------------------------

st.subheader("3. Schedule a Task")

if not owner.pets:
    st.info("Add at least one pet above before scheduling tasks.")
else:
    with st.form("add_task_form", clear_on_submit=True):
        pet_names    = [p.name for p in owner.pets]
        selected_pet = st.selectbox("Assign to pet", pet_names)

        col1, col2 = st.columns(2)
        with col1:
            task_desc = st.text_input("Task description")
            task_type = st.selectbox(
                "Task type",
                ["walk", "grooming", "vet", "medication", "vaccination"],
            )
        with col2:
            task_freq = st.selectbox("Frequency", ["once", "daily", "weekly", "monthly"])
            hours_from_now = st.number_input(
                "Due in (hours from now)", min_value=0.0, max_value=168.0, value=1.0, step=0.5
            )

        add_task_btn = st.form_submit_button("Add task")

    if add_task_btn:
        if not task_desc.strip():
            st.warning("Please enter a task description.")
        else:
            # Find the chosen Pet object inside owner.pets
            target_pet = owner.get_pet(selected_pet)   # <-- Phase 2 method

            new_task = Task(
                task_id=str(uuid.uuid4())[:8],
                description=task_desc.strip(),
                task_type=task_type,
                scheduled_time=datetime.now() + timedelta(hours=hours_from_now),
                frequency=task_freq,
            )
            target_pet.add_task(new_task)               # <-- Phase 2 method
            st.success(f"Task **'{new_task.description}'** added to {target_pet.name}!")

    # --- Filter controls ---
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        filter_pet = st.selectbox(
            "Filter by pet", ["All pets"] + [p.name for p in owner.pets], key="filter_pet"
        )
    with col_f2:
        filter_status = st.selectbox(
            "Filter by status", ["Pending", "Completed", "All"], key="filter_status"
        )

    # Build filtered task list
    def _status_match(task: Task) -> bool:
        if filter_status == "Pending":
            return not task.is_completed
        if filter_status == "Completed":
            return task.is_completed
        return True

    filtered_pets = (
        [p for p in owner.pets if p.name == filter_pet]
        if filter_pet != "All pets"
        else owner.pets
    )

    any_shown = False
    for pet in filtered_pets:
        tasks = sorted(
            [t for t in pet.tasks if _status_match(t)],
            key=lambda x: x.scheduled_time,
        )
        if tasks:
            any_shown = True
            st.markdown(f"**{pet.name}'s {filter_status.lower()} tasks:**")
            for t in tasks:
                due_str = t.scheduled_time.strftime("%b %d  %I:%M %p")
                status_icon = "✅" if t.is_completed else ("🔴 OVERDUE" if t.is_due() else "")
                st.markdown(
                    f"&nbsp;&nbsp;`{due_str}` &nbsp; **[{t.task_type}]** {t.description} "
                    f"*({t.frequency})* {status_icon}"
                )
    if not any_shown:
        st.info("No tasks match the selected filters.")

st.divider()

# ---------------------------------------------------------------------------
# Section 4 — Generate Schedule
#
# Scheduler.get_pending_tasks() calls owner.get_all_tasks() which iterates
# owner.pets and flattens every pet's task list into (Pet, Task) pairs.
# ---------------------------------------------------------------------------

st.subheader("4. Today's Schedule")

if st.button("Generate schedule"):
    if not owner.pets or not any(p.tasks for p in owner.pets):
        st.warning("Add at least one pet and one task first.")
    else:
        scheduler = Scheduler(owner)                    # <-- Phase 2 class
        pending   = scheduler.get_pending_tasks()       # <-- Phase 2 method

        # Conflict detection
        conflicts = scheduler.detect_conflicts(window_minutes=30)
        if conflicts:
            st.warning(f"⚠️ {len(conflicts)} scheduling conflict(s) detected (tasks within 30 min of each other):")
            for pet, ta, tb in conflicts:
                st.markdown(
                    f"&nbsp;&nbsp;**{pet.name}**: `{ta.task_type}` @ "
                    f"{ta.scheduled_time:%I:%M %p} conflicts with `{tb.task_type}` @ "
                    f"{tb.scheduled_time:%I:%M %p}"
                )

        if not pending:
            st.success("All tasks are complete — nothing left to do!")
        else:
            st.markdown(f"### {owner.name or 'Your'}'s schedule ({len(pending)} task(s))")
            for pet, task in pending:
                due_str  = task.scheduled_time.strftime("%b %d  %I:%M %p")
                is_due   = task.is_due()
                label    = "🔴 OVERDUE" if is_due else f"🕐 {due_str}"
                recurring_badge = " ♻️" if task.frequency != "once" else ""
                st.markdown(
                    f"**{pet.name}** &nbsp;|&nbsp; {label} &nbsp;|&nbsp; "
                    f"`{task.task_type}` — {task.description} *({task.frequency})*{recurring_badge}"
                )
