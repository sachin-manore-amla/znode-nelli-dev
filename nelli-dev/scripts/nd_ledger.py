#!/usr/bin/env python3
"""Nelli-Dev session ledger: a small LOCAL record of what Nelli-Dev ran, so /nelli-dev:status can show session progress.

Each hook event appends one JSON line to %USERPROFILE%\\.nelli-dev\\ledger\\<YYYY-MM-DD>.jsonl (folder override: NELLIDEV_HOME).
A line holds ONLY: ts, s (a short hash of the session id), ev (start|command|tool|stop), n (a command, skill or tool NAME),
q (1 when the call was a knowledge query). It never holds prompts, file contents, paths, command arguments, responses or secrets:
the line is built from a fixed whitelist and every name must look like an identifier, otherwise it is stored as "other".
Token and cost numbers are NOT recorded: Claude Code hooks do not provide them (see docs\\LEDGER-AND-FEEDBACK.md).
Set NELLIDEV_LEDGER=off to switch the ledger off.

Usage
  python nd_ledger.py hook          read one hook event as JSON on stdin and append a line (used by hooks.json; never fails)
  python nd_ledger.py show [--all] [--json]   summary of the latest session (--all: every stored day)
  python nd_ledger.py export [--out FILE]     write a readable summary (counts only) and print where it is
  python nd_ledger.py clear                   delete every ledger file
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from collections import Counter
from pathlib import Path

NAME_OK = re.compile(r"^[A-Za-z0-9_.:\-]{1,80}$")
COMMAND = re.compile(r"^\s*/(nelli-dev:[a-z][a-z\-]{0,30})(\s|$)")
KNOWLEDGE_CMD = re.compile(r"nd_(query_spec|pack_search|registry|find_earlier)\.py")


def home() -> Path:
    h = os.environ.get("NELLIDEV_HOME")
    return Path(h).expanduser() if h else Path.home() / ".nelli-dev"


def folder() -> Path:
    return home() / "ledger"


def _name(v) -> str:
    return v if isinstance(v, str) and NAME_OK.match(v) else "other"


def build_line(payload: dict, now: float | None = None) -> dict | None:
    """Turn a hook payload into a ledger line, or None. Reads only event name, tool name, skill name and the command NAME."""
    ev = payload.get("hook_event_name")
    sid = payload.get("session_id")
    s = hashlib.sha1(str(sid).encode()).hexdigest()[:8] if sid else "none"
    line = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(now or time.time())), "s": s}
    if ev == "SessionStart":
        line.update(ev="start", n="session")
    elif ev == "Stop":
        line.update(ev="stop", n="session")
    elif ev == "UserPromptSubmit":
        m = COMMAND.match(payload.get("prompt") if isinstance(payload.get("prompt"), str) else "")
        if not m:
            return None                      # an ordinary prompt: nothing is recorded, not even its length
        line.update(ev="command", n=m.group(1))
    elif ev == "PostToolUse":
        tool = _name(payload.get("tool_name"))
        ti = payload.get("tool_input") if isinstance(payload.get("tool_input"), dict) else {}
        name, q = tool, 0
        if tool == "Skill":
            name = "skill:" + _name(ti.get("skill"))
            q = 1 if name.startswith("skill:nelli-dev:") else 0
        elif tool in ("Bash", "PowerShell"):
            q = 1 if KNOWLEDGE_CMD.search(str(ti.get("command", ""))) else 0      # the command text is tested, never stored
        elif tool in ("Read", "Grep", "Glob"):
            hay = str(ti.get("file_path", "")) + str(ti.get("path", ""))
            q = 1 if re.search(r"nelli-dev[\\/](knowledge|registry)", hay) else 0  # tested, never stored
        elif "kb_search" in tool or "kb_article" in tool:
            q = 1
        line.update(ev="tool", n=name, q=q)
    else:
        return None
    return line


def append(line: dict) -> None:
    f = folder() / (line["ts"][:10] + ".jsonl")
    f.parent.mkdir(parents=True, exist_ok=True)
    with open(f, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(line, separators=(",", ":")) + "\n")


def cmd_hook(_a) -> int:
    try:
        if os.environ.get("NELLIDEV_LEDGER", "").lower() == "off":
            return 0
        payload = json.loads(sys.stdin.read() or "{}")
        line = build_line(payload) if isinstance(payload, dict) else None
        if line:
            append(line)
    except Exception:
        pass                                   # a hook must never disturb the session
    return 0


def read_lines(all_days: bool = False) -> list[dict]:
    files = sorted(folder().glob("*.jsonl")) if folder().exists() else []
    if not all_days:
        files = files[-1:]
    out = []
    for f in files:
        for raw in f.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                d = json.loads(raw)
                if isinstance(d, dict) and "ev" in d:
                    out.append(d)
            except ValueError:
                continue
    return out


def summarize(lines: list[dict], all_days: bool = False) -> dict:
    if lines and not all_days:
        last = lines[-1].get("s")
        lines = [x for x in lines if x.get("s") == last]
    cmds = Counter(x["n"] for x in lines if x["ev"] == "command")
    skills = Counter(x["n"][6:] for x in lines if x["ev"] == "tool" and str(x["n"]).startswith("skill:"))
    tools = Counter(x["n"] for x in lines if x["ev"] == "tool" and not str(x["n"]).startswith("skill:"))
    return {"events": len(lines), "from": lines[0]["ts"] if lines else None, "to": lines[-1]["ts"] if lines else None,
            "commands": dict(cmds), "skills": dict(skills), "tools": dict(tools),
            "knowledge_queries": sum(int(x.get("q", 0)) for x in lines),
            "tokens_and_cost": "not available (Claude Code hooks do not provide them)"}


COLLECTED = ("Collected locally only: time, event type, command/skill/tool names and a knowledge-query count. "
             "Never prompts, file contents, code paths, command arguments, responses or secrets. Nothing is sent.")


def _fmt(d: dict) -> str:
    def counts(c):
        return ", ".join(f"{k} x{v}" for k, v in sorted(c.items(), key=lambda kv: -kv[1])) or "none"
    return "\n".join([
        f"Events: {d['events']}" + (f" ({d['from']} to {d['to']})" if d["events"] else ""),
        f"Commands run: {counts(d['commands'])}",
        f"Skills used: {counts(d['skills'])}",
        f"Tools used: {counts(d['tools'])}",
        f"Knowledge queries: {d['knowledge_queries']}",
        f"Tokens and cost: {d['tokens_and_cost']}",
        COLLECTED])


def cmd_show(a) -> int:
    d = summarize(read_lines(a.all), a.all)
    print(json.dumps(d, indent=1) if a.json else _fmt(d))
    return 0


def cmd_export(a) -> int:
    d = summarize(read_lines(True), True)
    out = Path(a.out) if a.out else home() / "ledger-export" / (time.strftime("%Y%m%d-%H%M%S") + ".md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("# Nelli-Dev ledger summary (counts only)\n\n" + _fmt(d) + "\n", encoding="utf-8")
    print("Summary written to:", out)
    return 0


def cmd_clear(_a) -> int:
    n = 0
    if folder().exists():
        for f in folder().glob("*.jsonl"):
            f.unlink()
            n += 1
    print(f"Ledger cleared: {n} file(s) deleted from {folder()}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("hook").set_defaults(fn=cmd_hook)
    s = sub.add_parser("show"); s.add_argument("--all", action="store_true"); s.add_argument("--json", action="store_true"); s.set_defaults(fn=cmd_show)
    e = sub.add_parser("export"); e.add_argument("--out"); e.set_defaults(fn=cmd_export)
    sub.add_parser("clear").set_defaults(fn=cmd_clear)
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
