#!/usr/bin/env python3
"""Search YouTube via yt-dlp and print results with title, URL, views, duration, creator, and upload date."""

import sys
import io
import json

# Force UTF-8 output on Windows where the terminal may default to cp1252
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf-8-sig"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding and sys.stderr.encoding.lower() not in ("utf-8", "utf-8-sig"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
import subprocess
import argparse
from datetime import datetime


def format_duration(seconds):
    if seconds is None:
        return "N/A"
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def format_views(views):
    if views is None:
        return "N/A"
    views = int(views)
    if views >= 1_000_000_000:
        return f"{views / 1_000_000_000:.1f}B"
    if views >= 1_000_000:
        return f"{views / 1_000_000:.1f}M"
    if views >= 1_000:
        return f"{views / 1_000:.1f}K"
    return str(views)


def format_date(date_str):
    if not date_str:
        return "N/A"
    try:
        dt = datetime.strptime(str(date_str), "%Y%m%d")
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return str(date_str)


def search_youtube(query, n=5):
    cmd = [
        "yt-dlp",
        f"ytsearch{n}:{query}",
        "--flat-playlist",
        "--dump-json",
        "--no-warnings",
        "--quiet",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        print("Error: Search timed out after 60 seconds.", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(
            "Error: yt-dlp not found. Install it with:\n  pip install yt-dlp",
            file=sys.stderr,
        )
        sys.exit(1)

    if result.returncode != 0 and result.stderr.strip():
        print(f"yt-dlp warning: {result.stderr.strip()}", file=sys.stderr)

    videos = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue

        video_id = data.get("id", "")
        url = (
            data.get("url")
            or data.get("webpage_url")
            or (
                f"https://www.youtube.com/watch?v={video_id}"
                if video_id
                else "N/A"
            )
        )

        videos.append(
            {
                "title": data.get("title") or "N/A",
                "url": url,
                "views": format_views(data.get("view_count")),
                "duration": format_duration(data.get("duration")),
                "creator": (
                    data.get("uploader")
                    or data.get("channel")
                    or data.get("uploader_id")
                    or "N/A"
                ),
                "upload_date": format_date(data.get("upload_date")),
            }
        )

    return videos


def print_results(query, results):
    print(f'\nTop {len(results)} YouTube results for: "{query}"\n')
    print("=" * 72)
    for i, v in enumerate(results, 1):
        print(f"{i}. {v['title']}")
        print(f"   URL:      {v['url']}")
        print(
            f"   Views:    {v['views']:<10}  Duration: {v['duration']:<10}  Date: {v['upload_date']}"
        )
        print(f"   Creator:  {v['creator']}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Search YouTube using yt-dlp",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
        "  python youtube_search.py lofi hip hop\n"
        "  python youtube_search.py -n 10 python tutorial\n"
        "  python youtube_search.py --json guitar lesson",
    )
    parser.add_argument("query", nargs="+", help="Search query")
    parser.add_argument(
        "-n",
        "--count",
        type=int,
        default=5,
        metavar="N",
        help="Number of results to return (default: 5)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON instead of formatted text",
    )
    args = parser.parse_args()

    query = " ".join(args.query)
    if args.count < 1:
        print("Error: count must be at least 1.", file=sys.stderr)
        sys.exit(1)

    results = search_youtube(query, args.count)

    if not results:
        print(f'No results found for: "{query}"')
        sys.exit(0)

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print_results(query, results)


if __name__ == "__main__":
    main()
