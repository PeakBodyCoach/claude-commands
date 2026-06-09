Run the full NotebookLM → Obsidian pipeline for: $ARGUMENTS

This command is fully automated. It will:
1. Create a NotebookLM notebook and add all research sources
2. Run the full query set against the notebook
3. Generate an audio overview, slide deck, and briefing doc report inside the notebook
4. Download the briefing doc report and use it to cross-check the note synthesis
5. Synthesise the responses into a structured Obsidian note
6. Write the note directly to the vault, with a CliffNotes callout pinned at the top
7. Print the same CliffNotes summary in chat covering only the counterintuitive, surprising, or interesting findings

Requires: `notebooklm-py` v0.3.3+, Playwright Chromium, authenticated via `notebooklm login`

---

## Step 1 — Collect source URLs

Check whether `/research $ARGUMENTS` has already been run in this session. If yes, extract all URLs from that output automatically.

If not, ask:

> Paste the source URLs for this topic (one per line), or run `/research $ARGUMENTS` first.

Collect all URLs into a list. These will be added as NotebookLM sources.

---

## Step 2 — Check notebooklm-py is available

Run:

```bash
python -c "import notebooklm; print(notebooklm.__version__)"
```

If this fails, stop and tell the user:

> notebooklm-py is not installed or not found. Run: `pip install notebooklm-py` then authenticate with `notebooklm login`

---

## Step 3 — Create notebook and add sources

First check for a saved state file from a previous run. Build the topic slug from $ARGUMENTS (lowercase, spaces to hyphens). Then write and run this check:

```python
import json, os, sys

topic_slug = "$ARGUMENTS".lower().replace(" ", "-")
state_file = os.path.expanduser(f"~/.claude/nlm_state_{topic_slug}.json")

if os.path.exists(state_file):
    with open(state_file) as f:
        state = json.load(f)
    print(f"State file found: {state_file}")
    print(f"Notebook ID: {state['notebook_id']}")
    print(f"Sources previously added: {len(state.get('sources', []))}")
    with open("nlm_notebook_id.txt", "w") as f:
        f.write(state['notebook_id'])
    print("Skipping setup — proceeding directly to queries.")
    sys.exit(0)

print("No state file found — creating notebook.")
```

If the state file exists, skip to Step 4. Otherwise continue with notebook creation.

Write this to `nlm_setup.py` and execute it:

```python
import asyncio
import json
import os
import re
import tempfile
import urllib.request
from notebooklm.client import NotebookLMClient

raw_urls = [
    # REPLACE WITH ACTUAL URLs FROM STEP 1 — one string per line
]

pubmed_re = re.compile(r'https?://pubmed\.ncbi\.nlm\.nih\.gov/(\d+)/?')

def fetch_pubmed_abstracts(urls):
    sources = []
    temp_files = []
    for url in urls:
        m = pubmed_re.match(url.strip())
        if m:
            pmid = m.group(1)
            fetch_url = (
                f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
                f"?db=pubmed&id={pmid}&rettype=abstract&retmode=text"
            )
            try:
                with urllib.request.urlopen(fetch_url, timeout=15) as resp:
                    abstract_text = resp.read().decode("utf-8")
                tmp = os.path.join(tempfile.gettempdir(), f"pubmed_{pmid}.txt")
                with open(tmp, "w", encoding="utf-8") as f:
                    f.write(abstract_text)
                sources.append(tmp)
                temp_files.append(tmp)
                print(f"  PMID {pmid}: abstract fetched -> {tmp}")
            except Exception as e:
                print(f"  PMID {pmid}: fetch failed ({e}), using URL")
                sources.append(url)
        else:
            sources.append(url)
    return sources, temp_files


async def main():
    async with await NotebookLMClient.from_storage() as nlm:
        notebook_title = "$ARGUMENTS Research"
        print(f"Creating notebook: {notebook_title}")
        notebook = await nlm.notebooks.create(notebook_title)
        notebook_id = notebook.id
        print(f"Notebook created — ID: {notebook_id}")

        sources, temp_files = fetch_pubmed_abstracts(raw_urls)

        print(f"Adding {len(sources)} sources...")
        for source in sources:
            try:
                if os.path.isfile(source):
                    await nlm.sources.add_file(notebook_id, source)
                    print(f"  + file: {os.path.basename(source)}")
                else:
                    await nlm.sources.add_url(notebook_id, source)
                    print(f"  + url: {source[:80]}")
            except Exception as e:
                print(f"  ! failed: {source[:60]} — {e}")

        print("Waiting 90 seconds for source ingestion...")
        await asyncio.sleep(90)

        for tmp in temp_files:
            try:
                os.remove(tmp)
            except OSError:
                pass

        topic_slug = "$ARGUMENTS".lower().replace(" ", "-")
        state_file = os.path.expanduser(f"~/.claude/nlm_state_{topic_slug}.json")
        os.makedirs(os.path.dirname(state_file), exist_ok=True)
        with open(state_file, "w") as f:
            json.dump({"notebook_id": notebook_id, "sources": raw_urls}, f, indent=2)
        print(f"State saved to {state_file}")

        with open("nlm_notebook_id.txt", "w") as f:
            f.write(notebook_id)

        print("Setup complete.")


asyncio.run(main())
```

