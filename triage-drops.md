---
description: Transcribe and triage voice-note / text drops from the Telegram capture bot into tasks, vault seeds, content bench, reminders, or a digest.
---

# /triage-drops

Drain the voice-note capture queue and route each item to where it belongs.
Capture is thoughtless and instant (Tom holds the mic on a private Telegram
bot); this command is the deferred, automatic processing leg. Runs headless
on a schedule (hourly-ish 07:00-21:00) and on demand.

**Safety spine (do not violate):**
- **Never take a client-facing or destructive action.** No bookings, no
  cancellations, no client messages, no 1Fit edits, no calendar changes. A
  client-related drop becomes a *flag for Tom*, nothing more.
- **The one client-related write allowed** is routing a *session note* into the
  client's own `_inbox` session file (the `session-note` category below). This
  is not a client-facing action: it is Tom's own post-session capture, just
  transported off his phone, landing additively in a local vault file so
  `/process-sessions` can pick it up. It is done by a conservative helper that
  never guesses; anything it can't match cleanly falls back to a Tom flag.
- **When uncertain, downgrade to the digest.** Never guess an actionable
  destination. A wrong task or a wrong vault note is worse than an unclear-item
  ping.
- **Nothing is silently eaten.** Every item you finish MUST go through
  `finish_item.py` so it is archived with its transcript and logged.

## Step 1 - Pull and transcribe

Run:

```
python C:\Users\Tom\vn-inbox\pull_transcribe.py
```

This drains the VPS queue, transcribes voice notes locally (faster-whisper),
and writes `C:\Users\Tom\vn-inbox\processing\_batch.json`. Read that file.

- If `count` is 0, report "No drops to triage." and stop.
- Any item with `transcribe_ok: false` -> do NOT try to classify it. Add it to
  the digest ("couldn't transcribe, kept for retry") and leave it in
  `processing\` (do NOT run finish_item on it). It retries next run.

## Step 2 - Classify each item

For each ready item, read its `transcript` (and `caption` for voice). Decide a
single category. Bias toward the *least destructive* reading; if two readings
are plausible and one is actionable, prefer the safer one or the digest.

| Category | What it looks like | Destination (Step 3) |
|---|---|---|
| **task** | An action to do; admin, a fix, a purchase, "remember to…", "get Khaela to…" | `tasks.md` |
| **knowledge** | A fact, study, idea, or thing worth saving to the knowledge base | `_Web Clippings.md` seed |
| **content-idea** | A hook, angle, reaction target, or post idea | `_Reel Inbox.md` |
| **reminder** | A time-anchored nudge ("remind me Tuesday to…", "at 3pm…") | ntfy scheduled push |
| **session-note** | Tom reporting on a session he just coached, almost always opening with a client's first name then observations: "clean", pains/flags, loads, form, next-time cues, RPE, mood | route into that client's `_inbox` session file (Step 3) |
| **client** | Anything else about a specific PT client that is NOT a post-session report (their weight, a message to send, a programme question) | flag in `tasks.md` for Tom, DO NOT ACT |
| **unclear** | Ambiguous, half a thought, can't tell what it wants | digest only |

**session-note vs client vs task.** A `session-note` is Tom's own capture *about
a session that just happened* — his post-session dictation, transported. It
almost always opens by addressing a client by name ("Fraser, clean, wrist fine,
step-ups to 20kg"). An instruction to *do* something about a client ("remind Rich
his invoice is due", "book Simon Tuesday", "message Andrew his plan") is a `task`
or `client` flag, never a session note. If it is not clearly a post-session
report, do not classify it as `session-note` — the router will only write into a
pristine session file anyway, and a wrong reading falls back to a Tom flag.

Convert relative dates in the transcript to absolute using today's date.

## Step 3 - Route

Use today's date as `YYYY-MM-DD` throughout. After writing the destination,
archive the item (Step 4).

**task** - Append one line to
`C:\Users\Tom\Documents\Home Vault\2 - Business\Operations\tasks.md` under the
`## Projects` section (or the matching `## [Client]` section only if it is
genuinely admin about that client and still non-actioning). Format:
```
- [ ] <the task, cleaned up> (raised: YYYY-MM-DD) #task
```
Default unassigned. Add `#person/tom` ONLY if it needs Tom himself (his
judgement, voice, presence, recall, or a strategic call). Otherwise leave it
unassigned/Khaela's pool. (memory: tasks default to Khaela, never Tom.)

