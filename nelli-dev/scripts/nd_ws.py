"""Workspace resolution shared by the Nelli-Dev scripts.

Order: NELLIDEV_WORKSPACE, then CLAUDE_PROJECT_DIR, then the folder this package is installed in
(<workspace>/.claude/scripts/nd/ -> <workspace>), then the current folder. The installed-location step matters
because a shell's current folder can drift away from the project root, and a script must not scan the wrong place.
"""
from __future__ import annotations

import os
from pathlib import Path


def workspace() -> Path:
    for var in ("NELLIDEV_WORKSPACE", "CLAUDE_PROJECT_DIR"):
        if os.environ.get(var):
            return Path(os.environ[var]).resolve()
    here = Path(__file__).resolve()
    if len(here.parents) > 3 and here.parent.name == "nd" and here.parents[1].name == "scripts" and here.parents[2].name == ".claude":
        return here.parents[3]
    return Path.cwd().resolve()
