---
description: Write the front-door Verdict and Cliffnotes for a book, corroborate its load-bearing claims, and annotate content flags. Stage 3 of the book-study pipeline.
argument-hint: [book-slug]
---

# /book-study brief

Stage 3 of the book-study pipeline. This is the front-door layer: the critic and the teacher that sit in front of the retrieval notes. It reads the clusters extracted in Stage 2, corroborates the book's load-bearing claims (tiered), and writes two artefacts Tom interacts with first: a Verdict and a Cliffnotes. Both are later loaded into NotebookLM and queued as the first audio overviews.

## Arguments

- `$1` — Book slug (e.g. `anatomy-trains`, `supple-leopard`). Must match an existing manifest with at least some clusters at status `noted`.

Read `C:\Users\Tom\.claude\skills\book-study\SKILL.md` before doing anything else. It defines the Verdict template, the Cliffnotes template, the four claim ratings, the tiered corroboration rule, and the content-flag annotation format.

## Prerequisites

Before starting, check:

1. **Manifest exists** at `Home Vault\3 - Knowledge\Books\[Book Title]\_manifest.json`. If not, stop: "Run `/book-study init` first."
2. **At least one cluster is at status `noted`.** Brief works from the extracted cluster notes, not the raw PDF. If no clusters are noted, stop: "Run `/book-study extract` first."

Load the manifest and read every `noted` cluster note in the book folder. These are your primary material: the concepts, programming notes, and content flags already pulled out in Stage 2. Dip back into the PDF (`pdf_path` in the manifest) only where a claim needs checking against the author's exact wording.

## Procedure

### 1. Assemble the claim set

From the noted cluster notes, list the book's **load-bearing claims**: the assertions the book's argument actually rests on, and anything already flagged as a content opportunity (those are the provocative ones and matter most for the trust question).

Don't audit every sentence. Aim for the 8 to 20 claims that carry the book. A claim qualifies if the book would fall over without it, or if it's the sort of thing Tom might repeat to a client or put in content.

### 2. Tiered corroboration

For each claim, run the two tiers from SKILL.md:

**Tier 1 — reasoned pass (always).** Apply Claude's own critical read: is the claim internally consistent, does it overreach a real finding, does it contradict better-established knowledge or another book in the vault, is opinion being presented as settled fact? Assign a provisional rating: Solid / Mixed / Shaky / Nonsense.

**Tier 2 — external evidence (only where it earns it).** Escalate to the research skills only for claims the reasoned pass rated Shaky or Nonsense, or ones Tom flags:

- `/consensus` — behavioural training, nutrition, and recovery claims
- `/examine` — supplement claims
- `/pubmed` or `/research` — anything else

Pull the actual finding: effect size, population, whether it replicates. Update the rating and record the evidence. All of these are free sources. Never pivot to a paid or metered service without asking Tom first.

For claims that stay Solid or Mixed after Tier 1, note "author's own logic" or the corroborating reasoning as the evidence. You don't need to externally verify a claim that's already sound and uncontested.

Report as you go if a batch of external checks is going to be heavy, so Tom can narrow the set.

### 3. Write the Verdict

Write `00 - [Book Title] - Verdict.md` at the book folder root, using the Verdict template from SKILL.md.