Replace the `raw_urls` list with the actual source URLs before running.

---

## Step 4 — Run the query set

Write this to `nlm_query.py` and execute it:

```python
import asyncio
import json
from notebooklm.client import NotebookLMClient

CHECKPOINT_FILE = "nlm_responses.json"

queries = [
    # --- Knowledge queries (Obsidian note) ---
    "Give me a comprehensive overview of $ARGUMENTS — what it is, why it matters, and what the key claims are.",
    "What are the proposed mechanisms? How is it supposed to work physiologically?",
    "What does the strongest evidence actually show? Summarise the highest-quality studies and their findings.",
    "What is the current scientific consensus, and where does genuine uncertainty remain?",
    "What are the main limitations of the existing research — study design, population size, duration, funding?",
    "Are there any studies or findings that contradict the mainstream view on $ARGUMENTS? What do they show?",
    "What do we still not know? What are the open questions that need more research?",
    "What protocols, doses, or approaches have the best evidence behind them? Be specific with numbers where available.",
    "Who benefits most — are there specific populations, phenotypes, or contexts where this works better or worse?",
    "What are the most common mistakes, misconceptions, or overhyped claims about $ARGUMENTS?",
    "What concepts, mechanisms, or topics are most closely related to $ARGUMENTS?",
    "Who are the key researchers or practitioners in this area — and do they broadly agree or disagree?",
    "How does $ARGUMENTS interact with nutrition, training, sleep, or other lifestyle factors?",
    "Practical takeaway for a busy, evidence-literate person — what should they actually do or believe about $ARGUMENTS?",
    "What is the strongest counterargument against the mainstream position on $ARGUMENTS?",

    # --- Content strategy queries (content brief) ---
    "What specific myths or false claims about $ARGUMENTS appear in these sources — and who exactly is promoting each one? Name the creators, brands, or camps responsible.",
    "What is the single most surprising, counter-intuitive, or little-known finding about $ARGUMENTS from these sources? Give me the specific stat, number, or result if there is one.",
    "What does the audience clearly believe or want to believe about $ARGUMENTS that the evidence doesn't support? What emotional need does that belief serve?",
    "What are the sharpest one-liner claims or quotable moments across these sources — things that would stop someone mid-scroll if said plainly and directly?",
    "What would be the most contrarian but defensible position someone with 12 years of evidence-based coaching experience could take on $ARGUMENTS — one that goes against the current mainstream narrative in the fitness and nutrition space?",
]

try:
    with open(CHECKPOINT_FILE, encoding="utf-8") as f:
        responses = json.load(f)
    print(f"Resuming — {len(responses)} queries already completed.")
except FileNotFoundError:
    responses = {}

with open("nlm_notebook_id.txt") as f:
    notebook_id = f.read().strip()

print(f"Notebook ID: {notebook_id}")


async def run_queries():
    async with await NotebookLMClient.from_storage() as nlm:
        for i, query in enumerate(queries, 1):
            if query in responses:
                print(f"Query {i}/{len(queries)}: already done, skipping.")
                continue

            print(f"Query {i}/{len(queries)}: {query[:70]}...")
            try:
                result = await nlm.chat.ask(notebook_id, query)
                text = result.message if hasattr(result, "message") else str(result)
                responses[query] = text
                print(f"  OK ({len(text)} chars)")
            except Exception as e:
                print(f"  ERROR: {e}")
                responses[query] = f"[FAILED: {e}]"

            with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
                json.dump(responses, f, indent=2, ensure_ascii=False)

            await asyncio.sleep(4)

    print(f"\nDone. {len(responses)} responses saved to {CHECKPOINT_FILE}")


asyncio.run(run_queries())
```

