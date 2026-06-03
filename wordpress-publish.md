# /wordpress-publish

Push a Peak Body Coach blog article from the vault to WordPress via the REST API. Handles category discover-or-create, image uploads (featured + body images at marker positions), CTA append, photographer attribution, and post creation. On success, writes `published_url`, `wp_post_id`, and `published_date` back to the article's frontmatter.

By default the article is pushed as **scheduled** to the next free Monday in the blog cadence (computed from existing WP scheduled + recently published posts, plus any vault drafts that already have a `scheduled_date`). Override with `--publish` to go live immediately or `--schedule YYYY-MM-DD` to pick a specific date.

If the article's frontmatter already contains a `wp_post_id`, the command re-publishes (PATCHes) the existing post instead of creating a duplicate.

This command runs AFTER `/publish-gate` has cleared the article. The gate is the contract; this command is the upload.

## Usage

```
/wordpress-publish [topic-slug]                   # scheduled to next Monday slot
/wordpress-publish [topic-slug] --publish         # live immediately
/wordpress-publish [topic-slug] --schedule 2026-06-15
/wordpress-publish path/to/article.md
```

## Arguments

- `$ARGUMENTS` — either the article's topic slug or a path to the article markdown.
- `--publish` (optional) — push live immediately, no cadence check.
- `--schedule YYYY-MM-DD` (optional) — manual override; schedule the post for this date at 9am UTC.

Default behaviour (no flags): the slash command computes the next free Monday slot, presents it as the default in Step 2, and pushes the article as scheduled. The cadence is queue-aware: it counts both WP-side activity (scheduled future posts + posts published within the last 14 days) and any vault drafts that already have `scheduled_date` set, so the next slot is always at least 7 days after the most recent taken slot.

## Prerequisites

Before this command can run, the following must exist:

1. **`~/.claude/wordpress.json`** — auth config. Format:

   ```json
   {
     "site_url": "https://peakbodycoach.co.uk",
     "username": "<wp-admin-username>",
     "app_password": "<wp-application-password>"
   }
   ```

   Create the Application Password in WP admin under Users → Profile → Application Passwords. Name it `claude-code` or similar. Paste the generated password into the JSON file. The file is gitignored.

2. **`~/.claude/wordpress-cta.html`** (optional) — in-body CTA HTML snippet appended to every published post. **Default: empty.** The theme's `single.php` already auto-appends two CTAs (sidebar "Work together" block + bottom INK INTERLUDE section), so the script appends nothing by default. Create this file only if you want a third, in-body, article-specific CTA on top of the theme's.

3. **Article must have passed `/publish-gate`.** Frontmatter complete, two image markers in body, all assets in place with alt text. The push assumes the gate's checks have been done.

## Steps

### 1. Resolve the article

From `$ARGUMENTS`, work out the article path. Slug resolves to `Blog/1 - Draft/[slug]/[slug].md`.

### 2. Resolve the target date and confirm

Decide what date to schedule for:

1. **If `--publish` was passed:** status is `publish`. Skip the slot-info call; go straight to confirmation.
2. **If `--schedule YYYY-MM-DD` was passed:** status is `scheduled`, date is the user's. Still call `--show-slot-info` (see step 3) so the adjacency warning fires against the manual override too.
3. **Otherwise (default scheduled push):**
   - Run `python $HOME/.claude/commands/wordpress_publish.py --show-slot-info` and parse the JSON. Shape:
     ```json
     {
       "next_slot": "2026-06-08",
       "adjacent": {
         "prior": {"date": "2026-06-01", "category": "training", "title": "...", "slug": "..."},
         "next": null
       }
     }
     ```
   - If the article's frontmatter already has a `scheduled_date`, use that as the proposed slot (override `next_slot`).
   - Otherwise, use `next_slot`.

**Topic-adjacency check.** Read the article's frontmatter `category:` and slugify (lowercase, spaces to hyphens). Compare to `adjacent.prior.category` and `adjacent.next.category`. If either matches, prepend a warning line to the summary:

```
⚠ Topic stack: 2026-06-01 (exercise-order-hypertrophy-myth) is also Training.
```

If both sides match, list both warnings. If neither matches, omit the warning entirely.

Print the summary:

```
[⚠ warning line(s) if any]

About to push to WordPress:
  Article: [title]
  Slug: [slug]
  Category: [category]
  Status: [publish / scheduled YYYY-MM-DD]
  Re-publish: [yes (wp_post_id=NNNN) / no]
  Images to upload: featured + [N body images]
```

Ask (three-way prompt):

> Proceed? Reply `yes` to schedule for [proposed-date], `now` to publish live, or a date `YYYY-MM-DD` to override.

Interpret the reply:
- `yes` → use the proposed date as `--schedule [proposed-date]`.
- `now` → use `--publish`.
- A `YYYY-MM-DD` string → use `--schedule [that-date]`. Validate it's a real date >= today; reject otherwise. Re-run the adjacency check against the override date before re-confirming.
- Anything else, or explicit `no` → abort. If the user wants a queue-wide reshuffle to fix topic stacking, run `/content-schedule` instead.

### 3. Invoke the publish script

Run from the article folder or anywhere:

```bash
python $HOME/.claude/commands/wordpress_publish.py [slug] [--publish | --schedule YYYY-MM-DD]
```

Stream the script's stderr (progress logs) to the user. Capture stdout — that's the WP post URL.

### 4. Report and hand off

On success, print:

