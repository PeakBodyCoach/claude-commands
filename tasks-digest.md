---
description: Read-only daily triage of the open task board. Classifies every open task into do-now / needs-you / gated and writes a punch list that the 06:30 morning push folds in. Headless-safe — never edits tasks.md, never runs automations. NOT the interactive board-clearer (that's /tasks-helper) or the close/archive pass (/reconcile-tasks). Triggers: "/tasks-digest", the daily "PBC Tasks Digest" scheduled task.
---

# Tasks Digest

A **read-only** morning triage of the open task board. Runs headless before the 06:30 push (the "PBC Tasks Digest" scheduled task, ~06:00) and writes a punch list Tom scans on his phone and in Obsidian.

**This command NEVER edits `tasks.md`, never ticks or archives a task, and never runs any automation or skill.** It only reads and classifies. Closing/archiving is `/reconcile-tasks`; working tasks one-by-one is `/tasks-helper`. If you find yourself about to write to `tasks.md`, stop — that is out of scope.

## Inputs

- **tasks.md**: `C:\Users\Tom\Documents\Home Vault\2 - Business\Operations\tasks.md`
- **Output punch list**: `C:\Users\Tom\Documents\Home Vault\2 - Business\Operations\Tasks Punch List.md` (overwritten each run)

## Steps

### 1. Read the board

Read `tasks.md`. Consider only open tasks (`- [ ]`). Ignore every `- [x]` line. Each `## [Client]` / `## Projects` / `## Bark Leads` / etc. section is a bucket the task belongs to — keep the section name as the task's label.

### 2. Classify each open task into exactly one bucket

Read the full task line **and its trailing `<!-- ... -->` comments** — the blocker is very often only in the comment, not the visible text.

- **Gated** — the task is blocked on something not yet true. Signals: "gated on", "blocked", "HOLD", "hold the", "waits on", "waiting on", "pending [X]", "once [X] lands/ends", "paused" / "on his pause ending", "needs DNS", "needs [auth/access]", "can't run until", a `📅` date still in the future with an explicit dependency, or a comment describing an unmet precondition. When a task is clearly waiting on another named task or an external event, it is **gated** even if it carries `#person/tom`.
- **Needs you** — not gated, and it genuinely needs Tom: carries `#person/tom` (his coaching/programming/nutrition judgement, his voice for a client message/call, his presence `#at-session`, his recall, or a strategic/executive call). `#at-session` items are Needs-you (he actions them in the room).
- **Do now** — not gated, and NOT `#person/tom`: the unassigned / `#person/khaela` pool. Actionable today by automation or admin.

When a task could read as either gated or actionable, prefer **gated** only if there is a concrete named blocker; a vague "should probably" is Do-now or Needs-you, not gated.

### 3. Write the punch list

Overwrite `Tasks Punch List.md` with exactly this shape. **Line 1 must be the freshness stamp** — the morning push reads it to confirm the digest ran today:

```markdown
<!-- generated: YYYY-MM-DD HH:MM by tasks-digest -->
# Tasks Punch List — [friendly date, e.g. Thursday 13 August]

Read-only daily triage of open tasks in [[tasks]]. Not a substitute for /tasks-helper (work the board) or /reconcile-tasks (close + archive).

## Do now (N)
- **[Section]** — [one-line task summary]

## Needs you (N)
- **[Section]** — [one-line task summary]

## Gated (N)
- **[Section]** — [one-line task summary] — *gated on: [the blocker]*
```

Rules for the summaries:
- One line each, plain and specific enough to act on without opening tasks.md. Trim the task to its actionable core; drop `#tags`, `(raised:)`, and `tt:` markers.
- Order each bucket by urgency: overdue `📅` and `⏫` first, then `🔼`, then the rest.
- If a bucket is empty, still print its heading with `(0)` and no bullets.
- Keep Bark-Leads follow-up chores and routine Content-Posting tasks in whichever bucket they fall — don't special-case them.

### 4. Report (chat only — for interactive runs)

If run interactively, print the three counts and the file path. If run headless, the file write is the whole job; a one-line stdout summary is enough for the log.

## Notes

- **Idempotent and safe to re-run** — it only overwrites the punch list.
- The punch list is a snapshot, not a ledger: every run rebuilds it from scratch off the current `tasks.md`.
- If `tasks.md` can't be read, write a punch list whose body is a single line `ERROR: could not read tasks.md` under a current freshness stamp, so the morning push surfaces the failure rather than going silent.
