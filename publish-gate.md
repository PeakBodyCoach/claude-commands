# /publish-gate

Final pre-publish check for a Peak Body Coach blog article. Sweeps for unresolved placeholders, validates the 2-marker image structure, runs the SEO audit, confirms image assets are present with alt text and attribution, advisory-checks external link health, prints a WordPress upload checklist, and on confirmation moves the article subfolder from `Blog/1 - Draft/` to `Blog/3 - PostedArchive/` with `stage: published` set.

This is the last command in the blog production flow. It doesn't push to WordPress, it doesn't upload to Drive, and it doesn't touch Notion. The vault is the source of truth.

## Usage

```
/publish-gate [topic-slug]
/publish-gate path/to/article.md
```

## Arguments

`$ARGUMENTS` — either the article's topic slug (e.g. `glp1-muscle-loss`) or a full path to the article markdown.

If a slug is passed, resolve it to `Blog/1 - Draft/[topic-slug]/[topic-slug].md`. If a path is passed, use it directly.

## Configuration

- **Vault root:** `C:/Users/Tom/Documents/Home Vault/2 - Business/Content/`
- **Draft folder:** `Blog/1 - Draft/[topic-slug]/`
- **Archive folder:** `Blog/3 - PostedArchive/[topic-slug]/`
- **Image size ceiling:** 512000 bytes (500KB)

## Required article location

This command requires the same per-article subfolder convention as `/blog-images`:

```
Blog/1 - Draft/[topic-slug]/
    [topic-slug].md       <- the article
    image-plan.md         <- written by /blog-images
    images/
        [topic-slug]-featured.jpg
        [topic-slug]-quote.jpg     (optional)
        [topic-slug]-diagram.jpg   (optional)
        [topic-slug]-body-featured.jpg  (optional)
        attributions.csv
```

Before doing anything else, check the resolved path:

1. If the article is at `Blog/1 - Draft/[topic-slug]/[topic-slug].md` (filename matches parent folder, parent of parent is `1 - Draft`), proceed. The slug is the parent folder name.
2. If the article is at `Blog/1 - Draft/[any-name].md` (root of `1 - Draft/`, no per-article subfolder) OR inside a topic-bucket folder like `Blog/1 - Draft/blog-draft-training/[any-name].md`, **stop with this message**:

   > This article isn't in the new per-article subfolder convention. `/publish-gate` needs `Blog/1 - Draft/[topic-slug]/[topic-slug].md`. Either move the article into its own slug-named subfolder and re-run `/blog-images`, or — if this is a legacy draft you don't want to migrate — publish it by hand using the old Notion + Drive flow.

   Legacy drafts at the root of `1 - Draft/` are intentionally not handled by this command. The new structure applies to new articles only.

## Steps

### 1. Resolve the article and read its plan

From `$ARGUMENTS`, work out:

- **Slug** — parent folder name of the article file
- **Article folder** — full path to `Blog/1 - Draft/[topic-slug]/`
- **Article file** — `[topic-slug].md` inside that folder
- **Image plan** — read `image-plan.md` in the same folder if present. The plan should have Hero plus a Slot 1 and Slot 2 section, each labelled with the slot type (`quote`, `diagram`, or `body`). The slot types should match the body markers captured in Step 3. If `image-plan.md` is missing, that's not a hard stop — fall back to checking only the hero asset (always required) and warn the user that the plan is missing so they can verify what's intended.

Also read the article's frontmatter and confirm:

- `type: blog`
- `topic:` matches the slug
- `stage:` is `ready` (or `seo-audit`). If `stage:` is `drafting`, warn the user that the article hasn't been through the SEO audit yet and ask whether to proceed anyway.
- `meta_description:`, `category:`, `target_keyword:` are all present. If any are missing, stop and tell the user to run `/seo-optimisation` first — these are required for WordPress.

### 2. Unresolved placeholder sweep

Walk the article body and search for any of these writer-shorthand placeholders that should have been resolved before publish:

