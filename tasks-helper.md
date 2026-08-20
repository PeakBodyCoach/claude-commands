---
description: Walks a task board one task at a time and, for each, interprets it, proposes a concrete solution, and runs the right automation where one exists — otherwise gives exact manual steps. Built for Khaela to clear her board without deferring; Tom can run it on any client too. Triggers: "help me with my tasks", "work through my tasks", "what do I do for these tasks", "run the task helper", "/tasks-helper".
---

# Tasks Helper

Goes through a task board **one task at a time**, suggests the most concrete solution possible, and does as much directly in code as it can. Designed so Khaela never gets stuck on "I'm not sure what to do" — every task ends in either: done, precise manual steps, or tracked-and-reassigned to Tom.

This is a guided, interactive run. Do ONE task, resolve it, then move to the next. Don't batch.

## Inputs

- **tasks.md**: `$VAULT_PATH/2 - Business/Operations/tasks.md`
- **tasks-archive.md**: `$VAULT_PATH/2 - Business/Operations/tasks-archive.md`
- Client files under `$VAULT_PATH/2 - Business/Clients/[Client]/`
- 1Fit auth profile (to test live capability): `C:\Users\Tom\.claude\skills\1fit-sync\.auth\profile\`

## Step 0 — Scope and capability

**Scope** (default = Khaela's board):
- Default: every open `- [ ]` task that does NOT contain `#person/tom`, across all `## [Client]` sections. That's Khaela's board.
- If Tom runs it and names a client ("tasks helper for Simon") or asks for his own list, scope accordingly (a client's section, or `#person/tom` tasks).
- **`all` argument** (`/tasks-helper all`, or "the whole board", "everything including mine"): work **every** open `- [ ]` task across all sections, including `#person/tom` ones. This is the scope the morning remote run uses (scheduled task "PBC Tasks Helper Remote" → `claude-tasks-remote.ps1`), so Tom can clear his own tasks and the pool in one pass. Live 1Fit is available in that run (Tom's machine).

**Live-1Fit capability check** (decides whether automations can actually execute): live 1Fit runs through the persistent Chromium profile at `1fit-sync\.auth\profile\`. Before offering to run any live-1Fit automation, confirm it's available — the profile exists and the runner is logged in. **Khaela's 1Fit auth is not yet set up**, so when she runs this, treat live 1Fit as UNAVAILABLE: prep everything and hand off the live push, don't pretend to run it. When Tom runs it, live 1Fit is available.

State the scope and capability in one line at the start, e.g.: `Working Khaela's board — 6 tasks. Live 1Fit: not available on this machine yet, so I'll prep + hand off any OneFit pushes.`

## Step 1 — Per-task loop

For each task, in order, present a tight block and stop for a decision:

```
[3 of 6]  Mo Hussein
Task: Correct squat log on OneFit — sets of 8 should be sets of 5.
Read as: a logged-set fix inside 1Fit's UI.
Plan: <one of the routes below>
```

### Route the task

Match the task's intent to a route. Pick the most automated route that fits.

| Task reads like | Route | Runs now? |
|---|---|---|
| Add a new programme / cycle to OneFit; update/push a client's programme to OneFit | **Prep then push**: run `/normalise-programme [client]` (vault-side, fixes names + gaps), then `/1fit-sync [client]` | normalise: yes · push: live-1Fit |
| Add an exercise to the library / to OneFit | `/add-exercise [names]` | live-1Fit |
| Sync a client's habits | `/habit-sync [client]` | live-1Fit |
| Upload / sync a meal plan | `/meal-plan-sync [client]` | live-1Fit |
| Push macros to 1Fit | `/macro-sync [client]` | live-1Fit |
| Audit / normalise a programme against the library | `/normalise-programme [client]` | yes (vault-side) |
| Update a client's programme / split | Edit the client's Programmes.md in the vault (2 - Business\Clients\[Client]\) | yes |
| Look up / research cues, notes, progressions | Web + vault search, then write the note where it belongs | yes |
| Correct a logged set, remove an exercise, rename an exercise in 1Fit | **No automation** (1fit-sync is create-only) → exact manual steps | manual |
| Message a client, make a coaching call, write a programme from scratch | Tom's job → reassign | reassign |

### Execute the route

- **Runs now (vault-side / research):** propose it, and on a yes, actually run it (invoke the skill or do the work). Show the result.
- **Live-1Fit, and capability is available (Tom):** propose the exact command, and on a yes, run the automation.
- **Live-1Fit, capability NOT available (Khaela, pre-auth):** do all the prep you can now — run `/normalise-programme` so the programme is sync-ready, confirm the cycle exists, classify any new exercises, find demo videos — then output the ready-to-run command and a one-line handoff: "Prepped. The live OneFit push needs the 1Fit login (not set up for you yet). Either Tom runs `/1fit-sync [client]`, or I tag this to Tom." Offer to reassign or leave it parked.
- **Manual:** give numbered, click-by-click 1Fit steps for exactly this change. Be specific (which client, plan, workout, exercise, field, old value → new value).
- **Reassign:** confirm, then tag the line `#person/tom` (it drops off Khaela's board). Don't archive — it's still open, just hers-no-more.

### Close the task

After the route resolves, ask what to do with the task:
- **Done** (it was completed, by automation or by Khaela doing the manual steps): mark it `- [x] … ✅ <today>` and move it to `tasks-archive.md` under its `## [Client]` heading, keeping the `#task` tag and adding a `<!-- reason -->` (same mechanics as `/reconcile-tasks` step 4).
- **Reassign to Tom**: add `#person/tom`, leave open.
- **Leave open** (prepped but not finished, or she'll come back to it): no change, optionally append a short ` <!-- prepped: ... -->` note.

Then move to the next task.

## Step 2 — Report

At the end:

```
Tasks helper — [date], [scope]
Done + archived: X
Prepped, awaiting 1Fit auth / handoff: Y  (list)
Reassigned to Tom: Z  (list)
Left open: W
```

Keep it under 10 lines.

## Rules

- One task at a time. Always wait for Khaela's decision before acting or moving on.
- Prefer the most automated route, but never run a live-1Fit automation when capability is unavailable — prep and hand off instead. Be honest about what actually ran.
- Manual steps must be specific enough to follow without further questions. If you don't know a detail (which workout, exact current value), say so and tell her where to check.
- Never silently defer. A task Khaela can't do becomes either precise manual steps or a tracked `#person/tom` reassignment.
- All task edits go through `tasks.md` / `tasks-archive.md` in the canonical format (keep `#task`, keep `(raised: ...)`).
