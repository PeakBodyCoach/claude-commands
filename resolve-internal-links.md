# /resolve-internal-links

Resolve every `[INTERNAL LINK: text]` placeholder in a Peak Body Coach blog draft to a real WordPress URL. Fetches the published-post index from `peakbodycoach.co.uk`, semantic-ranks candidates per placeholder, presents top 3, and substitutes in place on confirmation. The duplicate `[INTERNAL LINK: ...]` list at the bottom of the draft is stripped after resolution.

This command is interactive. It runs before `/publish-gate` — the gate fails on any unresolved internal-link placeholder.

## Usage

```
/resolve-internal-links [topic-slug]
/resolve-internal-links path/to/article.md
```

## Arguments

`$ARGUMENTS` — either the article's topic slug (e.g. `glp1-muscle-loss`) or a full path to the article markdown.

If a slug is passed, resolve it to `Blog/1 - Draft/[topic-slug]/[topic-slug].md`. If a path is passed, use it directly.

## Configuration

- **Vault root:** `C:/Users/Tom/Documents/Home Vault/2 - Business/Content/`
- **WP REST API:** `https://peakbodycoach.co.uk/wp-json/wp/v2/posts`
- **Cache:** `~/.claude/wordpress-cache.json` (TTL 24 hours)
- **Auth config (optional, read for `site_url` if present):** `~/.claude/wordpress.json`

The WP REST `posts` endpoint is publicly accessible — no auth required for read.

## Required article location

This command requires the per-article subfolder convention:

```
Blog/1 - Draft/[topic-slug]/
    [topic-slug].md       <- the article (resolved in place)
```

If the article is in a legacy topic-bucket folder (e.g. `Blog/1 - Draft/blog-draft-ozempic/...`) or at the root of `1 - Draft/`, stop with:

> This article isn't in the new per-article subfolder convention. `/resolve-internal-links` needs `Blog/1 - Draft/[topic-slug]/[topic-slug].md`. Migrate the article to its own slug-named subfolder first (see the legacy-draft migration in `blog-publishing-pipeline-scope.md`).

## Steps

### 1. Resolve the article

From `$ARGUMENTS`, work out:

- **Slug** — parent folder name of the article file (or filename stem if path was passed)
- **Article file** — full path to `[topic-slug].md`

Confirm the file exists. If not, stop and report the resolved path.

### 2. Find placeholders in body

Walk the article body and capture every `[INTERNAL LINK: text]` occurrence. For each, record:

- The literal placeholder text (the part between the brackets after `INTERNAL LINK:`)
- The line number it appears on
- The 80-character context around it (so the user can see where in the article it sits)

Also detect the duplicate `[INTERNAL LINK: ...]` summary list that some drafts have at the bottom (typically under a heading like `**Internal link placeholders:**`). Note its position — it gets stripped after resolution.

If the body has zero `[INTERNAL LINK: ...]` placeholders in the article body proper (ignore the bottom summary list for this count), stop with:

> No `[INTERNAL LINK: ...]` placeholders found in body. Nothing to resolve.

### 3. Load the WP published-post index

Check `~/.claude/wordpress-cache.json`. If the file exists and `fetched_at` is within 24 hours, load the cached `posts` array.

Otherwise, fetch fresh:

```bash
curl -s "https://peakbodycoach.co.uk/wp-json/wp/v2/posts?per_page=100&_fields=id,slug,link,title&page=1"
```

If the response includes more than 100 posts (check `X-WP-TotalPages` header or pagination metadata), paginate with `&page=2`, `&page=3`, etc. until all pages are fetched.

Write the combined result back to `~/.claude/wordpress-cache.json`:

```json
{
  "fetched_at": "2026-05-23T14:30:00Z",
  "site_url": "https://peakbodycoach.co.uk",
  "posts": [
    {"id": 1473, "slug": "daily-protein-range", "link": "https://peakbodycoach.co.uk/daily-protein-range/", "title": "How Much Protein Do You Actually Need?"},
    ...
  ]
}
```

Strip HTML entities from titles (e.g. `&#8217;` → `'`) so semantic matching sees clean text.

If `~/.claude/wordpress.json` exists with a `site_url` field, use that as the base; otherwise default to `https://peakbodycoach.co.uk`.

### 4. Resolve each placeholder

Walk placeholders in document order. For each:

**Step 4a: Semantic rank.** Score every post in the index by relevance to the placeholder text. Match against post title primarily, then slug. A placeholder like `protein targets` should rank `daily-protein-range` highly. Pick the top 3.

**Step 4b: Present candidates.** Show:

```
Placeholder 1 of [N]: [INTERNAL LINK: protein targets]
Context: "...for the reasons I've written about elsewhere, most GLP-1 users [INTERNAL LINK: protein targets] aren't hitting the intake needed..."
Line: 36

Candidates:
  1. How Much Protein Do You Actually Need? — /daily-protein-range/
  2. Why You're Losing Weight But Still Feel Weak on Mounjaro — /feeling-weak-on-mounjaro/
  3. The Cheat Meal Paradox — /the-cheat-meal-paradox/

Pick one of: 1, 2, 3, custom (paste URL), skip (leave placeholder, will block /publish-gate)
```

**Always present 3 candidates** even if the top match feels unambiguous. No auto-pick.

If the index has fewer than 3 posts that meet any relevance threshold, show what exists and explain the shortfall. The user can still pick from a shorter list, paste a custom URL, or skip.

**Step 4c: Read the user's choice.**

- **1, 2, or 3** — use the chosen post's URL.
- **custom** — prompt for a URL. Accept any well-formed URL (`https://...`). Do not validate the URL is reachable.
- **skip** — leave the placeholder in place. Flag in the final report.

**Step 4d: Anchor text confirmation.** Default the anchor text to the placeholder description exactly as written. Confirm with the user:

```
Anchor text: "protein targets"  (default = placeholder description)
Press enter to accept, or type a replacement:
```

Anchor text override is per-link.

**Step 4e: Build the substitution.** Format: `[anchor text](URL)`. Example:

```
[INTERNAL LINK: protein targets] → [protein targets](https://peakbodycoach.co.uk/daily-protein-range/)
```

Record the substitution but don't write to disk yet. Continue to the next placeholder.

### 5. Apply substitutions and strip the bottom list

Once every placeholder has been processed:

**5a: Substitute.** Walk the body in reverse line order (so earlier substitutions don't shift later positions) and replace each `[INTERNAL LINK: ...]` with its corresponding `[anchor](URL)` resolution. Skip the ones the user chose to skip.

**5b: Strip the duplicate bottom list.** If the article body ends with a section like:

```
**Internal link placeholders:**
- [INTERNAL LINK: protein targets] — protein target / how much protein you need article
- [INTERNAL LINK: calorie deficit] — calorie deficit explainer
```

Remove the heading line and the entire bulleted list. Also remove any blank lines and the preceding `---` separator if it was only there to introduce the list.

If the bottom list is intermixed with other content (e.g. a CTA), leave the other content intact and only remove the placeholders heading + bullets.

**5c: Write to disk.** Save the article file in place.

### 6. Report

Summarise in chat:

```
Resolved [N] of [M] internal-link placeholders in [topic-slug]

Resolved:
  - "protein targets" → /daily-protein-range/
  - "calorie deficit" → /why-calorie-counting-works/
  - "intermittent fasting" → https://[custom URL]

Skipped (will block /publish-gate until fixed):
  - "DIAAS vs PDCAAS" — no matching article in WP index

Cache: [cache hit / refreshed]
Bottom placeholder list: [stripped / not present]
```

If any placeholders were skipped, tell the user verbatim:

> [N] placeholder(s) were skipped. Either write the dependency article(s) and publish them first, then re-run `/resolve-internal-links`, or remove the placeholder(s) from the body if they're no longer needed. `/publish-gate` will fail until all `[INTERNAL LINK: ...]` are resolved.

If all placeholders resolved cleanly:

> All internal links resolved. Re-run `/publish-gate [topic-slug]` to validate before WP push.

## Notes

- This command is destructive (rewrites the article in place). The git working tree should be clean before running, or you should commit after each resolution session.
- The 24-hour cache is keyed on the file's `fetched_at` timestamp. Force-refresh by deleting `~/.claude/wordpress-cache.json` and re-running.
- The cache is shared with `/wordpress-publish` (category lookups) and any future skill that needs the published-post index. One source of truth.
- Semantic ranking is the model's call — there's no embedding score or threshold. Read titles and slugs, judge relevance by topic similarity to the placeholder text. Bias toward exact-keyword matches in the slug (e.g. `protein targets` → `daily-protein-range` is a strong match because "protein" is in the slug) but don't require them.
- The skip option is intentional friction. Skipped placeholders fail the gate; the user is forced to either write the missing article or remove the placeholder. This keeps the internal-link graph consistent.
- HTML entities in WP titles (`&#8217;`, `&amp;`, etc.) must be decoded before presenting candidates to the user. Read titles as-rendered.
- Anchor text is the user's editorial call. Defaulting to the placeholder description preserves the writer's intent; the override exists for cases where the placeholder text was a slug (e.g. `[INTERNAL LINK: how-to-keep-muscle-on-ozempic]`) and a human-readable anchor is needed.
