# /research-tiers — Three-Tier Research Command

Invoke as: `/research-tiers $ARGUMENTS`

---

## Context: The tier system

All research topics live in:
`C:\Users\Tom\Documents\Home Vault\2 - Business\Content\Brand & Strategy\positioning-topics.md`

Each topic bullet is tagged with one of three tiers. Sub-bullets contain Tom's existing stance notes — always read these before starting work.

| Tag | Tier | What it means | Pipeline |
|---|---|---|---|
| `#overview` | Cursory summary | Never heard of it / no knowledge — just need the gist | Web synthesis (lightweight) |
| `#evidence` | Evidence check | Have a stance — need studies/data to back it | PubMed + Consensus + synthesis |
| `#research` | Deep research | Need genuine study before forming a view | Full `/research` → `/notebooklm-build` → `/content-brief` |

---

## Usage modes

**Single topic — auto-routes by tag:**
`/research-tiers saturated fat and heart disease`
Looks up the topic in positioning-topics.md, reads the tag, runs the matching pipeline.

**Batch overviews — processes multiple `#overview` topics in one run:**
`/research-tiers batch-overview`
`/research-tiers batch-overview 8`
Processes 5 topics by default. Pass a number to override.

**Explicit tier override — ignores the tag:**
`/research-tiers --overview [topic]`
`/research-tiers --evidence [topic]`
`/research-tiers --research [topic]`

---

## Tier 1: Overview pipeline

**Goal:** Enough grounding to form a basic view. Fast. No NotebookLM.

### Single topic steps

