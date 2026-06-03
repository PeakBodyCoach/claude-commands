Search OpenAlex for academic works on: $ARGUMENTS

OpenAlex is a free, fully open academic search engine indexing 250M+ works across every discipline. No API key required, no auth, no rate-limit panic. Better coverage than PubMed outside biomedicine: behavioural science, psychology, sport science, education, economics, sociology. Also indexes preprints, theses, grey literature, and conference papers PubMed doesn't see.

Each result includes title, authors, year, journal/venue, citation count, work type (article / review / preprint), OA status, open-access PDF URL when available, PMID and DOI cross-references, and topic concepts.

## How to run

```bash
python $HOME\.claude\commands\openalex.py <query>
```

Flags:
- `-n N` or `--count N` — number of results (default 8, max 200)
- `--year YYYY` — restrict to papers from this year onwards
- `--oa-only` — open-access only
- `--type TYPE` — restrict to `article`, `review`, `preprint`, `book`, or `chapter`
- `--sort relevance|citations|date` — default is relevance
- `--abstract` — include rebuilt abstract in output (OpenAlex stores them as an inverted index, the script reconstructs)
- `--json` — raw JSON

## Argument parsing

Everything that isn't a flag is the query. Pass `-n`, `--year`, `--oa-only`, `--type`, `--sort`, `--abstract`, `--json` through to the script as supplied.

## When to use

- **Behavioural and psychological topics** where PubMed is thin: motivational interviewing, self-determination theory, habit formation, fear-avoidance, coaching psychology.
- **Sport science** broadly. OpenAlex indexes Sports Medicine Open, IJSNEM, JSCR, and many smaller journals PubMed misses.
- **Cross-disciplinary topics**. Behaviour change touches psychology, public health, economics; OpenAlex links concepts across them.
- **Preprint discovery**. Filter `--type preprint` to surface bioRxiv / SportRxiv / SocArXiv work that's 6-18 months ahead of published literature.
- **As a quality-ranked supplement to PubMed**. Sort by citations on the same query and the highest-impact papers float up regardless of where they were indexed.

## Output format

For NotebookLM-compatible output, format each result like the `/scholar` command:

```
1. **[Paper Title]**
   [OpenAlex URL OR OA PDF URL OR DOI URL]
   [Work type] · [Venue] · [Year] · [Citations] citations · OA: [yes/no]
   [First Author] et al.
   PMID: [PMID if present] · DOI: [DOI if present]
   Topics: [top 2-3 OpenAlex concepts]
```

## Examples

- `/openalex behaviour change motivational interviewing` — top 8 across all disciplines
- `/openalex -n 10 --year 2020 --oa-only sleep extension athletes` — top 10 open-access papers since 2020
- `/openalex --type review female menopause resistance training` — review papers only
- `/openalex --sort citations habit formation` — sorted by impact, not relevance

## Polite pool

OpenAlex gives higher rate limits and priority routing to requests that include a mailto. The script sends `tom@peakbodycoach.co.uk` by default. Override with `$env:OPENALEX_MAILTO = "..."` in PowerShell if needed.

## Errors and edge cases

- Auto-retries on 429, 502, 503, 504 with linear backoff.
- Some works have no abstract; `--abstract` will silently skip those.
- OpenAlex types use hyphenated values (`book-chapter`); the script maps the friendly shorthand (`chapter`) for you.
