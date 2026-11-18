#!/usr/bin/env python3
"""Call the developer's recorded gateway with the stored credential. The only script (with nd_discover.py, which imports it) that sends the token.

Usage
  python nd_call.py GET /v1/stores --query pageSize=3 [--env dev] [--key REQ-ID] [--save] [--auth basic|bearer|none]
  python nd_call.py POST /v1/things --body-file body.json --allow-write      only after the developer approved THIS call

Rules enforced here (not left to the model):
  - only the recorded gateway host: a full URL on any other host is refused; redirects are never followed
  - GET and HEAD by default; any other method needs --allow-write (the guard also asks the developer)
  - writes whose route looks like money or card handling are refused outright: hand the curl to the developer
  - at most NELLIDEV_CALL_BUDGET calls (default 25) per request key; timeouts 20 s; 429 backs off at most twice
  - the credential is attached inside this process. Output, saved responses and errors are redacted: the credential
    itself, JWTs, Basic/Bearer strings, secret-like keys and personal-data keys (email, phone, names, street, birth date)
  - body output is capped (--max-chars, default 6000); the full redacted response can be saved with --save to
    nd-work/<key>/responses/ for reuse by nd_discover.py
"""
from __future__ import annotations

import argparse
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import quote, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nd_config  # noqa: E402
import nd_cred  # noqa: E402

BUDGET = int(os.environ.get("NELLIDEV_CALL_BUDGET", "25"))
TIMEOUT = 20
MONEY = re.compile(r"authori[sz]e|capture|refund|void|purchase|charge|payment|transaction|vault|credit[- ]?card|bank|transfer", re.I)
SECRET_KEY = re.compile(r"pass(word|wd)|secret|token|authorization|api[-_]?key|access[-_]?key|private[-_]?key|card[-_]?number|cvv|security[-_]?code|ssn", re.I)
PII_KEY = re.compile(r"^(e-?mail(address)?|phone(number)?|mobile(number)?|first-?name|last-?name|middle-?name|street(address)?\d*|address\d?|"
                     r"postal-?code|zip(code)?|date-?of-?birth|dob|birth-?date)$", re.I)
JWT = re.compile(r"eyJ[\w-]{5,}\.[\w-]{5,}\.[\w-]{5,}")
AUTH_TEXT = re.compile(r"\b(Basic|Bearer)\s+[A-Za-z0-9+/=._~-]{12,}")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def redact_text(text: str, secrets=()) -> str:
    for s in secrets:
        if s and len(s) >= 6:
            text = text.replace(s, "<credential>")
    text = JWT.sub("<jwt>", text)
    return AUTH_TEXT.sub(lambda m: m.group(1) + " <credential>", text)


def redact_json(node, secrets=()):
    if isinstance(node, dict):
        out = {}
        for k, v in node.items():
            if SECRET_KEY.search(k) and isinstance(v, (str, int, float)):
                out[k] = "<redacted>"
            elif PII_KEY.match(k) and isinstance(v, (str, int, float)) and v not in ("", None):
                out[k] = "<masked>"
            else:
                out[k] = redact_json(v, secrets)
        return out
    if isinstance(node, list):
        return [redact_json(x, secrets) for x in node]
    if isinstance(node, str):
        return redact_text(node, secrets)
    return node


def work_dir(key: str) -> Path:
    return Path(__import__("nd_ws").workspace()) / "nd-work" / key / "responses"


def spend(key: str) -> int:
    """Count this call against the request's budget; exit when it is used up."""
    d = work_dir(key)
    d.mkdir(parents=True, exist_ok=True)
    f = d / "_budget.json"
    try:
        n = json.loads(f.read_text(encoding="utf-8")).get("calls", 0)
    except (OSError, ValueError):
        n = 0
    if n >= BUDGET:
        sys.exit(f"call budget used up ({BUDGET} calls for {key}). Ask the developer before raising NELLIDEV_CALL_BUDGET.")
    f.write_text(json.dumps({"calls": n + 1}), encoding="utf-8")
    return n + 1


def build_url(env: dict, target: str, query: list[str]) -> str:
    base = env["gateway_url"].rstrip("/")
    if re.match(r"^https?://", target, re.I):
        if urlsplit(target).netloc.lower() != urlsplit(base).netloc.lower():
            sys.exit(f"refusing: {urlsplit(target).netloc} is not the recorded gateway ({urlsplit(base).netloc}).")
        url = target
    else:
        url = base + "/" + target.lstrip("/")
    if query:
        pairs = []
        for q in query:
            k, _, v = q.partition("=")
            pairs.append(f"{quote(k, safe='')}={quote(v, safe='')}")
        url += ("&" if "?" in url else "?") + "&".join(pairs)
    return url


