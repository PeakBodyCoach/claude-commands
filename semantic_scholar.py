#!/usr/bin/env python3
"""Search Semantic Scholar or walk citations for a seed paper.

Modes:
  - Search:  python semantic_scholar.py <query>
  - Walk:    python semantic_scholar.py --walk <PMID|DOI|S2 ID>

Citation walks return the top-cited papers that cite the seed (forward) and
the top-cited papers it references (backward).
"""

import argparse
import io
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# Force UTF-8 on Windows where the terminal may default to cp1252
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf-8-sig"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding and sys.stderr.encoding.lower() not in ("utf-8", "utf-8-sig"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

API_BASE = "https://api.semanticscholar.org/graph/v1"
USER_AGENT = "PeakBodyCoach-Research/0.1 (tom@peakbodycoach.co.uk)"

PAPER_FIELDS = ",".join(
    [
        "title",
        "authors.name",
        "year",
        "venue",
        "publicationVenue",
        "citationCount",
        "tldr",
        "openAccessPdf",
        "externalIds",
        "publicationTypes",
        "url",
    ]
)


def api_get(path, params=None, retries=3):
    """GET an API endpoint with simple retry on 429."""
    url = f"{API_BASE}/{path.lstrip('/')}"
    if params:
        url += "?" + urllib.parse.urlencode(params)

    headers = {"User-Agent": USER_AGENT}
    api_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
    if api_key:
        headers["x-api-key"] = api_key

    for attempt in range(retries):
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503, 504) and attempt < retries - 1:
                # Rate-limited or upstream hiccup. Back off and retry.
                wait = (attempt + 1) * 3
                label = "Rate-limited" if e.code == 429 else f"Upstream {e.code}"
                print(f"{label}, waiting {wait}s...", file=sys.stderr)
                time.sleep(wait)
                continue
            body = e.read().decode("utf-8", errors="replace")[:300]
            print(f"HTTP {e.code} from {url}\n{body}", file=sys.stderr)
            sys.exit(1)
        except urllib.error.URLError as e:
            print(f"Network error: {e.reason}", file=sys.stderr)
            sys.exit(1)


def normalise_id(seed):
    """Convert a raw seed string to a Semantic Scholar paper ID format."""
    s = seed.strip()
    if s.upper().startswith(("PMID:", "DOI:", "ARXIV:", "MAG:", "ACL:", "PMCID:", "URL:", "CORPUSID:")):
        # Already prefixed
        return s.upper().split(":", 1)[0] + ":" + s.split(":", 1)[1]
    if s.isdigit():
        return f"PMID:{s}"
    if "/" in s and s.lower().startswith("10."):
        return f"DOI:{s}"
    # Assume Semantic Scholar ID
    return s


def format_authors(authors, max_names=3):
    if not authors:
        return "N/A"
    names = [a.get("name", "?") for a in authors[:max_names]]
    if len(authors) > max_names:
        names.append("et al.")
    return ", ".join(names)


def short_venue(paper):
    v = paper.get("publicationVenue") or {}
    return v.get("name") or paper.get("venue") or "N/A"


def get_pmid(paper):
    eids = paper.get("externalIds") or {}
    return eids.get("PubMed")


def get_doi(paper):
    eids = paper.get("externalIds") or {}
    return eids.get("DOI")


def get_oa_pdf(paper):
    oa = paper.get("openAccessPdf") or {}
    return oa.get("url")


def get_tldr(paper):
    tldr = paper.get("tldr") or {}
    return tldr.get("text")


def get_pub_types(paper):
    types = paper.get("publicationTypes") or []
    return ", ".join(types) if types else "N/A"


def search_papers(query, limit=8, year_from=None):
    params = {"query": query, "limit": limit, "fields": PAPER_FIELDS}
    if year_from:
        params["year"] = f"{year_from}-"
    data = api_get("paper/search", params)
    return data.get("data", [])


def get_paper(seed_id):
    return api_get(f"paper/{seed_id}", {"fields": PAPER_FIELDS})


def get_citations(seed_id, limit=10):
    """Papers that cite the seed (forward walk)."""
    fields = "citingPaper." + ",citingPaper.".join(PAPER_FIELDS.split(","))
    data = api_get(f"paper/{seed_id}/citations", {"limit": 100, "fields": fields})
    papers = [item.get("citingPaper", {}) for item in data.get("data", [])]
    papers.sort(key=lambda p: p.get("citationCount") or 0, reverse=True)
    return papers[:limit]


