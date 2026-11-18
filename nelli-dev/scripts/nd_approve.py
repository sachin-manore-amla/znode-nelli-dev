#!/usr/bin/env python3
"""Record the developer's approval of the plan, bound to the exact plan files, so edits can begin (the guard checks this file).

Usage
  python nd_approve.py grant  --request ND-001 --by "<developer name>" --scope "Custom.Api.Core/*" --scope "apps/webstore/src/*"
  python nd_approve.py verify --request ND-001      # exit 1 if a plan file changed after approval
  python nd_approve.py revoke --request ND-001

Run `grant` ONLY after the developer has answered "approve" to the plan. Writing approval.json also
triggers a confirmation prompt from the guard, so the developer confirms it a second time on screen.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import sys
from pathlib import Path

PLAN_FILES = ("solution-proposal.md", "implementation-plan.md", "test-plan.md")


def folder(req: str) -> Path:
    return Path(__import__('nd_ws').workspace()) / "nd-work" / req.upper()


def digests(d: Path) -> dict:
    return {n: hashlib.sha256((d / n).read_bytes()).hexdigest() for n in PLAN_FILES if (d / n).exists()}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["grant", "verify", "revoke"])
    ap.add_argument("--request", required=True)
    ap.add_argument("--by")
    ap.add_argument("--scope", action="append", default=[])
    a = ap.parse_args()
    d = folder(a.request)
    f = d / "approval.json"
    if a.cmd == "grant":
        dg = digests(d)
        if "solution-proposal.md" not in dg or "implementation-plan.md" not in dg:
            sys.exit("refusing: solution-proposal.md and implementation-plan.md must exist in " + str(d))
        ws = Path(os.environ.get("NELLIDEV_WORKSPACE") or os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd()).resolve()
        scope = []
        for s in a.scope:
            n = s.replace("\\", "/")
            try:  # an absolute glob inside the workspace becomes workspace-relative
                if os.path.isabs(n) and os.path.normcase(n).startswith(os.path.normcase(str(ws).replace("\\", "/")) + "/"):
                    n = n[len(str(ws).replace("\\", "/")) + 1:]
            except OSError:
                pass
            scope.append(n)
        f.write_text(json.dumps({"approved": True, "by": a.by or "(unnamed)", "at": datetime.datetime.now().isoformat(timespec="seconds"),
                                 "scope": scope, "plan_sha256": dg}, indent=1), encoding="utf-8")
        print("approval recorded:", f)
    elif a.cmd == "revoke":
        if f.exists():
            f.write_text(json.dumps({"approved": False}), encoding="utf-8")
        print("approval revoked")
    else:
        if not f.exists():
            sys.exit("no approval recorded")
        rec = json.loads(f.read_text(encoding="utf-8"))
        if not rec.get("approved"):
            sys.exit("not approved")
        now = digests(d)
        changed = [n for n, h in rec.get("plan_sha256", {}).items() if now.get(n) != h]
        if changed:
            print("PLAN CHANGED after approval:", ", ".join(changed), "- ask the developer to approve again")
            return 1
        print("approval valid; plan unchanged since", rec["at"], "by", rec["by"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
