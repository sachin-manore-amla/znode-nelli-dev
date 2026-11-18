#!/usr/bin/env python3
"""Dependency and version-compatibility leads for a customization project (NuGet and npm manifests). Offline: no feed is contacted.

Usage
  python nd_dep_scan.py --root <project folder> [--json]

Looks at *.csproj, Directory.Packages.props, Directory.Build.props and package.json (not node_modules, bin, obj) for:
  floating or range versions, pre-release versions, one package at several versions, the Znode10.* / Znode.* packages at
  more than one version (a mixed SDK), old target frameworks, npm "latest"/"*"/git/URL dependencies, a missing lockfile.
Whether a version is vulnerable or supported by the installed Znode release is NOT decided here: run
`nd_security_scan.py --audits` (contacts the feeds; the guard asks first) and compare the Znode package versions with
the version of the developer's environment and the SDK/Webstore release notes. Exit 1 on any High lead.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nd_scan_common import PRUNE, report  # noqa: E402

OLD_TFM = re.compile(r"^(netcoreapp\d|net4\d+|net5\.0|net6\.0|net7\.0|netstandard1)", re.I)
PRE = re.compile(r"-(alpha|beta|rc|preview|pre|dev)", re.I)
ZNODE_PKG = re.compile(r"^(Znode|Znode10)\.", re.I)
LOCKFILES = ("package-lock.json", "yarn.lock", "pnpm-lock.yaml", "npm-shrinkwrap.json", "bun.lockb")


def manifests(root: Path, names=None, suffixes=()):
    out = []
    for f in root.rglob("*"):
        if f.is_file() and not any(p in PRUNE for p in f.relative_to(root).parts) and (
                (names and f.name in names) or f.suffix.lower() in suffixes):
            out.append(f)
    return sorted(out)


def lead(rule, sev, file, line, msg, text=""):
    return {"rule": rule, "sev": sev, "file": str(file), "line": line, "msg": msg, "text": text}


def scan_nuget(root: Path):
    hits, versions, tfms, scanned = [], defaultdict(dict), {}, 0
    for f in manifests(root, {"Directory.Packages.props", "Directory.Build.props"}, (".csproj",)):
        scanned += 1
        try:
            tree = ET.parse(f)
        except ET.ParseError:
            hits.append(lead("DEP-XML", "Low", f, 0, "project file could not be parsed: NOT checked"))
            continue
        for el in tree.iter():
            tag = el.tag.split("}")[-1]
            if tag in ("TargetFramework", "TargetFrameworks") and el.text:
                for t in el.text.split(";"):
                    tfms.setdefault(t.strip(), []).append(f)
                    if OLD_TFM.match(t.strip()):
                        hits.append(lead("DEP-OLD-TFM", "Medium", f, 0, f"target framework {t.strip()} is out of support: check it against the Znode release's framework", t.strip()))
            if tag in ("PackageReference", "PackageVersion"):
                name = el.get("Include") or el.get("Update")
                ver = el.get("Version") or next((c.text for c in el if c.tag.split("}")[-1] == "Version"), None)
                if not name or not ver:
                    continue
                versions[name].setdefault(ver.strip(), []).append(f)
                if "*" in ver or ver.strip().startswith(("[", "(")):
                    hits.append(lead("DEP-FLOATING", "High" if ZNODE_PKG.match(name) else "Medium", f, 0,
                                     f"{name} uses a floating or range version ({ver}): builds are not repeatable and can pick an incompatible release", f"{name} {ver}"))
                if PRE.search(ver):
                    hits.append(lead("DEP-PRERELEASE", "Medium", f, 0, f"{name} {ver} is a pre-release: confirm it is the version your Znode release ships with", f"{name} {ver}"))
    for name, vs in versions.items():
        if len(vs) > 1:
            first = sorted(vs)[0]
            hits.append(lead("DEP-MIXED-ZNODE" if ZNODE_PKG.match(name) else "DEP-MIXED", "High" if ZNODE_PKG.match(name) else "Low",
                             vs[first][0], 0, f"{name} is referenced at {len(vs)} different versions ({', '.join(sorted(vs))})"
                             + (": a mixed Znode SDK breaks at run time, align every project to one version" if ZNODE_PKG.match(name) else ""), name))
    return hits, scanned, {n: sorted(v) for n, v in versions.items() if ZNODE_PKG.match(n)}


def scan_npm(root: Path):
    hits, scanned, key = [], 0, {}
    for f in manifests(root, {"package.json"}):
        scanned += 1
        try:
            data = json.loads(f.read_text(encoding="utf-8-sig"))
        except ValueError:
            hits.append(lead("DEP-JSON", "Low", f, 0, "package.json could not be parsed: NOT checked"))
            continue
        for section in ("dependencies", "devDependencies", "optionalDependencies"):
            for name, ver in (data.get(section) or {}).items():
                v = str(ver).strip()
                if name in ("next", "react", "react-dom", "typescript", "next-auth", "next-intl"):
                    key[name] = v
                if v in ("latest", "*", "") or v.startswith(("git", "http", "github:", "file:", "link:")):
                    hits.append(lead("DEP-NPM-LATEST", "High" if v in ("latest", "*", "") else "Medium", f, 0,
                                     f"{name} is pinned to '{v}': not repeatable (or not from the registry)", f"{name} {v}"))
                elif PRE.search(v):
                    hits.append(lead("DEP-PRERELEASE", "Medium", f, 0, f"{name} {v} is a pre-release", f"{name} {v}"))
        if f.parent == root or (f.parent / "nx.json").exists():
            if not any((f.parent / lf).exists() or (root / lf).exists() for lf in LOCKFILES):
                hits.append(lead("DEP-NPM-NOLOCK", "Medium", f, 0, "no lockfile next to this package.json: installs are not repeatable and cannot be audited"))
    return hits, scanned, key


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", required=True)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    root = Path(a.root).resolve()
    if not root.is_dir():
        sys.exit(f"not a folder: {root}")
    h1, n1, znode = scan_nuget(root)
    h2, n2, npm = scan_npm(root)
    note = (f"offline manifest checks only; vulnerabilities and Znode-release compatibility are NOT decided here. "
            f"Znode packages found: {znode or 'none'}; key npm packages: {npm or 'none'}.")
    return report("Dependency scan", h1 + h2, [], [], n1 + n2, note, a.json)


if __name__ == "__main__":
    sys.exit(main())
