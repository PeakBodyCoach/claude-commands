---
description: Onboard a new client end-to-end — scaffolds the vault folder, profile file (Personal Info, Goals, Training Strategy, Nutrition Strategy, Monitoring & Accountability), Programmes.md stub, Nutrition Plan (via macro-planner or stub), clients.csv row, and tasks.md section from intake form responses or conversation. Replaces import-client. Use when Tom says "add a new client", "onboard [name]", "set up [name]", or pastes intake notes.
---

# New Client

End-to-end onboarding from intake form (or conversation) to fully scaffolded client. Writes: clients.csv row, folder + profile file, Programmes.md stub, Nutrition Plan (real or stub), tasks.md section.

## Data paths

```
clients.csv  → C:\Users\Tom\Documents\Home Vault\2 - Business\Clients\clients.csv
clients dir  → C:\Users\Tom\Documents\Home Vault\2 - Business\Clients\
tasks.md     → C:\Users\Tom\Documents\Home Vault\2 - Business\Operations\tasks.md
intake form  → C:\Users\Tom\Documents\Home Vault\2 - Business\Coaching\SOPs\Onboarding Form.md
```

---

## Step 0 — Mode select

Ask Tom which mode this is, unless the message already makes it obvious:

- **"Full intake"** — Tom has the intake form responses (filled-out questionnaire). Paste them in and the skill maps every field into the profile.
- **"Fast add"** — just a name and a few basics. Skill scaffolds the minimum and flags everything else as TBC.

In Full intake mode, ask Tom to paste the completed Onboarding Form responses before continuing.

---

## Step 1 — Gather / extract required info

**Roster row fields (always required, ask if missing):**
- Full name (canonical — becomes folder name and CSV key)
- Email
- Rate (£/session)
- Sessions per week (integer, or TBC for irregular/hybrid)
- Segment: `in-person` / `online` / `hybrid`

**Roster row fields (optional, TBC if unknown):**
- Phone
- Start date (first paid session; today if starting now)

**Intake form fields (Full intake mode — extract from pasted responses):**

| Form section | Maps to profile section |
|---|---|
| Personal Details (DoB, weight, height) | Personal Info |
| Training Priorities (multi-select) | Goals + Training Strategy |
| Nutrition Priorities (single-select) | Nutrition Strategy |
| Goal Description + Time Frame | Goals (incl. Time Frames if given) |
| Lifestyle Commitments | Personal Info + away_periods candidate (do not write — flag for Tom) |
| Injuries / Health | Injuries & Health |
| Exercise Preferences (include/avoid) | Training Strategy |
| Session Preferences (preferred times) | Personal Info |
| Nutrition Tracking (Y/N) | Monitoring & Accountability |
| Weekly Accountability Check-in (Y/N) | Monitoring & Accountability |
| Motivation & Accountability (free text) | Monitoring & Accountability |
| Anything Else | Personal Info or relevant section |

**Macro-planner inputs (capture if available — needed for the Nutrition Plan in Step 5):**
- Sex (M / F)
- Age (compute from DoB if given)
- Weight (kg)
- Height (cm)
- Activity level (`sedentary` / `light` / `moderate` / `very` / `extra`) — usually not in the intake form; ask Tom directly if Full intake mode
- Goal target — usually not in the intake form numerically; ask Tom directly (or use `fat loss moderate` as a default if nutrition priority = "Lose Weight/Fat" and Tom confirms)

If any roster row required fields are missing, collect before writing.

---

## Step 2 — Create the folder and profile file

**Path**: `C:\Users\Tom\Documents\Home Vault\2 - Business\Clients\[Full Name]\[Full Name].md`

```markdown
# [Full Name]

**Status**: Client | **Type**: [Personal/Online/Hybrid] | **Cadence**: [Nx/week, preferred times if known] | **Rate**: £[rate]/session
**Email**: [email] | **Phone**: [phone] | **Birthday**: [DoB if given, friendly format e.g. "16 July"] | **Started**: [start date, friendly format]

## Client Profile

### Personal Info
[bullet points — sex/age, occupation, schedule constraints, lifestyle context, preferred session times, anything from Lifestyle Commitments]

### Injuries & Health
[bullet points — injuries, health conditions, physical limitations. Omit section if nothing known.]

### Goals
[bullet points — selected Training Priorities, free-text goal description, target metrics where given]

### Time Frames
[bullet points — only if intake provided a time frame. Otherwise omit.]

### Training Strategy
[bullet points — initial approach, exercise preferences (include/avoid), training priorities. Omit section if nothing known yet.]

### Nutrition Strategy
[bullet points — nutrition priority (lose/gain/maintain/none), tracking preference, initial direction. Omit if "not a priority" with no other detail.]

### Monitoring & Accountability
[bullet points — built from intake responses:
- Nutrition tracking: Yes/No (and how, if specified)
- Weekly accountability check-in: Yes/No
- Preferred motivators (from "What motivates you most")
- Preferred accountability methods (from "How can we best keep you accountable")
- Default cadence if Tom doesn't specify: hands-on technique coaching during sessions, weekly informal check-in via WhatsApp]

## Session Log

<!-- New session entries are inserted directly below this heading -->
```

