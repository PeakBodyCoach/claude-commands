# /repair-positioning-gaps

Lifts the `Positioning gaps exposed` section from each cluster file's backup and pastes it into the current restructured file at the correct location. Fixes the gap loss that happened when `/restructure-clusters` failed to find or apply the positioning matches JSON data.

Also standardises section ordering so Positioning gaps sits below Thoughts and above Content Ideas / Source material.

## Purpose

The `/restructure-clusters` run wrote "(none identified)" to the Positioning gaps section of every cluster file because it couldn't find or correctly apply the positioning matches JSON files. The backups created just before restructure contain the original, populated gaps lists. This command pulls that content across without regenerating anything from JSON.

## Critical execution notes

**Do not use sub-agents.** Main agent reads and writes directly.

**One cluster file per pass.** Read the current file and its backup together, do the splice, write the result. Wait for `next` between clusters.

**Back up before overwriting.** New backup suffix: `.bak-gapsrepair-YYYY-MM-DD-HHMMSS`. Don't overwrite the existing `.bak-` files — those stay as they are.

**Preserve everything else.** Only change the Positioning gaps section and the section ordering. Source material, Thoughts, Content Ideas, Summary all stay intact.

## Inputs

**Clusters folder:**
`C:\Users\Tom\Documents\Home Vault\2 - Business\Content\Research\Clusters\`

For each `.md` cluster file in the folder (ignoring `.bak-` files), find the most recent matching `.bak-` file created by the previous restructure run (filename pattern: `[clusterfile].bak-YYYY-MM-DD-HHMMSS.md` or similar — inspect the actual backup naming).

---

## Pass 1 — Preflight

For each cluster markdown file in the folder:
- Check that a backup file exists with a matching prefix.
- Check that the current file contains a `## Positioning gaps exposed` section with "(none identified)" or similar empty placeholder.
- Check that the backup file contains a `## Positioning gaps exposed` section with actual bullet content.

Print:
```
Found [N] cluster files.
  [N] with empty gaps sections and matching backups available
  [N] with populated gaps already (will be skipped)
  [N] without matching backups (will be skipped with warning)

Say 'next' to begin repair.
```

If zero files need repair, exit cleanly.

---

## Pass 2 — Repair each cluster (one at a time)

For each cluster needing repair, in alphabetical order:

### Step A: Read both files

Read the current cluster file. Read its backup.

### Step B: Extract Positioning gaps from backup

Find the `## Positioning gaps exposed` section in the backup. Capture from the heading to the next `---` horizontal rule (or next `##` heading, whichever comes first).

### Step C: Build the new cluster file

Standard structure, preserving everything except the Positioning gaps section, which gets replaced, and section ordering, which gets standardised:

```
# [Title]

[Existing generation/restructure date lines]

---

## Summary

[Existing Summary content verbatim]

---

## Thoughts

[Existing Thoughts content verbatim, even if it's just the placeholder]

---

## Positioning gaps exposed

[Content lifted from backup verbatim]

---

[IF Content Ideas section exists:]
## Content Ideas

[Existing Content Ideas content verbatim]

---

## Source material

[Existing Source material content verbatim, including all subsections]
```

### Step D: Back up and write

1. Create `[clusterfile].bak-gapsrepair-YYYY-MM-DD-HHMMSS.md` from the current file.
2. Write the new file, overwriting the current one.
3. Print:
   ```
   [N]/[total]: [cluster-filename]
   Gaps lifted from: [source backup filename]
   Section order standardised: Summary → Thoughts → Positioning gaps → [Content Ideas →] Source material
   Repair backup: [repair backup filename]
   Say 'next' to continue.
   ```

### Step E: Handle user input

- `next`: proceed
- `q`: stop cleanly, processed files stay repaired

---

## Pass 3 — Final summary

```
Repair complete.
Files repaired: [N]
Files skipped: [N] ([reasons])
Repair backups in: [Clusters folder]

Positioning gaps are now restored and section ordering is:
  Summary → Thoughts → Positioning gaps → Content Ideas (where present) → Source material
```

---

## Error handling

- If the current file doesn't contain a `## Positioning gaps exposed` section at all (unexpected), log a warning and skip.
- If the backup doesn't contain a populated gaps section, log a warning and skip.
- If multiple backups match the cluster file prefix, use the most recent `bak-2026-04-21-111053` style one (the one from the restructure run, not earlier runs).
- If a repair backup write fails, abort before modifying the current file.

## What not to do

- Do not use sub-agents.
- Do not regenerate gaps from any JSON file. This command is purely lifting existing markdown content across.
- Do not modify Summary, Thoughts, Content Ideas, or Source material sections.
- Do not delete existing backup files.
