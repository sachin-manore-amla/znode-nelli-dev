#!/usr/bin/env python3
"""Record and check the developer's Znode environment (the API gateway URL used to connect to and test the APIs).

Nelli-Dev never guesses a host: it asks the developer for the gateway URL, records it here, and the guard then
allows API calls to that host only.

Usage
  python nd_env.py add --name dev --gateway-url https://<gateway host> --non-production [--note "<text>"]
  python nd_env.py from-env --name dev --non-production [--var NELLIDEV_GATEWAY_URL]   record the URL the developer set as a variable
  python nd_env.py credvar --name dev --var MY_TOKEN_VAR     record which variable holds the credential (name only)
  python nd_env.py list
  python nd_env.py check [--name dev]       # read-only reachability test + whether credentials are set (never their values)
  python nd_env.py remove --name dev
  python nd_env.py base [--name dev]        # print the recorded gateway URL (used by nd_query_spec.py when --base is omitted)

Recorded in the central config (%USERPROFILE%/.nelli-dev/config.json, see nd_config.py). Every change to it (a command run by the agent) asks the developer to confirm on screen
(the guard), because it decides which host the agent may call.

Rules enforced here: https only (http allowed for localhost); no credentials or query strings in the URL; the developer
must state the environment is NOT production (--non-production is required). Credentials are never stored here: the developer sets ZNODE_API_BASIC / ZNODE_API_TOKEN (and NELLIDEV_GATEWAY_URL)
as environment variables in their own terminal; this file records only the variable name.
`check` sends one unauthenticated GET to the gateway root and reports the status code; any HTTP status (even 401/404)
proves the host is reachable, a connection error proves it is not. It never sends a secret.
"""
from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit


def root() -> Path:
    return Path(__import__('nd_ws').workspace()).resolve()


def load() -> dict:
    """Environments from the central config (nd_config.py), plus any still only in an old workspace file."""
    import nd_config
    return {"environments": nd_config.environments(root())}


def save(envs: list) -> None:
    import nd_config
    nd_config.set_environments(envs)


def pick(data: dict, name: str | None):
    import nd_config
    return nd_config.pick_env(name, root())


def cmd_add(a) -> int:
    u = urlsplit(a.gateway_url)
    local = u.hostname in ("localhost", "127.0.0.1", "::1")
    if u.scheme != "https" and not (u.scheme == "http" and local):
        sys.exit("the gateway URL must be https (http only for localhost)")
    if not u.hostname or u.username or u.password or u.query or u.fragment:
        sys.exit("give the bare gateway URL: no credentials, query string or fragment")
    if not a.non_production:
        sys.exit("refusing: Nelli-Dev only works against development or test environments. Re-run with --non-production once the developer has confirmed this is not production.")
    url = f"{u.scheme}://{u.netloc}{u.path.rstrip('/')}"
    data = load()
    old = next((e for e in data["environments"] if e["name"] == a.name), {})
    rec = {"name": a.name, "gateway_url": url, "host": u.netloc, "non_production": True,
           "auth_scheme": a.auth_scheme, "note": a.note or ""}
    if old.get("credential_ref"):
        rec["credential_ref"] = old["credential_ref"]
    save([e for e in data["environments"] if e["name"] != a.name] + [rec])
    print(f"recorded {a.name}: {url}  (API calls are now allowed to {u.netloc} only)")
    return 0


URL_VAR = "NELLIDEV_GATEWAY_URL"


def cmd_from_env(a) -> int:
    """Record the gateway URL the developer set as an environment variable in their own terminal."""
    var = a.var or URL_VAR
    value = os.environ.get(var, "").strip()
    if not value:
        sys.exit(f"the variable {var} is not set in this session. The developer sets it in their own terminal "
                 f"(setup shows the command) and restarts Claude Code so it is visible here. Never pass the URL through chat.")
    a.gateway_url = value
    a.note = a.note or f"from {var}"
    a.auth_scheme = a.auth_scheme or "auto"
    rc = cmd_add(a)
    if rc == 0:
        data = load()
        for e in data["environments"]:
            if e["name"] == a.name:
                e["gateway_url_var"] = var
        save(data["environments"])
    return rc


