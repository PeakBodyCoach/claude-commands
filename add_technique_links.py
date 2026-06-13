#!/usr/bin/env python3
"""
add_technique_links.py

Scans a client file for known exercise names and writes a "## Coaching Notes"
section at the bottom with ![[]] section embeds of the relevant technique pages.

Each embed targets just the Step-by-Step section of the technique doc, not the
full document — so the cues are visible inline without the evidence tables etc.

Usage:
    python $HOME\.claude\commands\add_technique_links.py <path-to-client-file.md>

Re-run at any time to regenerate — the existing section is replaced.
"""

import re
import sys
from pathlib import Path

SECTION_HEADER = "## Coaching Notes"
SECTION_NOTE = "*Auto-generated from detected exercises. Re-run to update.*"
STEP_HEADING = "Step-by-Step: Setup and Execution"

# (display_name, obsidian_note_stem, [aliases_lowercase])
# Order matters: more specific aliases must come before general ones.
EXERCISE_MAP = [
    # ── Hip hinges ─────────────────────────────────────────────────────────
    ("Single-Leg RDL", "Single-Leg-RDL-Technique", [
        "single leg landmine rdl", "single-leg landmine rdl",
        "single leg rdl", "single-leg rdl", "sl rdl", "slrdl",
        "single leg romanian", "single-leg romanian",
    ]),
    ("RDL", "RDL-Technique", [
        "romanian deadlift", "barbell rdl", "bb rdl", "rdl",
    ]),
    ("Trap Bar Deadlift", "Trap-Bar-Deadlift-Technique", [
        "trap bar deadlift", "hex bar deadlift",
        "tbdl", "trap bar dl", "trap bar", "hex bar",
    ]),
    ("Deadlift", "Deadlift-Technique-V2", [
        "conventional deadlift", "barbell deadlift",
        "conv deadlift", "conv dl", "sumo deadlift", "deadlift",
    ]),
    # ── Squats ─────────────────────────────────────────────────────────────
    ("Low Bar Squat", "Low-Bar-Squat-Technique", [
        "low bar squat", "low-bar squat",
    ]),
    ("High Bar Squat", "High-Bar-Squat-Technique", [
        "high bar squat", "high-bar squat", "back squat", "barbell squat",
    ]),
    ("Bulgarian Split Squat", "Bulgarian-Split-Squat-Technique", [
        "bulgarian split squat", "rear foot elevated split squat",
        "rfess", "bss", "bulgarian",
    ]),
    ("Split Squat", "Split-Squat-Technique", [
        "split squat",
    ]),
    ("Lunge", "Lunge-Technique", [
        "walking lunge", "reverse lunge", "lunge",
    ]),
    # ── Upper push ─────────────────────────────────────────────────────────
    ("Bench Press", "Bench-Press-Technique", [
        "flat barbell bench press", "barbell bench press",
        "flat bench press", "bench press",
    ]),
    ("Dumbbell Chest Press", "Dumbbell-Chest-Press-Technique", [
        "incline dumbbell press", "dumbbell chest press",
        "db chest press", "dumbbell press", "db press",
    ]),
    ("Overhead Press", "Overhead-Press-Technique", [
        "overhead barbell press", "barbell overhead press",
        "overhead press", "military press", "shoulder press", "ohp",
    ]),
    ("Dips", "Dips-Technique", [
        "assisted dips", "assisted dip", "chest dips", "tricep dips",
        "dips", "dip",
    ]),
    # ── Upper pull ─────────────────────────────────────────────────────────
    ("Barbell Row", "Barbell-Row-Technique", [
        "barbell bent over row", "bent over row",
        "barbell row", "yates row", "bb row",
    ]),
    ("Single Arm Dumbbell Row", "Dumbbell-Single-Arm-Row-Technique", [
        "single arm dumbbell row", "dumbbell single arm row",
        "db single arm row", "single arm row", "sa row",
    ]),
    ("Pull-Up", "Pull-Up-Technique", [
        "pull-up", "pullup", "pull up",
        "chin-up", "chinup", "chin up",
    ]),
    ("Lat Pulldown", "Lat-Pulldown-Technique", [
        "lat pulldown", "lat pull-down", "lat pull down", "pulldown",
    ]),
    # ── Isolation ──────────────────────────────────────────────────────────
    ("Lateral Raise", "Lateral-Raise-Technique", [
        "unilateral cable lateral raise", "standing cable lateral raise",
        "cable lateral raise", "dumbbell lateral raise",
        "side lateral raise", "lateral raise", "lat raise",
    ]),
    ("Hip Thrust", "Hip-Thrust-Technique", [
        "barbell hip thrust", "bb hip thrust", "hip thrust",
    ]),
]


