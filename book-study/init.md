---
description: Ingest a book PDF, build the manifest, and scaffold the Obsidian vault folders. Stage 1 of the book-study pipeline.
argument-hint: [pdf-path] [book-slug]
---

# /book-study init

Stage 1 of the book-study pipeline. Takes a PDF path and book slug, produces a manifest, scaffolds vault folders, and reports the cluster structure so Tom can sense-check before running extract.

## Arguments

- `$1` — Absolute path to the book PDF (e.g. `C:\Users\Tom\Documents\Books\anatomy-trains.pdf`)
- `$2` — Book slug, kebab-case (e.g. `anatomy-trains`, `supple-leopard`)

Read `C:\Users\Tom\.claude\skills\book-study\SKILL.md` before doing anything else. It defines the manifest schema, cluster definition, folder layout, and tag taxonomy this command produces.

## Procedure

### 1. Validate inputs

- Confirm the PDF exists at `$1`. If not, stop and tell Tom.
- Confirm `$2` is kebab-case and doesn't collide with an existing book folder. If a folder at `Home Vault\3 - Knowledge\Books\[derived title]\` already exists, stop and ask whether to overwrite, resume, or pick a new slug.

### 2. Read the PDF

Use the `pdf-reading` skill approach — don't try to cat a binary file.

Read strategically, not exhaustively:

- **Table of contents / front matter** — full read. This gives you chapters, part structure, page ranges.
- **Each chapter's first 2–3 pages** — skim to catch the chapter's internal sub-heading structure and any opening summary.
- **Each chapter's sub-heading pages** — read enough around each sub-heading to decide whether it marks a cluster boundary or is just a sub-point.

You do NOT need to read the full body of every chapter at this stage. That happens in `/book-study extract`. The goal here is structural: chapters, clusters, page ranges.

If the PDF has no usable TOC (scanned, poorly OCRd, or just bad), report this clearly and ask Tom whether to:
- Push forward with visual inspection of chapter opener pages
- Abort and get a better PDF

### 3. Identify topic clusters

Apply the cluster rule from SKILL.md: *if you'd want to retrieve two ideas separately during a client session, they're separate clusters*.

For each chapter:
- Read the sub-heading structure
- Group sub-headings into 2–4 clusters based on retrieval logic
- Assign each cluster a human-readable title, a kebab-case slug, and a page range
- Build the cluster_id as `[book-slug]/ch[N]/[cluster-slug]`

Short chapters (under ~10 pages) often produce a single cluster. Dense chapters may produce 5. Don't force a target number.

Where the book has Parts or Sections above chapters, preserve that in the manifest as a `part` field on each chapter, but clusters remain the primary unit.

### 4. Build the manifest

Write to `C:\Users\Tom\Documents\Home Vault\3 - Knowledge\Books\[Book Title]\_manifest.json`.

`[Book Title]` uses the title case from the PDF (e.g. `Anatomy Trains`, not `anatomy-trains`). This is the human-readable folder name.

Manifest fields follow the schema in SKILL.md. At init time:

- Top-level fields (title, author, edition, book_slug, pdf_path, total_pages, date_processed, notebooklm_notebook_slug) — all filled
- Chapter fields (chapter_number, title, page_range, and part if relevant) — filled
- Cluster fields — `cluster_id`, `cluster_slug`, `title`, `page_range` filled; `status: "pending"`; all content arrays (`key_concepts`, `practical_applications`, `related_movements`, `content_flags`, `cross_references`) initialised empty; `obsidian_note_path: null`

### 5. Scaffold vault folders and initial files

Create if they don't exist:

**Book folder:**
```
Home Vault\3 - Knowledge\Books\[Book Title]\
```

**Book index** at `Home Vault\3 - Knowledge\Books\[Book Title]\_index.md`:

```markdown
---
type: book-index
domain: training
source: "[Book Title]"
author: "[Author]"
book_slug: "[book-slug]"
date_processed: 2026-04-16
---

# [Book Title]

## Chapters

### Chapter [N] — [Chapter Title]
- [ ] [[Book Title - Cluster 1 Title]] (pages X–Y)
- [ ] [[Book Title - Cluster 2 Title]] (pages X–Y)
```

Checkboxes flip to `[x]` as clusters are processed in Stage 2.

**Audio overview tracker** at `Home Vault\3 - Knowledge\Books\[Book Title]\_audio-overview-tracker.md`:

Initialise with the template from SKILL.md, Pending section empty (populated in Stage 3). Complete section empty.

**Master content opportunities file** at `Home Vault\3 - Knowledge\Books\_content-opportunities.md`:

Only create this if it doesn't already exist. If it exists, append a new top-level section `## [Book Title]` with the five empty format sub-sections (Carousel, Blog, Talking Head, Exercise Demo, Reaction). Do not overwrite existing books' sections.

### 6. Report back

Output to Tom in the chat:

- Book identified: title, author, edition, total pages
- Structure found: N chapters, M total clusters
- Cluster breakdown per chapter (concise table or list)
- Files created (paths)
- Any warnings (missing TOC, ambiguous cluster boundaries, chapter ranges that look off)
- Next step: `/book-study extract [book-slug] [chapter-range]` — suggest a sensible first range (e.g. Ch1–3 or the first Part)

Format the cluster breakdown so Tom can scan it and spot anywhere you've mis-split. He'll flag corrections before extract runs.

## Failure modes

- **PDF unreadable / scanned without OCR** — stop, report, suggest OCR pass first
- **No usable TOC** — offer the visual inspection fallback or abort
- **Existing book folder collision** — ask before touching anything
- **Vault path not found** — check `C:\Users\Tom\Documents\Home Vault\3 - Knowledge\` exists; if not, stop and surface it

Never proceed past a failure silently. The manifest is the source of truth for every later stage — if init gets it wrong, everything downstream compounds the error.