- **What the book argues** — the thesis in two or three plain sentences.
- **How much to trust it** — the headline judgement in one short paragraph. Broadly sound, mixed bag, or mostly hot air. Be willing to say a book is weak. That's the entire point of this layer.
- **Claim by claim** — the table. One row per load-bearing claim, with rating, one-line why, and the evidence (study + effect size where Tier 2 ran, "author's own logic" where it didn't).
- **Where it overreaches** — the specific places the author stretches past the evidence or sells opinion as fact.
- **How it fits with what you already know** — synthesis. Wikilink to other books' clusters in the vault where they agree, conflict, or extend. This is where a nonsense claim in one book gets caught by a solid finding in another.
- **Bottom line** — what to take, what to leave, what to stay sceptical about. Write it to read well aloud; it becomes an audio overview.

Voice: Tom's, direct, British spelling, contractions, no em dashes. This one is closer to content voice than the reference notes are, because Tom actually consumes it. It should sound like Tom talking straight about whether a book is worth the shelf space.

### 4. Write the Cliffnotes

Write `00 - [Book Title] - Cliffnotes.md` at the book folder root, using the Cliffnotes template from SKILL.md.

- Pitch it **below** the book's register. The reader is smart but new to the topic.
- Define jargon the first time it appears. Build each concept up rather than assuming it.
- **The big idea** — the whole book in one followable paragraph.
- **What you actually need to know** — the 5 to 10 load-bearing ideas, each a short plain-English explainer plus a line on why it matters.
- **What you can skip** — the padding and the in-the-weeds parts.
- **In one line** — the single thing to remember.

This is the accessibility layer. If someone read only the Cliffnotes, they should understand the book's core better than if they'd struggled through the book itself. Write it to read well aloud too.

### 5. Annotate the content flags

For every content flag in the manifest whose underlying claim you rated in the Verdict:

- Add `"verdict_rating": "[rating]"` to the flag object in the manifest.
- In the master `_content-opportunities.md`, append the caution to Shaky and Nonsense flags only:

  ```
  - **[Concept]** (Ch[N], [[Book Title - Cluster Title]]) — "[Hook]" `[Verdict: Shaky — contrarian take, verify before producing]`
  ```

- Leave Solid and Mixed flags as they are. No caution tag.

Remove no flags. The point is to make the weak ones visible, not to bin them. A Nonsense flag can still be great contrarian content; it just needs Tom to know that going in.

### 6. Point the index at the front door

In `Home Vault\3 - Knowledge\Books\[Book Title]\_index.md`, add a "Start here" line at the top of the body, above the Chapters section:

```markdown
## Start here
- [[00 - [Book Title] - Verdict]] — how much of this book to trust
- [[00 - [Book Title] - Cliffnotes]] — the plain-English digest
```

### 7. Record brief state on the manifest

Add a top-level `brief` object to the manifest so nlm-load and content-review can read it:

```json
"brief": {
  "date": "2026-07-21",
  "verdict_path": "...\\00 - [Book Title] - Verdict.md",
  "cliffnotes_path": "...\\00 - [Book Title] - Cliffnotes.md",
  "headline": "[one-line trust judgement]",
  "claims_checked": 14,
  "external_checks": 3
}
```

Write the updated manifest back to disk.

### 8. Report back

Output to Tom:

- Headline verdict: is this book worth trusting, in one line
- Claim tally: how many claims checked, the split across Solid / Mixed / Shaky / Nonsense, and how many needed external evidence
- The most important thing that didn't hold up (the single claim most worth knowing is weak)
- Any content flags that got a caution tag (count and quick list)
- Files written (Verdict, Cliffnotes, updated index, updated manifest, updated master flags)
- Next step: `/book-study nlm-load [book-slug]` — the front-door docs are now ready to load into NotebookLM and queue as the first two audio overviews

## Failure Modes

- **Manifest not found** — stop, point to `/book-study init`
- **No noted clusters** — stop, point to `/book-study extract`. Brief needs extracted material to work on
- **A cluster note referenced in the manifest is missing on disk** — note it, work from what's there, flag the gap in the report
- **External evidence is thin or contradictory** — say so in the Verdict rather than forcing a rating. "Contested, no clear answer" is an honest and useful verdict
- **Metered source is the only path for a check** — stop and ask Tom before spending anything. Mark the claim "unverified, paid check needed" and move on if he declines

Be willing to deliver a harsh verdict. The whole reason this stage exists is that the librarian stages take the book at face value. If the book is nonsense, the Verdict is where that gets said plainly.