```
✓ Pushed to WordPress.
  WP post: [post URL]
  Status: [publish / scheduled]
  Re-publish: [yes / no]

Frontmatter updated:
  published_url: [URL]
  wp_post_id: [N]
  published_date: [YYYY-MM-DD]
```

Then **auto-invoke `/publish-gate [slug]`** to archive the folder. The post is committed (live or scheduled-and-locked in WP), so the vault folder's work is done.

For re-publish (the post already had `wp_post_id`), the folder is likely already archived from the original push. The gate is a no-op in that case; no harm in invoking it. If the folder is still in `1 - Draft/` for some reason, the gate's archive step moves it.

### 5. Handle errors

If the script exits non-zero, print the script's stderr and stop. Common causes:

- **Missing config** — `~/.claude/wordpress.json` doesn't exist. Create it per Prerequisites.
- **401 Unauthorized** — App password wrong, or the user account doesn't have publish permissions. Verify the app password in WP admin.
- **404 on category create** — REST permissions issue. Check that the user role can create terms.
- **413 Payload Too Large on media upload** — server upload limit. Either reduce image size or raise the limit in WP/server config.
- **Missing image file** — confirm `images/[slug]-featured.jpg` and the slot images exist (gate should have caught this).
- **Yoast meta not written warning** — meta fields didn't appear in the response. See Notes below; may need a register_meta snippet.

## Notes

### Cadence (default scheduled push)

Blog cadence is one post per week on Mondays. Slot computation lives in `~/.claude/skills/content-schedule/cadence.py` (shared with `/content-schedule`). The publisher fetches:

- WP posts with `status=future` (any scheduled future post)
- WP posts with `status=publish` and `post_date >= today - 14 days`
- Vault drafts under `Blog/` with `scheduled_date >= today` in frontmatter

It unions these into a "taken" set, then picks the first Monday on or after `max(today, last-taken + 7d)` that isn't itself in the set. If the article being pushed already has `scheduled_date` in its frontmatter (because `/content-schedule` was run upstream), that date is the default instead of a fresh computation.

The user can always override in Step 2 by typing a `YYYY-MM-DD` date or `now`.

To inspect the next computed slot without pushing: `python $HOME/.claude/commands/wordpress_publish.py --show-next-slot`. Prints the date and exits. For the richer JSON form (next slot plus adjacent post categories for the topic-stack check), use `--show-slot-info` instead.

### Topic-adjacency warning

The cadence math is date-only — it doesn't know what topics are scheduled around the proposed slot. To stop two same-category posts landing on back-to-back Mondays, Step 2 above also calls `--show-slot-info`, looks at the prior and next taken slots (immediately ±1, no broader window), and surfaces a warning when either neighbour shares a category with the article being pushed.

The warning is informational, not blocking. User options at the confirmation prompt:
- Accept the warning and push to the proposed slot anyway (often fine — adjacency isn't always a problem).
- Override the date to a slot that breaks the stack.
- Abort and run `/content-schedule` for a queue-wide topic-aware reshuffle.

Adjacency uses the slugified category (e.g. `"Body Composition"` → `body-composition`). WP-side categories are resolved via the `~/.claude/wordpress-cache.json` slug→id map; unknown IDs trigger a fresh `/categories/{id}` GET and are cached for next time.

### Yoast meta fields

The script tries to write `_yoast_wpseo_metadesc` and `_yoast_wpseo_focuskw` via the post's `meta` field. This works only if those keys are registered with `show_in_rest: true`. Recent Yoast versions register them; older versions do not.

If the script warns that meta fields weren't written, drop this snippet into the child theme's `functions.php`:

```php
add_action('init', function() {
    foreach (['_yoast_wpseo_metadesc', '_yoast_wpseo_focuskw'] as $key) {
        register_post_meta('post', $key, [
            'show_in_rest' => true,
            'single' => true,
            'type' => 'string',
            'auth_callback' => function() { return current_user_can('edit_posts'); },
        ]);
    }
});
```

After the snippet is live, re-run `/wordpress-publish` and the warning should go away.

### Re-publish flow

If frontmatter has `wp_post_id`, the script PATCHes the existing post instead of creating a new one. Updates: title, content (rebuilt from current markdown), excerpt, featured_media, categories, meta. Body images are re-uploaded on every push (v1 limitation; produces duplicate media library entries for the same image across pushes — acceptable for now, optimise later if it becomes a problem).

To force a fresh push (new WP post), remove `wp_post_id` from the article's frontmatter.

### CTA template

The theme's `single.php` auto-renders two CTAs on every blog post (a sidebar "Work together" block and the bottom INK INTERLUDE section with discovery-call buttons). The script does NOT append a CTA by default to avoid duplication. If `~/.claude/wordpress-cta.html` exists and is non-empty, the script appends its contents as an extra in-body CTA — only useful for article-specific overrides. Otherwise, post body ends at the last paragraph of the article (plus photographer attribution if applicable), and the theme handles the rest.

### Markdown conversion

Uses `markdown-it-py` with the `commonmark` preset plus the `table` extension. Inline HTML in the markdown is preserved (set `html=True`). Output is raw HTML sent in the `content` field; WP renders it inside a Classic block when opened in the block editor.

### Cache

Reads and writes `~/.claude/wordpress-cache.json` for category slug→ID lookups. Shared with `/resolve-internal-links` (which reads the published-posts list).

### Dependencies

Script requires Python 3.8+ and these packages: `requests`, `pyyaml`, `markdown-it-py`. Install with:

```bash
pip install requests pyyaml markdown-it-py
```

If any are missing, the script exits with a clear install command.
