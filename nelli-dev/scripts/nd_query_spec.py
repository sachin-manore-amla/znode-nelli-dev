#!/usr/bin/env python3
"""Query the Znode Stoplight OpenAPI specs without loading them into context,
and turn any operation into a ready-to-run curl command.

The specs range from 50 KB to 12.3 MB, so they cannot be read whole. This tool
answers the questions you actually need answered: which operations exist, what
one operation looks like, which schema defines a property, which Admin /
Knowledgebase URLs are already documented for a concept - and what the request
for an operation looks like as a curl command.

Specs are found by scanning the workspace for Stoplight.json files (skipping
node_modules, bin, obj and the like), so a spec added to any repo is picked up
without editing this file. A service's own repo wins; the snapshot copies under
test-automation snapshot copies are used only for services that have no spec of their own.

Usage
  python query_spec.py specs [--all]
  python query_spec.py stats  multifront
  python query_spec.py tags   multifront
  python query_spec.py paths  multifront --tag Account
  python query_spec.py paths  cp --grep "place-order"
  python query_spec.py paths  all --grep "tax-gateway"          # every spec at once
  python query_spec.py op     multifront /Account/GetAccount/{accountId}
  python query_spec.py curl   tax /taxmanager/v1/tax-gateway/calculate --base https://<gateway>
  python query_spec.py curl   payment "/v1/transaction/{pluginIdentifier}/{transactionId}" --set pluginIdentifier=<id> --set transactionId=<id>
  python query_spec.py schema multifront --grep ErrorDetail
  python query_spec.py prop   multifront AccountCode
  python query_spec.py urls   multifront --grep account

`prop` and `urls` implement the "existing spec is the source of truth" lookup
required by the documentation rules - use them before writing any description.

`curl` never reads or prints a secret: the Authorization header is built from
the user's ZNODE_API_BASIC / ZNODE_API_TOKEN environment variables at run time.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import quote, urlsplit

# Specs live under <workspace>/nd-knowledge/specs/<family>.json (exported from the API documentation), or in any Stoplight.json in the workspace.
ROOT = Path(__import__('nd_ws').workspace())
SPEC_DIR = "nd-knowledge/specs/"

# Folders never searched for specs.
PRUNE = {
    "node_modules", "bin", "obj", ".git", ".nx", ".next", "dist", ".vs", ".idea",
    "__pycache__", ".venv", "venv", "testresults", ".playwright-mcp", ".claude", ".copilot",
}
# Stable keys for the specs the skills and agents already refer to.
KNOWN: dict[str, str] = {}
# Folder-name fragments -> key, for any other spec (checked from the spec's own folder upwards).
SERVICE_HINTS = (
    ("commerce", "commerce"), ("core-v2", "core-v2"), ("corev2", "core-v2"), ("core", "core-v2"),
    ("custom-table", "custom-table"), ("customtable", "custom-table"), ("dynamic-data", "custom-table"),
    ("payment", "payment"), ("report", "reports"), ("erp", "erp"), ("tax", "tax"), ("shipping", "shipping"),
    ("legacy", "core-v1-legacy"), ("v1", "core-v1-legacy"),
)
COPY_REPOS: set[str] = set()  # snapshot copies used by the Swagger contract tests
ALIASES = {"v2": "core-v2", "core": "core-v2", "v1": "core-v1-legacy", "table": "custom-table", "report": "reports"}
VERBS = ("get", "post", "put", "patch", "delete", "head", "options")
MONEY = re.compile(r"authori[sz]e|capture|refund|void|purchase|charge|credit(?![- ]card)", re.I)
CARD = re.compile(r"credit[- ]card|bank[- ]account|payment[- ]method|/vault|plugin/\{[^}]+\}/store\b", re.I)
PLACEHOLDER = re.compile(r"<[^<>\s][^<>]*>")


# --------------------------------------------------------------------------- #
# spec discovery and loading
# --------------------------------------------------------------------------- #
def _recorded_base() -> str | None:
    """The gateway URL the developer gave (nd-work/environment.json), when --base is omitted."""
    try:
        envs = json.loads((ROOT / "nd-work" / "environment.json").read_text(encoding="utf-8-sig")).get("environments", [])
        return envs[0]["gateway_url"] if len(envs) == 1 else None
    except (OSError, ValueError, KeyError, IndexError):
        return None


def _repo_short(repo: str) -> str:
    return re.sub(r"^znode(10)?-", "", repo.lower())


def _service_key(rel: str) -> str:
    folders = [part.lower() for part in rel.split("/")[:-1]]
    for folder in reversed(folders):
        for hint, key in SERVICE_HINTS:
            if hint in folder:
                return key
    parent = folders[-1] if folders else "spec"
    return _repo_short(folders[0]) if parent == "stoplight" and folders else parent


_DISCOVERED: dict[str, dict] | None = None


def discover() -> dict[str, dict]:
    """Map key -> spec entry, for every Stoplight.json in the workspace."""
    global _DISCOVERED
    if _DISCOVERED is not None:
        return _DISCOVERED
    entries = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d.lower() not in PRUNE]
        for name in filenames:
            path = Path(dirpath) / name
            rel = path.relative_to(ROOT).as_posix()
            in_specs = rel.lower().startswith(SPEC_DIR) and name.lower().endswith(".json")
            if name.lower() != "stoplight.json" and not in_specs:
                continue
            repo = rel.split("/", 1)[0]
            known = KNOWN.get(rel.lower()) or (Path(name).stem.lower() if in_specs else None)
            is_copy = repo.lower() in COPY_REPOS
            entries.append({
                "base": known or _service_key(rel), "path": path, "rel": rel, "repo": repo,
                "copy": is_copy, "rank": 0 if known else (2 if is_copy else 1),
            })
    pkg_specs = Path(__file__).resolve().parent.parent / "knowledge" / "specs"      # specs shipped with the plugin
    if pkg_specs.is_dir() and ROOT not in pkg_specs.parents:
        for path in sorted(pkg_specs.glob("*.json")):
            entries.append({"base": path.stem.lower(), "path": path, "rel": path.as_posix(), "repo": "nelli-dev-package",
                            "copy": True, "rank": 3})
    entries.sort(key=lambda e: (e["base"], e["rank"], e["rel"].lower()))
    specs: dict[str, dict] = {}
    for entry in entries:
        key = entry["base"]
        if key in specs:  # a duplicate or a copy: keep it reachable as key@repo
            key = f"{entry['base']}@{_repo_short(entry['repo'])}"
            n = 2
            while key in specs:
                key = f"{entry['base']}@{_repo_short(entry['repo'])}{n}"
                n += 1
        entry["primary"] = "@" not in key
        specs[key] = entry
    _DISCOVERED = specs
    return specs


def resolve(name: str) -> tuple[str, Path]:
    """Return (key, path) for a spec key, alias, or a path to any spec file."""
    direct = Path(name)
    if direct.suffix.lower() == ".json" and direct.is_file():
        return direct.name, direct.resolve()
    specs = discover()
    key = ALIASES.get(name.lower(), name.lower())
    if key not in specs:
        sys.exit(f"unknown spec {name!r}; choose from {', '.join(sorted(k for k in specs if specs[k]['primary']))}"
                 " (`specs --all` lists copies), or pass the path of a spec file")
    return key, specs[key]["path"]


def load(name: str) -> dict:
    # Znode spec files are UTF-8 *with BOM*; utf-8-sig is required.
    with resolve(name)[1].open(encoding="utf-8-sig") as fh:
        return json.load(fh)


def operations(spec: dict):
    """Yield (path, verb, operation) for every real operation."""
    for path, item in (spec.get("paths") or {}).items():
        if not isinstance(item, dict):
            continue
        for verb, op in item.items():
            if verb.lower() in VERBS and isinstance(op, dict):
                yield path, verb.lower(), op


def truncate(text: str, limit: int) -> str:
    text = " ".join(str(text).split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def pointer(spec: dict, ref: str):
    """Resolve a local JSON pointer such as #/components/schemas/Name."""
    if not ref.startswith("#/"):
        return {}
    node = spec
    for part in ref[2:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        node = node.get(part) if isinstance(node, dict) else None
        if node is None:
            return {}
    return node


# --------------------------------------------------------------------------- #
# commands
# --------------------------------------------------------------------------- #
def cmd_specs(args) -> None:
    specs = discover()
    print(f"{'key':<34} {'size':>8}  path")
    hidden = 0
    for key, entry in sorted(specs.items(), key=lambda kv: (not kv[1]["primary"], kv[0])):
        if not entry["primary"] and not args.all:
            hidden += 1
            continue
        size = f"{entry['path'].stat().st_size / 1048576:.1f} MB"
        note = "  (copy)" if entry["copy"] else ""
        print(f"{key:<34} {size:>8}  {entry['rel']}{note}")
    if hidden:
        print(f"\n{hidden} duplicate or copy spec(s) hidden; `specs --all` lists them")


def cmd_stats(args) -> None:
    spec = load(args.spec)
    ops = list(operations(spec))
    verbs: dict[str, int] = {}
    for _, verb, _ in ops:
        verbs[verb] = verbs.get(verb, 0) + 1
    info = spec.get("info", {})
    print(f"title       : {info.get('title')}")
    print(f"version     : {info.get('version')}  (openapi {spec.get('openapi')})")
    for server in spec.get("servers") or []:
        print(f"server      : {server.get('url')}  {server.get('description', '')}".rstrip())
    print(f"paths       : {len(spec.get('paths') or {})}")
    print(f"operations  : {len(ops)}  " + " ".join(f"{v}={n}" for v, n in sorted(verbs.items())))
    print(f"schemas     : {len((spec.get('components') or {}).get('schemas') or {})}")
    print(f"tags        : {len(spec.get('tags') or [])}")
    print(f"security    : {json.dumps(spec.get('security'))}")
    print(f"secSchemes  : {list(((spec.get('components') or {}).get('securitySchemes') or {}))}")


def cmd_tags(args) -> None:
    spec = load(args.spec)
    counts: dict[str, int] = {}
    for _, _, op in operations(spec):
        for tag in op.get("tags") or ["(untagged)"]:
            counts[tag] = counts.get(tag, 0) + 1
    if not counts:
        print("no tags in this spec")
        return
    for tag, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"{count:>5}  {tag}")


