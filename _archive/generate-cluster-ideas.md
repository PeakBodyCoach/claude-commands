# /generate-cluster-ideas

Reads an existing cluster file and appends a Content Ideas section near the top, converting raw entries and internal references into specific, voice-shaped content angles organised by format.

## Purpose

The clustering command organises source material by theme and flags positioning gaps. This command does the step that should always have been downstream of it: turning the clustered material into a working queue of content ideas.

## Critical execution notes for Claude Code

**Do not use sub-agents.** The main agent reads the cluster file, generates ideas, and writes the updated file directly.

**One cluster file per run.** This command processes a single specified cluster file, not all of them in a batch. Run it repeatedly for each cluster.

**Additive, not destructive.** The existing file structure is preserved in full. The Content Ideas section is inserted after the Summary and before Positioning gaps exposed. Nothing existing is overwritten or removed.

**Respect freeform thoughts sections.** Some cluster files have a `## Thoughts` or similar section where Tom has written stance notes. Read these first — when present, they shape the content ideas. When absent, work from source entries alone.

## Inputs

**Cluster file path:** prompted at runtime. Accept a full path or a filename (if filename only, assume `C:\Users\Tom\Documents\Home Vault\2 - Business\Content\Research\Clusters\[filename]`).

**Positioning doc path (read-only, for context):**
`C:\Users\Tom\Documents\Home Vault\2 - Business\Content\Brand & Strategy\positioning-topics.md`

The positioning doc is read for context on Tom's stances where they exist — not modified.

---

## Pass 1 — Read and analyse

1. Read the cluster file in full.
2. Note the presence or absence of a freeform thoughts section (commonly `## Thoughts`, could also be a different heading).
3. Enumerate:
   - Pre-angled entries (already have an `Angle:` line)
   - Raw external entries (no existing angle)
   - Internal reference topics (from research-glp1, research-technique, research-progression, research-muscle — already loosely angled but not in content-idea form)
   - Saturated entries (marked *Saturated — avoid*)
4. Read the positioning doc and identify any stances that sit under the positioning topics listed in this cluster's gaps section. Note them as input.

Print: `Cluster: [name]. [N] entries total. Thoughts section: [present/absent]. [N] positioning stances found for this territory.`

---

## Pass 2 — Generate content ideas

Produce ideas in three passes, in this order:

### 2a — Pillar ideas (cross-entry bundling)

Look for groups of related entries within the cluster that could be combined into one larger piece rather than several small ones. Candidates:

