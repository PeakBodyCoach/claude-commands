# /blog-images

Source images and identify candidate assets for a Peak Body Coach blog article. Reads the article, downloads stock photo candidates for hero and body slots, identifies the sharpest pull-quote sentence, recommends a diagram layout, and produces an `image-plan.md` with ready-to-run commands for the downstream image skills.

## Usage

```
/blog-images path/to/article.md
```

## Arguments

`$ARGUMENTS` — path to the blog article (markdown, text, or any readable file)

## Configuration

- **Stock image script location:** `C:/Users/Tom/projects/stock-images/download_images.py`
- **Vault root:** `C:/Users/Tom/Documents/Home Vault/2 - Business/Content/`
- **Output root (per article):** `Blog/1 - Draft/[topic-slug]/images/` — all generated assets land here, alongside the article
- **`image-plan.md` location:** `Blog/1 - Draft/[topic-slug]/image-plan.md` — article subfolder, NOT inside `images/`
- **Per-query image count:** 3

## Required article location

This command requires the new per-article subfolder convention:

```
Blog/1 - Draft/[topic-slug]/
    [topic-slug].md       <- the article
    image-plan.md         <- written by this command
    images/               <- written by this command
        hero/
        body/
        attributions.csv
        [slug]-featured.jpg
        [slug]-quote.jpg
        [slug]-diagram.jpg
        ...
```

Before running anything else, check the path the user passed:

1. If the article is at `Blog/1 - Draft/[topic-slug]/[topic-slug].md` (filename matches parent folder, parent of parent is `1 - Draft`), proceed. The slug is the parent folder name.
2. If the article is at `Blog/1 - Draft/[any-name].md` (root of `1 - Draft/`, no per-article subfolder) OR inside a topic-bucket folder like `Blog/1 - Draft/blog-draft-training/[any-name].md`, **stop with this message**:

   > This article isn't in the new per-article subfolder convention. `/blog-images` needs `Blog/1 - Draft/[topic-slug]/[topic-slug].md`. Either move the article into its own slug-named subfolder first, or — if this is a legacy draft you don't want to migrate — generate images by hand using `featured-image`, `pull-quote`, and `infographic-prompt` directly.

   Existing legacy drafts are deliberately not migrated by this command. The new structure applies to new articles only.

## What this command produces

Every blog post ships with three image assets: a hero (featured image) and two body images. The hero is always sourced as stock. The two body images are marker-driven: the article body contains exactly 2 typed HTML-comment markers, and this command produces content for whichever slot types the markers call for.

| Slot | Source | Marker (in body) | Produced by |
|---|---|---|---|
| Hero | Always — featured image | None (implicit, top of post) | `/blog-images` sources, `featured-image` skill treats |
| Body slot 1 | Marker-driven | `<!-- IMAGE: quote -->` or `<!-- IMAGE: diagram -->` or `<!-- IMAGE: body -->` | Per type — see slot rules below |
| Body slot 2 | Marker-driven | Same |

**Body slot type → producer:**

| Marker type | Producer skill | Stock needed? |
|---|---|---|
| `quote` | `pull-quote` | No (sentence identified from body) |
| `diagram` | `infographic-prompt` (Gemini) or `diagram-prompt` (NotebookLM) | No (layout proposed from body content) |
| `body` | `featured-image` skill | Yes (3 stock candidates downloaded) |

**Marker authority.** The markers in the body are authoritative on which slot types to produce. If the user wants to swap a slot type (e.g. diagram fit is weak, prefer body stock instead), they edit the marker in the body and re-run `/blog-images`. This command does not propose unmarked candidate types as alternatives.

## Steps

### 1. Read and analyse the article

Open the file at `$ARGUMENTS` and extract:

