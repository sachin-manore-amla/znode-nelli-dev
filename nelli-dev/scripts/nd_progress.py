#!/usr/bin/env python3
"""Keep the progress file for an Nelli-Dev task: the plan's steps and outputs, each step's status, a note and a timestamp.

Every task gets one, so it can be followed while it runs and resumed after an interruption:
  with a request id   <root>/nd-work/<KEY>/tracker.md
  otherwise         <root>/nd-work/_tasks/<task-slug>/progress.md, or --file <path> in the task's own output folder

Usage
  python nd_progress.py init   --key ND-001 --title "Refund total wrong" --mode deliver --size large ^
                                --step "reasoning: Understand the ticket and FSD" ^
                                --step "script: Trace the refund route" --output analysis.md
  python nd_progress.py update --key ND-001 2 doing --note "tracing ReturnsService"
  python nd_progress.py update --key ND-001 2 done  --note "chain saved in sources/route.md"
  python nd_progress.py add    --key ND-001 --step "script: Compare the two branches"
  python nd_progress.py output --key ND-001 analysis.md --path nd-work/ND-001/analysis.md
  python nd_progress.py show   --key ND-001        # exit 0 all done, 3 in progress, 1 something blocked
  python nd_progress.py list                         # every task, unfinished first
  python nd_progress.py parts  --key ND-001        # agents' part files: done / active / STALE

Part files (<task folder>/parts/<part>.md) are where agents save as they go: after each section they
append what they found and a line "UPDATED <yyyy-mm-dd hh:mm> - <what's next>", and they finish with
"DONE <yyyy-mm-dd hh:mm> - <summary>". A part with no DONE and no update for 10 minutes is STALE.

`init` never overwrites: on an existing file it shows where the task stands, so a restarted run resumes
from the first unfinished step. Step statuses: todo, doing, done, blocked, skipped. Output statuses: todo,
doing, ready, blocked. Each step's kind is "script" (facts pulled mechanically) or "reasoning".
Only the Steps and Outputs tables and the header's "Updated" time are rewritten; the rest of the file is
left as written (decisions, open questions, approvals, branches, links).
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__import__('nd_ws').workspace())
STEP_STATUS = {"todo": "⬜ todo", "doing": "🔄 doing", "done": "✅ done", "blocked": "⛔ blocked", "skipped": "⏭ skipped"}
OUTPUT_STATUS = {"todo": "⬜ todo", "doing": "🔄 doing", "ready": "✅ ready", "blocked": "⛔ blocked"}
STEPS_HEAD = "| # | Step | Kind | By | Status | Updated | Note |"
STEPS_SEP = "|---|---|---|---|---|---|---|"
OUTPUTS_HEAD = "| Output | Status | Updated | Path |"
OUTPUTS_SEP = "|---|---|---|---|"
KINDS = ("script", "reasoning")
KEY_SECTIONS = ("Decisions", "Open questions", "Approvals (what · when · by whom)",
                "Branches (repo · previous branch · new branch · pushed?)",
                "Links (requirement, solution proposal, documents, PRs, environments, test runs)")
TASK_SECTIONS = ("Decisions", "Open questions", "Links")


def stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def cell(text) -> str:
    return " ".join(str(text or "").replace("|", "/").split())


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60] or "task"


def progress_path(args) -> Path:
    if getattr(args, "file", None):
        return Path(args.file)
    if getattr(args, "key", None):
        return ROOT / "nd-work" / args.key.upper() / "tracker.md"
    if getattr(args, "task", None):
        return ROOT / "nd-work/_tasks" / slug(args.task) / "progress.md"
    sys.exit("give --key <KEY>, --task <slug> or --file <path>")


def split_step(text: str) -> tuple[str, str]:
    kind, sep, rest = text.partition(":")
    if sep and kind.strip().lower() in KINDS:
        return kind.strip().lower(), rest.strip()
    return "?", text.strip()


def table(lines: list[str], head: str):
    """(header index, rows as cell lists, index after the last row), or None when the table is missing."""
    for i, line in enumerate(lines):
        if line.strip() == head:
            rows, j = [], i + 2
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                rows.append([c.strip() for c in lines[j].strip().strip("|").split("|")])
                j += 1
            return i, rows, j
    return None


def render(head: str, sep: str, rows: list[list[str]]) -> list[str]:
    return [head, sep] + ["| " + " | ".join(row) + " |" for row in rows]


def load(path: Path) -> list[str]:
    if not path.is_file():
        sys.exit(f"no progress file at {path} - start one with `init`")
    return path.read_text(encoding="utf-8-sig").splitlines()


def save(path: Path, lines: list[str]) -> None:
    text = "\n".join(lines) + "\n"
    text = re.sub(r"(Updated: )\d{4}-\d\d-\d\d \d\d:\d\d", lambda m: m.group(1) + stamp(), text, count=1)
    path.write_text(text, encoding="utf-8-sig")  # with a BOM, so Windows PowerShell reads it correctly too


def replace_table(lines: list[str], head: str, sep: str, rows: list[list[str]]) -> list[str]:
    found = table(lines, head)
    if not found:
        sys.exit(f"the file has no table starting with {head!r}")
    start, _, end = found
    return lines[:start] + render(head, sep, rows) + lines[end:]


def summary(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    steps = (table(lines, STEPS_HEAD) or (0, [], 0))[1]
    outputs = (table(lines, OUTPUTS_HEAD) or (0, [], 0))[1]
    header = next((ln for ln in lines[1:4] if "Updated:" in ln), "")
    status = lambda row: row[4].split()[-1] if len(row) > 4 and row[4] else "?"
    return {
        "title": lines[0].lstrip("# ").strip() if lines else path.name, "path": path, "header": header,
        "steps": steps, "outputs": outputs,
        "done": sum(status(r) in ("done", "skipped") for r in steps),
        "doing": [r for r in steps if status(r) == "doing"],
        "blocked": [r for r in steps if status(r) == "blocked"],
        "todo": [r for r in steps if status(r) == "todo"],
        "ready": [r for r in outputs if len(r) > 1 and r[1].endswith("ready")],
        "updated": (re.search(r"Updated: ([\d-]+ [\d:]+)", header) or [None, "?"])[1],
        "known": bool(table(lines, STEPS_HEAD)),
    }


def print_summary(info: dict) -> int:
    print(f"{info['title']}   ({info['path']})")
    if not info["known"]:
        print("  no Steps table in the nd_progress format")
        return 1
    total = len(info["steps"])
    print(f"  steps {info['done']}/{total} done · {len(info['doing'])} doing · {len(info['blocked'])} blocked"
          f" · updated {info['updated']}")
    for row in info["doing"]:
        print(f"  now:     #{row[0]} {row[1]} ({row[2]})" + (f" - {row[6]}" if len(row) > 6 and row[6] else ""))
    for row in info["blocked"]:
        print(f"  blocked: #{row[0]} {row[1]}" + (f" - {row[6]}" if len(row) > 6 and row[6] else ""))
    if info["todo"]:
        row = info["todo"][0]
        print(f"  next:    #{row[0]} {row[1]} ({row[2]})")
    if info["outputs"]:
        names = ", ".join(r[0] for r in info["ready"]) or "none yet"
        print(f"  outputs {len(info['ready'])}/{len(info['outputs'])} ready: {names}")
    if info["blocked"]:
        return 1
    return 0 if total and info["done"] == total else 3


# ---------------------------------------------------------------- commands
def cmd_init(args) -> None:
    path = progress_path(args)
    if path.exists():
        print(f"Progress file already exists - resume from the first unfinished step:")
        sys.exit(print_summary(summary(path)))
    path.parent.mkdir(parents=True, exist_ok=True)
    steps = []
    for number, text in enumerate(args.step or [], 1):
        kind, what = split_step(text)
        steps.append([str(number), cell(what), kind, "Nelli-Dev", STEP_STATUS["todo"], "", ""])
        if kind == "?":
            print(f"warning: step {number} has no kind; start it with 'script:' or 'reasoning:'", file=sys.stderr)
    outputs = [[cell(name), OUTPUT_STATUS["todo"], "", ""] for name in args.output or []]
    title = f"{args.key.upper()} — {args.title}" if args.key else args.title
    meta = " · ".join([f"Mode: {args.mode}", f"Size: {args.size}", *(cell(m) for m in args.meta or []),
                       f"Started: {stamp()}", f"Updated: {stamp()}"])
    lines = [f"# {title}", meta, "", "## Steps", *render(STEPS_HEAD, STEPS_SEP, steps), "",
             "Kind: script · reasoning. Status: ⬜ todo · 🔄 doing · ✅ done · ⛔ blocked · ⏭ skipped", "",
             "## Outputs", *render(OUTPUTS_HEAD, OUTPUTS_SEP, outputs), ""]
    for section in KEY_SECTIONS if args.key else TASK_SECTIONS:
        lines += [f"## {section}", ""]
    save(path, lines)
    print(f"created {path}")
    print_summary(summary(path))


def cmd_update(args) -> None:
    path = progress_path(args)
    lines = load(path)
    found = table(lines, STEPS_HEAD)
    if not found:
        sys.exit("no Steps table in this file")
    rows = found[1]
    row = next((r for r in rows if r[0] == str(args.number)), None)
    if not row:
        sys.exit(f"no step #{args.number}; steps are 1-{len(rows)}")
    row[4], row[5] = STEP_STATUS[args.status], stamp()
    if args.note is not None:
        row[6] = cell(args.note)
    if args.by:
        row[3] = cell(args.by)
    save(path, replace_table(lines, STEPS_HEAD, STEPS_SEP, rows))
    print(f"#{row[0]} {row[1]}: {row[4]}" + (f" - {row[6]}" if row[6] else ""))


def cmd_add(args) -> None:
    path = progress_path(args)
    lines = load(path)
    found = table(lines, STEPS_HEAD)
    if not found:
        sys.exit("no Steps table in this file")
    rows = found[1]
    for text in args.step:
        kind, what = split_step(text)
        number = max((int(r[0]) for r in rows if r[0].isdigit()), default=0) + 1
        rows.append([str(number), cell(what), kind, cell(args.by or "Nelli-Dev"), STEP_STATUS["todo"], stamp(), ""])
        print(f"added #{number} {what} ({kind})")
    save(path, replace_table(lines, STEPS_HEAD, STEPS_SEP, rows))


def cmd_output(args) -> None:
    path = progress_path(args)
    lines = load(path)
    found = table(lines, OUTPUTS_HEAD)
    if not found:
        sys.exit("no Outputs table in this file")
    rows = found[1]
    row = next((r for r in rows if r[0].lower() == args.name.lower()), None)
    if not row:
        row = [cell(args.name), "", "", ""]
        rows.append(row)
    row[1], row[2] = OUTPUT_STATUS[args.status], stamp()
    if args.path:
        row[3] = cell(args.path)
    save(path, replace_table(lines, OUTPUTS_HEAD, OUTPUTS_SEP, rows))
    print(f"output {row[0]}: {row[1]}" + (f" ({row[3]})" if row[3] else ""))


def cmd_show(args) -> None:
    path = progress_path(args)
    load(path)
    code = print_summary(summary(path))
    if args.full:
        print()
        print(path.read_text(encoding="utf-8-sig"))
    sys.exit(code)


def cmd_parts(args) -> None:
    """Agents' part files: done (last marker DONE), active, or STALE (no update for --stale-min minutes)."""
    folder = Path(args.folder) if args.folder else progress_path(args).parent / "parts"
    files = sorted(folder.glob("*.md")) if folder.is_dir() else []
    if not files:
        print(f"no part files in {folder}")
        sys.exit(0)
    now = datetime.now().timestamp()
    stale = active = 0
    print(f"{'part':<34} {'state':<7} {'quiet':>6}  last line")
    for path in files:
        lines = [ln.strip() for ln in path.read_text(encoding="utf-8-sig", errors="replace").splitlines() if ln.strip()]
        marker = next((ln for ln in reversed(lines) if ln.startswith(("DONE", "UPDATED"))), "")
        quiet = (now - path.stat().st_mtime) / 60
        if marker.startswith("DONE"):
            state = "done"
        elif quiet > args.stale_min:
            state, stale = "STALE", stale + 1
        else:
            state, active = "active", active + 1
        last = marker or (lines[-1] if lines else "")
        print(f"{path.stem[:34]:<34} {state:<7} {quiet:>5.0f}m  {last[:90]}")
    if stale:
        print(f"\n{stale} stale part(s): stop that agent and restart it with 'continue from <its part file>'.")
    sys.exit(1 if stale else 3 if active else 0)


