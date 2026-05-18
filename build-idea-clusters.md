# /build-idea-clusters

Clusters the Peak Body Coach idea bank into themed reference libraries. Each cluster file is a working swipe file scoped by topic — containing the source material (with URLs and synopses) you'd reference when producing content on that theme.

## Purpose

The cluster files are the long-lived artefact of this workflow. The idea bank is a monthly ingestion buffer; the cluster files are permanent, growing, thematically-organised swipe libraries that you open when you want to make content on a theme.

Each cluster file holds:
- What you've said on the topic (your Thoughts, when added)
- What others have said (source material — the swipe file proper, organised by source type)
- Where your positioning doc has gaps on this territory

Pre-generated content ideas are not part of the default output. They can be added by the separate `/generate-cluster-ideas` command if wanted.

## Critical execution notes for Claude Code

**Do not use sub-agents for extraction passes.** Sub-agents tend to re-read source files excessively and thrash on large inputs. The main agent handles all extraction passes directly.

**Extract one source type at a time, not all at once.** Each extraction pass is a narrow, bounded job with a clear stopping point. Do not combine passes.

**Append to the JSON file, do not overwrite.** Each pass after the first reads the existing `_entries.json`, appends its new entries, and writes back.

**Stop between passes and wait for `next`.** After each pass, print the count and wait for the user to say `next` before running the next pass. This prevents thrashing and lets the user spot issues early.

## Inputs

**Idea bank path:**
`C:\Users\Tom\Documents\Home Vault\2 - Business\Content\Research\Idea Bank - 19-04-2026.md`

*(Update this path at runtime if processing a different dated idea bank.)*

**Positioning doc path:**
`C:\Users\Tom\Documents\Home Vault\2 - Business\Content\Brand & Strategy\positioning-topics.md`

