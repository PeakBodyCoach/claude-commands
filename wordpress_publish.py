"""WordPress publish script for Peak Body Coach blog articles.

Pushes a draft from the vault into WP via the REST API. Handles category
discover-or-create, image uploads (featured + body), marker substitution,
CTA + attribution append, and post creation or update.

Usage:
    python wordpress_publish.py <slug-or-path>
    python wordpress_publish.py <slug-or-path> --publish
    python wordpress_publish.py <slug-or-path> --schedule 2026-06-01

Config:
    ~/.claude/wordpress.json — site_url, username, app_password
    ~/.claude/wordpress-cta.html — optional CTA HTML snippet (default used if absent)
    ~/.claude/wordpress-cache.json — runtime cache for category and post lookups
"""

import argparse
import base64
import json
import mimetypes
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

try:
    import requests
    import yaml
    from markdown_it import MarkdownIt
except ImportError as e:
    sys.exit(
        f"Missing dependency: {e.name}. "
        "Install with: pip install requests pyyaml markdown-it-py"
    )

# Import shared cadence helpers from the content-schedule skill.
sys.path.insert(0, str(Path.home() / ".claude" / "skills" / "content-schedule"))
from cadence import compute_next_slot, fetch_vault_taken_slots  # noqa: E402


VAULT_BLOG_ROOT = Path("C:/Users/Tom/Documents/Home Vault/2 - Business/Content/Blog")
DRAFT_ROOT = VAULT_BLOG_ROOT / "1 - Draft"
ARCHIVE_ROOT = VAULT_BLOG_ROOT / "3 - PostedArchive"
CONFIG_PATH = Path.home() / ".claude" / "wordpress.json"
CTA_PATH = Path.home() / ".claude" / "wordpress-cta.html"
CACHE_PATH = Path.home() / ".claude" / "wordpress-cache.json"

YOAST_METADESC = "_yoast_wpseo_metadesc"
YOAST_FOCUSKW = "_yoast_wpseo_focuskw"

DEFAULT_CTA_HTML = ""  # Theme single.php auto-appends sidebar + INK INTERLUDE CTAs.
# To add an in-body CTA on top of those, drop HTML into ~/.claude/wordpress-cta.html.

MARKER_FILENAME = {
    "quote": "{slug}-quote.jpg",
    "diagram": "{slug}-diagram.jpg",
    "body": "{slug}-body-featured.jpg",
}


def load_config():
    if not CONFIG_PATH.exists():
        sys.exit(
            f"Missing {CONFIG_PATH}. Create it with:\n"
            '  { "site_url": "https://peakbodycoach.co.uk",\n'
            '    "username": "<wp-admin-username>",\n'
            '    "app_password": "<wp-app-password>" }'
        )
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def load_cta_html():
    if CTA_PATH.exists():
        return CTA_PATH.read_text(encoding="utf-8").strip()
    return DEFAULT_CTA_HTML


def load_cache():
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    return {"posts": [], "categories": {}, "fetched_at": None}


def save_cache(cache):
    CACHE_PATH.write_text(json.dumps(cache, indent=2), encoding="utf-8")


def resolve_article_path(slug_or_path):
    p = Path(slug_or_path)
    if p.is_file():
        return p
    candidate = DRAFT_ROOT / slug_or_path / f"{slug_or_path}.md"
    if candidate.exists():
        return candidate
    sys.exit(f"Could not resolve article path from '{slug_or_path}'. Tried: {candidate}")


def parse_frontmatter(text):
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    meta = yaml.safe_load(parts[1]) or {}
    body = parts[2].lstrip("\n")
    return meta, body


def write_frontmatter(meta, body):
    yaml_block = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True).strip()
    return f"---\n{yaml_block}\n---\n\n{body}"


def validate_frontmatter(meta):
    required = ["topic", "category", "meta_description", "target_keyword"]
    missing = [k for k in required if not meta.get(k)]
    if missing:
        sys.exit(f"Frontmatter missing required field(s): {', '.join(missing)}")


def find_body_markers(body):
    """Return list of (marker_type, line_num, span) in document order."""
    markers = []
    for m in re.finditer(r"<!--\s*IMAGE:\s*(\w+)\s*-->", body):
        line_num = body[: m.start()].count("\n") + 1
        markers.append((m.group(1), line_num, m.span()))
    return markers


