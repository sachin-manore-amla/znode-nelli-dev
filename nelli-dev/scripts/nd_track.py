#!/usr/bin/env python3
"""Track Nelli-Dev script runs: live progress, a time-stamped log and a status file for every run.

Two ways to use it.

1. Wrap any command, such as a skill script, dotnet test, npx nx or a git loop:

     python nd_track.py run --key ND-001 --name tests -- dotnet test <project>

   The command's output streams through unchanged and is copied, time-stamped,
   into the run log. The status file records the last output line, the line
   count, any "[n/m]", "n of m" or "nn%" progress the output shows, and a
   heartbeat every 5 seconds.

2. Import it in a script Nelli-Dev writes, for step-by-step progress:

     from nd_track import Tracker
     with Tracker("scan-callers", key=args.key, total=len(repos)) as track:
         for repo in repos:
             track.step(f"scanning {repo.name}")
         track.result(callers=12)

Check runs, including ones still going in the background:

     python nd_track.py list   [--key KEY] [--all] [--running]
     python nd_track.py status last [--key KEY]    # exit 0 ok, 3 running, 1 failed/stale/timeout
     python nd_track.py tail   last [--key KEY] [-n 40]

Runs are kept in nd-work/<KEY>/runs/ (with --key or ND_KEY), otherwise in
nd-work/_runs/. A run still marked "running" whose heartbeat is more than 30
seconds old is shown as "stale": its process ended without finishing.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import traceback
from datetime import datetime
from pathlib import Path

ROOT = Path(__import__('nd_ws').workspace())
WORK = ROOT / "nd-work"
HEARTBEAT_S = 5        # the status file is refreshed at least this often while running
STALE_S = 30           # no heartbeat for this long means the process is gone
PRINT_EVERY_S = 2.0    # progress lines on stderr, at most this often
STATUS_EVERY_S = 1.0   # status-file writes, at most this often (outside the heartbeat)
FRACTION = (
    re.compile(r"\[(\d+)\s*/\s*(\d+)\]"),                 # [3/23]
    re.compile(r"\b(\d+)/(\d+)\s+\(\d{1,3}%\)"),          # 3/23 (13%)  - a Tracker child
    re.compile(r"\b(\d+)\s+of\s+(\d+)\b", re.I),           # 3 of 23
)
PERCENT = re.compile(r"(?<![\d.])(\d{1,3}(?:\.\d+)?)%")
EXIT_RUNNING = 3


def runs_dir(key: str | None = None) -> Path:
    key = key or os.environ.get("ND_KEY")
    return WORK / key.upper() / "runs" if key else WORK / "_runs"


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", text).strip("-")[:40] or "run"


class Tracker:
    """Progress, log and status for one run. Use it as a context manager."""

    def __init__(self, name: str, key: str | None = None, total: int | None = None,
                 argv: list[str] | None = None, command: str | None = None,
                 quiet: bool = False, folder: Path | None = None):
        self.name = slug(name)
        key = (key or os.environ.get("ND_KEY") or "").upper() or None
        self.folder = Path(folder) if folder else runs_dir(key)
        self.folder.mkdir(parents=True, exist_ok=True)
        self.id = f"{datetime.now():%Y%m%d-%H%M%S}-{self.name}-{os.getpid()}"
        self.log_path = self.folder / f"{self.id}.log"
        self.status_path = self.folder / f"{self.id}.json"
        self.quiet = quiet
        self.started = time.time()
        self._lock = threading.RLock()
        self._stop = threading.Event()
        self._last_print = 0.0
        self._last_status = 0.0
        self._phase_started = self.started
        self.state = {
            "id": self.id, "name": self.name, "key": key, "status": "running",
            "pid": os.getpid(), "cwd": os.getcwd(),
            "argv": argv if argv is not None else sys.argv, "command": command,
            "started": now_iso(), "updated": now_iso(), "phase": None,
            "done": 0, "total": total, "percent": None, "eta_s": None,
            "message": "", "lines": 0, "warnings": 0, "result": {},
            "exit_code": None, "duration_s": None, "log": str(self.log_path),
        }
        self._log = self.log_path.open("a", encoding="utf-8", buffering=1)

    # ------------------------------------------------------------ lifecycle
    def __enter__(self) -> "Tracker":
        self._write_log(f"start {self.name} pid={os.getpid()} cwd={os.getcwd()}")
        self._write_log(f"argv {json.dumps(self.state['argv'], default=str)}")
        self._write_status(force=True)
        threading.Thread(target=self._heartbeat, name="nd-heartbeat", daemon=True).start()
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        if exc_type is None:
            self.finish("ok")
        elif issubclass(exc_type, KeyboardInterrupt):
            self.finish("interrupted", exit_code=130)
        elif issubclass(exc_type, SystemExit):
            code = exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 1)
            if exc.code not in (None, 0) and not isinstance(exc.code, int):
                self._write_log(f"exit message: {exc.code}")
            self.finish("ok" if code == 0 else "failed", exit_code=code)
        else:
            self._write_log("ERROR " + "".join(traceback.format_exception(exc_type, exc, tb)).rstrip())
            with self._lock:
                self.state["message"] = f"{exc_type.__name__}: {exc}"[:200]
            self.finish("failed", exit_code=1)
        return False  # never swallow the exception

    def finish(self, status: str, exit_code: int | None = None) -> None:
        if self._stop.is_set():
            return
        self._stop.set()
        with self._lock:
            self.state["status"] = status
            self.state["exit_code"] = exit_code if exit_code is not None else (0 if status == "ok" else 1)
            self.state["duration_s"] = round(time.time() - self.started, 1)
            self.state["eta_s"] = None
        self._write_log(f"end {status} in {self.state['duration_s']}s exit={self.state['exit_code']}")
        self._write_status(force=True)
        result = ", ".join(f"{k}={v}" for k, v in self.state["result"].items())
        self._emit(f"{status} in {self.state['duration_s']}s"
                   + (f" - {self._fraction()}" if self.state["done"] else "")
                   + (f" - {result}" if result else "")
                   + f" - log {self.log_path}", force=True)
        with self._lock:
            self._log.close()

    # ------------------------------------------------------------ progress
    def phase(self, name: str, total: int | None = None) -> None:
        """Start a new phase with its own step count."""
        with self._lock:
            self.state.update(phase=name, done=0, total=total, percent=None, eta_s=None)
            self._phase_started = time.time()
        self._write_log(f"phase {name}" + (f" ({total} steps)" if total else ""))
        self._progress(force=True)

    def set_total(self, total: int) -> None:
        with self._lock:
            self.state["total"] = total
        self._progress()

    def step(self, message: str = "", n: int = 1) -> None:
        """Count n steps done, with an optional note of what was just done."""
        with self._lock:
            self.state["done"] += n
            if message:
                self.state["message"] = message[:200]
        if message:
            self._write_log(f"[{self._fraction()}] {message}")
        self._progress()

    def log(self, message: str) -> None:
        """A free-form line in the log; it also becomes the status message."""
        self._write_log(message)
        with self._lock:
            if message:
                self.state["message"] = message.splitlines()[0][:200]
        self._write_status()

    def warn(self, message: str) -> None:
        with self._lock:
            self.state["warnings"] += 1
        self._write_log("WARN " + message)
        self._emit(f"warning: {message}", force=True)

    def result(self, **fields) -> None:
        """Summary values for the status file, Eg result(callers=12, files=340)."""
        with self._lock:
            self.state["result"].update(fields)
        self._write_log("result " + json.dumps(fields, default=str))
        self._write_status(force=True)

    def output_line(self, line: str) -> None:
        """One line of a wrapped command's output: log it and read any progress it shows."""
        self._write_log("| " + line)
        with self._lock:
            self.state["lines"] += 1
            if line.strip():
                self.state["message"] = line.strip()[:200]
            for pattern in FRACTION:
                match = pattern.search(line)
                if match:
                    done, total = int(match.group(1)), int(match.group(2))
                    if 0 <= done <= total and total > 0:
                        self.state["done"], self.state["total"] = done, total
                    break
            else:
                match = PERCENT.search(line)
                if match and float(match.group(1)) <= 100:
                    self.state["percent"] = round(float(match.group(1)), 1)
        self._progress()

    # ------------------------------------------------------------ internals
    def _fraction(self) -> str:
        done, total = self.state["done"], self.state["total"]
        return f"{done}/{total}" if total else str(done)

    def _progress(self, force: bool = False) -> None:
        with self._lock:
            done, total = self.state["done"], self.state["total"]
            if total:
                self.state["percent"] = round(100.0 * done / total, 1)
                elapsed = time.time() - self._phase_started
                self.state["eta_s"] = round(elapsed / done * (total - done)) if done else None
            text = self._fraction()
            if self.state["percent"] is not None:
                text += f" ({self.state['percent']:.0f}%)"
            if self.state["eta_s"]:
                text += f" eta {self.state['eta_s']}s"
            if self.state["phase"]:
                text = f"{self.state['phase']} {text}"
            if self.state["message"]:
                text += f" - {self.state['message'][:90]}"
        self._write_status(force=force)
        self._emit(text, force=force)

    def _emit(self, text: str, force: bool = False) -> None:
        if self.quiet:
            return
        now = time.time()
        if not force and now - self._last_print < PRINT_EVERY_S:
            return
        self._last_print = now
        try:
            sys.stdout.flush()  # keep the script's own output ahead of the progress line
            print(f"[zc] {self.name}: {text}", file=sys.stderr, flush=True)
        except (OSError, ValueError):
            pass

    def _write_log(self, text: str) -> None:
        stamp = f"{datetime.now():%Y-%m-%d %H:%M:%S}"
        with self._lock:
            if self._log.closed:
                return
            lines = str(text).splitlines() or [""]
            self._log.write(f"{stamp} {lines[0]}\n")
            for extra in lines[1:]:
                self._log.write(f"{' ' * len(stamp)} {extra}\n")

    def _write_status(self, force: bool = False) -> None:
        now = time.time()
        # Snapshot and write under one lock, so a heartbeat can never overwrite the final status.
        with self._lock:
            if not force and now - self._last_status < STATUS_EVERY_S:
                return
            self._last_status = now
            self.state["updated"] = now_iso()
            payload = json.dumps(self.state, indent=1, default=str)
            temp = self.status_path.with_suffix(".tmp")
            for _ in range(5):  # a reader may hold the file open for a moment on Windows
                try:
                    temp.write_text(payload, encoding="utf-8")
                    os.replace(temp, self.status_path)
                    return
                except OSError:
                    time.sleep(0.05)

    def _heartbeat(self) -> None:
        while not self._stop.wait(HEARTBEAT_S):
            self._write_status(force=True)


