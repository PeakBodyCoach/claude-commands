Run a full multi-source research sweep on: $ARGUMENTS

This command orchestrates six source searches and returns a combined source list formatted for direct import into NotebookLM.

---

## Execution plan

Run all six source searches in order. Do not skip any step.

### Source 1 — YouTube

Run the `/yt-search` command for **$ARGUMENTS**.

The YouTube command uses `yt-dlp` via `python $HOME\.claude\commands\youtube_search.py`. If it is not available in this session, search YouTube manually for: `$ARGUMENTS evidence based`

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

### Source 4 — Semantic Scholar

Run the `/scholar` command for **$ARGUMENTS**, or execute directly:

```bash
python $HOME\.claude\commands\semantic_scholar.py -n 8 $ARGUMENTS
```

Semantic Scholar covers 200M+ papers across all disciplines and includes citation counts, TLDR auto-summaries, and open-access PDF links. Better coverage than PubMed outside biomedicine (behaviour change, psychology, sport science). The script auto-retries on 429 and 5xx, but if `SEMANTIC_SCHOLAR_API_KEY` is set in the environment, requests use the much higher authenticated rate limit. See `/scholar` for setup.

### Source 5 — OpenAlex

Run the `/openalex` command for **$ARGUMENTS**, or execute directly:

```bash
python $HOME\.claude\commands\openalex.py -n 8 --year 2018 $ARGUMENTS
```

OpenAlex is a free, fully open academic search engine covering 250M+ works across all disciplines. Stronger than PubMed outside biomedicine: behavioural science, psychology, sport science, education. Also catches preprints and grey literature. No auth required, no rate-limit panic. Includes citation counts, journal venue, OA status, and OpenAlex topic concepts for each result.

### Source 6 — Substack / newsletters

Run the `/substack` command for **$ARGUMENTS**. Fetch all RSS feeds in the curated writer list and filter for relevant posts.

---

## Output format

Present all results under the heading:

# Research sources: $ARGUMENTS

Six sections. Each result uses the same numbered format as the YouTube search command:

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

## 🎓 Semantic Scholar

1. **[Paper Title]**
   [Semantic Scholar URL or open-access PDF URL]
   [Venue] · [Year] · [Citations] citations
   [First Author] et al.
   TLDR: [auto-generated TLDR if present]

## 🌐 OpenAlex

1. **[Paper Title]**
   [OpenAlex URL or open-access PDF URL]
   [Work type] · [Venue] · [Year] · [Citations] citations · OA: [yes/no]
   [First Author] et al.
   Topics: [top 2-3 OpenAlex concepts]

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
| Semantic Scholar | N | [highest-cited paper or strongest TLDR] |
| OpenAlex | N | [highest-cited paper or strongest behavioural finding] |
| Newsletters | N | [top writer or post] |

**Overall evidence picture:** 2–3 sentences on what sources agree on, where uncertainty exists, and any notable conflicts.

**NotebookLM ready:** All URLs above can be added directly as sources.

---

If a source type returns nothing, write "No results found" in that section. Do not fabricate any sources.
