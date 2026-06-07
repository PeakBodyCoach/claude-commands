Enrich an existing NotebookLM notebook with new sources from the updated research sweep, regenerate assets, and enrich the corresponding Obsidian vault note.

Usage: `/enrich-notebook <topic>`

`<topic>` can be a topic slug (matching the state file name) or a plain-English topic name. Claude resolves it to the correct slug.

---

## Step 1 — Load state file

Build the topic slug from $ARGUMENTS (lowercase, spaces to hyphens). Find the state file:

```
~/.claude/nlm_state_{topic-slug}.json
```

If no state file exists, stop and tell the user:

> No state file found for "{topic-slug}". Run `/notebooklm-build {topic}` first to create the notebook.

Read the state file. Extract:
- `notebook_id`
- `sources` (the list of URLs already in the notebook)

Print confirmation:
```
Notebook ID: {notebook_id}
Existing sources: {N}
```

---

## Step 2 — Run the updated research sweep

Run `/research $ARGUMENTS`. This triggers the full six-source sweep (YouTube, PubMed, Consensus.app, Semantic Scholar, OpenAlex, Newsletters).

Once the sweep completes, collect all URLs from the output.

**Deduplicate against existing sources:** Remove any URL already present in the state file's `sources` list. Also remove bare pubmed.ncbi.nlm.nih.gov URLs — these will be fetched via E-utilities instead.

Print:
```
Research sweep complete.
Existing sources: {N}
New candidates: {M}
Net new to add: {K}
```

If K = 0, tell the user: "No new sources found — notebook is already up to date." Then skip to Step 5 to regenerate assets with the existing source set anyway.

---

## Step 3 — Add new sources to the notebook

Write this to `nlm_enrich_setup.py` and execute it:

```python
import asyncio
import json
import os
import re
import tempfile
import time
import urllib.request
from notebooklm.client import NotebookLMClient

NOTEBOOK_ID = "{notebook_id}"  # Replace with actual ID from Step 1

new_urls = [
    # REPLACE WITH ACTUAL NEW URLs FROM STEP 2 — one string per line
]

existing_sources = [
    # REPLACE WITH EXISTING sources list from state file
]

pubmed_re = re.compile(r'https?://pubmed\.ncbi\.nlm\.nih\.gov/(\d+)/?')

def fetch_pubmed_abstract(url):
    m = pubmed_re.match(url.strip())
    if not m:
        return None, url
    pmid = m.group(1)
    fetch_url = (
        f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        f"?db=pubmed&id={pmid}&rettype=abstract&retmode=text"
    )
    try:
        time.sleep(4)
        with urllib.request.urlopen(fetch_url, timeout=15) as resp:
            abstract_text = resp.read().decode("utf-8")
        tmp = os.path.join(tempfile.gettempdir(), f"pubmed_{pmid}.txt")
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(abstract_text)
        print(f"  PMID {pmid}: abstract fetched -> {tmp}")
        return tmp, url
    except Exception as e:
        print(f"  PMID {pmid}: fetch failed ({e}), using URL")
        return None, url


async def main():
    async with await NotebookLMClient.from_storage() as nlm:
        sources_to_add = []
        temp_files = []

        for url in new_urls:
            if pubmed_re.match(url.strip()):
                tmp, original = fetch_pubmed_abstract(url)
                if tmp:
                    sources_to_add.append(tmp)
                    temp_files.append(tmp)
                else:
                    sources_to_add.append(original)
            else:
                sources_to_add.append(url)

        if not sources_to_add:
            print("No sources to add.")
            return

        print(f"Adding {len(sources_to_add)} new sources to notebook {NOTEBOOK_ID}...")
        for source in sources_to_add:
            try:
                if os.path.isfile(source):
                    await nlm.sources.add_file(NOTEBOOK_ID, source)
                    print(f"  + file: {os.path.basename(source)}")
                else:
                    await nlm.sources.add_url(NOTEBOOK_ID, source)
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

        print("Sources added.")


asyncio.run(main())
```

