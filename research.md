Run a full multi-source research sweep on: $ARGUMENTS

This command orchestrates four source searches and returns a combined source list formatted for direct import into NotebookLM.

---

## Execution plan

Run all four source searches in order. Do not skip any step.

### Source 1 — YouTube

Run the `/youtube-search` command (or `/yt-search`) for **$ARGUMENTS**.

The YouTube command uses `yt-dlp` via `python ~/.claude/commands/youtube_search.py`. If it is not available in this session, search YouTube manually for: `$ARGUMENTS evidence based`

### Source 2 — PubMed

Run the `/pubmed` command for **$ARGUMENTS**, or execute directly:

1. Fetch: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=$ARGUMENTS&retmax=8&sort=relevance&retmode=json`
2. Fetch summaries: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=[IDS]&retmode=json`
3. Keep 5–8 results: meta-analyses, systematic reviews, RCTs preferred. Year 2015+.

### Source 3 — Consensus.app

Run the `/consensus` command for **$ARGUMENTS**, or execute directly:

1. Fetch: `https://consensus.app/results/?q=$ARGUMENTS`
2. If the page renders client-side and returns no parseable content, output the URL and a CiC prompt for manual extraction (see `/consensus` for the fallback block).

Consensus is an AI-powered academic search engine that returns a directional verdict (yes / no / possibly / mixed) backed by individual study cards. Use it for behavioural, training, nutrition, recovery, and health-outcome questions. For supplement-specific evidence grades, use `/examine` standalone (no longer in the default research sweep).

### Source 4 — Substack / newsletters

Run the `/substack` command for **$ARGUMENTS**. Fetch all RSS feeds in the curated writer list and filter for relevant posts.

---

## Output format

Present all results under the heading:

# Research sources: $ARGUMENTS

Four sections. Each result uses the same numbered format as the YouTube search command:

```
## 🎬 YouTube

1. **[Video Title]**
   https://youtube.com/watch?v=...
   [Views] · [Duration] · [Upload Date]
   [Channel Name]

## 🔬 PubMed

1. **[Paper Title]**
   https://pubmed.ncbi.nlm.nih.gov/[PMID]/
   [Study type] · [Journal] · [Year]
   [First Author] et al.

## 🧪 Consensus.app

1. **[Paper Title]**
   [DOI or Consensus URL]
   [Verdict / direction] · [Journal] · [Year]
   [First Author] et al.

## 📬 Newsletters

1. **[Post Title]**
   [Post URL]
   [Date] · [One-sentence relevance note]
   [Writer Name]
```

---

After all four sections, output:

## Summary: $ARGUMENTS

| Source | Results | Highlight |
|---|---|---|
| YouTube | N | [top video or channel] |
| PubMed | N | [strongest paper or finding] |
| Consensus.app | N | [Consensus Meter verdict or strongest cited finding] |
| Newsletters | N | [top writer or post] |

**Overall evidence picture:** 2–3 sentences on what sources agree on, where uncertainty exists, and any notable conflicts.

**NotebookLM ready:** All URLs above can be added directly as sources.

---

If a source type returns nothing, write "No results found" in that section. Do not fabricate any sources.