| Placeholder pattern | What it is | How to resolve |
|---|---|---|
| `[INTERNAL LINK: ...]` | Unresolved internal link | Run `/resolve-internal-links [topic-slug]` |
| `[EXTERNAL LINK: ...]` | Unresolved external citation | Find the source URL and replace with `[anchor](URL)` |
| `[cite]` or `[cite — Author Year]` | Unresolved inline citation | Find the source URL and replace with a real markdown link |
| `[TODO: ...]` | Writer's note to self | Address the TODO, remove the marker |

If any are found, stop with:

```
GATE: FAIL — [N] unresolved placeholder(s) in body.

Found:
  - Line [N]: [INTERNAL LINK: protein targets]
  - Line [N]: [EXTERNAL LINK: Hamilton-Reeves 2010 meta-analysis]
  - Line [N]: [cite — Aragon & Schoenfeld 2013]
  - Line [N]: [TODO: tighten the second paragraph]

For `[INTERNAL LINK: ...]`: run `/resolve-internal-links [topic-slug]`.
For all others: edit the article directly to resolve.

Then re-run `/publish-gate`.
```

Do not move on to the SEO audit. Do not move the folder. Unresolved placeholders would ship as broken-looking literal text in the published post; the gate blocks until every one is gone.

### 3. Image marker count check

Walk the article body and count `<!-- IMAGE: type -->` HTML-comment markers. The Peak Body Coach standard assembly is exactly 2 body markers (the featured image is implicit and has no marker).

Validation:
- Exactly 2 markers must be present
- Each marker's type must be one of `quote`, `diagram`, or `body`

If 0 or 1 markers, stop with:

```
GATE: FAIL — body has [N] image marker(s) but exactly 2 are required.
```

Add the missing markers per `article-structure.md` (Image Markers in Body), then re-run.

If 3+ markers, stop with:

```
GATE: FAIL — body has [N] image markers but exactly 2 are required.
Remove the surplus marker(s) — the standard PBC assembly is hero + 2 body images.
```

If any marker uses an unsupported type, stop with:

```
GATE: FAIL — marker `<!-- IMAGE: [type] -->` at line [N] uses an unsupported type.
Allowed: quote, diagram, body.
```

Do not move on. The marker check is a precondition for the image presence check downstream.

### 4. Run the SEO gate

Invoke the `seo-optimisation` skill against the article. The skill produces a full audit report ending in either:

```
**GATE: PASS** ✓ — zero critical issues. Article cleared for `/publish-gate`.
```

or

```
**GATE: FAIL — fix [N] critical issues before publishing.**
- [headline of each critical issue]
```

Parse the final `GATE:` line. The verdict is binary.

- **GATE: PASS** → continue to step 5.
- **GATE: FAIL** → print the audit's critical-issues list and stop. Tell the user:

  > SEO gate failed with [N] critical issue(s). Fix the issues above (either directly or by re-running `/seo-optimisation` for guidance) and re-run `/publish-gate` when clear.

  Do not move on to image checks. Do not move the folder. The SEO gate is the contract — if it fails, nothing else runs.

### 5. Image presence, alt text, and attribution check

Required assets are determined by the body image markers captured in Step 3. The slot types tell you which files must exist in `images/`:

| Marker type | Required filename pattern |
|---|---|
| (always — hero/featured) | `[topic-slug]-featured.jpg` |
| `quote` | `[topic-slug]-quote.jpg` |
| `diagram` | `[topic-slug]-diagram.jpg` |
| `body` | `[topic-slug]-body-featured.jpg` |
| (always — stock licensing) | `attributions.csv` |

If both slot markers are the same type (e.g. two `body` markers), the second slot's filename gets a `-2` suffix (e.g. `[topic-slug]-body-featured-2.jpg`). The user picks the filename convention when generating; check whichever names appear in `image-plan.md`'s slot sections.

**5a. Presence.** For each required asset, confirm the file exists in `images/`. List any missing files. If any required asset is missing, stop with:

> Required image asset(s) missing in `images/`. Either generate them per `image-plan.md`, or edit the body marker to drop the slot, then re-run `/publish-gate`.

