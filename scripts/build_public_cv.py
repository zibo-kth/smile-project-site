#!/usr/bin/env python3
"""Build the full public academic CV from its template and canonical metrics."""

from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "cv" / "zibo-liu-full-academic-cv.template.html"
HTML = ROOT / "cv" / "zibo-liu-full-academic-cv.html"
DATA = ROOT / "cv" / "public-cv-data.json"
PDF = ROOT / "docs" / "assets" / "cv" / "zibo-liu-full-academic-cv.pdf"
DEFAULT_METRICS = Path("/home/zibo/projects/latex-cv/scholar_metrics.tex")
WINDOWS_CHROME = Path("/mnt/c/Program Files/Google/Chrome/Application/chrome.exe")
WINDOWS_TEMP = Path("/mnt/c/Users/liuzi/AppData/Local/Temp")


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def long_date(value: date) -> str:
    return f"{value.day} {value.strftime('%B %Y')}"


def import_metrics(path: Path, data: dict) -> bool:
    if not path.is_file():
        fail(f"canonical metrics file not found: {path}")
    text = path.read_text(encoding="utf-8")
    patterns = {
        "citations": r"ScholarCitations\}\{(\d+)\}",
        "h_index": r"ScholarHIndex\}\{(\d+)\}",
        "i10_index": r"ScholariTenIndex\}\{(\d+)\}",
    }
    values: dict[str, int] = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if not match:
            fail(f"cannot read {key} from canonical metrics file")
        values[key] = int(match.group(1))
    changed = any(data.get(key) != value for key, value in values.items())
    data.update(values)
    if changed:
        data["updated_date"] = long_date(date.today())
    return changed


def render(data: dict) -> str:
    required = {"updated_date", "citations", "h_index", "i10_index"}
    if required - data.keys():
        fail("public CV data is incomplete")
    text = TEMPLATE.read_text(encoding="utf-8")
    replacements = {
        "{{UPDATED_DATE}}": str(data["updated_date"]),
        "{{CITATIONS}}": str(data["citations"]),
        "{{HINDEX}}": str(data["h_index"]),
        "{{I10INDEX}}": str(data["i10_index"]),
    }
    for marker, value in replacements.items():
        text = text.replace(marker, value)
    if re.search(r"{{[A-Z0-9_]+}}", text):
        fail("unresolved marker remains in generated CV")
    if "sca" + "nia" in text.lower():
        fail("excluded organisation remains in generated public CV")
    return text


def print_pdf() -> None:
    if not WINDOWS_CHROME.is_file() or not WINDOWS_TEMP.is_dir():
        fail("Windows Chrome PDF renderer is unavailable on this host")
    with tempfile.TemporaryDirectory(prefix="smile-public-cv-", dir=WINDOWS_TEMP) as raw:
        temp = Path(raw)
        source = temp / "cv.html"
        output = temp / "cv.pdf"
        shutil.copy2(HTML, source)
        win_source = subprocess.check_output(["wslpath", "-w", str(source)], text=True).strip()
        win_output = subprocess.check_output(["wslpath", "-w", str(output)], text=True).strip()
        result = subprocess.run(
            [
                str(WINDOWS_CHROME),
                "--headless=new",
                "--disable-gpu",
                "--no-pdf-header-footer",
                f"--print-to-pdf={win_output}",
                f"file:///{win_source}",
            ],
            text=True,
            capture_output=True,
        )
        if result.returncode or not output.is_file() or output.stat().st_size < 40_000:
            fail(f"Chrome PDF rendering failed: {result.stderr.strip()}")
        PDF.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(output, PDF)
        PDF.chmod(0o644)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-canonical", nargs="?", const=str(DEFAULT_METRICS))
    parser.add_argument("--touch", action="store_true", help="set the public CV update date to today")
    parser.add_argument("--write", action="store_true", help="write the generated HTML")
    parser.add_argument("--pdf", action="store_true", help="render the PDF with local Windows Chrome")
    parser.add_argument("--check", action="store_true", help="verify generated source and PDF")
    args = parser.parse_args()

    data = json.loads(DATA.read_text(encoding="utf-8"))
    if args.from_canonical:
        import_metrics(Path(args.from_canonical), data)
    if args.touch:
        data["updated_date"] = long_date(date.today())
    expected = render(data)

    if args.write or args.from_canonical:
        DATA.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        HTML.write_text(expected, encoding="utf-8")
    if args.pdf:
        if not HTML.is_file() or HTML.read_text(encoding="utf-8") != expected:
            fail("generated CV HTML is stale; use --write with --pdf")
        print_pdf()
    if args.check:
        if not HTML.is_file() or HTML.read_text(encoding="utf-8") != expected:
            fail("generated CV HTML is stale; run scripts/build_public_cv.py --write --pdf")
        if not PDF.is_file() or PDF.stat().st_size < 40_000:
            fail("full public academic CV PDF is missing or unexpectedly small")
        print("Full public academic CV source and PDF are valid.")


if __name__ == "__main__":
    main()
