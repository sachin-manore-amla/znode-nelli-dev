#!/usr/bin/env python3
"""Credential handling for Nelli-Dev. The only module that can read the stored token.

The token is saved by the developer in their own terminal (nd_setup_token.py) in the Windows Credential
Manager (generic credential, target "nelli-dev/<environment>"). The central config keeps only a reference:
  credman:nelli-dev/<environment>     stored in the Windows Credential Manager
  env:<NAME>                          read from an environment variable the developer sets (other systems, or by choice)
Fallback when an environment has no reference: ZNODE_API_BASIC (basic) or ZNODE_API_TOKEN (bearer), as before.

This command line has NO command that prints a token, and none should be added. Code that needs the value
(nd_call.py) imports resolve() and uses it inside the process, never printing it.

Usage
  python nd_cred.py status [--name <environment>]     stored / missing / env var set (never a value)
  python nd_cred.py forget --name <environment>       delete the stored credential (the guard asks the developer)
"""
from __future__ import annotations

import argparse
import os
import sys

IS_WINDOWS = os.name == "nt"
SCHEME_VARS = {"basic": "ZNODE_API_BASIC", "bearer": "ZNODE_API_TOKEN"}
MAX_BLOB = 2560

if IS_WINDOWS:
    import ctypes
    from ctypes import wintypes

    class _CRED(ctypes.Structure):
        _fields_ = [("Flags", wintypes.DWORD), ("Type", wintypes.DWORD), ("TargetName", wintypes.LPWSTR),
                    ("Comment", wintypes.LPWSTR), ("LastWritten", wintypes.FILETIME),
                    ("CredentialBlobSize", wintypes.DWORD), ("CredentialBlob", ctypes.POINTER(ctypes.c_ubyte)),
                    ("Persist", wintypes.DWORD), ("AttributeCount", wintypes.DWORD), ("Attributes", ctypes.c_void_p),
                    ("TargetAlias", wintypes.LPWSTR), ("UserName", wintypes.LPWSTR)]

    _adv = ctypes.WinDLL("advapi32", use_last_error=True)
    _adv.CredWriteW.argtypes = [ctypes.POINTER(_CRED), wintypes.DWORD]
    _adv.CredWriteW.restype = wintypes.BOOL
    _adv.CredReadW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.POINTER(ctypes.POINTER(_CRED))]
    _adv.CredReadW.restype = wintypes.BOOL
    _adv.CredDeleteW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD]
    _adv.CredDeleteW.restype = wintypes.BOOL
    _adv.CredFree.argtypes = [ctypes.c_void_p]


def ref_for(env_name: str) -> str | None:
    return f"credman:nelli-dev/{env_name}" if IS_WINDOWS else None


def _target(ref: str) -> str:
    return ref.split(":", 1)[1]


def put(ref: str, secret: str) -> None:
    """Store a secret under a credman: reference. Raises on failure; never prints the value."""
    if not (IS_WINDOWS and ref.startswith("credman:")):
        raise RuntimeError("the credential store is available on Windows only; use an environment variable (env:<NAME>)")
    blob = secret.encode("utf-8")
    if not blob or len(blob) > MAX_BLOB:
        raise ValueError(f"the credential must be 1 to {MAX_BLOB} bytes")
    buf = (ctypes.c_ubyte * len(blob)).from_buffer_copy(blob)
    cred = _CRED()
    cred.Type = 1                       # CRED_TYPE_GENERIC
    cred.TargetName = _target(ref)
    cred.CredentialBlobSize = len(blob)
    cred.CredentialBlob = ctypes.cast(buf, ctypes.POINTER(ctypes.c_ubyte))
    cred.Persist = 2                    # CRED_PERSIST_LOCAL_MACHINE
    cred.UserName = "nelli-dev"
    if not _adv.CredWriteW(ctypes.byref(cred), 0):
        raise OSError(f"could not write the credential (error {ctypes.get_last_error()})")


def _read(ref: str) -> str | None:
    if not (IS_WINDOWS and ref.startswith("credman:")):
        return None
    p = ctypes.POINTER(_CRED)()
    if not _adv.CredReadW(_target(ref), 1, 0, ctypes.byref(p)):
        return None
    try:
        c = p.contents
        return bytes(bytearray(c.CredentialBlob[i] for i in range(c.CredentialBlobSize))).decode("utf-8")
    finally:
        _adv.CredFree(p)


def delete(ref: str) -> bool:
    if not (IS_WINDOWS and ref.startswith("credman:")):
        return False
    return bool(_adv.CredDeleteW(_target(ref), 1, 0))


def _strip_prefix(value: str) -> str:
    for p in ("Basic ", "Bearer ", "basic ", "bearer "):
        if value.startswith(p):
            return value[len(p):].strip()
    return value.strip()


def resolve(env: dict):
    """(scheme, secret, source) for an environment record, or None. The secret never leaves the calling process."""
    scheme = env.get("auth_scheme", "auto")
    ref = env.get("credential_ref")
    if ref:
        if ref.startswith("credman:"):
            v = _read(ref)
            if v:
                return (scheme, _strip_prefix(v), "credential store")
        elif ref.startswith("env:") and os.environ.get(ref[4:]):
            return (scheme, _strip_prefix(os.environ[ref[4:]]), f"environment variable {ref[4:]}")
    order = [scheme] if scheme in SCHEME_VARS else ["basic", "bearer"]
    for s in order:
        var = SCHEME_VARS[s]
        if os.environ.get(var):
            return (s, _strip_prefix(os.environ[var]), f"environment variable {var}")
    return None


def state(env: dict) -> str:
    """Human-readable credential state. Never a value."""
    ref = env.get("credential_ref")
    if ref and ref.startswith("credman:"):
        if _read(ref):
            return "stored in the credential store"
    elif ref and ref.startswith("env:"):
        return f"env {ref[4:]} set" if os.environ.get(ref[4:]) else f"env {ref[4:]} NOT set"
    for s in (["basic", "bearer"] if env.get("auth_scheme", "auto") == "auto" else [env["auth_scheme"]]):
        if s in SCHEME_VARS and os.environ.get(SCHEME_VARS[s]):
            return f"env {SCHEME_VARS[s]} set"
    return "NOT set"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("status"); s.add_argument("--name")
    f = sub.add_parser("forget"); f.add_argument("--name", required=True)
    a = ap.parse_args()
    import nd_config
    root = __import__("nd_ws").workspace()
    if a.cmd == "status":
        envs = [e for e in nd_config.environments(root) if not a.name or e.get("name") == a.name]
        if not envs:
            print("no environment recorded")
            return 1
        for e in envs:
            print(f"{e['name']}: {state(e)}")
        return 0
    e = nd_config.pick_env(a.name, root)
    if not e or not e.get("credential_ref"):
        sys.exit("no stored credential reference for that environment")
    print("deleted" if delete(e["credential_ref"]) else "nothing to delete")
    return 0


if __name__ == "__main__":
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.exit(main())