def call(env: dict, method: str, target: str, query=(), body: bytes | None = None, auth: str | None = None, key: str = "adhoc",
         allow_write: bool = False) -> dict:
    """One call. Returns {status, ms, size, json, text, url}; text and json are RAW (unredacted): redact before showing."""
    method = method.upper()
    if method not in ("GET", "HEAD") and not allow_write:
        sys.exit(f"refusing {method}: only GET and HEAD run without --allow-write, and that needs the developer's approval of this exact call.")
    if method not in ("GET", "HEAD") and MONEY.search(target):
        sys.exit("refusing: this route looks like money or card handling. Hand the curl to the developer; it is never run here.")
    url = build_url(env, target, list(query))
    headers = {"Accept": "application/json", "User-Agent": "nelli-dev"}
    secret = None
    scheme = auth or env.get("auth_scheme", "auto")
    if scheme != "none":
        got = nd_cred.resolve(dict(env, auth_scheme=auth) if auth in ("basic", "bearer") else env)
        if not got:
            sys.exit("no credential for this environment: the developer runs nd_setup_token.py in their own terminal (see /nelli-dev:setup).")
        used, secret, _src = got
        used = used if used in ("basic", "bearer") else "basic"
        headers["Authorization"] = ("Basic " if used == "basic" else "Bearer ") + secret
    if body is not None:
        headers["Content-Type"] = "application/json"
    spend(key)
    opener = urllib.request.build_opener(NoRedirect, urllib.request.HTTPSHandler(context=ssl.create_default_context()))
    resp = None
    for attempt in range(3):
        req = urllib.request.Request(url, data=body, method=method, headers=headers)
        t0 = time.time()
        try:
            resp = opener.open(req, timeout=TIMEOUT)
            status, raw = resp.status, resp.read()
        except urllib.error.HTTPError as ex:
            status, raw = ex.code, ex.read()
            if status == 429 and attempt < 2:
                time.sleep(min(float(ex.headers.get("Retry-After", "1") or 1), 10))
                continue
        except (urllib.error.URLError, OSError) as ex:
            sys.exit(f"UNREACHABLE {urlsplit(url).netloc}: {redact_text(str(getattr(ex, 'reason', ex)), [secret])}")
        break
    text = raw.decode("utf-8", errors="replace")
    try:
        data = json.loads(text) if text.strip() else None
    except ValueError:
        data = None
    return {"status": status, "ms": int((time.time() - t0) * 1000), "size": len(raw), "json": data, "text": text, "url": url, "secret": secret}


def shown(res: dict) -> str:
    """Redacted body text for display or storage."""
    secrets = [res.get("secret")]
    if res["json"] is not None:
        return json.dumps(redact_json(res["json"], secrets), indent=1)
    return redact_text(res["text"], secrets)


def save(key: str, method: str, target: str, res: dict) -> Path:
    d = work_dir(key)
    d.mkdir(parents=True, exist_ok=True)
    n = len([p for p in d.glob("*.json") if not p.name.startswith("_")]) + 1
    slug = re.sub(r"[^A-Za-z0-9]+", "-", target.split("?")[0]).strip("-")[:60]
    f = d / f"{n:03d}-{method}-{slug}.json"
    f.write_text(json.dumps({"method": method, "path": target.split("?")[0], "status": res["status"],
                             "body": json.loads(shown(res)) if res["json"] is not None else shown(res)}, indent=1), encoding="utf-8")
    return f


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("method")
    ap.add_argument("target", help="path on the recorded gateway (or a full URL on it)")
    ap.add_argument("--query", action="append", default=[], metavar="k=v")
    ap.add_argument("--env")
    ap.add_argument("--key", default="adhoc")
    ap.add_argument("--auth", choices=["basic", "bearer", "none"])
    ap.add_argument("--body-file")
    ap.add_argument("--allow-write", action="store_true")
    ap.add_argument("--save", action="store_true")
    ap.add_argument("--max-chars", type=int, default=6000)
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    env = nd_config.pick_env(a.env, __import__("nd_ws").workspace())
    if not env:
        sys.exit("no environment recorded (or several: pass --env). Run /nelli-dev:setup.")
    body = Path(a.body_file).read_bytes() if a.body_file else None
    res = call(env, a.method, a.target, a.query, body, a.auth, a.key, a.allow_write)
    print(f"HTTP {res['status']} ({res['ms']} ms, {res['size']} bytes) {a.method.upper()} {urlsplit(res['url']).path}")
    text = shown(res)
    print(text[: a.max_chars] + (f"\n... truncated ({len(text)} chars); use --save and read the file" if len(text) > a.max_chars else ""))
    if a.save:
        print("saved:", save(a.key, a.method.upper(), a.target, res))
    return 0 if res["status"] < 400 else 2


if __name__ == "__main__":
    sys.exit(main())
