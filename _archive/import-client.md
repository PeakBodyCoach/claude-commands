---
description: RETIRED (Phase 1 migration tool — all clients already imported). Use /new-client to onboard new clients going forward.
---

# Import Client

You are doing a one-shot import of client data from Notion into a vault markdown file. This populates the file with profile, current programme, metadata, and historical session log so the cron has prior context from day one.

## Usage

- `/import-client [Client Name]` — import a single client
- `/import-client --all` — import the full roster (loop over each)

## Inputs

- **Notion Client DB**: `1c25c5e3-ca9f-8138-973b-000b010616ae`
- **Output directory**: `$VAULT_PATH/2 - Business/Clients/`

## Roster

If `--all`, loop over these. For each, find the corresponding Notion page in the Client DB.

- Andrew Rhodes
- Belinda Boakye
- Decio Melim
- Fergus Redsell
- Fraser Bernstein
- Jack Price
- James Keen
- Jonathan Boseley
- Laura Easton Harris
- Mo Hussein
- Nick Thompson
- Oscar Douglas
- Rich Radley
- Sarvesh Ramachandran
- Simon Roache

## Steps per client

### 1. Locate the Notion page

Search the Client DB by name. If multiple matches, pick the one with `Stage = Client`. If no match, skip and report.

### 2. Fetch the page

Use Notion's fetch tool to get full page content including all toggle blocks.

### 3. Build the markdown file

Output structure:

```markdown
# [Client Name]

**Status**: [Stage] | **Type**: [Personal/Online/etc] | **Cadence**: [Times field, simplified] | **Rate**: £[Per Session]/session
**Email**: [Email] | **Birthday**: [Birthday, friendly format] | **Started**: [Program Start, friendly format]

## Client Profile

### Personal Info
[bullet content from "Personal Info" toggle]

### Injuries & Health
[bullet content from "Injuries/Health Factors" toggle]

### Goals
[bullet content from "Goals" toggle]

### Training Strategy
[bullet content from "Training Strategy" toggle]

### Additional Notes
[bullet content from "Additional Notes" toggle, if any]

## Current Programme

[Content from the most recent "New Program" toggle, or any visible "Workout A / Workout B" section. If none found, omit this section.]

## Session Log

<!-- New session entries are inserted directly below this heading -->

[Each Booking Notes entry becomes a `### YYYY-MM-DD — [Workout Type]` heading with the original content beneath, lightly cleaned. See cleanup rules below.]
```

### 4. Cleanup rules for session log entries

For each entry inside the Booking Notes toggle:

- Convert toggle summary (e.g. "Workout B - April 16, 2026") to `### 2026-04-16 — Workout B`
- Demote any `## Heading` inside the entry to `#### Heading` so document hierarchy stays clean
- Strip pure boilerplate lines:
  - Standalone "Progression notes: Progress as normal" with no other content
  - "Permanent changes made to this program: None mentioned"
  - "Permanent changes made to this program: N/A"
  - "Changes to make for future programs: N/A"
  - Any line that's just `N/A` or `None mentioned`
- Keep all meaningful content: technical cues, on-the-spot changes, client feedback, notes for next session, tasks, and exercise tables

### 5. Field mapping notes

- **Cadence (Times)**: Take the Times property and reduce to a short phrase. "FIXED — 2x/week, 7am or 8am, at least 2 days apart. Mon 8am common. Days vary across Mon–Fri." → "2x/week, 7-8am, weekdays". If unclear or empty, write the raw text.
- **Birthday**: Format as `1 November` (no year, since Birthday is recurring)
- **Started**: Use the `Program Start` or `Program Start Dates` start value, formatted as `7 January 2026`
- **Type**: From the `Type` property
- **Stage**: From the `Stage` property

If any field is empty in Notion, omit that part of the metadata line. Don't write `**Email**: ` with nothing after it.

### 6. Write the file

Path: `$VAULT_PATH/2 - Business/Clients/[Client Name].md`

If the file already exists:
- Single import (`/import-client [Name]`): warn and ask before overwriting
- Bulk import (`/import-client --all`): skip existing files and report which were skipped

### 7. Report

After all imports complete, reply with:
- Clients imported (count + names)
- Clients skipped because file already existed
- Clients skipped because no Notion match
- Any clients with missing or empty profile sections (so Tom knows where context is thin)

## Edge cases

- **No Booking Notes toggle on the Notion page**: Create the file with profile + programme + an empty Session Log section
- **No "Personal Info" / "Goals" toggles**: Omit those subsections from Client Profile
- **Multiple "New Program" toggles**: Use only the most recent
- **Toggles with empty content**: Omit the section
- **Notion page has no `Stage = Client` flag**: Still import if name matches and the page exists
