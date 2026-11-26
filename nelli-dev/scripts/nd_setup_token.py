#!/usr/bin/env python3
"""LEGACY (not part of setup since 0.4.0): store the Znode API credential in the Windows Credential Manager.
THE DEVELOPER RUNS THIS IN THEIR OWN TERMINAL. Setup now asks the developer to set an environment variable instead;
this script stays only so credentials already stored by an earlier version keep working and can be replaced.

It reads the token with hidden input and saves it in the Windows Credential Manager (target
"nelli-dev/<environment>"), then records only a reference in the central config. It refuses to run when input
is not an interactive terminal, so a token can never be piped in by an agent or script, and it never prints the value.

Usage (in your own terminal)
  python nd_setup_token.py --env <environment name>
  python nd_setup_token.py --env <environment name> --use-env-var MY_ZNODE_TOKEN    other systems, or if you prefer
                                                          an environment variable you set yourself (nothing is stored)
Paste the credential without the words "Basic" or "Bearer" (they are removed if you include them).
"""
from __future__ import annotations

import argparse
import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nd_config  # noqa: E402
import nd_cred  # noqa: E402


def record(env_name: str, ref: str) -> None:
    cfg = nd_config.load()
    for e in cfg["environments"]:
        if e["name"] == env_name:
            e["credential_ref"] = ref
            nd_config.save(cfg)
            return
    # environment may still be only in an old workspace file: carry it over
    legacy = next((e for e in nd_config.environments(__import__("nd_ws").workspace()) if e.get("name") == env_name), None)
    if not legacy:
        sys.exit(f"no environment named {env_name}: record it first (/nelli-dev:setup or nd_env.py add)")
    cfg["environments"].append({k: v for k, v in dict(legacy, credential_ref=ref).items() if k != "legacy"})
    nd_config.save(cfg)


def store_token(env_name: str, secret: str) -> str:
    """Save a secret for an environment and record its reference. Returns the reference. Used by main() and the tests."""
    ref = nd_cred.ref_for(env_name)
    if not ref:
        raise RuntimeError("no credential store on this system: use --use-env-var")
    nd_cred.put(ref, secret)
    record(env_name, ref)
    return ref


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--env", required=True)
    ap.add_argument("--use-env-var", metavar="NAME")
    a = ap.parse_args()
    if a.use_env_var:
        record(a.env, f"env:{a.use_env_var}")
        print(f"recorded: {a.env} reads its credential from the environment variable {a.use_env_var} (set it yourself; nothing was stored).")
        return 0
    if not sys.stdin.isatty():
        sys.exit("refusing: run this yourself in an interactive terminal. The credential is never accepted through a pipe, a file or chat.")
    secret = getpass.getpass(f"Credential for {a.env} (input hidden): ")
    if not secret.strip():
        sys.exit("nothing entered; nothing stored")
    try:
        store_token(a.env, secret)
    except (RuntimeError, ValueError, OSError) as ex:
        sys.exit(f"not stored: {ex}")
    print(f"stored in the credential store for {a.env} (value not shown). Close this window; tell the assistant only that it is done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
