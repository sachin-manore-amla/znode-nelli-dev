#!/usr/bin/env python3
"""Nelli-Dev guard: a PreToolUse hook that enforces the workspace, approval and secret rules outside the model.

Claude Code runs this before every Read, Write, Edit, NotebookEdit and Bash call made by the
nelli-dev agent. It reads the call as JSON on stdin and answers with a permission decision
(deny, ask or nothing = allow). It is the host-side half of the guardrails in the design
document (G1, G3, G4, G5, G10); the agent's prompt is the other half.

Rules
  0. Other repositories: a folder with its own .git inside the workspace is readable only when recorded as a project; Grep/Glob must name a path.
  1. Files: only inside the workspace (NELLIDEV_WORKSPACE, else CLAUDE_PROJECT_DIR, else the hook's cwd). Anything else is denied.
  2. Secrets: .env*, *.pfx, *.pem, *.key, id_rsa*, secrets.* are never read or written. appsettings*.json
     asks first (it holds connection strings; read key names only, never print values).
  3. Approval gate: before <workspace>/nd-work/<request>/approval.json says "approved": true, writes are
     allowed only under nd-work/ and nd-knowledge/. After approval they may go anywhere in the
     workspace (limited to approval.json "scope" globs when that list is present).
  4. approval.json itself: every write to it asks the person, so the approval cannot come from the model alone.
  5. The guard, the agent and its skills (.claude/, nelli-dev/) are read-only.
  6. HTTP and web reads: curl/wget/Invoke-WebRequest, WebFetch and browser navigation only to the gateway hosts recorded in nd-work/environment.json (nd_env.py) and the public Znode docs sites.
  7. Bash and PowerShell: denies git push/reset --hard/clean, recursive deletes, reading env files, dumping the environment,
     printing the credential variables; asks before any HTTP call that is not GET/HEAD, before package installs and deploys.
  8. Writes through the shell: every file the command visibly writes (redirections > >> &>, tee, Out-File, Set-Content, Add-Content,
     New-Item, Copy-Item, Move-Item, cp, mv, mkdir, rm, curl -o, iwr -OutFile, Expand-Archive, git clone, dotnet -o and similar,
     also inside cmd /c, powershell -Command and bash -c strings, after a cd) goes through the same file rules as the Write tool:
     outside the workspace, the recorded projects and the scratch area <temp>/nelli-dev is denied; inside it needs the approved plan
     (or nd-work/, nd-knowledge/). A target the guard cannot resolve (variables, subshells) or code that writes files from an
     interpreter one-liner asks the developer.

Usage (as a hook; see agents/nelli-dev.md)  python nd_guard.py            # JSON on stdin
Self test                                   python nd_guard.py --selftest
Exit code is 0 always; the decision is in the JSON written to stdout. A crash fails closed (deny).
"""
from __future__ import annotations

import fnmatch
import json
import os
import re
import sys
import tempfile
from pathlib import Path

SECRET_FILES = ("*.pfx", "*.pem", "*.key", "id_rsa*", "id_ed25519*", "secrets.*", "*.keystore", "*.p12")
SECRET_ENV = re.compile(r"(^|[\\/])(\.env(\.[^\\/]*)?|[^\\/]*\.env)$", re.I)
ASK_FILES = ("appsettings*.json", "local.settings.json", "web.config")
PROTECTED_DIRS = (".claude", "nelli-dev", ".git", "node_modules")
FREE_WRITE_DIRS = ("nd-work", "nd-knowledge")
# The plugin folder (skills, scripts, registry, pack): readable by the agent, never writable. Claude Code sets CLAUDE_PLUGIN_ROOT for hooks.
PLUGIN_ROOT = os.path.normcase(os.path.realpath(os.environ.get("CLAUDE_PLUGIN_ROOT") or str(Path(__file__).resolve().parent.parent)))
# Scratch area outside the workspace that the agent may write (and read): <system temp>/nelli-dev. Nothing else outside the workspace.
TEMP_AREA = os.path.normcase(os.path.realpath(os.path.join(tempfile.gettempdir(), "nelli-dev")))
AGENT_TYPE = ""     # set per call from the hook payload (agent_type)
AGENT_PREFIX = "nelli-dev"      # the guard applies to the plugin's own agents: agent_type "nelli-dev:<agent>" (or "nelli-dev")


def decision(kind: str, reason: str) -> None:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse", "permissionDecision": kind, "permissionDecisionReason": f"Nelli-Dev guard: {reason}"}}))
    sys.exit(0)


def norm(p: str | Path) -> str:
    return os.path.normcase(os.path.realpath(str(p)))


def workspace(cwd: str | None) -> str:
    # explicit setting first, then the project root Claude Code gives hooks, and only then the (movable) current folder
    here = Path(__file__).resolve()
    installed = str(here.parents[3]) if len(here.parents) > 3 and here.parent.name == "nd" and here.parents[2].name == ".claude" else None
    return norm(os.environ.get("NELLIDEV_WORKSPACE") or os.environ.get("CLAUDE_PROJECT_DIR") or installed or cwd or os.getcwd())


def inside(path: str, root: str) -> bool:
    try:
        return os.path.commonpath([path, root]) == root
    except ValueError:  # different drives
        return False


def rel(path: str, root: str) -> str:
    return os.path.relpath(path, root).replace("\\", "/")


def _config():
    """The central configuration module (nd_config.py, same folder); None if it cannot be loaded."""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import nd_config
        return nd_config
    except Exception:
        return None


def project_roots(root: str):
    """Folders the developer confirmed as their projects (central config, then an old nd-work/zc-work file): [(name, normalized path)]."""
    cfg = _config()
    try:
        projects = cfg.projects(root) if cfg else []
    except Exception:
        projects = []
    return [(p["name"], norm(p["path"])) for p in projects if p.get("path")]


ALWAYS_OK_HOSTS = ("support.znode.com", "www.znode.com", "apidocs.znode.com", "localhost", "127.0.0.1")


def allowed_hosts(root: str) -> set:
    """Hosts the agent may call: the developer's recorded gateway(s) plus the public Znode documentation sites."""
    hosts = set(ALWAYS_OK_HOSTS)
    cfg = _config()
    try:
        for e in (cfg.environments(root) if cfg else []):
            hosts.add(e["host"].lower().split(":")[0])
    except Exception:
        pass
    return hosts


def other_repo(full: str, root: str) -> str | None:
    """If the path sits inside a git repository (below the workspace root) that is not a recorded project, return its folder."""
    recorded = [pr for _, pr in project_roots(root)]
    cur = Path(full)
    root_p = Path(root)
    for parent in [cur] + list(cur.parents):
        if os.path.normcase(str(parent)) == os.path.normcase(str(root_p)) or len(parent.parts) <= len(root_p.parts):
            return None
        if (parent / ".git").exists():
            n = norm(parent)
            return None if any(inside(n, pr) or n == pr for pr in recorded) else str(parent)
    return None


