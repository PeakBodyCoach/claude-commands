---
description: Read topic clusters from the manifest, extract content from the PDF, and write structured Obsidian notes. Stage 2 of the book-study pipeline.
argument-hint: [book-slug] [chapter-range]
---

# /book-study extract

Stage 2 of the book-study pipeline. Reads the manifest built by `/book-study init`, processes each topic cluster's PDF pages, and writes one Obsidian note per cluster. Also flags content opportunities and appends them to the master list.

## Arguments

- `$1` — Book slug (e.g. `anatomy-trains`, `supple-leopard`). Must match an existing manifest.
- `$2` — Chapter range to process (e.g. `1-3`, `4`, `all`). Use ranges to avoid context limits on large books.

Read `C:\Users\Tom\.claude\skills\book-study\SKILL.md` before doing anything else. It defines the note template, tag taxonomy, content flag criteria, and voice rules.

## Prerequisites

Before starting, check:

1. **Manifest exists** at `Home Vault\3 - Knowledge\Books\[Book Title]\_manifest.json`. If not, stop: "Run `/book-study init` first."
2. **PDF is accessible** at the path stored in the manifest's `pdf_path` field. If not, stop and report.
3. **Book folder exists** at `Home Vault\3 - Knowledge\Books\[Book Title]\`. If not, stop: init hasn't completed properly.

Load the manifest and identify which clusters fall within the requested chapter range. Skip any cluster where `status` is already `noted` unless Tom explicitly says to reprocess.

## Procedure

### 1. Plan the extraction

List the clusters to process. Output a brief summary:

```
Processing [Book Title], chapters [range]:
- Ch3: "SBL — Tracks and Stations" (pp. 65–74) — pending
- Ch3: "SBL — Clinical Patterns" (pp. 75–84) — pending
- Ch3: "SBL — Assessment and Release" (pp. 85–92) — pending
```

If the range includes clusters already marked `noted`, report them as skipped. If everything in the range is already done, say so and suggest the next unprocessed range.

### 2. Read each cluster's pages

Use the `pdf-reading` skill approach. For each cluster:

- Read the full page range assigned to that cluster in the manifest
- If a cluster's page range is large (15+ pages), read in chunks rather than all at once to avoid context overflow
- Focus on extracting: key concepts, practical implications for PT work, specific exercises or assessments mentioned, anatomical relationships, anything counterintuitive or commonly misunderstood

You're reading for **application, not academic summary**. The question is always: "What does Tom need to know from these pages to programme better for his clients?"

### 3. Write the Obsidian note

For each cluster, produce one note using the template from SKILL.md.

**Filename:** `[Book Title] - [Cluster Title].md`
**Location:** `Home Vault\3 - Knowledge\Books\[Book Title]\`

Section-by-section guidance:

**Frontmatter:**
- `type: book-notes`
- `domain: training` (default for anatomy/movement books; use `nutrition` if the book is nutrition-focused)
- `source`, `author`, `chapter`, `chapter_title` — from manifest
- `cluster_id` — from manifest
- `tags` — conceptual and thematic terms from the content (3–8 tags). Use the book's own terminology here: `myofascial-meridians`, `joint-centration`, `motor-control`, etc.
- `body_regions` — from the controlled vocabulary in SKILL.md. Only include regions the cluster genuinely covers. Don't pad.
- `movement_patterns` — from the controlled vocabulary. Only include patterns the cluster directly bears on.
- `clinical_relevance` — what client complaints or presentations this maps to. Freer vocabulary, kebab-case.
- `date_processed` — today's date
- `notebooklm_notebook` — book slug
- `pdf_pages` — page range as string (e.g. "65-74")

**Core Concepts:**
- 4–8 bullets. Each should stand alone as a retrievable idea.
- Write in Tom's voice: direct, practical, British spelling, contractions. Not textbook language.
- No em dashes. No "quietly" figuratively. No symmetrical flips.
- Each bullet should make sense without reading the others.
- If a concept is genuinely complex, use two sentences. Don't oversimplify anatomy to the point of inaccuracy.

**What This Means for Programming:**
- 3–6 bullets. Each connects a concept from above to a real programming decision.
- Be specific: "If a client presents with X, this tells you to check Y before programming Z."
- Think about the populations Tom works with: busy professionals, gym-goers with movement issues, people returning from injury.

**Assessments & Cues:**
- Movement tests, screening positions, or self-assessment options mentioned in or implied by the source material.
- Coaching cues derived from the anatomical or movement understanding in this cluster.
- If the book provides specific assessment protocols, include them concisely.
- If no assessments are directly mentioned but relevant ones are implied, include them with a note that they're inferred.

**Related Exercises & Movements:**
- Wikilink format: `[[Exercise Name]] — one-line reason it's linked`
- Include exercises the book mentions directly AND relevant exercises Tom would programme based on this material.
- Keep to 4–8 entries. Quality over quantity.
- If an exercise note doesn't exist yet in the vault, link it anyway. Broken links are fine; they show what notes to create later.

