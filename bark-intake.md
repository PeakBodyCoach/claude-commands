---
description: Headless auto-intake of YES-verdict Bark leads queued by the server scanner. Drains the VPS bark queue to this PC, then for each lead prepares a vault lead note + a ready-to-send first-contact draft (no follow-up tasks, no deck staging) and pushes a "lead prepped" alert, so the moment Tom buys the lead on Bark he can paste and send. Never buys leads, never spends credits. Runs via the "PBC Bark Intake Poll" scheduled task, or on demand. Triggers: "/bark-intake", "run the bark intake", "prep the queued bark leads".
---

# bark-intake (auto-prepare queued Bark leads)

This is the **headless auto-intake** counterpart to `/bark-lead`. The server-side
`bark-scan` scanner already scored these leads **YES** against the rubric and
dumped each one's full Q&A to the VPS queue. This command prepares them so Tom
is ready to send the instant he buys the lead.

**Hard rules (read first):**
- **Never buy a lead or spend a credit.** Purchase is Tom's manual step on Bark;
  a lead's phone number is hidden until he buys. This command only prepares.
- These leads are **already YES** — do NOT re-run the filter or skip them. Trust
  the scanner's verdict.
- **No follow-up tasks, no whatsapp-deck staging** (both depend on Tom having
  bought + made contact). Delivery is: vault note + ntfy alert. That's the whole
  difference from `/bark-lead`.
- Read `bark-lead/SKILL.md` for the note format (Step 2), the first-contact draft
  rules (Step 3), and the message templates + voice. This command reuses those;
  it only changes what gets produced and where it lands.

## Step 1 — Drain the queue

Run the pull script (scp-drains the VPS queue to this PC, deletes only confirmed
copies, writes the pending batch):

```
python C:\Users\Tom\bark-inbox\pull_queue.py
```

Then read `C:\Users\Tom\bark-inbox\processing\_batch.json`. If `count` is 0,
report "No queued bark leads." and stop — this is the normal empty-run outcome.

## Step 2 — Per lead, prepare note + draft

For each item in `_batch.json.items` (each carries the full `lead` payload and a
`lane` of `pt` or `nutrition`):

1. **Duplicate guard.** If `2 - Business\Leads\<First Last>.md` already exists,
   do NOT overwrite it (Tom may have run `/bark-lead` by hand, or a prior poll
   prepped it). Skip creation, note it as "already had a note", and go straight
   to archiving (Step 3).

2. **Create the lead note.** Follow `bark-lead` Step 2: copy `_Lead Template.md`
   to `2 - Business\Leads\<First Last>.md`, fill the frontmatter
   (`lane` from the item's `lane`; `locale` = `local`/`borderline` for pt,
   `online` for nutrition; `stage: new`; `goal` from the lead's goal/why answer;
   `created` = today; **omit `next_action`** — no follow-up tasks in this mode).
   Paste the free text (`project_detail`) and the full Q&A (`custom_fields`
   question/answer pairs) into `## Enquiry`. Put the Bark link / phone under
   `## Contact` if present in the payload.

3. **Draft the first-contact message.** Follow `bark-lead` Step 3 exactly (lane
   template + `voice-foundation` + `client-messaging`). Because this is headless
   and Tom's live availability isn't known, PT-lane drafts use the **alternate
   availability close** ("how's your availability tomorrow / later today"), not
   two hard-coded time slots. Nutrition lane has no call close (async).
   Run the voice self-check (no em dashes, contractions, British spelling, soft
   open-question close, no zinger).

4. **Write the draft into the note**, under a `## Draft — First Contact` heading,
   so Tom can open it on his phone (Obsidian sync) and copy it after buying.
   Do NOT stage it to the deck.

5. **Push the alert** (bark topic), so Tom knows it's ready:

```
python C:\Users\Tom\scripts\ntfy_push.py pbc-bark-3c6addcb "Lead prepped: <name>" "<lane>, <city>, <credits>cr. Note + draft ready in the vault. Buy on Bark, then paste and send." --tags memo
```

## Step 3 — Archive the queue item

Once the note + draft are written (or on the duplicate-guard skip), archive the
pending file so it isn't reprocessed:

```
python C:\Users\Tom\bark-inbox\finish_lead.py <project_id> --name "<First Last>" --lane <lane> --note "<vault note path>"
```

If note creation genuinely failed (e.g. template missing), do NOT archive —
leave the file in `processing\` so the next poll retries, and flag it in the
report.

## Step 4 — Report

Keep it tight (this runs headless; the report lands in the task log):

```
Bark intake — <date>
Prepped: X  (names)
Skipped (already had a note): Y  (names)
Errors (left for retry): Z  (names + why)
```

Each prepped lead also fired its own "Lead prepped" push, so Tom sees them on
his phone regardless of the log.