- **Title** — first H1, or filename if there's no H1
- **Slug** — the parent folder name. By convention this matches the article filename stem (e.g. `glp1-muscle-loss/glp1-muscle-loss.md` → slug `glp1-muscle-loss`). The parent folder is authoritative — if filename and folder name disagree, trust the folder
- **Article folder** — the parent folder, full path. All subsequent commands and paths use this as the working directory
- **Topic** — what is this article actually about, in one sentence
- **Tone** — serious explainer, sardonic takedown, how-to, myth-buster
- **Concrete imagery** — note any specific scenes, objects, or visual concepts the article references
- **Category** — pick one of: Nutrition, Training, Industry, Behaviour, Body Composition, Coaching. Default to closest match if uncertain
- **Headline candidate** — propose a featured-image-ready headline (7–10 words, makes a specific claim). Often this is the article H1, but the H1 may be too long
- **Subhead candidate** — one sentence in sentence case, under ~12 words, complementing the headline
- **SEO keywords** — extract 3–5 search keywords for the article. These get embedded into PNG metadata for image SEO. Rules:
  - The first keyword is typically the slug itself in human-readable form (e.g. "mounjaro muscle loss")
  - Other keywords should be search terms a reader might use to find this content
  - Mix of broad ("glp-1", "weight loss") and specific ("muscle preservation", "protein on glp-1")
  - Lowercase, comma-separated when emitted

### 1a. Read body image markers

Walk the body and find every `<!-- IMAGE: type -->` HTML comment marker. Capture in document order as **Slot 1** and **Slot 2**, recording each marker's type (`quote`, `diagram`, or `body`) and its position (line number, surrounding context).

**Validation — stop the command if any of these fail:**

- Marker count must be exactly 2. If 0 or 1 markers, stop with:

  > Body has [N] image marker(s) but exactly 2 are required. See `article-structure.md` under Image Markers in Body for the spec, or run the article through `blog-writing` again to have the markers inserted.

  If 3+ markers, stop with:

  > Body has [N] image markers but exactly 2 are required. Remove the surplus marker(s) per the standard PBC assembly (hero + 2 body images).

- Each marker's type must be one of `quote`, `diagram`, or `body`. If an unknown type is found, stop with:

  > Marker `<!-- IMAGE: [type] -->` at line [N] uses an unsupported type. Allowed: `quote`, `diagram`, `body`. Edit the marker and re-run.

Once validation passes, you know which slot types to produce content for in the following steps. From this point on, only do work for the slot types the markers call for.

### 2. Identify the sharpest pull-quote candidate

**Skip this step if no marker has type `quote`.**

Read the article and find the single best candidate sentence. Rules:

- Complete sentence, 5–30 words
- Makes a specific claim, not a setup or transition
- Works without surrounding context (no "this means", "as we saw above")
- Contains at least one concrete noun or number
- Avoid sentences starting with "If", "When", "While" — usually conditional setups
- The most quotable line is often a tight assertion, not the most "important" sentence

The candidate sentence should be near the quote marker's position in body. If the sentence immediately before the marker doesn't meet the rules, look at the surrounding two or three paragraphs for the best match — the writer placed the marker there for a reason, even if the strongest sentence isn't the one directly above.

If no sentence in the article meets these rules well, return the closest match with a note flagging it. The user decides whether to use it or swap the marker for `body`.

### 3. Propose a diagram layout and draft the content

**Skip this step if no marker has type `diagram`.**

Match the article's structure to one of the eleven `infographic-prompt` layouts. Check them in the order listed — the first strong match wins.

