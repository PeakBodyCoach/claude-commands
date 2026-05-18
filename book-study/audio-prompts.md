---
description: Display the audio overview queue for a book, showing pending and completed prompts. Stage 4 of the book-study pipeline.
argument-hint: [book-slug]
---

# /book-study audio-prompts

Stage 4 of the book-study pipeline. Reads the audio overview tracker and displays the queue so Tom can work through it in NotebookLM's web interface.

## Arguments

- `$1` — Book slug (e.g. `anatomy-trains`, `supple-leopard`). Or `all` to show trackers for every book.

Read `C:\Users\Tom\.claude\skills\book-study\SKILL.md` for the audio overview tracker format.

## Prerequisites

1. **Audio overview tracker exists** at `Home Vault\3 - Knowledge\Books\[Book Title]\_audio-overview-tracker.md`. If not, stop: "Run `/book-study nlm-load` first."

## Procedure

### 1. Read the tracker

Parse the tracker file. Count pending and completed entries.

### 2. Display the queue

Output a clean summary:

```
Audio Overview Queue — [Book Title]

Pending: [N] overviews
──────────────────────
1. Ch[N] — [Chapter Title] ([cluster count] clusters)
   Prompt: [first 100 chars]...
   Estimated listen: [time]

2. ...

Completed: [N] overviews
──────────────────────
✓ Ch[N] — [Chapter Title] (listened [date])
```

If `$1` is `all`, repeat for every book that has a tracker.

### 3. Offer mark-complete

Ask Tom if he's listened to any pending overviews. If he names one or more:

- Flip the checkbox from `- [ ]` to `- [x]` in the tracker file
- Add the listened date
- Move the entry from Pending to Complete
- Write the updated tracker back to disk

### 4. Suggest next action

If pending overviews remain, suggest which one to listen to next (shortest first for feed sessions, most foundational first for commutes).

If all are complete for this book, suggest moving to `/book-study content-review` or starting the next book.

## Failure Modes

- **Tracker file missing** — point to `/book-study nlm-load`
- **Book slug doesn't match any folder** — list available book folders and ask Tom to pick
