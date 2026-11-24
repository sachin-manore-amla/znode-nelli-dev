#!/usr/bin/env python3
"""Check the Nelli-Dev plugin package: layout, commands, agents, hook, guard, registry. Read-only.

Usage
  python nd_verify.py            # prints one line per check; exit 1 if any fails

Replaces the old copy installer: the package is a Claude Code plugin (.claude-plugin/plugin.json) and is
installed with the plugin mechanism, not by copying files.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMMANDS = ["advise", "ask", "curl", "deliver", "docs", "feedback", "recommend-api", "review", "setup", "status"]   # PLAN.md 2.1
AGENTS = ["api-curl-builder", "code-reviewer", "doc-writer", "nelli-dev", "sdk-builder", "test-author", "webstore-builder"]
failed = 0
# the only places that may still name the old product: they exist to migrate its data
MIGRATION_REFS = {"scripts/nd_migrate.py", "scripts/nd_config.py", "scripts/nd_verify.py", "scripts/nd_guard.py",
                  "skills/setup/SKILL.md", "skills/status/SKILL.md"}


def check(ok: bool, label: str, detail: str = "") -> None:
    global failed
    failed += not ok
    print(("ok   " if ok else "FAIL ") + label + (f": {detail}" if detail and not ok else ""))


def front(path: Path) -> dict:
    m = re.match(r"^---\n(.*?)\n---\n", path.read_text(encoding="utf-8"), re.S)
    out, key = {}, None
    for line in (m.group(1) if m else "").split("\n"):
        if re.match(r"^[A-Za-z-]+:", line):
            key, _, v = line.partition(":")
            out[key] = v.strip()
        elif key and line.strip().startswith("- "):
            out.setdefault(key + "[]", []).append(line.strip()[2:])
    return out


def main() -> int:
    pj = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    check(pj.get("name") == "nelli-dev", "plugin manifest name is nelli-dev")

    agents = sorted(p.stem for p in (ROOT / "agents").glob("*.md"))
    check(agents == AGENTS, "agents are exactly the expected six", f"{agents}")
    skill_dirs = {d.name for d in (ROOT / "skills").iterdir() if d.is_dir()}
    for a in AGENTS:
        text = (ROOT / "agents" / f"{a}.md").read_text(encoding="utf-8")
        fm = front(ROOT / "agents" / f"{a}.md")
        check(fm.get("name") == a, f"agent {a}: name matches file")
        check("\nhooks:" not in "\n" + text.split("\n---\n", 1)[0], f"agent {a}: no front-matter hooks (ignored for plugin agents)")
        missing = [s for s in fm.get("skills[]", []) if s.split(":")[-1] not in skill_dirs]
        check(not missing, f"agent {a}: preloaded skills exist", str(missing))

    visible, bad = [], []
    for d in sorted((ROOT / "skills").iterdir()):
        if not d.is_dir():
            continue
        f = d / "SKILL.md"
        if not f.exists():
            bad.append(d.name)
            continue
        fm = front(f)
        if fm.get("name") != d.name:
            bad.append(d.name)
        if fm.get("user-invocable") != "false":
            visible.append(d.name)
            if d.name not in ("setup", "status", "feedback"):
                ag = fm.get("agent", "").split(":")[-1]
                if fm.get("context") != "fork" or ag not in AGENTS:
                    bad.append(d.name + " (fork or agent)")
    check(not bad, "every skill has SKILL.md with a matching name; commands fork into a real agent", str(bad))
    check(sorted(visible) == COMMANDS, "visible slash commands are exactly the plan's table", str(sorted(visible)))

    hooks = json.loads((ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8"))["hooks"]["PreToolUse"][0]
    check("PowerShell" in hooks["matcher"] and "Bash" in hooks["matcher"], "guard hook covers Bash and PowerShell")
    check((ROOT / "scripts" / "nd_guard.py").exists() and "nd_guard.py" in hooks["hooks"][0]["command"], "guard hook points at nd_guard.py")

    leftovers = []
    for f in list((ROOT / "agents").glob("*.md")) + list((ROOT / "skills").glob("*/SKILL.md")) + list((ROOT / "scripts").glob("*.py")):
        if re.search(r"z-custom|ZCUSTOM|\bzc[-_]", f.read_text(encoding="utf-8"), re.I) and f.relative_to(ROOT).as_posix() not in MIGRATION_REFS:
            leftovers.append(f.name)
    check(not leftovers, "no old Z-Custom names in agents, skills or scripts", str(leftovers))

    for label, cmd in (("guard self-test", ["nd_guard.py", "--selftest"]), ("registry check", ["nd_registry.py", "check"])):
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / cmd[0]), *cmd[1:]], capture_output=True, text=True, cwd=str(ROOT))
        check(r.returncode == 0, label, (r.stdout + r.stderr)[-200:])
    print("\nALL CHECKS PASSED" if not failed else f"\n{failed} CHECK(S) FAILED")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
