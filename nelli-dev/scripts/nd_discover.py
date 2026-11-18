#!/usr/bin/env python3
"""Find the real values an API request needs, without a database: earlier responses, read-only GETs on the gateway, spec examples.

Usage
  python nd_discover.py resolve --spec <spec> --op "POST /v1/carts" [--key REQ-ID] [--set name=value ...] [--max-calls 6] [--json]

For every required input of the operation (path, query and header parameters, and body fields whose name ends in Id) it tries, in order:
  1. a value you pass with --set
  2. earlier responses saved for this request key, then for any request (nd-work/*/responses/, already redacted)
  3. a read-only GET through the recorded gateway on an operation of the same spec that returns that field
     (found by name and by the response schema; page size at most 5; GET only; counted against the call budget)
  4. the spec's example, default or first enum value (marked "spec example", not proven)
  5. otherwise: unresolved. Ask the developer, with options.
Nothing is ever written to the gateway here, no database is read, and no credential is printed. Values from live calls
come from the raw response in memory; what is shown and saved is redacted (personal data masked).

The result lists each input with its value, where it came from and how sure that is, and the nd_query_spec.py command
that turns the operation into a curl with these values.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nd_call  # noqa: E402
import nd_config  # noqa: E402
import nd_query_spec as qs  # noqa: E402

PAGE_PARAMS = {"pagesize": 3, "pageindex": 1, "page": 1, "limit": 3, "top": 3, "take": 3}
ID_TAIL = re.compile(r"(Id|ID|Code)$")


def words(name: str) -> list[str]:
    return [w.lower() for w in re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])|\d+", name)]


def param_list(spec: dict, path: str, op: dict) -> list[dict]:
    out = []
    for p in list((spec["paths"][path].get("parameters") or [])) + list(op.get("parameters") or []):
        if isinstance(p, dict) and "$ref" in p:
            p = qs.pointer(spec, p["$ref"])
        if isinstance(p, dict) and p.get("name"):
            out.append(p)
    return out


def deref(spec: dict, schema, depth=0):
    while isinstance(schema, dict) and "$ref" in schema and depth < 8:
        schema, depth = qs.pointer(spec, schema["$ref"]), depth + 1
    return schema if isinstance(schema, dict) else {}


def schema_props(spec: dict, schema, depth=0) -> dict:
    """All property names reachable in a schema (through $ref, allOf, arrays, objects), depth-limited."""
    out = {}
    s = deref(spec, schema)
    if depth > 4:
        return out
    for key in ("allOf", "oneOf", "anyOf"):
        for sub in s.get(key) or []:
            out.update(schema_props(spec, sub, depth + 1))
    if isinstance(s.get("items"), dict):
        out.update(schema_props(spec, s["items"], depth + 1))
    for name, sub in (s.get("properties") or {}).items():
        out[name] = sub
        out.update(schema_props(spec, sub, depth + 1))
    return out


def response_schema(op: dict):
    for code, r in (op.get("responses") or {}).items():
        if str(code).startswith("2") and isinstance(r, dict):
            for ct, c in (r.get("content") or {}).items():
                if "json" in ct and isinstance(c, dict) and c.get("schema"):
                    return c["schema"]
    return None


def required_inputs(spec: dict, path: str, op: dict) -> list[dict]:
    items = []
    for p in param_list(spec, path, op):
        if p.get("required") or p.get("in") == "path":
            items.append({"name": p["name"], "where": p.get("in", "query"), "schema": p.get("schema") or {}, "example": p.get("example")})
    body = ((op.get("requestBody") or {}).get("content") or {})
    for ct, c in body.items():
        if "json" in ct and c.get("schema"):
            s = deref(spec, c["schema"])
            req = set(s.get("required") or [])
            for n, sub in schema_props(spec, c["schema"]).items():
                if ID_TAIL.search(n) and (n in req or not req):
                    items.append({"name": n, "where": "body", "schema": deref(spec, sub), "example": deref(spec, sub).get("example")})
            break
    seen, out = set(), []
    for i in items:
        if i["name"].lower() not in seen:
            seen.add(i["name"].lower())
            out.append(i)
    return out


def find_key(node, name: str):
    """First scalar value of a key (case-insensitive) anywhere in parsed JSON; lists are searched item by item."""
    low = name.lower()
    if isinstance(node, dict):
        for k, v in node.items():
            if k.lower() == low and isinstance(v, (str, int)) and not isinstance(v, bool) and v not in ("", 0, None):
                return v
        for v in node.values():
            r = find_key(v, name)
            if r is not None:
                return r
    elif isinstance(node, list):
        for v in node:
            r = find_key(v, name)
            if r is not None:
                return r
    return None


def from_saved(name: str, key: str):
    base = Path(__import__("nd_ws").workspace()) / "nd-work"
    order = [base / key / "responses"] + [d / "responses" for d in sorted(base.glob("*")) if d.name != key]
    for d in order:
        for f in sorted(d.glob("*.json")) if d.is_dir() else []:
            if f.name.startswith("_"):
                continue
            try:
                v = find_key(json.loads(f.read_text(encoding="utf-8")).get("body"), name)
            except (OSError, ValueError):
                continue
            if v is not None and v not in ("<masked>", "<redacted>"):
                return v, f"earlier response {f.parent.parent.name}/{f.name}"
    return None


def candidates(spec: dict, name: str, own_path: str):
    """GET operations that probably return the field, best first: [(score, path, op)]."""
    ent = [w for w in words(ID_TAIL.sub("", name)) if w not in ("id", "code")] or words(name)
    ranked = []
    for path, verb, op in qs.operations(spec):
        if verb != "get" or path == own_path:
            continue
        if any(p.get("in") == "path" for p in param_list(spec, path, op)):
            continue          # needs another id first: discovery stays one hop deep
        if any((p.get("required") and p.get("in") in ("query", "header")) for p in param_list(spec, path, op)):
            continue
        segs = [re.sub(r"s$", "", s.lower()) for s in re.split(r"[/_\-]", path) if s]
        score = 0
        for w in ent:
            w1 = re.sub(r"s$", "", w)
            if w1 in segs:
                score += 3
            elif any(w1 in s for s in segs):
                score += 1
        text = f"{op.get('operationId', '')} {op.get('summary', '')}".lower()
        score += sum(1 for w in ent if w in text)
        rs = response_schema(op)
        if rs is not None and any(k.lower() == name.lower() for k in schema_props(spec, rs)):
            score += 3
        if score >= 3:
            ranked.append((score - 0.01 * len(path), path, op))
    return sorted(ranked, key=lambda r: -r[0])[:3]


def spec_example(i: dict):
    s = i["schema"] or {}
    if i.get("example") not in (None, ""):
        return i["example"]
    for k in ("example", "default"):
        if s.get(k) not in (None, ""):
            return s[k]
    if s.get("enum"):
        return s["enum"][0]
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("resolve")
    r.add_argument("--spec", required=True)
    r.add_argument("--op", required=True, help='"METHOD /path"')
    r.add_argument("--key", default="adhoc")
    r.add_argument("--env")
    r.add_argument("--set", action="append", default=[], metavar="name=value")
    r.add_argument("--max-calls", type=int, default=6)
    r.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    verb, _, path = a.op.partition(" ")
    spec = qs.load(a.spec)
    path_, verb_, op = qs.find_operations(spec, path.strip(), verb)[0]
    env = nd_config.pick_env(a.env, __import__("nd_ws").workspace())
    given = dict(s.split("=", 1) for s in a.set)
    rows, calls = [], 0
    for i in required_inputs(spec, path_, op):
        n = i["name"]
        row = {"name": n, "where": i["where"], "value": None, "source": "unresolved", "sure": "ask the developer"}
        if n in given:
            row.update(value=given[n], source="given by the developer", sure="given")
        elif (hit := from_saved(n, a.key)):
            row.update(value=hit[0], source=hit[1], sure="real data from an earlier call")
        elif env and calls < a.max_calls:
            for _score, cpath, cop in candidates(spec, n, path_):
                if calls >= a.max_calls:
                    break
                q = [f"{p['name']}={PAGE_PARAMS[p['name'].lower()]}" for p in param_list(spec, cpath, cop) if p["name"].lower() in PAGE_PARAMS]
                try:
                    res = nd_call.call(env, "GET", cpath, q, key=a.key)
                    calls += 1
                except SystemExit as ex:
                    row["source"] = f"live discovery failed: {nd_call.redact_text(str(ex.code))}"
                    break
                if res["status"] < 300 and res["json"] is not None:
                    nd_call.save(a.key, "GET", cpath, res)
                    v = find_key(res["json"], n)
                    if v is not None:
                        row.update(value=v, source=f"GET {cpath} on the gateway (live, page size 3 at most)", sure="proven live")
                        break
                else:
                    row["source"] = f"GET {cpath} returned HTTP {res['status']}"
        if row["value"] is None and (ex_ := spec_example(i)) is not None:
            row.update(value=ex_, source="spec example", sure="NOT proven: replace with a real value")
        rows.append(row)
    shown = [dict(r, value=nd_call.redact_text(str(r["value"])) if r["value"] is not None else None) for r in rows]
    sets = " ".join(f'--set {r["name"]}={r["value"]}' for r in shown if r["value"] is not None and r["where"] in ("path", "query"))
    cmd = f'python nd_query_spec.py curl {a.spec} "{path_}" {sets}'.strip()
    if a.json:
        print(json.dumps({"operation": f"{verb_.upper()} {path_}", "inputs": shown, "calls_used": calls, "curl_command": cmd}, indent=1))
        return 0
    print(f"{verb_.upper()} {path_}: {len(rows)} required input(s), {calls} read-only call(s) made")
    for r in shown:
        print(f"  {r['name']:<24} {str(r['value']):<30} {r['sure']:<40} {r['source']}")
    unresolved = [r["name"] for r in shown if r["value"] is None]
    if unresolved:
        print("unresolved (ask the developer):", ", ".join(unresolved))
    print("curl:", cmd)
    return 0


if __name__ == "__main__":
    sys.exit(main())