def cmd_paths(args) -> None:
    every = args.spec.lower() == "all"
    keys = [k for k, e in discover().items() if e["primary"]] if every else [args.spec]
    width = max(len(k) for k in keys) + 1 if every else 0
    pattern = re.compile(args.grep, re.I) if args.grep else None
    shown = 0
    for key in keys:
        spec = load(key)
        for path, verb, op in operations(spec):
            if args.tag and args.tag.lower() not in [t.lower() for t in op.get("tags") or []]:
                continue
            if args.verb and verb != args.verb.lower():
                continue
            haystack = f"{path} {op.get('summary', '')} {op.get('operationId', '')}"
            if pattern and not pattern.search(haystack):
                continue
            print(f"{key if every else '':<{width}}{verb.upper():<7} {path}")
            if op.get("summary"):
                print(f"{'':<{width}}        {truncate(op['summary'], 110)}")
            shown += 1
            if args.limit and shown >= args.limit:
                print(f"... stopped at --limit {args.limit}")
                return
    print(f"\n{shown} operation(s)")


def find_operations(spec: dict, wanted: str, verb: str | None):
    matches = [(p, v, o) for p, v, o in operations(spec)
               if (p == wanted or p.lower() == wanted.lower()) and (not verb or v == verb.lower())]
    if not matches:
        near = sorted({p for p, _, _ in operations(spec) if wanted.lower() in p.lower()})[:10]
        sys.exit("path not found" + (f"; did you mean:\n  " + "\n  ".join(near) if near else ""))
    return matches