**Output folder:**
`C:\Users\Tom\Documents\Home Vault\2 - Business\Content\Research\Clusters\`

Create the folder if it does not exist.

---

## Pass 1 — Entry extraction (ten narrow passes)

Run each sub-pass in order. After each, print the count and wait for user to say `next`.

**Entry schema (universal):**
- `source`: source tag (e.g. "watchlist-youtube", "swipe-esg")
- `source_detail`: channel, newsletter, or section name
- `title`: entry title
- `creator`: named person or brand behind the content, where identifiable ("Layne Norton", "Stronger By Science", "ESG Fitness"). For research topics, use "Peak Body Coach reference library".
- `url`: direct URL to the source content. Empty string if no URL exists in the idea bank.
- `synopsis`: two to three sentences describing what the piece covered and what makes it notable. Longer than the previous one-line `claim` — enough that the user can decide whether to click through without reading the full entry in the idea bank.
- `pre_angled`: boolean
- `existing_angle_note`: if `pre_angled` is true, one-sentence summary of the Peak Body Coach angle. Otherwise blank.

### Pass 1a — watchlist-youtube

Read only the YOUTUBE section of the Content Watchlist in the idea bank. One entry per video.
- `source`: "watchlist-youtube"
- `source_detail`: channel name
- `creator`: channel name (same as source_detail for YouTube)
- `url`: the `**URL:**` line attached to each video entry in the idea bank
- `pre_angled`: false
- `existing_angle_note`: ""

Create `_entries.json` in the Clusters folder if it does not exist.

Print: `Pass 1a complete. [N] watchlist-youtube entries written. Say 'next' to continue.`

### Pass 1b — watchlist-email

Read only the Email Digest section. One entry per newsletter item.
- `source`: "watchlist-email"
- `source_detail`: newsletter name (e.g. "Ripped Body", "RP Strength", "The Ready State")
- `creator`: named author where given (e.g. "Andy Morgan" for Ripped Body, "Kelly Starrett" for The Ready State). If only the brand is named, use that.
- `url`: empty string (newsletters typically don't have stable URLs in the digest — leave blank)
- `pre_angled`: false

Append and write back. Print count and wait.

### Pass 1c — intel-angles

Read only the "Angles Swipe File" section inside Content Intel. One entry per numbered angle.
- `source`: "intel-angles"
- `source_detail`: "Content Intel Angles"
- `creator`: "Peak Body Coach Content Intel" (these are already angled for PBC)
- `url`: the `**Source:**` URL attached to each angle
- `pre_angled`: true
- `existing_angle_note`: one-sentence summary of the PBC angle

Append and write back. Print count and wait.

### Pass 1d — intel-research

Read only the "Body Composition & Fat Loss Research Brief" section inside Content Intel. One entry per numbered finding.
- `source`: "intel-research"
- `source_detail`: "Content Intel Research Brief"
- `creator`: the journal or study author where given in the entry, otherwise "Content Intel Research Brief"
- `url`: the `Source::` URL attached to each finding
- `pre_angled`: false

Append and write back. Print count and wait.

### Pass 1e — intel-competitor

Read only the Competitor section. One entry per numbered item across ALL subsections: "Top Topics Being Covered Right Now", "New Frameworks & Named Concepts", "Content Gaps", "Saturated Angles to Avoid".
- `source`: "intel-competitor"
- `source_detail`: which subsection the item came from (e.g. "Top Topics", "New Frameworks", "Content Gaps", "Saturated Angles")
- `creator`: the brand or platform named in the item (e.g. "HYROX365", "Menopause Movement", "MacroFactor"). For anonymous aggregate items (e.g. "Strength Training for Women" as a category), use "Competitor landscape".
- `url`: the `**Source:**` URL attached to each item
- `pre_angled`: false

Append and write back. Print count and wait.

### Pass 1f — swipe-esg

Read only the ESG Fitness section under Specific Swipes. One entry per POST.
- `source`: "swipe-esg"
- `source_detail`: "ESG Fitness"
- `creator`: "Emma Storey Gordon (ESG Fitness)"
- `url`: the `**URL:**` attached to each post (Instagram URL)
- `pre_angled`: true (ESG posts have "Angle for PBC" sections)
- `existing_angle_note`: one-sentence summary of the PBC adaptation angle

Append and write back. Print count and wait.

### Pass 1g — research-glp1

Read only the GLP-1 Knowledge Base section under Research. Each bullet under "Content topics:" in ALL GLP-1 subsections is ONE separate entry.
- `source`: "research-glp1"
- `source_detail`: subsection name (e.g. "GLP-1 Pharmacology", "GLP-1 Body Composition")
- `creator`: "Peak Body Coach reference library"
- `url`: ""
- `synopsis`: expanded from the bullet — the bullet text plus a sentence on why it's a usable content angle
- `pre_angled`: true
- `existing_angle_note`: one-sentence summary of the angle inherent in the bullet

Append and write back. Print count and wait.

### Pass 1h — research-technique

Read only the Technique Guides & Lever/Anatomy section under Research. Each bullet under "Content topics:" is ONE entry.
- `source`: "research-technique"
- `source_detail`: technique name
- `creator`: "Peak Body Coach reference library"
- `url`: ""
- `synopsis`: bullet text plus a sentence on its content angle
- `pre_angled`: true
- `existing_angle_note`: one-sentence summary

Append and write back. Print count and wait.

### Pass 1i — research-progression

Read only the Movement Pattern Progression Maps section. Each bullet under "Content topics:" is ONE entry.
- `source`: "research-progression"
- `source_detail`: pattern name
- `creator`: "Peak Body Coach reference library"
- `url`: ""
- `synopsis`: bullet text plus angle sentence
- `pre_angled`: true
- `existing_angle_note`: one-sentence summary

Append and write back. Print count and wait.

### Pass 1j — research-muscle

Read only the Muscle Group Reference Library section. Each bullet under "Content topics:" is ONE entry.
- `source`: "research-muscle"
- `source_detail`: muscle group
- `creator`: "Peak Body Coach reference library"
- `url`: ""
- `synopsis`: bullet text plus angle sentence
- `pre_angled`: true
- `existing_angle_note`: one-sentence summary

Append and write back.

Print: `Pass 1 complete. Total entries: [N]. Breakdown: [source tag counts]. Say 'next' to begin clustering.`

---

## Pass 2 — Clustering (with pause for approval)

Read `_entries.json`. Group entries by theme. Aim for roughly 8–12 clusters. Clusters should be themes a coach would recognise as coherent content territories.

Expected cluster categories based on the April 2026 idea bank (approximate, let the actual entries drive the final set):

- GLP-1 and pharmacological weight loss
- Volume, intensity, and progressive overload
- Exercise selection and technique
- Fat loss mechanism and calorie deficit
- Protein and nutrition
- Supplements and wellness industry misinformation
- Body composition, measurement, and metabolic adaptation
- Menopause, older adults, and population-specific training
- Maintenance, mindset, and adherence
- Muscle group reference
- Cardio, zone 2, and longevity
- Mobility, flexibility, and recovery

A cluster of 3-4 entries is fine if the theme is genuinely distinct. Do not force over-consolidation.

**This is a single pass. Do not use a sub-agent. Load `_entries.json` once, assign cluster IDs to each entry, write `_clusters.json` once.** Output structure:

```json
{
  "clusters": [
    {"id": 1, "name": "Cluster name", "entry_indices": [3, 17, 42]}
  ]
}
```

After writing `_clusters.json`, pause and print:

```
Proposed clusters:
1. [Cluster name] — [N] entries
2. [Cluster name] — [N] entries
...