def extract_candidate_lines(content: str) -> str:
    """Pull lines most likely to contain exercise names."""
    lines = []
    in_programme = False

    for line in content.splitlines():
        s = line.strip()

        # Track Current Programme block
        if re.match(r'^## Current Programme', s):
            in_programme = True
        elif re.match(r'^## ', s) and in_programme:
            in_programme = False

        if in_programme:
            lines.append(s)
            continue

        # exercises: [...] structured fields
        if s.startswith("exercises:"):
            lines.append(s)
            continue

        # Numbered list items (programme or session)
        if re.match(r'^\d+\.', s):
            lines.append(s)
            continue

        # Bullet points with em-dash (session log exercise entries)
        if s.startswith("- ") and (" — " in s or " - " in s):
            lines.append(s)
            continue

        # Bold headings **Exercise Name**
        for m in re.finditer(r'\*\*([^*]+)\*\*', s):
            lines.append(m.group(1))

    return "\n".join(lines)


def find_exercises(content: str) -> list[tuple[str, str]]:
    """Return deduplicated list of (display_name, note_stem) for matched exercises."""
    text = extract_candidate_lines(content).lower()
    found = []
    seen = set()

    for display_name, note_stem, aliases in EXERCISE_MAP:
        if note_stem in seen:
            continue
        for alias in aliases:
            # Non-alpha boundary matching (handles hyphens, brackets, digits)
            pattern = r'(?<![a-z])' + re.escape(alias) + r'(?![a-z])'
            if re.search(pattern, text):
                found.append((display_name, note_stem))
                seen.add(note_stem)
                break

    return found


def build_section(exercises: list[tuple[str, str]]) -> str:
    lines = [SECTION_HEADER, "", SECTION_NOTE, ""]
    for display_name, note_stem in exercises:
        lines.append(f"### {display_name}")
        lines.append(f"![[{note_stem}#{STEP_HEADING}]]")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def update_file(path: Path) -> None:
    content = path.read_text(encoding="utf-8")
    scan_content = content

    parent = path.parent
    client_name = parent.name

    # Sibling Programmes file: canonical "[Name] - Programmes.md", fallback to bare
    for candidate in (parent / f"{client_name} - Programmes.md", parent / "Programmes.md"):
        if candidate.exists():
            scan_content += "\n" + candidate.read_text(encoding="utf-8")
            break

    # Sibling Session Log file (canonical separate-file layout)
    session_log = parent / f"{client_name} - Session Log.md"
    if session_log.exists():
        scan_content += "\n" + session_log.read_text(encoding="utf-8")

    exercises = find_exercises(scan_content)

    if not exercises:
        print("No matching exercises found — no section written.")
        return

    print(f"Matched {len(exercises)} exercise(s):")
    for name, stem in exercises:
        print(f"  - {name}  ->  ![[{stem}#{STEP_HEADING}]]")

    # Strip any existing Coaching Notes section
    existing = re.compile(
        r'\n{0,2}^## Coaching Notes\b[\s\S]*',
        re.MULTILINE
    )
    had_section = bool(existing.search(content))
    if had_section:
        content = existing.sub("", content)
        print("Replacing existing Coaching Notes section.")

    content = content.rstrip() + "\n\n" + build_section(exercises)
    path.write_text(content, encoding="utf-8")
    print(f"\nWritten: {path.name}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python add_technique_links.py <client-file.md>")
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}")
        sys.exit(1)

    update_file(path)


if __name__ == "__main__":
    main()
