#!/usr/bin/env python3
"""Nelli-Dev consent: what, if anything, the developer agrees may be shared. Stored in the central config under "consent".

Levels
  off             (default) nothing leaves the machine; only the local ledger exists
  usage           anonymous usage counts may be shared
  usage+feedback  usage counts and developer-written feedback notes may be shared
There is no network sending. "Share" means this tool writes a sanitized report FILE and tells the developer where it is and
how to send it (https://support.znode.com, or <support contact to be confirmed by Znode>). The developer sends it, or not.

Usage
  python nd_consent.py status [--json]
  python nd_consent.py set --level off|usage|usage+feedback
  python nd_consent.py withdraw                 same as set --level off
  python nd_consent.py report                   (level usage or higher) write a usage-counts report file
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nd_config  # noqa: E402
import nd_ledger  # noqa: E402

LEVELS = ("off", "usage", "usage+feedback")
NOTICE_VERSION = "1"
SUPPORT = "https://support.znode.com (or <support contact to be confirmed by Znode>)"


def current() -> dict:
    c = nd_config.load().get("consent")
    if isinstance(c, dict) and c.get("level") in LEVELS:
        return c
    return {"level": "off", "notice_version": None, "timestamp": None}


def set_level(level: str) -> dict:
    if level not in LEVELS:
        raise ValueError("level must be one of: " + ", ".join(LEVELS))
    cfg = nd_config.load()
    cfg["consent"] = {"level": level, "notice_version": NOTICE_VERSION, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")}
    nd_config.save(cfg)
    return cfg["consent"]


def cmd_status(a) -> int:
    c = current()
    if a.json:
        print(json.dumps(c, indent=1))
    else:
        print(f"consent level: {c['level']}" + ("" if c["timestamp"] else " (default, never changed)"))
        if c["timestamp"]:
            print(f"notice version {c['notice_version']}, set {c['timestamp']}")
        print("Nothing is ever sent automatically; sharing means a file you send yourself. See privacy/DATA-INVENTORY.md.")
    return 0


def cmd_set(a) -> int:
    print("consent level:", set_level(a.level)["level"])
    return 0


def cmd_withdraw(_a) -> int:
    set_level("off")
    print("consent withdrawn: level is now off. Local ledger data stays until you run: python nd_ledger.py clear")
    return 0


def cmd_report(_a) -> int:
    c = current()
    if c["level"] == "off":
        print("Consent level is off: no report written. Change it with: python nd_consent.py set --level usage")
        return 1
    d = nd_ledger.summarize(nd_ledger.read_lines(True), True)
    out = nd_config.home() / "reports" / (time.strftime("%Y%m%d-%H%M%S") + "-usage.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"kind": "nelli-dev usage counts", "notice_version": c["notice_version"], "counts": d}, indent=1), encoding="utf-8")
    print("Report written to:", out)
    print("Nothing was sent. Review the file; to share it, send it via " + SUPPORT + ".")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("status"); s.add_argument("--json", action="store_true"); s.set_defaults(fn=cmd_status)
    t = sub.add_parser("set"); t.add_argument("--level", required=True, choices=LEVELS); t.set_defaults(fn=cmd_set)
    sub.add_parser("withdraw").set_defaults(fn=cmd_withdraw)
    sub.add_parser("report").set_defaults(fn=cmd_report)
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
