"""Post-deploy step for the July 2026 SEO fix (theme v0.2.0).

Run AFTER the peakbodycoach theme zip is uploaded. Does two things:
1. Writes Yoast meta descriptions for the five key pages via REST
   (needs the v0.2.0 theme live: it registers _yoast_wpseo_metadesc for pages).
2. Verifies the legacy 301 redirects and the deduped homepage head.

Usage: python seo_post_deploy.py
"""

import json
import re
import sys
from pathlib import Path

import requests

CONFIG = Path.home() / ".claude" / "wordpress.json"

PAGE_METADESC = {
    1487: "1:1 personal training and nutrition coaching in Deptford, SE8, plus online coaching UK-wide. I'm Tom, and I coach for results that last.",
    1490: "1:1 body composition and nutrition coaching, in person at the Commando Temple or online. Training, nutrition and weekly check-ins built around your life.",
    1494: "Personal training at the Commando Temple, Deptford SE8. Strength, fat loss and nutrition coaching with Tom Rawcliffe. Book a free discovery call.",
    1496: "Coaching for people on Ozempic, Wegovy or Mounjaro. Keep muscle, eat enough protein and come off the medication without regaining the weight.",
    1492: "I'm Tom Rawcliffe, a personal trainer and nutrition coach in South East London. Here's how I work and what coaching with me looks like.",
}

REDIRECTS = {
    "/about-us/": "/about/",
    "/services/": "/coaching/",
    "/consultation/": "/contact/",
    "/contact-us/": "/contact/",
    "/privacy-policy/": "/privacy/",
    "/privacy-policy-2/": "/privacy/",
    "/terms-conditions/": "/terms/",
    "/blog/": "/articles/",
}


def main():
    cfg = json.loads(CONFIG.read_text())
    auth = (cfg["username"], cfg["app_password"])
    site = cfg["site_url"].rstrip("/")
    base = site + "/wp-json/wp/v2"
    failures = 0

    print("-- Writing Yoast meta descriptions --")
    for page_id, desc in PAGE_METADESC.items():
        r = requests.post(f"{base}/pages/{page_id}", auth=auth,
                          json={"meta": {"_yoast_wpseo_metadesc": desc}})
        ok = r.ok and r.json().get("meta", {}).get("_yoast_wpseo_metadesc") == desc
        print(f"  page {page_id}: {'OK' if ok else 'FAILED (is theme v0.2.0 live?)'}")
        failures += 0 if ok else 1

    print("-- Verifying legacy 301s --")
    for old, new in REDIRECTS.items():
        r = requests.get(site + old, allow_redirects=False)
        target = r.headers.get("Location", "")
        ok = r.status_code == 301 and target.rstrip("/") == (site + new).rstrip("/")
        print(f"  {old} -> {r.status_code} {target or '(no redirect)'} {'OK' if ok else 'FAILED'}")
        failures += 0 if ok else 1

    print("-- Verifying homepage head dedupe --")
    html = requests.get(site + "/", headers={"Cache-Control": "no-cache"}).text
    n_desc = len(re.findall(r'<meta name="description"', html))
    n_canon = len(re.findall(r'<link rel="canonical"', html))
    print(f"  description tags: {n_desc} (want 1), canonical tags: {n_canon} (want 1)")
    if n_desc > 1 or n_canon > 1:
        print("  NOTE: LiteSpeed may be serving a cached page; purge cache in "
              "wp-admin (LiteSpeed Cache -> Purge All) and re-run.")

    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
