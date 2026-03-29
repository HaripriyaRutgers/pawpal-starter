# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
    The app allows the user to:
        - Input their pet's basic information first like name, breed, age etc
        - Track each time they take their pet on a walk + the route and duration
        - Track their medical history + meds + vaccinations + vet appointment dates
        - Put in remainders for when it needs grooming/ hair cut etc.

- What classes did you include, and what responsibilities did you assign to each?
    Pet is the central class — everything links back to it
    WalkRecord- captures each individual walk with route, duration, and distance
    MedicalProfile-  groups all health-related data into one place, acting as a container for meds, vaccines, and vet visits
    Medication, Vaccination, and VetAppointment are separate classes but under MedicalProfile since they each have distinct fields and lifecycles
    Reminder- is a flexible, reusable class — supports one-time or recurring reminders for walks, grooming, or vet appointments, driven by a type field (e.g. "grooming", "walk", "vet")
    

    Attributes- dog basic information, walk info, medical info
    Methods- Remind that it is time for walks, time for grooming, time for vet appts/ vaccinations

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, several changes were made during implementation:

The most significant change was adding a dedicated `Scheduler` class that was not in the initial UML. Originally, scheduling logic was spread across `Pet` and `Owner`. Pulling it into its own class gave one place to handle sorting, filtering, conflict detection, and recurring task management — each of which would have cluttered `Pet` if left there.

A second change was adding `Task.next_occurrence()`. The initial design had `Task` as a passive data container. During implementation it became clear that the task itself was the right place to know how to compute its own next date, since it owns `frequency` and `scheduled_time`. This kept the recurrence logic self-contained and testable in isolation.

A third change was splitting conflict detection into two methods: `detect_conflicts()` returning structured tuples (used by the app for programmatic checks) and `conflict_warnings()` returning plain strings (used by the UI for display). The initial design had no conflict detection at all — it emerged as a necessary feature once two tasks were accidentally scheduled at the same time during testing.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?

