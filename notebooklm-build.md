Run the full NotebookLM → Obsidian pipeline for: $ARGUMENTS

This command is fully automated. It will:
1. Create a NotebookLM notebook and add all research sources
2. Run the full query set against the notebook
3. Synthesise the responses into a structured Obsidian note
4. Write the note directly to the vault

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
import time
import json
import os
import re
import tempfile
import urllib.request
from notebooklm import NotebookLM

nlm = NotebookLM()

notebook_title = "$ARGUMENTS Research"
print(f"Creating notebook: {notebook_title}")
notebook = nlm.create_notebook(notebook_title)
print(f"Notebook created — ID: {notebook.id}")

raw_urls = [
    # REPLACE WITH ACTUAL URLs FROM STEP 1 — one string per line
]

# PubMed URLs trigger reCAPTCHA when scraped by NotebookLM.
# Convert them to abstract text files via NCBI E-utilities instead.
pubmed_re = re.compile(r'https?://pubmed\.ncbi\.nlm\.nih\.gov/(\d+)/?')
sources = []
temp_files = []

for url in raw_urls:
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
            print(f"  PMID {pmid}: abstract fetched → {tmp}")
        except Exception as e:
            print(f"  PMID {pmid}: fetch failed ({e}), falling back to URL")
            sources.append(url)
    else:
        sources.append(url)

print(f"Adding {len(sources)} sources...")
notebook.add_sources(sources)

print("Waiting 90 seconds for source ingestion...")
time.sleep(90)

# Clean up temp abstract files
for tmp in temp_files:
    try:
        os.remove(tmp)
    except OSError:
        pass

# Save state file so future runs skip setup
topic_slug = "$ARGUMENTS".lower().replace(" ", "-")
state_file = os.path.expanduser(f"~/.claude/nlm_state_{topic_slug}.json")
os.makedirs(os.path.dirname(state_file), exist_ok=True)
with open(state_file, "w") as f:
    json.dump({"notebook_id": notebook.id, "sources": raw_urls}, f, indent=2)
print(f"State saved to {state_file}")

with open("nlm_notebook_id.txt", "w") as f:
    f.write(notebook.id)

print("Setup complete.")
```

Replace the `raw_urls` list with the actual source URLs before running.

---

## Step 4 — Run the query set

Write this to `nlm_query.py` and execute it:

```python
import time
import json
import signal
import sys
from notebooklm import NotebookLM

# --- Per-query timeout handler ---
class QueryTimeout(Exception):
    pass

def timeout_handler(signum, frame):
    raise QueryTimeout()

QUERY_TIMEOUT_SECS = 75  # kill any single query after 75 seconds

nlm = NotebookLM()

with open("nlm_notebook_id.txt") as f:
    notebook_id = f.read().strip()

notebook = nlm.get_notebook(notebook_id)

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

CHECKPOINT_FILE = "nlm_responses.json"

# Load existing checkpoint if resuming after a crash
try:
    with open(CHECKPOINT_FILE, encoding="utf-8") as f:
        responses = json.load(f)
    print(f"Resuming — {len(responses)} queries already completed.")
except FileNotFoundError:
    responses = {}

completed = 0
skipped = 0

for i, query in enumerate(queries, 1):
    # Skip already-completed queries (checkpoint resume)
    if query in responses:
        print(f"Query {i}/{len(queries)}: already done, skipping.")
        completed += 1
        continue

    print(f"Query {i}/{len(queries)}: {query[:70]}...")

    # Set per-query timeout (Unix only — on Windows this is a no-op, rely on try/except)
    try:
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(QUERY_TIMEOUT_SECS)
    except (AttributeError, OSError):
        pass  # SIGALRM not available on Windows — timeout relies on notebooklm-py's own timeout

    try:
        response = notebook.query(query)
        responses[query] = response
        completed += 1
        print(f"  ✓ {len(response)} chars")
    except QueryTimeout:
        print(f"  ✗ Timed out after {QUERY_TIMEOUT_SECS}s — skipping")
        responses[query] = "[TIMED OUT — re-run to retry]"
        skipped += 1
    except Exception as e:
        print(f"  ✗ Error: {e}")
        responses[query] = f"[FAILED: {e}]"
        skipped += 1
    finally:
        try:
            signal.alarm(0)  # cancel alarm
        except (AttributeError, OSError):
            pass

    # Save checkpoint after every query
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(responses, f, indent=2, ensure_ascii=False)

    time.sleep(4)  # brief pause between queries

