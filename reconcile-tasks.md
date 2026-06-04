---
description: Close the loop on tasks.md. Scans each client's Session Log, Programmes, and Khaela reports for evidence that open tasks are already done, then presents confirm batches. On approval, ticks tasks with a done-date and moves them to tasks-archive.md. Also flags stale and ambiguous items, and normalises task format. Use whenever Tom says "reconcile tasks", "tidy the task list", "what tasks are actually done", "triage tasks", or "clean up tasks.md".
---

# Reconcile Tasks

`tasks.md` has a writer for *open* tasks (`/process-sessions`) but, historically, no writer for *done*. Work happens in the real world (programme updated, OneFit fixed, conversation had) and the box never gets ticked, so the list drifts. This command is the missing done-writer: it gathers evidence, asks Tom to confirm, then closes and archives.

**Never mark a task done without either strong file evidence or Tom's explicit confirmation. Never delete a task line. Archiving is a move, not a delete.**

## Inputs

- **tasks.md**: `$VAULT_PATH/2 - Business/Operations/tasks.md` (canonical open list, per-client `## [Client]` sections)
- **Archive**: `$VAULT_PATH/2 - Business/Operations/tasks-archive.md` (create if missing)
- **Per client**: `$VAULT_PATH/2 - Business/Clients/[Client]/[Client] - Session Log.md`, `[Client] - Programmes.md`, `[Client] - Profile.md`
- **Khaela reports**: `$VAULT_PATH/2 - Business/Operations/Khaela/_session-reports/*.md`
- **sessions.csv**: `$VAULT_PATH/2 - Business/Operations/Bookings/sessions.csv` (for credit / cancellation / catch-up tasks)
- **clients.csv**: `$VAULT_PATH/2 - Business/Clients/clients.csv` (roster + status — `paused`/`churned` clients' whole sections are archive candidates)

## Task format (canonical, going forward)

```
- [ ] Description #person/khaela 📅 2026-06-10 ⏫ (raised: 2026-05-29) #task
```

- `- [ ]` open, `- [x]` done. A done task ends with `✅ YYYY-MM-DD`.
- **Every task line must end with `#task`** — the Tasks plugin's global filter. Without it the dashboards don't see the task. Hidden in rendered views. Carry it through when archiving too.
- **Assignee (three states)**: `#person/tom` = Tom-only, hidden from Khaela's board. `#person/khaela` = explicitly Khaela's. **No tag = unassigned**, visible to Khaela as available. Khaela's board (`Khaela Tasks.md`) shows everything that is NOT `#person/tom`. (Migrate any legacy `— Khaela` suffix to `#person/khaela`.)
- **Due date**: `📅 YYYY-MM-DD` only where a real deadline exists. Omit otherwise.
- **Priority** (optional): `⏫` high, `🔼` medium, `🔽` low. Omit for normal.
- **Raised date**: keep the existing trailing `(YYYY-MM-DD)`; rewrite as `(raised: YYYY-MM-DD)` when you touch a line. This is the source date, not a due date.
- These are Obsidian Tasks-plugin signifiers. The plugin is not currently installed (only Dataview is), so they render as plain text today; the Dataview dashboards read them fine. If Tom installs the Tasks plugin later, the dashboards become clickable.

## Steps

### 1. Scope

Default: all clients with a `## [Client]` section in tasks.md, plus `## Roster-level`. If Tom names a client ("reconcile Belinda"), scope to that one section only.

Read clients.csv. Any task under a section for a client whose status is `paused` or `churned` is an automatic **archive candidate** (reason: client paused/churned) unless the task is a billing chase still owed.

### 2. Gather evidence per task

For each open `- [ ]` under each in-scope `## [Client]`:

Read that client's **Session Log** (entries since the task's raised date), **Programmes.md** (active cycle), and any **Khaela report** mentioning the client. For roster-level billing tasks, check **sessions.csv** and any invoicing notes. Classify the task into exactly one bucket:

| Bucket | Test |
|---|---|
| **DONE** | Strong evidence it happened: a later session log `program_changes`/narrative records the change; the active programme already contains it; a Khaela report says she did it; sessions.csv shows the credit/catch-up applied. |
| **STALE** | Raised > 60 days ago, no mention in any session since, and not obviously still needed. Likely abandoned. |
| **PAUSED** | Belongs to a `paused`/`churned` client. |
| **OPEN** | Still valid and actionable, no completion evidence. |
| **AMBIGUOUS** | Partial or conflicting evidence; needs Tom's call. |

