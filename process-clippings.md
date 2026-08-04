---
description: Process the vault web clippings staging file. Builds each seed captured by the vault clipper extension into a proper knowledge note in the right 3 - Knowledge folder, then clears the processed entries from the staging file. Runs weekly via the "PBC Weekly Clippings" scheduled task, or on demand ("process the clippings").
---

# Process Clippings

Turn every seed in the web clippings staging file into a real knowledge note, then clear the staging file. Seeds are captured by the vault clipper Chrome extension (bridge at `C:\Users\Tom\vault-clipper\`).

## Paths

- Staging file: `C:\Users\Tom\Documents\Home Vault\3 - Knowledge\_Web Clippings.md`
- Knowledge tree: `C:\Users\Tom\Documents\Home Vault\3 - Knowledge\`

## Steps

### 1. Read the staging file

Each seed is a `## YYYY-MM-DD - Title` section with a `- Source:` URL, an optional `- Note:` line (Tom's capture note, treat it as a steer), and the clipped text as a blockquote.

**If there are no `## ` entries, print "No clippings to process." and stop.** Do not touch anything else.

### 2. Load the voice rules

Read `~/.claude/skills/voice-foundation/SKILL.md` before writing anything. All notes follow it. Never use em dashes anywhere, use a comma or full stop.

### 3. Build one note per seed

For each seed:

1. **Pick the destination folder** by inspecting the existing `3 - Knowledge` structure and matching where neighbouring topics live. Known conventions:
   - Nutrition, supplements, and body-composition topics go in `3 - Knowledge\Nutrition\` with tag `topic/nutrition`.
   - Training, movement, and rehab topics go under `3 - Knowledge\Training\` in the matching subfolder.
   - When unsure, open two or three neighbouring notes in the candidate folder and copy their frontmatter and tag conventions.
2. **Check for an existing note on the topic first** (search the knowledge tree by keyword). If one exists, extend it with the new material and source rather than creating a duplicate.
3. **Write a substantive note**, never a bare-link stub. Minimum content:
   - What the source claims or shows, in plain English.
   - The key numbers, mechanisms, or conditions that make the claim true or limited (e.g. effect windows, doses, populations).
   - A practical takeaway line: what this means for coaching or for Tom.
   - The source as a markdown link at the bottom (`Source: [Title](url)`).
   - Frontmatter and tags matching the destination folder's conventions.
4. **Optional content flag:** if the material has obvious content potential, end the note with a one-line `**Content angle:**` suggestion. Do not write anything to the Reel Inbox; Tom curates that himself.

The clipped blockquote is raw material, not the note. Summarise and structure it; do not paste it wholesale.

### 4. Clear processed seeds

Rewrite `_Web Clippings.md` keeping the header block (title + explanatory paragraph) and removing every entry that was successfully processed. If a seed could not be processed (dead source, unclassifiable), leave its entry in place and say so in the output.

### 5. Report

Print a short summary: notes created or extended (with paths), seeds left in staging, any flags. When run headless this lands in `C:\Users\Tom\.claude\process-clippings.log`.
