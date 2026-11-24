#!/usr/bin/env python3
"""Token and cost estimates for Nelli-Dev commands, and the per-request and daily caps. Standard library only, no network.

ALL NUMBERS ARE ESTIMATES (bands from a few measured runs, not a bill). Real cost depends on the model, the size of the
workspace and how much of the knowledge is read. Tokens are derived from cost with an assumed blended price per million tokens.

Usage
  python nd_budget.py estimate <command> [--json]     band, typical cost and tokens, and whether a go-ahead is needed
  python nd_budget.py check [--command <c>] [--helpers N] [--json]
                                                      today's recorded spend against the caps; with --command also that command's estimate
  python nd_budget.py record --command <c> [--usd N]  add to today's ledger (estimate unless --usd is given)
  python nd_budget.py rule                            the rule text the agents follow

Commands: advise, ask, curl, recommend-api, review, deliver (also: docs, setup, status are about zero).

Caps come from the central configuration file (key "budget"), read defensively; the file is never written by this script.
Expected shape (all optional):
  "budget": {"per_request_usd": 2.0, "daily_usd": 15.0, "max_helper_agents": 4, "usd_per_mtok": 3.0, "enabled": true}
Defaults are used for anything missing or invalid. The ledger is <config folder>/budget-ledger.json (spend per day).

Exit codes: 0 within the caps, 3 a go-ahead from the developer is needed (above the per-request cap or the helper cap),
4 the daily cap is reached (stop and report), 2 usage error.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

# command -> (low USD, typical USD, high USD, basis)
BANDS = {
    "advise": (0.10, 0.20, 0.40, "measured: about 0.2 USD"),
    "ask": (0.05, 0.15, 0.30, "measured: a regression question about 0.15 USD"),
    "curl": (0.10, 0.40, 1.00, "measured: about 0.1 to 1 USD, more when many values must be discovered"),
    "recommend-api": (0.10, 0.20, 0.50, "not measured separately: assumed between ask and curl"),
    "review": (0.30, 1.00, 3.00, "not measured: assumed from the size of a diff"),
    "deliver": (3.00, 6.00, 12.00, "measured: about 6 USD; large requirements cost more"),
    "docs": (0.05, 0.10, 0.30, "not measured"),
    "setup": (0.0, 0.02, 0.05, "not measured"),
    "status": (0.0, 0.01, 0.03, "not measured"),
}
ALIASES = {"recommend": "recommend-api", "recommend_api": "recommend-api", "regression": "ask", "question": "ask", "advice": "advise"}
DEFAULTS = {"per_request_usd": 2.0, "daily_usd": 15.0, "max_helper_agents": 4, "usd_per_mtok": 3.0, "enabled": True}

RULE = """Budget rule (estimates, not a bill)
1. Before a heavy command (anything with an estimate above the per-request cap, today deliver and review) run
   python nd_budget.py estimate <command>, show the band to the developer in one line, and ask for a go-ahead
   (Proceed (Recommended) / Cheaper variant / Stop). Without a go-ahead do not start it.
2. Run python nd_budget.py check at the start of a request. Exit 4 = the daily cap is reached: stop and report. Exit 3 = ask.
3. Retrieve, do not read everything: nd_pack_search.py find then show only the top documents; read only the skill sections the task needs
   (search the file for the heading), not whole skills; open an API spec operation, not a whole spec.
