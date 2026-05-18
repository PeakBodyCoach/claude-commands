---
description: Generate the morning brief — today's clients with last session's pending changes and flagged items. Use --tomorrow to look ahead a day (used by the evening scheduled run).
---

# Morning Brief

You are generating Tom's morning brief. The goal is to pre-load him on his clients before he walks into the gym.

## Usage

- `/morning-brief` — generate today's brief (manual use during the day)
- `/morning-brief --tomorrow` — generate tomorrow's brief (used by the 9pm scheduled run so the file is ready in the morning)

## Inputs

- **sessions.csv**: `$VAULT_PATH/2 - Business/Operations/Bookings/sessions.csv`
- **tasks.md**: `$VAULT_PATH/2 - Business/Operations/tasks.md`
- **Client files directory**: `$VAULT_PATH/2 - Business/Clients/`
- **Output file**: `$VAULT_PATH/0-Dashboard/morning-brief.md` (overwrite each run)

## Steps

### 1. Determine the target date

- Default: today
- With `--tomorrow`: tomorrow

### 2. Get the bookings for the target date

Read `sessions.csv`. Filter for rows where `date` matches the target date and `status = scheduled`. For each row, extract: `client_name`, `time`, `week_number` (if populated).

If there are no matching rows, write a one-line file: "No sessions scheduled on [date]." and stop.

### 3. For each client booked

Open `$VAULT_PATH/2 - Business/Clients/[Client Name]/[Client Name].md`. Find the `## Session Log` heading and read the most recent `### ` entry beneath it.

Extract from that entry:
- The date of the last session
- `program_changes` field (anything pending for next session)
- `flagged_body_parts` field
- `recurring_themes` field
- Any line in the bullet content that mentions "next time", "next session", or things to watch for

Also read `tasks.md`. Find the `## [Client Name]` section and collect all `- [ ]` lines (open tasks only — ignore `- [x]`).

If the client file doesn't exist or is empty, note that and move on.

### 4. Write the brief

Format:

```markdown
# Morning Brief — [Target date, friendly format]

## [Time] — [Client Name] (wk[N] if known)

**Last session**: [date]
**Pending changes**: [program_changes from last session, or "None"]
**Watch**: [flagged_body_parts + recurring_themes, or "Nothing flagged"]
**Notes for today**: [extracted next-time notes, or omit if none]
**Open tasks**: [- [ ] items from tasks.md, or omit if none]

---

## [Time] — [Next Client]
...
```

Order by session time, earliest first.

If a client has nothing pending, nothing flagged, and no open tasks, the entry can be a single line: `**Nothing flagged from last session.**`

### 5. Confirm completion

No reply needed beyond writing the file. The log will pick up errors.

## Edge cases

- **Booking but no client file**: Write the booking with `**No prior session data.**`
- **Client file exists but empty**: Same as above
- **Cancelled/rescheduled bookings**: Skip