def cmd_credvar(a) -> int:
    """Record WHICH environment variable holds the credential (the name only; never a value)."""
    import re
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{1,63}", a.var):
        sys.exit("give a plain variable name (letters, digits, underscore)")
    data = load()
    for e in data["environments"]:
        if e["name"] == a.name:
            e["credential_ref"] = f"env:{a.var}"
            save(data["environments"])
            print(f"recorded: {a.name} reads its credential from the environment variable {a.var} (the developer sets it in their own terminal).")
            return 0
    sys.exit(f"no environment named {a.name}: record it first")


def creds_status(e: dict | None = None) -> str:
    import nd_cred
    envs = [e] if e else load()["environments"]
    return " · ".join(f"credential {x['name']}: {nd_cred.state(x)}" for x in envs) + " (values never shown)"


def cmd_list(_a) -> int:
    envs = load()["environments"]
    if not envs:
        print("no environment recorded: ask the developer for the gateway URL of their development environment (or record that none is available: runtime claims stay code-only).")
        return 1
    for e in envs:
        print(f"{e['name']:10} {e['gateway_url']}   {e.get('note', '')}")
    print(creds_status())
    return 0


def cmd_check(a) -> int:
    e = pick(load(), a.name)
    if not e:
        sys.exit("no such environment (or several recorded: give --name)")
    ctx = ssl.create_default_context()
    req = urllib.request.Request(e["gateway_url"], method="GET", headers={"User-Agent": "nelli-dev-reachability-check"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
            code = r.status
    except urllib.error.HTTPError as ex:
        code = ex.code
    except (urllib.error.URLError, OSError) as ex:
        print(f"UNREACHABLE {e['gateway_url']}: {getattr(ex, 'reason', ex)}")
        print(creds_status(e))
        return 1
    print(f"REACHABLE {e['gateway_url']}: HTTP {code} in {int((time.time() - t0) * 1000)} ms (unauthenticated GET of the root; a 401/403/404 here is normal)")
    print(creds_status(e))
    import nd_cred
    if code < 500 and nd_cred.state(e).endswith("NOT set"):
        print("authenticated calls need the credential variable (ZNODE_API_BASIC or ZNODE_API_TOKEN) set by the developer in their own terminal, then Claude Code restarted; never paste the credential in chat. /nelli-dev:setup shows the command.")
    return 0


def cmd_remove(a) -> int:
    save([e for e in load()["environments"] if e["name"] != a.name])
    print("removed", a.name, "(a stored credential is kept: nd_cred.py forget removes it)")
    return 0


def cmd_base(a) -> int:
    e = pick(load(), a.name)
    if not e:
        return 1
    print(e["gateway_url"])
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("add"); s.add_argument("--name", required=True); s.add_argument("--gateway-url", required=True)
    s.add_argument("--non-production", action="store_true"); s.add_argument("--auth-scheme", choices=["auto", "basic", "bearer"], default="auto"); s.add_argument("--note"); s.set_defaults(fn=cmd_add)
    fe = sub.add_parser("from-env"); fe.add_argument("--name", required=True); fe.add_argument("--var"); fe.add_argument("--non-production", action="store_true")
    fe.add_argument("--auth-scheme", choices=["auto", "basic", "bearer"]); fe.add_argument("--note"); fe.set_defaults(fn=cmd_from_env)
    cv = sub.add_parser("credvar"); cv.add_argument("--name", required=True); cv.add_argument("--var", required=True); cv.set_defaults(fn=cmd_credvar)
    sub.add_parser("list").set_defaults(fn=cmd_list)
    c = sub.add_parser("check"); c.add_argument("--name"); c.set_defaults(fn=cmd_check)
    r = sub.add_parser("remove"); r.add_argument("--name", required=True); r.set_defaults(fn=cmd_remove)
    b = sub.add_parser("base"); b.add_argument("--name"); b.set_defaults(fn=cmd_base)
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
