Generate a content research dossier for: $ARGUMENTS

This command bridges the NotebookLM research pipeline and the content creation skills.
It reads the research already gathered and produces two structured outputs:
1. Pre-loaded angle candidates for the angle-generation skill
2. Pre-filled section material for the content-sheet skill

Run this after `/notebooklm-build $ARGUMENTS` has completed.

---

## Step 1 — Load the research

Look for the Obsidian note at:
`C:\Users\Tom\Documents\Home Vault\3 - Resources\[topic-subfolder]\$ARGUMENTS.md`

Also check whether `nlm_responses.json` is still present in the working directory.
If it is, use it — it contains more granular detail than the note.
If not, the Obsidian note is sufficient.

If neither exists, tell the user:
> Run `/notebooklm-build $ARGUMENTS` first to generate the research base.

---

## Step 2 — Extract content-strategy signals

From the research, identify and extract:

**A. Myths and their promoters**
List every false or misleading claim appearing in the sources. For each:
- State the myth as the audience would actually believe it (not academically)
- Name the specific creator, brand, camp, or influencer type promoting it
- Identify the kernel of truth that makes it believable
- Note the emotional need or appeal it serves

**B. Surprising stats and findings**
Extract any specific numbers, percentages, thresholds, or counter-intuitive findings
from the research. Prefer concrete over vague. Note the source.

**C. Audience belief gaps**
What does the audience clearly believe or want to believe about this topic that
the evidence contradicts? What is the emotional payoff of that belief?

**D. Named enemies**
Who specifically profits from the misconceptions? Be precise —
not "the supplement industry" but "brands selling [specific product] to people
who [specific situation where it doesn't help]."

**E. Contrarian position**
What is the most defensible against-the-grain position an evidence-based coach
with 12 years of experience could take on this topic?

**F. Quotable raw material**
What facts, findings, or framings from the research could become a one-liner
that stops someone mid-scroll? List 3–5 candidates — these don't need to be
polished yet.

---

## Step 3 — Output Part 1: Angle candidates

Output this block first, clearly labelled for the angle-generation skill:

---
### ANGLE CANDIDATES FOR: $ARGUMENTS
*Feed these into the angle-generation skill. Each is grounded in the actual research.*

**Contrarian**
- [Research-grounded contrarian angle — based on what the evidence actually shows vs the prevailing narrative]
- [Second contrarian angle if a distinct one exists]

**Tension & Taboo**
- [The awkward truth buried in the research that the mainstream takes avoid naming]

**Novelty & Curiosity Gap**
- [The most surprising stat or counter-intuitive finding, framed as a hook]
- [Second novelty angle if distinct]

**Audience Belief Gap**
- [What this audience believes vs what the evidence shows — framed as a position, not a question]

**Wrongly Framed Question**
- [The question everyone asks about $ARGUMENTS, and why it's the wrong question based on what the research shows]

**Cynical**
- [What someone who's seen this topic grifted and misrepresented for years would privately say about it]

**Enemy-facing**
- [A position that directly names who is profiting from the misconceptions and what they're selling]

*Note: These are starting points. The angle-generation skill will push them further.
Pick 2–4 to explore in depth, or say "run all".*

---

## Step 4 — Output Part 2: Content sheet pre-fill

Output this block second, clearly labelled for the content-sheet skill:

---
### CONTENT SHEET PRE-FILL FOR: $ARGUMENTS
*These sections are pre-populated from the NotebookLM research. Paste into the
content sheet at the relevant sections. Tom's angle and personal disclosure still
need Tom's input — those are flagged.*

**Myths & Misconceptions** *(pre-filled from research)*

1. **Myth:** [myth as audience believes it]
   - **Who promotes it:** [specific name/brand/camp]
   - **Why it persists:** [emotional appeal or incentive]
   - **Kernel of truth:** [the grain of truth inside it]

2. **Myth:** [second myth]
   - **Who promotes it:** [specific]
   - **Why it persists:** [reason]
   - **Kernel of truth:** [grain of truth]

[Continue for all myths identified — minimum 2, maximum 5]

**Enemy** *(pre-filled from research)*
[Specific description of who profits from the misconceptions — behaviour and claim,
not just category]

**Evidence & Credibility** *(pre-filled from research — translate to plain coaching language)*

- [Finding 1]: [what was tested → what it showed → what it means for the reader]
- [Finding 2]: [same format]
- [Finding 3]: [same format]
[Include specific numbers and source names where available]

**Inversions / Script Flips** *(generated from research counterarguments)*

- [Inversion 1 — a genuine flip based on what the evidence shows, not just a myth rewrite]
- [Inversion 2 — must feel counter-intuitive, not just obvious]

**Quotable Moments** *(raw candidates from research — will need sharpening)*

- [Candidate 1]
- [Candidate 2]
- [Candidate 3]

**Tom's Angle + Personal Disclosure**
[NEEDS TOM'S INPUT: The research shows [summary of what the evidence actually says].
What does Tom actually think about this beyond the standard take? What has he seen
coaching clients? What does he do himself? The research gives the platform — Tom's
personal angle and at least one specific personal detail are still needed here.]

---

## Step 5 — Confirm and hand off

After both output blocks, add:

---
**Research dossier complete for: $ARGUMENTS**

Next steps:
1. Take the angle candidates above into the angle-generation skill — pick 2–4 categories or say "run all"
2. Once an angle is chosen, take the content sheet pre-fill into the content-sheet skill along with the chosen angle
3. The content sheet skill will complete the remaining sections (audience, solution, analogies, objections, tone direction, content opportunities)

The Obsidian knowledge note is already in your vault at:
`C:\Users\Tom\Documents\Home Vault\3 - Resources\[subfolder]\$ARGUMENTS.md`