class WPClient:
    def __init__(self, site_url, username, app_password):
        self.site_url = site_url.rstrip("/")
        self.api = f"{self.site_url}/wp-json/wp/v2"
        token = base64.b64encode(f"{username}:{app_password}".encode()).decode()
        self.headers = {"Authorization": f"Basic {token}"}

    def get(self, path, **kwargs):
        return requests.get(f"{self.api}{path}", headers=self.headers, timeout=30, **kwargs)

    def post(self, path, **kwargs):
        return requests.post(f"{self.api}{path}", headers=self.headers, timeout=60, **kwargs)

    def patch(self, path, **kwargs):
        return requests.post(
            f"{self.api}{path}",
            headers={**self.headers, "X-HTTP-Method-Override": "PATCH"},
            timeout=60,
            **kwargs,
        )

    def resolve_category(self, name, cache):
        slug = name.lower().replace(" ", "-")
        cached = cache.get("categories", {})
        if slug in cached:
            return cached[slug]
        r = self.get("/categories", params={"slug": slug})
        r.raise_for_status()
        results = r.json()
        if results:
            cat_id = results[0]["id"]
        else:
            r = self.post("/categories", json={"name": name, "slug": slug})
            r.raise_for_status()
            cat_id = r.json()["id"]
            print(f"  Created WP category: {name} (id={cat_id})", file=sys.stderr)
        cached[slug] = cat_id
        cache["categories"] = cached
        save_cache(cache)
        return cat_id

    def upload_media(self, file_path, alt_text=""):
        if not file_path.exists():
            sys.exit(f"Image file not found: {file_path}")
        mime, _ = mimetypes.guess_type(str(file_path))
        mime = mime or "image/jpeg"
        with file_path.open("rb") as f:
            data = f.read()
        headers = {
            **self.headers,
            "Content-Type": mime,
            "Content-Disposition": f'attachment; filename="{file_path.name}"',
        }
        r = requests.post(f"{self.api}/media", headers=headers, data=data, timeout=120)
        r.raise_for_status()
        media = r.json()
        if alt_text:
            requests.post(
                f"{self.api}/media/{media['id']}",
                headers={**self.headers, "X-HTTP-Method-Override": "PATCH"},
                json={"alt_text": alt_text},
                timeout=30,
            )
        return media

    def create_or_update_post(self, payload, post_id=None):
        if post_id:
            r = self.patch(f"/posts/{post_id}", json=payload)
        else:
            r = self.post("/posts", json=payload)
        r.raise_for_status()
        return r.json()


def substitute_markers(body, markers, uploaded_images):
    """Walk markers in reverse so spans stay valid, replace each with <img> HTML."""
    result = body
    for (marker_type, _line, (start, end)), media in zip(reversed(markers), reversed(uploaded_images)):
        url = media["source_url"]
        alt = media.get("alt_text", "")
        img_html = f'<figure class="wp-block-image size-large"><img src="{url}" alt="{alt}"/></figure>'
        result = result[:start] + img_html + result[end:]
    return result


def read_alt_text_for_slot(image_plan_text, slot_type):
    """Parse image-plan.md for the alt text of a slot of the given type. Best-effort."""
    if not image_plan_text:
        return ""
    pattern = rf"(?i)({slot_type}|hero).*?alt[- ]?text[^:]*:\s*[\"']?([^\"'\n]+)"
    m = re.search(pattern, image_plan_text)
    return m.group(2).strip() if m else ""


def read_attributions(attr_csv_path):
    if not attr_csv_path.exists():
        return []
    lines = attr_csv_path.read_text(encoding="utf-8").strip().splitlines()
    return [line for line in lines[1:] if line.strip()]  # skip header


def format_attribution_paragraph(attr_csv_path, used_filenames):
    rows = read_attributions(attr_csv_path)
    credits = []
    for row in rows:
        parts = [p.strip() for p in row.split(",")]
        if len(parts) < 3:
            continue
        filename, photographer, source = parts[0], parts[1], parts[2]
        if any(filename in uf or Path(filename).stem in uf for uf in used_filenames):
            credits.append(f"{photographer} on {source}")
    if not credits:
        return ""
    return "<p><em>Photography: " + "; ".join(credits) + ".</em></p>"