| Priority | Layout | Use when the article contains... |
|---|---|---|
| 1 | `single-stat-callout` | One key statistic with supporting context (e.g. "19% of people maintain goals past 8 weeks"). Most visually strong layout — reach for this first whenever a single number is the hero of the article. |
| 2 | `spectrum` | A dose-response or optimal-range argument (e.g. "how much protein", "how much volume", "sleep duration"). The content sits on a continuous scale with a meaningful sweet spot. |
| 3 | `mechanism` | A cause-and-effect chain explaining HOW something works (e.g. "why GLP-1s cause muscle loss", "how MPS works", "the cortisol-sleep cycle"). Order is causal, not just sequential. |
| 4 | `evidence-callout` | A bold research claim supported by 3-4 evidence points, where the finding is a sentence rather than a number (e.g. "protein distribution matters as much as total intake"). |
| 5 | `action-plan` | A sequenced set of 3-6 imperative steps the reader should take — instructional "how to" content. Items are things to DO, in order. |
| 6 | `hero-breakdown` | A composition split or allocation with percentages (e.g. "where should your protein come from", "how to split your training week"). |
| 7 | `priority-stack` | A ranked hierarchy where the order signals importance — "do this first, not last" (e.g. nutrition hierarchy, training priority). Items are not equally weighted. |
| 8 | `acronym-framework` | An acronym to unpack — established (SMART, FITT) or invented PBC framework. |
| 9 | `two-column-comparison` | The article explicitly structures its argument as parallel opposing pairs — 4-7 named left/right pairs already present in the text (e.g. a dedicated myth-vs-fact section with multiple paired items). Do NOT use just because the article mentions misconceptions or contrasts ideas in passing. |
| 10 | `listicle` | A list of principles, observations, or aphorisms — things the reader should THINK or KNOW, not do. Items are equally weighted, not ranked, not imperatives. |
| 11 | `three-elements` | Exactly three single-word pillar concepts (e.g. "lift, eat, sleep"). Weakest layout — only use if the content genuinely reduces to three punchy single words with no further structure needed. |

Using the priority table, identify the **3-4 most plausible layouts** for this article. For each, write a one-sentence gist describing what the infographic would show. Mark your recommendation.

**Example output format:**
- **mechanism** (recommended): restriction → forbidden fruit effect → binge → tighter rules, 4-node left-to-right chain
- **evidence-callout**: hero claim "THE RESTRICTION WAS PRODUCING THE BINGE ALL ALONG" + 3 Polivy/Herman/Mann research points
- **listicle**: 5 signs you're in the binge-restrict loop, on a cream paper card
- **two-column-comparison** (weak fit): discipline camp vs intuitive eating camp, 5 paired rows

Present the gists and ask Tom which layout to generate. **Wait for his response before proceeding.**

Once Tom confirms a layout:

1. Read `C:/Users/Tom/.claude/skills/infographic-prompt/layouts/[chosen-layout].json`
2. Fill in all content placeholders from the article. Voice rules apply: British spelling, no em dashes, ALL CAPS for titles and kicker pills, sentence case for body items and taglines. Do not leave any placeholder unfilled.
3. Write the filled `content` block (just the content object, not the full layout JSON) to `images/_diagram-content.json` inside the article's images folder.
4. Run the generator:

```powershell
cd C:/Users/Tom/projects/stock-images
python generate_infographic.py `
  --layout [chosen-layout] `
  --content "C:/Users/Tom/Documents/Home Vault/2 - Business/Content/Blog/1 - Draft/[topic-slug]/images/_diagram-content.json" `
  --output "C:/Users/Tom/Documents/Home Vault/2 - Business/Content/Blog/1 - Draft/[topic-slug]/images/[topic-slug]-diagram.png"
```

5. Report the result: image size if successful, or the error message if it failed.

If the script fails or Tom wants a fallback, the NotebookLM D2 prompt in `image-plan.md` is always available as an alternative.

### 4. Generate hero and body search queries

**Hero queries: always generate.** **Body queries: only if a marker has type `body`.**

For each slot you need queries for, write **3 candidate search queries**. Rules:

- 2–4 words each
- Concrete nouns and visual concepts, not abstract ideas
- Match the article's tone — Peak Body Coach is serious and evidence-based, so avoid Instagram-influencer or supplement-ad imagery
- Vary the angles so the candidate set has range

**Hero** captures the article's overall topic. Editorial, magazine-quality. Lead-image energy.

**Body** illustrates a specific section, concept, or counter-point. Should feel different from the hero — if hero is wide and atmospheric, body is closer and specific. If hero is a person, body is an object, and vice versa. The body slot's marker position tells you which section it illustrates; pick queries that serve that section's content, not the article overall.

**Avoid duplication** (only relevant when both hero and body are stock). Hero and body queries must not produce visually similar images.

**Worked example.** Article: "Why GLP-1s Cause Muscle Loss And What To Do About It"
- Hero queries: `injection pen close up`, `prescription medication vial`, `weight loss medication`
- Body queries (if `body` marker exists): `dumbbell rack gym`, `bathroom scale feet`, `elderly person walking`

### 5. Build the queries config

Write a temporary config to `C:/Users/Tom/projects/stock-images/_blog-config.json`. Always include the `hero` key. Include the `body` key only if a marker has type `body`.

If both slots are needed:

```json
{
  "hero": {
    "sources": ["unsplash", "pexels"],
    "queries": ["query1", "query2", "query3"]
  },
  "body": {
    "sources": ["unsplash", "pexels"],
    "queries": ["query1", "query2", "query3"]
  }
}
```

If only hero is needed (markers are quote + diagram, or quote + quote, etc.):

```json
{
  "hero": {
    "sources": ["unsplash", "pexels"],
    "queries": ["query1", "query2", "query3"]
  }
}
```

### 6. Run the downloader

The downloader's `--output` arg now points directly at the article's `images/` subfolder inside the vault. The downloader creates the folder if it doesn't exist.

```powershell
cd C:/Users/Tom/projects/stock-images
python download_images.py `
  --config _blog-config.json `
  --output "C:/Users/Tom/Documents/Home Vault/2 - Business/Content/Blog/1 - Draft/[topic-slug]/images" `
  --per-query 3
```

