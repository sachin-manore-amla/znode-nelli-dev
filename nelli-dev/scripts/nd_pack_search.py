#!/usr/bin/env python3
"""Search the product-knowledge pack (customer-safe functional documents). This is the FIRST source Nelli-Dev consults.

Usage
  python nd_pack_search.py find "<keywords>" [--module accounts|custom-table|...] [--top 6]
  python nd_pack_search.py list                      modules and document counts, build date and source commit
  python nd_pack_search.py show <pack path>          print one document (path as shown by find)

find ranks documents by keyword hits in the title and path (heavy) and the body, and prints the best matching lines.
Read the top documents in full before relying on them. A pack document is product knowledge, not proof: where it
disagrees with the API reference or the code, say so and follow the precedence in the agent definition.

Pack folder: NELLIDEV_PACK, else <workspace>/nd-knowledge/pack, else the package's knowledge/pack.
"""
import argparse, json, os, re, sys
from pathlib import Path

STOP = {"the", "a", "an", "of", "to", "in", "for", "and", "or", "on", "how", "do", "i", "we", "can", "is", "it", "with", "my", "our", "what", "does"}


def pack_dir():
    cands = [os.environ.get("NELLIDEV_PACK")]
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import nd_ws
        cands.append(str(Path(nd_ws.workspace()) / "nd-knowledge" / "pack"))
    except Exception:
        pass
    cands.append(str(Path(__file__).resolve().parent.parent / "knowledge" / "pack"))
    for c in cands:
        if c and (Path(c) / "index.json").is_file():
            return Path(c)
    sys.exit("Knowledge pack not found (set NELLIDEV_PACK, or install the package). Say 'knowledge pack not available' in the answer and continue with the API reference and the KB.")


def terms(q):
    return [t for t in re.findall(r"[a-z0-9][a-z0-9-]+", q.lower()) if t not in STOP]


def find(q, module, top):
    d = pack_dir()
    idx = json.loads((d / "index.json").read_text(encoding="utf-8"))
    ts = terms(q)
    if not ts:
        sys.exit("give at least one keyword")
    scored = []
    for e in idx:
        if module and e["module"] != module:
            continue
        text = (d / e["path"]).read_text(encoding="utf-8", errors="replace")
        low = text.lower()
        head = (e["title"] + " " + e["path"]).lower()
        s = 0
        for t in ts:
            s += 6 * head.count(t) + min(low.count(t), 12)
        hit_terms = sum(1 for t in ts if t in low or t in head)
        if hit_terms == 0:
            continue
        s += 10 * hit_terms
        scored.append((s, e, text))
    scored.sort(key=lambda x: -x[0])
    if not scored:
        print("no document in the knowledge pack matches: say so in the answer, then use the API reference and the KB.")
        return
    for s, e, text in scored[:top]:
        print(f"{s:4}  {e['path']}  [{e['kind']}]  {e['title']}")
        shown = 0
        for line in text.splitlines():
            if any(t in line.lower() for t in ts) and line.strip() and not line.startswith("#"):
                print("        " + line.strip()[:170])
                shown += 1
                if shown == 2:
                    break


def lst():
    d = pack_dir()
    idx = json.loads((d / "index.json").read_text(encoding="utf-8"))
    prov = json.loads((d / "PROVENANCE.json").read_text(encoding="utf-8")) if (d / "PROVENANCE.json").exists() else {}
    by = {}
    for e in idx:
        by[e["module"]] = by.get(e["module"], 0) + 1
    print(f"pack {d} built {prov.get('built', '?')} from source commit {prov.get('source_commit', '?')}")
    for m, n in sorted(by.items()):
        print(f"  {m:14} {n} document(s)")
    q = prov.get("quarantined", [])
    if q:
        print(f"  {len(q)} document(s) withheld for review")


def show(path):
    d = pack_dir()
    f = (d / path).resolve()
    if d.resolve() not in f.parents or not f.is_file():
        sys.exit("not a pack document")
    sys.stdout.write(f.read_text(encoding="utf-8", errors="replace"))


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("find"); f.add_argument("query"); f.add_argument("--module"); f.add_argument("--top", type=int, default=6)
    sub.add_parser("list")
    s = sub.add_parser("show"); s.add_argument("path")
    a = ap.parse_args()
    if a.cmd == "find":
        find(a.query, a.module, a.top)
    elif a.cmd == "list":
        lst()
    else:
        show(a.path)


if __name__ == "__main__":
    main()
