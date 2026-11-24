#!/usr/bin/env python3
"""Classify files or diff hunks as ZNODE-RELEVANT or GENERIC before a Nelli-Dev review.

Nelli-Dev reviews Znode customizations only. This tool gives the reviewing agent a first sort of the review target so that
generic code (style, naming, formatting, language idioms, unrelated architecture) is left out and only the Znode-specific
parts are reviewed.

IMPORTANT: the output gives LEADS, NOT FACTS. A file is marked ZNODE-RELEVANT when concrete signals match (see SIGNALS) and
GENERIC when none do. Both can be wrong: a signal can appear in a comment, and a customization can be hidden behind an
indirection the patterns do not see. The reviewing agent must confirm each classification by reading the file (or the hunk)
before it reports a finding or lists the file as "out of scope: generic". Confidence "low" means only weak signals matched.

Usage
  python nd_review_scope.py <path-or-file> [more paths] [--json] [--request "<what the developer asked>"]
  python nd_review_scope.py --files-from list.txt            one path per line
  python nd_review_scope.py --git-diff <ref> [--repo <dir>]  classify the hunks of `git diff <ref>` (read-only git)
  python nd_review_scope.py --diff-file patch.diff|-         classify a unified diff from a file or stdin

Secret files are never read: .env*, keys, certificates, keystores, feed config, local settings and credential files are
skipped by name and reported as "skipped (secret file)". appsettings*.json is read for KEY NAMES only (no value is kept
or printed). Matched text is never echoed except short code identifiers; nothing is edited, sent or executed (the only
subprocess is the read-only `git diff` when --git-diff is used).

Output: a text summary (default) or JSON (--json): per file classification, confidence, areas, signals with line numbers,
per-hunk results for diffs, files skipped, and the fixed decline message when nothing Znode-relevant is in the target or
the request asks only for generic review.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path

DECLINE = ("Nelli-Dev reviews Znode customizations only (SDK extension points, Webstore customizations, Znode API usage, "
           "security and performance of those). For general code quality, style or language review, please use your own "
           "code review tools.")

DISCLAIMER = "Leads, not facts: the reviewer must confirm each classification by reading the file."

MAX_BYTES = 1_000_000
SKIP_DIRS = {"node_modules", "bin", "obj", ".git", "dist", ".next", "coverage", "nd-work", ".vs", ".idea", "__pycache__", ".nuget", "out"}
REVIEW_EXT = {".cs", ".csproj", ".props", ".targets", ".json", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".yml", ".yaml",
              ".config", ".xml", ".sql", ".css", ".scss", ".md", ".txt", ".html", ".cshtml"}
LOCKFILES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "packages.lock.json"}
SECRET_PATTERNS = [".env", ".env.*", "*.env", "*.pem", "*.key", "*.pfx", "*.p12", "*.cer", "*.crt", "*.der", "*.jks", "*.keystore",
                   "*.pkcs12", "*.p8", "*.ppk", "id_rsa*", "id_ed25519*", "id_ecdsa*", "secrets.json", "*.secret", "*.secrets",
                   "credentials*", ".npmrc", ".netrc", "nuget.config", "local.settings.json", "launchsettings.json", "*.user",
                   "*.publishsettings"]


def is_secret_name(path: str) -> bool:
    name = path.replace("\\", "/").rsplit("/", 1)[-1].lower()
    return any(fnmatch.fnmatch(name, p) for p in SECRET_PATTERNS)


# --- signals ---------------------------------------------------------------------------------------------------------
# (id, area, strength, regex, applies-to) ; applies-to: a tuple of extensions or None for all reviewable text files.
CODE = (".cs", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".cshtml")
PROJ = (".csproj", ".props", ".targets", ".config", ".xml")
I = re.I
SIGNALS = [
    # Custom API SDK and Znode namespaces / types
    ("znode-namespace", "SDK extension points", "strong", re.compile(r"\b(?:using|namespace)\s+(?:Znode10?\.|Znode\.|Custom\.Api)[\w.]*"), (".cs", ".cshtml")),
    ("custom-api-reference", "SDK extension points", "strong", re.compile(r"\bCustom\.Api[\w.]*|\bCustom\.Admin[\w.]*"), CODE + PROJ),
    ("znode-type", "SDK extension points", "strong", re.compile(r"\b(?:I)?Znode[A-Z]\w+"), (".cs", ".cshtml")),
    ("method-override", "method overrides", "strong", re.compile(r"\b(?:SkipExecution|IMethodOverride\w*|MethodOverride\w*)\b"), (".cs",)),
    ("event-consumer", "events", "weak", re.compile(r"\bIConsumer<\s*\w+|\[WebhookReceiver|\bConsumeContext<"), (".cs",)),
    ("capability-registry-id", "SDK extension points", "weak",
     re.compile(r"\b(?:custom-endpoint|custom-table|event-consumer|method-override|ocelot-route|direct-data-access|data-exchange(?:-processor)?|"
                r"promotion-extension|erp-touchpoint|admin-customization|global-attribute-udf|page-builder-and-theme|plugin-templates|"
                r"product-information-overrides|events-and-webhooks)\b"), None),
    # Znode API families, headers, routes
    ("znode-header", "API usage", "strong", re.compile(r"\bZnode-(?:AccountId|UserId|PortalCode|StoreCode|CatalogCode|LocaleCode|DomainName|PublishState)\b", I), None),
    ("znode-api-config", "API usage", "strong",
     re.compile(r"\b(?:ZnodeApiRootUri|ZnodeApiV2RootUri|ZnodeApiGateway|ZnodeCommercePortalRootUri|CustomAPIRootUri|IdorRequestHeaderEncryptionKey)\b"), None),
    ("znode-api-route", "API usage", "strong",
     re.compile(r"[\"'`/](?:commerceapi|commerceportal|znodeengineapiv2|multifrontapi|customapi|cpapi)/", I), None),
    ("znode-versioned-route", "API usage", "strong",
     re.compile(r"[\"'`/]v[12]/(?:accounts?|orders?|carts?|catalogs?|products?|portals?|stores?|pricelists?|prices?|promotions?|vouchers?|"
                r"inventor(?:y|ies)|warehouses?|categories|brands?|custom-?tables?|quotes?|returns?|users?|publish\w*|shipping\w*|tax\w*)\b", I), None),
    ("client-supplied-identity-header", "authentication (client-supplied identity)", "strong",
     re.compile(r"(?:Request\.Headers|\.headers\.get|headers\(\)\.get|Headers\.TryGetValue|\bHeaders\[)[^;\n]{0,60}"
                r"Znode-(?:UserId|AccountId|PortalCode|StoreCode)", I), None),
    # Ocelot
    ("ocelot-route", "gateway routes", "strong", re.compile(r"\"(?:UpstreamPathTemplate|DownstreamPathTemplate|DownstreamHostAndPorts)\""), (".json",)),
    # Webstore
    ("webstore-env", "Webstore customization", "strong",
     re.compile(r"\b(?:API_V2_DOMAIN|API_DOMAIN|ZNODE_REVALIDATE_TOKEN|ZNODE_DEBUG_TOKEN|WEBSTORE_DOMAIN_NAME)\b"), None),
    ("page-builder", "Webstore customization", "strong", re.compile(r"@puckeditor/core"), CODE + (".json",)),
    ("webstore-package", "Webstore customization", "strong", re.compile(r"[\"'](?:@znode[\w./-]*)[\"']", I), CODE + (".json",)),
    ("cache-tag-or-revalidate", "caching and publish", "weak", re.compile(r"\brevalidateTag\s*\(|\brevalidatePath\s*\(|next\s*:\s*\{[^}]*\btags\b"), CODE),
    ("public-env-secret", "secrets", "weak", re.compile(r"NEXT_PUBLIC_\w*(?:SECRET|TOKEN|KEY|PASSWORD)\w*"), CODE + (".json",)),
    ("direct-data-access", "bypassing Znode", "weak", re.compile(r"\b(?:SqlConnection|SqlCommand|FromSqlRaw|ExecuteSqlRaw|ExecuteSqlInterpolated)\b"), (".cs",)),
    ("znode-table-or-db", "bypassing Znode", "strong", re.compile(r"\bZnode_Entities\b|\bZnodeECommerceDB\b|\bZnode(?:Oms|Order|Publish|Pim|Cms|User|Portal)[A-Z]\w*"), None),
    # Package edits (project files)
    ("znode-package-reference", "NuGet packages and version", "strong",
     re.compile(r"<(?:PackageReference|PackageVersion)\b[^>]*\bInclude\s*=\s*\"Znode(?:10)?\.[\w.]+\"", I), PROJ),
    ("znode-assembly-reference", "NuGet packages (edited or copied)", "strong",
     re.compile(r"<(?:Reference|ProjectReference)\b[^>]*\bInclude\s*=\s*\"[^\"]*Znode[\w.\\/-]*\"|<HintPath>[^<]*Znode", I), PROJ),
]
PATH_SIGNALS = [
    ("path-webstore-clients", "Webstore customization", "strong", re.compile(r"(?:^|/)packages/(?:clients|base-components|agents|cache)/")),
    ("path-ocelot-file", "gateway routes", "strong", re.compile(r"(?:^|/)ocelot[\w.-]*\.json$")),
    ("path-bff-route", "Webstore BFF routes", "weak", re.compile(r"(?:^|/)app/api/.+/route\.(?:ts|js)$")),
    ("path-sdk-folder", "SDK extension points", "weak", re.compile(r"(?:^|/)Custom\.Api[\w.]*/", I)),
]
APPSETTINGS_KEY = re.compile(r"^(?:Znode\w*|CustomAPI\w*|CustomApi\w*|IdorRequestHeaderEncryptionKey|Ocelot|MicroServices)$", I)
KEY_RE = re.compile(r"\"([^\"\\]{1,80})\"\s*:")

GENERIC_WORDS = re.compile(r"\b(?:style|styles|naming|formatting|format|lint|linter|idiom|idioms|refactor\w*|clean code|readability|"
                           r"best practices|code smell\w*|solid|linq|c#|\.net|dotnet|react|typescript|javascript|code quality|"
                           r"general review|generic review|variable names?)\b", I)
ZNODE_WORDS = re.compile(r"\b(?:znode|sdk|webstore|extension|override\w*|event consumer|consumer|custom api|bff|cache|caching|publish|"
                         r"tenan\w*|authenticat\w*|authoriz\w*|secret\w*|header\w*|ocelot|nuget|package\w*|portal|catalog|order|cart|"
                         r"api usage|registry|customization)\b", I)


def request_intent(text: str | None) -> str:
    if not text:
        return "unspecified"
    g, z = bool(GENERIC_WORDS.search(text)), bool(ZNODE_WORDS.search(text))
    return "mixed" if g and z else "generic-only" if g else "znode" if z else "unspecified"


def norm(p: str) -> str:
    return p.replace("\\", "/")


def match_lines(text: str, ext: str, rel: str) -> list[dict]:
    out: list[dict] = []
    seen: dict[str, int] = {}
    lines = text.splitlines()
    for sid, area, strength, rx, exts in SIGNALS:
        if exts is not None and ext not in exts:
            continue
        for n, line in enumerate(lines, 1):
            if len(line) > 2000:
                line = line[:2000]
            m = rx.search(line)
            if m and seen.get(sid, 0) < 3:
                seen[sid] = seen.get(sid, 0) + 1
                tok = m.group(0)
                tok = tok if len(tok) <= 60 else tok[:57] + "..."
                out.append({"id": sid, "area": area, "strength": strength, "line": n, "match": tok})
    return out


def appsettings_signals(text: str) -> list[dict]:
    """Key names only. No value is read into the result."""
    out, n_seen = [], 0
    for n, line in enumerate(text.splitlines(), 1):
        for key in KEY_RE.findall(line):
            if APPSETTINGS_KEY.match(key) and n_seen < 5:
                n_seen += 1
                out.append({"id": "appsettings-znode-key", "area": "configuration (Znode keys)", "strength": "strong", "line": n, "match": key})
    return out


def classify_text(rel: str, text: str) -> list[dict]:
    r = norm(rel)
    ext = Path(r).suffix.lower()
    name = r.rsplit("/", 1)[-1].lower()
    sig: list[dict] = []
    if re.match(r"appsettings[\w.-]*\.json$", name):
        return appsettings_signals(text)
    if ext in (".md", ".txt"):
        return []
    sig += match_lines(text, ext, r)
    return sig


def path_signals(rel: str) -> list[dict]:
    r = norm(rel)
    return [{"id": sid, "area": area, "strength": st, "line": 0, "match": r.rsplit("/", 1)[-1]} for sid, area, st, rx in PATH_SIGNALS if rx.search(r)]


def verdict(sigs: list[dict]) -> tuple[str, str]:
    if not sigs:
        return "GENERIC", "none"
    return "ZNODE-RELEVANT", "high" if any(s["strength"] == "strong" for s in sigs) else "low"


def summarize(sigs: list[dict]) -> list[str]:
    return sorted({s["area"] for s in sigs})


def read_text(path: Path) -> str | None:
    try:
        if path.stat().st_size > MAX_BYTES:
            return None
        data = path.read_bytes()
        if b"\x00" in data[:4096]:
            return None
        return data.decode("utf-8", errors="replace")
    except OSError:
        return None


def collect(paths: list[str]) -> tuple[list[Path], list[tuple[str, str]]]:
    files: list[Path] = []
    skipped: list[tuple[str, str]] = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            for f in sorted(p.rglob("*")):
                if any(part in SKIP_DIRS for part in f.relative_to(p).parts[:-1]) or not f.is_file():
                    continue
                files.append(f)
        elif p.is_file():
            files.append(p)
        else:
            skipped.append((raw, "not found"))
    return files, skipped


def classify_files(files: list[Path], base: Path | None) -> tuple[list[dict], list[tuple[str, str]]]:
    results, skipped = [], []
    for f in files:
        rel = norm(str(f if base is None else _rel(f, base)))
        if is_secret_name(rel):
            skipped.append((rel, "skipped (secret file): not read"))
            continue
        name = f.name.lower()
        if name in LOCKFILES or name.endswith(".min.js"):
            skipped.append((rel, "skipped (lockfile or minified): not reviewable"))
            continue
        if f.suffix.lower() not in REVIEW_EXT:
            skipped.append((rel, "skipped (not a reviewable text type)"))
            continue
        text = read_text(f)
        if text is None:
            skipped.append((rel, "skipped (binary, too large or unreadable)"))
            continue
        sigs = path_signals(rel) + classify_text(rel, text)
        c, conf = verdict(sigs)
        results.append({"path": rel, "classification": c, "confidence": conf, "areas": summarize(sigs), "signals": sigs})
    return results, skipped


def _rel(f: Path, base: Path) -> Path:
    try:
        return f.resolve().relative_to(base.resolve())
    except ValueError:
        return f


# --- diff mode ------------------------------------------------------------------------------------------------------
HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@(.*)$")


def parse_diff(text: str) -> dict[str, list[dict]]:
    files: dict[str, list[dict]] = {}
    cur: str | None = None
    hunk: dict | None = None
    for line in text.splitlines():
        if line.startswith("diff --git "):
            m = re.match(r"diff --git a/(.*?) b/(.*)$", line)
            cur = m.group(2) if m else None
            hunk = None
            if cur is not None:
                files.setdefault(cur, [])
        elif line.startswith("+++ ") and not line.startswith("+++ /dev/null"):
            cur = line[4:].strip()
            cur = cur[2:] if cur.startswith("b/") else cur
            files.setdefault(cur, [])
        elif cur is not None and (m := HUNK.match(line)):
            hunk = {"start": int(m.group(1)), "header": m.group(2).strip(), "lines": []}
            files[cur].append(hunk)
        elif hunk is not None and cur is not None and line[:1] in ("+", "-", " "):
            hunk["lines"].append(line[1:])
    return files


def classify_diff(text: str, repo: Path | None) -> tuple[list[dict], list[tuple[str, str]]]:
    results, skipped = [], []
    for rel, hunks in parse_diff(text).items():
        if is_secret_name(rel):
            skipped.append((rel, "skipped (secret file): hunks not read"))
            continue
        if Path(rel).name.lower() in LOCKFILES:
            skipped.append((rel, "skipped (lockfile)"))
            continue
        hres, allsig = [], path_signals(rel)
        for h in hunks:
            body = "\n".join([h["header"]] + h["lines"])
            sigs = classify_text(rel, body)
            c, conf = verdict(sigs)
            hres.append({"start_line": h["start"], "classification": c, "confidence": conf, "signals": sigs})
            allsig += sigs
        file_sigs_extra: list[dict] = []
        if repo is not None:  # whole-file context, when the file is on disk and not a secret
            disk = repo / rel
            text_disk = read_text(disk) if disk.is_file() else None
            if text_disk is not None:
                file_sigs_extra = [s for s in classify_text(rel, text_disk)]
        sigs_all = allsig + [s for s in file_sigs_extra if s not in allsig]
        c, conf = verdict(sigs_all)
        results.append({"path": norm(rel), "classification": c, "confidence": conf, "areas": summarize(sigs_all),
                        "signals": sigs_all[:12], "hunks": hres})
    return results, skipped


def git_diff(ref: str, repo: Path) -> str:
    # Read-only. Secret files are excluded from the diff itself so their content never enters this process.
    excludes = [f":(exclude,glob)**/{p}" for p in SECRET_PATTERNS]
    cmd = ["git", "-C", str(repo), "diff", "--no-color", "-U3", ref, "--", "."] + excludes
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    if r.returncode != 0:
        raise SystemExit(f"git diff failed: {r.stderr.strip()[:300]}")
    return r.stdout


# --- output ---------------------------------------------------------------------------------------------------------
def build(results, skipped, intent) -> dict:
    rel = [r for r in results if r["classification"] == "ZNODE-RELEVANT"]
    gen = [r for r in results if r["classification"] == "GENERIC"]
    secret = [s for s in skipped if "secret" in s[1]]
    out = {
        "tool": "nd_review_scope", "disclaimer": DISCLAIMER, "request_intent": intent,
        "counts": {"znode_relevant": len(rel), "generic": len(gen), "skipped": len(skipped), "skipped_secret": len(secret)},
        "files": results, "skipped": [{"path": p, "reason": r} for p, r in skipped],
        "out_of_scope_generic": [r["path"] for r in gen],
    }
    if intent == "generic-only" or not rel:
        out["decline_message"] = DECLINE
    return out


def text_summary(o: dict) -> str:
    c = o["counts"]
    lines = [f"Review scope (leads, not facts: confirm each by reading the file). Request intent: {o['request_intent']}.",
             f"ZNODE-RELEVANT {c['znode_relevant']} | GENERIC {c['generic']} | skipped {c['skipped']} (secret files {c['skipped_secret']})"]
    for r in o["files"]:
        if r["classification"] == "ZNODE-RELEVANT":
            ids = ", ".join(sorted({s["id"] for s in r["signals"]}))
            lines.append(f"  RELEVANT ({r['confidence']}) {r['path']}  [{'; '.join(r['areas'])}]  signals: {ids}")
    for p in o["out_of_scope_generic"]:
        lines.append(f"  out of scope: generic  {p}")
    for s in o["skipped"]:
        lines.append(f"  {s['reason']}  {s['path']}")
    if "decline_message" in o:
        lines.append("Say: " + o["decline_message"])
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Classify review targets as ZNODE-RELEVANT or GENERIC (leads, not facts).")
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--files-from")
    ap.add_argument("--git-diff", metavar="REF")
    ap.add_argument("--diff-file", metavar="FILE")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--request", help="the developer's request text, to detect a generic-only ask")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8")
        except Exception:
            pass
    repo = Path(a.repo)
    if a.git_diff:
        results, skipped = classify_diff(git_diff(a.git_diff, repo), repo)
    elif a.diff_file:
        txt = sys.stdin.read() if a.diff_file == "-" else Path(a.diff_file).read_text(encoding="utf-8", errors="replace")
        results, skipped = classify_diff(txt, repo if a.repo != "." else None)
    else:
        paths = list(a.paths)
        if a.files_from:
            paths += [l.strip() for l in Path(a.files_from).read_text(encoding="utf-8").splitlines() if l.strip()]
        if not paths:
            ap.error("give a path, --files-from, --git-diff or --diff-file")
        files, miss = collect(paths)
        base = Path(paths[0]) if len(paths) == 1 and Path(paths[0]).is_dir() else None
        results, skipped = classify_files(files, base)
        skipped += miss
    out = build(results, skipped, request_intent(a.request))
    print(json.dumps(out, indent=2) if a.json else text_summary(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