def approval(root: str):
    """Return (approved, scope) from the newest approval.json, or (False, None)."""
    work = Path(root) / "nd-work"
    files = sorted(work.glob("*/approval.json"), key=lambda f: f.stat().st_mtime, reverse=True) if work.exists() else []
    for f in files[:1]:
        try:
            data = json.loads(f.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError):
            return False, None
        if data.get("approved") is not True:
            return False, None
        import hashlib
        for name, h in (data.get("plan_sha256") or {}).items():
            plan = f.parent / name
            if not plan.exists() or hashlib.sha256(plan.read_bytes()).hexdigest() != h:
                return False, None  # plan changed after approval: approve again
        return True, data.get("scope")
    return False, None


def in_scope(full: str, r: str, scope) -> bool:
    """True when the path matches any approved scope glob (relative, '<project>/<path>', or absolute; case-insensitive)."""
    abs_n = full.replace("\\", "/").lower()
    rel_n = r.replace("\\", "/").lower()
    for g in scope:
        gn = g.replace("\\", "/").lower()
        absolute = bool(re.match(r"^[a-z]:/", gn)) or gn.startswith("/")
        target = abs_n if absolute else rel_n
        base = gn.rstrip("*").rstrip("/")
        if fnmatch.fnmatchcase(target, gn) or target == base or target.startswith(base + "/") or (gn.endswith("*") and target.startswith(gn.rstrip("*"))):
            return True
    return False


def check_file(tool: str, path: str, root: str, writing: bool) -> None:
    path = os.path.expanduser(os.path.expandvars(path))
    full = norm(path if os.path.isabs(path) else os.path.join(root, path))
    name = os.path.basename(full)
    if name.lower() == ".nd-guard-probe.env":
        decision("deny", "GUARD ACTIVE: this refusal is the startup probe working as intended. Continue with the run.")
    if ".nelli-dev" in full.lower().replace("\\", "/").split("/"):
        decision("deny", "the central Nelli-Dev configuration and credential references are read and changed only through the nd_* scripts, never as files.")
    if SECRET_ENV.search(full) or any(fnmatch.fnmatch(name.lower(), g) for g in SECRET_FILES):
        decision("deny", f"{name} is a secret file. Secrets are never read or written by the agent.")
    if inside(full, PLUGIN_ROOT):
        if writing:
            decision("deny", "the Nelli-Dev plugin folder (agents, skills, scripts, registry, knowledge) is read-only for the agent.")
        return
    if inside(full, TEMP_AREA) and not inside(full, root):
        return      # the scratch area: temporary files only, never code or configuration
    proj = next(((n, pr) for n, pr in project_roots(root) if inside(full, pr)), None)
    if not inside(full, root) and not proj:
        decision("deny", f"{full} is outside the authorized workspace {root}, the recorded project folders and the scratch area {TEMP_AREA} "
                         "(ask the developer for the folder and record it with nd_projects.py).")
    if proj and not inside(full, root):
        r = proj[0] + "/" + rel(full, proj[1])        # scope globs for an outside project are written as "<name>/<path>"
        first = r.split("/")[1] if "/" in r else ""
    else:
        r = rel(full, root)
        first = r.split("/")[0]
    other = other_repo(full, root)
    if other and not proj:
        decision("deny", f"{other} is another repository that is not one of the developer's recorded projects. "
                         "Ask the developer for the folder and record it with nd_projects.py; do not read other repositories.")
    if name.lower() in ("approval.json", "projects.json", "environment.json") and writing:
        what = {"approval.json": "the developer's approval of the plan", "projects.json": "the project folders it may touch",
                "environment.json": "the host it may call"}[name.lower()]
        decision("ask", f"{name} widens what the agent may do ({what}). Confirm only if you agreed to it.")
    if any(fnmatch.fnmatch(name.lower(), g) for g in ASK_FILES):
        decision("ask", f"{name} can hold connection strings. The agent may read key names only and must not print values.")
    if not writing:
        return
    if AGENT_TYPE.endswith(":code-reviewer") and not (first in FREE_WRITE_DIRS and inside(full, root)):
        decision("deny", "the reviewer is read-only: its only writes are review reports under nd-work/.")
    if first in PROTECTED_DIRS and not (proj and not inside(full, root) and first not in (".git", "node_modules")):
        decision("deny", f"{first}/ is read-only for the agent (guard, agent definition, skills, dependencies).")
    if first in FREE_WRITE_DIRS and inside(full, root):
        return
    ok, scope = approval(root)
    if not ok:
        decision("deny", "no approved plan yet. Present the solution proposal and plan, get the developer's approval, "
                         "then record it (nd_approve.py). Only nd-work/ and nd-knowledge/ can be written before that.")
    if scope and not in_scope(full, r, scope):
        decision("deny", f"{r} is outside the approved scope {scope}. Ask the developer to extend the scope first.")


