---
description: End-of-day wrap-up. Finds today's Claude Code sessions, lists changed skills and commands and vault files, writes a summary doc to the skills repo, and pushes both repos to GitHub. Run at the end of each working day.
---

# Evening Summary

Generate today's end-of-day summary and push everything to GitHub.

## Steps

### 1. Identify the current user

```powershell
$env:USERNAME
```

This is the `[username]` used in the summary filename.

### 2. Find today's Claude Code sessions

Run this Python script to extract unique sessions from today:

```python
import json, datetime
from pathlib import Path

history = Path.home() / '.claude' / 'history.jsonl'
today = datetime.date.today()
seen = {}

with open(history) as f:
    for line in f:
        try:
            e = json.loads(line)
            ts = datetime.datetime.fromtimestamp(e['timestamp'] / 1000)
            if ts.date() == today:
                sid = e.get('sessionId', '')
                if sid and sid not in seen:
                    seen[sid] = e.get('display', '(no description)')
        except:
            pass

for sid, desc in seen.items():
    print(f"{sid}|||{desc[:80]}")
```

Each line is `session-id|||first message`. Format for the summary as:

```
- `[session-id]` — [description]
  Resume: claude --resume [session-id]
```

If no sessions: note "No sessions recorded today."

### 2b. Apply the exclusion filter

If `$HOME\.claude\summary-exclusions.md` exists, read it and apply it before writing anything:

- Drop any session whose ID is listed there.
- For each remaining session, check ALL of its prompts from today in `history.jsonl` (not just the first) against the listed patterns; drop any session with a match.
- Drop any changed-file paths (steps 3 and 4) that match a listed pattern.

Exclusions are SILENT: the summary must read as complete, with no omission notes, placeholders, or references to this filter or the exclusions file. If the file doesn't exist, skip this step.

### 3. Find changed skills and commands

```bash
git -C "$HOME/.claude/skills" status --short
git -C "$HOME/.claude/commands" status --short
```

List any new (`??`) or modified (`M`) files. Group into Skills and Commands sections.
If both clean: "No changes today."

### 4. Find changed vault files

```python
import os, datetime
from pathlib import Path

vault = Path.home() / 'Documents' / 'Home Vault'
if not vault.exists():
    print("VAULT_NOT_FOUND")
else:
    today = datetime.date.today()
    changed = []
    for f in vault.rglob('*'):
        if f.is_file():
            mtime = datetime.datetime.fromtimestamp(f.stat().st_mtime).date()
            if mtime == today:
                changed.append(str(f.relative_to(vault)))
    for c in sorted(changed):
        print(c)
```

If `VAULT_NOT_FOUND`: skip this section entirely.
If nothing changed: "No vault files modified today."
Otherwise list the files, grouped by top-level folder.

### 5. Pull open to-dos

```python
from pathlib import Path

tasks = Path.home() / 'Documents' / 'Home Vault' / '2 - Business' / 'Operations' / 'tasks.md'
if tasks.exists():
    lines = tasks.read_text(encoding='utf-8').splitlines()
    open_tasks = [l.strip() for l in lines if l.strip().startswith('- [ ]')]
    for t in open_tasks[:20]:
        print(t)
```

Include up to 20 open tasks under an "Open To-Dos" section. Skip this section if the file doesn't exist.

### 6. Write the summary document

Path: `[skills repo root]/_summaries/YYYY-MM-DD-[username].md`

Resolve the skills root:
```bash
git -C "$HOME/.claude/skills" rev-parse --show-toplevel
```

Content:

```markdown
# Evening Summary — YYYY-MM-DD — [username]

## Sessions Today
- `[session-id]` — [description]
  Resume: `claude --resume [session-id]`

(repeat for each session)

## Skills & Commands Changed
### Skills
- [file list, or "No changes"]

### Commands
- [file list, or "No changes"]

## Vault Changes
- [file list grouped by folder, or "No changes", or section omitted if no vault]

## Open To-Dos
- [ ] [task]
(section omitted if no tasks file)
```

If a summary for this user already exists for today, overwrite it.

### 7. Push both repos

```bash
cd "$HOME/.claude/skills" && git add . && git diff --cached --quiet || git commit -m "sync: $(date +%Y-%m-%d) evening summary" && git push
cd "$HOME/.claude/commands" && git add . && git diff --cached --quiet || git commit -m "sync: $(date +%Y-%m-%d) commands" && git push
```

### 8. Report

```
Evening summary — YYYY-MM-DD
User: [username]
Sessions: N recorded
Skills: [pushed N changes / nothing to commit]
Commands: [pushed N changes / nothing to commit]
Summary written: _summaries/YYYY-MM-DD-[username].md
```