After running, update the state file to include the new URLs:

```python
import json, os

topic_slug = "$ARGUMENTS".lower().replace(" ", "-")
state_file = os.path.expanduser(f"~/.claude/nlm_state_{topic_slug}.json")
with open(state_file) as f:
    state = json.load(f)

new_urls = [
    # SAME LIST AS ABOVE
]
state["sources"] = list(set(state.get("sources", []) + new_urls))
with open(state_file, "w") as f:
    json.dump(state, f, indent=2)
print(f"State file updated: {len(state['sources'])} total sources")
```

---

## Step 4 — Re-run the query set

Write this to `nlm_enrich_query.py` and execute it. Uses a separate checkpoint file so it doesn't collide with any existing `nlm_responses.json`:

```python
import asyncio
import json
from notebooklm.client import NotebookLMClient

NOTEBOOK_ID = "{notebook_id}"  # Replace with actual ID
CHECKPOINT_FILE = "nlm_enrich_responses.json"

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

    # --- Content strategy queries ---
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

print(f"Notebook ID: {NOTEBOOK_ID}")


async def run_queries():
    async with await NotebookLMClient.from_storage() as nlm:
        for i, query in enumerate(queries, 1):
            if query in responses:
                print(f"Query {i}/{len(queries)}: already done, skipping.")
                continue

            print(f"Query {i}/{len(queries)}: {query[:70]}...")
            try:
                result = await nlm.chat.ask(NOTEBOOK_ID, query)
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

---

## Step 5 — Generate new assets

Write this to `nlm_enrich_generate.py` and execute it with `python3 -u`. This generates fresh audio, slides, and briefing doc reflecting the enriched source set. Existing notebook artifacts are untouched.

```python
import asyncio
import json
import os
from pathlib import Path
from notebooklm.client import NotebookLMClient
from notebooklm import AudioFormat, AudioLength, SlideDeckFormat, SlideDeckLength
from notebooklm.rpc.types import ReportFormat

NOTEBOOK_ID = "{notebook_id}"  # Replace with actual ID
ARTIFACT_STATE = "nlm_enrich_artifacts.json"
ARTIFACT_TYPE_AUDIO = 1
ARTIFACT_TYPE_REPORT = 2
ARTIFACT_TYPE_SLIDES = 8

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

Keep bullets short — one idea per bullet. No jargon without a brief explanation.
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

        if os.path.exists(ARTIFACT_STATE):
            with open(ARTIFACT_STATE) as f:
                task_ids = json.load(f)
            print(f"Resuming — loaded task IDs from {ARTIFACT_STATE}", flush=True)
        else:
            task_ids = {}

        for name in ["audio", "slides", "report"]:
            if name in task_ids:
                print(f"  Skipping {name} — already tracked: {task_ids[name]}", flush=True)
                continue
            print(f"Submitting {name}...", flush=True)
            if name == "audio":
                result = await nlm.artifacts.generate_audio(
                    NOTEBOOK_ID,
                    instructions=AUDIO_INSTRUCTIONS,
                    audio_format=AudioFormat.DEEP_DIVE,
                    audio_length=AudioLength.LONG,
                )
            elif name == "slides":
                result = await nlm.artifacts.generate_slide_deck(
                    NOTEBOOK_ID,
                    instructions=SLIDE_INSTRUCTIONS,
                    slide_format=SlideDeckFormat.PRESENTER_SLIDES,
                    slide_length=SlideDeckLength.DEFAULT,
                )
            elif name == "report":
                result = await nlm.artifacts.generate_report(
                    NOTEBOOK_ID,
                    report_format=ReportFormat.BRIEFING_DOC,
                    extra_instructions=REPORT_INSTRUCTIONS,
                )
            task_ids[name] = result.task_id
            print(f"  {name} task ID: {result.task_id}", flush=True)
            with open(ARTIFACT_STATE, "w") as f:
                json.dump(task_ids, f, indent=2)

        todo = {k: v for k, v in task_ids.items() if v}
        done = {}
        print("Polling...", flush=True)
        for i in range(45):
            await asyncio.sleep(20)
            for name, task_id in list(todo.items()):
                art = await nlm.artifacts.get(NOTEBOOK_ID, task_id)
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

        if done.get("report"):
            print("\nDownloading report...", flush=True)
            out = await nlm.artifacts.download_report(
                NOTEBOOK_ID,
                output_path="nlm_enrich_report.md",
                artifact_id=done["report"],
            )
            text = Path(out).read_text(encoding="utf-8")
            print(f"  Saved {len(text)} chars to {out}", flush=True)

        print("\nFinal artifact IDs:", flush=True)
        for name, task_id in done.items():
            if task_id:
                art = await nlm.artifacts.get(NOTEBOOK_ID, task_id)
                print(f"  {name}: {task_id}  title: {art.title}", flush=True)
        print("Done.", flush=True)


