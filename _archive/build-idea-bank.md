---
name: build-idea-bank
description: >
  Build a dated Idea Bank from recent content watchlist digests and vault research outputs. Use whenever Tom asks to build the idea bank, compile the weekly intel, consolidate the watchlist, or "build the idea bank". Takes no arguments — runs against the vault automatically. Outputs a dated Idea Bank - YYYY-MM-DD.md ready for the content-sheet skill.
---

# /build-idea-bank

Builds a new `Idea Bank - YYYY-MM-DD.md` (today's date) by consolidating recent content watchlist digests and vault research outputs. Content Intel and Specific Swipes are left as stubs for hand-curation.

## Vault paths

- Watchlist digests: `C:\Users\Tom\Documents\Home Vault\2 - Business\Content\Research\Content Watchlist\`
- Idea bank output: `C:\Users\Tom\Documents\Home Vault\2 - Business\Content\Research\`
- Research notes: `C:\Users\Tom\Documents\Home Vault\3 - Knowledge\`

## Step 1 — find the baseline date

Glob `Content\Research\Idea Bank*.md`. If any exist, note the modification date of the most recently modified one. Call this the **baseline date**. If none exist, the baseline date is 30 days ago (pull all available digests).

## Step 2 — check for an existing idea bank dated today

If `Idea Bank - YYYY-MM-DD.md` (today's date) already exists in `Content\Research\`, ask:

> An idea bank for today already exists. Overwrite it, or stop?

Stop unless Tom confirms overwrite.

## Step 3 — collect watchlist digests

Glob `Content\Research\Content Watchlist\content-watchlist-*.md`. Keep only files with a modification date newer than the baseline date. If none qualify, report "No new watchlist digests found since [baseline date]" and stop — don't build an empty bank.

Read each qualifying digest in full.

## Step 4 — extract YOUTUBE entries

From each digest, extract every channel block under the `## YOUTUBE` heading. A channel block is everything from a `### [Channel Name]` heading to the next `### ` heading (or the end of the YOUTUBE section).

Within each channel block, keep: channel name, video title, duration, URL, transcript. Discard nothing from this section — include every video entry as-is.

Collect all channel blocks. De-duplicate by video URL: if the same URL appears in two digests (because digests overlap a day), include it once only (from the earliest digest).

## Step 5 — extract EMAIL DIGEST entries

From each digest, extract every entry under the `## EMAIL` heading. A valid email entry has: sender name, subject, date, body.

Apply the same three filters used by `/content-watchlist`:

1. **Promo sender skip** — read `C:\Users\Tom\.claude\skills\content-watchlist\content-watchlist-config.yaml`. Build a lookup of sender address → signal. Skip any entry whose sender address maps to `signal: promo`.

2. **Sales subject skip** — skip any entry whose subject line (case-insensitive) matches:
   `sale | % off | discount | promo code | coupon | free gift | early access | limited time | last chance | flash | use code | shop now | only \d+ left | exclusive offer | member price | bundle | lifetime deal | expires | hurry | black friday | cyber monday | don't miss | final hours`

3. **Already-seen skip** — read `C:\Users\Tom\.claude\state\content-watchlist-seen.json` if it exists. Skip any entry whose Gmail message ID is already in the `seen_ids` list.

Note: if a digest was already compiled into a previous idea bank, those email entries will largely be filtered by rule 3. This is the expected behaviour.

Keep each passing entry in full (sender name, subject, date, body).

## Step 6 — collect Research entries

Glob `C:\Users\Tom\Documents\Home Vault\3 - Knowledge\**\*.md` for files modified since the baseline date. Keep only files whose frontmatter contains `tier/overview`, `tier/evidence`, or `tier/research-complete` in the `tags` field.

For each matching file, read: filename, `created` frontmatter field (or modification date if absent), and the first 3–5 non-empty lines of body content (excluding frontmatter) as a synopsis.

If none qualify, the Research section gets a placeholder stub.

## Step 7 — build the idea bank file

Write to `Content\Research\Idea Bank - YYYY-MM-DD.md` (today's date in ISO format):

```markdown
# Idea Bank — YYYY-MM-DD

---

## YOUTUBE

[All channel blocks extracted in Step 4, formatted exactly as they appear in the digests.]

---

## Email Digest

[All qualifying email entries from Step 5, formatted as:]

### [Sender Name]
**Subject:** [subject]
**Date:** [date]
**Body:**
[body text]

---

---

# 🗂️ CONTENT INTEL

## Angles Swipe File

*Hand-fill: reactive angles, contrarian takes, trend responses. See previous idea banks for format.*

---

## Research Brief

*Hand-fill: body composition and training research findings from the past fortnight. Each entry: what it found, source type, why it matters, counterintuitive angle, client takeaway, source URL.*

---

## Competitor

*Hand-fill: top topics being covered right now, new frameworks and named concepts, content gaps, saturated angles to avoid. Sources: Reddit, YouTube landscape, ACSM, LeisureDB, Mintel.*

---

# Specific Swipes

*Hand-fill: carousel and format swipes from specific creators. Include URL, hook slide, slide text, key hooks and angles.*

---

# Research

*New knowledge documents built since [baseline date]. Each entry has a one-sentence synopsis.*

[For each file found in Step 6:]

## [[filename without extension]]
*Created: [date]*

[Synopsis: first 3–5 lines of body text]

**Content topics to develop:**
- *(hand-fill)*
- *(hand-fill)*
- *(hand-fill)*

---

[If no files found in Step 6:]

*No new tier-tagged research notes found since [baseline date]. Hand-fill with any knowledge documents built this week.*
```

## Step 8 — print summary

After writing the file, print:

```
Idea Bank built: Idea Bank - YYYY-MM-DD.md

Auto-consolidated:
  YouTube entries: [N videos from N digests]
  Email entries: [N included / N skipped (N promo sender, N sales subject, N already seen)]
  Research stubs: [N tier-tagged notes found]

Needs hand-curation:
  Content Intel — Angles Swipe File
  Content Intel — Research Brief
  Content Intel — Competitor
  Specific Swipes

Ready for: /content-sheet once hand sections are filled.
```

## Notes

- The command does not re-run filters on emails that appeared in the Email section of a watchlist digest. If the digest already applied `/content-watchlist` filtering, the emails in it are pre-filtered. The command applies filters again as a safety net for digests built before the filtering rules were in place.
- Content Intel and Specific Swipes are genuinely editorial. The command leaves them as stubs deliberately — do not attempt to auto-fill them.
- If Tom runs `/build-idea-bank` before running `/content-watchlist`, the digests will not yet exist. The command will report "no new digests" and stop cleanly.
- The idea bank is the input to `/build-idea-clusters`. Don't route to that skill until the hand-curation sections are filled.