Replace `[topic-slug]` with the actual slug from step 1.

This produces:

```
Blog/1 - Draft/[topic-slug]/images/
    hero/
        query1-01.jpg ... query1-03.jpg
        ...
    body/
        ...
    attributions.csv
```

### 7. Write the image asset plan

Create `image-plan.md` at the **article subfolder**, NOT inside `images/`:

`C:/Users/Tom/Documents/Home Vault/2 - Business/Content/Blog/1 - Draft/[topic-slug]/image-plan.md`

Use this exact structure:

```markdown
# Image asset plan: [Article title]

Article folder: `C:/Users/Tom/Documents/Home Vault/2 - Business/Content/Blog/1 - Draft/[topic-slug]/`
Article file: `[topic-slug].md`
Slug: [topic-slug]
Category: [chosen category]
Topic: [one-sentence summary]

---

## How to use this plan

All commands below assume you're in the article folder. Set that first:

```powershell
cd "C:/Users/Tom/Documents/Home Vault/2 - Business/Content/Blog/1 - Draft/[topic-slug]"
```

Every article ships with three images: a hero (featured) plus two body images. The hero is always present. The two body slots are marker-driven — `/blog-images` read the two `<!-- IMAGE: type -->` markers in the article body and only the matching candidate sections are included below.

## Slot map (from body markers)

- **Hero** — always required (featured image, no body marker)
- **Slot 1** — type: `[type from marker 1]`, marker at line [N]
- **Slot 2** — type: `[type from marker 2]`, marker at line [N]

If a slot's fit feels weak after reviewing this plan, edit the marker in the article body (change `quote` → `body`, `diagram` → `body`, etc.) and re-run `/blog-images`. Markers are authoritative.

Each section below has a ready-to-run command. Copy, edit if needed, run from the article folder.

---

## Hero (always required, featured image)

**Include this section unconditionally.** Hero is the featured image; it has no body marker and is always present.

**Suggested treatment args:**
- headline: "[headline candidate, ALL CAPS]"
- subhead: "[subhead candidate, sentence case]"
- category: "[category]"
- surface: ink (default)

**Stock candidates** (in `images/hero/`):

### Query: [query 1]
Rationale: [why this query suits the hero slot]

- **query1-01.jpg** — alt: "[suggested alt text]"
- **query1-02.jpg** — alt: "[suggested alt text]"
- **query1-03.jpg** — alt: "[suggested alt text]"

[repeat for queries 2 and 3]

**Suggested top pick:** [filename] — [one-line reason]

**To produce this asset, run:**

```bash
python ~/.claude/skills/featured-image/generate_featured_image.py \
  images/hero/[chosen-filename] \
  images/[topic-slug]-featured.png \
  --headline "[headline candidate]" \
  --category "[category]" \
  --subhead "[subhead candidate]" \
  --slug "[topic-slug]" \
  --alt-text "[alt text for chosen photo]" \
  --photographer "[photographer name from images/attributions.csv]" \
  --keywords "[3-5 comma-separated keywords for this article]"