# ---------------------------------------------------------------- reading runs
def status_files(key: str | None = None, every: bool = False) -> list[Path]:
    if every:
        folders = [WORK / "_runs"]
        if WORK.is_dir():
            folders += [p / "runs" for p in WORK.iterdir() if p.is_dir() and (p / "runs").is_dir()]
    else:
        folders = [runs_dir(key)]
    files = [f for folder in folders if folder.is_dir() for f in folder.glob("*.json")]
    return sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)


def read_status(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def effective(state: dict) -> str:
    if state.get("status") == "running":
        try:
            age = time.time() - datetime.fromisoformat(state["updated"]).timestamp()
        except (KeyError, ValueError):
            return "stale"
        if age > STALE_S:
            return "stale"
    return state.get("status") or "?"


def recent_runs(key: str | None = None, every: bool = True, limit: int = 10,
                skip_names: tuple[str, ...] = ()) -> list[dict]:
    """The newest runs, each with an 'effective' status (running, ok, failed, stale, ...)."""
    runs = []
    for path in status_files(key, every):
        state = read_status(path)
        if not state or state.get("name") in skip_names:
            continue
        state["effective"] = effective(state)
        runs.append(state)
        if len(runs) >= limit:
            break
    return runs


def describe_run(state: dict) -> str:
    progress = (f"{state.get('done')}/{state.get('total')}" if state.get("total")
                else f"{state.get('lines')} lines" if state.get("lines") else str(state.get("done") or "-"))
    if state.get("percent") is not None:
        progress += f" {state['percent']:.0f}%"
    if state.get("effective") == "running":
        elapsed = time.time() - datetime.fromisoformat(state["started"]).timestamp()
        timing = f"{elapsed:.0f}s so far"
    else:
        timing = f"{state.get('duration_s')}s" if state.get("duration_s") is not None else "-"
    return f"{state.get('effective', state.get('status')):<11} {progress:<14} {timing:<12} {(state.get('message') or '')[:70]}"


def pick(args) -> dict:
    every = args.all or not args.key  # no key: look across every ticket, like `list`
    files = status_files(args.key, every)
    if not files:
        sys.exit(f"no runs in {WORK if every else runs_dir(args.key)}")
    if args.run in (None, "last"):
        chosen = files[0]
    else:
        chosen = next((f for f in files if f.stem.startswith(args.run) or args.run in f.stem), None)
        if not chosen:
            sys.exit(f"no run matching {args.run!r}")
    state = read_status(chosen)
    if not state:
        sys.exit(f"cannot read {chosen}")
    state["effective"] = effective(state)
    return state


def tail_lines(path: str, count: int) -> list[str]:
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read().splitlines()[-count:]
    except OSError:
        return []


# ---------------------------------------------------------------- commands
def cmd_run(args) -> None:
    command = args.command[1:] if args.command and args.command[0] == "--" else args.command
    if not command:
        sys.exit("run: put the command after --, Eg nd_track.py run -- python x.py")
    display = subprocess.list2cmdline(command)
    exe = shutil.which(command[0])
    name = args.name or (Path(command[1]).stem if len(command) > 1 and Path(command[0]).stem.lower()
                         in ("python", "python3", "py") else Path(command[0]).stem)
    env = dict(os.environ, PYTHONUNBUFFERED="1", PYTHONIOENCODING="utf-8")
    if args.key:
        env["ND_KEY"] = args.key.upper()
    timed_out = threading.Event()
    with Tracker(name, key=args.key, argv=command, command=display, quiet=True) as track:
        try:
            proc = subprocess.Popen([exe] + command[1:] if exe else display, shell=not exe,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    env=env, cwd=args.cwd or None)
        except OSError as error:
            track.log(f"could not start the command: {error}")
            raise SystemExit(127)
        track.log(f"started pid={proc.pid}: {display}")
        timer = None
        if args.timeout:
            def expire():
                timed_out.set()
                track.log(f"timeout after {args.timeout}s - stopping the command")
                proc.kill()
            timer = threading.Timer(args.timeout, expire)
            timer.daemon = True
            timer.start()
        for raw in iter(proc.stdout.readline, b""):
            line = raw.decode("utf-8", errors="replace").rstrip("\r\n")
            try:
                sys.stdout.write(line + "\n")
                sys.stdout.flush()
            except (OSError, ValueError):
                pass
            track.output_line(line)
        code = proc.wait()
        if timer:
            timer.cancel()
        if timed_out.is_set():
            track.finish("timeout", exit_code=124)
            raise SystemExit(124)
        if code != 0:
            raise SystemExit(code)
    print(f"[zc] run {track.id}: ok - log {track.log_path}", file=sys.stderr)


def cmd_list(args) -> None:
    runs = recent_runs(args.key, args.all or not args.key, args.limit)
    if args.running:
        runs = [r for r in runs if r["effective"] == "running"]
    if not runs:
        print("no runs")
        return
    print(f"{'run':<44} {'status':<11} {'progress':<14} {'time':<12} message")
    for state in runs:
        print(f"{state['id'][:44]:<44} {describe_run(state)}")


def cmd_status(args) -> None:
    state = pick(args)
    print(f"run      {state['id']}")
    print(f"status   {state['effective']}" + (" (no heartbeat - the process ended without finishing)"
                                              if state["effective"] == "stale" else ""))
    print(f"progress {describe_run(state)}")
    if state.get("command"):
        print(f"command  {state['command']}")
    if state.get("result"):
        print(f"result   {json.dumps(state['result'], default=str)}")
    if state.get("warnings"):
        print(f"warnings {state['warnings']}")
    print(f"started  {state.get('started')}   updated {state.get('updated')}")
    print(f"log      {state.get('log')}")
    for line in tail_lines(state.get("log", ""), args.lines):
        print(f"  {line}")
    status = state["effective"]
    sys.exit(0 if status == "ok" else EXIT_RUNNING if status == "running" else 1)


def cmd_tail(args) -> None:
    state = pick(args)
    for line in tail_lines(state.get("log", ""), args.lines):
        print(line)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("run", help="run a command with progress tracking")
    p.add_argument("--key", help="request id: the run is kept in nd-work/<KEY>/runs/")
    p.add_argument("--name", help="short name for the run (default: the script or program name)")
    p.add_argument("--timeout", type=int, help="stop the command after this many seconds")
    p.add_argument("--cwd", help="working directory for the command")
    p.add_argument("command", nargs=argparse.REMAINDER, help="-- then the command and its arguments")
    p.set_defaults(func=cmd_run)

    for name, func, helptext in (("list", cmd_list, "recent runs"),
                                 ("status", cmd_status, "one run's status and last log lines"),
                                 ("tail", cmd_tail, "the last lines of one run's log")):
        p = sub.add_parser(name, help=helptext)
        if name != "list":
            p.add_argument("run", nargs="?", default="last", help="'last' (default) or part of a run id")
        p.add_argument("--key", help="request id whose runs to read")
        p.add_argument("--all", action="store_true", help="read every runs folder")
        if name == "list":
            p.add_argument("--limit", type=int, default=15)
            p.add_argument("--running", action="store_true", help="only runs still going")
        else:
            p.add_argument("-n", "--lines", type=int, default=5 if name == "status" else 40)
        p.set_defaults(func=func)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
