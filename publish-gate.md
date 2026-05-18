# /publish-gate

Final pre-publish check for a Peak Body Coach blog article. Runs the SEO audit, validates that the required image assets exist and are under the 500KB ceiling, prints a WordPress upload checklist, and on confirmation moves the article subfolder from `Blog/1 - Draft/` to `Blog/3 - PostedArchive/` with `stage: published` set.

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
- **Image plan** — read `image-plan.md` in the same folder if present. Look for which Candidates were marked as the picked slots (typically A + C + D, or A + B + C, etc.). If `image-plan.md` is missing, that's not a hard stop — fall back to checking only the hero asset (always required) and warn the user that the plan is missing so they can verify what's intended.

Also read the article's frontmatter and confirm:

- `type: blog`
- `topic:` matches the slug
- `stage:` is `ready` (or `seo-audit`). If `stage:` is `drafting`, warn the user that the article hasn't been through the SEO audit yet and ask whether to proceed anyway.
- `meta_description:`, `category:`, `target_keyword:` are all present. If any are missing, stop and tell the user to run `/seo-optimisation` first — these are required for WordPress.

### 2. Run the SEO gate

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

- **GATE: PASS** → continue to step 3.
- **GATE: FAIL** → print the audit's critical-issues list and stop. Tell the user:

  > SEO gate failed with [N] critical issue(s). Fix the issues above (either directly or by re-running `/seo-optimisation` for guidance) and re-run `/publish-gate` when clear.

  Do not move on to image checks. Do not move the folder. The SEO gate is the contract — if it fails, nothing else runs.

### 3. Image presence check

Walk `images/` in the article folder and confirm the assets that the plan expects exist:

| Slot | Required filename pattern | Required? |
|---|---|---|
| Hero | `[topic-slug]-featured.jpg` | Always |
| Pull-quote | `[topic-slug]-quote.jpg` | If Candidate C was picked in the image plan |
| Diagram | `[topic-slug]-diagram.jpg` | If Candidate D was picked in the image plan |
| Body | `[topic-slug]-body-featured.jpg` | If Candidate B was picked in the image plan |
| Attributions | `attributions.csv` | Always (stock licensing) |

If `image-plan.md` is missing, only the hero and attributions checks are enforced. Warn the user that optional slots can't be validated without the plan.

For each missing required asset, list it in the output. If any required asset is missing, stop with:

> Required image asset(s) missing in `images/`. Either generate them per `image-plan.md`, or update the plan to drop the slot, then re-run `/publish-gate`.

Do not move the folder. Do not flip `stage: published`.

### 4. Image file-size check

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

### 5. Print the WordPress upload checklist

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
  [ ] Paste meta description into Yoast / Rank Math
  [ ] Upload featured image; set as Featured Image in WordPress
  [ ] Upload remaining images, insert at appropriate positions in the body
  [ ] Copy photographer attribution lines from images/attributions.csv to the article footer
  [ ] Add internal links suggested in the SEO audit's back-link section
  [ ] Publish

Once the post is live, confirm here and I'll archive the folder.
```

Then ask:

> Has the post gone live? Reply `yes` to archive the article folder, or `no` to leave it in Draft for now.

### 6. Archive on confirmation

On `yes`:

1. **Update the article's frontmatter** in place:
   - Set `stage: published`
   - Add `published_date: YYYY-MM-DD` (today's date in ISO format)
2. **Move the entire article folder** from `Blog/1 - Draft/[topic-slug]/` to `Blog/3 - PostedArchive/[topic-slug]/`. PowerShell:

   ```powershell
   Move-Item `
     "C:/Users/Tom/Documents/Home Vault/2 - Business/Content/Blog/1 - Draft/[topic-slug]" `
     "C:/Users/Tom/Documents/Home Vault/2 - Business/Content/Blog/3 - PostedArchive/[topic-slug]"
   ```

3. **Confirm the move** by listing the destination:

   ```powershell
   Get-ChildItem "C:/Users/Tom/Documents/Home Vault/2 - Business/Content/Blog/3 - PostedArchive/[topic-slug]/" |
     Select-Object Name |
     Format-Table -AutoSize
   ```

4. **Report back:**

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