Cite the evidence in one short phrase per task (e.g. "Programmes.md active cycle now lists incline DB curl" or "Khaela report 2026-05-21 confirms upload"). Never assert DONE without a citable source.

### 3. Present confirm batches

Per client, show a compact block. Do not dump the whole vault back at Tom — one line per task, grouped by bucket:

```
## Belinda Boakye  (9 open)
DONE (evidence) — tick + archive?
  1. Add assisted pull-up/dip back into solo workouts — Programmes.md active cycle lists both (2026-05-29)
  2. Credit Belinda one session (coach missed 13 May) — sessions.csv row 13 May = coach-missed, credit noted
STALE (>60d, no mention) — archive as dropped?
  3. Follow up on nutrition adjustment mindset — raised 2026-02-27, no mention since
OPEN — keeping
  4. Re-establish weight tracking — still live
AMBIGUOUS — your call:
  5. Research luteal-phase fatigue strategies — partial: discussed verbally, never written up. Done or keep?
```

Then ask once per client (or once for the whole run if Tom says "do them all"): **"Tick + archive the DONE, drop the STALE, leave the rest? Tell me any to move."** Default action on approval: archive DONE and dropped-STALE; leave OPEN and unresolved AMBIGUOUS in place.

### 4. Apply

On Tom's confirm, for each task to close:

1. **Mark done in place first**: change `- [ ]` to `- [x]`, append ` ✅ <today's date>`. For dropped/stale, append ` ❌ <today>` instead of `✅` (cancelled, not completed).
2. **Move the line** out of tasks.md into `tasks-archive.md` under a `## [Client]` heading (create the heading if absent), keeping the full line plus a trailing `<!-- reason: ... -->` comment.
3. Remove the now-moved line from tasks.md.
4. For tasks **kept** but touched, normalise to canonical format (add `#person/khaela` if it was `— Khaela`; rewrite `(date)` → `(raised: date)`).
5. If a `## [Client]` section in tasks.md is left empty, leave the heading in place (morning brief and the dashboards expect it) with nothing under it.

`tasks-archive.md` line example:
```
- [x] Add assisted pull-up and assisted dip back into solo workouts ✅ 2026-06-04 (raised: 2026-05-29) <!-- reason: active programme already lists both -->
```

### 4b. Assignment pass (optional)

If Tom asks to "sort assignments" or "who does what", or after a large triage, surface the **unassigned** open tasks (no `#person/` tag) grouped by likely owner:

- **Khaela-doable** (OneFit uploads/fixes, exercise-library additions, Notion updates, logging corrections) — leave unassigned (she sees these on her board) or tag `#person/khaela` if Tom wants them explicitly hers.
- **Tom-only** (coaching calls, client messages, writing/normalising programmes, technique investigation, nutrition strategy, billing decisions) — tag `#person/tom` so they drop off Khaela's board.

Propose the split, let Tom confirm, then apply the tags in place. Default if Tom doesn't engage: leave everything unassigned (Khaela sees the full pool, which is the intended default).

### 5. Report

```
Reconcile tasks — [date]
Scanned: N open tasks across M clients
Closed (done): X
Dropped (stale/paused): Y
Left open: Z
Archived to: tasks-archive.md
Still need your call: [list any AMBIGUOUS Tom didn't resolve]
```

Keep under 12 lines unless flagging issues.

## Edge cases

- **Billing chases** (roster-level): only mark DONE if sessions.csv / invoicing notes show paid or re-issued. An unpaid overdue invoice stays OPEN even if old.
- **Credit/catch-up tasks**: DONE if sessions.csv shows the credit burned or the catch-up session logged.
- **Duplicate tasks** (same intent, two lines): close the older, keep the clearest one; note the merge in the archive comment.
- **No evidence either way**: that is OPEN, not DONE. When unsure, leave it and surface as AMBIGUOUS. Bias to keeping a task rather than wrongly closing it.
- **Re-run safety**: idempotent. Already-archived tasks aren't in tasks.md, so a second run just re-scans whatever remains open.
