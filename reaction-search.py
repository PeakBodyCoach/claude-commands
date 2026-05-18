"""
reaction-search.py — Find YouTube Shorts reaction targets and pull transcripts.

Usage:
    # Explicit queries
    python reaction-search.py --topic "GLP-1 muscle loss" "query 1" "query 2" "query 3"

    # Pull queries from a content sheet markdown file
    python reaction-search.py --from-sheet "C:\\path\\to\\sheet.md"

Requires:
    - YOUTUBE_API_KEY env var (Google Cloud → YouTube Data API v3 key)
    - pip install google-api-python-client youtube-transcript-api

Writes a date-stamped markdown file to:
    C:\\Users\\Tom\\Documents\\Home Vault\\2 - Business\\Content\\Research\\reaction-targets\\
"""

import argparse
import datetime
import os
import re
import sys
from pathlib import Path

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import (
        TranscriptsDisabled,
        NoTranscriptFound,
        VideoUnavailable,
    )
except ImportError as e:
    print(f"ERROR: missing dependency — {e}")
    print("Run: pip install google-api-python-client youtube-transcript-api")
    sys.exit(1)


DEFAULT_VAULT_PATH = (
    r"C:\Users\Tom\Documents\Home Vault\2 - Business\Content\Research\reaction-targets"
)
SHORTS_MAX_SECONDS = 180  # Shorts cap at 3 minutes
CANDIDATES_PER_QUERY = 15  # search returns under-4-min, post-filter to ≤3 min


def parse_iso_duration(iso_duration: str) -> int:
    """Parse ISO 8601 duration (PT1M30S) → total seconds."""
    match = re.match(
        r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso_duration or ""
    )
    if not match:
        return 0
    h, m, s = match.groups()
    return int(h or 0) * 3600 + int(m or 0) * 60 + int(s or 0)


def slugify(text: str, max_len: int = 50) -> str:
    """Turn a topic string into a safe filename slug."""
    slug = re.sub(r"[^\w\s-]", "", text.lower())
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    return slug[:max_len] or "untitled"


