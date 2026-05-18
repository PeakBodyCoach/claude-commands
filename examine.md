Fetch evidence summaries from Examine.com for: $ARGUMENTS

Examine.com is a source-cited nutrition and supplement research database. Use web fetch to pull their content. Follow these steps exactly:

## Step 1 — Construct target URLs

Build candidate URLs (replace spaces with hyphens, lowercase everything):

1. `https://examine.com/supplements/$ARGUMENTS-slug/`
2. `https://examine.com/nutrition/$ARGUMENTS-slug/`
3. `https://examine.com/search/?q=$ARGUMENTS-url-encoded` (fallback)

Try URL 1 first. If it 404s or has no useful content, try URL 2, then URL 3.

## Step 2 — Fetch and extract

Retrieve the page. Extract:
- The summary verdict / "bottom line"
- Human effect matrix entries: outcome → effect direction → evidence grade
- Key cited studies (title + PMID/DOI if shown)
- FAQ entries if present

If using the search fallback, fetch the 2–3 most relevant result pages individually.

## Step 3 — Display results

Display each page in this format (matching the YouTube search command style):

1. **[Topic Name — page type, e.g. "Creatine — Supplement Overview"]**
   https://examine.com/supplements/[slug]/
   [Overall verdict in one sentence] · Evidence grade: [A/B/C/D if shown]
   Examine.com

2. **[Outcome — e.g. "Creatine → Muscle Strength"]**
   https://examine.com/supplements/[slug]/#muscle-strength
   [Effect direction] · [N studies] · Grade [X]
   Examine.com

List up to 5 outcome entries most relevant to the search topic.

After all results:

---
**Examine.com search complete.** Retrieved [N] page(s) for "$ARGUMENTS". Evidence note: [one sentence on overall evidence strength as Examine grades it].

Do not fabricate evidence grades or outcome data — only report what is on the fetched page.
