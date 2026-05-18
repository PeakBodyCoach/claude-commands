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

For every article, the Peak Body Coach blog system uses **three** image assets selected from **four candidate types**:

| Candidate | What it is | Produced by |
|---|---|---|
| Hero stock | Stock photo + brand treatment | `/blog-images` sources, `featured-image` skill treats |
| Body stock | Second stock photo + brand treatment | `/blog-images` sources, `featured-image` skill treats |
| Pull-quote card | Branded quote graphic | `pull-quote` skill |
| Diagram | Editorial infographic | `infographic-prompt` skill → Gemini Nano Banana 2 |

This command always sources hero stock, always sources body stock, always identifies a pull-quote candidate, and always proposes a diagram layout. **No conditional logic, no flags.** The user picks the three candidates that best serve the article.

The standard assembly is hero + quote + diagram. Body stock substitutes for either quote or diagram when the user prefers it on the day.

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

### 2. Identify the sharpest pull-quote candidate

Read the article and find the single best candidate sentence. Rules:

- Complete sentence, 5–30 words
- Makes a specific claim, not a setup or transition
- Works without surrounding context (no "this means", "as we saw above")
- Contains at least one concrete noun or number
- Avoid sentences starting with "If", "When", "While" — usually conditional setups
- The most quotable line is often a tight assertion, not the most "important" sentence

If no sentence in the article meets these rules well, return the closest match with a note flagging it. The user decides whether to use it.

### 3. Propose a diagram layout and draft the content

Match the article's structure to one of the six `infographic-prompt` layouts:

| Layout | Use when the article contains... |
|---|---|
| `single-stat-callout` | One key statistic with supporting context (e.g. "19% of people maintain goals past 8 weeks") |
| `listicle` | A list of 3-7 reasons, principles, or actions |
| `hero-breakdown` | A composition split or allocation (e.g. "where should your protein come from") |
| `two-column-comparison` | Expectations vs reality, myth vs fact, before vs after |
| `three-elements` | A 3-pillar framework with single-word concepts |
| `acronym-framework` | An acronym to unpack (SMART, FITT, SWOT, custom) |

Pick the strongest fit and write a one-line rationale. If no layout fits well, propose the closest with a note that the diagram fit is weak — the user can opt to skip the diagram slot in favour of body stock.

After picking the layout, read both files:
- `C:/Users/Tom/.claude/skills/infographic-prompt/style-preset.json`
- `C:/Users/Tom/.claude/skills/infographic-prompt/layouts/[chosen-layout].json`

Fill in all content placeholders in the layout's `content` block from the article. Voice rules apply: British spelling, no em dashes, Title Case for comparison rows and secondary labels, ALL CAPS for titles and kicker pills, sentence case for body items and taglines. Do not leave any placeholder unfilled. The filled-in style-preset and layout JSON become the paste-ready Gemini prompt in Candidate D.

Then, also read `C:/Users/Tom/.claude/skills/diagram-prompt/SKILL.md`. Pick a composition archetype from that skill that suits the article's content (single-figure with annotation, anatomical comparison, single concept with supporting graphic, or sequence diagram). Draft the natural-language composition block for a NotebookLM diagram prompt. If the article's content is not anatomy or biomechanics, pick the closest conceptual fit and flag the weakness. Both prompts go into Candidate D — the user picks which to generate, or generates both.

### 4. Generate hero and body search queries

For each slot, write **3 candidate search queries**. Rules:

- 2–4 words each
- Concrete nouns and visual concepts, not abstract ideas
- Match the article's tone — Peak Body Coach is serious and evidence-based, so avoid Instagram-influencer or supplement-ad imagery
- Vary the angles so the candidate set has range

**Hero** captures the article's overall topic. Editorial, magazine-quality. Lead-image energy.

**Body** illustrates a specific section, concept, or counter-point. Should feel different from the hero — if hero is wide and atmospheric, body is closer and specific. If hero is a person, body is an object, and vice versa.

**Avoid duplication.** Hero and body queries must not produce visually similar images.