Options:
  (a) approve and proceed
  (r) rename a cluster — format: r [number] [new name]
  (m) merge two clusters — format: m [number] [number]
  (s) split a cluster — format: s [number]
  (q) abort
```

Handle each option:
- `a`: proceed to Pass 3
- `r`: rename the cluster in `_clusters.json`, show updated list, re-prompt
- `m`: merge two clusters, prompt for new name, update file, re-prompt
- `s`: show the cluster's entries, ask which to split into a new cluster, update file, re-prompt
- `q`: exit cleanly, leave JSONs in place

Loop until user enters `a`.

---

## Pass 3 — Positioning doc cross-reference

For each cluster, do a separate pass. **One cluster per pass, do not batch.** Each pass:

1. Read the positioning doc once at start of pass.
2. Read `_clusters.json` and get the entries for this cluster.
3. For each entry, identify:
   - Existing positioning doc topics this entry touches (topic name, section header, whether stance is written)
   - Topics NOT in the positioning doc but that should be (proposed topic name, section, which entries triggered the proposal)
4. Write results to `_positioning_matches_cluster_[N].json`.
5. Print:
   ```
   Cluster [N] — [cluster name]
     → [X] existing positioning topics touched ([Y] with stances, [Z] empty)
     → [W] new topic suggestions
   Say 'next' to process next cluster.
   ```

Wait for `next` between clusters.

---

## Pass 4 — Positioning doc write-back

Once all clusters cross-referenced:

1. Create a backup: `positioning-topics.md.bak-YYYY-MM-DD-HHMMSS`.
2. For each proposed new topic across all clusters, append a bullet within the appropriate existing section:
   ```
   - [Proposed topic name] <!-- pipeline-suggested YYYY-MM-DD -->
   ```
3. Do not modify existing topics. Do not add stances. If a proposed topic appears across multiple clusters, append only once.

Print: `Appended [N] new topics to positioning doc. Backup saved to [path]. Say 'next' to generate cluster output files.`

---

## Pass 5 — Per-cluster output files

For each cluster, write a markdown file to the Clusters folder. Filename: lowercase, dash-separated, no special characters.

**One cluster file at a time, confirming before the next.** This is deterministic assembly from the JSON inputs.

File structure:

```markdown
# [Cluster name]

