---
description: Step-by-step audit for one active PT client. Phase 1 silently normalises folder mechanics (filenames, CSV pointers, stale banners, Session Log extraction, YAML-format profile migration). Phase 2 walks Tom through content gaps one question at a time (programme currency, nutrition plan or opt-out, check-ins or opt-out, header bar fills, stale sections). Use whenever Tom says "audit [client]", "check [client]'s folder", "is [client] up to date", "review [client]'s setup", or any variant on confirming a single client is fully filled in.
---

# Client Audit

End-to-end audit and walkthrough for a single active PT client. Reads the client's folder against the Andrew Rhodes canonical pattern, normalises mechanical drift in one batch, then walks Tom through content gaps with fix-now / mark-opt-out / skip choices.

## Inputs

Take a client name from Tom's invocation (e.g. `/client-audit Belinda Boakye`). If no name given, read `clients.csv`, list active clients, ask which one.

If the name is ambiguous or doesn't match a CSV row, ask. Don't guess.

## Data paths

```
clients.csv  → C:\Users\Tom\Documents\Home Vault\2 - Business\Clients\clients.csv
clients dir  → C:\Users\Tom\Documents\Home Vault\2 - Business\Clients\
tasks.md     → C:\Users\Tom\Documents\Home Vault\2 - Business\Operations\tasks.md
sessions.csv → C:\Users\Tom\Documents\Home Vault\2 - Business\Operations\sessions.csv
availability → C:\Users\Tom\Documents\Home Vault\2 - Business\Operations\availability.md
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

### Q3 — Programme currency

Read `[Name] - Programmes.md`. Check:
- Latest cycle's date.
- Whether it's marked superseded.
- Whether a current cycle exists.

Cases:
- **Current cycle exists, dated within a sensible window for their phase**: PASS, mention the cycle name briefly.
- **Latest cycle is marked superseded with no replacement**: ask "Write a new cycle now, add a task to tasks.md, or note client is between programmes?"
- **No cycles at all (just the scaffold stub)**: same three choices.

### Q4 — Nutrition Plan

Cases:
- **File exists**: read the `created:` frontmatter or filename date. If within 8 weeks and the goal/weight in the plan matches Profile: PASS. If stale: ask "Re-run /macro-planner now, defer, or confirm still current?"
- **File missing AND no `### Nutrition Plan: opt-out` section in Profile**:
  - Fix now → invoke `/macro-planner` inline.
  - Mark opt-out → prompt for reason, write the opt-out section to Profile with today's date.
  - Skip → record in skip list, take no action.
- **File missing AND opt-out section present**: PASS, mention the recorded reason and date so Tom can confirm still valid.

### Q5 — Check-ins

Same structure as Q4.

Cases:
- **File exists with entries in last 4 weeks**: PASS.
- **File exists but stale**: ask "Add an entry now, defer, or confirm still on track?"
- **File missing AND no `### Check-ins: opt-out` section in Profile**:
  - Fix now → create `[Name] - Check-ins.md` with a starter entry template (date header, blank body, ready for Tom to fill).
  - Mark opt-out → prompt for reason, write opt-out section to Profile.
  - Skip.
- **File missing AND opt-out section present**: PASS, mention the recorded reason.

### Q6 — Session Log recency

Inspect last entry in `[Name] - Session Log.md`.

- **Within 3x cadence interval** (e.g. 1x/wk → 21 days, 2x/wk → 10 days, 3x/wk → 7 days): PASS.
- **Stale**: flag with date of last entry and ask whether client is still active, paused, or sessions happening without being logged.

No action enforced. Information only.

### Q7 — Bookings

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
