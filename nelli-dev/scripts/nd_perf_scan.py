#!/usr/bin/env python3
"""Performance leads for a customization: N+1 calls, sync-over-async, sequential independent fetches, heavy imports, missing caching.

Usage
  python nd_perf_scan.py --paths Custom.Api.Core apps/webstore/src [--git-diff origin/main --repo .] [--json]

Leads only. Static analysis cannot measure latency: confirm a lead by tracing the user action or by
running a measured test (see the quality-performance-checks skill). Exit 1 on any High lead.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nd_scan_common import Rule, git_changed, read, report, run_rules, walk  # noqa: E402

CS = (".cs",)
TS = (".ts", ".tsx", ".js", ".jsx", ".mjs")
RULES = [
    Rule("PERF-SYNC-ASYNC", "High", re.compile(r"\.Result\b(?!\w)|\.Wait\s*\(\)|GetAwaiter\(\)\.GetResult\(\)"), "blocks a thread on async work (deadlock and thread-starvation risk)", CS),
    Rule("PERF-HTTPCLIENT", "High", re.compile(r"new\s+HttpClient\s*\("), "new HttpClient per call exhausts sockets: use IHttpClientFactory or the registered Znode client", CS),
    Rule("PERF-TOLIST-EARLY", "Medium", re.compile(r"\.ToList\(\)\s*\.\s*(?:Where|Select|Any|Count|FirstOrDefault)\("), "materializes the whole set before filtering", CS),
    Rule("PERF-COUNT", "Low", re.compile(r"\.Count\(\)\s*(?:>|>=|==|!=)\s*[01]\b"), "use Any() instead of a Count() comparison", CS),
    Rule("PERF-NOSTORE", "Medium", re.compile(r"cache\s*:\s*['\"]no-store['\"]|revalidate\s*:\s*0|dynamic\s*=\s*['\"]force-dynamic['\"]"), "opts out of caching: confirm the data truly must be fresh on every request", TS),
    Rule("PERF-HEAVY-IMPORT", "Medium", re.compile(r"import\s+(?:\*\s+as\s+\w+|\w+)\s+from\s+['\"](?:lodash|moment|rxjs)['\"]"), "whole-library import grows the bundle: import the function or use a lighter library", TS),
    Rule("PERF-USEEFFECT-FETCH", "Medium", re.compile(r"useEffect\s*\(\s*\(\)\s*=>\s*\{?[^}]*fetch\s*\("), "client-side fetch in an effect: consider fetching on the server", TS),
]
LOOP_CS = re.compile(r"^\s*(?:foreach|for|while)\s*\(|\.ForEach\s*\(")
LOOP_TS = re.compile(r"\bfor\s*\(|\bfor\s+await\s*\(|\.forEach\s*\(|\.map\s*\(\s*async")
CALL_CS = re.compile(r"await\s+[\w.]*(?:Client|Repository|Service|Cache|Context)\w*\.\w+|await\s+_\w+\.\w+Async|await\s+\w+\.\w+Async")
CALL_TS = re.compile(r"await\s+(?:fetch|axios|\w*[Cc]lient\.\w+|\w*[Ss]ervice\.\w+|\w*Api\w*\()")
SEQ_TS = re.compile(r"=\s*await\s+(?:fetch|\w*[Cc]lient\.\w+|\w*Api\w*\()")


def loop_leads(files):
    out = []
    for f in files:
        ext = f.suffix.lower()
        lines = read(f) or []
        loop, call = (LOOP_CS, CALL_CS) if ext in CS else (LOOP_TS, CALL_TS)
        for n, line in enumerate(lines, 1):
            if loop.search(line):
                for m in range(n, min(n + 14, len(lines))):
                    if call.search(lines[m]):
                        out.append({"rule": "PERF-N+1", "sev": "High", "file": str(f), "line": m + 1, "text": lines[m].strip()[:140],
                                    "msg": "remote/DB call inside a loop (N+1): batch the call, or fetch once before the loop"})
                        break
        if ext in TS:
            run = 0
            for n, line in enumerate(lines, 1):
                if SEQ_TS.search(line):
                    run += 1
                    if run == 3:
                        out.append({"rule": "PERF-SEQUENTIAL", "sev": "Medium", "file": str(f), "line": n, "text": line.strip()[:140],
                                    "msg": "3+ awaited calls in a row: if independent, run them with Promise.all"})
                elif line.strip() and not line.strip().startswith(("//", "const ", "let ", "}")):
                    run = 0
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--paths", nargs="*", default=[])
    ap.add_argument("--git-diff")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    paths = a.paths + (git_changed(a.repo, a.git_diff) if a.git_diff else [])
    if not paths:
        ap.error("give --paths or --git-diff")
    files, skipped = walk(paths, CS + TS)
    hits, unreadable = run_rules(files, RULES)
    hits += loop_leads(files)
    return report("Performance scan", hits, unreadable, skipped, len(files),
                  "static leads only; no latency or load is measured. The loop check looks 14 lines ahead and can miss calls hidden in helpers, or flag cached calls. Confirm with a trace or a measured test before reporting a finding.", a.json)


if __name__ == "__main__":
    sys.exit(main())