def fetch_wp_taken_slots(client, today, cache, lookback_days=14):
    """Return WP-side taken slots with category metadata.

    Returns `{date: {"category": slug, "title": str, "slug": str}}` covering:
      - Posts with status=future (scheduled)
      - Posts with status=publish and post_date >= today - lookback_days

    Categories are resolved via the cache's slug->id map (reversed at runtime);
    unknown IDs trigger a fresh `/categories/{id}` GET that also populates the
    cache for future calls. Silently returns whatever it could fetch; errors
    don't block the publisher.
    """
    taken: dict = {}
    cat_id_to_slug = {v: k for k, v in (cache.get("categories") or {}).items()}
    cache_dirty = False

    def resolve_post_category(post):
        nonlocal cache_dirty
        cat_ids = post.get("categories") or []
        if not cat_ids:
            return ""
        first_id = cat_ids[0]
        if first_id in cat_id_to_slug:
            return cat_id_to_slug[first_id]
        try:
            r = client.get(f"/categories/{first_id}")
            if r.status_code == 200:
                data = r.json()
                slug = data.get("slug", "") or ""
                if slug:
                    cache.setdefault("categories", {})[slug] = first_id
                    cat_id_to_slug[first_id] = slug
                    cache_dirty = True
                return slug
        except Exception as e:
            print(f"  WARN: couldn't resolve category id {first_id}: {e}", file=sys.stderr)
        return ""

    def make_entry(post):
        title_raw = (post.get("title") or {}).get("rendered") or ""
        title = re.sub(r"<[^>]+>", "", title_raw).strip()
        return {
            "category": resolve_post_category(post),
            "title": title,
            "slug": post.get("slug", "") or "",
        }

    try:
        r = client.get("/posts", params={"status": "future", "per_page": 100})
        if r.status_code == 200:
            for post in r.json():
                d = date.fromisoformat(post["date"][:10])
                taken[d] = make_entry(post)
    except Exception as e:
        print(f"  WARN: couldn't fetch WP scheduled posts: {e}", file=sys.stderr)
    try:
        cutoff = today - timedelta(days=lookback_days)
        r = client.get(
            "/posts",
            params={
                "status": "publish",
                "after": cutoff.isoformat() + "T00:00:00",
                "per_page": 100,
            },
        )
        if r.status_code == 200:
            for post in r.json():
                d = date.fromisoformat(post["date"][:10])
                taken[d] = make_entry(post)
    except Exception as e:
        print(f"  WARN: couldn't fetch WP recent posts: {e}", file=sys.stderr)

    if cache_dirty:
        save_cache(cache)
    return taken


