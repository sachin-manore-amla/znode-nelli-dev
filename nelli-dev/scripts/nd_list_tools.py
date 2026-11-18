#!/usr/bin/env python3
"""List every script and tool Nelli-Dev can use right now, grouped by where it lives.

Scripts are added over time, so Nelli-Dev runs this at the start of a task and picks
its tools from what exists at that moment:

  skills   helper scripts shipped with the skills (<plugin>/skills/<skill>/)
  library  Nelli-Dev's reusable scripts (<plugin>/scripts/)
  work     one ticket's own scripts (nd-work/<KEY>/scripts/, with --key)
  repos    each repo's tooling: package.json scripts, and PowerShell, shell and
           batch tools near the repo root or in scripts/tools/build folders
  tests    .NET test projects (*Test*.csproj) and package.json test scripts
  runs     the latest tracked runs (nd_track.py), flagging any still running
           or stale, so work left going in the background is never missed

Usage
  python list_tools.py                         # every section
  python list_tools.py --section skills        # skills | library | work | repos | tests | runs
  python list_tools.py --key ND-001          # add that ticket's own scripts
  python list_tools.py --grep spec             # filter by name, path or description
  python list_tools.py --repo my-custom-api --section tests

Read-only: it reads file names, Python docstrings and first comment lines only.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nd_track import Tracker, describe_run, recent_runs  # noqa: E402  (same library folder)

# Workspace root: NELLIDEV_WORKSPACE (old name ZNODE_WORKSPACE), else <root>/.claude/scripts/list_tools.py -> <root>.
ROOT = Path(__import__('nd_ws').workspace())
PKG = Path(__file__).resolve().parent.parent      # the plugin folder

PRUNE = {
    "node_modules", "bin", "obj", ".git", ".nx", ".next", "dist", ".vs", ".idea", "__pycache__",
    ".venv", "venv", "packages", "testresults", "coverage", "wwwroot", ".playwright-mcp",
}
SCRIPT_EXT = {".py", ".js", ".ps1", ".sh", ".bat", ".cmd", ".sql"}
SHELL_EXT = {".ps1", ".sh", ".bat", ".cmd"}
TOOL_DIRS = {"scripts", "script", "tools", "build", "deploy", "devops", "fixes"}
SKIP_COMMENT = re.compile(r"^(requires|eslint|@ts-|-\*-|pylint|noqa|#?region|#?endregion|type:|copyright)", re.I)
TOOL_DEPTH = 3     # how deep to look for shell tools under a repo
TEST_DEPTH = 8     # how deep to look for test projects
PER_REPO = 20      # tools listed per repo before "+N more"


def clean(text: str, limit: int = 110) -> str:
    text = " ".join(text.lstrip("*#/ ").split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def describe(path: Path) -> str:
    """The Python docstring's first line, else the file's first comment line."""
    try:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return ""
    if path.suffix.lower() == ".py":
        try:
            doc = ast.get_docstring(ast.parse(text))
        except (SyntaxError, ValueError):
            doc = None
        if doc:
            paragraph = doc.strip().split("\n\n", 1)[0]  # the whole first sentence, even when it wraps
            return clean(paragraph)
    in_block = False
    for raw in text.splitlines()[:60]:
        line = raw.strip()
        if not line:
            continue
        if in_block:
            closing = line.endswith(("#>", "*/")) or line.startswith(("#>", "*/"))
            body = line.replace("#>", "").replace("*/", "").strip(" *")
            if closing:
                in_block = False
            if body and not body.startswith(".") and not SKIP_COMMENT.match(body):
                return clean(body)
            continue
        if line.startswith(("<#", "/*")):
            body = line[2:].replace("#>", "").replace("*/", "").strip(" *")
            in_block = not line.endswith(("#>", "*/")) or len(line) <= 4
            if body and not body.startswith(".") and not SKIP_COMMENT.match(body):
                return clean(body)
            continue
        if line.startswith("#!") or line.lower().startswith("@echo"):
            continue
        match = re.match(r"(?://+|#+|--+|rem\s|::)\s*(.*)", line, re.I)
        if match:
            body = match.group(1).strip()
            if body and not SKIP_COMMENT.match(body):
                return clean(body)
            continue
        break  # reached code without a leading comment
    return ""


def listed(folder: Path, recursive: bool = False) -> list[Path]:
    if not folder.is_dir():
        return []
    files = folder.rglob("*") if recursive else folder.iterdir()
    return sorted(p for p in files if p.is_file() and p.suffix.lower() in SCRIPT_EXT
                  and "__pycache__" not in p.parts and "node_modules" not in p.parts)


def repos() -> list[Path]:
    return sorted(p for p in ROOT.iterdir() if p.is_dir() and (p / ".git").exists())


def package_scripts(repo: Path) -> dict[str, str]:
    manifest = repo / "package.json"
    if not manifest.is_file():
        return {}
    try:
        return json.loads(manifest.read_text(encoding="utf-8-sig")).get("scripts") or {}
    except (OSError, ValueError):
        return {}


def scan_repo(repo: Path) -> tuple[list[Path], list[Path]]:
    """Return (shell tools, test projects) found under one repo."""
    tools: list[Path] = []
    tests: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(repo):
        here = Path(dirpath)
        depth = len(here.relative_to(repo).parts)
        dirnames[:] = [d for d in dirnames if d.lower() not in PRUNE and not d.startswith(".github")]
        if depth >= TEST_DEPTH:
            dirnames[:] = []
        in_tool_dir = any(part.lower() in TOOL_DIRS for part in here.relative_to(repo).parts)
        for name in filenames:
            ext = Path(name).suffix.lower()
            if ext == ".csproj" and "test" in name.lower():
                tests.append(here / name)
            elif depth <= TOOL_DEPTH and (ext in SHELL_EXT or (ext == ".py" and in_tool_dir)):
                tools.append(here / name)
    return sorted(tools), sorted(tests)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--section", choices=("skills", "library", "work", "repos", "tests", "runs"),
                        action="append", help="limit to one or more sections (repeatable)")
    parser.add_argument("--key", help="request id whose work-folder scripts to include")
    parser.add_argument("--grep", help="regex filter on name, path and description")
    parser.add_argument("--repo", help="only repos whose name contains this text")
    args = parser.parse_args()
    with Tracker("list_tools", key=args.key) as track:
        report(args, track)


def report(args, track: Tracker) -> None:
    wanted = set(args.section or ("skills", "library", "work", "repos", "tests", "runs"))
    pattern = re.compile(args.grep, re.I) if args.grep else None

    def keep(*fields: str) -> bool:
        return not pattern or any(pattern.search(f or "") for f in fields)

    def rel(path: Path) -> str:
        try:
            return str(path.relative_to(ROOT))
        except ValueError:
            return str(path)

    print(f"Workspace: {ROOT}")

    if "skills" in wanted:
        base = PKG / "skills"
        rows = [(p, p.relative_to(base).parts[0], describe(p)) for p in listed(base, recursive=True)
                if p.suffix.lower() in (".py", ".js")]
        rows = [r for r in rows if keep(r[0].name, r[1], r[2])]
        print(f"\n== Skill scripts ({len(rows)})  {rel(base)}")
        for path, skill, desc in rows:
            print(f"  {path.name:<26} {skill:<28} {desc}")

    if "library" in wanted:
        base = PKG / "scripts"
        rows = [(p, describe(p)) for p in listed(base, recursive=True)]
        rows = [r for r in rows if keep(str(r[0].relative_to(base)), r[1])]
        print(f"\n== Nelli-Dev script library ({len(rows)})  {rel(base)}")
        for path, desc in rows:
            print(f"  {str(path.relative_to(base)):<26} {desc}")

    if "work" in wanted and args.key:
        base = ROOT / "nd-work" / args.key.upper() / "scripts"
        rows = [(p, describe(p)) for p in listed(base, recursive=True)]
        rows = [r for r in rows if keep(r[0].name, r[1])]
        print(f"\n== {args.key.upper()} scripts ({len(rows)})  {rel(base)}")
        for path, desc in rows:
            print(f"  {str(path.relative_to(base)):<26} {desc}")

    if wanted & {"repos", "tests"}:
        chosen = [r for r in repos() if not args.repo or args.repo.lower() in r.name.lower()]
        test_rows: list[tuple[str, str, str]] = []
        if "repos" in wanted:
            print(f"\n== Repo tooling ({len(chosen)} repos)")
        track.phase("repos", total=len(chosen))
        for repo in chosen:
            track.step(repo.name)
            tools, tests = scan_repo(repo)
            npm = package_scripts(repo)
            for name, command in npm.items():
                if "test" in name.lower() and keep(repo.name, name, command):
                    test_rows.append((repo.name, f"npm run {name}", clean(command, 80)))
            for project in tests:
                if keep(repo.name, project.stem, rel(project)):
                    test_rows.append((repo.name, project.stem, rel(project.parent)))
            if "repos" not in wanted:
                continue
            lines = [(f"npm run {n}", clean(c, 80)) for n, c in npm.items() if keep(repo.name, n, c)]
            lines += [(str(t.relative_to(repo)), describe(t)) for t in tools
                      if keep(repo.name, str(t.relative_to(repo)), "")]
            if not lines:
                continue
            print(f"  {repo.name}")
            for label, desc in lines[:PER_REPO]:
                print(f"    {label:<44} {desc}")
            if len(lines) > PER_REPO:
                print(f"    ... +{len(lines) - PER_REPO} more (use --repo {repo.name})")
        if "tests" in wanted:
            print(f"\n== Tests ({len(test_rows)})")
            for repo_name, name, where in test_rows:
                print(f"  {repo_name:<34} {name:<44} {where}")

    if "runs" in wanted:
        runs = recent_runs(every=True, limit=8, skip_names=("list_tools",))
        live = [r for r in runs if r["effective"] in ("running", "stale")]
        print(f"\n== Recent runs ({len(runs)} shown, {len(live)} running or stale)  nd-work\\*\\runs"
              "  - details: nd_track.py status <run>")
        for state in runs:
            print(f"  {state['id'][:40]:<40} {describe_run(state)}")
    track.result(sections=len(wanted))


if __name__ == "__main__":
    main()