DENY_CMDS = [
    (r"\bgit\s+(?:-C\s+\S+\s+)?push\b", "pushing leaves the machine; the developer pushes."),
    (r"\bgit\s+(?:-C\s+\S+\s+)?(?:reset\s+--hard|clean\b|checkout\s+--\s|restore\s+\.)", "destructive git command."),
    (r"\brm\s+-[a-z]*r[a-z]*f|\brm\s+-[a-z]*f[a-z]*r|Remove-Item\b[^|;]*-Recurse|\brd\s+/s|\brmdir\s+/s|\bdel\s+/s", "recursive delete."),
    (r"(?:cat|type|more|less|head|tail|Get-Content|gc|Select-String|sls|grep|rg|sed|awk)\b[^|;&]*\.env(?:\.\w+)?\b", "reading an env file."),
    (r"(?:cat|type|Get-Content|gc)\b[^|;&]*\.(?:pfx|pem|key|p12)\b", "reading a key or certificate file."),
    (r"(?:^|[;&|]\s*)(?:printenv|env|set)\s*(?:$|[|;&])|Get-ChildItem\s+(?:env:|Env:)|\bgci\s+env:|\$env:\w*\s*\|", "dumping the environment."),
    (r"\b(?:Invoke-Expression|iex)\b|\bcurl\b[^|;]*\|\s*(?:sh|bash|pwsh|powershell)|\bwget\b[^|;]*\|\s*(?:sh|bash)", "piping downloads into a shell."),
    (r"\b(?:az|kubectl|helm|terraform)\s+(?:delete|destroy|apply)\b", "infrastructure change."),
    (r"\b(?:cmdkey|vaultcmd)\b|\bCredRead|Get-StoredCredential|\bnd_cred\.py\s+get\b|(?:python|py)\S*\s+(?:-\w+\s+)*-c\b[^|;&]*nd_cred", "reading the credential store. The token is used only inside the nd_* scripts."),
    (r"\bnd_setup_token\b", "the developer enters the credential in their own terminal (nd_setup_token.py). Ask them to run it; never run it or pass a credential yourself."),
    (r"\.nelli-dev\b", "the central configuration is read and changed only through the nd_* scripts."),
    (r"(?:echo|Write-Output|Write-Host|Write-Error|printf|print|Out-String|ConvertTo-Json|Set-Content|Add-Content|Out-File)\b[^|;&]*ZNODE_API_(?:BASIC|TOKEN)|GetEnvironmentVariable\([^)]*ZNODE_API|(?:^|[;&|(]\s*)\$env:ZNODE_API_(?:BASIC|TOKEN)\s*(?:$|[;|)])",
     "printing the credential variables. They are used only inside the nd_* scripts."),
    (r"\b(?:powershell|pwsh)(?:\.exe)?\b[^|;&]*\s-(?:e|ec|enc|encodedcommand)\s", "an encoded command cannot be inspected."),
]
ASK_CMDS = [
    (r"\bnd_call\.py\s+(?:POST|PUT|PATCH|DELETE)\b|--allow-write", "this call can change data on the gateway. Confirm only if the developer approved this exact call."),
    (r"(?:-X\s*|--request\s+)(?:POST|PUT|PATCH|DELETE)\b|--data\b|\s-d\s|Invoke-RestMethod\b[^|;]*-Method\s+(?:Post|Put|Patch|Delete)", "this HTTP call can change data."),
    (r"\b(?:npm|yarn|pnpm)\s+(?:install|i|add|publish)\b|\bdotnet\s+(?:add\s+package|nuget\s+push)\b|\bpip\s+install\b", "installing or publishing packages."),
    (r"\bdocker\s+(?:push|compose\s+up|run)\b|\bznode\s+deploy\b|\bdotnet\s+publish\b", "building or deploying a runtime."),
    (r"\bgit\s+(?:-C\s+\S+\s+)?(?:commit|merge|rebase|stash|tag)\b", "changes git history; commit only what the developer approved."),
]


REVIEWER_CMD = re.compile(
    r"(?:^|[;&|(\s])(?:rm|mv|cp|del|ren|rmdir|mkdir|touch|Remove-Item|Move-Item|Copy-Item|Rename-Item|New-Item|Set-Content|Add-Content|Out-File)(?![\w-])", re.I)
REVIEWER_SED = re.compile(r"\bsed\s+-\w*i", re.I)
REVIEWER_GIT = re.compile(r"\bgit\s+(?:-C\s+\S+\s+)?(?:apply|checkout|stash|merge|rebase|commit|add|reset|restore|clean)\b", re.I)
REVIEWER_REDIRECT = re.compile(r"(?<![\w=&<-])\d?>>?\s*(?!&|/dev/null|\$null|NUL\b)[^\s&]", re.I)


def reviewer_mutates(cmd: str) -> bool:
    return bool(REVIEWER_CMD.search(cmd) or REVIEWER_SED.search(cmd) or REVIEWER_GIT.search(cmd) or REVIEWER_REDIRECT.search(cmd))


# ---- writes through the shell -------------------------------------------------------------------------------------------
# A small quote-aware reader for the visible parts of a command line. It is a net, not a parser of every shell.
NULL_TARGETS = ("/dev/null", "/dev/stdout", "/dev/stderr", "nul", "$null", "nul:")
SHELLS = {"cmd": ("/c", "/k"), "powershell": ("-c", "-command"), "pwsh": ("-c", "-command"), "bash": ("-c",), "sh": ("-c",), "zsh": ("-c",), "wsl": ("-c",)}
CD_VERBS = ("cd", "chdir", "set-location", "sl", "pushd", "push-location")
# verb -> (positional mode, options whose value is a path, options that take a value that is not a path)
_PS_WRITE = ("first", {"path", "filepath", "literalpath"}, {"value", "encoding", "inputobject", "delimiter", "width", "stream"})
_PS_DELETE = ("all", {"path", "literalpath"}, {"include", "exclude", "filter", "itemtype", "value", "type", "name", "d", "t", "r"})
WRITE_VERBS = {
    "set-content": _PS_WRITE, "add-content": _PS_WRITE, "out-file": _PS_WRITE, "export-csv": _PS_WRITE, "export-clixml": _PS_WRITE,
    "tee-object": _PS_WRITE, "start-transcript": _PS_WRITE, "clear-content": _PS_DELETE, "tee": ("all", set(), set()),
    "new-item": _PS_DELETE, "ni": _PS_DELETE, "mkdir": _PS_DELETE, "md": _PS_DELETE, "touch": _PS_DELETE,
    "remove-item": _PS_DELETE, "ri": _PS_DELETE, "rm": _PS_DELETE, "del": _PS_DELETE, "erase": _PS_DELETE, "rd": _PS_DELETE, "rmdir": _PS_DELETE,
    "copy-item": ("last", {"destination"}, {"path", "literalpath", "filter", "include", "exclude"}),
    "cpi": ("last", {"destination"}, {"path", "literalpath", "filter", "include", "exclude"}),
    "cp": ("last", {"t", "target-directory", "destination"}, set()), "copy": ("last", {"destination"}, set()),
    "move-item": ("all", {"path", "literalpath", "destination"}, {"filter", "include", "exclude"}),
    "mi": ("all", {"path", "literalpath", "destination"}, set()), "mv": ("all", {"t", "target-directory", "destination"}, set()),
    "move": ("all", set(), set()), "ren": ("all", set(), set()), "rename-item": ("all", {"path", "literalpath"}, {"newname"}),
    "rni": ("all", {"path", "literalpath"}, {"newname"}),
    "robocopy": ("last", set(), set()), "xcopy": ("last", set(), set()), "ln": ("all", set(), set()), "mklink": ("all", set(), set()),
    "curl": ("none", {"o", "output", "output-dir", "dump-header", "cookie-jar", "trace", "trace-ascii", "stderr"}, set()),
    "wget": ("none", {"o", "output-document", "output-file", "p", "directory-prefix"}, set()),
    "invoke-webrequest": ("none", {"outfile"}, set()), "iwr": ("none", {"outfile"}, set()),
    "invoke-restmethod": ("none", {"outfile"}, set()), "irm": ("none", {"outfile"}, set()),
    "expand-archive": ("none", {"destinationpath"}, set()), "compress-archive": ("none", {"destinationpath"}, set()),
    "unzip": ("none", {"d"}, set()), "tar": ("none", {"c", "directory"}, set()), "dotnet": ("none", {"o", "output"}, set()),
    "truncate": ("all", set(), {"s", "size"}),
}
INPLACE_VERBS = ("sed", "perl", "gsed")
WRITE_CODE = re.compile(r"open\s*\([^)]*['\"][wax+]b?['\"]|write_text|write_bytes|shutil\.|os\.(?:remove|rename|replace|unlink|makedirs)|"
                        r"WriteAll(?:Text|Bytes|Lines)|\[\s*(?:System\.)?IO\.File\s*\]|File\.Write|writeFile|appendFile|fs\.(?:write|unlink|rm)", re.I)