Wait for all 20 queries to complete before proceeding.

---

## Step 5 — Generate audio overview, slide deck, and briefing doc report

Write this to `nlm_generate.py` and execute it with `python3 -u` (unbuffered output). The script checks for existing in-progress or completed artifacts before submitting new ones, and saves task IDs to `nlm_artifacts.json` immediately after each submission. If polling times out or fails, re-running the script resumes from `nlm_artifacts.json` without submitting duplicates.

```python
import asyncio
import json
import os
from pathlib import Path
from notebooklm.client import NotebookLMClient
from notebooklm import AudioFormat, AudioLength, SlideDeckFormat, SlideDeckLength
from notebooklm.rpc.types import ReportFormat

ARTIFACT_STATE = "nlm_artifacts.json"
ARTIFACT_TYPE_AUDIO = 1
ARTIFACT_TYPE_REPORT = 2
ARTIFACT_TYPE_SLIDES = 8

with open("nlm_notebook_id.txt") as f:
    notebook_id = f.read().strip()

print(f"Notebook ID: {notebook_id}", flush=True)

AUDIO_INSTRUCTIONS = """
You are presenting this research to an experienced personal trainer and evidence-based strength coach with over a decade of client experience. Frame the conversation for someone who needs to understand the evidence well enough to apply it in real sessions and explain it plainly to clients.

Focus on:
- The most counterintuitive or surprising findings from the sources — lead with what challenges conventional wisdom, not what confirms it
- Specific numbers, effect sizes, and study names where available
- The distinction between what the evidence actually shows versus what is commonly believed or coached
- Practical application: what does this mean for how a coach should programme or advise clients?
- Where genuine uncertainty remains — do not overstate the evidence

Avoid generic recaps of well-known principles. Assume the listener already knows the basics. Prioritise the nuance and the edges.
"""

SLIDE_INSTRUCTIONS = """
Create a presenter slide deck for a personal trainer or strength coach. Structure it as a reference and teaching resource on $ARGUMENTS.

- Opening slide: the central finding or most important takeaway as a single bold statement
- Evidence slides: the key studies and what they actually showed — include specific numbers
- Practical slides: what this means for programme design and client coaching, with specific recommendations
- Misconceptions slide: the most common wrong beliefs and what the evidence says instead
- Closing slide: a simple decision framework or action checklist

Keep bullets short — one idea per bullet. No jargon without a brief explanation. Suitable for a coach reviewing before a client consultation or presenting to a small group.
"""

REPORT_INSTRUCTIONS = """
Focus on clinical and coaching utility. Organise the briefing document around these headings:
1. Executive summary — five key points a coach or practitioner needs to know immediately
2. Core mechanisms — how this works physiologically, with uncertainty flagged where it exists
3. Evidence quality — grade the available literature (RCTs, observational, mechanistic, consensus)
4. Practical application — specific protocols, doses, and populations where evidence is strongest
5. Common mistakes and misconceptions — what is overstated or misunderstood in practice
6. Monitoring and reassessment — what to track and over what timeframe
7. Red flags and contraindications — when to refer or change approach
8. Evidence gaps — what is genuinely unknown and should not be assumed

Cite sources directly. Do not fabricate references. Use specific numbers and study names where available.
"""


async def main():
    async with await NotebookLMClient.from_storage() as nlm:

        # Load previously saved task IDs if resuming after a timeout
        if os.path.exists(ARTIFACT_STATE):
            with open(ARTIFACT_STATE) as f:
                task_ids = json.load(f)
            print(f"Resuming — loaded task IDs from {ARTIFACT_STATE}", flush=True)
        else:
            task_ids = {}

        # Scan existing notebook artifacts — pick the most recent non-failed one per type
        # to avoid submitting duplicates if the script is re-run
        print("Scanning existing artifacts...", flush=True)
        existing = await nlm.artifacts.list(notebook_id)
        type_map = {
            ARTIFACT_TYPE_AUDIO: "audio",
            ARTIFACT_TYPE_REPORT: "report",
            ARTIFACT_TYPE_SLIDES: "slides",
        }
        for art in sorted(existing, key=lambda a: a.created_at, reverse=True):
            atype = getattr(art, "_artifact_type", None)
            name = type_map.get(atype)
            if name and name not in task_ids and art.status in (1, 2, 3):
                task_ids[name] = art.id
                print(f"  Found existing {name}: {art.id} (status={art.status})", flush=True)

        # Submit only the types that are not already tracked
        for name in ["audio", "slides", "report"]:
            if name in task_ids:
                print(f"  Skipping {name} — already tracked: {task_ids[name]}", flush=True)
                continue
            print(f"Submitting {name}...", flush=True)
            if name == "audio":
                result = await nlm.artifacts.generate_audio(
                    notebook_id,
                    instructions=AUDIO_INSTRUCTIONS,
                    audio_format=AudioFormat.DEEP_DIVE,
                    audio_length=AudioLength.LONG,
                )
            elif name == "slides":
                result = await nlm.artifacts.generate_slide_deck(
                    notebook_id,
                    instructions=SLIDE_INSTRUCTIONS,
                    slide_format=SlideDeckFormat.PRESENTER_SLIDES,
                    slide_length=SlideDeckLength.DEFAULT,
                )
            elif name == "report":
                result = await nlm.artifacts.generate_report(
                    notebook_id,
                    report_format=ReportFormat.BRIEFING_DOC,
                    extra_instructions=REPORT_INSTRUCTIONS,
                )
            task_ids[name] = result.task_id
            print(f"  {name} task ID: {result.task_id}", flush=True)
            # Save immediately so a re-run won't re-submit this type
            with open(ARTIFACT_STATE, "w") as f:
                json.dump(task_ids, f, indent=2)

        # Poll until all three are ready (up to 15 minutes)
        todo = {k: v for k, v in task_ids.items() if v}
        done = {}
        print("Polling...", flush=True)
        for i in range(45):
            await asyncio.sleep(20)
            for name, task_id in list(todo.items()):
                art = await nlm.artifacts.get(notebook_id, task_id)
                print(f"  [{(i+1)*20}s] {name}={art.status} '{art.title}'", flush=True)
                if art.status == 3:
                    done[name] = task_id
                    del todo[name]
                    print(f"    ^ ready", flush=True)
                elif art.status == 4:
                    done[name] = None
                    del todo[name]
                    print(f"    ^ FAILED", flush=True)
            if not todo:
                break
        else:
            print(f"Timed out — still pending: {list(todo.keys())}", flush=True)
            print("Re-run this script to resume polling without re-submitting.", flush=True)

        # Download report to temp file for note enrichment — deleted in cleanup
        if done.get("report"):
            print("\nDownloading report as markdown...", flush=True)
            out = await nlm.artifacts.download_report(
                notebook_id,
                output_path="nlm_report.md",
                artifact_id=done["report"],
            )
            text = Path(out).read_text(encoding="utf-8")
            print(f"  Saved {len(text)} chars to {out}", flush=True)

        print("\nFinal artifact IDs:", flush=True)
        for name, task_id in done.items():
            if task_id:
                art = await nlm.artifacts.get(notebook_id, task_id)
                print(f"  {name}: {task_id}  title: {art.title}", flush=True)
        print("Done.", flush=True)


asyncio.run(main())
```

