---
description: Morning sync. Pulls the latest skills and commands from GitHub, then surfaces yesterday's evening summary from your collaborator in chat. Run at the start of each working day before anything else.
---

# Morning Summary

Pull the latest skills and commands, then show what your collaborator did yesterday.

## Steps

### 1. Pull both repos

```bash
git -C "$HOME/.claude/skills" pull
git -C "$HOME/.claude/commands" pull
```

Capture the output. If "Already up to date." — note it. Otherwise note what changed.

### 2. Find yesterday's summary from your collaborator

```python
import os, datetime
from pathlib import Path

yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
me = os.environ.get('USERNAME', os.environ.get('USER', ''))
summaries = Path.home() / '.claude' / 'skills' / '_summaries'

found = []
if summaries.exists():
    for f in summaries.glob(f'{yesterday}-*.md'):
        if me.lower() not in f.stem.lower():
            found.append(f)

for f in found:
    print(f.read_text(encoding='utf-8'))
```

If files found: display the full content of each in chat under a header like `## From [username] — yesterday`.

If nothing found: "No evening summary from your collaborator for [yesterday's date]. They may not have run /evening-summary yet."

### 3. Report what changed in skills and commands

```bash
git -C "$HOME/.claude/skills" log --since="24 hours ago" --oneline --name-only
git -C "$HOME/.claude/commands" log --since="24 hours ago" --oneline --name-only
```

List any new or modified files pulled in. If nothing: "No skill or command changes since yesterday."

### 4. Report

```
Morning summary — YYYY-MM-DD
Skills: [X new commits pulled / already up to date]
Commands: [X new commits pulled / already up to date]
Collaborator summary: [found — [username] | not found]
Changed skills: [list or "none"]
Changed commands: [list or "none"]
```

Keep the report tight. The collaborator summary content is displayed above the report block, not inside it.