asyncio.run(main())
```

Run with:

```bash
cd "$HOME" && python3 -u nlm_enrich_generate.py 2>&1
```

If the script times out, re-run the same command — it loads `nlm_enrich_artifacts.json`, skips submissions, and resumes polling.

---

## Step 6 — Find the existing Obsidian vault note

Search the vault for the note corresponding to this topic. Try:

```
C:\Users\Tom\Documents\Home Vault\3 - Knowledge\**\*{topic-words}*.md
```

If multiple matches exist, pick the one whose frontmatter `notebook:` field matches the notebook title, or whose title most closely matches the topic. Confirm the path before proceeding.

---

## Step 7 — Enrich the Obsidian vault note

Read both sources:
- `nlm_enrich_responses.json` (primary: 20 targeted queries against the enriched notebook)
- `nlm_enrich_report.md` (primary: full independent synthesis from the enriched notebook)

**Both are primary sources. The vault note must incorporate the full detail from both.**

Read the existing vault note in full.

Identify what is in the report or query responses that is **not already adequately covered** in the existing note. Look specifically for:
- New studies named in the report that are absent from the note's Key studies section
- Specific numbers, effect sizes, or population sub-groups present in the report but missing from the note
- Structured tables (evidence grade, monitoring, technique selection, protocol comparison) present in the report but absent from the note
- Sections the report has that the note is missing entirely: Monitoring, Red flags and contraindications, Evidence gaps
- New counterarguments or failure points surfaced by the enriched source set

Add all missing content to the existing note. Do not delete or rewrite sections that are already well-covered.

Add or update `updated: {today's date}` in the frontmatter.

Write the enriched note back to its vault path.

Formatting rules — apply throughout:
- British spelling
- No em dashes — use colons, commas, or new sentences instead
- Contractions always
- `[[wikilinks]]` for every named concept, person, mechanism, or study
- Hedge accurately — do not overstate certainty
- Where new responses contradict existing content, represent both sides

---

## Step 8 — Update the enrichment queue

Open `C:\Users\Tom\Documents\Home Vault\1 - Projects\NotebookLM Enrichment Queue.md`.

Find the row for this topic in the Status tracking table and mark the three columns:
- New sources added: number added (or "0 — already current")
- Assets regenerated: ✅
- Vault note enriched: ✅
- Done: ✅

---

## Step 9 — Cleanup and summary

```bash
rm nlm_enrich_setup.py nlm_enrich_query.py nlm_enrich_generate.py nlm_enrich_responses.json nlm_enrich_report.md nlm_enrich_artifacts.json
```

Print a summary in chat:

```
### Enrichment complete: $ARGUMENTS

**New sources added:** {K} (list the titles/domains)
**Assets regenerated:**
  - Audio: "{title}"
  - Slides: "{title}"
  - Briefing doc: "{title}"
**Vault note:** {path} — updated

**What changed:**
[2–3 sentences on what the new sources contributed that wasn't in the original notebook. Be specific.]
```

Then print CliffNotes following the same rules as `/notebooklm-build` Step 8 — only the counterintuitive, surprising, or interesting findings. Only include things genuinely new relative to what was already in the vault note before enrichment.
