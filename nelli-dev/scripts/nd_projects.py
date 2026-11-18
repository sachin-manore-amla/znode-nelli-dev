#!/usr/bin/env python3
"""Find, record and list the customer's project folders (where the Custom API SDK and the Webstore are cloned).

Nelli-Dev never assumes these paths: it asks the developer, then records the answer here.

Usage
  python nd_projects.py detect [--root <folder>] [--depth 3]       # candidate folders found by their signature files
  python nd_projects.py add --name sdk|webstore|<other> --path <folder>   # validate and record (the guard asks the developer to confirm)
  python nd_projects.py list                                        # recorded projects with branch and git status
  python nd_projects.py remove --name <name>

Recorded in the central config (%USERPROFILE%/.nelli-dev/config.json, see nd_config.py). The guard allows file access inside the workspace AND inside
these recorded folders only (writes still need the approved plan and scope). Because that widens what the
agent can touch, every write to projects.json asks the developer to confirm on screen.

Signatures: SDK = a *.sln plus Custom.Api.Core/ or Engine.Custom.Api/; Webstore = nx.json plus apps/webstore/.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

PRUNE = {"node_modules", "bin", "obj", ".git", ".nx", ".next", "dist", ".vs", ".idea", "__pycache__", "nd-work", ".claude"}


def workspace() -> Path:
    return Path(__import__('nd_ws').workspace()).resolve()


def load() -> dict:
    """Projects from the central config (nd_config.py), plus any still only in an old workspace file."""
    import nd_config
    return {"projects": nd_config.projects(workspace())}


def save(projects: list) -> None:
    import nd_config
    nd_config.set_projects(projects)


def git(path: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(path), *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def kind(p: Path) -> str | None:
    if (p / "nx.json").exists() and (p / "apps" / "webstore").is_dir():
        return "webstore"
    if list(p.glob("*.sln")) and ((p / "Custom.Api.Core").is_dir() or (p / "Engine.Custom.Api").is_dir()):
        return "sdk"
    return None


def describe(p: Path) -> str:
    branch = git(p, "branch", "--show-current") or "(not a git repo / detached)"
    dirty = git(p, "status", "--porcelain")
    commit = git(p, "log", "-1", "--format=%h %cs") or "?"
    return f"branch {branch} · {commit} · {'clean' if not dirty and git(p, 'rev-parse', '--is-inside-work-tree') else ('uncommitted changes' if dirty else 'git status unknown')}"


def cmd_detect(a) -> int:
    root = Path(a.root).resolve() if a.root else workspace()
    found = []
    base_depth = len(root.parts)
    for d, dirs, _ in os.walk(root):
        dirs[:] = [x for x in dirs if x not in PRUNE]
        if len(Path(d).parts) - base_depth > a.depth:
            dirs[:] = []
            continue
        k = kind(Path(d))
        if k:
            found.append((k, Path(d)))
            dirs[:] = []
    if not found:
        print(f"no SDK or Webstore clone found under {root} (depth {a.depth}). Ask the developer for the folder paths.")
        return 0
    for k, p in found:
        print(f"{k:9} {p}   [{describe(p)}]")
    print("These are CANDIDATES. Ask the developer to confirm which folders are theirs; do not use one without confirmation.")
    return 0


def cmd_add(a) -> int:
    p = Path(a.path).expanduser().resolve()
    if not p.is_dir():
        sys.exit(f"not a folder: {p}")
    k = kind(p)
    if a.name in ("sdk", "webstore") and k != a.name:
        sys.exit(f"{p} does not look like the {a.name} (signature files missing). Check the path, or use another --name if this is deliberate.")
    ws = workspace()
    data = load()
    save([x for x in data["projects"] if x["name"] != a.name] + [{"name": a.name, "path": str(p), "kind": k}])
    print(f"recorded {a.name}: {p}\n  {describe(p)}")
    if ws not in p.parents and p != ws:
        print("  note: this folder is outside the workspace; the guard will allow it because it is recorded here.")
    return 0


def cmd_list(_a) -> int:
    pr = load()["projects"]
    if not pr:
        print("no projects recorded yet: ask the developer where the Custom API SDK and the Webstore are cloned.")
        return 1
    for x in pr:
        p = Path(x["path"])
        print(f"{x['name']:10} {p}   [{describe(p) if p.is_dir() else 'MISSING'}]")
    return 0


def cmd_remove(a) -> int:
    save([x for x in load()["projects"] if x["name"] != a.name])
    print("removed", a.name)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("detect"); d.add_argument("--root"); d.add_argument("--depth", type=int, default=3); d.set_defaults(fn=cmd_detect)
    s = sub.add_parser("add"); s.add_argument("--name", required=True); s.add_argument("--path", required=True); s.set_defaults(fn=cmd_add)
    sub.add_parser("list").set_defaults(fn=cmd_list)
    r = sub.add_parser("remove"); r.add_argument("--name", required=True); r.set_defaults(fn=cmd_remove)
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