def cmd_op(args) -> None:
    spec = load(args.spec)
    for path, verb, op in find_operations(spec, args.path, args.verb):
        print("=" * 78)
        print(f"{verb.upper()} {path}")
        print(f"operationId : {op.get('operationId')}")
        print(f"tags        : {', '.join(op.get('tags') or [])}")
        print(f"summary     : {op.get('summary')}")
        params = op.get("parameters") or []
        print(f"parameters  : {len(params)}")
        for prm in params:
            schema = prm.get("schema") or {}
            print(
                f"  - {prm.get('name')} ({prm.get('in')})"
                f"{' required' if prm.get('required') else ''}"
                f"  type={schema.get('type')}"
                f"  example={json.dumps(schema.get('example'))[:60] if 'example' in schema else '-'}"
            )
        body = op.get("requestBody")
        if body:
            print(f"requestBody : {list((body.get('content') or {}).keys())}")
        print(f"responses   : {', '.join((op.get('responses') or {}).keys())}")
        for code, resp in (op.get("responses") or {}).items():
            print(f"  {code}: {truncate(resp.get('description', ''), 90)}")
            content = resp.get("content") or {}
            for ctype, media in content.items():
                ref = (media.get("schema") or {}).get("$ref", "")
                print(f"       {ctype}  {ref.rsplit('/', 1)[-1] if ref else ''}"
                      f"  examples={'yes' if media.get('examples') or media.get('example') else 'NO'}")
        desc = op.get("description") or ""
        if desc and not args.no_description:
            print("-" * 78)
            print(desc if args.full else desc[: args.desc_chars])
            if not args.full and len(desc) > args.desc_chars:
                print(f"\n[... {len(desc) - args.desc_chars} more chars; use --full]")


