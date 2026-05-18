---
description: Create a NotebookLM notebook for a book, load the PDF, and save audio overview prompts and test-me scenarios. Stage 3 of the book-study pipeline.
argument-hint: [book-slug]
---

# /book-study nlm-load

Stage 3 of the book-study pipeline. Creates a NotebookLM notebook, loads the book's PDF as a source, generates audio overview prompts per chapter grouping, and saves test-me scenario queries as notebook notes.

## Arguments

- `$1` — Book slug (e.g. `anatomy-trains`, `supple-leopard`). Must match an existing manifest with at least some clusters at status `noted`.

Read `C:\Users\Tom\.claude\skills\book-study\SKILL.md` before doing anything else. It defines the NotebookLM prompt templates and audio overview tracker format.

## Prerequisites

1. **Manifest exists** with at least one cluster at status `noted`. If no clusters are noted, stop: "Run `/book-study extract` first."
2. **NotebookLM auth is fresh.** Before doing anything, check auth by running a lightweight NotebookLM command. If it fails, stop immediately with:

   > "NotebookLM auth has expired. Run the manual PowerShell re-auth step first, then rerun this command."

   Do not attempt to re-auth automatically. Do not proceed past this check if it fails.

3. **NotebookLM skill is accessible** at `C:\Users\Tom\.claude\skills\notebooklm\`. Commands are invoked via `python scripts/run.py nlm.py [command]` from that directory.

## Procedure

### 1. Create the notebook

```bash
cd C:\Users\Tom\.claude\skills\notebooklm
python scripts/run.py nlm.py create-notebook "[Book Title]"
```

Save the returned notebook ID. Update the manifest's `notebooklm_notebook_slug` field if it differs from what was set at init.

### 2. Load the PDF as a source

```bash
python scripts/run.py nlm.py add-source [notebook-id] --file "[pdf_path from manifest]"
```

Confirm the source was added successfully. If it fails (file too large, format issue), report clearly and stop. The notebook is useless without the source.

### 3. Generate and save audio overview prompts

Group clusters into chapter-level audio overview units. Each chapter (or tight group of 2-3 related chapters) gets one audio overview prompt.

Use the template from SKILL.md:

```
Create an audio overview covering [cluster titles or chapter title].

Focus on:
- What a personal trainer needs to know for client programming
- Practical cues, assessments, and common restriction patterns
- Common misconceptions or places trainers get this wrong
- Where this connects to other systems or movement patterns

Treat the listener as an experienced personal trainer with 10+ years' experience, not a student. Skip introductory explanations of basic anatomy. Assume familiarity with major muscle groups and movement terminology.
```

Customise the first line for each chapter's actual content. Don't use the generic template verbatim for every chapter.

Save each prompt as a note in the NotebookLM notebook:

```bash
python scripts/run.py nlm.py add-note [notebook-id] --title "Audio Prompt — Ch[N] [Chapter Title]" --content "[prompt text]"
```

### 4. Generate and save test-me scenario queries

Pull the NotebookLM Queries from each completed cluster's Obsidian note. These were written during Stage 2 (extract).

For each cluster, save its queries as a single notebook note:

```bash
python scripts/run.py nlm.py add-note [notebook-id] --title "Test Me — [Cluster Title]" --content "[scenario queries]"
```

Group all queries for one cluster into a single note rather than one note per query. This keeps the notebook navigable.

### 5. Update the audio overview tracker

Write to `Home Vault\3 - Knowledge\Books\[Book Title]\_audio-overview-tracker.md`.

Add each chapter's audio overview to the Pending section:

```markdown
- [ ] **Ch[N] — [Chapter Title] ([cluster count] clusters)**
  - Prompt: "[the customised prompt text]"
  - Clusters covered: [list of cluster titles]
  - Estimated listen: [estimate based on cluster count: 1-2 clusters = 10-15 min, 3-4 = 15-20 min, 5+ = 20-25 min]
```

### 6. Update the manifest

For each cluster that had its queries saved to NotebookLM, update status from `noted` to `nlm-loaded`.

Write the updated manifest back to disk.

### 7. Report back

Output:

- Notebook created (name and ID)
- PDF loaded (confirm success)
- Audio overview prompts saved (count and chapter list)
- Test-me scenarios saved (count of notes, total query count)
- Audio overview tracker updated (path)
- Reminder: "Audio overviews need to be triggered manually in NotebookLM's web interface. Work through the tracker queue during feeds or the commute."
- Next step: `/book-study audio-prompts [book-slug]` to see the queue, or `/book-study content-review [book-slug]` to review content flags

## Failure Modes

- **Auth expired** — stop immediately, point to manual re-auth. Never try to work around this.
- **PDF too large for NotebookLM** — report the limit and suggest splitting the PDF into parts. Do not proceed without a loaded source.
- **Note creation fails** — report which note failed, continue with the rest, flag the failures in the report
- **Manifest shows zero `noted` clusters** — stop, point to `/book-study extract`
