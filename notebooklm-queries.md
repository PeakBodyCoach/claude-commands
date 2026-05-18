Generate a curated set of NotebookLM queries for the topic: $ARGUMENTS

**Note:** This command is for manual use — when you want to query an existing notebook by hand, or interrogate a notebook that was not built via the automated pipeline. For the full automated pipeline (create notebook, add sources, run queries, write Obsidian note in one go), use `/notebooklm-build $ARGUMENTS` instead.

---

## Step 1 — Infer query shape from the topic

Before generating queries, classify the topic:

- **Intervention / compound** (e.g. creatine, intermittent fasting, cold exposure) → lean toward mechanism, evidence quality, and practical application queries
- **Condition / population** (e.g. PCOS, menopause, endurance athletes) → lean toward prevalence, pathophysiology, and protocol queries
- **Trend / concept** (e.g. fibremaxxing, carnivore diet, zone 2 training) → lean toward evidence base, expert consensus, and counterargument queries
- **Training methodology** (e.g. RPE-based programming, deload protocols) → lean toward mechanism, implementation, and individual variation queries

Adjust the query list below to suit the classified type. Keep all queries — just reword where needed.

---

## Step 2 — Output the query list

Display this intro message first:

---
**NotebookLM query list for: $ARGUMENTS**

Copy each query below and ask it in your NotebookLM notebook. Paste all responses back into Claude Code and run:
`/notebooklm-build $ARGUMENTS`

---

Then output the numbered query list:

**Core understanding**
1. Give me a comprehensive overview of $ARGUMENTS — what it is, why it matters, and what the key claims are.
2. What are the proposed mechanisms? How is it supposed to work physiologically?
3. What does the strongest evidence actually show? Summarise the highest-quality studies (meta-analyses, RCTs) and their findings.
4. What is the current scientific consensus, and where does genuine uncertainty remain?

**Evidence quality**
5. What are the main limitations of the existing research — study design, population, duration, funding source?
6. Are there any studies or findings that contradict the mainstream view on $ARGUMENTS? What do they show?
7. What do we still not know? What are the open questions that need more research?

**Practical application**
8. What protocols, doses, or approaches have the best evidence behind them? Be specific with numbers where available.
9. Who benefits most from $ARGUMENTS — are there specific populations, phenotypes, or contexts where it works better or worse?
10. What are the most common mistakes, misconceptions, or overhyped claims about $ARGUMENTS?

**Context and connections**
11. What concepts, mechanisms, or topics are most closely related to $ARGUMENTS that I should also understand?
12. Who are the key researchers, practitioners, or voices in this area — and do they broadly agree or disagree?
13. How does $ARGUMENTS interact with or relate to nutrition, training, sleep, or other lifestyle factors?

**Synthesis**
14. If I had to summarise the practical takeaway for a busy, evidence-literate person — what should they actually do or believe about $ARGUMENTS?
15. What is the strongest counterargument against the mainstream position on $ARGUMENTS?

---

After the query list, remind the user:

> Run all 15 queries in NotebookLM. You don't need to copy every word of the response — a summary paste is fine. Then run `/notebooklm-build $ARGUMENTS` and paste all Q&A pairs when prompted.
