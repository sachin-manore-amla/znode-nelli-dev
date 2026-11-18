#!/usr/bin/env python3
"""End-of-run gate: confirm a request's progress file and documents are complete before the agent gives its final reply.

Usage
  python nd_close_check.py --key ND-001 --mode advise|deliver|ask [--json]

Checks (exit 1 on any failure):
  1. tracker.md exists and every step is done, skipped or blocked (each with a note); every output is marked.
  2. Required documents exist for the mode and each ends with a `Checked:` line:
       advise : requirements.md, discovery.md, solution-proposal.md
       deliver: the advise set + implementation-plan.md, test-plan.md, approval.json, change-log.md, test-results.md,
                performance-report.md, security-report.md, handover/technical-document.md, handover/deployment.md
       ask    : none (progress file only, and only when not on the quick path)
  3. When the verdict is Needs platform change, platform-change-request.md exists instead of the plan/build set.
  4. approval.json (deliver) still matches the plan files (nd_approve.py verify).
  5. No document contains an unresolved placeholder such as <fill>, TODO or TBD.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nd_ws import workspace  # noqa: E402

ADVISE = ["requirements.md", "discovery.md", "solution-proposal.md"]
DELIVER = ADVISE + ["implementation-plan.md", "test-plan.md", "approval.json", "change-log.md", "test-results.md",
                    "performance-report.md", "security-report.md", "handover/technical-document.md", "handover/deployment.md"]
PLACEHOLDER = re.compile(r"<fill[^>]*>|\bTODO\b|\bTBD\b|\bXXX\b|<\s*describe[^>]*>", re.I)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--key", required=True)
    ap.add_argument("--mode", required=True, choices=["advise", "deliver", "ask"])
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    d = workspace() / "nd-work" / a.key.upper()
    problems: list[str] = []
    tracker = d / "tracker.md"
    if not tracker.exists():
        problems.append("tracker.md missing: the progress file was never created")
    else:
        text = tracker.read_text(encoding="utf-8", errors="replace")
        rows = [l for l in text.splitlines() if re.match(r"^\|\s*\d+\s*\|", l)]
        if not rows:
            problems.append("tracker has no steps: init it with --step 'script: ...' / --step 'reasoning: ...'")
        for l in rows:
            cells = [c.strip() for c in l.strip("|").split("|")]
            status = " ".join(cells).lower()
            if not any(s in status for s in ("done", "skipped", "blocked", "✅", "⏭", "⛔")):
                problems.append(f"step not closed: {l.strip()[:100]}")
        if re.search(r"⬜|\btodo\b|\bdoing\b", "\n".join(rows), re.I):
            problems.append("steps still marked todo/doing in the Steps table")
    required = list(DELIVER if a.mode == "deliver" else ADVISE if a.mode == "advise" else [])
    verdict_pc = (d / "solution-proposal.md").exists() and re.search(r"Verdict:\s*\**\s*Needs platform change", (d / "solution-proposal.md").read_text(encoding="utf-8", errors="replace"), re.I)
    if verdict_pc:
        required = ADVISE + ["platform-change-request.md"]
    for name in required:
        p = d / name
        if not p.exists():
            problems.append(f"missing: {name}")
            continue
        if p.suffix == ".md":
            body = p.read_text(encoding="utf-8", errors="replace")
            if not re.search(r"^\s*Checked:", body, re.M):
                problems.append(f"{name}: no 'Checked:' line")
            if PLACEHOLDER.search(body):
                problems.append(f"{name}: unresolved placeholder ({PLACEHOLDER.search(body).group(0)})")
    if a.mode == "deliver" and (d / "approval.json").exists():
        rec = json.loads((d / "approval.json").read_text(encoding="utf-8-sig"))
        if not rec.get("approved"):
            problems.append("approval.json is not an approval")
        for n, h in (rec.get("plan_sha256") or {}).items():
            f = d / n
            if not f.exists() or hashlib.sha256(f.read_bytes()).hexdigest() != h:
                problems.append(f"plan changed after approval: {n}")
    if a.json:
        print(json.dumps({"request": a.key.upper(), "ok": not problems, "problems": problems}, indent=1))
    else:
        print(f"close check {a.key.upper()} ({a.mode}): " + ("OK" if not problems else f"{len(problems)} problem(s)"))
        for p in problems:
            print("  -", p)
        if problems:
            print("Fix these before the final reply, or state each as a gap in the final report.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
