---
description: Step-by-step audit for one active PT client against the 121 service standard. Phase 1 silently normalises folder mechanics (filenames, CSV pointers, stale banners, Session Log extraction, YAML-format profile migration). Phase 2 walks Tom through content gaps one question at a time, enforcing "current to standard" not just "file exists": programme currency + 6-week backstop + homework/rationale, nutrition plan-around-the-number + behavioural anchor, the behaviour-change engine chain (check-ins read-back + habits + monitoring dashboard), the onboarding gate, and the comms proxy. Use whenever Tom says "audit [client]", "check [client]'s folder", "is [client] up to date", "review [client]'s setup", or any variant on confirming a single client is fully filled in and delivered to standard.
---

# Client Audit

End-to-end audit and walkthrough for a single active PT client. Reads the client's folder against the Andrew Rhodes canonical pattern AND the 121 service standard, normalises mechanical drift in one batch, then walks Tom through content gaps with fix-now / mark-opt-out / skip choices.

This audit enforces two layers. The **documentation standard** (which files exist, canonical shape) is Phase 1 plus the header/section checks. The **service standard** (is the client actually delivered to the locked 121 scope) is the sharpened Phase 2: the 6-week programme backstop, nutrition as a plan-around-the-number with a behavioural anchor, the linked behaviour-change engine, the onboarding gate, and the comms rhythm. The standard is defined in `2 - Business/Operations/121 Delivery/121 Personal - Delivery Scope.md` and its four cluster deliverable docs in the same folder (moved from 1 - Projects on 2026-06-10 when the 121 standard went operational; the operating runbook is `121 Delivery - Operating Rhythm.md` alongside them). The audit moves a check from "the file exists" to "the file is current to standard".

## Inputs

Take a client name from Tom's invocation (e.g. `/client-audit Belinda Boakye`). If no name given, read `clients.csv`, list active clients, ask which one.

If the name is ambiguous or doesn't match a CSV row, ask. Don't guess.

## Data paths

```
clients.csv  → C:\Users\Tom\Documents\Home Vault\2 - Business\Clients\clients.csv
clients dir  → C:\Users\Tom\Documents\Home Vault\2 - Business\Clients\
tasks.md     → C:\Users\Tom\Documents\Home Vault\2 - Business\Operations\tasks.md
sessions.csv → C:\Users\Tom\Documents\Home Vault\2 - Business\Operations\Bookings\sessions.csv
availability → C:\Users\Tom\Documents\Home Vault\2 - Business\Operations\Bookings\availability.md
```

## Canonical folder structure (Andrew Rhodes pattern)

```
Clients/[Full Name]/
├── [Full Name] - Profile.md         ← header bar + Client Profile sections
├── [Full Name] - Programmes.md      ← per-cycle programmes, newest at top
├── [Full Name] - Session Log.md     ← separate file, newest entries on top
├── [Full Name] - Bookings.md        ← Upcoming + History tables
├── [Full Name] - Nutrition Plan.md  ← OR opt-out section in Profile
└── [Full Name] - Check-ins.md       ← OR opt-out section in Profile
```

## Canonical Profile.md shape

**Header bar (two lines, all fields shown even when TBC):**

```
**Status**: Client | **Type**: [Personal/Online/Hybrid] | **Cadence**: [Nx/week, preferred times] | **Rate**: £[rate]/session
**Email**: [...] | **Phone**: [...] | **Location**: [...] | **Birthday**: [...] | **Started**: [...]
```

Optional third line for an active banner (only when meaningful):
```
⚠️ **[Short status note, e.g. "Relocating to US May 2026" or "On reduced cadence through April."]**
```

**Required Client Profile sections (all five must be present and non-empty):**
- `### Personal Info`
- `### Goals`
- `### Training Strategy`
- `### Nutrition Strategy`
- `### Monitoring & Accountability`

**The Monitoring & Accountability section is the engine dashboard.** Under the service standard it is no longer a free-text note, it must carry four populated fields plus a review date, no blanks:

```markdown
### Monitoring & Accountability
- Metrics tracked: [weight cadence, performance, habits; photos only if the client opted in]
- Named failure point: [the one from the Nutrition Plan, e.g. late-night snacking]
- Current habit(s): [1-2 max, the one(s) addressing the failure point]
- Accountability mechanism: [how Tom holds them to it]
- Next progress review: [YYYY-MM-DD, within the future 6-week window]
```

This is checked as a linked chain in Q5, not as five independent fields.