**5b. Alt text populated.** Open `image-plan.md` and for each slot section (Hero + each body slot), find the alt-text field. Fail if any required slot has an empty alt-text field or contains the literal placeholder text `[alt text for chosen photo]` / `[suggested alt text]`.

If any slot has missing or placeholder alt text, stop with:

```
GATE: FAIL — alt text missing or unwritten for [N] slot(s).

  - Hero: alt text is empty
  - Slot 1 (quote): alt text still reads "[alt text for chosen photo]"

Edit image-plan.md to write real alt text for each slot, then re-run.
```

**5c. Photographer attribution.** Open `images/attributions.csv` and read its rows. For every published image filename in `images/` (top-level `.jpg` files only, not the `hero/` or `body/` subfolders of raw candidates), confirm there's a matching attribution row.

The pull-quote, diagram, and treated-stock outputs don't always need attribution rows (the generated graphics aren't licensed photos), but the underlying stock photos used in the hero and body treatments do. Cross-reference filenames: a `[slug]-featured.jpg` was treated from a stock photo whose attribution must appear; a `[slug]-quote.jpg` is a pure typography card and needs no attribution.

If any stock-derived image lacks a matching attribution row, stop with:

```
GATE: FAIL — photographer attribution missing for [N] image(s).

  - [slug]-featured.jpg — no attribution row in attributions.csv
  - [slug]-body-featured.jpg — no attribution row in attributions.csv

Add the missing rows to attributions.csv (photographer name, source platform, photo URL), then re-run.
```

Do not move the folder. Do not flip `stage: published`.

### 6. Image file-size check