1. Open positioning-topics.md. Find the topic line and read its sub-bullet (Tom's note — may be "never heard of this" or blank).
2. Run two web searches:
   - `[topic] nutrition evidence based`
   - `[topic] scientific consensus`
3. Synthesise a brief knowledge note using the output format below. 350–450 words total. No padding.
4. Write to vault. Print confirmation.
5. Offer to update the tag in positioning-topics.md.

### Batch overview mode

1. Open positioning-topics.md. Extract all lines tagged `#overview` plus their sub-bullet notes. Display the full list and total count.
2. Confirm batch size: default 5, or use the number passed by the user.
3. Process each topic sequentially (not in parallel):
   - Read Tom's note
   - One targeted web search: `[topic] evidence based explained`
   - Synthesise overview note (350 words max in batch mode — keep it tight)
   - Write to vault
   - Print: `✓ [topic] → [path]`
4. After the batch, report:

```
Batch complete — [n] overview notes written.

✓ [Topic 1] → [path]
✓ [Topic 2] → [path]
...

[N] #overview topics still in the queue. Run `/research-tiers batch-overview` to continue.
```

5. Ask: *Update any tags in positioning-topics.md? Say "update [topic] to #evidence" or "remove [topic]" and I'll make the changes.*

### Overview output format

```markdown
---
title: "[Topic, title-cased]"
tags:
  - topic/[nutrition|training|supplementation|recovery|body-composition|health|psychology]
  - tier/overview
  - status/overview-complete
created: [YYYY-MM-DD]
source: web-synthesis
related: ["[[Related Concept 1]]", "[[Related Concept 2]]"]
---

# [Topic]

> [One-sentence bottom line. Blunt and practical. No hedging.]

## What it is

[1–2 paragraphs. What this concept, claim, or debate actually is. Plain English — no jargon without explanation.]

## The main claim or debate

[1 paragraph. What the central argument is. Who believes what, and why the disagreement exists.]

## Evidence in brief

- [Key finding or consensus point 1]
- [Key finding or consensus point 2]
- [Notable caveat or where evidence is thin]

## Tom's context

[Tom's existing note from positioning-topics.md, verbatim. Then 1–2 sentences on what this means for a fat loss or muscle building coaching context.]

## Next step

After reviewing, update positioning-topics.md:
- Change to `#evidence` if you now have a stance and want studies behind it
- Remove the tag if fully resolved
```

**Save to:** `C:\Users\Tom\Documents\Home Vault\3 - Knowledge\[subfolder based on topic/ tag]\[Topic].md`

Subfolder map:
| topic/ tag | Path |
|---|---|
| nutrition | `3 - Knowledge\Nutrition` |
| training | `3 - Knowledge\Training` |
| supplementation | `3 - Knowledge\Supplementation` |
| recovery | `3 - Knowledge\Recovery` |
| body-composition | `3 - Knowledge\Body Composition` |
| health | `3 - Knowledge\Health` |
| psychology | `3 - Knowledge\Psychology` |

---

## Tier 2: Evidence pipeline

**Goal:** Build an evidence file that backs up a stance Tom already holds.

### Steps

1. Open positioning-topics.md. Find the topic line. Read Tom's stance note — this is the position to validate and support.
2. Run `/pubmed [topic]` — retrieve 5–8 studies. Prefer meta-analyses, systematic reviews, RCTs, year 2015+.
3. Run `/consensus [topic]` — retrieve the Consensus Meter verdict and the top study cards. (For supplement-specific evidence grades, run `/examine [topic]` instead or in addition.)
4. Synthesise an evidence note. Translate study findings into plain coaching language. Flag where the evidence supports Tom's stance cleanly, and where it is weaker or more nuanced.
5. Write to vault. Print confirmation.
6. Output a suggested refined stance note, ready to paste back into positioning-topics.md.

### Evidence output format

```markdown
---
title: "[Topic] — Evidence File"
tags:
  - topic/[category]
  - tier/evidence
  - status/evidence-complete
created: [YYYY-MM-DD]
source: pubmed + consensus
---

# [Topic] — Evidence File

## Tom's position

[Verbatim from positioning-topics.md sub-bullet]

## Evidence verdict

[1 paragraph: does the literature support the position? How strongly? What is the overall evidence quality?]

## Key studies

| Study | Type | Finding | Year |
|---|---|---|---|
| [Author et al.] | [Meta-analysis / RCT / Cohort] | [One-sentence finding] | [Year] |

[4–6 rows. PubMed links below the table.]

1. **[Title]**
   https://pubmed.ncbi.nlm.nih.gov/[PMID]/
   [Study type] · [Journal] · [Year]

## Consensus.app summary

[Consensus Meter verdict + 2–4 top study findings in plain language]

## Where the evidence is thin

[Honest gaps — where studies don't cleanly back the position, or where nuance matters]

## Suggested positioning-topics.md update

> [Refined, sharpened stance note — ready to paste as the sub-bullet on the topic line. Should be more specific and citation-grounded than the original.]
```

**Save to:** `C:\Users\Tom\Documents\Home Vault\3 - Knowledge\[subfolder]\[Topic] — Evidence.md`

---

## Tier 3: Deep research pipeline

**Goal:** Genuine knowledge building from scratch. Full source sweep, NotebookLM synthesis, content strategy.

### Steps

Run the full existing pipeline in order:

1. **`/research [topic]`** — four-source sweep (YouTube, PubMed, Consensus, Substack). Produces the source URL list.
2. **`/notebooklm-build [topic]`** — creates a NotebookLM notebook, adds all sources, runs the full 20-query set, synthesises and writes the Obsidian knowledge note to the vault.
3. **`/content-brief [topic]`** — reads the NotebookLM output and produces a research dossier, ready for the `content-sheet` skill.

No changes to those commands — this tier just routes to them and ensures they run in sequence.

### After completion

Update positioning-topics.md:
- The `#research` tag can be removed, or changed to `#research-done` if you want a record
- Offer to update the sub-bullet with a sharpened stance note based on what the research revealed

---

## After any tier completes

Always confirm:
```
✓ [Topic] — [tier] complete
Note written to: [full vault path]
```

Then ask:
> Update the tag in positioning-topics.md? Options: change to `#[next-tier]`, mark as `#[tier]-done`, or remove entirely.