```

The `--slug` flag rewrites the filename to `[topic-slug]-featured.png` for SEO. The other flags embed metadata into the PNG that WordPress reads on upload (Title, Description, Alt, Author, Keywords).

---

## Body stock slot (include if any marker has type `body`)

**Include this section in the image-plan.md output only if Slot 1 or Slot 2 has type `body`.** Label the section heading with the slot number it fills (e.g. "Slot 1 — Body stock" or "Slot 2 — Body stock"). If both slots are type `body`, include this section once and note both slot numbers; the user will produce two separate treated images using different headlines.

**Stock candidates** (in `images/body/`):

### Query: [query 1]
Rationale: [why this query suits the body slot]

- **query1-01.jpg** — alt: "[suggested alt text]"
- **query1-02.jpg** — alt: "[suggested alt text]"
- **query1-03.jpg** — alt: "[suggested alt text]"

[repeat for queries 2 and 3]

**Suggested top pick:** [filename] — [one-line reason]

**Headline framing for body slot:** the body image needs a different
headline from the hero so the page doesn't read as duplicate framing.
Often a question or sub-claim from later in the article works:
"[suggested body-image headline]"

**To produce this asset, run:**

```bash
python ~/.claude/skills/featured-image/generate_featured_image.py \
  images/body/[chosen-filename] \
  images/[topic-slug]-body-treated.png \
  --headline "[suggested body-image headline]" \
  --category "[category]" \
  --position top-left \
  --slug "[topic-slug]-body" \
  --alt-text "[alt text for chosen body photo]" \
  --photographer "[photographer name from images/attributions.csv]" \
  --keywords "[3-5 comma-separated keywords]"
```

The `--slug` is set to `[topic-slug]-body` to differentiate the body-image filename from the hero (`[topic-slug]-body-featured.png` vs `[topic-slug]-featured.png`). The body image needs its own alt text — the photo is different from the hero, so the description should be too.

---

## Pull-quote slot (include if any marker has type `quote`)

**Include this section in the image-plan.md output only if Slot 1 or Slot 2 has type `quote`.** Label the section heading with the slot number it fills (e.g. "Slot 1 — Pull-quote card").

**Sharpest candidate sentence found:**

> "[quote text]"

**Why this works:** [one-line — what makes it claim-led / specific / quotable]

[OR, if no strong candidate exists:]

> "[closest candidate]"

**Note:** No sentence in the article cleanly meets the pull-quote rules.
This is the closest. Consider skipping the quote slot and using body stock
instead.

**To produce this asset, run:**

```bash
python ~/.claude/skills/pull-quote/generate_quote_image.py \
  images/[topic-slug]-quote.png \
  --quote "[quote text]" \
  --category "[category]" \
  --format landscape \
  --slug "[topic-slug]" \
  --alt-text "Pull-quote graphic reading: [quote text]" \
  --keywords "[3-5 comma-separated keywords]"
```

The `--slug` rewrites the filename to `[topic-slug]-quote.png` for SEO. The pull-quote skill auto-generates alt text from the quote if `--alt-text` is omitted, but providing it explicitly gives you control over the phrasing.

(Use `--format square` to also produce an Instagram-shareable version.)

---

## Diagram slot (include if any marker has type `diagram`)

**Include this section in the image-plan.md output only if Slot 1 or Slot 2 has type `diagram`.** Label the section heading with the slot number it fills (e.g. "Slot 2 — Diagram").

**Layout used:** [layout name]

**Why:** [one-line rationale]

**Generated at:** `images/[topic-slug]-diagram.png` ([size]KB)

**To regenerate** (if the output needs a retry), run from the article folder:

```powershell
cd C:/Users/Tom/projects/stock-images
python generate_infographic.py `
  --layout [chosen-layout] `
  --content "C:/Users/Tom/Documents/Home Vault/2 - Business/Content/Blog/1 - Draft/[topic-slug]/images/_diagram-content.json" `
  --output "C:/Users/Tom/Documents/Home Vault/2 - Business/Content/Blog/1 - Draft/[topic-slug]/images/[topic-slug]-diagram.png"
```

