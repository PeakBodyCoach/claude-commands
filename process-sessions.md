---
description: Process today's session voice notes from the inbox, route to client files, extract structured data, append rows to sessions.csv and client Bookings.md, write Khaela's report to vault, append tasks to tasks.md, clear the inbox
---

# Process Sessions

You are processing today's session voice notes from the inbox into the vault. Tasks land in tasks.md; Khaela's report writes to a vault markdown file.

## Inputs

- **Inbox file**: `$VAULT_PATH/2 - Business/Clients/_inbox.md`
- **Client files directory**: `$VAULT_PATH/2 - Business/Clients/` (each client has a subfolder; main file is `[Client Name]/[Client Name].md`)
- **tasks.md**: `$VAULT_PATH/2 - Business/Operations/tasks.md`
- **Khaela reports dir**: `$VAULT_PATH/2 - Business/Operations/Khaela/_session-reports/`

## Client roster

Match dictated names against this roster. Use fuzzy matching but never guess. If you can't confidently match, flag the block as UNMATCHED and leave it in the inbox.

- Andrew Rhodes
- Belinda Boakye
- Decio Melim
- Fergus Redsell
- Fraser Bernstein
- Jack Price
- James Keen
- Jonathan Boseley (alias: JB)
- Laura Easton Harris
- Mo Hussein
- Nick Thompson
- Oscar Douglas
- Rich Radley
- Sarvesh Ramachandran
- Simon Roache
- Taylor Reikofski
- Tulha Patel


## Steps

### 1. Read the inbox

Read `_inbox.md`. If it's empty (or only contains the comment line), report "Nothing to process" and stop.

### 2. Parse session blocks

Each level-1 heading (`# `) marks a new session. Everything between two headings belongs to the client named in the first heading.

Header format is loose because it's a Whisper transcript. Expect variations like:
- `# Rich Radley, Workout B, April 27`
- `# Rich Radley workout be april 27th`
- `# Rich, Workout 2`
- `# JB session today`

Normalise each header:
- Strip punctuation
- Fuzzy-match the name against the roster (handle aliases, e.g. "JB" → Jonathan Boseley)
- Parse workout type: A/B/C/D, "1/2/3/4" → A/B/C/D, "be"/"bee" → B, "see" → C, "dee" → D. Default to "Session" if unclear. Use "Check-in" if no exercises are present.
- Date defaults to today if not specified or unparseable

### 3. For each parsed block: read history

Open the matched client's file (`$VAULT_PATH/2 - Business/Clients/[Client Name]/[Client Name].md`). Find the `## Session Log` heading. Read the 3 most recent `### ` entries below it. Use these to detect recurring themes.

If the file has no `## Session Log` heading yet (e.g. fresh client), proceed with no history context.

### 4. Extract structured fields

From each block's bullet content, extract:

- **exercises**: list of exercises mentioned by name
- **flagged_body_parts**: any body parts mentioned with issues, pain, tightness, or restriction
- **rpe_notes**: RPE/RIR values mentioned, mapped per exercise where possible (e.g. `{squat: 8, bench: 7}`)
- **mood**: client's stated mood, energy, or general state if mentioned (single word or short phrase, omit if not stated)
- **life_events**: external life things — travel, illness, work stress, sport, sleep, family
- **program_changes**: explicit programming changes for the next session (e.g. "going to 82.5 next time")
- **tasks**: actionable follow-ups Tom needs to do (book, send, remind, follow up, check)
- **recurring_themes**: anything appearing in this session AND in 2+ of the previous 3 sessions you read in step 3. Format as `[theme] — [count]th mention this period`.

Omit any field that has no content. Don't fabricate. If a field genuinely has nothing, drop the line.

### 5. Insert into client file

Find the `## Session Log` heading in the client file (`$VAULT_PATH/2 - Business/Clients/[Client Name]/[Client Name].md`). Insert the new entry directly below it (so it becomes the most-recent entry — sessions are reverse chronological).

If the file has no `## Session Log` heading, append one and place the entry beneath it.

Format:

```markdown
### YYYY-MM-DD — [Workout Type]
exercises: [squat, bench, pendlay row]
flagged_body_parts: [shoulder]
rpe_notes: {squat: 8}
mood: tired
life_events: [racquetball injury Friday]
program_changes: [bench → 82.5kg next session]
recurring_themes: [shoulder twinge — 2nd mention this month]

- Squat: lockout sticky on rep 6, told him to brace harder, RPE 8 last set
- Bench: felt easier than last week, going to 82.5 next time
- Mentioned shoulder twinge from racquetball Friday
```

The bullets below the structured block are the original voice note content, lightly cleaned (sentence case, punctuation, but not reworded).

### 6. Update sessions.csv and client bookings file

**sessions.csv** (`$VAULT_PATH/2 - Business/Operations/Bookings/sessions.csv`):