# ----------------------------- curl builder -------------------------------- #
def sample(schema, spec: dict, name: str, depth: int, stack: frozenset, required_only: bool):
    """Build an example value for a schema: its examples first, then a typed skeleton."""
    if not isinstance(schema, dict):
        return None
    ref = schema.get("$ref")
    if ref:
        if ref in stack:
            return {}  # recursive model: stop here
        return sample(pointer(spec, ref), spec, name, depth, stack | {ref}, required_only)
    if "example" in schema:
        return copy.deepcopy(schema["example"])
    if isinstance(schema.get("examples"), list) and schema["examples"]:
        return copy.deepcopy(schema["examples"][0])
    if schema.get("allOf"):
        merged: dict = {}
        for part in schema["allOf"]:
            value = sample(part, spec, name, depth, stack, required_only)
            if isinstance(value, dict):
                merged.update(value)
        if schema.get("properties"):
            rest = {k: v for k, v in schema.items() if k != "allOf"}
            merged.update(sample(rest, spec, name, depth, stack, required_only) or {})
        return merged
    for combo in ("oneOf", "anyOf"):
        if schema.get(combo):
            return sample(schema[combo][0], spec, name, depth, stack, required_only)
    if schema.get("default") is not None:
        return copy.deepcopy(schema["default"])
    if schema.get("enum"):
        return schema["enum"][0]
    kind = schema.get("type")
    if isinstance(kind, list):
        kind = next((k for k in kind if k != "null"), None)
    if kind == "object" or "properties" in schema or "additionalProperties" in schema:
        if depth <= 0:
            return {}
        out: dict = {}
        required = set(schema.get("required") or [])
        for prop, sub in (schema.get("properties") or {}).items():
            if required_only and prop not in required:
                continue
            if isinstance(sub, dict) and sub.get("readOnly"):
                continue
            out[prop] = sample(sub, spec, prop, depth - 1, stack, required_only)
        extra = schema.get("additionalProperties")
        if not out and isinstance(extra, dict):
            out[f"<{name or 'key'}>"] = sample(extra, spec, name, depth - 1, stack, required_only)
        return out
    if kind == "array":
        if depth <= 0:
            return []
        return [sample(schema.get("items") or {}, spec, name, depth - 1, stack, required_only)]
    if kind in ("integer", "number"):
        return 0
    if kind == "boolean":
        return False
    if kind == "string":
        fmt = schema.get("format")
        return f"<{name or 'string'}{':' + fmt if fmt else ''}>"
    return None


def schema_names(schema, spec: dict, seen: set | None = None, names: dict | None = None) -> dict:
    """Every property name reachable from a schema: lower-case -> declared spelling."""
    names = {} if names is None else names
    seen = set() if seen is None else seen
    if not isinstance(schema, dict):
        return names
    ref = schema.get("$ref")
    if ref:
        if ref not in seen:
            seen.add(ref)
            schema_names(pointer(spec, ref), spec, seen, names)
        return names
    for prop, sub in (schema.get("properties") or {}).items():
        names.setdefault(prop.lower(), prop)
        schema_names(sub, spec, seen, names)
    for key in ("items", "additionalProperties"):
        if isinstance(schema.get(key), dict):
            schema_names(schema[key], spec, seen, names)
    for key in ("allOf", "oneOf", "anyOf"):
        for part in schema.get(key) or []:
            schema_names(part, spec, seen, names)
    return names


def parse_value(text: str):
    try:
        return json.loads(text)
    except ValueError:
        return text


def set_path(body, dotted: str, value, names: dict) -> list[str]:
    """Set Field.Child.0.Name in a JSON body, creating objects and lists as needed.

    New keys take the schema's spelling; returns the names the schema does not declare.
    """
    parts = dotted.split(".")
    unknown = [p for p in parts if not p.isdigit() and names and p.lower() not in names]
    node = body
    for i, part in enumerate(parts):
        last = i == len(parts) - 1
        if isinstance(node, list):
            if not part.isdigit():
                sys.exit(f"--set {dotted}: expected a list index at {part!r}")
            index = int(part)
            while len(node) <= index:
                node.append(copy.deepcopy(node[-1]) if node else {})
            if last:
                node[index] = value
                return unknown
            if not isinstance(node[index], (dict, list)):
                node[index] = [] if parts[i + 1].isdigit() else {}
            node = node[index]
        elif isinstance(node, dict):
            key = next((k for k in node if k.lower() == part.lower()), names.get(part.lower(), part))
            if last:
                node[key] = value
                return unknown
            if not isinstance(node.get(key), (dict, list)):
                node[key] = [] if parts[i + 1].isdigit() else {}
            node = node[key]
        else:
            sys.exit(f"--set {dotted}: {'.'.join(parts[:i])} is not an object")
    return unknown


