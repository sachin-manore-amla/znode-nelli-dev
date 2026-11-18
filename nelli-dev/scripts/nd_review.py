#!/usr/bin/env python3
"""Plan a review of customization code: resolve the target inside the developer's recorded projects, run every scanner, list the leads.

Usage
  python nd_review.py plan [--project sdk|webstore|<name>] [--diff <base ref>] [--target <path inside the project>] [--audits] [--json]
  python nd_review.py projects                       the recorded customization projects this tool may review

Scope (enforced here and by the guard): only folders recorded with nd_projects.py. A path outside them, a Znode core
repository, or any folder the developer did not record is refused. Nothing is edited, committed or sent anywhere.

What it runs: security (nd_security_scan), performance (nd_perf_scan), practice (nd_practice_scan) and dependencies
(nd_dep_scan; with --audits also the vulnerability audits, which contact the package feeds: the guard asks first).
Output: the changed or targeted files, the review skills to load for the area, the leads per check, and what was not checked.
Every lead is only a lead: the reviewer confirms each at its file:line before it becomes a finding.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nd_config  # noqa: E402
import nd_dep_scan  # noqa: E402
import nd_perf_scan  # noqa: E402
import nd_practice_scan  # noqa: E402
import nd_projects  # noqa: E402
import nd_security_scan  # noqa: E402
from nd_scan_common import SEV, git_changed, run_rules, walk  # noqa: E402

CS, TS = (".cs",), (".ts", ".tsx", ".js", ".jsx", ".mjs")
SKILLS = {
    "sdk": ["review-sdk", "sdk-conventions", "sdk-custom-api", "quality-security-checks", "quality-performance-checks", "api-auth-and-headers"],
    "webstore": ["review-webstore", "webstore-customization", "quality-security-checks", "quality-performance-checks", "api-auth-and-headers"],
}


def inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def recorded(root) -> list[dict]:
    out = []
    for p in nd_config.projects(root):
        path = Path(p["path"])
        out.append({"name": p["name"], "path": path, "kind": p.get("kind") or nd_projects.kind(path) or "other", "exists": path.is_dir()})
    return out


def pick(projects, name):
    if name:
        return [p for p in projects if p["name"] == name] or [p for p in projects if p["kind"] == name]
    return [p for p in projects if p["kind"] in ("sdk", "webstore")]


def lead_sort(h):
    return (SEV[h["sev"]], h["file"], h["line"])


def review_project(p: dict, base, target, audits: bool) -> dict:
    root = p["path"]
    if base:
        paths = [f for f in git_changed(str(root), base) if inside(Path(f), root)]
        scope = f"files changed against {base}"
    elif target:
        t = Path(target)
        t = t if t.is_absolute() else root / t
        if not inside(t, root):
            sys.exit(f"refusing: {t} is not inside the recorded project {p['name']} ({root}).")
        paths, scope = [str(t)], f"{t}"
    else:
        paths, scope = [str(root)], "the whole project"
    files, skipped = walk(paths, CS + TS)
    sec, unread = run_rules(files, nd_security_scan.RULES)
    sec += nd_security_scan.ownership_leads(files)
    if audits:
        sec += nd_security_scan.audits([str(root)])
    perf, _ = run_rules(files, nd_perf_scan.RULES)
    perf += nd_perf_scan.loop_leads(files)
    prac, _ = run_rules(files, nd_practice_scan.RULES)
    prac += (nd_practice_scan.catch_leads(files) + nd_practice_scan.controller_leads(files)
             + nd_practice_scan.registration_leads(files, root) + nd_practice_scan.route_leads(files)
             + nd_practice_scan.client_gateway_leads(files) + nd_practice_scan.shared_pkg_leads([str(f) for f in files]))
    dh1, _, znode = nd_dep_scan.scan_nuget(root)
    dh2, _, npm = nd_dep_scan.scan_npm(root)
    leads = {"security": sorted(sec, key=lead_sort), "performance": sorted(perf, key=lead_sort),
             "practice": sorted(prac, key=lead_sort), "dependencies": sorted(dh1 + dh2, key=lead_sort)}
    nots = ["run-time behaviour, latency and load", "data flow (the scanners are pattern-based)", "vulnerabilities in packages"
            + ("" if audits else " (--audits was not run)"), "whether the packages match the developer's Znode release"]
    if skipped:
        nots.append(f"{len(skipped)} binary file(s)")
    if unread:
        nots.append(f"{len(unread)} unreadable file(s)")
    return {"project": p["name"], "kind": p["kind"], "path": str(root), "scope": scope, "files": [str(f) for f in files],
            "skills_to_load": SKILLS.get(p["kind"], ["quality-security-checks", "quality-performance-checks"]),
            "znode_packages": znode, "npm_key_packages": npm, "leads": leads,
            "counts": {k: {s: sum(1 for h in v if h["sev"] == s) for s in SEV if any(h["sev"] == s for h in v)} for k, v in leads.items()},
            "not_checked": nots}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("projects")
    pl = sub.add_parser("plan")
    pl.add_argument("--project")
    pl.add_argument("--diff")
    pl.add_argument("--target")
    pl.add_argument("--audits", action="store_true")
    pl.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    root = __import__("nd_ws").workspace()
    projects = recorded(root)
    if a.cmd == "projects":
        for p in projects:
            print(f"{p['name']:10} {p['kind']:9} {p['path']}" + ("" if p["exists"] else "  MISSING"))
        return 0 if projects else 1
    if not projects:
        sys.exit("no customization project is recorded: run /nelli-dev:setup (the reviewer only reviews the folders the developer recorded).")
    chosen = pick(projects, a.project)
    if not chosen:
        sys.exit(f"no recorded project named or of kind {a.project!r}; recorded: " + ", ".join(p["name"] for p in projects))
    if (a.target or a.diff) and len(chosen) > 1:
        sys.exit("--target and --diff need one project: pass --project <name>.")
    results = [review_project(p, a.diff, a.target, a.audits) for p in chosen if p["exists"]]
    if a.json:
        print(json.dumps({"projects": results}, indent=1))
        return 0
    for r in results:
        print(f"## {r['project']} ({r['kind']}) {r['path']}\nscope: {r['scope']} · {len(r['files'])} file(s)\nload skills: {', '.join(r['skills_to_load'])}")
        for k, v in r["leads"].items():
            print(f"\n[{k}] {len(v)} lead(s) {r['counts'][k] or ''}")
            for h in v[:40]:
                print(f"  [{h['sev']}] {h['rule']} {h['file']}:{h['line']}  {h['msg']}")
            if len(v) > 40:
                print(f"  ... {len(v) - 40} more (use --json)")
        print("\nnot checked: " + "; ".join(r["not_checked"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
