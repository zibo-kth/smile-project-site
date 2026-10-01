#!/usr/bin/env python3
"""Validate links, fragments, assets, IDs, and release hygiene in built HTML."""

from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


class Document(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.targets: list[str] = []
        self.title_parts: list[str] = []
        self.in_title = False
        self.scroll_regions: list[dict[str, str | None]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = dict(attrs)
        if data.get("id"):
            self.ids.append(data["id"] or "")
        if data.get("name"):
            self.ids.append(data["name"] or "")
        for key in ("href", "src"):
            if data.get(key):
                self.targets.append(data[key] or "")
        classes = set((data.get("class") or "").split())
        if {"science-figure", "scrollable"}.issubset(classes):
            self.scroll_regions.append(data)
        if tag == "title":
            self.in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)


def fail(messages: list[str]) -> None:
    for message in messages:
        print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


if not SITE.is_dir():
    fail(["site/ does not exist; run 'mkdocs build --strict' first"])

documents: dict[Path, Document] = {}
errors: list[str] = []

for html in sorted(SITE.rglob("*.html")):
    parser = Document()
    parser.feed(html.read_text(encoding="utf-8"))
    documents[html.resolve()] = parser
    duplicates = sorted(value for value, count in Counter(parser.ids).items() if count > 1)
    if duplicates:
        errors.append(f"{html.relative_to(SITE)} has duplicate IDs: {', '.join(duplicates)}")
    for region in parser.scroll_regions:
        if region.get("tabindex") != "0" or not region.get("aria-label"):
            errors.append(
                f"{html.relative_to(SITE)} has a scrollable figure without tabindex=0 and aria-label"
            )


def resolve_target(source: Path, raw: str) -> tuple[Path | None, str]:
    parts = urlsplit(raw)
    if parts.scheme or parts.netloc or raw.startswith("//"):
        return None, ""
    path = unquote(parts.path)
    fragment = unquote(parts.fragment)
    if path.startswith("/"):
        target = SITE / path.lstrip("/")
    elif path:
        target = source.parent / path
    else:
        target = source
    target = target.resolve()
    try:
        target.relative_to(SITE.resolve())
    except ValueError:
        errors.append(f"{source.relative_to(SITE)} points outside site/: {raw}")
        return None, ""
    if target.is_dir() or path.endswith("/"):
        target = target / "index.html"
    elif not target.exists() and not target.suffix:
        candidate = target / "index.html"
        if candidate.exists():
            target = candidate
    return target, fragment


for source, document in documents.items():
    for raw in document.targets:
        target, fragment = resolve_target(source, raw)
        if target is None:
            continue
        if not target.exists():
            errors.append(f"{source.relative_to(SITE)} has missing target: {raw}")
            continue
        if fragment and target.suffix.lower() == ".html":
            target_doc = documents.get(target.resolve())
            if target_doc is None or fragment not in target_doc.ids:
                errors.append(
                    f"{source.relative_to(SITE)} has missing fragment '{fragment}' in {target.relative_to(SITE)}"
                )

excluded_organisation = "sca" + "nia"
stale_public_assets = (
    "assets/cv/zibo-liu-cv_2026-03-21.pdf",
    "assets/cv/zibo-liu-full-academic-cv.pdf",
    "assets/application-pathways.svg",
    "assets/smile-system-map.svg",
    "assets/technology-roadmap.svg",
    f"assets/logos/{excluded_organisation}.jpg",
    "assets/smile-inverse-loop.svg",
    "assets/indoor-truck-cabin-concept.svg",
    "assets/outdoor-luma-park-concept.svg",
)
for relative in stale_public_assets:
    if (SITE / relative).exists():
        errors.append(f"stale public asset remains: {relative}")

for relative, minimum in (("assets/cv/zibo-liu-public-cv-2026-10.pdf", 10_000),):
    public_cv = SITE / relative
    if not public_cv.is_file() or public_cv.stat().st_size < minimum:
        errors.append(f"public CV PDF is missing or unexpectedly small: {relative}")

for public_file in SITE.rglob("*"):
    if not public_file.is_file():
        continue
    relative = public_file.relative_to(SITE)
    if excluded_organisation in str(relative).lower():
        errors.append(f"excluded organisation remains in a public path: {relative}")
    if public_file.suffix.lower() in {".html", ".json", ".svg", ".txt", ".xml"}:
        content = public_file.read_text(encoding="utf-8")
        if excluded_organisation in content.lower():
            errors.append(f"excluded organisation remains in public content: {relative}")

home = documents.get((SITE / "index.html").resolve())
if home is None:
    errors.append("home page was not generated")
else:
    title = "".join(home.title_parts).strip()
    if title in {"SMILE - SMILE", "Home - SMILE", "SMILE Project - SMILE Project"}:
        errors.append(f"home page has generic title: {title}")

if errors:
    fail(errors)

print(f"Rendered site checks passed for {len(documents)} HTML pages.")