The scheduler considers three constraints:
1. **Time** — every task has a `scheduled_time`; the schedule is always sorted earliest-first so the owner sees what needs doing next
2. **Recurrence** — frequency (`daily`, `weekly`, `monthly`, `once`) determines whether completing a task auto-generates the next instance and when
3. **Conflicts** — two tasks at the same time for the same pet (same-pet conflict) or for different pets (cross-pet conflict, meaning the owner can't be in two places) both trigger warnings

- How did you decide which constraints mattered most?

Time was the foundation — without a reliable sort order the schedule is unusable. Recurrence came second because a pet care app without auto-repeating daily tasks (walks, medication) would require constant manual re-entry. Conflict detection came last but proved the most visible feature in the UI, since a silent double-booking is worse than no schedule at all.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The Scheduler chose always-correct over always-fast — acceptable for a single-owner pet app, but would need a caching layer before scaling to many pets or frequent polling.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

AI was used across every phase but with a different role in each:
- **Design phase** — used to pressure-test the UML, asking "what responsibilities does this class have that it shouldn't?" which surfaced the decision to extract `Scheduler` from `Owner`
- **Implementation phase** — used to generate method bodies once the signature and contract were agreed (e.g. "write `next_occurrence()` that returns `None` for `once` and a new Task shifted by `timedelta` for recurring frequencies")
- **Debugging** — used to explain why `window_minutes=0` missed conflicts when `in_hours(2)` was called separately for each task (microsecond drift between calls)
- **Refactoring** — used to suggest `itertools.combinations` as a cleaner replacement for the nested `range(len(...))` index loops in conflict detection

- What kinds of prompts or questions were most helpful?

The most effective prompts were **specific and constrained**: "given this method signature and these two inputs, what should it return?" worked far better than "how do I detect conflicts?". Asking AI to explain a tradeoff ("what does this design give up?") consistently surfaced considerations that weren't obvious — the stale-data tradeoff in `_all_tasks()` came from exactly this kind of question. Asking for the "lightweight" version of a feature also produced simpler, more readable code than open-ended requests.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

The initial AI suggestion for `next_occurrence()` used `self.scheduled_time + delta` as the base for the new task's due date. This was rejected and modified. The problem: if a daily task was three days overdue and you completed it today, the next occurrence would be calculated as three-days-ago plus one day — placing it two days in the past, still overdue before it was even created.

The fix was `base = max(self.scheduled_time, datetime.now())` — use the original scheduled time if the task is on time (to preserve the daily cadence), but anchor from now if the task is overdue. This one-line change was not in the AI's first draft.

- How did you evaluate or verify what the AI suggested?

The check was a mental walkthrough: "if a daily walk was scheduled Monday and I complete it Thursday, what date does the formula produce?" The original formula gave Tuesday (Monday + 1 day), which is in the past. The corrected formula gives Friday (Thursday + 1 day), which is in the future. Running `main.py` with a task pinned to `in_hours(-72)` confirmed the fix behaved correctly before it was committed.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?

Two behaviors were covered by automated tests in `tests/test_pawpal.py`:
1. `Task.mark_complete()` correctly flips `is_completed` from `False` to `True`
2. `Pet.add_task()` correctly increments the pet's task count

- Why were these tests important?

These are the lowest-level building blocks that every other feature depends on. If `mark_complete()` silently failed, recurring task auto-scheduling would appear to work but would generate duplicate tasks indefinitely. If `add_task()` failed, no task would ever appear in the schedule regardless of what the UI showed. Testing the foundation first gave confidence that bugs in higher-level features (sorting, conflict detection) were in the algorithm, not in the data layer.

**b. Confidence**

- How confident are you that your scheduler works correctly?
#### Confidence Level

(2 / 5)

The two existing tests pass cleanly and confirm basic object mutation works.
However, every algorithm added in this project — recurring scheduling, conflict
detection, filtering, and sorting — is entirely untested. A bug in any of those
paths would not be caught by the test suite today.
- What edge cases would you test next if you had more time?

In priority order:
1. `next_occurrence()` with an overdue task — confirm the new due date is always in the future
2. `conflict_warnings()` — one test for a same-pet clash, one for a cross-pet clash, one for no conflicts returning an empty list
3. `get_pending_tasks()` — confirm tasks come back sorted earliest-first even when added out of order
4. `complete_task()` with a `daily` task — confirm a new task appears in the pet's list with a due date exactly one day ahead
5. `Owner.remove_pet()` with a name that doesn't exist — confirm `ValueError` is raised rather than silently doing nothing

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The conflict detection design. Having two separate methods — `detect_conflicts()` returning structured data for programmatic use and `conflict_warnings()` returning plain strings for the UI — kept the logic clean and made it straightforward to display same-pet conflicts as red `st.error` banners and cross-pet conflicts as yellow `st.warning` banners with different actionable tips for each. The non-crashing guarantee (always returns a list, never raises) also made it safe to call on every schedule generation without defensive try/except blocks in the UI.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

Two things:

First, test coverage. The core algorithms — recurring scheduling, conflict detection, sorted filtering — have zero automated tests. This was the biggest risk in the project: every feature worked when manually verified in `main.py`, but a future change to `next_occurrence()` or `conflict_warnings()` could silently break behavior with no safety net.

Second, the `Scheduler` caches nothing. Every call to `get_pending_tasks()`, `conflict_warnings()`, and `run_reminders()` independently rebuilds the full task list from scratch. For the current scale (2 pets, ~7 tasks) this is fine, but adding a simple `refresh()` method that computed `_pending` once per button-press would eliminate redundant work and make the data flow explicit.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

AI is most useful when you already know what you want and can describe it precisely — and least useful when you haven't decided yet. Every time a prompt was vague ("add conflict detection"), the suggestion required significant modification. Every time the contract was stated clearly ("write a method that takes two pending tasks and returns True if their scheduled times are within N minutes of each other, without raising an exception"), the output was close to production-ready.

The role of "lead architect" meant making every design decision before asking AI to implement it: which class owns this method, what does it return, what are the edge cases, what should it never do. AI handled the translation from decision to working code quickly and accurately. But the decisions themselves — where to put `next_occurrence()`, why `conflict_warnings()` returns strings instead of raising, why `Scheduler` never touches `Pet` directly — those required human judgment and could not be delegated.

**d. AI Strategy — VS Code Copilot**

- Which Copilot features were most effective for building your scheduler?

Inline completions were most effective for method bodies where the signature made the intent unambiguous — `is_due()`, `is_active()`, and `is_overdue()` were completed almost exactly as-is. The chat interface was more useful for design questions ("what's the tradeoff of rebuilding the task list on every call vs caching it?") and for explaining why a specific bug occurred (the microsecond drift issue with `in_hours()` being called twice for the same conflict time).

- Give one example of an AI suggestion you rejected or modified to keep your system design clean.

Copilot's first suggestion for conflict detection was a single method that both detected conflicts and printed warnings directly to the console. This was rejected because it mixed detection logic with output formatting — making it impossible to reuse detection in the Streamlit UI without also triggering console prints. The method was split: `detect_conflicts()` returns structured data, `conflict_warnings()` returns strings, and neither one prints anything. The caller decides what to do with the result.

- How did using separate chat sessions for different phases help you stay organized?

Each session had a clear scope — UML review, core class implementation, recurring logic, conflict detection, UI wiring — which prevented earlier decisions from being relitigated. When the conflict detection session started, the class structure was already fixed, so AI suggestions were constrained to fit the existing design rather than proposing a different architecture. Separate sessions also made it easy to review what each phase produced before moving on, rather than having a single long conversation where earlier context got buried.

- Summarize what you learned about being the "lead architect" when collaborating with powerful AI tools.

The lead architect's job is to make decisions that AI cannot: what belongs in this class versus that one, what invariants must always hold, what the system should refuse to do. AI executes those decisions faster and with fewer syntax errors than writing by hand. But if you skip the architecture step and ask AI to design as well as implement, you get code that works for the example in front of it but doesn't compose cleanly — methods in the wrong class, missing edge case handling, no clear separation between layers. The discipline of deciding first, then prompting, produced a system where each class had one clear responsibility and could be read independently of the others.
