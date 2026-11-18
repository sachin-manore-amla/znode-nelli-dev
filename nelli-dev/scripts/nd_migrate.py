#!/usr/bin/env python3
"""Move Z-Custom data into Nelli-Dev. Dry run by default; nothing is deleted or overwritten.

What it carries over (from <workspace>/zc-work and an old nd-work environment/projects file):
  - environments and project folders  -> the central config (nd_config.py). Credentials are never read or copied.
  - request folders (zc-work/*)       -> nd-work/* , only when the target folder does not exist yet.
    Not copied: approval.json (an approval must be given again under the new name), env files, keys and certificates.
The old zc-work stays where it is, untouched; move it to a retired folder yourself once you are satisfied.

Usage
  python nd_migrate.py                 show what would be carried over
  python nd_migrate.py --apply         do it (the guard asks the developer to confirm)
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nd_config  # noqa: E402

SKIP_FILES = ("approval.json", ".env", ".env.*", "*.env", "*.pem", "*.key", "*.pfx", "*.p12")


def skipped(name: str) -> bool:
    return any(fnmatch.fnmatch(name.lower(), g) for g in SKIP_FILES)


def plan(root: Path) -> dict:
    central = nd_config.load()
    have_env = {e["name"] for e in central["environments"]}
    have_pr = {p["name"] for p in central["projects"]}
    envs = [e for e in nd_config.environments(root) if e.get("legacy") and e["name"] not in have_env]
    prs = [p for p in nd_config.projects(root) if p.get("legacy") and p["name"] not in have_pr]
    folders, left_out = [], []
    old = root / "zc-work"
    if old.is_dir():
        for d in sorted(old.iterdir()):
            if not d.is_dir():
                continue
            if (root / "nd-work" / d.name).exists():
                left_out.append((d.name, "already exists in nd-work"))
                continue
            files = [f for f in d.rglob("*") if f.is_file()]
            keep = [f for f in files if not skipped(f.name)]
            folders.append({"name": d.name, "files": len(keep), "left_out": len(files) - len(keep)})
    return {"envs": envs, "projects": prs, "folders": folders, "already_there": left_out}


def apply(root: Path, p: dict) -> None:
    cfg = nd_config.load()
    cfg["environments"] += [{k: v for k, v in e.items() if k != "legacy"} for e in p["envs"]]
    cfg["projects"] += [{k: v for k, v in x.items() if k != "legacy"} for x in p["projects"]]
    if cfg["default_env"] is None and len(cfg["environments"]) == 1:
        cfg["default_env"] = cfg["environments"][0]["name"]
    nd_config.save(cfg)
    copied = []
    for f in p["folders"]:
        src, dst = root / "zc-work" / f["name"], root / "nd-work" / f["name"]
        for item in src.rglob("*"):
            if item.is_file() and not skipped(item.name):
                target = dst / item.relative_to(src)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, target)
        copied.append(f["name"])
    (root / "nd-work").mkdir(exist_ok=True)
    log = {"when": datetime.now(timezone.utc).isoformat(timespec="seconds"), "environments": [e["name"] for e in p["envs"]],
           "projects": [x["name"] for x in p["projects"]], "request_folders": copied}
    (root / "nd-work" / "_migration.json").write_text(json.dumps(log, indent=1), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    root = Path(__import__("nd_ws").workspace())
    p = plan(root)
    print(f"workspace: {root}")
    print("environments to record:", ", ".join(e["name"] for e in p["envs"]) or "none")
    print("projects to record:", ", ".join(f"{x['name']} ({x['path']})" for x in p["projects"]) or "none")
    for f in p["folders"]:
        print(f"request folder {f['name']}: {f['files']} file(s) to copy" + (f", {f['left_out']} left out (approval, env or key files)" if f["left_out"] else ""))
    for n, why in p["already_there"]:
        print(f"request folder {n}: skipped ({why})")
    if not (p["envs"] or p["projects"] or p["folders"]):
        print("nothing to migrate")
        return 0
    if not a.apply:
        print("dry run: nothing changed. Run with --apply to carry this over.")
        return 0
    apply(root, p)
    print("done. Credentials were not touched: the developer runs nd_setup_token.py for each environment. Old zc-work is unchanged.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