**Rules for filling sections:**
- Omit any section that has no content. Don't write empty headings or "TBC" placeholders inside sections — the section absence itself is the signal.
- For Personal Info, prefer terse single bullets (e.g. "Female, 42, moderately active.") to long paragraphs.
- For Monitoring & Accountability, if intake says No to both nutrition tracking and weekly check-in, write a single line: "Light touch — coaching during sessions only, no formal tracking or check-ins requested at intake."

---

## Step 3 — Create Programmes.md stub

**Path**: `C:\Users\Tom\Documents\Home Vault\2 - Business\Clients\[Full Name]\Programmes.md`

```markdown
---
title: Programmes — [Full Name]
tags: [clients, programme]
---

# Programmes — [Full Name]

Per-cycle training programmes. Newest at top.

---

## Cycle 1

**Focus:** TBD

*Programme to be written.*
```

---

## Step 4 — Create the Nutrition Plan (real or stub)

**Decision tree:**

- If **all six macro-planner inputs are confirmed** (sex, age, weight, height, activity, goal) → invoke the `macro-planner` skill inline with those inputs. It writes `<YYYY-MM-DD> [Full Name] - Nutrition Plan.md` into the client folder. Use today's date.

- If **nutrition priority = "Not A Priority"** and Tom has not asked for a plan → skip this step. Note in the confirm message that no nutrition plan was created.

- Otherwise → create a **stub** at `C:\Users\Tom\Documents\Home Vault\2 - Business\Clients\[Full Name]\[YYYY-MM-DD] [Full Name] - Nutrition Plan.md`:

```markdown
---
type: nutrition-plan
client: [Full Name]
created: [YYYY-MM-DD]
phase: Intake — pending
tags: [nutrition-plan, client-doc]
status: stub
---

# Nutrition Plan — [Full Name]

*Intake pending. Run `/macro-planner` for [Full Name] once the missing inputs below are gathered.*

## Inputs gathered so far

| Field | Value |
|---|---|
| Sex | [value or **missing**] |
| Age | [value or **missing**] |
| Weight (kg) | [value or **missing**] |
| Height (cm) | [value or **missing**] |
| Activity level | [value or **missing — usually decided by Tom**] |
| Goal | [nutrition priority from intake, e.g. "Lose Weight/Fat — magnitude not yet set"] |

## Next step

Gather the missing fields above, then re-run `/macro-planner` for [Full Name]. This file will be replaced with the full plan when generated.
```

---

## Step 5 — Append to clients.csv

Append one row to `C:\Users\Tom\Documents\Home Vault\2 - Business\Clients\clients.csv`:

```
[Full Name],[email],[phone],[start_date],[end_date],[rate],[sessions_per_week],[status],[segment],[Full Name]/[Full Name].md
```

- `end_date`: leave empty
- `status`: `active`
- `notes_file`: `[Full Name]/[Full Name].md`

Verify the name doesn't already exist in clients.csv before appending.

---

## Step 6 — Add section to tasks.md

Find `C:\Users\Tom\Documents\Home Vault\2 - Business\Operations\tasks.md`. Add a `## [Full Name]` section in alphabetical order among the existing client headings.

Pre-populate the section with onboarding follow-ups based on what's still outstanding. Use Obsidian task syntax with today's date in parentheses. Only add tasks that genuinely apply:

```markdown
## [Full Name]
- [ ] Write Cycle 1 programme. (YYYY-MM-DD)
- [ ] Complete nutrition intake (missing: [list]) and re-run /macro-planner. (YYYY-MM-DD)   ← only if Nutrition Plan was stubbed
- [ ] Add to availability.md if active this week. (YYYY-MM-DD)
- [ ] Book first session via /add-session or Sunday booking. (YYYY-MM-DD)
- [ ] Add upcoming time off to away_periods.csv: [details]. (YYYY-MM-DD)   ← only if intake flagged any
```

If the client is genuinely complete at onboarding (programme already drafted, nutrition plan generated inline, first session already booked), leave the section empty.

---

## Step 7 — Confirm

Reply with:

- **Client name and folder path created**
- **clients.csv row appended** (show the row)
- **Files created** — list of: profile, Programmes.md, Nutrition Plan (real / stub / skipped), tasks.md section
- **Fields left as TBC** that Tom should fill in later
- **Follow-up tasks** added to tasks.md (one-line summary)
- **Reminders**:
  - Add to `availability.md` if active this week (unless already done at intake)
  - Book first session via `/add-session` or Sunday booking workflow
  - If intake flagged upcoming time off, add to `away_periods.csv` manually
