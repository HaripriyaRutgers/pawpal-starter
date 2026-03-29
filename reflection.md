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

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