INTERPRETERS = ("python", "python3", "py", "node", "perl", "ruby", "pwsh", "powershell")


def _read_words(cmd: str):
    """Split a command line into segments of ("w", word) and ("r", redirect target); quotes respected, operators only when unquoted."""
    first = cmd
    m = re.search(r"<<-?\s*['\"]?\w", cmd)
    if m:                                  # here-document: the body is data; only the first line is read
        nl = cmd.find("\n", m.end())
        first = cmd[:nl] if nl >= 0 else cmd
    segs, toks, buf = [], [], []
    have, quote, redir = False, None, False
    i, n = 0, len(first)

    def flush():
        nonlocal buf, have, redir
        if have:
            toks.append(("r" if redir else "w", "".join(buf)))
            redir = False
        buf, have = [], False

    def end():
        nonlocal toks
        flush()
        if toks:
            segs.append(toks)
        toks = []

    while i < n:
        c = first[i]
        if quote:
            if c == quote:
                quote = None
            else:
                buf.append(c)
        elif c in "'\"":
            quote, have = c, True
        elif c == "\n" or c == ";":
            end()
        elif c == ">":
            if buf and all(ch.isdigit() for ch in buf):
                buf, have = [], False       # 2> : the file descriptor number
            else:
                flush()
            if i + 1 < n and first[i + 1] == ">":
                i += 1
            if i + 1 < n and first[i + 1] == "&":        # 2>&1
                i += 1
                while i + 1 < n and (first[i + 1].isdigit() or first[i + 1] == "-"):
                    i += 1
            else:
                redir = True
        elif c == "&" and i + 1 < n and first[i + 1] == ">":
            pass                              # &> : the '>' is handled next
        elif c in "|&":
            end()
            while i + 1 < n and first[i + 1] in "|&":
                i += 1
        elif c.isspace():
            flush()
        else:
            buf.append(c)
            have = True
        i += 1
    end()
    return segs


def expand_path(raw: str, base: str | None):
    """Resolve a path written in a command: ~, $env:X, %X%, $X, git-bash /c/...; None when it cannot be known (subshell, unset variable)."""
    p = raw.strip().strip("\"'")
    if not p:
        return None
    p = re.sub(r"\$\{?env:(\w+)\}?", lambda m: os.environ.get(m.group(1), m.group(0)), p, flags=re.I)
    p = re.sub(r"%(\w+)%", lambda m: os.environ.get(m.group(1), m.group(0)), p)
    p = re.sub(r"\$\{?(\w+)\}?", lambda m: (os.path.expanduser("~") if m.group(1) == "HOME" else (base or "") if m.group(1) == "PWD"
                                            else os.environ.get(m.group(1), m.group(0))), p)
    if p.startswith("~"):
        p = os.path.expanduser(p)
    if re.search(r"[$`%]|\(", p):
        return None
    if os.name == "nt":
        m = re.match(r"^/([a-zA-Z])(?:/(.*))?$", p)
        if m:
            p = m.group(1).upper() + ":/" + (m.group(2) or "")
    if not os.path.isabs(p):
        if base is None:
            return None
        p = os.path.join(base, p)
    return norm(p)


def _targets_for(verb: str, args: list) -> list:
    if verb == "git":
        pos, skip = [], False
        for a in args:
            if skip:
                skip = False
            elif a in ("-C", "-c"):
                skip = True
            elif not a.startswith("-"):
                pos.append(a)
        if pos[:1] == ["clone"] and len(pos) >= 3:
            return [pos[-1]]
        if pos[:1] == ["init"] and len(pos) >= 2:
            return [pos[1]]
        if pos[:2] == ["worktree", "add"] and len(pos) >= 3:
            return [pos[2]]
        return []
    if verb == "dd":
        return [a[3:] for a in args if a.startswith("of=")]
    if verb in INPLACE_VERBS:
        if any(re.match(r"^-[a-z]*i", a) for a in args if a.startswith("-") and not a.startswith("--")):
            return [a for a in args if not a.startswith("-")]
        return []
    spec = WRITE_VERBS.get(verb)
    if not spec:
        return []
    mode, popts, vopts = spec
    out, pos, i = [], [], 0
    while i < len(args):
        a = args[i]
        if a.startswith("-") and len(a) > 1 and not a[1].isdigit():
            body = a.lstrip("-")
            name, sep, attached = body.partition("=" if a.startswith("--") else ":")
            key = name.lower()
            if key in popts:
                if sep:
                    out.append(attached)
                elif i + 1 < len(args):
                    out.append(args[i + 1])
                    i += 1
            elif key in vopts and not sep:
                i += 1
        elif verb in ("robocopy", "xcopy") and re.match(r"^/[A-Za-z?]+(:.*)?$", a):
            pass
        else:
            pos.append(a)
        i += 1
    if mode == "all":
        out += pos
    elif mode == "first" and not out:
        out += pos[:1]
    elif mode == "last" and not out:
        out += pos[-1:]
    return out


def shell_writes(cmd: str, base, depth: int = 0):
    """(targets, opaque): the (raw path, base folder) pairs a command visibly writes, and reasons the guard cannot tell."""
    targets, opaque = [], []
    if depth > 3:
        return targets, ["commands nested more than three levels"]
    for toks in _read_words(cmd):
        words = [t for k, t in toks if k == "w"]
        for k, t in toks:
            if k == "r" and t.strip().strip("\"'").lower() not in NULL_TARGETS:
                targets.append((t, base))
        if not words:
            continue
        verb = re.sub(r"\.(exe|cmd|bat|ps1)$", "", os.path.basename(words[0].replace("\\", "/")).lower())
        args = words[1:]
        if verb in CD_VERBS:
            dest = next((a for a in args if not a.startswith("-") and a.lower() != "/d"), None)
            if dest:
                newbase = expand_path(dest, base)
                if newbase is None:
                    opaque.append("a directory change the guard cannot resolve, so relative paths after it cannot be checked")
                base = newbase
            continue
        if verb in SHELLS:
            flags = SHELLS[verb]
            for j, a in enumerate(args):
                if a.lower() in flags and j + 1 < len(args):
                    inner = " ".join(args[j + 1:]) if verb == "cmd" else args[j + 1]
                    t2, o2 = shell_writes(inner, base, depth + 1)
                    targets += t2
                    opaque += o2
                    break
            continue
        if verb in INTERPRETERS:
            for j, a in enumerate(args):
                if a.lower() in ("-c", "-e", "-command", "-ec") and j + 1 < len(args) and WRITE_CODE.search(args[j + 1]):
                    opaque.append(f"{verb} code that writes files")
        for t in _targets_for(verb, args):
            if t.strip().strip("\"'").lower() in NULL_TARGETS or "://" in t or t in ("-", ""):
                continue
            targets.append((t, base))
    return targets, opaque