**Optional sections preserved as-is (do not delete if present):**
- `### Injuries & Health`
- `### Time Frames`
- Any client-specific non-canonical sections (e.g. Mo's `### Weight & GLP-1 History`, Jonathan's `### Plan Overview`, Mo's `### Assessment Results`). These hold real info, leave them.

**Opt-out markers (added to Profile only when an artefact is intentionally absent):**

```markdown
### Nutrition Plan: opt-out
- Reason: [reason Tom gave]
- Recorded: [YYYY-MM-DD]
```

```markdown
### Check-ins: opt-out
- Reason: [reason Tom gave]
- Recorded: [YYYY-MM-DD]
```

---

## Step 0 — Load context

1. Read the CSV row. If missing or `status != active`, abort with a one-line explanation.
2. List the client's folder. Capture: which canonical files exist, which legacy files exist, any extras (one-off PDFs, dated handouts, etc).
3. Read the Profile file in full.
4. Read the Programmes file (just the first cycle or two).
5. Read the most recent 3 entries of the Session Log (whether separate file or embedded section).
6. Read the Nutrition Plan and Check-ins files if present.

Build an internal audit map of drifts and gaps before saying anything to Tom.

---

## Phase 1 — Mechanical normalisation (one batched confirmation)

Detect every mechanical drift up front. Present as a numbered diff. Wait for a single "apply all / apply selected / skip" choice. Do not bug Tom per-item.

**Mechanical drift types:**

| Drift | Fix |
|---|---|
| `[Name].md` exists instead of `[Name] - Profile.md` | Rename |
| `Programmes.md` (bare) exists instead of `[Name] - Programmes.md` | Rename |
| Embedded `## Session Log` section inside Profile | Extract everything from that heading to end-of-file into a new `[Name] - Session Log.md`. Remove the section from Profile. |
| YAML frontmatter + `## Snapshot / ## Background / ## Goals / ## Health` profile format (Taylor and Tulha at time of writing) | Propose migration to canonical field-bar + Client Profile format. Show the mapping (Snapshot → Personal Info, Background → Personal Info or Training Strategy, Goals → Goals, Health → Injuries & Health). Preserve all YAML metadata in a kept frontmatter block. Confirm before applying. |
| CSV `notes_file` pointer wrong | Update to `[Name]/[Name] - Profile.md` |
| Status banner mentions a past date and CSV status is active (e.g. "PAUSED, expected back week of 20 Apr" when today is past that and CSV is active) | Remove the banner. If Tom wants a fresh banner he'll add in Phase 2. |
| No `## [Full Name]` heading in `Operations/tasks.md` | Insert in alphabetical order with an empty body |
| Profile has any duplicate heading or malformed section ordering | Fix |
| `[Name] - Bookings.md` Upcoming table holds a row whose date is in the past AND that date already has a Session Log entry (the session happened) | Move it from Upcoming to the top of the History table (carry any note across). Leaves Upcoming reflecting only genuinely-future sessions, so Q9 reads true |

**Output format:**

```
Phase 1 — mechanical fixes proposed for [Full Name]:

1. Rename Belinda Boakye.md → Belinda Boakye - Profile.md
2. Extract Session Log section (12 entries) → Belinda Boakye - Session Log.md
3. Clear stale status banner: "⚠️ Switched to 1x/wk March 2026" (date passed, banner no longer load-bearing)
4. CSV pointer: Belinda Boakye/Belinda Boakye.md → Belinda Boakye/Belinda Boakye - Profile.md

Apply all / select / skip Phase 1?
```

If the client is fully canonical at Phase 1 (Andrew Rhodes is the only one starting in that state), say "Phase 1: no mechanical drift detected" and move on.

---

## Phase 2 — Content walkthrough (one question at a time)

Walk through gaps in this order. For each gap, present the fix-now / mark-opt-out / skip choices clearly. Don't combine questions. Wait for Tom's answer before moving on.

### Q1 — Header bar fills

Inspect the header bar. For each missing or TBC field (Email, Phone, Location, Birthday, Started, Rate, Cadence, Type):
- Show what's there now.
- Ask Tom to fill or confirm leave as TBC.
- Update header bar in Profile when answered.

Group all missing fields into a single question batch (don't ask one field at a time).

### Q2 — Canonical sections content

For each of the five required Client Profile sections, in order:
- **Personal Info**: present? Has actual content beyond placeholder? If empty or placeholder-only, ask Tom to dictate content.
- **Goals**: same check.
- **Training Strategy**: same.
- **Nutrition Strategy**: same.
- **Monitoring & Accountability**: same.

If a section is filled but its content references a stale goal or phase that contradicts the current programme or nutrition plan, flag it: "Nutrition Strategy mentions 'aiming for 65kg by Easter' but current Nutrition Plan target is 63kg by July. Update?"

Don't rewrite sections wholesale, ask Tom for the new content (free text or bullet dictation), then write.

### Q3 — Programme currency and standard

Read `[Name] - Programmes.md`. The standard is now testable, not "a sensible window". Inspect the active (top, non-superseded) cycle for three things:

1. **Currency** — within the **6-week backstop**. Any cycle is owed a review by 6 weeks even if progressing, so nothing goes stale silently. Past 6 weeks from the cycle's start date = stale.
2. **`**For you:**` line** — the one-line client-facing rationale for the cycle is present.
3. **`### Homework / Mobility` block** — present in the active cycle. Homework is standard for every client, with a floor of mobility/stretching.

Cases:
- **Current cycle, within 6 weeks, both elements present**: PASS, name the cycle.
- **Current cycle but past the 6-week backstop**: ask "Write a new cycle now (/write-programme), add a task to tasks.md, or note client is between programmes?"
- **Cycle present but missing the `**For you:**` line and/or the `### Homework / Mobility` block**: flag the specific missing element. Offer to add it now (Tom dictates the rationale / homework) or defer as a task. Legacy cycles predate these, so expect to backfill.
- **Latest cycle superseded with no replacement, or no cycles at all (scaffold stub)**: ask "Write a new cycle now, add a task, or note between programmes?"

> [!note] Producing-skill dependency
> The `**For you:**` line and `### Homework / Mobility` block are emitted going forward by an updated `/write-programme` (build step 4). Until that lands, the audit flags their absence as a backfill gap, not a fault.

### Q4 — Nutrition plan and standard

The standard moved from "file exists" to "a plan around the number, with a named behavioural anchor". A bare macro target no longer passes (it's the exact thing that already failed these clients).

Cases:
- **Plan file exists**: check three things.
  1. **Built around the number** — more than macro targets alone: a structured approach, either a bespoke meal plan OR a deliberately-chosen flexible-tracking framework agreed with the client. Targets-only does NOT meet standard, flag it.
  2. **Named behavioural anchor** — one named failure point (late-night snacking, weekend drinking, etc.) plus one concrete strategy for it. This is the origin of the behaviour-change engine, re-checked in Q5. Missing = flag.
  3. **Currency** — within the **8-week backstop**, with the plan's goal/weight matching Profile. Stale = ask "Re-run /macro-planner now, defer, or confirm still current?"
- **File missing AND `### Nutrition Plan: opt-out` section present**: PASS. The opt-out is a positive recorded marker, not a gap. Mention the reason and date so Tom can confirm still valid.
- **File missing AND no opt-out section**:
  - Fix now → invoke `/macro-planner` inline.
  - Mark opt-out → prompt for reason, write the opt-out section to Profile with today's date.
  - Skip → record in skip list, take no action.

### Q5 — Behaviour-change engine (check-ins + habits + monitoring)

The heart of the new standard. Check-ins, habits and Monitoring are **one linked engine, not three independent ticks**. Verify the **chain** and flag the specific broken link, don't tick the boxes separately.

The chain: **named failure point (from the Q4 nutrition plan) → an assigned habit addressing it → the check-in loop reviewing it weekly with a read-back → the Monitoring dashboard recording the whole state.**

Check, in order:
1. **Failure point** — the named failure point from the Nutrition Plan (Q4) is mirrored in the Profile Monitoring & Accountability section.
2. **Habit** — at least one active habit (assigned via `/habit-sync`, lives in 1Fit) addresses that failure point, recorded in M&A. Hard cap 1-2 habits, never a checklist.
3. **Check-in loop** — `[Name] - Check-ins.md` most recent entry is within the last **7 days** AND carries a `Read-back sent` marker. Tom's response is the active ingredient; a logged weight with no read-back is the exact version the evidence finds useless. Or a recorded `### Check-ins: opt-out` exists (then this link is a PASS).
4. **Monitoring dashboard** — the M&A section has all four fields populated with no blanks (metrics tracked, current habit(s), named failure point, accountability mechanism), plus a **next progress review date**.
5. **Progress review currency** — the next progress review date is within the future 6-week window, or past and due (flag as due).
6. **WIA consistency** — if the metrics field prescribes high-frequency weighing (daily, or near-daily) but the WIA screen reads `Not yet screened`, flag it. Frequency must be set *after* the screen, not before. Offer to run the one-question screen now (Domain 6 of the Onboarding Intake SOP) or drop the frequency to a safe default until screened.

Cases:
- **Whole chain intact**: PASS, state plainly that the engine is running.
- **Any link broken**: flag the **specific** link, e.g. "habit assigned but no read-back on the check-in in 12 days" or "M&A failure point blank while the nutrition plan names weekend drinking". Offer to fix that link now, defer it as a task, or (for the check-in link only) mark opt-out.
- **Check-ins file missing AND no opt-out**: fix now → create `[Name] - Check-ins.md` from `Clients/_Templates/Check-ins Template.md` (replace `{{Full Name}}`) / mark opt-out → prompt reason, write to Profile / skip.
- **Check-ins file exists in a pre-standard format** (e.g. a bare weight table, or entries with no `Read-back sent` field — most legacy clients): offer to **migrate it to the new template**. Preserve every existing entry (carry weight and any notes across), reformat to the standard fields (Weight / Adherence / Struggle / Flag / Read-back sent / Notes), add the prompt + read-back-shape header block from the template, and set `Read-back sent:` on historical entries to `unknown (pre-standard)` rather than back-dating a claim. Newest stays on top.

> [!note] Producing-skill dependency
> `read-back sent` markers come from the updated check-in workflow, the M&A dashboard fields from the new Profile template (build steps 2 and 5-7). Legacy clients will show most of this chain empty. That is the gap the roster run closes, present it as backfill, not failure.

### Q6 — Onboarding gate

Only fully meaningful for clients within or just past the onboarding window. Determine the window from `Started` (header bar) and session count: **3 sessions or 2 weeks from start, whichever comes first.**

- **Client well past the window** (established): treat as a catch-up check. Verify the five conditions and surface any specific gaps as a task. Don't re-run onboarding.
- **Client inside the window**: verify the five conditions, flag what's still open.

The five completion conditions:
1. All five Profile sections filled (real content, not placeholder).
2. Nutrition intake done, no "pending".
3. Baseline metrics captured (weight, key measurements). Progress photos are opt-in only and not part of this baseline, never flag their absence.
4. First habit assigned.
5. WIA screen recorded (weight-related information avoidance, screened before any monitoring frequency is prescribed).

Surface **specific** missing fields, never a bare "onboarding incomplete".

### Q7 — Comms proxy

Light, mostly informational. The comms standard is a proactive rhythm (session recap + check-in read-back), so the auditable proxy is whether those two touchpoints are firing.

Check:
- The most recent Session Log entry carries a `recap_sent` marker.
- The most recent Check-ins entry carries a `read-back sent` marker (also surfaced in Q5).

- **Both present**: PASS, proactive rhythm running.
- **Missing**: flag as a gap. These markers are emitted by updated `/process-sessions` (recap) and the check-in loop (read-back), build steps 4-5. Legacy entries predate them, so this is backfill.

### Q8 — Session Log recency

Inspect last entry in `[Name] - Session Log.md`.

- **Within 3x cadence interval** (e.g. 1x/wk → 21 days, 2x/wk → 10 days, 3x/wk → 7 days): PASS.
- **Stale**: flag with date of last entry and ask whether client is still active, paused, or sessions happening without being logged.

No action enforced. Information only.

### Q9 — Bookings

Inspect `[Name] - Bookings.md` Upcoming table.

- **At least one upcoming session within next two weeks**: PASS.
- **Empty Upcoming**: ask "Run /add-session, defer to Sunday booking workflow, or mark client as paused this week?"

---

## Step 3 — Summary

Print a summary block at the end:

```
Audit complete: [Full Name]

Phase 1 (mechanical):
- [bullet list of fixes applied, or "no drift detected"]

Phase 2 (content):

Service standard:
- Programme: [pass / past 6-week backstop / missing For-you line / missing homework block]
- Nutrition: [pass / opt-out / targets-only no plan / no behavioural anchor / stale]
- Behaviour-change engine: [intact / broken link: which one]
- Onboarding gate: [complete / specific gaps]
- Comms rhythm: [running / recap or read-back markers missing]

Filled now:
- [list]

Marked opt-out:
- [list]

Deferred (task added to tasks.md):
- [list]

Skipped this run:
- [list]

Open items:
- [anything unresolved or worth re-running later]
```

End by reminding Tom of any genuinely-open items he should circle back on (e.g. "Still no current cycle in Programmes.md — task added for this week.").

---

## Conventions

- **British spelling** throughout any content Claude writes into client files.
- **No em dashes** in any prose Claude generates. Use a comma or full stop.
- **Contractions always** ("don't", "we'll", "you're"), never the long form, in any text written for Tom or his clients.
- **Today's date** for any opt-out marker, task entry, or "Recorded:" field.
- **Never block on TBC fields** (phone, birthday, location). Flag them in Q1 and move on if Tom can't fill them.
- **Preserve non-canonical Client Profile sections**. They hold real client-specific information; don't flatten them to canon.
- **One question at a time in Phase 2**. Don't combine Q3 and Q4 into a single ask. Wait for Tom's answer before moving on.
- **Don't rewrite the Profile from scratch** when filling a section. Use Edit to insert or replace only the affected section, preserve everything else.
- **Treat the behaviour-change engine as one linked chain** (Q5), not four independent ticks. Flag the specific broken link, not a generic "monitoring incomplete".
- **Absent service-standard markers on legacy clients are backfill gaps, not failures.** `recap_sent`, `read-back sent`, the `**For you:**` line, the `### Homework / Mobility` block and the M&A dashboard fields are emitted by producing skills updated in later build steps. Present their absence as "to backfill", framed the same as any fix-now / defer / opt-out gap, never as the client failing.