**knowledge** - Append a seed to
`C:\Users\Tom\Documents\Home Vault\3 - Knowledge\_Web Clippings.md` in the exact
seed format the weekly `process-clippings` run expects (do NOT build the note
now, just bench the seed):
```
## YYYY-MM-DD - <short title you generate>
- Note: <the transcript, lightly cleaned>

> <the transcript as a blockquote>
```
No `Source` line (there's no URL). process-clippings will build it properly.

**content-idea** - Append a row to
`C:\Users\Tom\Documents\Home Vault\2 - Business\Content\Content Ideas\_Reel Inbox.md`,
matching the existing table columns `| Saved | Clip | Angle / why | Source |`:
```
| YYYY-MM-DD | <short idea label> | <the angle / why, from the transcript> | (voice note) |
```
Never draft content from a voice note; benching only. (memory: content ideas
get benched, never drafted from a voice note.)

**reminder** - Fire a scheduled ntfy push to Tom's personal topic
`pbc-daily-2cc88344`. If you can extract a clear delivery time, schedule it;
otherwise deliver at the next morning window (`tomorrow, 7am`). Run:
```
python -c "import sys; sys.path.insert(0, r'C:\Users\Tom\scripts'); import ntfy_push; ntfy_push.push('pbc-daily-2cc88344', 'Reminder', 'MESSAGE_HERE', priority=3, tags=['alarm_clock'], delay='DELAY_HERE')"
```
`delay` accepts a unix-timestamp string or natural forms like `30m`,
`tomorrow, 3pm`. Free-tier window is 10s to 3 days; if the reminder is further
out than 3 days, make it a `#person/tom` task in `tasks.md` instead and note the
date. (memory: never spend paid quota; ntfy free tier only.)

**client** - Do NOT act. Append a flag to `tasks.md` under the client's section
(or `## Projects` if unsure which client), format:
```
- [ ] [voice-note drop] <verbatim gist> - review, do not auto-action #person/tom (raised: YYYY-MM-DD) #task
```

**session-note** - This is Tom's own session capture, just transported, so it is
allowed to land in his `_inbox` session file (the one client-related write the
safety spine permits — additive, local, satisfies the `/process-sessions`
capture gate, never a client-facing action). Hand the transcript to the router,
which matches conservatively and never guesses. Pass `--backfill` so a
successful write also pulls the corresponding workout from 1Fit into the file:
```
python C:\Users\Tom\vn-inbox\route_session_note.py --backfill --transcript "<the transcript, verbatim>"
```
Pass the transcript verbatim (transcription cleanup only) — the router strips the
leading client name and converts voice-typed em dashes itself. Never summarise or
embellish Tom's session notes. It prints one JSON line; act on `status`:

- **`written` / `already_written`** - the note landed in `<file>` (`mode` is
  `voice_notes` for substantive notes or `quick_capture` for a bare "clean").
  With `--backfill`, a `backfill` object also reports the 1Fit pull:
  `ok:true` means the `## 1Fit Log` was written (or was already present);
  `ok:false` is non-fatal — the note still stands and the 9pm backfill is the
  backstop, so just note it in the report. Archive as category `session-note`,
  destination the filename.
- **`occupied`** - a client matched but that session file already holds Tom's
  capture (he is writing it up himself, or it is a second note for the same
  session). Do NOT write over it. Fall back: append a `client` flag to `tasks.md`
  (per the **client** route above) so nothing is lost, and archive as
  `session-note` -> `tasks.md (occupied)`.
- **`ambiguous`** - the name matched two clients, or the same client twice on the
  target day. Do NOT guess. Fall back to a `client` flag in `tasks.md`; archive
  as `session-note` -> `tasks.md (ambiguous)`.
- **`no_match`** - no session file matched (no booking that day, wrong day, or an
  unfamiliar name). Fall back to a `client` flag in `tasks.md`; archive as
  `session-note` -> `tasks.md (no_match)`.

The router only ever writes into a *pristine* session file (empty Quick capture
and empty Voice Notes); if Tom has already started that file by hand it returns
`occupied` and defers to him. One consequence: a second voice note for the same
session lands as an `occupied` flag rather than a second append — that is the
deliberate safe default, not a bug.

**unclear** - Add to the digest list. No destination write.

## Step 4 - Archive every finished item

Immediately after handling an item, archive it:
```
python C:\Users\Tom\vn-inbox\finish_item.py <message_id> <category> <destination> "<one-line summary>"
```
- Archive **every item you handled**, including `unclear` ones (use category
  `unclear`, destination `digest`) - they were seen and digested, so they are
  done.
- The ONLY items you must NOT archive are `transcribe_ok:false` ones: leave
  them in `processing\` so the next run retries transcription.

## Step 5 - Digest push

If any items were `unclear` or `transcribe_ok:false`, push one digest to
`pbc-daily-2cc88344`:
```
python C:\Users\Tom\scripts\ntfy_push.py pbc-daily-2cc88344 "Voice-note digest" "MESSAGE" --priority low --tags speech_balloon
```
List each unclear item's gist and each failed transcription on its own line.

## Step 6 - Report

Print a compact summary in chat: one line per item (`message_id -> category ->
destination`), then the digest contents if any. This is the run's audit trail.