Run with:

```bash
cd "$HOME" && python3 -u nlm_generate.py 2>&1
```

If the script times out during polling, re-run the same command — it loads `nlm_artifacts.json`, skips all submissions, and resumes polling.

Report the artifact IDs and titles to the user on completion.

---

## Step 6 — Synthesise the Obsidian note

Read both `nlm_responses.json` and `nlm_report.md` as **co-equal primary sources**. The vault note must incorporate the full detail from both. Do not treat the report as a gap-filler — it is often the richer document and frequently contains structured tables, specific effect sizes, named studies, population-specific sub-analyses, and failure-point mechanics that the query responses do not surface in the same detail.

**How to use the two sources together:**
- Read the full report first. Note every specific number, table row, named study, population sub-group, and failure-point it contains.
- Then read all 20 query responses. Note what they add that the report does not cover (typically nuance, counterarguments, practitioner framing).
- Write the vault note using both. Every specific number, effect size, named trial, and structured table from the report must appear in the vault note. Every counterintuitive finding, caveat, or practical framing from the queries must appear too.
- The vault note should be at least as detailed as the report, and more so where the queries add depth.

Before writing, internally identify from both sources:

- The 3–5 most important factual claims
- The strongest evidence cited (study names, authors, effect sizes)
- Any contradictions or tensions between responses
- All related concepts, mechanisms, and named researchers mentioned
- Practical protocols or specific numbers
- Explicit caveats, limitations, and open questions
- Any assessment tools, monitoring approaches, or red flags the report names that the queries omit