*Generated [YYYY-MM-DD] from [idea bank filename]*

---

## Summary

[2–3 sentence summary of what's in this cluster — the shape of the source material, the dominant themes, and whether positioning is well-developed or gap-heavy on this territory.]

**Entry counts:**
- External content pieces: [N]  *(watchlist, ESG, intel-competitor entries with identifiable creators other than PBC)*
- Intel-generated angles and research: [N]  *(intel-angles, intel-research)*
- Internal reference topics: [N]  *(research-* sources)*

---

## Thoughts

*Add freeform stance notes here. Dictated voice notes welcome. This section is your content material — the generate-cluster-ideas command will treat it as a first-class idea source.*

---

## Source material

*The swipe file for this theme. When producing content, browse here for framings, claims, and jumping-off points. Each item includes the creator, a URL where one exists, and a synopsis.*

### External content pieces

#### [Entry title]
**Creator:** [creator]
**Source:** [source_detail]
**URL:** [url or "no URL"]
**Synopsis:** [synopsis]
**PBC angle (pre-set):** [existing_angle_note — only if pre_angled is true]

---

### Content Intel — angles, research briefs, competitor signal

#### [Entry title]
**Source:** [source_detail]
**URL:** [url or "no URL"]
**Synopsis:** [synopsis]
**PBC angle (pre-set):** [existing_angle_note — only if pre_angled is true]

---

### Internal reference library

#### [Entry title]
**Source:** [source_detail]
**Synopsis:** [synopsis]
**Angle:** [existing_angle_note]

---

## Positioning gaps exposed

- [ ] [Topic name] (existing — section: [section name])
- [ ] [Proposed topic name] (new — section: [section name])

---
```

**Section assignment rules for Source material:**

- `External content pieces`: entries where source is watchlist-youtube, watchlist-email, or swipe-esg. Also intel-competitor entries where the creator is a named brand/platform/person (HYROX365, Menopause Movement, MacroFactor, named influencer categories).
- `Content Intel — angles, research briefs, competitor signal`: entries where source is intel-angles or intel-research, plus intel-competitor entries with creator "Competitor landscape" (aggregate category observations rather than named specific things).
- `Internal reference library`: entries where source starts with "research-" (research-glp1, research-technique, research-progression, research-muscle).

Within each subsection, do not sub-group further — just list entries in the order they appear in `_entries.json`.

Print: `Wrote [cluster-filename]. Say 'next' for next cluster.`

After the last cluster file:
```
All cluster files written to [output folder].
```

---

## Final summary

Print a compact summary:

```
Idea bank processed: [path]
Entries extracted: [N]
Clusters built: [N]
Positioning topics touched: [N] (existing: [X], new suggestions: [Y])
Positioning doc backup: [path]
Output files: [N] cluster markdown files in [path]

Each cluster file is a swipe library for its theme. Open the relevant file when you want to produce content on that territory.

Optional next step: run /generate-cluster-ideas against a cluster file to pre-generate content ideas. Only needed when you want ideas produced in advance rather than generating them in the moment from the source material.
```

---

## Error handling and resume behaviour

- If `_entries.json` already exists at the start of Pass 1a, ask whether to start fresh (delete and rebuild) or resume (skip source types already represented).
- If `_clusters.json` already exists at the start of Pass 2, ask whether to overwrite or skip to Pass 3.
- If the Clusters folder doesn't exist, create it.
- If any path doesn't exist at runtime, print the path and ask for correction.

## What not to do

- Do not use the Task tool or any sub-agent.
- Do not run multiple extraction passes in a single response.
- Do not re-read the idea bank more than once per pass.
- Do not skip the URL field — it's the main improvement in this version. Leave empty only where the idea bank genuinely has no URL for that entry.
- Do not generate content ideas in this command. That's what /generate-cluster-ideas is for.