The content JSON is at `images/_diagram-content.json` — edit it directly if you want to tweak wording before regenerating.

---

### Fallback — Diagram prompt (NotebookLM, illustration-led, loosened brand)

Use this if the Gemini API output is poor, or if the article is anatomy/biomechanics content that needs illustration rather than typography.

**Composition archetype:** [single-figure with annotation / anatomical comparison / single concept with supporting graphic / sequence diagram]

**Fit note:** [strong / weak — one line on why. If weak (e.g. non-anatomy content), flag it here.]

### D2 — NotebookLM prompt

**Composition archetype:** [single-figure with annotation / anatomical comparison / single concept with supporting graphic / sequence diagram]

**Fit note:** [strong / weak — one line on why. If weak (e.g. non-anatomy content), flag it here.]

**Paste-ready NotebookLM prompt:**

```
Create a [composition shape] explaining [topic]: [one-line summary of core argument].

VISUAL STYLE:
Editorial technical-drawing aesthetic, in the style of a sports science textbook figure or an engineering blueprint. Anatomical illustration is the central element. Choose either Ink #171717 background OR a clean cream/grid-paper background based on best composition. Cream #ECE6D7 for primary text. One restrained accent colour permitted for force vectors, anatomical highlights, and annotation lines. Pick from cyan, muted teal, or muted red. Use the accent sparingly. Fine grain or paper texture across the image. British spelling throughout.

TYPOGRAPHY:
Title: bold condensed display sans-serif (Anton-style), ALL CAPS, dominant scale.
Kicker pills and annotation labels: monospace typewriter font (Courier-style), ALL CAPS, sitting in square-corner pills with contrasting fill. NO rounded corners on pills.
Cue/section headings: Title Case, modern sans-serif (Switzer-style), regular weight.
Body text and explanations: sentence case, modern sans-serif (Switzer-style), regular weight.

COMPOSITION:
[Natural-language description of where each element sits, what each annotation says, what the central illustration shows, and what arrows and force vectors are needed. Include kicker pill labels, heading text, body explanations, arrow directions verbatim.]

HARD CONSTRAINTS:
- The anatomical illustration is technical-editorial in style, not photorealistic, not cartoonish, not anime, not glossy textbook.
- The figure must not show identifiable facial features. Use rear views, bald figures, or minimal profile detail.
- No watermarks, no logos, no decorative marks in any corner.
- Pills have SQUARE CORNERS only. No border-radius under any circumstances.
- The accent colour appears in 3-5 places maximum, never overwhelming the Cream/Ink base.
- Every annotation carries information. No decorative labels.
- Asymmetric composition, never grid-locked.
- British spelling throughout.
```

**NotebookLM settings:** Style preset: Scientific. Orientation: Landscape (or Portrait for tall single-figure compositions). Detail level: Standard.

**Source to load:** [what document or note to load as a source in the notebook before generating]

After generating, crop the watermark (run from the article folder):
`python ~/.claude/skills/infographic-prompt/scripts/remove_notebooklm_watermark.py images/<downloaded.png> --bg "#171717" --mask-width 70 --mask-height 55`

For cream/grid-paper outputs, drop `--bg "#171717"` (auto-samples the background). If the mask clips text, reduce `--mask-width` further. Save as a file starting with `gemini` in `images/`.

---

## Compress to JPEG

Once all assets are generated and the watermark removed from any diagram, run this from the article folder to convert everything to web-ready JPEG (quality 85):

```bash
python -c "
from PIL import Image
import os, glob
for png in glob.glob('images/*.png'):
    jpg = png.replace('.png', '.jpg')
    Image.open(png).convert('RGB').save(jpg, 'JPEG', quality=85, optimize=True)
    print(os.path.basename(png) + ' -> ' + os.path.basename(jpg) + ' (' + str(os.path.getsize(jpg)//1024) + 'KB)')
"
```

Typically 85-90% smaller than the source PNGs. Delete the source PNGs once the JPEGs look good — `/publish-gate` checks file size and only the JPEGs need to come in under 500KB.

---

## Photographer attribution