def ps_literal(text: str) -> str:
    return "'" + text.replace("'", "''") + "'"


def sh_literal(text: str) -> str:
    return "'" + text.replace("'", "'\\''") + "'"


def cmd_curl(args) -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    key, spec_path = resolve(args.spec)
    spec = load(args.spec)
    matches = find_operations(spec, args.path, args.verb)
    if len(matches) > 1:
        sys.exit("several operations share this path; pick one with --verb "
                 + "/".join(v.upper() for _, v, _ in matches))
    path, verb, op = matches[0]
    item = (spec.get("paths") or {}).get(path) or {}

    pending: dict[str, str] = {}
    for pair in args.set or []:
        name, sep, value = pair.partition("=")
        if not sep:
            sys.exit(f"--set {pair!r}: use name=value")
        pending[name.strip()] = value

    def take(name: str):
        for candidate in list(pending):
            if candidate.lower() == name.lower():
                return pending.pop(candidate)
        return None

    params: dict[tuple[str, str], dict] = {}
    for prm in (item.get("parameters") or []) + (op.get("parameters") or []):
        if isinstance(prm, dict) and "$ref" in prm:
            prm = pointer(spec, prm["$ref"])
        if isinstance(prm, dict) and prm.get("name"):
            params[(prm.get("in"), prm["name"])] = prm

    used_examples: list[str] = []

    def default(prm: dict):
        """The spec's example for a parameter (recorded, since it is sample data), else a placeholder."""
        schema = prm.get("schema") or {}
        for source in (prm, schema):
            if "example" in source:
                value = source["example"]
                used_examples.append(f"{prm['name']} ({prm.get('in')})")
                return value if isinstance(value, str) else json.dumps(value)
        return f"<{prm['name']}>"

    # path
    url_path = path
    for (where, name), prm in params.items():
        if where == "path":
            value = take(name)
            url_path = url_path.replace("{" + name + "}", quote(value if value is not None else default(prm), safe="~<>"))
    # query
    query = []
    for (where, name), prm in params.items():
        if where == "query":
            value = take(name)
            if value is None and (prm.get("required") or args.all_params):
                value = default(prm)
            if value is not None:
                query.append(f"{quote(name, safe='')}={quote(value, safe='~,<>')}")
    # headers
    headers: list[tuple[str, str]] = []
    for (where, name), prm in params.items():
        if where == "header" and name.lower() not in ("authorization", "content-type"):
            value = take(name)
            if value is None and (prm.get("required") or args.all_params):
                value = default(prm)
            if value is not None:
                headers.append((name, value))
    for name in [n for n in pending if n.lower().startswith("znode-") or n.lower() in ("device-id", "user-agent")]:
        headers.append((name, pending.pop(name)))
    for raw in args.header or []:
        name, _, value = raw.partition(":")
        headers.append((name.strip(), value.strip()))

    # body
    notes: list[str] = []
    content = ((op.get("requestBody") or {}).get("content") or {})
    ctype = next((c for c in ("application/json", "application/json-patch+json", "text/json") if c in content),
                 next(iter(content), None))
    body_schema = ((content.get(ctype) or {}).get("schema") or {}) if ctype else {}
    names = schema_names(body_schema, spec)
    body = None
    if args.body_file:
        body = json.loads(Path(args.body_file).read_text(encoding="utf-8-sig"))
    elif ctype:
        media = content[ctype] or {}
        if media.get("example") is not None:
            body = copy.deepcopy(media["example"])
        elif isinstance(media.get("examples"), dict) and media["examples"]:
            first = next(iter(media["examples"].values())) or {}
            body = copy.deepcopy(first.get("value") if "value" in first else pointer(spec, first.get("$ref", "")).get("value"))
        if body is None:
            body = sample(body_schema, spec, "", args.depth, frozenset(), args.required_only)
            if args.required_only and body == {}:
                notes.append("the schema declares no required fields, so --required-only starts from an empty body")
    for name, value in list(pending.items()):
        if body is None:
            sys.exit(f"--set {name}: not a parameter of this operation, and it has no request body")
        unknown = set_path(body, name, parse_value(value), names)
        if unknown:
            notes.append(f"--set {name}: {', '.join(unknown)} is not in the request schema")
        pending.pop(name)

    # base URL: --base, else the operation's server, else the spec's
    servers = op.get("servers") or item.get("servers") or spec.get("servers") or [{}]
    spec_base = (servers[0] or {}).get("url") or "https://<host>"
    base = args.base or _recorded_base() or spec_base
    if args.base and urlsplit(args.base).path in ("", "/") and urlsplit(spec_base).path not in ("", "/"):
        base = args.base.rstrip("/") + urlsplit(spec_base).path  # keep a prefix such as /commerceapi/v1
    base_path = urlsplit(base).path.rstrip("/")
    first_segment = base_path.strip("/").split("/")[0] if base_path else ""
    if first_segment and url_path.lower().startswith("/" + first_segment.lower() + "/"):
        # the spec path already carries the full route (Eg /commerceapi/v1.1/carts/add-to-cart under a
        # /commerceapi/v1 server): use the path as is, or the URL would hold the prefix twice
        base = base.rstrip("/")[: len(base.rstrip("/")) - len(base_path)]
        notes.append(f"the path already starts with /{first_segment}/, so the server prefix {base_path} is not added")
    url = base.rstrip("/") + url_path + ("?" + "&".join(query) if query else "")

    # auth: from the operation's security requirement, never from a stored value
    schemes = (spec.get("components") or {}).get("securitySchemes") or {}
    requirement = op.get("security", spec.get("security")) or []
    scheme_name = next((n for req in requirement for n in req), None)
    scheme = schemes.get(scheme_name) if scheme_name else None
    mode = args.auth
    if not mode:
        text = f"{scheme_name or ''} {(scheme or {}).get('description') or ''}".lower()
        mode = "none" if not scheme else ("bearer" if "bearer" in text and "basic" not in text else "basic")
    variable = args.auth_var or {"basic": "ZNODE_API_BASIC", "bearer": "ZNODE_API_TOKEN"}.get(mode)

    body_text = json.dumps(body, indent=2) if body is not None and ctype and "json" in ctype else None
    form_fields = body if body is not None and ctype and not body_text and isinstance(body, dict) else None

    # header comments
    lines = [f"# {verb.upper()} {path}" + (f" - {op['summary'].strip()}" if op.get("summary") else ""),
             f"# spec {key}: {spec_path.relative_to(ROOT).as_posix() if ROOT in spec_path.parents else spec_path}"
             + (f"   operationId {op['operationId']}" if op.get("operationId") else "")]
    what = f"{path} {op.get('operationId', '')} {op.get('summary', '')}"
    if verb != "get":
        lines.append(f"# [WRITE] {verb.upper()} may change data - run only with approval")
    if verb != "get" and MONEY.search(what):
        lines.append("# [MONEY] moves money - never run it against a live gateway; the user runs it on a test gateway")
    if CARD.search(what) or {"cardnumber", "cardsecuritycode", "cvv", "routingnumber", "bankaccountnumber"} & set(names):
        lines.append("# [CARD] carries card or bank details - test values only, never real ones")
    if scheme:
        where = scheme.get("in", "header")
        lines.append(f"# auth: scheme '{scheme_name}' ({scheme.get('type')} in {where} '{scheme.get('name')}')"
                     f" -> {mode}" + (f" from the user's {variable} environment variable" if variable else ""))
        if where != "header":
            lines.append(f"# note: the spec declares this key in a {where}; the other Znode specs use the"
                         " Authorization header, so it is sent as a header here")
    if not args.base:
        lines.append(f"# base URL is the spec's server ({spec_base}); pass --base for the real environment")
    lines += [f"# note: {note}" for note in notes]
    if used_examples:
        lines.append(f"# sample data: the spec's example is used for {', '.join(used_examples)} - replace with real values")
    if body is not None and not args.body_file:
        lines.append("# sample data: the body starts from the spec's examples; only the --set fields are real")
    leftovers = sorted(set(PLACEHOLDER.findall(url + " " + " ".join(v for _, v in headers) + " " + (body_text or ""))))
    if leftovers:
        shown = ", ".join(leftovers[:12]) + (f" (+{len(leftovers) - 12} more)" if len(leftovers) > 12 else "")
        lines.append(f"# fill {len(leftovers)} placeholder(s): {shown}")

    if args.bash:
        if mode == "basic":
            lines.append(f'AUTH="Basic $(printf \'%s\' "${variable}" | base64 -w0)"')
        elif mode == "bearer":
            lines.append(f'AUTH="Bearer ${variable}"')
        cmd = [f"curl -sk -X {verb.upper()} {sh_literal(url)}"]
        if mode in ("basic", "bearer"):
            cmd.append('-H "Authorization: $AUTH"')
        cmd += [f"-H {sh_literal(f'{n}: {v}')}" for n, v in headers]
        if body_text is not None:
            lines += ["cat > /tmp/znode-curl-body.json <<'JSON'", body_text, "JSON"]
            cmd += [f"-H {sh_literal('Content-Type: ' + ctype)}", "--data-binary @/tmp/znode-curl-body.json"]
        elif form_fields:
            flag = "-F" if ctype.startswith("multipart/") else "--data-urlencode"
            cmd += [f"{flag} {sh_literal(f'{k}={v}')}" for k, v in form_fields.items()]
        lines.append(" ".join(cmd))
    else:
        if mode == "basic":
            lines.append(f"$basic = [Environment]::GetEnvironmentVariable('{variable}', 'User')")
            lines.append('$auth  = "Basic " + [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($basic))')
        elif mode == "bearer":
            lines.append(f"$auth  = \"Bearer \" + [Environment]::GetEnvironmentVariable('{variable}', 'User')")
        cmd = [f"curl.exe -sk -X {verb.upper()} {ps_literal(url)}"]
        if mode in ("basic", "bearer"):
            cmd.append('-H "Authorization: $auth"')
        cmd += [f"-H {ps_literal(f'{n}: {v}')}" for n, v in headers]
        if body_text is not None:
            lines += ['$f = "$env:TEMP\\znode-curl-body.json"', "[IO.File]::WriteAllText($f, @'", body_text, "'@)"]
            cmd += [f"-H {ps_literal('Content-Type: ' + ctype)}", '--data-binary "@$f"']
        elif form_fields:
            flag = "-F" if ctype.startswith("multipart/") else "--data-urlencode"
            cmd += [f"{flag} {ps_literal(f'{k}={v}')}" for k, v in form_fields.items()]
        lines.append(" ".join(cmd))
    print("\n".join(lines))


