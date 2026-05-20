Search Semantic Scholar for papers on: $ARGUMENTS

Semantic Scholar is an AI-powered academic search engine covering 200M+ papers across all disciplines. The free Graph API returns title, authors, year, venue, citation count, TLDR summary, open-access PDF link, PMID, and DOI for every hit. Better coverage than PubMed outside biomedicine (psychology, behaviour change, sport science, education).

Two modes:

## Search mode (default)

Find papers by query string.

```bash
python ~/.claude/commands/semantic_scholar.py <query>
```

Flags:
- `-n N` or `--count N` — number of results (default 8)
- `--year YYYY` — restrict to papers from this year onwards
- `--json` — raw JSON output

## Walk mode (citation graph)

Given a seed paper (PMID, DOI, or Semantic Scholar ID), return the top-cited papers that cite it (forward walk) AND the top-cited papers it references (backward walk). This is the killer feature: surface the foundational papers everyone in a topic cites, plus the newer work building on a key paper.

```bash
python ~/.claude/commands/semantic_scholar.py --walk PMID:12345678
python ~/.claude/commands/semantic_scholar.py --walk 10.1371/journal.pone.0088384
```

Flags:
- `--forward N` — number of citing papers (default 5)
- `--backward N` — number of references (default 5)
- `--json` — raw JSON output

## Argument parsing

Everything that isn't a flag is the query. If `--walk <ID>` is present, run walk mode and ignore the query. If `--year`, `-n`, `--count`, `--forward`, `--backward`, or `--json` are present, pass them through.

## Output format

For NotebookLM-compatible output, format each result like the `/pubmed` command:

```
1. **[Paper Title]**
   [Semantic Scholar URL OR PDF URL OR DOI URL]
   [Pub types] · [Venue] · [Year] · [Citations] citations
   [First Author] et al.
   TLDR: [TLDR text if present]
   PMID: [PMID if present] · DOI: [DOI if present]
```

For walk mode, present two clearly-labelled sections: **Cited by** (forward) and **References** (backward).

## When to use

- **Default for any general research sweep**: run alongside `/pubmed` for broader coverage, especially on behavioural / psychological / coaching topics where PubMed is thin.
- **Walk mode** when you've found a strong seed paper (a meta-analysis, the foundational RCT) and want to map the citation neighbourhood. Forward walk surfaces newer papers building on it. Backward walk surfaces the classics it builds on.

## Examples

- `/scholar alcohol muscle protein synthesis` — top 8 papers, all years
- `/scholar -n 5 --year 2020 sleep extension athletes` — top 5 since 2020
- `/scholar --walk PMID:24533082` — citation graph around Parr 2014 (alcohol + MPS)
- `/scholar --walk 10.1016/j.smrv.2024.102023 --forward 8 --backward 3` — wider forward walk on a 2024 sleep review

## API key (recommended)

The unauthenticated public endpoint is heavily rate-limited (the free tier is a shared pool across all anonymous users). 429 errors are common.

Free Semantic Scholar API key: request at https://www.semanticscholar.org/product/api#api-key-form

Once you have one, set it in your shell environment:

```powershell
# PowerShell — add to $PROFILE to persist
$env:SEMANTIC_SCHOLAR_API_KEY = "your-key-here"
```

```bash
# Bash — add to ~/.bashrc to persist
export SEMANTIC_SCHOLAR_API_KEY="your-key-here"
```

The script picks it up automatically and sends it as the `x-api-key` header. With a key you get 1 request / sec sustained, plenty for the research flow.

## Errors and edge cases

- If the API returns 429 (rate limit), the script auto-retries with backoff. The fix is an API key, see above.
- If a PMID has no Semantic Scholar entry (rare for biomedical papers), the walk returns empty. Try the DOI form instead.
- If the script reports `HTTP 404`, the seed ID is wrong — check the PMID or DOI.
