Search curated Substack newsletters for posts on: $ARGUMENTS

Check each RSS feed in the curated writer list below for relevant content. Follow these steps exactly:

## Curated writer list

<!-- EDIT THIS LIST — add/remove writers as needed -->
<!-- Any RSS feed works, not just Substack -->

| Writer | RSS Feed URL | Specialism |
|---|---|---|
| Peter Attia | https://peterattiamd.com/feed/ | Longevity, performance medicine |
| Layne Norton | https://biolayne.substack.com/feed | Evidence-based nutrition, training |
| Andy Galpin | https://andygalpin.substack.com/feed | Exercise science, performance |
| Eric Trexler | https://erictrexler.substack.com/feed | Nutrition science, body composition |
| Mike Israetel | https://renaissanceperiodization.substack.com/feed | Hypertrophy, sport science |
| Stan Efferding | https://stanefferding.substack.com/feed | Vertical diet, performance nutrition |
| Stephan Guyenet | https://weightology.substack.com/feed | Obesity science, appetite regulation |
| James Krieger | https://weightology.net/feed/ | Evidence-based nutrition |
| Alan Aragon | https://alanaragon.substack.com/feed | Nutrition research, body composition |
| Greg Nuckols | https://gregnuckols.substack.com/feed | Strength science, research review |

<!-- Add more rows as needed. Substack feeds: https://[writer].substack.com/feed -->

## Step 1 — Fetch each RSS feed

For each writer, fetch their RSS URL. Parse the XML to extract:
- `<title>` — post title
- `<link>` — post URL
- `<pubDate>` — publication date
- `<description>` or `<content:encoded>` — excerpt

## Step 2 — Filter for relevance

Keep posts where the title or description contains terms related to **$ARGUMENTS**. Prefer posts published within the last 24 months. Aim for 4–8 relevant posts across the list.

## Step 3 — Display results

Display each relevant post in this format (matching the YouTube search command style):

1. **[Post Title]**
   [Post URL]
   [Publish date] · [one sentence on relevance to $ARGUMENTS]
   [Writer Name]

2. **[Post Title]**
   ...

After all results:

---
**Substack search complete.** Checked [N] feeds, found [M] relevant posts for "$ARGUMENTS". No relevant content from: [writer names or "none"].

If a feed fails to load, note it and move on. Do not hallucinate post titles or URLs.
