Fetch evidence summaries from Consensus.app for: $ARGUMENTS

Consensus.app is an AI-powered academic search engine that synthesises findings across peer-reviewed papers into a directional verdict (yes / no / possibly / mixed), backed by individual study cards. It is the right source for any behavioural, training, nutrition, recovery, or health-outcome question. For supplement-specific evidence grades, use `/examine` instead.

## Step 1 — Construct the search URL

URL-encode the query (spaces become `+`, special characters percent-encoded). The search URL is:

```
https://consensus.app/results/?q=$ARGUMENTS
```

## Step 2 — Attempt to fetch

Try WebFetch on the URL. Consensus often renders client-side, so the response may be empty, partial, or contain only the page shell. If so, do NOT fabricate findings.

## Step 3 — Display results

If the fetch returns useful content, extract:

- The Consensus Meter result (e.g. "75% of studies say yes", or the verdict label)
- The AI-generated summary if present (verbatim)
- The top 5–8 study cards with title, first author, journal, year, and DOI or link

Format each result:

```
1. **[Paper Title]**
   [DOI or Consensus URL]
   [Verdict / direction] · [Journal] · [Year]
   [First Author] et al.
```

After all results:

---
**Consensus.app search complete.** Found [N] studies for "$ARGUMENTS". Verdict: [the Consensus Meter direction]. Summary: [one sentence on the synthesised finding].

## Fallback — when the fetch fails

If WebFetch returns 403, 429, empty content, or only the page shell, output this block instead:

---
**Consensus.app fetch did not return parseable content** (the page renders client-side). Open this URL manually:

```
https://consensus.app/results/?q=[the encoded query]
```

Recommended steps in the browser:
1. Read the Consensus Meter verdict at the top.
2. Skim the top 5–8 study cards.
3. Paste the verdict and the strongest 3–5 citations back into the chat so they can be added to NotebookLM.

Or use Claude in Chrome with this prompt:

```
Open https://consensus.app/results/?q=[encoded query] in this tab.

Extract:
1. The Consensus Meter verdict (yes/no/possibly/mixed, plus the percentage if shown).
2. The AI summary at the top of the page (verbatim).
3. The top 8 study cards, each with: title, first author, journal, year, DOI or link, and the one-line finding Consensus extracted.

Format as clean markdown for pasting into Obsidian.
```

Do not fabricate verdicts, percentages, or study citations under any circumstances.