def check_shell_writes(cmd: str, root: str, cwd) -> None:
    base = norm(cwd) if cwd else root
    targets, opaque = shell_writes(cmd, base)
    if opaque:
        decision("ask", f"cannot verify where this command writes ({opaque[0]}). Confirm only if you expect it to write inside the workspace.")
    for raw, b in targets:
        t = expand_path(raw, b)
        if t is None:
            decision("ask", f"the write target '{raw}' cannot be resolved by the guard (variable, subshell or unknown folder). Confirm only if it is inside the workspace.")
        check_file("Bash", t, root, True)


def check_bash(cmd: str, root: str, cwd=None) -> None:
    if AGENT_TYPE.endswith(":code-reviewer") and reviewer_mutates(cmd) and "nd-work" not in cmd:
        decision("deny", "the reviewer is read-only: shell commands that create, change or delete files are refused (reports go under nd-work/).")
    for pat, why in DENY_CMDS:
        if re.search(pat, cmd, re.I):
            decision("deny", why)
    check_shell_writes(cmd, root, cwd)
    if re.search(r"approval\.json|nd_approve", cmd):
        decision("ask", "this command records the developer's approval. Confirm only if you approved the plan.")
    if re.search(r"environment\.json|nd_env\.py\s+(?:add|remove)", cmd):
        decision("ask", "this command records which gateway host the agent may call. Confirm only if the developer gave you that URL and said it is not production.")
    if re.search(r"(?<![\w-])(?:curl(?:\.exe)?|wget|Invoke-WebRequest|Invoke-RestMethod|iwr|irm)(?![\w-])", cmd, re.I):
        ok = allowed_hosts(root)
        for m in re.finditer(r"https?://([^/\s'\"?#:]+)", cmd, re.I):
            if m.group(1).lower() not in ok:
                decision("deny", f"{m.group(1)} is not a recorded gateway. Ask the developer for the gateway URL of their development "
                                 "environment and record it with nd_env.py; the agent calls recorded gateways and the public Znode docs only.")
    if re.search(r"nd_migrate\.py[^|;&]*--apply|nd_cred\.py\s+forget", cmd):
        decision("ask", "this command moves old Z-Custom data into the central configuration or deletes a stored credential. Confirm only if the developer asked for it.")
    if re.search(r"projects\.json|nd_projects\.py\s+(?:add|remove)", cmd):
        decision("ask", "this command records which project folders the agent may touch. Confirm only if the developer gave you that path.")
    for pat, why in ASK_CMDS:
        if re.search(pat, cmd, re.I):
            decision("ask", why)


def handle(payload: dict) -> None:
    global AGENT_TYPE
    AGENT_TYPE = payload.get("agent_type") or AGENT_TYPE
    tool = payload.get("tool_name", "")
    ti = payload.get("tool_input") or {}
    root = workspace(payload.get("cwd"))
    if tool in ("Read", "NotebookRead"):
        p = ti.get("file_path") or ti.get("notebook_path")
        if p:
            check_file(tool, p, root, False)
    elif tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        p = ti.get("file_path") or ti.get("notebook_path")
        if p:
            check_file(tool, p, root, True)
    elif tool in ("Bash", "PowerShell"):
        check_bash(ti.get("command", ""), root, payload.get("cwd"))
    elif tool in ("Grep", "Glob"):
        p = ti.get("path")
        if not p:
            decision("deny", f"{tool} needs an explicit path inside a recorded project, nd-work, nd-knowledge or .claude/skills: "
                             "a search with no path would sweep the whole workspace.")
        check_file(tool, p, root, False)
    elif tool == "WebFetch" or tool.endswith("__navigate") or tool.endswith("__preview_start"):
        url = ti.get("url") or ""
        m = re.match(r"(?:https?://)?([^/\s:?#]+)", url, re.I)
        if m and url.lower() not in ("back", "forward") and m.group(1).lower() not in allowed_hosts(root):
            decision("deny", f"{m.group(1)} is not an allowed host. The agent reads support.znode.com, apidocs.znode.com and the "
                             "developer's recorded gateway only (record the gateway with nd_env.py).")
    # Glob / Grep: read-only; env files are excluded by the secret scanner and agent rules.