- Multiple raw entries converging on the same theme (e.g. AG1 + glutamine + ZMA + "supplements are mostly a scam" → one pillar piece on the supplement industry's credibility crisis)
- A raw external entry that happens to align with a pre-angled entry or an internal reference topic
- An internal reference topic where several muscle-group or technique bullets chain into a coherent programme-design piece

For each pillar, produce:
- **Title:** the piece's working title in PBC voice (direct, sardonic where appropriate, no AI-intensifier language)
- **Format:** blog | carousel | reel | undecided (default to blog when the territory wants depth; carousel when the take is punchy; reel when it's a single sharp hook)
- **Core take:** one sentence, the actual argument
- **Supporting entries:** list the entry titles from the cluster that feed this pillar
- **Why it works:** one sentence on why this is a strong piece — converging signal, positioning fit, demographic relevance, timeliness, etc.

Cap at 3 pillars per cluster. If the cluster doesn't naturally yield any, say so explicitly rather than forcing one.

### 2b — Single-piece ideas

For each remaining entry not absorbed into a pillar (except saturated ones), produce a content idea:

- Raw external entries: convert the claim into a PBC content angle — what's Tom's take, where does the tension live, what format suits it
- Pre-angled entries: restate the existing angle in tightened content-idea form (title, format, take)
- Internal reference topics: convert the reference bullet into a specific content piece, not a general area

Each idea follows the same structure as pillars but without the supporting entries field:
- **Title:** working title
- **Format:** blog | carousel | reel
- **Core take:** one sentence
- **Source entry:** the single entry this came from
- **Why it works:** one sentence

Do not produce an idea for every entry if several are redundant. Combine where combination is stronger; skip where the idea would be weak or already covered by a pillar.

### 2c — Saturated and avoid

List any entries explicitly flagged as saturated (marked *Saturated — avoid*), with a one-line note on why producing this angle is not worth doing right now. These are intelligence, not ideas — they keep Tom from wasting effort on crowded angles.

---

## Pass 3 — Prioritisation

Across all pillar and single-piece ideas in this cluster, assign priority:

- **High:** strong positioning fit, converging signal, fills a gap Tom explicitly cares about (GLP-1 specialism, core brand debunking, strong client relevance)
- **Medium:** solid idea, no urgency
- **Low:** valid but thin, or adjacent to Tom's main territory

Also flag cross-cluster crossover where noticed — ideas that could sit in more than one cluster (note which other cluster). Don't force these; only flag when obvious.

---

## Pass 4 — File write-back

Assemble the new Content Ideas section. Structure:

```markdown
## Content Ideas

*Generated [YYYY-MM-DD]. [N] pillar ideas, [M] single-piece ideas.*

### Pillar ideas

#### [Title]
**Format:** [format]
**Priority:** [High/Medium/Low]
**Core take:** [one sentence]
**Supporting entries:** [entry titles]
**Why it works:** [one sentence]
**Cross-cluster:** [if applicable]

---

### Single-piece ideas

#### [Title]
**Format:** [format]
**Priority:** [High/Medium/Low]
**Core take:** [one sentence]
**Source:** [entry title]
**Why it works:** [one sentence]
**Cross-cluster:** [if applicable]

---

### Saturated — do not produce

- [Entry title]: [one-line reason]

---
```

Insert this section into the cluster file immediately after the Summary block (and any Thoughts section that follows it) and before the Positioning gaps exposed section. The existing file content remains untouched below.

Before writing, create a backup: `[original-filename].bak-YYYY-MM-DD-HHMMSS` in the same Clusters folder.

Print: `Appended Content Ideas section to [filename]. Backup: [backup-filename]. [X] pillars, [Y] single-piece ideas, [Z] saturated flags.`

---

## Pass 5 — Summary

Print a compact summary:

```
Cluster: [cluster name]
Ideas generated: [total]
  - Pillar ideas: [N]
  - Single-piece ideas: [M]
  - Saturated/avoid: [Z]
Priority breakdown: High [X], Medium [Y], Low [Z]
Cross-cluster flags: [N]
Backup: [path]

Next step: review the Content Ideas section in [filename]. Run again against the next cluster file when ready.
```

---

## Notes on voice and style

When generating titles and core takes, apply voice-foundation rules:

- No em dashes. Use commas, full stops, or colons.
- British spelling throughout.
- No AI-intensifier words ("crucial", "vital", "pivotal", "game-changing", "revolutionary"). Direct is better than dramatic.
- Contractions where natural.
- Sardonic where appropriate; straight when the subject is serious.
- No banned figurative "quiet/quietly".
- Titles should read like a confident coach wrote them, not like an AI assistant wrote them.

Content ideas are Tom's to use or discard — the goal is to produce options he can pick from quickly, not to commit him to producing them all.

## Error handling

- If the cluster file path doesn't exist, print the path and ask for correction.
- If the Content Ideas section already exists in the target file, ask whether to skip, replace, or append a new dated section below the existing one. Default: ask.
- If the backup write fails, abort before modifying the main file.

## What not to do

- Do not use the Task tool or any sub-agent.
- Do not modify the Positioning gaps exposed section, the entries list, or any other existing section of the cluster file.
- Do not regenerate the positioning doc cross-reference data — it's already done.
- Do not force a specific number of ideas. Quality over quantity. A cluster producing 5 sharp ideas is better than one producing 15 padded ones.
- Do not produce ideas for saturated entries beyond the one-line avoid flag.
