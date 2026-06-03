Search curated Substack and newsletter feeds for posts on: $ARGUMENTS

Check each RSS feed in the curated writer list below for relevant content. Follow these steps exactly.

## Curated writer list

Last verified: 2026-05-20. Most of the original Substack-only list went dead between 2024 and 2026 as writers migrated off Substack. This is the refreshed working set, drawn from author home sites and major publishing platforms.

### Verified working

| Writer | RSS Feed URL | Specialism | Notes |
|---|---|---|---|
| Peter Attia | https://peterattiamd.com/feed/ | Longevity, performance medicine | Weekly long-form + AMA podcast. |
| James Krieger | https://weightology.net/feed/ | Evidence-based nutrition, body comp | Now mostly archive; active content sits in REPS Research Review (paid). |
| Menno Henselmans | https://mennohenselmans.com/feed/ | Hypertrophy, training science, study breakdowns | **High signal.** Weekly evidence-based posts. |
| Renaissance Periodization | https://rpstrength.com/blogs/articles.atom | Hypertrophy, programming, women's training, GLP-1 | **High signal.** Frequent, applied. |
| Lyle McDonald | https://bodyrecomposition.com/feed | Fat loss, metabolic adaptation, training | Updates rarely but each post is deep. |

### Cloudflare-blocked (work in browser, fail WebFetch)

Add these once Phase 4 of the research-workflow-roadmap (Playwright helper) lands. Until then they need manual checking.

| Writer | RSS Feed URL | Specialism |
|---|---|---|
| Stronger By Science | https://www.strongerbyscience.com/feed/ | Strength, hypertrophy, research review |
| Examine.com research updates | https://examine.com/feed/ | Nutrition and supplement research summaries |

### Removed (dead URLs as of 2026-05-20)

Documented so future re-checks know what was tried.

| Writer | Last-known URL | Status |
|---|---|---|
| Layne Norton | biolayne.substack.com/feed | 404. biolayne.com/feed exists but only carries product/coaching announcements, not training content. Active output is on YouTube and podcasts. |
| Andy Galpin | andygalpin.substack.com/feed | 404. Output is now podcast-only (The Galpin Equity Project, Huberman appearances). |
| Eric Trexler | erictrexler.substack.com/feed | Feed empty. Active output is on Stronger By Science. |
| Mike Israetel / RP Substack | renaissanceperiodization.substack.com/feed | 404. Replaced with the RP blog feed above. |
| Stan Efferding | stanefferding.substack.com/feed | 404. Output is YouTube-only. |
| Alan Aragon | alanaragon.substack.com/feed and alanaragon.com/feed | Both empty. The Alan Aragon Research Review is paid and has no public RSS. |
| Greg Nuckols personal | gregnuckols.substack.com/feed | 404. Active output is on Stronger By Science. |
| Stephan Guyenet | weightology.substack.com/feed | 404 and was a misattribution; Guyenet writes at stephanguyenet.com which has no working RSS. |

<!--
Adding a new feed:
- Verify the URL returns valid RSS or Atom XML with <item> or <entry> elements containing real recent posts.
- Note the writer's specialism in one short phrase.
- If a feed renders empty even though the site is alive, the writer likely moved their content to a podcast or paid newsletter — move them to "Removed" with a note about their actual current home.
-->

## Step 1 — Fetch each RSS feed

For each writer in "Verified working", fetch their RSS URL. Parse the XML to extract:
- `<title>` — post title
- `<link>` — post URL
- `<pubDate>` — publication date
- `<description>` or `<content:encoded>` — excerpt

For each writer in "Cloudflare-blocked", attempt the fetch. Expect a 403 or 429. Note the failure and move on. Do not retry.

## Step 2 — Filter for relevance

Keep posts where the title or description contains terms related to **$ARGUMENTS**. Prefer posts published within the last 24 months. Aim for 4–8 relevant posts across the list.

## Step 3 — Display results

Display each relevant post in this format:

```
1. **[Post Title]**
   [Post URL]
   [Publish date] · [one sentence on relevance to $ARGUMENTS]
   [Writer Name]
```

After all results:

---
**Newsletter search complete.** Checked [N] feeds, found [M] relevant posts for "$ARGUMENTS". No relevant content from: [writer names or "none"]. Cloudflare-blocked (skipped): [N writers].

If a feed fails to load unexpectedly, note it inline and move on. Do not hallucinate post titles or URLs.