def selftest() -> int:
    import tempfile
    ws = tempfile.mkdtemp(prefix="ndws_")
    os.environ["NELLIDEV_WORKSPACE"] = ws
    os.environ["NELLIDEV_HOME"] = tempfile.mkdtemp(prefix="ndhome_")     # never the developer's real central config
    os.makedirs(os.path.join(ws, "nd-work", "ND-001"))
    cases = [
        ("Write", {"file_path": os.path.join(ws, "src", "a.cs")}, "deny"),                       # before approval
        ("Write", {"file_path": os.path.join(ws, "nd-work", "ND-001", "plan.md")}, None),        # docs always ok
        ("Write", {"file_path": os.path.join(ws, "nd-work", "ND-001", "approval.json")}, "ask"),
        ("Read", {"file_path": os.path.join(ws, "apps", "webstore", ".env")}, "deny"),
        ("Read", {"file_path": os.path.join(ws, ".nd-guard-probe.env")}, "deny"),                 # the agent's startup probe
        ("Read", {"file_path": os.path.join(ws, "config", "prod.env")}, "deny"),
        ("Read", {"file_path": os.path.join(ws, "docs", "environment.md")}, None),
        ("Read", {"file_path": os.path.join(ws, "appsettings.json")}, "ask"),
        ("Read", {"file_path": os.path.join(os.path.dirname(ws), "other", "x.cs")}, "deny"),
        ("Bash", {"command": "git push origin main"}, "deny"),
        ("Bash", {"command": "cat apps/webstore/.env"}, "deny"),
        ("Bash", {"command": "curl.exe -X POST https://localhost/y -d '{}'"}, "ask"),
        ("Bash", {"command": "curl.exe -sk https://localhost/y"}, None),
        ("Bash", {"command": "dotnet build"}, None),
        ("Bash", {"command": "echo hi > C:/Windows/x.txt"}, "deny"),
        ("Bash", {"command": "Get-ChildItem Env:"}, "deny"),
    ]
    with open(os.path.join(ws, "nd-work", "ND-001", "approval.json"), "w", encoding="utf-8") as f:
        json.dump({"approved": False}, f)
    after = [
        (("Write", {"file_path": os.path.join(ws, "src", "a.cs")}), "deny"),
    ]
    import io, contextlib
    failed = 0

    def run(tool, ti):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            try:
                handle({"tool_name": tool, "tool_input": ti, "cwd": ws})
                out = None
            except SystemExit:
                s = buf.getvalue().strip()
                out = json.loads(s)["hookSpecificOutput"]["permissionDecision"] if s else None
        return out

    for tool, ti, want in cases:
        got = run(tool, ti)
        ok = got == want
        failed += not ok
        print(("ok  " if ok else "FAIL"), tool, str(ti)[:70], "->", got, "(want", f"{want})")
    for (tool, ti), want in after:
        got = run(tool, ti); ok = got == want; failed += not ok
        print(("ok  " if ok else "FAIL"), "approved=false", tool, "->", got)
    with open(os.path.join(ws, "nd-work", "ND-001", "approval.json"), "w", encoding="utf-8") as f:
        json.dump({"approved": True, "scope": ["src/*", "Custom.Api.Core/*"]}, f)
    plan_path = os.path.join(ws, "nd-work", "ND-001", "implementation-plan.md")
    open(plan_path, "w").write("plan v1")
    import hashlib
    with open(os.path.join(ws, "nd-work", "ND-001", "approval.json"), "w", encoding="utf-8") as f:
        json.dump({"approved": True, "scope": ["src/*", "Custom.Api.Core/*"],
                   "plan_sha256": {"implementation-plan.md": hashlib.sha256(b"plan v1").hexdigest()}}, f)
    for tool, ti, want in [("Write", {"file_path": os.path.join(ws, "src", "a.cs")}, None),
                           ("Write", {"file_path": os.path.join(ws, "other", "b.cs")}, "deny"),
                           ("Write", {"file_path": os.path.join(ws, ".claude", "agents", "z.md")}, "deny")]:
        got = run(tool, ti); ok = got == want; failed += not ok
        print(("ok  " if ok else "FAIL"), "approved+scope", tool, ti["file_path"][-30:], "->", got)
    open(plan_path, "w").write("plan v2 (changed after approval)")
    got = run("Write", {"file_path": os.path.join(ws, "src", "a.cs")}); ok = got == "deny"; failed += not ok
    print(("ok  " if ok else "FAIL"), "plan changed after approval: write ->", got)
    os.environ.pop("NELLIDEV_WORKSPACE")
    os.environ["CLAUDE_PROJECT_DIR"] = ws
    os.makedirs(os.path.join(ws, "elsewhere"), exist_ok=True)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        handle({"tool_name": "Read", "tool_input": {"file_path": os.path.join(ws, "nd-work", "ND-001", "plan.md")}, "cwd": os.path.join(ws, "elsewhere")})
    ok = buf.getvalue().strip() == ""
    failed += not ok
    print(("ok  " if ok else "FAIL"), "cwd moved, CLAUDE_PROJECT_DIR=workspace: read inside workspace -> allowed" if ok else "workspace not taken from CLAUDE_PROJECT_DIR")
    outside = tempfile.mkdtemp(prefix="ndproj_")
    os.makedirs(os.path.join(outside, "Custom.Api.Core"))
    os.environ["NELLIDEV_WORKSPACE"] = ws
    for tool, ti, want, label in [
        ("Read", {"file_path": os.path.join(outside, "Custom.Api.Core", "A.cs")}, "deny", "outside project not recorded: read"),
        ("Write", {"file_path": os.path.join(ws, "nd-work", "projects.json")}, "ask", "recording a project asks the developer")]:
        got = run(tool, ti); ok = got == want; failed += not ok
        print(("ok  " if ok else "FAIL"), label, "->", got)
    with open(os.path.join(ws, "nd-work", "projects.json"), "w", encoding="utf-8") as f:
        json.dump({"projects": [{"name": "sdk", "path": outside}]}, f)
    with open(os.path.join(ws, "nd-work", "ND-001", "approval.json"), "w", encoding="utf-8") as f:
        json.dump({"approved": True, "scope": ["sdk/Custom.Api.Core/*"]}, f)
    for tool, ti, want, label in [
        ("Read", {"file_path": os.path.join(outside, "Custom.Api.Core", "A.cs")}, None, "recorded project: read allowed"),
        ("Write", {"file_path": os.path.join(outside, "Custom.Api.Core", "A.cs")}, None, "recorded project: write in approved scope"),
        ("Write", {"file_path": os.path.join(outside, "Other", "B.cs")}, "deny", "recorded project: write outside approved scope"),
        ("Write", {"file_path": os.path.join(outside, ".git", "config")}, "deny", "recorded project: .git protected"),
        ("Read", {"file_path": os.path.join(outside, "apps", ".env")}, "deny", "recorded project: env file still secret")]:
        got = run(tool, ti); ok = got == want; failed += not ok
        print(("ok  " if ok else "FAIL"), label, "->", got)
    for cmd, want, label in [("curl.exe -sk https://gw.example.invalid/v1/x", "deny", "curl to an unrecorded host"),
                             ("curl.exe -s https://apidocs.znode.com/", None, "curl to the public docs"),
                             ("python nd_env.py add --name dev --gateway-url https://gw.example.invalid --non-production", "ask", "recording a gateway asks the developer")]:
        got = run("Bash", {"command": cmd}); ok = got == want; failed += not ok
        print(("ok  " if ok else "FAIL"), label, "->", got)
    with open(os.path.join(ws, "nd-work", "environment.json"), "w", encoding="utf-8") as f:
        json.dump({"environments": [{"name": "dev", "gateway_url": "https://gw.example.invalid", "host": "gw.example.invalid", "non_production": True}]}, f)
    for cmd, want, label in [("curl.exe -sk https://gw.example.invalid/v1/x", None, "curl to the recorded gateway (GET)"),
                             ("curl.exe -sk https://other.example.invalid/v1/x", "deny", "curl to another host after recording"),
                             ("curl.exe -sk -X DELETE https://gw.example.invalid/v1/x", "ask", "non-GET call to the recorded gateway still asks")]:
        got = run("Bash", {"command": cmd}); ok = got == want; failed += not ok
        print(("ok  " if ok else "FAIL"), label, "->", got)
    for tool, ti, want, label in [("WebFetch", {"url": "https://support.znode.com/support/solutions/articles/1"}, None, "WebFetch KB"),
                                  ("WebFetch", {"url": "https://example.com/x"}, "deny", "WebFetch other site"),
                                  ("mcp__Claude_Browser__navigate", {"url": "https://apidocs.znode.com/docs/commerce-api"}, None, "browser apidocs"),
                                  ("mcp__Claude_Browser__navigate", {"url": "https://evil.example.com"}, "deny", "browser other site"),
                                  ("mcp__Claude_Browser__navigate", {"url": "back"}, None, "browser back")]:
        got = run(tool, ti); ok = got == want; failed += not ok
        print(("ok  " if ok else "FAIL"), label, "->", got)
    ab = os.path.join(outside, "Custom.Api.Core", "B.cs")
    with open(os.path.join(ws, "nd-work", "ND-001", "approval.json"), "w", encoding="utf-8") as f:
        json.dump({"approved": True, "scope": [(norm(outside) + "/Custom.Api.Core/*").upper().replace("\\", "/")]}, f)
    for tool, ti, want, label in [("Write", {"file_path": ab}, None, "absolute upper-case scope glob matches"),
                                  ("Write", {"file_path": os.path.join(outside, "Elsewhere", "C.cs")}, "deny", "absolute scope glob still limits")]:
        got = run(tool, ti); ok = got == want; failed += not ok
        print(("ok  " if ok else "FAIL"), label, "->", got)
    other = os.path.join(ws, "otherrepo")
    os.makedirs(os.path.join(other, ".git"), exist_ok=True)
    os.makedirs(os.path.join(ws, "docs"), exist_ok=True)
    with open(os.path.join(ws, "nd-work", "projects.json"), "w", encoding="utf-8") as f:
        json.dump({"projects": [{"name": "sdk", "path": outside}]}, f)
    for tool, ti, want, label in [
        ("Read", {"file_path": os.path.join(other, "Secret.cs")}, "deny", "unrecorded repository inside the workspace: read"),
        ("Write", {"file_path": os.path.join(other, "x.cs")}, "deny", "unrecorded repository inside the workspace: write"),
        ("Read", {"file_path": os.path.join(ws, "docs", "fsd.md")}, None, "plain workspace folder (no repo): read"),
        ("Grep", {"pattern": "x"}, "deny", "Grep with no path"),
        ("Grep", {"pattern": "x", "path": other}, "deny", "Grep inside an unrecorded repository"),
        ("Glob", {"pattern": "**/*.cs", "path": outside}, None, "Glob inside a recorded project"),
        ("Grep", {"pattern": "x", "path": os.path.join(ws, "nd-work")}, None, "Grep in nd-work")]:
        got = run(tool, ti); ok = got == want; failed += not ok
        print(("ok  " if ok else "FAIL"), label, "->", got)
    home = os.environ["NELLIDEV_HOME"]
    skill_ref = os.path.join(PLUGIN_ROOT, "skills", "api-catalog", "SKILL.md")
    for tool, ti, want, label in [
        ("Read", {"file_path": skill_ref}, None, "plugin folder readable"),
        ("Grep", {"pattern": "x", "path": os.path.join(PLUGIN_ROOT, "skills")}, None, "plugin folder searchable"),
        ("Write", {"file_path": skill_ref}, "deny", "plugin folder not writable"),
        ("Read", {"file_path": os.path.join(PLUGIN_ROOT, "x", ".env")}, "deny", "env file in the plugin folder still secret")]:
        got = run(tool, ti); ok = got == want; failed += not ok
        print(("ok  " if ok else "FAIL"), label, "->", got)
    # the reviewer is read-only
    rv = lambda tool, ti: run(tool, dict(ti, **{}))  # noqa: E731
    global AGENT_TYPE
    AGENT_TYPE = "nelli-dev:code-reviewer"
    with open(os.path.join(ws, "nd-work", "ND-001", "approval.json"), "w", encoding="utf-8") as f:
        json.dump({"approved": True, "scope": ["*"]}, f)       # even with an approved plan the reviewer cannot write code
    for tool, ti, want, label in [
        ("Write", {"file_path": os.path.join(outside, "Custom.Api.Core", "A.cs")}, "deny", "reviewer cannot write project code (plan approved)"),
        ("Write", {"file_path": os.path.join(ws, "nd-work", "ND-001", "review-1.md")}, None, "reviewer may write its report under nd-work"),
        ("Bash", {"command": "git -C . diff --name-only origin/main"}, None, "reviewer may read a diff"),
        ("Bash", {"command": "python nd_review.py plan --project sdk --json 2>&1"}, None, "reviewer runs its plan script"),
        ("Bash", {"command": "sed -i s/a/b/ Custom.Api.Core/A.cs"}, "deny", "reviewer cannot edit through the shell"),
        ("Bash", {"command": "echo x > Custom.Api.Core/A.cs"}, "deny", "reviewer cannot redirect into a file"),
        ("Bash", {"command": "git checkout -- ."}, "deny", "reviewer cannot restore files")]:
        got = run(tool, ti); ok = got == want; failed += not ok
        print(("ok  " if ok else "FAIL"), label, "->", got)
    AGENT_TYPE = ""
    # the hook filter: only Nelli-Dev agents are guarded
    import subprocess
    def hook(payload, guard_all=False):
        env = dict(os.environ, NELLIDEV_GUARD_ALL="1" if guard_all else "0")
        r = subprocess.run([sys.executable, str(Path(__file__).resolve())], input=json.dumps(payload), capture_output=True, text=True, env=env)
        return "deny" if '"deny"' in r.stdout else ("ask" if '"ask"' in r.stdout else None)
    bad = {"tool_name": "Bash", "tool_input": {"command": "git push origin main"}, "cwd": ws}
    for payload, want, label in [(dict(bad, agent_type="nelli-dev:sdk-builder"), "deny", "hook: Nelli-Dev agent is guarded"),
                                 (dict(bad, agent_type="nelli-dev"), "deny", "hook: lead agent as main thread is guarded"),
                                 (dict(bad, agent_type="other:agent"), None, "hook: another agent is not restricted"),
                                 (dict(bad), None, "hook: main session without an agent is not restricted")]:
        got = hook(payload); ok = got == want; failed += not ok
        print(("ok  " if ok else "FAIL"), label, "->", got)
    for tool, ti, want, label in [
        ("Read", {"file_path": os.path.join(os.path.expanduser("~"), ".nelli-dev", "config.json")}, "deny", "central config read as a file"),
        ("Write", {"file_path": os.path.join(os.path.expanduser("~"), ".nelli-dev", "config.json")}, "deny", "central config written as a file"),
        ("Bash", {"command": "cat ~/.nelli-dev/config.json"}, "deny", "central config read through the shell"),
        ("Bash", {"command": "cmdkey /list"}, "deny", "credential store listing"),
        ("Bash", {"command": "python -c \"import nd_cred; print(nd_cred._read('credman:nelli-dev/dev'))\""}, "deny", "token read through inline python"),
        ("Bash", {"command": "python nd_setup_token.py --env dev"}, "deny", "agent running the token script"),
        ("Bash", {"command": "python nd_migrate.py --apply"}, "ask", "migration apply asks the developer"),
        ("Bash", {"command": "python nd_migrate.py"}, None, "migration dry run"),
        ("Bash", {"command": "python nd_config.py status --json"}, None, "config status"),
        ("Bash", {"command": "python nd_call.py GET /v1/stores --query pageSize=3 --key R1"}, None, "nd_call GET runs without a prompt"),
        ("Bash", {"command": "python nd_call.py POST /v1/carts --body-file b.json --allow-write"}, "ask", "nd_call write asks the developer"),
        ("Bash", {"command": "python nd_discover.py resolve --spec commerce --op \"GET /v1/x\""}, None, "nd_discover runs without a prompt"),
        ("Bash", {"command": "python nd_cred.py status"}, None, "credential status"),
        ("Bash", {"command": "python nd_cred.py forget --name dev"}, "ask", "forgetting a credential asks the developer")]:
        got = run(tool, ti); ok = got == want; failed += not ok
        print(("ok  " if ok else "FAIL"), label, "->", got)
    # writes outside the workspace: the Write tool, redirections, PowerShell and common commands (defect 6)
    outside_file = os.path.join(os.path.dirname(ws), "outside.txt")
    scratch = os.path.join(TEMP_AREA, "scratch.txt")
    with open(os.path.join(ws, "nd-work", "ND-001", "approval.json"), "w", encoding="utf-8") as f:
        json.dump({"approved": False}, f)
    for tool, ti, want, label in [
        ("Write", {"file_path": outside_file}, "deny", "Write tool outside the workspace"),
        ("Write", {"file_path": scratch}, None, "Write tool in the scratch area"),
        ("Write", {"file_path": os.path.join(tempfile.gettempdir(), "other-tool", "x.txt")}, "deny", "Write tool in another temp folder"),
        ("Bash", {"command": "echo x > ../outside.txt"}, "deny", "redirect to a parent folder"),
        ("Bash", {"command": "echo x >> " + outside_file}, "deny", "append redirect to an absolute path outside"),
        ("Bash", {"command": "Set-Content -Path ../outside.txt -Value x"}, "deny", "PowerShell Set-Content -Path outside"),
        ("Bash", {"command": "Set-Content ../outside.txt x"}, "deny", "PowerShell Set-Content positional outside"),
        ("Bash", {"command": "'x' | Out-File -FilePath " + outside_file}, "deny", "PowerShell Out-File outside"),
        ("Bash", {"command": "Copy-Item a.txt $env:USERPROFILE\\a.txt"}, "deny", "Copy-Item to the profile folder"),
        ("Bash", {"command": "cp a.txt " + outside_file}, "deny", "cp to outside"),
        ("Bash", {"command": "mv nd-work/a.txt ../a.txt"}, "deny", "mv out of the workspace"),
        ("Bash", {"command": "curl.exe -s -o " + outside_file + " https://localhost/y"}, "deny", "curl -o outside"),
        ("Bash", {"command": "Invoke-WebRequest https://localhost/y -OutFile " + outside_file}, "deny", "iwr -OutFile outside"),
        ("Bash", {"command": "cmd /c \"echo x > " + outside_file + "\""}, "deny", "redirect hidden inside cmd /c"),
        ("Bash", {"command": "powershell -Command \"Set-Content -Path " + outside_file + " -Value x\""}, "deny", "Set-Content hidden inside powershell -Command"),
        ("Bash", {"command": "cd " + os.path.dirname(ws) + "; echo x > a.txt"}, "deny", "relative redirect after cd out of the workspace"),
        ("Bash", {"command": "echo x > $unknown\\a.txt"}, "ask", "unresolvable write target asks"),
        ("Bash", {"command": "python -c \"open('a.txt','w').write('x')\""}, "ask", "interpreter one-liner that writes asks"),
        ("Bash", {"command": "echo x > src/a.cs"}, "deny", "workspace write before approval"),
        ("Bash", {"command": "echo x > nd-work/ND-001/notes.md"}, None, "nd-work write before approval"),
        ("Bash", {"command": "echo x > " + scratch}, None, "scratch area redirect"),
        ("Bash", {"command": "echo \"a>b\" ; dotnet build 2>&1 > /dev/null"}, None, "quoted > and 2>&1 are not writes"),
        ("Bash", {"command": "curl.exe -sk https://localhost/y 2>nul"}, None, "2>nul is not a write"),
        ("Bash", {"command": "Write-Output $env:ZNODE_API_TOKEN"}, "deny", "printing the credential variable"),
        ("Bash", {"command": "python nd_cred.py get --name dev"}, "deny", "credential read through nd_cred get"),
        ("Read", {"file_path": os.path.join(os.path.expanduser("~"), ".nelli-dev", "credentials.json")}, "deny", "credential file read"),
    ]:
        got = run(tool, ti); ok = got == want; failed += not ok
        print(("ok  " if ok else "FAIL"), label, "->", got, f"(want {want})" if not ok else "")
    with open(os.path.join(ws, "nd-work", "ND-001", "approval.json"), "w", encoding="utf-8") as f:
        json.dump({"approved": True, "scope": ["src/*"]}, f)
    for tool, ti, want, label in [
        ("Bash", {"command": "echo x > src/a.cs"}, None, "workspace redirect inside the approved scope"),
        ("Bash", {"command": "echo x > other/a.cs"}, "deny", "workspace redirect outside the approved scope"),
        ("Bash", {"command": "echo x > .claude/agents/z.md"}, "deny", "redirect into a protected folder"),
        ("Write", {"file_path": outside_file}, "deny", "approved plan does not open the outside"),
    ]:
        got = run(tool, ti); ok = got == want; failed += not ok
        print(("ok  " if ok else "FAIL"), label, "->", got, f"(want {want})" if not ok else "")
    import nd_config
    cfg = nd_config.load()
    cfg["environments"] = [{"name": "central", "gateway_url": "https://central.example.invalid", "host": "central.example.invalid", "non_production": True}]
    cfg["projects"] = [{"name": "sdk2", "path": outside}]
    nd_config.save(cfg)
    for cmd, want, label in [("curl.exe -sk https://central.example.invalid/v1/x", None, "curl to a gateway from the central config")]:
        got = run("Bash", {"command": cmd}); ok = got == want; failed += not ok
        print(("ok  " if ok else "FAIL"), label, "->", got)
    print("selftest:", "PASS" if not failed else f"{failed} FAILED")
    return 1 if failed else 0


def main() -> None:
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    try:
        payload = json.load(sys.stdin)
        agent = payload.get("agent_type")
        if os.environ.get("NELLIDEV_GUARD_ALL") != "1" and not (agent and (agent == AGENT_PREFIX or agent.startswith(AGENT_PREFIX + ":"))):
            return      # not a Nelli-Dev agent: no opinion, the developer's other work is not restricted
        handle(payload)
    except SystemExit:
        raise
    except Exception as exc:  # fail closed
        decision("deny", f"guard error ({type(exc).__name__}: {exc}); blocking to be safe.")


if __name__ == "__main__":
    main()