def find_adjacent_categories(slot, taken_with_meta):
    """Return `{prior, next}` entries immediately around `slot` in the taken set.

    Each entry is `{"date": "YYYY-MM-DD", "category": slug, "title": str,
    "slug": str}` or None at a boundary. `slot` itself is excluded from the
    walk so a same-day collision doesn't masquerade as adjacency.
    """
    dates = sorted(d for d in taken_with_meta.keys() if d != slot)
    prior = None
    nxt = None
    for d in dates:
        if d < slot:
            prior = {"date": d.isoformat(), **taken_with_meta[d]}
        elif d > slot and nxt is None:
            nxt = {"date": d.isoformat(), **taken_with_meta[d]}
            break
    return {"prior": prior, "next": nxt}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("slug_or_path", nargs="?")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--publish", action="store_true", help="Publish live immediately")
    group.add_argument("--schedule", help="Schedule for YYYY-MM-DD")
    group.add_argument(
        "--show-next-slot",
        action="store_true",
        help="Print the next free blog cadence slot (YYYY-MM-DD) and exit",
    )
    group.add_argument(
        "--show-slot-info",
        action="store_true",
        help="Print JSON: next_slot plus adjacent.prior/adjacent.next category info, then exit",
    )
    args = parser.parse_args()

    # --show-next-slot / --show-slot-info: compute next slot from WP + vault, emit, exit.
    if args.show_next_slot or args.show_slot_info:
        config = load_config()
        cache = load_cache()
        client = WPClient(config["site_url"], config["username"], config["app_password"])
        today = date.today()
        wp_taken = fetch_wp_taken_slots(client, today, cache)
        vault_taken = fetch_vault_taken_slots("blog", today)
        # WP wins on date collisions (live posts are authoritative over vault drafts).
        merged = {**vault_taken, **wp_taken}
        slot = compute_next_slot("blog", set(merged.keys()), today)
        if args.show_slot_info:
            adjacent = find_adjacent_categories(slot, merged)
            print(json.dumps({
                "next_slot": slot.isoformat(),
                "adjacent": adjacent,
            }, indent=2))
        else:
            print(slot.isoformat())
        sys.exit(0)

    if not args.slug_or_path:
        parser.error("slug_or_path is required (unless --show-next-slot or --show-slot-info is used)")

    config = load_config()
    client = WPClient(config["site_url"], config["username"], config["app_password"])
    cache = load_cache()

    article_path = resolve_article_path(args.slug_or_path)
    slug = article_path.parent.name
    article_folder = article_path.parent
    images_dir = article_folder / "images"

    print(f"Article: {article_path}", file=sys.stderr)
    print(f"Slug: {slug}", file=sys.stderr)

    raw = article_path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(raw)
    validate_frontmatter(meta)

    is_republish = bool(meta.get("wp_post_id"))
    if is_republish:
        print(f"Re-publish detected (wp_post_id={meta['wp_post_id']}, will PATCH)", file=sys.stderr)

    markers = find_body_markers(body)
    if len(markers) != 2:
        sys.exit(f"Body has {len(markers)} image markers, expected 2. Run /publish-gate first.")

    image_plan_path = article_folder / "image-plan.md"
    image_plan = image_plan_path.read_text(encoding="utf-8") if image_plan_path.exists() else ""

    print("Resolving category...", file=sys.stderr)
    category_id = client.resolve_category(meta["category"], cache)

    print("Uploading featured image...", file=sys.stderr)
    featured_path = images_dir / f"{slug}-featured.jpg"
    featured_alt = read_alt_text_for_slot(image_plan, "hero") or meta.get("title", slug)
    featured = client.upload_media(featured_path, alt_text=featured_alt)
    print(f"  featured: id={featured['id']} url={featured['source_url']}", file=sys.stderr)

    used_filenames = [featured_path.name]
    uploaded_body_images = []
    for marker_type, line, _span in markers:
        body_filename = MARKER_FILENAME[marker_type].format(slug=slug)
        body_path = images_dir / body_filename
        alt = read_alt_text_for_slot(image_plan, marker_type)
        print(f"Uploading body image ({marker_type}, line {line}): {body_filename}", file=sys.stderr)
        media = client.upload_media(body_path, alt_text=alt)
        print(f"  body: id={media['id']} url={media['source_url']}", file=sys.stderr)
        uploaded_body_images.append(media)
        used_filenames.append(body_filename)

    body_with_images = substitute_markers(body, markers, uploaded_body_images)

    md = MarkdownIt("commonmark", {"breaks": False, "html": True}).enable(["table"])
    body_html = md.render(body_with_images)

    cta_html = load_cta_html()
    if cta_html:
        body_html += "\n\n<hr/>\n\n" + cta_html

    attr_html = format_attribution_paragraph(images_dir / "attributions.csv", used_filenames)
    if attr_html:
        body_html += "\n\n" + attr_html

    title = meta.get("title") or extract_h1(body) or slug

    status = None
    if args.publish:
        status = "publish"
    elif args.schedule:
        status = "future"
    elif not is_republish:
        status = "draft"
    # else: re-publish without an explicit status flag — omit status from payload
    # so WP preserves whatever the post is currently set to (don't silently un-publish).

    payload = {
        "title": title,
        "slug": slug,
        "content": body_html,
        "excerpt": meta["meta_description"],
        "categories": [category_id],
        "featured_media": featured["id"],
        "meta": {
            YOAST_METADESC: meta["meta_description"],
            YOAST_FOCUSKW: meta["target_keyword"],
        },
    }
    if status:
        payload["status"] = status
    if args.schedule:
        scheduled = datetime.fromisoformat(args.schedule).replace(
            hour=9, minute=0, tzinfo=timezone.utc
        )
        payload["date"] = scheduled.isoformat()

    print(f"Pushing post (status={status or 'preserve-existing'})...", file=sys.stderr)
    post = client.create_or_update_post(payload, post_id=meta.get("wp_post_id"))
    print(f"  post id={post['id']} status={post.get('status')} link={post['link']}", file=sys.stderr)

    post_meta = post.get("meta", {})
    if not (post_meta.get(YOAST_METADESC) or post_meta.get(YOAST_FOCUSKW)):
        print(
            "  WARN: Yoast meta fields not present in response. "
            "Theme may not be exposing them via REST. "
            "Check post in WP admin; if blank, add the register_meta snippet to the child theme. "
            "See wordpress-publish.md notes.",
            file=sys.stderr,
        )

    meta["wp_post_id"] = post["id"]
    post_status = post.get("status")
    post_date_str = (post.get("date") or "")[:10]  # "2026-06-01T09:00:00" -> "2026-06-01"

    if post_status == "publish":
        # Live: clean slug URL, real publish date, stage=published.
        meta["stage"] = "published"
        meta["published_url"] = post["link"]
        meta["published_date"] = post_date_str or datetime.now().strftime("%Y-%m-%d")
        meta.pop("scheduled_date", None)
        wrote = "stage=published, wp_post_id, published_url, published_date"
    elif post_status == "future":
        # Scheduled: WP scheduler will run it on post_date. No published_url yet
        # (drafts/futures return ?p=N which would clobber a clean URL). No
        # published_date either — the post isn't published yet.
        meta["stage"] = "scheduled"
        if post_date_str:
            meta["scheduled_date"] = post_date_str
        meta.pop("published_url", None)
        meta.pop("published_date", None)
        wrote = "stage=scheduled, wp_post_id, scheduled_date"
    else:
        # Draft or unknown: leave stage alone, don't write dates. wp_post_id
        # is the only writeback so future re-publishes know to PATCH.
        wrote = "wp_post_id"

    article_path.write_text(write_frontmatter(meta, body), encoding="utf-8")
    print(f"Wrote {wrote} to frontmatter.", file=sys.stderr)

    print(post["link"])  # stdout = the URL for the slash command to capture


def extract_h1(body):
    m = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    return m.group(1).strip() if m else None


if __name__ == "__main__":
    main()
