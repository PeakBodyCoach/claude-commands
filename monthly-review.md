---
description: Generate per-client monthly pattern summaries from session history. Run on the 1st of each month for the month just ended.
---

# Monthly Review

You are generating per-client pattern summaries for the month just ended. The goal is to surface things Tom would never spot week-to-week — recurring complaints, exercise progression patterns, mood/life trends, anything he's said he'd action and hasn't.

## Inputs

- **Client files directory**: `$VAULT_PATH/2 - Business/Clients/`
- **Output directory**: `$VAULT_PATH/2 - Business/Clients/_monthly-reviews/`
- **Reference month**: the calendar month immediately prior to today's run date

## Steps

### 1. Identify the reference month

If running on 1 May 2026, the reference month is April 2026. Use this to filter session entries.

### 2. For each client file

Open every `.md` file in the clients directory (excluding `_inbox.md` and the `_monthly-reviews` subfolder). Find the `## Session Log` heading and filter the `### YYYY-MM-DD` entries beneath it to those falling within the reference month.

If a client has fewer than 2 sessions in the month, skip them. Pattern detection needs at least 2 datapoints.

### 3. Extract patterns

Across the month's sessions for each client, surface:

- **Body parts flagged repeatedly** (appeared in 2+ sessions): list with frequency
- **Recurring exercises with progression notes**: which lifts moved, which stalled, which regressed
- **Mood/energy trends**: any pattern across the month (consistently low energy weeks 2-3, etc.)
- **Recurring life events**: travel, illness, sleep issues, work stress mentioned more than once
- **Pending program changes**: anything written as `program_changes` that doesn't appear actioned in a subsequent session
- **Open tasks**: read `$VAULT_PATH/2 - Business/Operations/tasks.md`, find the `## [Client Name]` section, and list any `- [ ]` items whose source date `(YYYY-MM-DD)` falls within the reference month. These are tasks raised that month that are still open.

Be conservative. Don't invent patterns from single mentions. The threshold is 2+ instances within the month.

### 4. Write the per-client summary

File: `$VAULT_PATH/2 - Business/Clients/_monthly-reviews/[Client Name] — [Month Year].md`

Format:

```markdown
# [Client Name] — [Month Year]

**Sessions this month**: [count]
**Workout types covered**: [A, B, C]

## Recurring body parts flagged
- Shoulder — 4 sessions (sessions of [dates])
- Lower back — 2 sessions ([dates])

## Exercise progression
- Squat: 100kg → 110kg across the month, RPE stable at 7-8
- Bench: stalled at 80kg three sessions running, RPE creeping 7→8→9

## Life events
- Racquetball injury (mentioned 3x, mid-month onward)
- Travel for work (week of 14th)

## Pending program changes
- Bench → 82.5kg next session (logged 27th, not yet actioned)

## Open tasks
- "Send revised programme" (logged 12th, still Not started)

## Patterns worth investigating
[Brief — 2-4 sentences max — anything that looks like a real pattern Tom should think about. Coaching judgment stays with Tom; this is signal-surfacing only.]
```

If a section has nothing to report, omit the section entirely. Don't write "None" or "Nothing flagged" — just leave it out.

### 5. Generate roster summary

Also write a single roster-level file: `$VAULT_PATH/2 - Business/Clients/_monthly-reviews/_roster — [Month Year].md`

Format:

```markdown
# Roster Summary — [Month Year]

## Cross-client patterns
- 4 clients flagged shoulder issues this month (Rich, Mo, Belinda, Simon) — worth reviewing how shoulders are loaded across programmes
- 3 clients stalled on bench progression (Rich, Fergus, Andrew)

## Open tasks across roster
- Total: [count of all `- [ ]` items in tasks.md with source dates in reference month]
- Oldest: [task] (logged [date], [client])

## Sessions delivered
- Total sessions: [count]
- Per client: [list with counts]
```

### 6. Report

Reply with: count of per-client reports written, link/path to roster summary, and any notable cross-client patterns. Under 10 lines.

## Edge cases

- **Client with fewer than 2 sessions this month**: Skip
- **Client file missing**: Skip
- **No clients meet threshold**: Write only the roster summary noting low session counts, don't generate empty per-client files
