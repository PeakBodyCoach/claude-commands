# /restructure-clusters

Rewrites existing cluster markdown files in the new Source material format using the enriched `_entries.json`. Preserves any manually-added sections (Thoughts, Content Ideas) from the existing files.

## Purpose

The old cluster file format had entries broken down into Pre-angled / Raw external / Internal reference sections, with claims only. The new format organises entries by source type (External content pieces / Content Intel / Internal reference library) with creator, URL, and synopsis per entry. This command rewrites each cluster file in the new shape without losing content that was added manually after the initial build (Thoughts sections, Content Ideas sections, edits to the Summary).

## Critical execution notes

**Do not use sub-agents.** Main agent handles all passes directly.

**One cluster file per pass.** Read one cluster file, rewrite it, wait for `next`. Do not batch.

**Preserve manually-added content.** Thoughts sections, Content Ideas sections, and any edits made to the Summary must survive intact. Only rewrite sections generated from entry data.

**Back up before overwriting.** Every cluster file gets a `.bak-YYYY-MM-DD-HHMMSS` backup before rewrite.

## Inputs

**Enriched entries JSON:**
`C:\Users\Tom\Documents\Home Vault\2 - Business\Content\Research\Clusters\_entries.json`

**Clusters JSON:**
`C:\Users\Tom\Documents\Home Vault\2 - Business\Content\Research\Clusters\_clusters.json`

**Positioning matches JSON (one per cluster, from the earlier positioning cross-reference pass):**
`C:\Users\Tom\Documents\Home Vault\2 - Business\Content\Research\Clusters\_positioning_matches_cluster_[N].json`

**Cluster markdown files (existing):**
`C:\Users\Tom\Documents\Home Vault\2 - Business\Content\Research\Clusters\[cluster-filename].md`

---

## Pass 1 — Preflight check

Verify:
- `_entries.json` exists and every entry has `creator`, `url`, and `synopsis` populated (indicating `/enrich-entries` has been run).
- `_clusters.json` exists.
- All positioning matches JSON files exist for every cluster.
- Every cluster listed in `_clusters.json` has a corresponding markdown file.

If any check fails, print what's missing and exit cleanly.

If all checks pass, print:
```
Found [N] cluster files ready to restructure.
Enriched entries: [N]
Say 'next' to begin with cluster 1.
```

---

## Pass 2 — Restructure cluster files (one at a time)

For each cluster in `_clusters.json`, in order:

### Step A: Read the existing cluster file and extract preserved sections

Parse the file and identify these sections by heading:
- The title (H1) — keep as-is
- The `## Summary` section — preserve the existing text (it may have been edited)
- Any `## Thoughts` section — preserve in full, including dictated voice notes
- Any `## Content Ideas` section — preserve in full
- The `## Positioning gaps exposed` section — regenerate fresh from the positioning matches JSON (not preserved)
- The existing entry sections (`## Pre-angled entries`, `## Raw external entries`, `## Internal reference topics`) — discard, they will be replaced by the new Source material section

### Step B: Build the new cluster file

Structure:

```markdown
# [Cluster name from clusters.json]

*Generated [original generation date from existing file] from [idea bank filename]*
*Restructured [today's date] with enriched source data*

---

## Summary

[Preserved text from the existing Summary. Update only the "Entry counts" sub-block at the end to use the new category labels:]

**Entry counts:**
- External content pieces: [N]
- Intel-generated angles and research: [N]
- Internal reference topics: [N]

---

[IF Thoughts section existed in original file:]

## Thoughts

[Preserved content verbatim]

---

[IF Thoughts section did not exist, insert an empty one:]

## Thoughts

*Add freeform stance notes here. Dictated voice notes welcome. This section is your content material — the generate-cluster-ideas command will treat it as a first-class idea source.*

---

[IF Content Ideas section existed in original file:]

## Content Ideas

[Preserved content verbatim]

---

## Source material

*The swipe file for this theme. When producing content, browse here for framings, claims, and jumping-off points. Each item includes the creator, a URL where one exists, and a synopsis.*

### External content pieces

[For each entry in this cluster where:
  - source is watchlist-youtube, watchlist-email, or swipe-esg, OR
  - source is intel-competitor AND creator is not "Competitor landscape"
]

#### [Entry title]
**Creator:** [creator]
**Source:** [source_detail]
**URL:** [url if present, otherwise "no URL"]
**Synopsis:** [synopsis]
[IF pre_angled is true:]
**PBC angle (pre-set):** [existing_angle_note]

---

### Content Intel — angles, research briefs, competitor signal

[For each entry in this cluster where:
  - source is intel-angles or intel-research, OR
  - source is intel-competitor AND creator is "Competitor landscape"
]

#### [Entry title]
**Source:** [source_detail]
**URL:** [url if present, otherwise "no URL"]
**Synopsis:** [synopsis]
[IF pre_angled is true:]
**PBC angle (pre-set):** [existing_angle_note]

---

### Internal reference library

[For each entry in this cluster where source starts with "research-"]

#### [Entry title]
**Source:** [source_detail]
**Synopsis:** [synopsis]
**Angle:** [existing_angle_note]

---

## Positioning gaps exposed

[Regenerated from _positioning_matches_cluster_[N].json:]

- [ ] [Topic name] (existing — section: [section name])
- [ ] [Proposed topic name] (new — section: [section name])

---
```

### Step C: Back up and write

1. Create backup: `[cluster-filename].bak-YYYY-MM-DD-HHMMSS`
2. Write the new cluster file, overwriting the existing one.
3. Print:
   ```
   Cluster [N]/[total]: [cluster name]
   Backup: [backup filename]
   Preserved: [list — e.g. "Thoughts, Content Ideas"] or "(no manual additions found)"
   New entry counts: External [X], Intel [Y], Internal [Z]
   Say 'next' to process the next cluster or 'q' to stop.
   ```

### Step D: Handle user input

- `next`: proceed to next cluster
- `q`: stop cleanly. Processed clusters remain restructured; unprocessed ones remain untouched.
- Any other input: print the available commands and wait again.

---

## Pass 3 — Final summary

After all clusters processed:

```
Restructure complete.
Clusters rewritten: [N]
Preserved sections carried across:
  - Thoughts sections: [N] found and preserved
  - Content Ideas sections: [N] found and preserved
  - Summary edits: carried across verbatim where present

Backups in: [Clusters folder]

Old entry-type sections (Pre-angled / Raw external / Internal reference topics) have been replaced by the new Source material section organised by source type with creator, URL, and synopsis per entry.
```

---

## Error handling

- If a cluster file referenced in `_clusters.json` doesn't exist, log a warning and continue with the next cluster.
- If a positioning matches JSON file is missing for a cluster, skip regenerating the Positioning gaps section for that cluster — preserve the existing one from the old file instead.
- If a backup write fails, abort before rewriting the main file.
- If the file parser can't identify section boundaries cleanly (e.g. non-standard headings), print the problem, the cluster name, and ask whether to skip this cluster or abort.

## What not to do

- Do not use sub-agents.
- Do not modify `_entries.json`, `_clusters.json`, or the positioning matches JSONs.
- Do not touch the positioning doc.
- Do not discard Thoughts or Content Ideas content. If in doubt, preserve rather than drop.
- Do not process multiple clusters in a single response.
