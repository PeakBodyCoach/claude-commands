# /enrich-entries

Enriches the existing `_entries.json` with fields that the original extraction pass didn't capture: creator, URL, and a longer synopsis. Runs as ten narrow passes matching the original extraction, but only adds the missing fields rather than re-extracting from scratch.

## Purpose

The first version of `/build-idea-clusters` captured title, source, source_detail, claim, pre_angled, and existing_angle_note. The updated cluster file format also needs creator, URL, and a longer synopsis per entry. This command adds those three fields to the existing entries without redoing the clustering or positioning work.

Pair with `/restructure-clusters` afterwards to rewrite the cluster files using the enriched entries.

## Critical execution notes

**Do not use sub-agents.** Main agent handles all passes directly.

**One source type per pass.** Same pattern as `/build-idea-clusters`. Print count and wait for `next`.

**Update in place, do not rewrite from scratch.** Read `_entries.json`, find the entries matching the current source type, add the three new fields to each, write back. Do not regenerate existing fields.

**Idempotent.** If a run is interrupted and restarted, entries that already have creator/URL/synopsis populated are skipped. Only missing fields are filled.

## Inputs

**Entries JSON:**
`C:\Users\Tom\Documents\Home Vault\2 - Business\Content\Research\Clusters\_entries.json`

**Idea bank path:**
`C:\Users\Tom\Documents\Home Vault\2 - Business\Content\Research\Idea Bank - 19-04-2026.md`

*(Update if processing a different dated idea bank.)*

---

## Fields to add

For every entry, add:
- `creator`: named person or brand behind the content. Rules differ per source — see below.
- `url`: direct URL to the source content if one exists in the idea bank. Empty string otherwise.
- `synopsis`: two to three sentences describing what the piece covered. The existing `claim` field stays — synopsis is richer. If the existing claim is already two to three sentences, synopsis can be the same content re-phrased slightly longer, or claim verbatim if it already serves.

Do not modify existing fields.

---

## Pass 1 — watchlist-youtube

For every entry where `source == "watchlist-youtube"`:
- `creator`: same as `source_detail` (the YouTube channel name)
- `url`: the `**URL:**` line attached to the video in the idea bank's YOUTUBE section
- `synopsis`: two to three sentences derived from the video transcript in the idea bank

Print: `Pass 1 complete. [N] watchlist-youtube entries enriched. Say 'next' to continue.`

## Pass 2 — watchlist-email

For every entry where `source == "watchlist-email"`:
- `creator`: named author if given in the idea bank (e.g. "Andy Morgan" for Ripped Body, "Kelly Starrett" for The Ready State, "Menno Henselmans" for his own emails). If only the brand, use that (e.g. "RP Strength").
- `url`: empty string (newsletters don't have stable URLs in the digest)
- `synopsis`: two to three sentences derived from the email body

Append and write back. Print count and wait.

## Pass 3 — intel-angles

For every entry where `source == "intel-angles"`:
- `creator`: "Peak Body Coach Content Intel"
- `url`: the `**Source:**` URL attached to each angle in the Content Intel Angles Swipe File
- `synopsis`: two to three sentences from the angle's Take and supporting text

Append and write back. Print count and wait.

## Pass 4 — intel-research

For every entry where `source == "intel-research"`:
- `creator`: the journal or study author where named in the idea bank entry, otherwise "Content Intel Research Brief"
- `url`: the `Source::` URL attached to each finding
- `synopsis`: two to three sentences covering the finding, source type, and why it matters

Append and write back. Print count and wait.

## Pass 5 — intel-competitor

For every entry where `source == "intel-competitor"`:
- `creator`: the brand or platform named in the item. Rules:
  - Named brands/platforms: "HYROX365", "Menopause Movement", "MacroFactor", "Equinox" (when referenced directly in the item)
  - Category observations without a single named source: "Competitor landscape"
- `url`: the `**Source:**` URL attached to each item
- `synopsis`: two to three sentences covering what the signal is and any quantitative evidence (search growth, survey figures, etc.)

Append and write back. Print count and wait.

## Pass 6 — swipe-esg

For every entry where `source == "swipe-esg"`:
- `creator`: "Emma Storey Gordon (ESG Fitness)"
- `url`: the `**URL:**` attached to each post in the Specific Swipes → ESG Fitness section (Instagram URL)
- `synopsis`: two to three sentences covering the post's core argument and format

Append and write back. Print count and wait.

## Pass 7 — research-glp1

For every entry where `source == "research-glp1"`:
- `creator`: "Peak Body Coach reference library"
- `url`: ""
- `synopsis`: the bullet text plus a sentence on why it's a usable content angle

Append and write back. Print count and wait.

## Pass 8 — research-technique

For every entry where `source == "research-technique"`:
- `creator`: "Peak Body Coach reference library"
- `url`: ""
- `synopsis`: bullet text plus a sentence on its content angle

Append and write back. Print count and wait.

## Pass 9 — research-progression

For every entry where `source == "research-progression"`:
- `creator`: "Peak Body Coach reference library"
- `url`: ""
- `synopsis`: bullet text plus angle sentence

Append and write back. Print count and wait.

## Pass 10 — research-muscle

For every entry where `source == "research-muscle"`:
- `creator`: "Peak Body Coach reference library"
- `url`: ""
- `synopsis`: bullet text plus angle sentence

Append and write back.

Print: `Pass 10 complete. All entries enriched. Say 'next' for final summary.`

---

## Final summary

Print:

```
Enrichment complete.
Entries processed: [N]
Fields added: creator, url, synopsis
Backup of original _entries.json: [path]

Next step: run /restructure-clusters to rewrite the cluster markdown files using the enriched data.
```

Before Pass 1 writes anything, create a backup: `_entries.json.bak-YYYY-MM-DD-HHMMSS` in the same folder.

---

## Error handling

- If `_entries.json` doesn't exist, print the path and exit.
- If an entry already has all three enrichment fields populated, skip it silently (idempotent).
- If an entry has some but not all of the three fields, only fill the missing ones.
- If a URL can't be found in the idea bank for an entry that should have one, log the title to the terminal and continue with empty URL.

## What not to do

- Do not use sub-agents.
- Do not regenerate existing fields.
- Do not re-run clustering or positioning cross-reference — those outputs are unaffected by this command.
- Do not touch the cluster markdown files.
