#!/usr/bin/env python3
"""Nelli-Dev feedback: build a sanitized feedback note and, only after the developer confirms, save it as a local file. Never sends anything.

Usage
  python nd_feedback.py preview --note "text" [--command NAME] [--confidence "pasted confidence line"]   (or --note-stdin)
  python nd_feedback.py save    --note "text" [--command NAME] [--confidence "..."] --confirmed
`preview` prints the sanitized note and writes nothing. `save` refuses without --confirmed (the developer said yes after seeing the
preview) and writes %USERPROFILE%\\.nelli-dev\\feedback\\<timestamp>.md. To share it, the developer sends it via https://support.znode.com
(or <support contact to be confirmed by Znode>).
Redaction removes tokens, bearer/basic strings, keys, passwords, emails, host names, IP addresses and drive/home paths.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nd_config  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RULES = [
    (r"(?i)\b(bearer|basic)\s+[A-Za-z0-9+/=._\-]{6,}", r"\1 <redacted>"),
    (r"eyJ[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]*", "<redacted-token>"),
    (r"(?i)\b([A-Za-z0-9_\-]*(?:password|passwd|pwd|secret|token|api[_-]?key|apikey|access[_-]?key|authorization|credential|connectionstring)[A-Za-z0-9_\-]*)\s*[:=]\s*\S+", r"\1=<redacted>"),
    (r"(?i)\b(?:sk|pk|ghp|gho|xox[abp]|AKIA)[A-Za-z0-9_\-]{12,}", "<redacted-key>"),
    (r"(?i)\b(Server|Data Source|User Id|Uid|Pwd)\s*=\s*[^;\s]+", r"\1=<redacted>"),
    (r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)+", "<email>"),
    (r"(?i)\b[a-z][a-z0-9+.\-]*://[^\s\"'<>]+", "<url>"),
    (r"\\\\[^\s\\]+\\[^\s]*", "<path>"),
    (r"(?i)\b[A-Z]:[\\/][^\s\"'<>|]*", "<path>"),
    (r"(?:/(?:home|Users|var|etc|opt|mnt|srv)/[^\s\"'<>]+)", "<path>"),
    (r"\b\d{1,3}(?:\.\d{1,3}){3}\b", "<ip>"),
    (r"(?i)\b(?:[a-z0-9\-]+\.)+(?:com|net|org|io|dev|local|internal|corp|cloud|co|biz|info)\b", "<host>"),
    (r"\b[A-Za-z0-9+/_\-]{32,}={0,2}", "<redacted-long-value>"),
]


def redact(text: str) -> str:
    for pat, rep in RULES:
        text = re.sub(pat, rep, text)
    return text


def plugin_version() -> str:
    try:
        return json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]
    except (OSError, ValueError, KeyError):
        return "unknown"


def build(note: str, command: str | None, confidence: str | None) -> str:
    cmd = redact(command or "")[:60] or "not given"
    conf = redact(confidence or "")[:300] or "not given"
    return "\n".join(["# Nelli-Dev feedback", "", f"- Plugin version: {plugin_version()}", f"- Command: {cmd}",
                      f"- Confidence line: {conf}", "", "## Note", "", redact(note)[:2000], ""])


def _note(a) -> str:
    return sys.stdin.read() if a.note_stdin else (a.note or "")


def cmd_preview(a) -> int:
    print(build(_note(a), a.command, a.confidence))
    print("--- Nothing has been saved or sent. Confirm to save this file locally.")
    return 0


def cmd_save(a) -> int:
    if not a.confirmed:
        print("Refused: show the preview first and pass --confirmed only after the developer agrees.")
        return 1
    out = nd_config.home() / "feedback" / (time.strftime("%Y%m%d-%H%M%S") + ".md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build(_note(a), a.command, a.confidence), encoding="utf-8")
    print("Feedback saved to:", out)
    print("Nothing was sent. To share it, send the file via https://support.znode.com (or <support contact to be confirmed by Znode>).")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("preview", cmd_preview), ("save", cmd_save)):
        p = sub.add_parser(name)
        p.add_argument("--note"); p.add_argument("--note-stdin", action="store_true")
        p.add_argument("--command"); p.add_argument("--confidence")
        if name == "save":
            p.add_argument("--confirmed", action="store_true")
        p.set_defaults(fn=fn)
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
