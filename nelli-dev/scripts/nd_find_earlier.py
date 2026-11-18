#!/usr/bin/env python3
"""Find earlier output on a topic before starting: docs, ticket and task folders, method notes and memory, ranked by keyword hits.

Run it before the heavy work, then fill only the gaps (Nelli-Dev-IMPROVEMENTS item 13).

Usage
  python find_earlier.py "returns refund voucher"
  python find_earlier.py "bundle product type" --limit 15
  python find_earlier.py ND-001                    # a request id works too

Searches, under the workspace root: docs/, nd-work/, nd-work/_tasks/, method-work/ and the documents at the
root itself (Eg *_Approach_Doc_*.html). It also searches the Claude memory folder for this workspace.
Run logs and Nelli-Dev's own scripts are skipped. Read-only.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__import__('nd_ws').workspace())
FOLDERS = ("docs", "nd-work", "nd-work/_tasks", "method-work")
SKIP_DIRS = {"runs", "_runs", "_scripts", "scripts", "node_modules", ".git", "__pycache__"}
EXT = {".md", ".html", ".htm", ".txt"}
MAX_BYTES = 3_000_000


def memory_folder() -> Path | None:
    """Claude keeps project memory in ~/.claude/projects/<root with ':' and '\\' as '-'>/memory."""
    slug = re.sub(r"[:\\/]", "-", str(ROOT)).lower()
    base = Path.home() / ".claude" / "projects"
    if base.is_dir():
        for folder in base.iterdir():
            if folder.name.lower() == slug and (folder / "memory").is_dir():
                return folder / "memory"
    return None


def candidates() -> list[tuple[str, Path]]:
    found: list[tuple[str, Path]] = []
    for name in FOLDERS:
        base = ROOT / name
        if not base.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d.lower() not in SKIP_DIRS]
            for file in filenames:
                if Path(file).suffix.lower() in EXT:
                    found.append((name, Path(dirpath) / file))
    if ROOT.is_dir():
        found += [("root", p) for p in ROOT.iterdir() if p.is_file() and p.suffix.lower() in EXT]
    memory = memory_folder()
    if memory:
        found += [("memory", p) for p in memory.glob("*.md")]
    return found


def plain(path: Path) -> str:
    try:
        if path.stat().st_size > MAX_BYTES:
            return ""
        text = path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return ""
    if path.suffix.lower() in (".html", ".htm"):
        text = re.sub(r"(?is)<(script|style).*?</\1>", " ", text)
        text = re.sub(r"<[^>]+>", " ", text)
    return text


def title_of(text: str, path: Path) -> str:
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("#"):
            return line.lstrip("# ").strip()[:90]
        if line.startswith("name:"):
            return line[5:].strip()[:90]
    return path.stem[:90]


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("topic", help="keywords, Eg \"returns refund voucher\", or a request id")
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    words = [w.lower() for w in re.findall(r"[\w-]{3,}", args.topic)] or [args.topic.lower()]
    results = []
    for area, path in candidates():
        text = plain(path)
        if not text:
            continue
        low, name = text.lower(), path.name.lower()
        counts = {w: low.count(w) + 25 * name.count(w) for w in words}  # a word in the file name weighs heavily
        matched = sum(1 for c in counts.values() if c)
        if not matched:
            continue
        headings = [ln.strip().lstrip("# ")[:80] for ln in text.splitlines()
                    if ln.lstrip().startswith("#") and any(w in ln.lower() for w in words)][:2]
        results.append((matched, sum(counts.values()), area, path, title_of(text, path), headings))

    results.sort(key=lambda r: (-r[0], -r[1]))
    print(f"Workspace: {ROOT}   topic: {' '.join(words)}")
    if not results:
        print("nothing earlier on this topic - start fresh")
        return
    for matched, hits, area, path, title, headings in results[: args.limit]:
        when = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d")
        try:
            shown = path.relative_to(ROOT)
        except ValueError:
            shown = path
        print(f"\n{matched}/{len(words)} words, {hits:>4} hits  {when}  [{area}]  {shown}")
        print(f"    {title}")
        for heading in headings:
            print(f"    § {heading}")
    if len(results) > args.limit:
        print(f"\n... {len(results) - args.limit} more (raise --limit)")


if __name__ == "__main__":
    main()