**Worked example.** Article: "Why GLP-1s Cause Muscle Loss And What To Do About It"
- Hero queries: `injection pen close up`, `prescription medication vial`, `weight loss medication`
- Body queries: `dumbbell rack gym`, `bathroom scale feet`, `elderly person walking`

### 5. Build the queries config

Write a temporary config to `C:/Users/Tom/projects/stock-images/_blog-config.json`:

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

Four candidate types, pick three (or sometimes four) for the article.

The **standard assembly** for Peak Body Coach is:
- Slot 1 = Hero stock (always)
- Slot 2 = Pull-quote card
- Slot 3 = Diagram

Substitute body stock in for slot 2 or slot 3 when the proposed quote
or diagram doesn't fit the article on the day. Use both stock slots
plus quote OR diagram if the article is photo-led.

Each candidate type below has a ready-to-run command. Copy, edit if
needed, run from the article folder.

---

## Candidate A — Hero stock (always slot 1)

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

## Candidate B — Body stock

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

## Candidate C — Pull-quote card

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

## Candidate D — Diagram

**Best-fit layout:** [layout name]

**Why this layout:** [one-line — what the article contains that makes
this layout the right choice]

[OR, if no layout fits well:]

**Best-fit layout:** [closest layout]

**Note:** Diagram fit is weak for this article. Consider skipping the
diagram slot and using body stock instead.

Candidate D has two prompts — one for each visual lane. Pick one to generate, or generate both.

### D1 — Infographic prompt (Gemini Nano Banana 2, typography-only, strict brand)

**Paste-ready Gemini prompt:**

```
Generate the following infographic exactly as specified. Apply every constraint. Do not add elements not explicitly listed.

FORMAT: [layout's format_default]

STYLE PRESET (locked — apply to all output):
[full style-preset.json content]

COMPOSITION (this specific layout):
[full layout JSON with all content placeholders filled in from the article]
```

After generating, crop the watermark (run from the article folder):
`python ~/.claude/skills/infographic-prompt/scripts/remove_notebooklm_watermark.py images/<downloaded.png> --bg "#171717" --mask-width 200 --mask-height 50`

Save as a file starting with `gemini` in `images/`.

---

### D2 — Diagram prompt (NotebookLM, illustration-led, loosened brand)

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
- Pull-quote candidate: [first 50 chars of the quote]... — [strong / weak]
- Diagram layout proposed: [layout] — [strong / weak fit]
- Hero queries: [list]
- Body queries: [list]
- Total stock images downloaded: [count]
- Folder: `Blog/1 - Draft/[topic-slug]/`
- Next step: review `image-plan.md`, pick three of four candidate types, run the relevant commands

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
- **Hero** — `images/[topic-slug]-featured.jpg` present (required for publish)
- **Pull-quote** — `images/[topic-slug]-quote.jpg` present (optional)
- **Body** — `images/[topic-slug]-body-featured.jpg` present (optional)
- **Diagram** — `images/[topic-slug]-diagram.jpg` present, or a `gemini*.jpg` that needs renaming (optional)
- **Attributions** — `images/attributions.csv` present

Finally, tell the user the next step verbatim:

> When you're ready to publish, run `/publish-gate [topic-slug]` to validate SEO, check image sizes, and move the article subfolder to `3 - PostedArchive/`. This command does not push to Notion or upload to Drive — vault is the source of truth.

That ends the `/blog-images` flow. Nothing else runs from this command.

---

## Notes

- If the downloader hits Unsplash rate limits, it falls through to Pexels automatically — no action needed
- If a query returns zero results from both sources, mention it in the report so Tom can rerun with a different query
- Don't delete `_blog-config.json` after the run — leave it for inspection or manual rerun
- If the article path doesn't exist or can't be read, stop and report the error rather than guessing
- The pull-quote candidate is always proposed — never refuse to suggest one. If no sentence meets the rules cleanly, propose the closest and flag it as weak so the user can decide.
- The diagram layout is always proposed — never refuse to suggest one. If no layout fits cleanly, propose the closest and flag it as weak so the user can decide.
- Both flags ("weak quote", "weak diagram fit") are signals to the user, not directives. The user makes the editorial call from the candidates in front of them.
