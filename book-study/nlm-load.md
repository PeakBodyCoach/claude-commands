---
description: Create a NotebookLM notebook, load the book PDF plus the front-door Verdict and Cliffnotes, and save audio overview prompts and test-me scenarios. Stage 4 of the book-study pipeline.
argument-hint: [book-slug]
---

# /book-study nlm-load

Stage 4 of the book-study pipeline. Creates a NotebookLM notebook, loads the book's PDF plus the front-door Verdict and Cliffnotes as sources, generates audio overview prompts (front-door overviews first, then per chapter grouping), and saves test-me scenario queries as notebook notes.

## Arguments

- `$1` — Book slug (e.g. `anatomy-trains`, `supple-leopard`). Must match an existing manifest with at least some clusters at status `noted`.

Read `C:\Users\Tom\.claude\skills\book-study\SKILL.md` before doing anything else. It defines the NotebookLM prompt templates and audio overview tracker format.

## Prerequisites

1. **Manifest exists** with at least one cluster at status `noted`. If no clusters are noted, stop: "Run `/book-study extract` first."
1b. **Front-door docs exist.** Check for `00 - [Book Title] - Verdict.md` and `00 - [Book Title] - Cliffnotes.md` at the book folder root (and a `brief` object on the manifest). If they're missing, warn Tom that the front door hasn't been built and offer to either run `/book-study brief` first (recommended) or proceed loading the book PDF alone without the front-door overviews. Don't silently skip them.
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

Then add the two front-door docs as sources so their audio overviews can be generated from Tom's own critique and digest, not just the book:

```bash
python scripts/run.py nlm.py add-source [notebook-id] --file "[book folder]\00 - [Book Title] - Verdict.md"
python scripts/run.py nlm.py add-source [notebook-id] --file "[book folder]\00 - [Book Title] - Cliffnotes.md"
```

If the front-door docs are missing and Tom chose to proceed without them (see prerequisite 1b), skip this and note it in the report.

### 3. Generate and save the front-door audio overviews

These come first because they're what Tom listens to first. Use the two front-door prompt templates from SKILL.md.

Generate the **Verdict overview** against the Verdict source, using the Verdict audio overview prompt. Save the prompt as a note:

```bash
python scripts/run.py nlm.py add-note [notebook-id] --title "Audio Prompt — Verdict" --content "[Verdict audio overview prompt]"
```

Generate the **Cliffnotes overview** against the Cliffnotes source, using the accessible audio overview prompt (build concepts up, define jargon, no assumed expertise). This is deliberately the opposite register to the expert-PT chapter overviews below. Save the prompt as a note:

```bash
python scripts/run.py nlm.py add-note [notebook-id] --title "Audio Prompt — Cliffnotes" --content "[accessible audio overview prompt]"
```

These two go at the top of the audio tracker's "Front door — listen first" block in step 6.

### 4. Generate and save the per-chapter audio overview prompts

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

### 5. Generate and save test-me scenario queries

Pull the NotebookLM Queries from each completed cluster's Obsidian note. These were written during Stage 2 (extract).

For each cluster, save its queries as a single notebook note:

```bash
python scripts/run.py nlm.py add-note [notebook-id] --title "Test Me — [Cluster Title]" --content "[scenario queries]"
```

Group all queries for one cluster into a single note rather than one note per query. This keeps the notebook navigable.

### 6. Update the audio overview tracker

Write to `Home Vault\3 - Knowledge\Books\[Book Title]\_audio-overview-tracker.md`.

First add the two front-door overviews to a "Front door — listen first" block at the very top of the tracker, above Pending (format in SKILL.md):

```markdown
## Front door — listen first
- [ ] **Verdict — [Book Title]**
  - Prompt: [Verdict audio overview prompt]
  - Source: `00 - [Book Title] - Verdict.md`
  - Estimated listen: 8–12 min
- [ ] **Cliffnotes — [Book Title]**
  - Prompt: [accessible audio overview prompt]
  - Source: `00 - [Book Title] - Cliffnotes.md`
  - Estimated listen: 10–15 min
```

Then add each chapter's audio overview to the Pending section:

```markdown
- [ ] **Ch[N] — [Chapter Title] ([cluster count] clusters)**
  - Prompt: "[the customised prompt text]"
  - Clusters covered: [list of cluster titles]
  - Estimated listen: [estimate based on cluster count: 1-2 clusters = 10-15 min, 3-4 = 15-20 min, 5+ = 20-25 min]
```

### 7. Update the manifest

For each cluster that had its queries saved to NotebookLM, update status from `noted` to `nlm-loaded`.

Write the updated manifest back to disk.

### 8. Report back

Output:

- Notebook created (name and ID)
- Sources loaded (book PDF, Verdict, Cliffnotes — confirm each)
- Front-door overviews queued (Verdict + Cliffnotes, flagged as listen-first)
- Per-chapter audio overview prompts saved (count and chapter list)
- Test-me scenarios saved (count of notes, total query count)
- Audio overview tracker updated (path)
- Reminder: "Audio overviews need to be triggered manually in NotebookLM's web interface. Listen to the Verdict and Cliffnotes first, then work through the chapter queue during feeds or the commute."
- Next step: `/book-study audio-prompts [book-slug]` to see the queue, or `/book-study content-review [book-slug]` to review content flags

## Failure Modes

- **Auth expired** — stop immediately, point to manual re-auth. Never try to work around this.
- **PDF too large for NotebookLM** — report the limit and suggest splitting the PDF into parts. Do not proceed without a loaded source.
- **Note creation fails** — report which note failed, continue with the rest, flag the failures in the report
- **Manifest shows zero `noted` clusters** — stop, point to `/book-study extract`
- **Front-door docs missing** — warn, offer to run `/book-study brief` first or proceed with the book PDF alone. If proceeding alone, skip the front-door sources and overviews and say so in the report
