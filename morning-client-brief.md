---
description: Generate per-session files in _inbox/ for each of today's (or the week's) scheduled clients, pre-populated with client context, last session pending items, today's programme, and live-notes prompts. Use --week to generate all session files for the current Mon-Sun week in one pass (run Monday morning or via the Sunday booking workflow).
---

# Morning Client Brief

You are generating Tom's morning client brief. Output is one per-session markdown file per booked session, in the inbox folder, pre-populated so Tom can take notes during the session on his phone alongside 1Fit.

## Usage

- `/morning-client-brief` — generate today's session files (manual use during the day)
- `/morning-client-brief --tomorrow` — generate tomorrow's session files (used by the 9pm scheduled run so files are ready in the morning)
- `/morning-client-brief --week` — generate all session files for the current Mon-Sun week in one pass; skips files that already exist so it is safe to re-run mid-week

## Inputs

- **sessions.csv**: `$VAULT_PATH/2 - Business/Operations/Bookings/sessions.csv`
- **tasks.md**: `$VAULT_PATH/2 - Business/Operations/tasks.md`
- **Client folder**: `$VAULT_PATH/2 - Business/Clients/[Client Name]/`
  - `[Client Name] - Profile.md`
  - `[Client Name] - Programmes.md`
  - `[Client Name] - Session Log.md`
- **Output folder**: `$VAULT_PATH/2 - Business/Clients/_inbox/`
- **Weekly file**: `$VAULT_PATH/This Week.md` (overwritten each run)

## Steps

### 1. Determine the target date(s)

- Default: today only
- With `--tomorrow`: tomorrow only
- With `--week`: all days in the current Mon-Sun week (the week containing today)

### 2. Get the bookings for the target date(s)

Read `sessions.csv`.

- **Default / `--tomorrow`**: filter for rows where `date` matches the single target date and `status = scheduled`. If there are no matching rows, print "No sessions scheduled on [date]." and stop (still ensure folder exists per Step 3).
- **`--week`**: filter for rows where `date` falls within the current Mon-Sun week and `status = scheduled`. Sort by date then by time. If there are no matching rows, print "No sessions scheduled this week." and stop (still ensure folder exists per Step 3).

For each matching row, extract: `client_name`, `time`, `week_number`, `regular_flexible`.

### 3. Ensure the inbox folder exists

Path: `$VAULT_PATH/2 - Business/Clients/_inbox/`. Create it if it doesn't exist. Also create `$VAULT_PATH/2 - Business/Clients/_inbox/_processed/` for /process-sessions to use later.

### 4. For each booked session, generate a per-session file

**Filename**: `_inbox/YYYY-MM-DD HHMM Client Name.md` (24-hour clock, no colon — e.g. `2026-05-21 0800 Nick Thompson.md`)

**Idempotency**: if the file already exists, skip it and report `skipped (exists)`. Do not overwrite — Tom may already have edited it.

**Section order in every generated file:**
1. Header
2. Watch strip (if any flags exist)
3. Today's Plan
4. Immediate Tasks (if any open tasks exist)
5. Live Notes
6. `---`
7. From Last Session
8. Client Context
9. Voice Notes

The file is designed for a single readable glance at the top (Watch + programme), then live editing (Live Notes), then reference detail below the fold.

**Build the file from these sources:**

#### Header block

```
# [Client Name] — [Day DD MMM], HH:MM
[cycle line]
```

For the cycle line:
- If `week_number` is populated in sessions.csv: `Week N of cycle`
- Else if the most recent Session Log entry contains a clear week marker: use that
- Else: omit the line entirely

#### Watch strip

Immediately after the header, output a compact blockquote with the flags Tom needs before coaching starts. Pull from:
- Injury / health flags and technique watchpoints in `[Client Name] - Profile.md`
- `flagged_body_parts` + `recurring_themes` from the most recent Session Log entry

Format as a single blockquote, semicolon-separated, max 3 items. Keep it to one line where possible:

