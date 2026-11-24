#!/usr/bin/env python3
"""Nelli-Dev update check (SessionStart hook): says when the local marketplace clone holds a newer version than the installed plugin.

Read-only and offline: it compares the installed .claude-plugin\\plugin.json version with the plugin entry in
<claude folder>\\plugins\\marketplaces\\znode-nelli-dev\\.claude-plugin\\marketplace.json. No network, no identifiers, installs nothing.
Silent when equal, older or when the clone is missing or unreadable. Test overrides: --installed X.Y.Z, --marketplace <marketplace.json>.

Usage  python nd_update_check.py [--installed X.Y.Z] [--marketplace FILE]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKETPLACE = "znode-nelli-dev"
PLUGIN = "nelli-dev"


def parse(v) -> tuple | None:
    m = re.match(r"^\s*v?(\d+)\.(\d+)\.(\d+)", str(v))
    return tuple(int(x) for x in m.groups()) if m else None


def marketplace_file() -> Path:
    base = Path(os.environ.get("CLAUDE_CONFIG_DIR") or (Path.home() / ".claude"))
    return base / "plugins" / "marketplaces" / MARKETPLACE / ".claude-plugin" / "marketplace.json"


def check(installed: str | None = None, mfile: Path | None = None) -> str | None:
    try:
        if installed is None:
            installed = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]
        data = json.loads((mfile or marketplace_file()).read_text(encoding="utf-8-sig"))
        latest = next(p["version"] for p in data["plugins"] if p.get("name") == PLUGIN)
        a, b = parse(installed), parse(latest)
        if a and b and b > a:
            return (f"Nelli-Dev {latest} is available. Run /plugin marketplace update {MARKETPLACE} then "
                    f"/plugin update {PLUGIN}@{MARKETPLACE}; changes: RELEASE-NOTES.md")
    except Exception:
        return None
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--installed")
    ap.add_argument("--marketplace")
    a = ap.parse_args()
    msg = check(a.installed, Path(a.marketplace) if a.marketplace else None)
    if msg:
        print(msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
