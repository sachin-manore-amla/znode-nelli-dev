#!/usr/bin/env python3
"""Capability Registry tool: list, search, show and check the registry (the source of the Supported / Customizable / Needs-platform-change verdict).

Usage
  python nd_registry.py list
  python nd_registry.py find "promotion discount"
  python nd_registry.py show promotion-extension
  python nd_registry.py check --sdk <path to the SDK clone> --webstore <path to the Webstore clone>

`check` verifies the schema and that every evidence path really exists in the repos, and exits 1 on any
failure. `verified` entries must have evidence and no missing path; `partial` entries must list what is unverified.
Registry directory: NELLIDEV_REGISTRY, else <workspace>/nd-knowledge/registry, else the registry folder next to this script's package.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

CLASSES = {"supported", "customizable", "restricted", "platform-change"}
STATUS = {"verified", "partial", "unverified"}
REQUIRED = ["id", "title", "class", "extension_type", "znode_versions", "summary", "when_to_use", "not_for", "evidence", "limitations", "platform_change_if", "verification"]
DOC_HOSTS = ("support.znode.com", "www.znode.com", "apidocs.znode.com", "learn.microsoft.com", "nextjs.org", "docs.nrwl.io", "nx.dev")


def registry_dir() -> Path:
    for c in (os.environ.get("NELLIDEV_REGISTRY"),
              str(Path(__import__('nd_ws').workspace()) / "nd-knowledge" / "registry"),
              str(Path(__file__).resolve().parents[1] / "registry")):
        if c and Path(c).is_dir() and list(Path(c).glob("*.json")):
            return Path(c)
    sys.exit("registry folder not found (set NELLIDEV_REGISTRY)")


def load() -> list[dict]:
    out = []
    for f in sorted(registry_dir().glob("*.json")):
        out.append(json.loads(f.read_text(encoding="utf-8-sig")) | {"_file": f.name})
    return out


def cmd_list(_):
    for e in load():
        print(f"{e['id']:32} {e['class']:15} {e['verification']['status']:10} {e['title']}")


def cmd_find(a):
    words = [w.lower() for w in re.split(r"\W+", a.query) if w]
    scored = []
    for e in load():
        blob = json.dumps([e["title"], e["summary"], e["when_to_use"], e["not_for"], e["extension_type"], e["id"]]).lower()
        s = sum(blob.count(w) for w in words)
        if s:
            scored.append((s, e))
    for s, e in sorted(scored, key=lambda x: -x[0]):
        print(f"{s:3}  {e['id']:30} [{e['class']}/{e['verification']['status']}] {e['summary'][:110]}")
    if not scored:
        print("no registry entry matches: treat as UNKNOWN, not as 'supported'. Search the KB and API docs, and if nothing documents it, classify as Needs platform change or ask.")


def cmd_show(a):
    e = next((x for x in load() if x["id"] == a.id), None)
    if not e:
        sys.exit("unknown id")
    e.pop("_file", None)
    print(json.dumps(e, indent=2, ensure_ascii=False))


def cmd_check(a):
    roots = {"sdk": Path(a.sdk) if a.sdk else None, "webstore": Path(a.webstore) if a.webstore else None}
    bad = warn = 0
    ids = set()
    for e in load():
        p = []
        for k in REQUIRED:
            if k not in e:
                p.append(f"missing key {k}")
        if e.get("id") in ids:
            p.append("duplicate id")
        ids.add(e.get("id"))
        if e.get("class") not in CLASSES:
            p.append(f"class must be one of {sorted(CLASSES)}")
        v = e.get("verification", {})
        if v.get("status") not in STATUS:
            p.append("verification.status invalid")
        if v.get("status") == "verified" and not e.get("evidence"):
            p.append("verified entry has no evidence")
        if v.get("status") == "partial" and not v.get("unverified"):
            p.append("partial entry must list what is unverified")
        for ev in e.get("evidence", []):
            if ev.get("repo") == "package":
                if not ev.get("path"):
                    p.append("package evidence needs the package id, version and member in path")
                continue
            if ev.get("repo") == "kb":
                if not any(h in ev.get("path", "") for h in DOC_HOSTS):
                    p.append(f"kb evidence must be a URL on an allowed host: {ev.get('path')}")
                continue
            root = roots.get(ev.get("repo"))
            if root is None:
                warn += 1
                print(f"  warn {e['id']}: repo '{ev.get('repo')}' not given, path not checked: {ev.get('path')}")
            elif not (root / ev["path"]).exists():
                p.append(f"evidence path missing: {ev['repo']}:{ev['path']}")
        for d in e.get("docs", []):
            if not any(h in d.get("url", "") for h in DOC_HOSTS):
                p.append(f"doc url host not allowed: {d.get('url')}")
        print(("FAIL " if p else "ok   ") + f"{e.get('id')}")
        for m in p:
            print("     -", m)
        bad += bool(p)
    print(f"\n{len(ids)} entries, {bad} failing, {warn} path(s) unchecked")
    sys.exit(1 if bad else 0)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list").set_defaults(fn=cmd_list)
    f = sub.add_parser("find"); f.add_argument("query"); f.set_defaults(fn=cmd_find)
    s = sub.add_parser("show"); s.add_argument("id"); s.set_defaults(fn=cmd_show)
    c = sub.add_parser("check"); c.add_argument("--sdk"); c.add_argument("--webstore"); c.set_defaults(fn=cmd_check)
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    a.fn(a)


if __name__ == "__main__":
    main()