print(f"\nDone. {completed} completed, {skipped} skipped.")
print(f"Results saved to {CHECKPOINT_FILE}")
if skipped > 0:
    print(f"Re-run this script to retry timed-out queries — checkpoint will resume from where it left off.")
```

**Important:** On Windows, SIGALRM is unavailable. The per-query timeout relies on notebooklm-py's internal timeout. If a query hangs beyond the tool's own timeout, the script will still move on due to the exception handler. The checkpoint means any re-run picks up exactly where it stopped.
```

Wait for all 15 queries to finish before proceeding.

---

## Step 5 — Synthesise the Obsidian note

Read `nlm_responses.json`. Before writing, internally identify:

- The 3–5 most important factual claims across all responses
- The strongest evidence cited (study names, authors, effect sizes)
- Any contradictions or tensions between responses
- All related concepts, mechanisms, and named researchers mentioned
- Practical protocols or specific numbers
- Explicit caveats, limitations, and open questions

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

## Overview

[2–3 paragraphs. What it is, why it matters, what the key claims are. Prose only — no bullets in this section. Pull the strongest signals from across all 15 responses.]

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

## Step 6 — Write to the Obsidian vault

Determine the subfolder from the `topic/` tag:

| topic/ tag | Vault path |
|---|---|
| nutrition | `C:\Users\Tom\Documents\Home Vault\3 - Resources\Nutrition` |
| training | `C:\Users\Tom\Documents\Home Vault\3 - Resources\Training` |
| supplementation | `C:\Users\Tom\Documents\Home Vault\3 - Resources\Supplementation` |
| recovery | `C:\Users\Tom\Documents\Home Vault\3 - Resources\Recovery` |
| body-composition | `C:\Users\Tom\Documents\Home Vault\3 - Resources\Body Composition` |
| health | `C:\Users\Tom\Documents\Home Vault\3 - Resources\Health` |
| performance | `C:\Users\Tom\Documents\Home Vault\3 - Resources\Performance` |
| psychology | `C:\Users\Tom\Documents\Home Vault\3 - Resources\Psychology` |

Filename: title-case the topic, spaces to hyphens, `.md` extension. Example: `Fibremaxxing.md`

Write this to `nlm_write.py` and execute it:

```python
import os

folder = r"C:\Users\Tom\Documents\Home Vault\Knowledge\[Subfolder]"
filepath = os.path.join(folder, "[Filename].md")

os.makedirs(folder, exist_ok=True)

note_content = """\
[FULL NOTE CONTENT — write the complete markdown here]
"""

with open(filepath, "w", encoding="utf-8") as f:
    f.write(note_content)

print(f"✓ Written to: {filepath}")
```

After writing, confirm:

```
✓ Note written to: C:\Users\Tom\Documents\Home Vault\Knowledge\[Subfolder]\[Filename].md
✓ Notebook: "$ARGUMENTS Research"
✓ Sources added: [N]
✓ Queries run: 20 (15 knowledge + 5 content strategy)
```

Then list:

**Wikilinks to stub out:** Every `[[link]]` used in the note that likely needs its own file — your backlog for future notes.

---

## Cleanup

```bash
rm nlm_setup.py nlm_query.py nlm_write.py nlm_notebook_id.txt nlm_responses.json
```