`images/attributions.csv` contains the photographer credit for every downloaded
stock image. Whichever stock you use, copy the relevant credit line(s) to the
article footer when publishing. This is required by both Unsplash and Pexels
licences.

Format: "Hero image by [Name] on Unsplash. Body image by [Name] on Pexels."
```

**Alt text rules** (SEO-critical, follow strictly):

- Describe what's literally in the image, not what it represents abstractly
- Include the article's main keyword naturally where it fits — never shoehorned
- Under 125 characters
- No "image of", "photo of", "picture of" prefixes
- Specific over generic
- Vary alt text across files — never duplicate
- Since the actual image content isn't visible, write alt text based on what the query implies. The user edits when they pick their favourite.

### 8. Report back

Summarise in chat:

- Article identified: [title]
- Slug used: [topic-slug]
- Category: [category]
- Headline proposed: [headline]
- SEO keywords: [comma-separated list]
- Slot map: Slot 1 = [type], Slot 2 = [type] (from body markers)
- Pull-quote candidate (if any quote marker): [first 50 chars of the quote]... — [strong / weak]
- Diagram generated (if any diagram marker): [layout] — [size]KB at `images/[slug]-diagram.png`, or error message if failed
- Hero queries: [list]
- Body queries (if any body marker): [list]
- Total stock images downloaded: [count]
- Folder: `Blog/1 - Draft/[topic-slug]/`
- Next step: review `image-plan.md`, run the slot commands (Hero plus the two body slot commands). If a slot's fit feels weak, edit the marker in the article body and re-run `/blog-images`.

### 9. Confirm and hand off

After the user has picked their slots and run the relevant commands, list what's now in the article subfolder so the state is visible at a glance:

```powershell
Get-ChildItem "C:/Users/Tom/Documents/Home Vault/2 - Business/Content/Blog/1 - Draft/[topic-slug]/" -Recurse |
  Select-Object FullName, Length |
  Format-Table -AutoSize
```

Then report whether the article is ready for the publish gate:

- **Article file** — confirmed at `Blog/1 - Draft/[topic-slug]/[topic-slug].md`
- **`image-plan.md`** — present in the article subfolder
- **Hero** — `images/[topic-slug]-featured.jpg` present (always required)
- **Slot 1 ([type])** — matching asset present (required, type per marker 1)
- **Slot 2 ([type])** — matching asset present (required, type per marker 2)
- **Attributions** — `images/attributions.csv` present (required if hero or any body slot is stock)

Expected filenames by slot type:
- `quote` → `[topic-slug]-quote.jpg`
- `diagram` → `[topic-slug]-diagram.jpg` (convert from `[topic-slug]-diagram.png` via the compress step below)
- `body` → `[topic-slug]-body-featured.jpg`

Finally, tell the user the next step verbatim:

> When you're ready to publish, run `/publish-gate [topic-slug]` to validate SEO, check image sizes, and move the article subfolder to `3 - PostedArchive/`. This command does not push to Notion or upload to Drive — vault is the source of truth.

That ends the `/blog-images` flow. Nothing else runs from this command.

---

## Notes

- If the downloader hits Unsplash rate limits, it falls through to Pexels automatically — no action needed
- If a query returns zero results from both sources, mention it in the report so Tom can rerun with a different query
- Don't delete `_blog-config.json` after the run — leave it for inspection or manual rerun
- If the article path doesn't exist or can't be read, stop and report the error rather than guessing
- If a quote marker exists, the pull-quote candidate is always proposed — never refuse to suggest one. If no sentence meets the rules cleanly, propose the closest and flag it as weak so the user can decide whether to swap the marker for `body`.
- If a diagram marker exists, always generate gists for at least 3 layouts and recommend one — never refuse. If no layout fits cleanly, flag it as weak so Tom can swap the marker to `body` if he prefers.
- The `images/_diagram-content.json` file is left in place after generation — Tom can edit it and rerun `generate_infographic.py` directly without re-running the full command.
- The `GEMINI_API_KEY` env var must be set before the generator runs. If it's missing the script exits with a clear message.
- Both flags ("weak quote", "weak diagram fit") are signals to the user, not directives. The user makes the editorial call by editing the marker in the article body and re-running `/blog-images`.