For every `.jpg` in `images/` (top level, not subfolders — the `hero/` and `body/` subfolders contain the raw stock candidates and don't get published), read the byte size. Anything over 512000 bytes (500KB) fails the check.

Report per-file:

```
images/[topic-slug]-featured.jpg — 287KB ✓
images/[topic-slug]-quote.jpg — 156KB ✓
images/[topic-slug]-diagram.jpg — 612KB ✗ (over 500KB ceiling)
```

If any file is over the ceiling, stop with:

> Image file size(s) over 500KB. Re-export the listed files at lower quality (the JPEG compress block at the bottom of `image-plan.md` is the usual fix), then re-run `/publish-gate`.

Do not move the folder.

### 7. External link health check (advisory)

This check runs after all blocking checks have passed. It does NOT fail the gate. It warns the user about external links that look broken so they can fix them before publishing, while accepting that some servers flake or block bot HEAD requests.

For every external markdown link in the article body (any `[text](https://...)` where the host is not `peakbodycoach.co.uk`), run a HEAD request with a 5-second timeout:

```bash
curl -sI --max-time 5 -o /dev/null -w "%{http_code}" "[URL]"
```

Collect results. For each link, classify:

- `2xx` — OK
- `3xx` — OK (redirect; the eventual target is likely fine)
- `404` — WARN (likely broken)
- `403`, `429`, `503` — NOTE (server may be blocking bot requests; manual check recommended)
- Timeout or connection error — NOTE (server slow or down; manual check recommended)

Report:

```
External link health (advisory):
  ✓ 12 links OK (2xx or 3xx)
  ⚠ 1 link returned 404:
      - "Hamilton-Reeves 2010 meta-analysis" → https://example.com/study  (line 31)
  ℹ 2 links could not be verified:
      - "Wegovy SmPC" → https://www.medicines.org.uk/...  (403 — likely bot-blocking, check manually)
      - "Lowe et al. 2020" → https://jamanetwork.com/...  (timeout, try again later)
```

Continue to Step 8 regardless. The user decides whether to fix warnings before publishing.

### 8. Print the WordPress upload checklist

Once the SEO gate has passed and all image checks are clean, print:

```
READY TO PUBLISH ✓

Article: [Article title]
Slug: [topic-slug]
Category: [category]
Meta description: [meta_description from frontmatter]
Target keyword: [target_keyword from frontmatter]
Word count: [approximate]

Images cleared:
  - images/[topic-slug]-featured.jpg ([size]KB)
  - images/[topic-slug]-quote.jpg ([size]KB)         (if present)
  - images/[topic-slug]-diagram.jpg ([size]KB)       (if present)
  - images/[topic-slug]-body-featured.jpg ([size]KB) (if present)

WordPress upload checklist:
  [ ] Create new post, paste article body from [topic-slug].md
  [ ] Set title, slug, category as above
  [ ] Paste meta description into Yoast
  [ ] Set target keyword as Yoast focus keyword
  [ ] Upload featured image; set as Featured Image in WordPress
  [ ] Upload body images, insert at the `<!-- IMAGE: ... -->` marker positions in the body
  [ ] Copy photographer attribution lines from images/attributions.csv to the article footer
  [ ] Publish

Once the post is live, confirm here and I'll archive the folder.
```

Then ask:

> Has the post gone live? Reply `yes` to archive the article folder, or `no` to leave it in Draft for now.

### 9. Archive on confirmation

On `yes`:

1. **Update the article's frontmatter** in place:
   - Set `stage: published`
   - Add `published_date: YYYY-MM-DD` (today's date in ISO format)
2. **Clean up candidate images and intermediate files.** Before archiving, delete the raw stock candidates and any leftover PNGs so only the final compressed JPEGs survive into `3 - PostedArchive/`. Run from PowerShell:

   ```powershell
   # Remove raw candidate subfolders
   Remove-Item -Recurse -Force "C:/Users/Tom/Documents/Home Vault/2 - Business/Content/Blog/1 - Draft/[topic-slug]/images/hero" -ErrorAction SilentlyContinue
   Remove-Item -Recurse -Force "C:/Users/Tom/Documents/Home Vault/2 - Business/Content/Blog/1 - Draft/[topic-slug]/images/body" -ErrorAction SilentlyContinue
   # Remove any remaining intermediate PNGs
   Remove-Item -Force "C:/Users/Tom/Documents/Home Vault/2 - Business/Content/Blog/1 - Draft/[topic-slug]/images/*.png" -ErrorAction SilentlyContinue
   ```

   After running, the `images/` folder should contain only the final `.jpg` files and `attributions.csv`. If it contains anything unexpected, report it to the user before continuing.

3. **Move the entire article folder** from `Blog/1 - Draft/[topic-slug]/` to `Blog/3 - PostedArchive/[topic-slug]/`. PowerShell:

   ```powershell
   Move-Item `
     "C:/Users/Tom/Documents/Home Vault/2 - Business/Content/Blog/1 - Draft/[topic-slug]" `
     "C:/Users/Tom/Documents/Home Vault/2 - Business/Content/Blog/3 - PostedArchive/[topic-slug]"
   ```

4. **Confirm the move** by listing the destination:

   ```powershell
   Get-ChildItem "C:/Users/Tom/Documents/Home Vault/2 - Business/Content/Blog/3 - PostedArchive/[topic-slug]/" |
     Select-Object Name |
     Format-Table -AutoSize
   ```

5. **Report back:**

   > Archived `[topic-slug]` to `Blog/3 - PostedArchive/`. Run `/pipeline-status` whenever you next want to see the updated published-count milestones — the archive move alone updates the count, nothing else to flip.

On `no`: leave the folder untouched. Tell the user:

> Folder left in `Blog/1 - Draft/[topic-slug]/`. Re-run `/publish-gate [topic-slug]` after the post is live.

That ends the flow.

---

## Notes

- The published-count milestone state (`Content/_pipeline-milestones.json`) is read by `/pipeline-status` directly off the archive folder via `count_published_archive()`. This command doesn't touch that JSON file — the archive move plus `stage: published` is the only signal needed.
- If the user passes a slug that doesn't resolve to an existing folder, stop and report the path you tried. Don't guess at alternatives.
- If the article is already in `Blog/3 - PostedArchive/`, tell the user it's already published and stop. Don't re-run any checks.
- This command does not push to WordPress, Drive, Notion, or any other external system. It's a local validation + filesystem move. The actual WordPress upload is manual.
- If the SEO audit takes a long path (web search, archive scan), don't paraphrase the result — print the full audit so the user can see what passed and what's flagged, then act on the final `GATE:` line.