Then write the complete note using this exact structure:

```markdown
---
title: "[Topic name, title-cased]"
aliases: ["[alternative name if any]", "[abbreviation if any]"]
tags:
  - topic/[nutrition|training|supplementation|recovery|body-composition|health|performance|psychology]
  - evidence/[strong|moderate|weak|mixed]
  - type/[intervention|concept|condition|methodology|nutrient|compound]
  - status/reviewed
created: [today's date YYYY-MM-DD]
source: notebooklm-synthesis
notebook: "$ARGUMENTS Research"
related: ["[[Related Concept 1]]", "[[Related Concept 2]]", "[[Related Concept 3]]"]
---

# [Topic Name]

> [One-sentence bottom line. Blunt and practical.]

> [!note]- CliffNotes
> [The same 4 to 7 bullets produced for Step 8, pinned here at the top of the note. Counterintuitive, surprising, or interesting findings only. Lead with the specific number, study name, or contrast. One sentence per bullet, two max if a number needs context. No basics, no mechanism recaps. Generate the bullets once and reuse the identical set in the Step 8 chat summary.]
> - [finding]
> - [finding]

## Overview

[2–3 paragraphs. What it is, why it matters, what the key claims are. Prose only — no bullets in this section. Pull the strongest signals from across all 20 responses.]

## Mechanism

[How it works physiologically. One bullet per mechanism. Flag uncertainty explicitly where it exists.]

- **[Mechanism name]:** [explanation]

## Evidence

[One prose paragraph on overall evidence quality, volume, and direction. Then the table:]

| Outcome | Effect | Evidence quality | Notes |
|---|---|---|---|
| [outcome] | [positive/negative/neutral/mixed] | [High/Moderate/Low] | [caveat or key study] |

[3–8 rows. Cover outcomes most discussed across the responses.]

### Key studies

- **[Author, Year]** — [finding, one sentence]

*If no specific studies were named: "Specific citations not returned by notebook — see source list."*

## Practical application

### Who benefits
[1–2 sentences on populations or contexts where this is most relevant.]

### Protocol / dose
[Specific numbers and timing from the responses. Bullets. If none given, state that explicitly.]

- [detail]

### Common mistakes
- [mistake or misconception]

## Limitations and open questions

- [limitation]
- [open question]

## Counterarguments

[1–2 paragraphs. The strongest case against the mainstream view, drawn from the responses. Represent it fairly — no strawmanning.]

## Key figures

- **[[Name]]** — [position or contribution, one sentence]

## Related concepts

[Prose paragraph linking this topic to related areas. Write every related concept as a [[wikilink]]. Pack in as many valid links as possible — this section drives vault navigation.]

## Sources

*Synthesised from the "$ARGUMENTS Research" NotebookLM notebook via the `/research` + `/notebooklm-build` pipeline.*

See: [[Research Sources - $ARGUMENTS]]
```

