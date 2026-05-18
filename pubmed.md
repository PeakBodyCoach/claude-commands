Search PubMed for high-quality research on: $ARGUMENTS

Use the NCBI E-utilities API (no API key required). Follow these steps exactly:

## Step 1 — Search for PMIDs

Fetch this URL (URL-encode the query — replace spaces with `+`):

```
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=$ARGUMENTS&retmax=8&sort=relevance&retmode=json
```

Extract the list of PMIDs from `result.idlist`.

If no results, broaden the query (remove qualifiers, use MeSH-friendly terms) and retry once.

## Step 2 — Fetch summaries

```
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=PMID1,PMID2,...&retmode=json
```

Extract for each: Title, Authors, Journal, Year, PMID, publication type.

## Step 3 — Filter

Keep 5–8 results. Prefer:
- Meta-analyses, systematic reviews, RCTs, cohort studies
- Year 2015 or later (2019+ preferred)
- Clearly relevant to the search query

Drop corrections, retractions, and conference abstracts.

## Step 4 — Display results

Display each result in this format (matching the YouTube search command style):

1. **[Paper Title]**
   https://pubmed.ncbi.nlm.nih.gov/[PMID]/
   [Study type] · [Journal] · [Year]
   [First Author] et al.

2. **[Paper Title]**
   ...

After all results:

---
**PubMed search complete.** Found [N] results for "$ARGUMENTS". Strongest evidence: [one sentence on what the literature shows].

Do not hallucinate PMIDs, titles, or authors — only output what the API returns.
