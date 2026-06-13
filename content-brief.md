Generate a content research dossier for: $ARGUMENTS

This command turns the NotebookLM research base into a single structured research dossier:
the upstream raw material the `content-sheet` skill draws from. It does the research
extraction only. It does NOT pre-write angles or pre-fill a content sheet, those are the
`angle-generation` and `content-sheet` skills' jobs, and pre-doing them here just drifts
out of sync with the skills.

Run this after `/notebooklm-build $ARGUMENTS` has completed.

---

## Step 1 — Load the research

Look for the Obsidian note at:
`C:\Users\Tom\Documents\Home Vault\3 - Knowledge\[topic-subfolder]\$ARGUMENTS.md`

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

## Step 3 — Output the dossier

Present the extracted signals as a single clearly-labelled research dossier. This is the
deliverable. Keep it to the research, do not write angles or content-sheet sections,
the skills downstream own those.

---
### RESEARCH DOSSIER: $ARGUMENTS

**Myths & promoters**
[From A: each myth as the audience actually believes it, who promotes it, the kernel of
truth that makes it believable, and the need it serves. Minimum 2.]

**Surprising stats & findings**
[From B: concrete numbers, thresholds, counter-intuitive findings, with source names.]

**Audience belief gaps**
[From C: what the audience believes or wants to believe vs what the evidence shows, and
the emotional payoff of that belief.]

**Named enemies**
[From D: who specifically profits from the misconceptions — behaviour and claim, not
just category.]

**Contrarian position**
[From E: the most defensible against-the-grain position an evidence-based coach could take.]

**Quotable raw material**
[From F: 3–5 unpolished candidate one-liners straight from the research.]

---

## Step 4 — Confirm and hand off

After the dossier, add:

---
**Research dossier complete for: $ARGUMENTS**

This is the research base, not a brief. Next step: take it into the `content-sheet` skill,
which builds the structured brief every format skill draws from and adds Tom's angle and
personal disclosure. If the angle isn't decided yet, run `angle-generation` on the dossier first.

The Obsidian knowledge note is already in your vault at:
`C:\Users\Tom\Documents\Home Vault\3 - Knowledge\[subfolder]\$ARGUMENTS.md`