Append one row per processed session. Column order: `date,time,client_name,status,regular_flexible,location,week_number,rate_at_time,credit_burn,notes`

- `date`: YYYY-MM-DD from the parsed header
- `time`: use if present in header or transcript; leave blank if not stated
- `client_name`: matched client name (from roster, canonical form)
- `status`: `complete` for normal sessions; `cancelled-no-fee` or `coach-missed` where applicable (infer from transcript)
- `regular_flexible`: `regular` if this is a standing slot, `flexible` if ad-hoc — default `regular` if unclear
- `location`: `Commando Temple` unless stated otherwise
- `week_number`, `rate_at_time`: leave blank
- `credit_burn`: `FALSE` by default; `TRUE` only if the transcript explicitly indicates a credit was used
- `notes`: brief note for anything unusual; empty for clean sessions

**Client Bookings.md** (`$VAULT_PATH/2 - Business/Clients/[Client Name]/[Client Name] - Bookings.md`):

If this file doesn't exist for a client, skip silently — do not create it.

1. If a row matching the **session's date** exists in the Upcoming table, remove it from Upcoming.
2. Prepend a new row to the top of the History table:

   | Date | Time | Type | Notes |
   | YYYY-MM-DD | HH:MM or blank | regular/flexible | Cancellation note or blank |

3. For cancellations or coach-missed, add a brief note matching the sessions.csv note.
4. Check that the row isn't already present in History before inserting (avoid duplicates on re-runs).

### 7. Append tasks to tasks.md

**File**: `$VAULT_PATH/2 - Business/Operations/tasks.md`

For each item in `tasks`, append a line under the client's `## [Client Name]` heading:

```
- [ ] [task description] ([today's date])
```

If the `## [Client Name]` section already exists, insert the new tasks directly below the heading (before existing tasks — most recent first). If the section doesn't exist, create it at the bottom of the file before the closing content.

Do not duplicate a task that already appears word-for-word in the section.

### 8. Generate Khaela's daily report

Write a markdown file to:
`$VAULT_PATH/2 - Business/Operations/Khaela/_session-reports/[YYYY-MM-DD].md`

Create the `_session-reports/` folder if it doesn't exist.

> **Note**: delivery method to be confirmed with Khaela. For now this lands as a vault file.

Content:

```markdown
# Session Reports — [Today's Date, friendly format]

@Khaela — session notes below. Transcripts are at the bottom.

---

## [Client Name]
**[YYYY-MM-DD] — [Workout Type]**

[2–4 bullet points covering the key things that happened — what moved well, what was flagged, any notable coaching points. Plain prose, no square brackets.]

**Programme changes:**
- [Specific change to make in OneFit or the written programme]

**To do:**
- [Actionable task for Khaela]

---

## Transcripts

### [Client Name] — [YYYY-MM-DD]
[Original raw transcript from inbox]
```

Rules for the summary section:
- Write in plain sentences or short bullets — no `exercises: [...]` or `program_changes: [...]` field syntax
- Only include programme changes and tasks that are actually present; omit those headings if there's nothing to action
- For cancellations with no session content, one sentence is enough — state what happened and any credit/task
- Keep each client block short enough to scan in 10 seconds

One `## [Client Name]` summary section per client processed, in inbox order. All raw transcripts collected into a single `## Transcripts` section at the end, in the same order.

### 9. Handle unmatched blocks

If a client name in a header can't be confidently matched against the roster:
- Don't process the block
- Don't include it in Khaela's report or task creation
- Leave it in the inbox with `# UNMATCHED:` prefixed to the original heading
- Report it in the final summary

### 10. Clear the inbox

After all matched blocks have been successfully processed:
- Reset `_inbox.md` to its template state (heading + drop line)
- Preserve any UNMATCHED blocks at the bottom of the file

Template content:

```markdown
# Today's session notes

Paste voice notes below. First dictation of each session is the header (e.g. "Rich Radley, Workout B, April 27").

```

### 11. Report

Reply with a tight summary:
- Clients processed (with workout type)
- Tasks appended to tasks.md (count)
- Unmatched blocks (if any) — name them so Tom can fix
- Path to Khaela's vault report file

Keep the report under 10 lines unless there are issues to flag.

## Edge cases

- **Empty inbox**: Report "Nothing to process" and stop
- **No exercises in a block**: Process as Check-in, structured fields can be sparse, that's fine
- **Multiple sessions for one client in one day**: Insert each as a separate dated entry, both at top of session log
- **Client name unmatched**: Flag as UNMATCHED, don't guess
- **Whisper artifacts** (filler words, repetitions, "um" "uh"): Strip silently during cleanup
- **Known mistranscription:** "kill" → "curl" (Whisper consistently mishears the exercise name "curl" as "kill" — always substitute silently)
- **Client file has no Session Log heading**: Append the heading and insert beneath