def cmd_list(args) -> None:
    files = sorted((ROOT / "nd-work").glob("*/tracker.md")) + sorted((ROOT / "nd-work/_tasks").glob("*/progress.md"))
    infos = [summary(f) for f in files]
    infos.sort(key=lambda i: i["updated"], reverse=True)  # newest first ...
    infos.sort(key=lambda i: i["known"] and bool(i["steps"]) and i["done"] == len(i["steps"]))  # ... unfinished on top
    if not infos:
        print("no progress files yet")
        return
    for info in infos:
        total = len(info["steps"])
        state = ("blocked" if info["blocked"] else "done" if total and info["done"] == total
                 else "doing" if info["doing"] else "todo") if info["known"] else "other format"
        print(f"{state:<8} {info['done']}/{total:<3} {info['updated']:<17} {info['title'][:60]}   {info['path']}")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    def target(p):
        p.add_argument("--key", help="request id: <root>/nd-work/<KEY>/tracker.md")
        p.add_argument("--task", help="task slug when there is no key: <root>/nd-work/_tasks/<slug>/progress.md")
        p.add_argument("--file", help="an explicit progress file, Eg in the task's output folder")

    p = sub.add_parser("init", help="create the progress file from the plan (never overwrites)")
    target(p)
    p.add_argument("--title", required=True)
    p.add_argument("--mode", required=True, help="deliver, analyse, pr, ask, curl, docs, ...")
    p.add_argument("--size", required=True, choices=("small", "medium", "large"))
    p.add_argument("--step", action="append", help="'script: <step>' or 'reasoning: <step>' (repeat)")
    p.add_argument("--output", action="append", help="an output the task will produce (repeat)")
    p.add_argument("--meta", action="append", help="extra header fact, Eg 'Target branch: int' (repeat)")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("update", help="set one step's status, with a one-line note")
    target(p)
    p.add_argument("number", type=int)
    p.add_argument("status", choices=tuple(STEP_STATUS))
    p.add_argument("--note")
    p.add_argument("--by", help="who did it, Eg api-builder")
    p.set_defaults(func=cmd_update)

    p = sub.add_parser("add", help="add steps when the plan changes")
    target(p)
    p.add_argument("--step", action="append", required=True)
    p.add_argument("--by")
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("output", help="add an output or set its status (default: ready)")
    target(p)
    p.add_argument("name")
    p.add_argument("--status", choices=tuple(OUTPUT_STATUS), default="ready")
    p.add_argument("--path")
    p.set_defaults(func=cmd_output)

    p = sub.add_parser("show", help="where the task stands (exit 0 done, 3 in progress, 1 blocked)")
    target(p)
    p.add_argument("--full", action="store_true", help="also print the whole file")
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("parts", help="agents' part files: done, active or stale (exit 0 all done, 3 active, 1 stale)")
    target(p)
    p.add_argument("--folder", help="part-file folder (default: <task folder>/parts)")
    p.add_argument("--stale-min", type=float, default=10, help="minutes without an update before a part is stale")
    p.set_defaults(func=cmd_parts)

    p = sub.add_parser("list", help="every task's progress file, unfinished first")
    p.set_defaults(func=cmd_list)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
