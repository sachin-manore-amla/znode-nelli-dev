#!/usr/bin/env python3
"""Print the version stamp for an output: each repo's branch, commit and uncommitted changes, plus the environment and the date.

Generated docs and reports carry it, so readers know what they were built from and when they may be out
of date, and scripts can regenerate them (Nelli-Dev-IMPROVEMENTS item 18).

Usage
  python version_stamp.py --repo my-custom-api --repo my-webstore --env "customer dev"
  python version_stamp.py --repo my-custom-api --format line
  python version_stamp.py --repo my-webstore --env "customer dev (<url>)"

--format block (default) prints a Markdown table to paste at the end of a document; --format line prints
one line for short replies. Exits 1 when a repo is missing or isn't a git repository. Read-only.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__import__('nd_ws').workspace())


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                            encoding="utf-8", errors="replace")
    return result.stdout.strip() if result.returncode == 0 else ""


def describe(name: str) -> dict:
    repo = Path(name) if Path(name).is_absolute() else ROOT / name
    if not (repo / ".git").exists():
        return {"repo": repo.name, "error": "not found or not a git repository"}
    changes = [ln for ln in git(repo, "status", "--porcelain").splitlines() if ln.strip()]
    return {
        "repo": repo.name,
        "branch": git(repo, "rev-parse", "--abbrev-ref", "HEAD") or "?",
        "commit": git(repo, "rev-parse", "--short", "HEAD") or "?",
        "date": git(repo, "log", "-1", "--format=%cs") or "?",
        "tree": "clean" if not changes else f"{len(changes)} uncommitted change(s)",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", action="append", required=True, help="repo folder name under the root (repeat)")
    parser.add_argument("--env", help="environment the output was checked against, Eg customer dev")
    parser.add_argument("--format", choices=("block", "line"), default="block")
    args = parser.parse_args()

    repos = [describe(name) for name in args.repo]
    built = datetime.now().strftime("%Y-%m-%d %H:%M")
    env = args.env or "none (code only)"
    if args.format == "line":
        parts = [f"{r['repo']} @ {r['branch']} ({r['commit']}, {r['tree']})" if "error" not in r
                 else f"{r['repo']} ({r['error']})" for r in repos]
        print(f"Built from: {' · '.join(parts)} · environment: {env} · {built}")
    else:
        print(f"**Built from** — {built} · environment: {env}\n")
        print("| Repo | Branch | Commit | Working tree |")
        print("|---|---|---|---|")
        for r in repos:
            if "error" in r:
                print(f"| {r['repo']} | — | — | {r['error']} |")
            else:
                print(f"| {r['repo']} | {r['branch']} | {r['commit']} ({r['date']}) | {r['tree']} |")
    sys.exit(1 if any("error" in r for r in repos) else 0)


if __name__ == "__main__":
    main()