Formatting rules — apply throughout without exception:
- British spelling
- No em dashes — use colons, commas, or new sentences instead
- `[[wikilinks]]` for every concept, person, mechanism, or study that warrants its own note
- Evidence labels: **High** (meta-analysis/RCT), **Moderate** (cohort/observational), **Low** (mechanistic/anecdote only)
- Hedge accurately — do not overstate certainty from the notebook responses
- Where responses contradict each other, represent both sides rather than picking one
- Do not invent citations — only use what the notebook returned

---

## Step 7 — Write to the Obsidian vault

Determine the subfolder from the `topic/` tag:

| topic/ tag | Vault path |
|---|---|
| nutrition | `C:\Users\Tom\Documents\Home Vault\3 - Knowledge\Nutrition` |
| training | `C:\Users\Tom\Documents\Home Vault\3 - Knowledge\Training` |
| supplementation | `C:\Users\Tom\Documents\Home Vault\3 - Knowledge\Supplementation` |
| recovery | `C:\Users\Tom\Documents\Home Vault\3 - Knowledge\Recovery` |
| body-composition | `C:\Users\Tom\Documents\Home Vault\3 - Knowledge\Body Composition` |
| health | `C:\Users\Tom\Documents\Home Vault\3 - Knowledge\Health` |
| performance | `C:\Users\Tom\Documents\Home Vault\3 - Knowledge\Performance` |
| psychology | `C:\Users\Tom\Documents\Home Vault\3 - Knowledge\Psychology` |

Filename: title-case the topic, spaces to hyphens, `.md` extension. Example: `Creatine-Timing.md`

Write the note content directly using the Write tool. After writing, confirm:

```
✓ Note written to: C:\Users\Tom\Documents\Home Vault\3 - Knowledge\[Subfolder]\[Filename].md
✓ Notebook: "$ARGUMENTS Research"
✓ Sources added: [N]
✓ Queries run: 20 (15 knowledge + 5 content strategy)
✓ Audio overview: generated in notebook (artifact ID: [...])
✓ Slide deck: generated in notebook (artifact ID: [...])
✓ Briefing doc report: generated in notebook (artifact ID: [...])
```

Then list:

**Wikilinks to stub out:** Every `[[link]]` used in the note that likely needs its own file — your backlog for future notes.

---

## Step 8 — CliffNotes summary in chat

Print a short CliffNotes summary of the research directly in the chat output, under this exact heading:

```
### CliffNotes
```

This is the **same set of bullets** pinned in the `> [!note]- CliffNotes` callout at the top of the vault note (Step 6). Generate the bullets once, use the identical set in both places. Do not write a different summary for each.

Rules for the summary:
- Bullet list only, no preamble or closing line.
- 4 to 7 bullets. Stop when you run out of genuinely interesting material — do not pad.
- One bullet per finding. One sentence each, two max if a number needs context.
- **Only include things that are counterintuitive, surprising, or interesting** to an evidence-literate reader. Skip anything that would be obvious to someone who already coaches in this area.
- Lead with the specific number, study name, or contrast where one exists. Vague claims aren't interesting.
- No basics ("a deficit is needed for fat loss", "protein helps"). No mechanism recaps. No restatement of well-known principles.
- Do not include section headers, links, or formatting beyond the bullets themselves.

If nothing in the research clears the "interesting to an expert" bar, write a single bullet saying so honestly. Do not invent surprises.

---

## Step 9 — Share notebook (optional)

**Known recipients:**
- Khaela → `espiritu.pro.work@gmail.com`

If the user provided a recipient email or name (e.g. "share with Khaela"), share the notebook with them as a viewer:

```bash
python scripts/run.py nlm.py share-permission <email> --role viewer
```

Report the confirmation. If no email was provided, skip this step silently — do not prompt.

The recipient will receive a Google share invite and can open the notebook at notebooklm.google.com using their Gmail account. As a viewer they can play the audio overview, view the slide deck and briefing doc, and ask follow-up questions via the chat interface. They cannot add sources or generate new studio content.

---

## Cleanup

```bash
rm nlm_setup.py nlm_query.py nlm_generate.py nlm_notebook_id.txt nlm_responses.json nlm_report.md nlm_artifacts.json
```
