#!/usr/bin/env python3
"""Central Nelli-Dev configuration: one user-level file shared by every workspace, agent and script.

Location: %USERPROFILE%\\.nelli-dev\\config.json (override the folder with NELLIDEV_HOME).
The file holds NO secret. An environment records only a credential REFERENCE (see nd_cred.py).

Usage
  python nd_config.py status [--json]     what is configured and what is still missing (never a secret value)
  python nd_config.py path                the config file location
  python nd_config.py set-default --name <environment>

Environments and projects are recorded with nd_env.py and nd_projects.py (the guard asks the developer to
confirm each change). The first-time wizard is the /nelli-dev:setup command.

Compatibility: environments and projects recorded by the old per-workspace files (nd-work or zc-work
environment.json / projects.json) are still read when the central file lacks them; nd_migrate.py moves them.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

SCHEMA = 1


def home() -> Path:
    h = os.environ.get("NELLIDEV_HOME")
    return Path(h).expanduser() if h else Path.home() / ".nelli-dev"


def path() -> Path:
    return home() / "config.json"


def _empty() -> dict:
    return {"schema": SCHEMA, "default_env": None, "environments": [], "projects": [], "consent": None, "budget": None}


def load() -> dict:
    cfg = _empty()
    try:
        data = json.loads(path().read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return cfg
    if isinstance(data, dict):
        cfg.update({k: v for k, v in data.items() if k in cfg})
    return cfg


def save(cfg: dict) -> None:
    cfg["schema"] = SCHEMA
    h = home()
    h.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=h, prefix=".cfg", suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(cfg, fh, indent=1)
    os.replace(tmp, path())
    try:
        os.chmod(path(), 0o600)
    except OSError:
        pass


def _legacy(root, name: str) -> dict:
    """Old per-workspace record (nd-work first, then zc-work): read-only."""
    if not root:
        return {}
    for folder in ("nd-work", "zc-work"):
        try:
            return json.loads((Path(root) / folder / name).read_text(encoding="utf-8-sig"))
        except (OSError, ValueError):
            continue
    return {}


def environments(root=None) -> list[dict]:
    envs = list(load()["environments"])
    names = {e.get("name") for e in envs}
    for e in _legacy(root, "environment.json").get("environments", []):
        if e.get("name") not in names and e.get("host"):
            envs.append(dict(e, legacy=True))
    return envs


def projects(root=None) -> list[dict]:
    pr = list(load()["projects"])
    names = {p.get("name") for p in pr}
    for p in _legacy(root, "projects.json").get("projects", []):
        if p.get("name") not in names and p.get("path"):
            pr.append(dict(p, legacy=True))
    return pr


def pick_env(name: str | None = None, root=None):
    envs = environments(root)
    if name:
        return next((e for e in envs if e.get("name") == name), None)
    default = load().get("default_env")
    if default:
        return next((e for e in envs if e.get("name") == default), None)
    return envs[0] if len(envs) == 1 else None


def set_environments(envs: list[dict]) -> None:
    cfg = load()
    cfg["environments"] = [{k: v for k, v in e.items() if k != "legacy"} for e in envs]
    if cfg["default_env"] not in {e["name"] for e in cfg["environments"]}:
        cfg["default_env"] = cfg["environments"][0]["name"] if len(cfg["environments"]) == 1 else None
    save(cfg)


def set_projects(projs: list[dict]) -> None:
    cfg = load()
    cfg["projects"] = [{k: v for k, v in p.items() if k != "legacy"} for p in projs]
    save(cfg)


def status(root=None) -> dict:
    import nd_cred
    envs = environments(root)
    projs = projects(root)
    out_envs = []
    for e in envs:
        out_envs.append({"name": e.get("name"), "gateway_url": e.get("gateway_url"), "non_production": e.get("non_production"),
                         "auth_scheme": e.get("auth_scheme", "auto"), "credential": nd_cred.state(e), "legacy": bool(e.get("legacy"))})
    missing = []
    if not envs:
        missing.append("environment (gateway URL)")
    elif not any(x["credential"].startswith(("stored", "env ")) for x in out_envs):
        missing.append("credential (the developer sets ZNODE_API_BASIC or ZNODE_API_TOKEN in their own terminal and restarts Claude Code)")
    if not projs:
        missing.append("project folders (Custom API SDK and/or Webstore)")
    return {"config_file": str(path()), "config_exists": path().exists(), "default_env": load().get("default_env"),
            "environments": out_envs,
            "projects": [{"name": p.get("name"), "path": p.get("path"), "legacy": bool(p.get("legacy"))} for p in projs],
            "missing": missing, "configured": not missing}


def cmd_status(a) -> int:
    root = __import__("nd_ws").workspace()
    s = status(root)
    if a.json:
        print(json.dumps(s, indent=1))
        return 0
    print(f"config file: {s['config_file']} ({'present' if s['config_exists'] else 'not created yet'})")
    for e in s["environments"]:
        print(f"environment {e['name']}: {e['gateway_url']} · scheme {e['auth_scheme']} · credential: {e['credential']}"
              + (" · from an old workspace file (run nd_migrate.py)" if e["legacy"] else ""))
    for p in s["projects"]:
        print(f"project {p['name']}: {p['path']}" + (" · from an old workspace file" if p["legacy"] else ""))
    print("configured: yes" if s["configured"] else "still needed: " + "; ".join(s["missing"]))
    return 0


def cmd_path(_a) -> int:
    print(path())
    return 0


def cmd_set_default(a) -> int:
    cfg = load()
    if a.name not in {e["name"] for e in cfg["environments"]}:
        sys.exit("no such environment in the central configuration")
    cfg["default_env"] = a.name
    save(cfg)
    print("default environment:", a.name)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("status"); s.add_argument("--json", action="store_true"); s.set_defaults(fn=cmd_status)
    sub.add_parser("path").set_defaults(fn=cmd_path)
    d = sub.add_parser("set-default"); d.add_argument("--name", required=True); d.set_defaults(fn=cmd_set_default)
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    return a.fn(a)


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.exit(main())
