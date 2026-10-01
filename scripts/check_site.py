#!/usr/bin/env python3
"""Small, deterministic pre-deploy checks for the public SMILE site."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess
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

swedish_title = "SMILE: Ljudlandskapsutformning med Metamaterialinnovation och Lärande"
home = (DOCS / "index.md").read_text(encoding="utf-8")
for identity in (swedish_title, "SMILE-乐景工程"):
    if identity not in home:
        fail(f"project identity is missing from the home page: {identity}")

one_page_cv = DOCS / "assets" / "cv" / "zibo-liu-public-cv-2026-10.pdf"
one_page_cv_source = ROOT / "cv" / "zibo-liu-public-cv.html"
if not one_page_cv.is_file() or one_page_cv.stat().st_size < 10_000:
    fail(f"public profile PDF is missing or unexpectedly small: {one_page_cv.relative_to(ROOT)}")
if not one_page_cv_source.is_file():
    fail("one-page public profile source is missing")

for command in ([sys.executable, str(ROOT / "scripts" / "render_related_research.py")],):
    result = subprocess.run(command, cwd=ROOT)
    if result.returncode:
        fail(f"validation command failed: {' '.join(command[1:])}")

public_words = re.findall(r"\b[\w’'-]+\b", markdown)
if len(public_words) > 2_600:
    fail(f"public page copy is too detailed ({len(public_words)} words; limit 2600)")

team = (DOCS / "team.md").read_text(encoding="utf-8")
for wording in (
    "drives and leads the Swedish Research Council-funded SMILE project",
    "Collaborators and researchers",
    "project network, not a single reporting line",
):
    if wording not in team:
        fail(f"project leadership or collaboration wording is missing: {wording}")
for wrong_wording in ("my research team", "Participating Researchers"):
    if wrong_wording.lower() in team.lower():
        fail(f"misleading team wording remains: {wrong_wording}")

news = (DOCS / "news.md").read_text(encoding="utf-8")
for public_update in (
    "1 June 2026",
    "KTH–UCL workshop",
    "SMILE City: A Pre-study",
    "incoming postdoctoral researcher",
    "Around the field",
):
    if public_update.lower() not in news.lower():
        fail(f"requested public update is missing: {public_update}")

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
for fact in ("2025-06253", "1 January 2026", "31 December 2029"):
    if fact not in funding:
        fail(f"verified funding fact is missing: {fact}")

excluded_organisation = "sca" + "nia"
published_inputs = [ROOT / "mkdocs.yml"]
published_inputs.extend((ROOT / "cv").glob("*.html"))
published_inputs.extend(path for path in DOCS.rglob("*") if path.is_file())
text_suffixes = {".css", ".html", ".js", ".md", ".svg", ".txt", ".yaml", ".yml"}
for path in published_inputs:
    relative = path.relative_to(ROOT)
    if excluded_organisation in str(relative).lower():
        fail(f"excluded organisation remains in a public path: {relative}")
    if path.suffix.lower() in text_suffixes:
        content = path.read_text(encoding="utf-8")
        if excluded_organisation in content.lower():
            fail(f"excluded organisation remains in public content: {relative}")

for relative in (
    "diagram-sources/smile-diagrams.html",
    "cv/public-cv-data.json",
    "cv/zibo-liu-full-academic-cv.html",
    "cv/zibo-liu-full-academic-cv.template.html",
    "docs/assets/cv/zibo-liu-full-academic-cv.pdf",
    "docs/assets/application-pathways.svg",
    "docs/assets/smile-system-map.svg",
    "docs/assets/technology-roadmap.svg",
    "scripts/build_public_cv.py",
):
    if (ROOT / relative).exists():
        fail(f"retired public asset or generator remains: {relative}")

for svg in sorted((DOCS / "assets").glob("*.svg")):
    try:
        ET.parse(svg)
    except ET.ParseError as exc:
        fail(f"invalid SVG {svg.relative_to(ROOT)}: {exc}")

print("SMILE site source checks passed.")