**Cross-References:**
- Links to other clusters in the same book where relationships exist.
- Links to clusters in other books if the manifest for that book exists.
- Links to relevant existing vault notes (exercises, course notes, etc.) if you can identify them from the note title conventions.
- Format: `[[Note Title]] — one-line relationship description`
- Only link where the relationship adds genuine retrieval value.

**Content Opportunities:**
- Apply the six criteria from SKILL.md: counterintuitive, commonly misunderstood, visually demonstrable, challenges mainstream advice, surprising connection, actionable paradigm shift.
- Threshold: only flag what you'd actually want to produce content on. Aim for 2–5 per cluster. Zero is fine if nothing qualifies.
- Write the concept and hook in content-ready voice. When Tom pulls these into `/content-sheet`, the hook should already feel like his.
- Format as a markdown table: Concept | Hook | Format

**NotebookLM Queries:**
- 2–4 scenario-based "test me" questions per cluster.
- Structure: client presents with [pattern] → what does this material tell you to do?
- Make them realistic to Tom's practice: the kind of thing he'd actually see walk in the door.
- These get saved into NotebookLM later in Stage 3. For now they live in the note.

### 4. Update the manifest

After each cluster note is written:

- Set the cluster's `status` to `"noted"`
- Set `obsidian_note_path` to the full path of the written note
- Populate `key_concepts` with short-form summaries of the Core Concepts bullets
- Populate `practical_applications` with short-form summaries of the Programming section
- Populate `related_movements` with the exercise names (no wikilink brackets)
- Populate `content_flags` with objects: `{ "concept": "...", "hook": "...", "format": "..." }`
- Populate `cross_references` with the linked note titles

Write the updated manifest back to disk after each cluster (not just at the end). If something fails mid-run, the manifest reflects what's been completed.

### 5. Append to the master content opportunities file

For each content flag generated, append to `Home Vault\3 - Knowledge\Books\_content-opportunities.md`.

Find the book's section (e.g. `## Anatomy Trains`). Find the right format sub-section (e.g. `### Carousel / Short-form`). Append the entry:

```
- **[Concept]** (Ch[N], [[Book Title - Cluster Title]]) — "[Hook]"
```

If the book's section doesn't exist in the file yet, create it with all five format sub-sections (Carousel / Short-form, Blog / Long-form, Video — Talking Head, Video — Exercise Demo, Video — Reaction).

Never duplicate entries. If a concept with the same text already exists under that book's section, skip it.

### 6. Update the book index

In `Home Vault\3 - Knowledge\Books\[Book Title]\_index.md`, flip the checkbox for each completed cluster from `- [ ]` to `- [x]`.

### 7. Report back

After processing all clusters in the range, output:

- Clusters processed (count and names)
- Clusters skipped (already noted)
- Content opportunities flagged (count and quick list of concepts)
- Any clusters where the PDF pages were unclear, the content was thin, or cross-references couldn't be resolved
- Next step: suggest the next unprocessed chapter range, or if all chapters are done, suggest moving to `/book-study brief` to build the front-door Verdict and Cliffnotes before loading into NotebookLM

## Handling Large Books

If the requested range would produce more than ~6 clusters, warn Tom and suggest splitting into smaller batches. Context limits mean extraction quality drops if too many clusters are processed in one run.

Recommended batch size: 2–4 chapters per run (roughly 4–10 clusters depending on the book).

## Voice Rules (from SKILL.md)

Apply to all note content:
- No em dashes (commas or full stops)
- British spelling throughout
- Contractions always
- No "quiet/quietly" figuratively
- No symmetrical flips ("not X, but Y")

Do NOT apply:
- Heavy anti-AI restructuring (these are reference notes, not published content)
- Hook-driven openings

**Exception:** content opportunity hooks should be written in content-ready voice. These feed directly into the content pipeline.

## Failure Modes

- **Manifest not found** — stop, point to `/book-study init`
- **PDF unreadable at specified pages** — report which cluster failed, skip it, continue with the rest, mark it `"status": "failed"` in manifest
- **Cluster pages don't match expected content** — likely a manifest error from init. Report clearly so Tom can fix the manifest and rerun
- **Master content opportunities file missing** — create it from scratch using the template in SKILL.md
- **Context overflow on a large cluster** — split the read into chunks, process sequentially, merge the output

Never silently produce a thin note because the read failed. A note with two vague bullets is worse than no note with a clear error message.