```
> **Watch:** [flag 1]; [flag 2]; [flag 3 if needed]
```

If nothing is flagged from either source, omit the Watch strip entirely.

#### Today's Plan

Open `[Client Name] - Programmes.md`. Pull the topmost (active) cycle.

**Workout selector for multi-workout cycles**:

Clients work through their workouts in order (A, B, C, ...) within the week. Today's workout is determined by how many sessions the client has this week up to and including today.

1. Read sessions.csv, filter rows where `client_name` matches AND date is in the same Mon–Sun week as the target date AND date <= target date AND status is `scheduled` or `complete`. Count these rows; call it `N` (the client's Nth session of the week, with today being the Nth).
2. Get sub-headings under the active cycle in document order (e.g. "Workout A — ...", "Workout B — ...", or "Tuesday: Anterior", "Friday: Posterior").
3. Filter out solo/elective workouts: skip any sub-heading whose heading contains "Solo" or "Elective", or whose Focus line begins with "Elective".
4. Today's workout = filtered_sub_headings[N - 1] (1-indexed: N=1 → first, N=2 → second, etc).
5. If `N` exceeds the number of filtered sub-headings, use the last one and add a `_(warning: session count exceeds workout count, showing last in rotation)_` note.

For **single-workout cycles** (no sub-headings — just exercises directly under the cycle heading), skip the selector and show the whole cycle.

**Format for a single-workout cycle:**

```
## Today's Plan
**Cycle:** [cycle heading]
**Focus:** [focus line, or "(not set)"]

1. [Exercise] — SxR @ WEIGHT *(note if present)*
2. ...
```

**Format for a multi-workout cycle:**

```
## Today's Plan
**Cycle:** [cycle heading]
**Today's workout:** [chosen sub-heading text] (session N of week)
**Focus:** [per-workout Focus line, or cycle-level Focus, or "(not set)"]

1. [Exercise] — SxR @ WEIGHT *(note if present)*
2. ...
```

Only render today's specific workout. Do NOT include the other workouts — Tom can tap into Programmes.md if he needs them.

If Programmes.md is missing, empty, or has no active cycle: `**No programme on file.**`

#### Immediate Tasks

Open `tasks.md` and collect all `- [ ]` lines under `## [Client Name]` (open tasks only). Strip trailing metadata: drop `#task`, `#person/...` tags, and `(raised: ...)` notes, keeping just the task text (and a `📅 date` if present).

If any open tasks exist, output:

```
## Immediate Tasks
- [ ] [task 1]
- [ ] [task 2]
```

Omit the section entirely if there are no open tasks.

#### Live Notes section (static prompts)

```
## Live Notes
**Changes made:** 
**Form notes:** 
**Tasks / follow-ups:** 
**For next session:** 
**Khaela report:** 
```

#### Separator

Output a horizontal rule to mark the end of the at-a-glance section and the start of reference detail:

```
---
```

#### From Last Session

Open `[Client Name] - Session Log.md`. Walk the `### ` entries under `## Session Log` from newest down. Pick the **most recent completed session** — an entry with an `exercises:` field present (skip cancellations, no-shows, and pre-session notes entries that lack that field). Extract:
- The date from the entry heading
- `program_changes` field (verbatim if present)
- `flagged_body_parts` + `recurring_themes` (combined as "Watch:")
- Any bullet line mentioning "next time", "next session", or things to watch for

Format:

```
## From Last Session
**Date:** [last session date]
**Pending changes:** [program_changes, or "None"]
**Watch:** [flagged + themes, or "Nothing flagged"]
**Notes for today:** [next-time notes from bullets, omit line if none]
```

If no Session Log heading exists or it's empty: `**No prior session data.**`

#### Client Context

Open `[Client Name] - Profile.md`. Build a 3-4 line glance strip. Pull:
- Primary goal (from Goals section, one line)
- Current training strategy or focus (one line)
- Any injury / health flag (one line, only if present)
- Technique watchpoints (one line, only if present)

Format as bullets under `## Client Context`. Keep this terse — if the profile has lots of detail, summarise. Tom can tap into the full profile if needed.

If profile is empty or missing: `**No client profile on file.**`

#### Voice Notes section (static placeholder)

```
## Voice Notes
<!-- Paste or dictate voice notes here. /process-sessions reads this section alongside Live Notes. -->
```

### 5. Refresh This Week.md

Regenerate `$VAULT_PATH/This Week.md` from scratch (overwrite previous contents). This is Tom's mobile-bookmark target: the file he taps from to navigate into each session.

**Determine the target week:**

The week containing the target date, Monday through Sunday. e.g. if target date is 2026-05-22 (Friday), the week is Mon 2026-05-18 through Sun 2026-05-24.

**Read sessions.csv:** filter for rows where `date` is in the target week (regardless of status). Group by date, sort by time within each day.

**File format:**

```markdown
# This Week — w/c [Day DD Month YYYY]

## [DayName DD Month]
- HH:MM  [[YYYY-MM-DD HHMM Client Name|Client Name]]
- HH:MM  [[YYYY-MM-DD HHMM Client Name|Client Name]]  *(annotation if non-scheduled)*

## [DayName DD Month]  ← today
- HH:MM  [[...]]

## [DayName DD Month]
(no sessions)
```

**Status rendering rules:**

| sessions.csv status | Render as |
|---|---|
| `scheduled` | Plain wiki link, no annotation |
| `complete` | Wiki link + ` *(complete)*` |
| `cancelled-no-fee` | Strikethrough text (no link) + ` *(cancelled, no fee)*` |
| `cancelled-late-fee` | Strikethrough text (no link) + ` *(cancelled, late fee)*` |
| `no-show` | Strikethrough text (no link) + ` *(no-show)*` |
| `coach-missed` | Strikethrough text (no link) + ` *(coach missed)*` |
| `extra` | Wiki link + ` *(extra)*` |
| anything else | Wiki link + ` *(<status>)*` |

If `notes` column has content for a row, append it to the annotation: `*(<status>, <notes>)*` (e.g. `*(makeup, coach missed 15 May)*`).

**Today marker:** the day-heading for the target date gets ` ← today` appended (two spaces before the arrow).

**Empty days:** include the heading with `(no sessions)` underneath so the week structure is always 7 days.

**Filename to link to:** matches the per-session file convention: `YYYY-MM-DD HHMM Client Name` (no `.md` in the wiki link). Use the canonical client name from sessions.csv.

If a session file doesn't exist (e.g. backfilled past sessions before this system existed), Obsidian shows the link as unresolved. That's expected behaviour, not an error.

### 6. Report

Print a tight summary:

Single-day mode:
```
Morning client brief — [target date]
Created: N session files
  - HH:MM  Client Name
  - HH:MM  Client Name
Skipped (existing): M
This Week.md refreshed.
Issues: [missing profile / empty programme / etc., if any]
```

Week mode:
```
Morning client brief — week of [Mon DD MMM YYYY]
Created: N session files
  - YYYY-MM-DD HH:MM  Client Name
  - YYYY-MM-DD HH:MM  Client Name
Skipped (existing): M
This Week.md refreshed.
Issues: [missing profile / empty programme / etc., if any]
```

Keep the report under 10 lines unless there are issues to flag.

## Edge cases

- **Booking but no client folder**: still create the file with `**No client profile on file.**` and `**No prior session data.**`. The Live Notes container is useful regardless.
- **Programme file missing or empty**: `**No programme on file.**` in Today's Plan.
- **Multiple sessions same client same day**: each gets its own file, time in filename keeps them distinct.
- **File already exists**: skip, don't overwrite. Report as `skipped (exists)`.
- **Cancelled/rescheduled bookings**: skip (filter is `status = scheduled` only).
