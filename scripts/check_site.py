#!/usr/bin/env python3
"""Small, deterministic pre-deploy checks for the public SMILE site."""

from __future__ import annotations

from pathlib import Path
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


required_pages = {
    "index.md",
    "about.md",
    "work-packages.md",
    "metamaterials.md",
    "results.md",
    "news.md",
    "team.md",
    "funding.md",
    "contact.md",
}

missing = sorted(name for name in required_pages if not (DOCS / name).is_file())
if missing:
    fail(f"missing required page(s): {', '.join(missing)}")

markdown = "\n".join((DOCS / name).read_text(encoding="utf-8") for name in required_pages)

for placeholder in ("(To be added)", "will be populated", "WP structure (draft)"):
    if placeholder.lower() in markdown.lower():
        fail(f"public placeholder remains: {placeholder}")

results = (DOCS / "results.md").read_text(encoding="utf-8")
correct_authors = (
    "Zibo Liu, Tin Oberman, Xiang Fang, Naveen Indolia, "
    "Francesco Aletta, Azra Habibovic, and Jian Kang"
)
if correct_authors not in results:
    fail("foundational preprint author list is missing or out of order")
if "Andrew Mitchell" in results:
    fail("incorrect author Andrew Mitchell remains in the preprint record")

funding = (DOCS / "funding.md").read_text(encoding="utf-8")
for fact in ("2025-06253", "SEK 3,500,000", "1 January 2026", "31 December 2029"):
    if fact not in funding:
        fail(f"verified funding fact is missing: {fact}")

for svg in sorted((DOCS / "assets").glob("*.svg")):
    try:
        ET.parse(svg)
    except ET.ParseError as exc:
        fail(f"invalid SVG {svg.relative_to(ROOT)}: {exc}")

print("SMILE site source checks passed.")