def cmd_schema(args) -> None:
    spec = load(args.spec)
    schemas = (spec.get("components") or {}).get("schemas") or {}
    if args.name:
        found = schemas.get(args.name)
        if found is None:
            cands = [k for k in schemas if args.name.lower() in k.lower()][:15]
            sys.exit("schema not found" + (f"; candidates:\n  " + "\n  ".join(cands) if cands else ""))
        print(json.dumps(found, indent=2)[: args.chars])
        return
    pattern = re.compile(args.grep, re.I) if args.grep else None
    hits = [k for k in sorted(schemas) if not pattern or pattern.search(k)]
    for key in hits[: args.limit]:
        props = (schemas[key].get("properties") or {})
        print(f"{key}  ({len(props)} properties)")
    print(f"\n{len(hits)} schema(s)" + (f", showing {min(len(hits), args.limit)}" if len(hits) > args.limit else ""))


def cmd_prop(args) -> None:
    """Find every schema carrying a property name - the doc-rules reuse lookup."""
    spec = load(args.spec)
    schemas = (spec.get("components") or {}).get("schemas") or {}
    target = args.property.lower()
    shown = 0
    for name in sorted(schemas):
        props = schemas[name].get("properties") or {}
        for prop_name, prop in props.items():
            if prop_name.lower() != target:
                continue
            if not isinstance(prop, dict):
                continue
            print("=" * 78)
            print(f"{name}.{prop_name}")
            print(f"  type={prop.get('type')} format={prop.get('format')} "
                  f"nullable={prop.get('nullable')} example={json.dumps(prop.get('example'))}")
            desc = prop.get("description")
            if desc:
                print("  ---")
                body = desc if args.full else desc[: args.chars]
                print("  " + body.replace("\n", "\n  "))
            shown += 1
            if args.limit and shown >= args.limit:
                print(f"\n... stopped at --limit {args.limit}")
                return
    print(f"\n{shown} schema(s) define {args.property!r}")
    if not shown:
        print("No existing documentation to reuse - write a fresh description and "
              "omit Admin URL / Knowledgebase sections rather than inventing them.")


