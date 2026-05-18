---
description: Summarise content opportunities flagged during extraction, ready for handoff to angle generation. Stage 5 of the book-study pipeline.
argument-hint: [book-slug]
---

# /book-study content-review

Stage 5 of the book-study pipeline. Reads the content opportunities flagged during extraction and presents them in a format ready for the angle generation and content sheet workflow.

## Arguments

- `$1` — Book slug (e.g. `anatomy-trains`, `supple-leopard`). Or `all` to review across all books.

Read `C:\Users\Tom\.claude\skills\book-study\SKILL.md` for the content flag criteria and format fit heuristics.

## Prerequisites

1. **Master content opportunities file exists** at `Home Vault\3 - Knowledge\Books\_content-opportunities.md`.
2. **At least one cluster has been extracted** for the requested book (check manifest for any `noted` or `nlm-loaded` status entries).

If prerequisites aren't met, report clearly and point to the right earlier stage.

## Procedure

### 1. Read the master file

Parse the content opportunities for the requested book. Count entries per format category.

### 2. Read the manifest for additional context

Load the manifest and cross-reference content flags with their source clusters. This lets you add context about which clusters the flags came from.

### 3. Present the summary

Output in this structure:

```
Content Opportunities — [Book Title]
[Total] flags across [N] clusters
══════════════════════════════════

CAROUSEL / SHORT-FORM ([count])
────────────────────────────────
1. [Concept] — "[Hook]"
   Source: Ch[N], [Cluster Title]
   Why carousel: [one line on format fit]

2. ...

BLOG / LONG-FORM ([count])
────────────────────────────────
1. [Concept] — "[Hook]"
   Source: Ch[N], [Cluster Title]
   Why blog: [one line on format fit]

2. ...

VIDEO — TALKING HEAD ([count])
────────────────────────────────
...

VIDEO — EXERCISE DEMO ([count])
────────────────────────────────
...

VIDEO — REACTION ([count])
────────────────────────────────
...
```

If `$1` is `all`, show each book as a separate section, then add a combined summary at the end with total counts across all books.

### 4. Offer handoff

After presenting the summary, ask Tom which flags he wants to take forward:

> "Want to run any of these through angle generation? Pick by number or say 'skip' to just review."

If Tom picks one or more:

- Confirm the concept and hook
- Offer to launch the angle generation skill directly with the concept as input
- The angle generation skill accepts a topic in any form, so passing the concept + hook + source context is enough

If Tom says skip, that's fine. The flags stay in the master file for later.

### 5. Cross-book connections (when reviewing `all`)

When reviewing across all books, flag any concepts that appear related across different books. For example, if Anatomy Trains flags "fascial continuity as a programming lens" and Supple Leopard flags "joint-by-joint approach to mobility", note the connection. These cross-book angles often produce the strongest content because they synthesise rather than summarise.

Present these as a separate section:

```
CROSS-BOOK ANGLES
────────────────────────────────
• [Concept A from Book 1] + [Concept B from Book 2]
  Potential angle: [what the synthesis could be]
  Suggested format: [best fit]
```

## Failure Modes

- **Master file missing** — create it from the SKILL.md template (empty), then report that no flags exist yet and point to `/book-study extract`
- **Book section empty** — extraction either hasn't run or no flags were generated. Check manifest to determine which, and report
- **Book slug doesn't match** — list available books from existing manifests and ask Tom to pick
