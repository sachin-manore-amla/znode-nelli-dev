"""Shared helpers for the Nelli-Dev scanners: file walking, git-diff file lists, rule running, reporting."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

PRUNE = {"node_modules", "bin", "obj", ".git", ".nx", ".next", "dist", ".vs", ".idea", "__pycache__", ".venv", "venv",
         "coverage", "wwwroot", ".claude", "nd-work"}
BINARY = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".woff", ".woff2", ".ttf", ".eot", ".pdf", ".zip", ".dll", ".exe", ".pdb",
          ".nupkg", ".mp4", ".webp", ".bin", ".lock"}
SEV = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "Info": 4}


@dataclass
class Rule:
    rid: str
    sev: str
    pattern: re.Pattern
    msg: str
    exts: tuple = ()
    redact: bool = False


def walk(paths, exts=()):
    """Return (files, skipped). exts limits the files taken; skipped lists binaries that were not scanned."""
    files, skipped = [], []
    for p in map(Path, paths):
        cand = [p] if p.is_file() else [f for f in p.rglob("*")
                                         if f.is_file() and not any(part in PRUNE for part in f.relative_to(p).parts)]
        for f in cand:
            if f.suffix.lower() in BINARY:
                skipped.append(str(f))
            elif exts and f.suffix.lower() not in exts and f.name.lower() not in exts:
                continue
            else:
                files.append(f)
    return files, skipped


def git_changed(repo, ref):
    out = subprocess.run(["git", "-C", repo, "diff", "--name-only", "--diff-filter=ACMR", ref], capture_output=True, text=True)
    if out.returncode:
        sys.exit("git diff failed: " + out.stderr.strip())
    return [str(Path(repo) / line) for line in out.stdout.splitlines() if line.strip()]


def read(f):
    try:
        return f.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    except OSError:
        return None


def run_rules(files, rules):
    hits, unreadable = [], []
    for f in files:
        lines = read(f)
        if lines is None:
            unreadable.append(str(f))
            continue
        for rule in rules:
            if rule.exts and f.suffix.lower() not in rule.exts and f.name.lower() not in rule.exts:
                continue
            for n, line in enumerate(lines, 1):
                if rule.pattern.search(line):
                    text = "(redacted)" if rule.redact else line.strip()[:140]
                    hits.append({"rule": rule.rid, "sev": rule.sev, "file": str(f), "line": n, "msg": rule.msg, "text": text})
    return hits, unreadable


def report(title, hits, unreadable, skipped, scanned, note, as_json):
    """Print the report; return 1 when any Critical or High lead exists."""
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    hits.sort(key=lambda h: (SEV[h["sev"]], h["file"], h["line"]))
    if as_json:
        print(json.dumps({"title": title, "scanned": scanned, "hits": hits, "unreadable": unreadable,
                          "skipped": skipped, "note": note}, indent=1))
    else:
        print(f"# {title}: {scanned} file(s) scanned, {len(hits)} lead(s)")
        counts = {s: sum(1 for h in hits if h["sev"] == s) for s in SEV}
        print("  " + "  ".join(f"{s} {c}" for s, c in counts.items() if c))
        for h in hits:
            print(f"[{h['sev']}] {h['rule']} {h['file']}:{h['line']}  {h['msg']}\n      {h['text']}")
        if unreadable:
            print(f"\nUNREADABLE ({len(unreadable)}): " + "; ".join(unreadable[:10]))
        if skipped:
            print(f"SKIPPED binary ({len(skipped)}): not scanned")
        print(f"\nAccuracy: {note}")
    return 1 if any(h["sev"] in ("Critical", "High") for h in hits) else 0