def cmd_urls(args) -> None:
    """Extract already-documented Admin Sandbox and Knowledgebase URLs."""
    spec = load(args.spec)
    url_re = re.compile(
        r"https?://(?:support\.znode\.com|www\.znode\.com|apidocs\.znode\.com)[^\s)\"'\\]+"
    )
    pattern = re.compile(args.grep, re.I) if args.grep else None
    found: dict[str, int] = {}

    def scan(text: str) -> None:
        text = text or ""
        if pattern and not pattern.search(text):
            return  # --grep matches the URL or its surrounding description
        for url in url_re.findall(text):
            found[url] = found.get(url, 0) + 1

    for _, _, op in operations(spec):
        scan(op.get("description", ""))
        for prm in op.get("parameters") or []:
            scan(prm.get("description", ""))
    for schema in ((spec.get("components") or {}).get("schemas") or {}).values():
        scan(schema.get("description", ""))
        for prop in (schema.get("properties") or {}).values():
            if isinstance(prop, dict):
                scan(prop.get("description", ""))

    for url, count in sorted(found.items(), key=lambda kv: (-kv[1], kv[0]))[: args.limit]:
        print(f"{count:>4}x  {url}")
    print(f"\n{len(found)} distinct URL(s). Reuse these verbatim - never fabricate new ones.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("specs", help="list the spec files found in the workspace")
    p.add_argument("--all", action="store_true", help="include duplicates and snapshot copies")
    p.set_defaults(func=cmd_specs)

    p = sub.add_parser("stats", help="counts and metadata for one spec")
    p.add_argument("spec"); p.set_defaults(func=cmd_stats)

    p = sub.add_parser("tags", help="tags with operation counts")
    p.add_argument("spec"); p.set_defaults(func=cmd_tags)

    p = sub.add_parser("paths", help="list operations (spec 'all' searches every spec)")
    p.add_argument("spec")
    p.add_argument("--tag"); p.add_argument("--verb"); p.add_argument("--grep")
    p.add_argument("--limit", type=int, default=100)
    p.set_defaults(func=cmd_paths)

    p = sub.add_parser("op", help="dump one operation")
    p.add_argument("spec"); p.add_argument("path")
    p.add_argument("--verb")
    p.add_argument("--full", action="store_true", help="print the whole description")
    p.add_argument("--desc-chars", type=int, default=2000)
    p.add_argument("--no-description", action="store_true")
    p.set_defaults(func=cmd_op)

    p = sub.add_parser("curl", help="build a ready-to-run curl command for one operation")
    p.add_argument("spec"); p.add_argument("path")
    p.add_argument("--verb", help="needed when several verbs share the path")
    p.add_argument("--base", help="environment base URL (default: the gateway recorded with nd_env.py, else the spec's server)")
    p.add_argument("--set", action="append", metavar="NAME=VALUE",
                   help="fill a path, query or header parameter, or a body field (dotted: Address.City, Items.0.SKU)")
    p.add_argument("--header", action="append", metavar="'NAME: VALUE'", help="add another header")
    p.add_argument("--body-file", help="start from this JSON body (e.g. one captured in the network log)")
    p.add_argument("--required-only", action="store_true", help="skeleton body with required fields only")
    p.add_argument("--depth", type=int, default=4, help="how deep to expand nested models (default 4)")
    p.add_argument("--all-params", action="store_true", help="include optional query and header parameters")
    p.add_argument("--auth", choices=("basic", "bearer", "none"), help="override the auth mode taken from the spec")
    p.add_argument("--auth-var", help="environment variable holding the credential (default ZNODE_API_BASIC / ZNODE_API_TOKEN)")
    p.add_argument("--bash", action="store_true", help="bash instead of PowerShell")
    p.set_defaults(func=cmd_curl)

    p = sub.add_parser("schema", help="find or dump a schema")
    p.add_argument("spec"); p.add_argument("name", nargs="?")
    p.add_argument("--grep"); p.add_argument("--limit", type=int, default=40)
    p.add_argument("--chars", type=int, default=4000)
    p.set_defaults(func=cmd_schema)

    p = sub.add_parser("prop", help="find schemas defining a property (doc reuse lookup)")
    p.add_argument("spec"); p.add_argument("property")
    p.add_argument("--limit", type=int, default=5)
    p.add_argument("--chars", type=int, default=800)
    p.add_argument("--full", action="store_true")
    p.set_defaults(func=cmd_prop)

    p = sub.add_parser("urls", help="list documented Admin / Knowledgebase URLs")
    p.add_argument("spec"); p.add_argument("--grep")
    p.add_argument("--limit", type=int, default=60)
    p.set_defaults(func=cmd_urls)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
