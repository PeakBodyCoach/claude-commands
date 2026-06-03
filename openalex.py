#!/usr/bin/env python3
"""Search OpenAlex for academic works across all disciplines.

OpenAlex indexes 250M+ works, including journal articles, reviews, preprints,
theses, and grey literature. Particularly strong outside biomedicine
(behavioural science, sport science, psychology, education).

Example usage:
  python openalex.py alcohol muscle protein synthesis
  python openalex.py -n 10 --year 2020 --oa-only sleep extension athletes
  python openalex.py --sort citations behaviour change motivational interviewing
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

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf-8-sig"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding and sys.stderr.encoding.lower() not in ("utf-8", "utf-8-sig"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

API_BASE = "https://api.openalex.org"

# OpenAlex's "polite pool" gets higher rate limits and priority routing when
# a mailto is supplied. Set OPENALEX_MAILTO in env, or fall back to the default.
DEFAULT_MAILTO = "tom@peakbodycoach.co.uk"


def api_get(path, params=None, retries=3):
    url = f"{API_BASE}/{path.lstrip('/')}"
    params = dict(params or {})
    mailto = os.environ.get("OPENALEX_MAILTO", DEFAULT_MAILTO)
    if mailto:
        params["mailto"] = mailto
    if params:
        url += "?" + urllib.parse.urlencode(params, safe=":,>|")

    for attempt in range(retries):
        req = urllib.request.Request(
            url, headers={"User-Agent": f"PeakBodyCoach-Research/0.1 (mailto:{mailto})"}
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503, 504) and attempt < retries - 1:
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


def reconstruct_abstract(inverted_index):
    """OpenAlex stores abstracts as a position-indexed inverted index.
    Rebuild a flat string from {word: [positions]}.
    """
    if not inverted_index:
        return None
    positions = []
    for word, indices in inverted_index.items():
        for idx in indices:
            positions.append((idx, word))
    positions.sort()
    return " ".join(word for _, word in positions)


def format_authors(authorships, max_names=3):
    if not authorships:
        return "N/A"
    names = []
    for a in authorships[:max_names]:
        author = a.get("author") or {}
        names.append(author.get("display_name") or "?")
    if len(authorships) > max_names:
        names.append("et al.")
    return ", ".join(names)


def get_venue(work):
    loc = work.get("primary_location") or {}
    src = loc.get("source") or {}
    return src.get("display_name") or "N/A"


def get_oa_url(work):
    best = work.get("best_oa_location") or {}
    return best.get("pdf_url") or best.get("landing_page_url")


def get_pmid(work):
    ids = work.get("ids") or {}
    pmid_url = ids.get("pmid")
    if pmid_url:
        return pmid_url.rsplit("/", 1)[-1]
    return None


def get_doi(work):
    doi = work.get("doi")
    if doi:
        # Strip the "https://doi.org/" prefix if present
        return doi.replace("https://doi.org/", "")
    return None


def get_top_concepts(work, n=3):
    concepts = work.get("concepts") or []
    return [c.get("display_name") for c in concepts[:n] if c.get("display_name")]


def search_works(query, count, year_from, oa_only, work_type, sort_by):
    filters = []
    if year_from:
        filters.append(f"publication_year:>{year_from - 1}")
    if oa_only:
        filters.append("is_oa:true")
    if work_type:
        # Map shorthand to OpenAlex type values
        type_map = {
            "article": "article",
            "review": "review",
            "preprint": "preprint",
            "book": "book",
            "chapter": "book-chapter",
        }
        mapped = type_map.get(work_type, work_type)
        filters.append(f"type:{mapped}")

    params = {
        "search": query,
        "per-page": count,
    }
    if filters:
        params["filter"] = ",".join(filters)
    if sort_by == "citations":
        params["sort"] = "cited_by_count:desc"
    elif sort_by == "date":
        params["sort"] = "publication_date:desc"
    # default sort = relevance

    data = api_get("works", params)
    return data.get("results", []), data.get("meta", {})


def print_work(idx, w, show_abstract=False):
    title = w.get("title") or w.get("display_name") or "N/A"
    year = w.get("publication_year") or "N/A"
    cites = w.get("cited_by_count")
    cites_str = str(cites) if cites is not None else "N/A"
    venue = get_venue(w)
    authors = format_authors(w.get("authorships") or [])
    pmid = get_pmid(w) or "N/A"
    doi = get_doi(w) or "N/A"
    oa = w.get("open_access") or {}
    is_oa = oa.get("is_oa")
    oa_str = "yes" if is_oa else "no"
    oa_url = get_oa_url(w)
    work_type = w.get("type") or "N/A"
    s2_or_oa_url = w.get("id") or "N/A"
    concepts = get_top_concepts(w)

    print(f"{idx}. {title}")
    print(f"   URL:        {s2_or_oa_url}")
    print(f"   Year: {year}   Citations: {cites_str:<6}  OA: {oa_str}   Type: {work_type}")
    print(f"   Venue:      {venue}")
    print(f"   Authors:    {authors}")
    print(f"   PMID:       {pmid}    DOI: {doi}")
    if oa_url:
        print(f"   PDF/OA:     {oa_url}")
    if concepts:
        print(f"   Topics:     {', '.join(concepts)}")
    if show_abstract:
        abstract = reconstruct_abstract(w.get("abstract_inverted_index"))
        if abstract:
            # Trim long abstracts
            if len(abstract) > 600:
                abstract = abstract[:600] + "..."
            print(f"   Abstract:   {abstract}")
    print()


def print_results(query, works, meta, show_abstract):
    total = meta.get("count")
    total_str = f" (of {total} total)" if total is not None else ""
    print(f'\nTop {len(works)} OpenAlex results for: "{query}"{total_str}\n' + "=" * 72)
    if not works:
        print("No results.")
        return
    for i, w in enumerate(works, 1):
        print_work(i, w, show_abstract=show_abstract)


def main():
    parser = argparse.ArgumentParser(
        description="Search OpenAlex across all academic disciplines.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
        "  python openalex.py alcohol muscle protein synthesis\n"
        "  python openalex.py -n 10 --year 2020 --oa-only behaviour change motivational interviewing\n"
        "  python openalex.py --sort citations sleep extension athletes\n"
        "  python openalex.py --type review --abstract female menopause resistance training\n",
    )
    parser.add_argument("query", nargs="+", help="Search query")
    parser.add_argument(
        "-n", "--count", type=int, default=8, metavar="N",
        help="Number of results (default: 8, max: 200)",
    )
    parser.add_argument(
        "--year", type=int, metavar="YYYY",
        help="Restrict to papers from this year onwards",
    )
    parser.add_argument(
        "--oa-only", action="store_true",
        help="Restrict to open-access papers",
    )
    parser.add_argument(
        "--type",
        choices=["article", "review", "preprint", "book", "chapter"],
        help="Restrict to a specific work type",
    )
    parser.add_argument(
        "--sort",
        choices=["relevance", "citations", "date"],
        default="relevance",
        help="Sort order (default: relevance)",
    )
    parser.add_argument(
        "--abstract", action="store_true",
        help="Include rebuilt abstract in output",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output raw JSON instead of formatted text",
    )
    args = parser.parse_args()

    query = " ".join(args.query)
    if args.count < 1 or args.count > 200:
        print("Error: count must be between 1 and 200.", file=sys.stderr)
        sys.exit(1)

    works, meta = search_works(
        query,
        count=args.count,
        year_from=args.year,
        oa_only=args.oa_only,
        work_type=args.type,
        sort_by=args.sort,
    )

    if args.json:
        print(json.dumps({"meta": meta, "results": works}, indent=2, ensure_ascii=False))
        return

    if not works:
        print(f'No results found for: "{query}"')
        sys.exit(0)

    print_results(query, works, meta, show_abstract=args.abstract)


if __name__ == "__main__":
    main()
