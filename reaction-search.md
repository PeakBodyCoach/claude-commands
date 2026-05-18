---
description: Find YouTube Shorts reaction targets and pull their transcripts to Obsidian
---

# Reaction Search

Find YouTube Shorts reaction video targets and pull their transcripts. Output goes to a date-stamped markdown file in the Obsidian vault Research folder.

## Decide how to get the inputs

There are three modes. Check them in this order:

### Mode 1: Content sheet exists in the current conversation

If a content sheet has just been built in our conversation and has a filled "Reaction Search Queries" section with YouTube queries, use those. Show Tom the topic and the three queries you'll run, confirm, then call the script with explicit positional arguments:

```bash
python "C:\Users\Tom\.claude\scripts\reaction-search.py" --topic "<TOPIC>" "<QUERY1>" "<QUERY2>" "<QUERY3>"
```

### Mode 2: Tom points to a saved content sheet

If Tom references a content sheet by name or path (e.g. "use the GLP-1 muscle loss sheet"), find the file in the vault and pass its path via `--from-sheet`. The script handles topic and query extraction itself:

```bash
python "C:\Users\Tom\.claude\scripts\reaction-search.py" --from-sheet "<PATH>"
```

Content sheets typically live under `C:\Users\Tom\Documents\Home Vault\2 - Business\Content\`. Use Filesystem tools to find the right file if the path isn't given. Confirm the file you found before running.

### Mode 3: No sheet in play

Ask Tom one question at a time:
1. "What's the topic?"
2. "What queries should I run?"

Then call with positional args as in Mode 1.

## Output handling

After the script runs:
1. Report the file path back to Tom
2. Mention how many videos were found and how many had transcripts
3. Walk into the pick + stage step below — don't just hand off

## Pick a target and stage it

After the candidates file is written, the next step is to pick one target and stage its metadata for `/video-script-writing` to pick up. This is a single round-trip with Tom, not a separate command.

### 1. Show the shortlist

Read the candidates file. List the videos that have transcripts (skip the ones flagged as missing — they're not usable for a script). Cap the shortlist at 5. For each, show:

```
[N] [Title] — @[creator] — [duration]s — [view count] views
    [first 12-15 words of the summary or transcript]
```

### 2. Ask Tom which one

> "Which target do you want to stage for the script? Reply with the number, or 'none' to skip staging."

If Tom replies `none`, do nothing further. The candidates file is still on disk if he wants to come back to it.

### 3. Write the staging file

If Tom picks a number, write `C:\Users\Tom\.claude\state\reaction-staging.json` with this exact shape:

```json
{
  "topic": "<original topic string from the search>",
  "topic_slug": "<topic slugged: lowercase, spaces → hyphens, no punctuation>",
  "saved_at": "<ISO 8601 timestamp, e.g. 2026-05-17T14:30:00>",
  "target": {
    "title": "<video title>",
    "url": "<full youtube url>",
    "creator": "<@handle>",
    "duration_seconds": <int>,
    "view_count": <int>,
    "transcript": "<full transcript text from the candidates file>",
    "summary": "<one-line summary of the claim Tom will react to — write this fresh from the transcript>"
  }
}
```

Create the `state/` folder if it doesn't exist:

```powershell
New-Item -ItemType Directory -Force -Path "C:\Users\Tom\.claude\state" | Out-Null
```

Overwrite any existing `reaction-staging.json` without prompting — it's transient cross-session state, not a record. The `/video-script-writing` skill is responsible for deleting it after use.

### 4. Confirm and hand off

Report:

> "Staged `[creator]` — `[title]`. Run `/video-script-writing [topic-slug]` next, or just say 'write the reaction script' and I'll pick it up automatically."

## Error handling

Map common script errors:

- **"YOUTUBE_API_KEY not set"** → point Tom to `setup.md` in the reaction-search folder
- **"quotaExceeded"** → daily 10k unit cap hit (~30 runs of 3 queries). Tell him to retry tomorrow.
- **"No 'Reaction Search Queries' section..."** → the sheet doesn't have the section filled in, or the heading is malformed. Offer to ask for queries directly instead.
- **"marked N/A"** → Tom flagged the topic as non-video in the sheet. Ask if he wants to override.
- **ImportError / missing dependency** → `pip install google-api-python-client youtube-transcript-api`

## Notes on what the script does

- Uses YouTube Data API `videoDuration=short` (under 4 mins) then post-filters to ≤3 mins to approximate Shorts
- Sorts results within each query by view count descending so highest-impact targets surface first
- Transcripts pulled via `youtube-transcript-api` (separate endpoint, no quota cost)
- Auto-captions count — most Shorts have them, but some creators disable. Missing transcripts are flagged in the output file