def parse_content_sheet(path: str):
    """Extract topic and YouTube queries from a content sheet markdown file.

    Looks for:
      - Topic: YAML frontmatter `title:` field, then first H1, then filename
      - Queries: numbered or bulleted items under the **YouTube** subheading
        inside the "## Reaction Search Queries" section

    Returns (topic: str, queries: list[str])
    Raises ValueError if the section or queries are missing.
    """
    sheet_path = Path(path)
    if not sheet_path.exists():
        raise FileNotFoundError(f"Content sheet not found: {path}")

    text = sheet_path.read_text(encoding="utf-8")

    # --- Topic extraction ---
    topic = None
    fm_match = re.search(
        r"^---\s*\n.*?^(?:title|topic):\s*(.+?)\s*$",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if fm_match:
        topic = fm_match.group(1).strip().strip('"').strip("'")
    if not topic:
        h1_match = re.search(r"^#\s+(.+?)$", text, re.MULTILINE)
        if h1_match:
            topic = h1_match.group(1).strip()
    if not topic:
        topic = sheet_path.stem
    # Strip markdown emphasis chars from the title
    topic = re.sub(r"[*_`]", "", topic).strip()

    # --- Reaction Search Queries section ---
    section_match = re.search(
        r"##\s*Reaction Search Queries(.+?)(?=^##\s|\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if not section_match:
        raise ValueError(
            f"No 'Reaction Search Queries' section in {sheet_path.name}"
        )
    section = section_match.group(1)

    # Check for N/A marker
    if re.search(r"\bN/?A\b", section, re.IGNORECASE):
        raise ValueError(
            f"Reaction Search Queries marked N/A in {sheet_path.name} "
            "(not a video topic)"
        )

    # --- YouTube subsection ---
    yt_match = re.search(
        r"\*\*YouTube\*\*.*?\n(.+?)(?=\*\*TikTok\*\*|\Z)",
        section,
        re.DOTALL,
    )
    if not yt_match:
        raise ValueError(
            f"No '**YouTube**' subsection under Reaction Search Queries"
        )
    yt_block = yt_match.group(1)

    # --- Extract list items ---
    queries = []
    for line in yt_block.split("\n"):
        m = re.match(r"^\s*(?:\d+[\.\)]|-|\*)\s+(.+)$", line)
        if not m:
            continue
        q = m.group(1).strip().strip('"').strip("'")
        # Skip empty placeholders and N/A entries
        if not q or len(q) < 3:
            continue
        if re.match(r"^N/?A\b", q, re.IGNORECASE):
            continue
        queries.append(q)

    if not queries:
        raise ValueError(
            f"No YouTube queries found in {sheet_path.name} "
            "(section exists but is empty)"
        )

    return topic, queries


def search_shorts(youtube, query: str, max_results: int = CANDIDATES_PER_QUERY):
    """Search for short videos matching query. Returns list of video IDs."""
    response = (
        youtube.search()
        .list(
            part="snippet",
            q=query,
            type="video",
            videoDuration="short",  # under 4 minutes — we post-filter to ≤3
            maxResults=max_results,
            order="relevance",
        )
        .execute()
    )
    return [item["id"]["videoId"] for item in response.get("items", [])]


def get_video_details(youtube, video_ids: list) -> list:
    """Batch-fetch full video metadata for a list of IDs."""
    if not video_ids:
        return []
    response = (
        youtube.videos()
        .list(
            part="snippet,contentDetails,statistics",
            id=",".join(video_ids),
        )
        .execute()
    )
    return response.get("items", [])


def filter_to_shorts(videos: list) -> list:
    """Keep only videos ≤3 minutes. Annotate with parsed duration."""
    shorts = []
    for v in videos:
        duration_sec = parse_iso_duration(v["contentDetails"]["duration"])
        if 0 < duration_sec <= SHORTS_MAX_SECONDS:
            v["_duration_sec"] = duration_sec
            shorts.append(v)
    return shorts


def get_transcript(video_id: str):
    """Pull transcript text. Returns string or None if unavailable."""
    try:
        entries = YouTubeTranscriptApi.get_transcript(
            video_id, languages=["en", "en-GB", "en-US"]
        )
        return " ".join(e["text"] for e in entries)
    except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable):
        return None
    except Exception:
        return None


def format_video_entry(video: dict, transcript) -> str:
    snippet = video["snippet"]
    stats = video.get("statistics", {})
    duration = video["_duration_sec"]
    views = int(stats.get("viewCount", 0))

    out = f"### {snippet['title']}\n\n"
    out += f"- **Channel:** {snippet['channelTitle']}\n"
    out += f"- **Published:** {snippet['publishedAt'][:10]}\n"
    out += f"- **Duration:** {duration}s\n"
    out += f"- **Views:** {views:,}\n"
    out += f"- **URL:** https://www.youtube.com/shorts/{video['id']}\n\n"

    if transcript:
        out += f"**Transcript:**\n\n> {transcript}\n\n"
    else:
        out += "**Transcript:** *(not available — no captions on this video)*\n\n"

    out += "---\n\n"
    return out


def main():
    parser = argparse.ArgumentParser(
        description="Search YouTube Shorts for reaction targets and pull transcripts.",
    )
    parser.add_argument(
        "queries",
        nargs="*",
        help="One or more search queries (quote each one). Optional if --from-sheet used.",
    )
    parser.add_argument(
        "--from-sheet",
        metavar="PATH",
        help="Path to a content sheet markdown file. Pulls topic + YouTube queries from it.",
    )
    parser.add_argument(
        "--topic",
        default=None,
        help="Topic name for the output filename. Overrides sheet topic if both given.",
    )
    parser.add_argument(
        "--vault-path",
        default=DEFAULT_VAULT_PATH,
        help="Output folder (defaults to Obsidian vault Research path)",
    )
    parser.add_argument(
        "--no-transcripts",
        action="store_true",
        help="Skip transcript fetching (faster, lighter)",
    )
    args = parser.parse_args()

    # Resolve queries and topic — either from sheet or positional args
    if args.from_sheet:
        try:
            sheet_topic, sheet_queries = parse_content_sheet(args.from_sheet)
        except (ValueError, FileNotFoundError) as e:
            print(f"ERROR: {e}")
            sys.exit(1)
        queries = sheet_queries
        topic = args.topic or sheet_topic
        print(f"Loaded {len(queries)} queries from: {args.from_sheet}")
        print(f"Topic: {topic}")
        if args.queries:
            print("(ignoring positional queries — using --from-sheet instead)")
    else:
        queries = args.queries
        topic = args.topic or "reaction-targets"
        if not queries:
            parser.error(
                "Provide queries as positional arguments or use --from-sheet PATH"
            )

    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        print("ERROR: YOUTUBE_API_KEY environment variable not set.")
        print("See setup.md for instructions.")
        sys.exit(1)

    youtube = build("youtube", "v3", developerKey=api_key)

    output_dir = Path(args.vault_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    date_stamp = datetime.datetime.now().strftime("%Y-%m-%d")
    topic_slug = slugify(topic)
    output_file = output_dir / f"{date_stamp}-{topic_slug}.md"

    # Header
    content = f"# Reaction Targets: {topic}\n\n"
    content += f"*Generated {date_stamp}*\n\n"
    if args.from_sheet:
        content += f"*Source sheet: `{args.from_sheet}`*\n\n"
    content += f"Queries run: {len(queries)}\n\n"
    content += "---\n\n"

    total_results = 0
    total_with_transcripts = 0

    for query in queries:
        print(f"Searching: {query!r}")
        content += f"## Query: \"{query}\"\n\n"

        try:
            video_ids = search_shorts(youtube, query)
            videos = get_video_details(youtube, video_ids)
            shorts = filter_to_shorts(videos)

            if not shorts:
                content += "*No Shorts results.*\n\n---\n\n"
                continue

            # Sort by views descending so highest-impact ones surface first
            shorts.sort(
                key=lambda v: int(v.get("statistics", {}).get("viewCount", 0)),
                reverse=True,
            )

            for video in shorts:
                if args.no_transcripts:
                    transcript = None
                else:
                    transcript = get_transcript(video["id"])
                    if transcript:
                        total_with_transcripts += 1
                content += format_video_entry(video, transcript)
                total_results += 1

        except HttpError as e:
            content += f"*YouTube API error: {e}*\n\n---\n\n"
            print(f"  ERROR on query {query!r}: {e}")
        except Exception as e:
            content += f"*Unexpected error: {e}*\n\n---\n\n"
            print(f"  ERROR on query {query!r}: {e}")

    output_file.write_text(content, encoding="utf-8")

    print()
    print(f"Done: wrote {total_results} results ({total_with_transcripts} with transcripts)")
    print(f"  -> {output_file}")


if __name__ == "__main__":
    main()