def get_references(seed_id, limit=10):
    """Papers that the seed cites (backward walk)."""
    fields = "citedPaper." + ",citedPaper.".join(PAPER_FIELDS.split(","))
    data = api_get(f"paper/{seed_id}/references", {"limit": 100, "fields": fields})
    papers = [item.get("citedPaper", {}) for item in data.get("data", [])]
    papers.sort(key=lambda p: p.get("citationCount") or 0, reverse=True)
    return papers[:limit]


def print_paper(idx, p):
    title = p.get("title") or "N/A"
    s2_url = p.get("url") or "N/A"
    year = p.get("year") or "N/A"
    cites = p.get("citationCount")
    cites_str = str(cites) if cites is not None else "N/A"
    oa = get_oa_pdf(p)
    oa_str = "yes" if oa else "no"
    venue = short_venue(p)
    authors = format_authors(p.get("authors") or [])
    pmid = get_pmid(p) or "N/A"
    doi = get_doi(p) or "N/A"
    types = get_pub_types(p)
    tldr = get_tldr(p)

    print(f"{idx}. {title}")
    print(f"   URL:        {s2_url}")
    print(f"   Year: {year}   Citations: {cites_str:<6}  OA: {oa_str}   Type: {types}")
    print(f"   Venue:      {venue}")
    print(f"   Authors:    {authors}")
    print(f"   PMID:       {pmid}    DOI: {doi}")
    if oa:
        print(f"   PDF:        {oa}")
    if tldr:
        print(f"   TLDR:       {tldr}")
    print()


def print_results(header, papers):
    print(f"\n{header}\n" + "=" * 72)
    if not papers:
        print("No results.")
        return
    for i, p in enumerate(papers, 1):
        print_paper(i, p)


def cmd_search(query, count, year_from, as_json):
    papers = search_papers(query, limit=count, year_from=year_from)
    if as_json:
        print(json.dumps(papers, indent=2, ensure_ascii=False))
        return
    suffix = f" (>= {year_from})" if year_from else ""
    print_results(
        f'Top {len(papers)} Semantic Scholar results for: "{query}"{suffix}', papers
    )


def cmd_walk(seed, forward_n, backward_n, as_json):
    seed_id = normalise_id(seed)
    seed_paper = get_paper(seed_id)
    citations = get_citations(seed_id, limit=forward_n)
    references = get_references(seed_id, limit=backward_n)

    if as_json:
        print(
            json.dumps(
                {"seed": seed_paper, "citations": citations, "references": references},
                indent=2,
                ensure_ascii=False,
            )
        )
        return

    print(f'\nCitation walk for {seed_id}\n' + "=" * 72)
    print(f"Seed: {seed_paper.get('title') or 'N/A'}")
    print(f"      {short_venue(seed_paper)} · {seed_paper.get('year') or 'N/A'} · "
          f"{seed_paper.get('citationCount') or 0} citations")
    s2_url = seed_paper.get("url")
    if s2_url:
        print(f"      {s2_url}")
    print()

    print_results(
        f"Cited by (forward, top {len(citations)} by citation count)", citations
    )
    print_results(
        f"References (backward, top {len(references)} by citation count)", references
    )


def main():
    parser = argparse.ArgumentParser(
        description="Search Semantic Scholar or walk citations.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
        "  python semantic_scholar.py alcohol muscle protein synthesis\n"
        "  python semantic_scholar.py -n 10 --year 2020 sleep extension athletes\n"
        "  python semantic_scholar.py --walk PMID:24533082\n"
        "  python semantic_scholar.py --walk 10.1371/journal.pone.0088384\n",
    )
    parser.add_argument("query", nargs="*", help="Search query (when not using --walk)")
    parser.add_argument(
        "--walk", metavar="ID", help="Citation walk for a seed paper (PMID, DOI, or S2 ID)"
    )
    parser.add_argument(
        "-n", "--count", type=int, default=8, metavar="N",
        help="Number of search results (default: 8)",
    )
    parser.add_argument(
        "--forward", type=int, default=5, metavar="N",
        help="Number of citing papers in walk mode (default: 5)",
    )
    parser.add_argument(
        "--backward", type=int, default=5, metavar="N",
        help="Number of referenced papers in walk mode (default: 5)",
    )
    parser.add_argument(
        "--year", type=int, metavar="YYYY",
        help="Restrict search to papers from this year onwards",
    )
    parser.add_argument(
        "--json", action="store_true", help="Output raw JSON instead of formatted text"
    )
    args = parser.parse_args()

    if args.walk:
        cmd_walk(args.walk, args.forward, args.backward, args.json)
        return

    if not args.query:
        parser.error("Provide a query, or use --walk <ID>")

    query = " ".join(args.query)
    if args.count < 1:
        print("Error: count must be at least 1.", file=sys.stderr)
        sys.exit(1)

    cmd_search(query, args.count, args.year, args.json)


if __name__ == "__main__":
    main()