4. Use the cheaper model for lookups where an agent allows it (Explore for read-only searches); keep the main model for judgment.
5. At most max_helper_agents helper agents per request (default 4), started in one message; no helper for a step one script settles.
6. At the cap, stop and report what is done, what is left and what it would cost; never continue silently.
7. After the run: python nd_budget.py record --command <c> so the daily total stays honest."""


def _config_path() -> Path:
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import nd_config
        return nd_config.path()
    except Exception:
        h = os.environ.get("NELLIDEV_HOME")
        return (Path(h).expanduser() if h else Path.home() / ".nelli-dev") / "config.json"


def caps() -> dict:
    out = dict(DEFAULTS)
    try:
        data = json.loads(_config_path().read_text(encoding="utf-8-sig"))
        b = data.get("budget") if isinstance(data, dict) else None
        if isinstance(b, dict):
            for k, default in DEFAULTS.items():
                v = b.get(k)
                if isinstance(default, bool):
                    if isinstance(v, bool):
                        out[k] = v
                elif isinstance(v, (int, float)) and not isinstance(v, bool) and v > 0:
                    out[k] = type(default)(v)
    except (OSError, ValueError):
        pass
    return out


def ledger_path() -> Path:
    return _config_path().parent / "budget-ledger.json"


def spent_today() -> float:
    try:
        data = json.loads(ledger_path().read_text(encoding="utf-8"))
        return float(data.get(date.today().isoformat(), 0.0))
    except (OSError, ValueError, TypeError):
        return 0.0


def estimate(command: str) -> dict:
    c = ALIASES.get(command.lower().lstrip("/").replace("nelli-dev:", ""), command.lower().lstrip("/").replace("nelli-dev:", ""))
    if c not in BANDS:
        raise KeyError(command)
    lo, typ, hi, basis = BANDS[c]
    cp = caps()
    rate = cp["usd_per_mtok"]
    tok = lambda usd: int(usd / rate * 1_000_000)  # noqa: E731
    return {"command": c, "label": "ESTIMATE", "usd_low": lo, "usd_typical": typ, "usd_high": hi, "tokens_low": tok(lo), "tokens_typical": tok(typ),
            "tokens_high": tok(hi), "basis": basis, "assumed_usd_per_mtok": rate, "per_request_cap_usd": cp["per_request_usd"],
            "needs_go_ahead": cp["enabled"] and typ > cp["per_request_usd"], "high_exceeds_cap": cp["enabled"] and hi > cp["per_request_usd"]}


def line(e: dict) -> str:
    return (f"ESTIMATE for {e['command']}: about {e['usd_typical']:.2f} USD (band {e['usd_low']:.2f}-{e['usd_high']:.2f}), "
            f"roughly {e['tokens_typical']//1000}k tokens ({e['tokens_low']//1000}k-{e['tokens_high']//1000}k; assumes {e['assumed_usd_per_mtok']:g} USD per million tokens). "
            f"Basis: {e['basis']}. Per-request cap {e['per_request_cap_usd']:g} USD: "
            + ("a go-ahead is needed." if e["needs_go_ahead"] else ("within the cap, but the high end may exceed it." if e["high_exceeds_cap"] else "within the cap.")))


def cmd_check(a) -> int:
    cp = caps()
    spent = spent_today()
    res = {"enabled": cp["enabled"], "spent_today_usd": round(spent, 2), "daily_cap_usd": cp["daily_usd"], "per_request_cap_usd": cp["per_request_usd"],
           "max_helper_agents": cp["max_helper_agents"], "status": "ok", "notes": []}
    code = 0
    if cp["enabled"] and spent >= cp["daily_usd"]:
        res["status"], code = "daily-cap-reached", 4
        res["notes"].append("the daily cap is reached: stop and report; do not continue silently")
    if a.command:
        try:
            e = estimate(a.command)
        except KeyError:
            print(f"unknown command '{a.command}'; known: {', '.join(BANDS)}", file=sys.stderr)
            return 2
        res["estimate"] = e
        if cp["enabled"] and code == 0:
            if spent + e["usd_typical"] > cp["daily_usd"]:
                res["status"], code = "would-exceed-daily-cap", 3
                res["notes"].append(f"typical cost would take today's total to {spent + e['usd_typical']:.2f} USD, above the daily cap")
            elif e["needs_go_ahead"]:
                res["status"], code = "go-ahead-needed", 3
                res["notes"].append("typical cost is above the per-request cap")
    if a.helpers is not None and cp["enabled"] and a.helpers > cp["max_helper_agents"]:
        res["status"] = res["status"] if code == 4 else "too-many-helpers"
        code = 4 if code == 4 else 3
        res["notes"].append(f"{a.helpers} helper agents planned, the cap is {cp['max_helper_agents']}: reduce the plan or ask for a go-ahead")
    res["exit"] = code
    if a.json:
        print(json.dumps(res, indent=1))
    else:
        print(f"budget {res['status']}: today {res['spent_today_usd']:.2f} of {res['daily_cap_usd']:g} USD (estimates); per-request cap {res['per_request_cap_usd']:g} USD")
        if "estimate" in res:
            print(line(res["estimate"]))
        for n in res["notes"]:
            print("  - " + n)
    return code


def cmd_record(a) -> int:
    try:
        usd = a.usd if a.usd is not None else estimate(a.command)["usd_typical"]
    except KeyError:
        print(f"unknown command '{a.command}'", file=sys.stderr)
        return 2
    p = ledger_path()
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        data = {}
    today = date.today().isoformat()
    data = {k: v for k, v in data.items() if k >= (date.today().replace(day=1).isoformat())}      # keep this month only
    data[today] = round(float(data.get(today, 0.0)) + usd, 4)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=1), encoding="utf-8")
    print(f"recorded {usd:.2f} USD (estimate) for {a.command}; today {data[today]:.2f} USD")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("estimate"); e.add_argument("command"); e.add_argument("--json", action="store_true")
    c = sub.add_parser("check"); c.add_argument("--command"); c.add_argument("--helpers", type=int); c.add_argument("--json", action="store_true")
    r = sub.add_parser("record"); r.add_argument("--command", required=True); r.add_argument("--usd", type=float)
    sub.add_parser("rule")
    try:
        a = ap.parse_args(argv)
    except SystemExit as ex:
        return 2 if ex.code else 0
    if a.cmd == "estimate":
        try:
            est = estimate(a.command)
        except KeyError:
            print(f"unknown command '{a.command}'; known: {', '.join(BANDS)}", file=sys.stderr)
            return 2
        print(json.dumps(est, indent=1) if a.json else line(est))
        return 0
    if a.cmd == "check":
        return cmd_check(a)
    if a.cmd == "record":
        return cmd_record(a)
    print(RULE)
    return 0


if __name__ == "__main__":
    sys.exit(main())
