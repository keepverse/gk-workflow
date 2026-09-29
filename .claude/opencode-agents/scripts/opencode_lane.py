"""opencode lane runner — headless opencode workers with the cmdc/pi lane contract.

Repo-tracked counterpart to the user-level cmdc/pi runner: same agent-dir
shapes (brief.md, status.json, timeline.jsonl, notes.jsonl, result.json,
events.jsonl), same <<<REPORT ... REPORT>>> evidence block, same charter hard
rule. It produces the contract; it never forks it.

Commands (run from the repo root):
    spawn   --id <kebab> --brief <md> --context <jsonl> --allow <glob>...
            --model <provider/model> [--verify <cmd>] [--setup <cmd>]
            [--budget N] [--segment N] [--effort <variant>] [--base HEAD]
    status  [--id X]
    tail    --id X [--notes] [-n N]
    steer   --id X "<text>"        (delivered next segment boundary)
    budget  --id X --add N
    stop    --id X [--now]
    verify  --id X [--command <cmd>]
    cleanup --id X [--purge]
    audit   --id X                 (scope + evidence cross-check)

Foreground commands only for the operator (repo rule). spawn returns once the
detached supervisor is running; status/tail poll the files.
"""

import argparse
import fnmatch
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

CREATE_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0
DETACHED = 0x00000008 if sys.platform == "win32" else 0

REPO = Path(__file__).resolve().parents[3]
ROOT = REPO / ".claude" / "opencode-agents"
AGENTS = ROOT / "agents"
CHARTER_FILE = ROOT / "allowed-models.json"

REPORT_RE = re.compile(r"<<<REPORT\s*(\{.*?\})\s*REPORT>>>", re.S)
FENCED_RE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.S)
QUOTA_ERR = re.compile(r"weekly usage limit|usage limit for your plan|insufficient (credits|balance)|"
                       r"out of credits|quota exceeded|billing", re.IGNORECASE)
CONTEXT_ERR = re.compile(r"maximum context length|context length|context window|too many tokens|"
                         r"prompt is too long", re.IGNORECASE)
FATAL_CFG_ERR = re.compile(r"RegionError|DataPolicyError|401|403|invalid api key|unauthori[sz]ed",
                           re.IGNORECASE)
DROP_EVENTS = set()


# ---------- small json/file helpers ----------

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def read_json(path: Path, default=None):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def append_jsonl(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False) + "\n")


def read_jsonl(path: Path, start: int = 0):
    try:
        lines = path.read_text(encoding="utf-8").splitlines()[start:]
    except OSError:
        return []
    out = []
    for ln in lines:
        try:
            out.append(json.loads(ln))
        except ValueError:
            continue
    return out


# ---------- charter (hard rule: owner-approved models only) ----------

def charter() -> dict:
    try:
        return json.loads(CHARTER_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def charter_refusal() -> str | None:
    c = charter()
    if not c.get("approvedAt"):
        return ("the owner charter (allowed-models.json) has no approvedAt: "
                "ask the owner for runtimes, exact models, budget and stop rule first")
    return None


def model_refusal(model: str | None) -> str | None:
    allowed = ((charter().get("models") or {}).get("opencode") or [])
    if not model or model not in allowed:
        return (f"model {model!r} is not in the owner's allowed-models.json "
                f"for opencode {allowed}")
    return None


# ---------- process helpers ----------

def pid_alive(pid) -> bool:
    if not pid:
        return False
    try:
        if sys.platform == "win32":
            r = subprocess.run(["tasklist", "/FI", f"PID eq {pid}"],
                               capture_output=True, text=True)
            return str(pid) in r.stdout
        os.kill(pid, 0)
        return True
    except (OSError, ValueError):
        return False


def kill_tree(pid) -> None:
    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"],
                           capture_output=True)
        else:
            os.killpg(os.getpgid(pid), signal.SIGKILL)
    except (OSError, ValueError, ProcessLookupError):
        pass


def git(args, cwd, check=True) -> str:
    r = subprocess.run(["git"] + args, cwd=str(cwd), capture_output=True,
                       text=True, creationflags=CREATE_NO_WINDOW)
    if check and r.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {r.stderr.strip()[:300]}")
    return r.stdout


def run_shell(command: str, cwd: str, timeout: int) -> dict:
    shell = ["pwsh", "-NoProfile", "-NonInteractive", "-Command", command] \
        if sys.platform == "win32" else ["bash", "-lc", command]
    try:
        r = subprocess.run(shell, cwd=cwd, capture_output=True, text=True,
                           timeout=timeout, creationflags=CREATE_NO_WINDOW)
        return {"rc": r.returncode, "out": r.stdout[-3000:],
                "err": r.stderr[-1000:]}
    except subprocess.TimeoutExpired:
        return {"rc": 124, "out": "", "err": f"timeout after {timeout}s"}


# ---------- brief / scope / report ----------

def brief_verification(brief: str) -> list[str]:
    """Extract commands only from the brief's Verification section."""
    commands: list[str] = []
    in_section = False
    for line in brief.splitlines():
        if re.match(r"^##\s+Verification\s*$", line, re.IGNORECASE):
            in_section = True
            continue
        if in_section and re.match(r"^##\s+", line):
            break
        if in_section:
            commands.extend(re.findall(r"`([^`\n]+)`", line))
    return commands


def in_scope(path: str, allow: list[str]) -> bool:
    p = path.replace("\\", "/")
    return any(fnmatch.fnmatch(p, a.replace("\\", "/")) or
               fnmatch.fnmatch(p, a.replace("\\", "/").rstrip("/") + "/*")
               for a in allow)


def parse_report(text: str):
    for rx in (REPORT_RE, FENCED_RE):
        m = rx.search(text or "")
        if m:
            try:
                return json.loads(m.group(1))
            except ValueError:
                continue
    return None


def render_context(items: list[dict]) -> str:
    return "\n".join(f"- [{it.get('kind', 'fact')}] {it.get('text', '')}"
                     for it in items)


def compose_prompt(brief: str, context: str, extra: str = "") -> str:
    rules = ROOT / "rules.md"
    parts = [brief.strip()]
    if context.strip():
        parts.append("## Context (already verified — do not re-derive)\n" + context.strip())
    if rules.exists():
        parts.append("## Binding repo rules\n" + rules.read_text(encoding="utf-8").strip())
    if extra.strip():
        parts.append(extra.strip())
    parts.append(
        "## Evidence contract\n"
        "End your last message with a <<<REPORT {...} REPORT>>> block: "
        '{"status":"done|partial|blocked","summary":"...","changed_files":[...],'
        '"verification":[{"command":"...","result":"..."}],'
        '"open_issues":["..."]}. changed_files and verification must be real: '
        "the commands named must have been run in this worktree.")
    return "\n\n".join(parts)


# ---------- opencode invocation ----------

def opencode_argv() -> list[str]:
    if os.environ.get("OPENCODE_ENTRY"):
        return [os.environ["OPENCODE_ENTRY"]]
    exe = shutil.which("opencode")
    if not exe:
        raise SystemExit("opencode not found on PATH")
    return [exe]


def opencode_run_argv(meta: dict, session_id: str | None = None) -> list[str]:
    """Build the v2 CLI invocation; the project directory is positional."""
    argv = opencode_argv() + ["run", "--format", "json", meta["cwd"]]
    model = meta.get("model")
    if model:
        if meta.get("effort"):
            model = f"{model}#{meta['effort']}"
        argv += ["--model", model]
    if session_id:
        argv += ["--session", session_id]
    return argv


def run_segment_succeeded(rc: int, last_reason: str | None, final_text: str) -> bool:
    """Accept both legacy stop events and v2's clean exit after final text."""
    return rc == 0 and (last_reason == "stop" or bool((final_text or "").strip()))


# ---------- supervisor ----------

class Supervisor:
    def __init__(self, d: Path):
        self.d = d
        self.meta = read_json(d / "meta.json", {})
        self.st = read_json(d / "status.json", {})
        self.last_error = ""
        self.last_event = time.time()
        self.stop_now = False
        self.child = None

    def flush(self):
        write_json(self.d / "status.json", self.st)

    def tl(self, **kw):
        append_jsonl(self.d / "timeline.jsonl", {"ts": now_iso(), **kw})

    def note(self, kind, **kw):
        append_jsonl(self.d / "notes.jsonl", {"ts": now_iso(), "kind": kind, **kw})

    def log(self, msg):
        with (self.d / "runner.log").open("a", encoding="utf-8") as fh:
            fh.write(f"{now_iso()} {msg}\n")

    # -- event normalisation: opencode --format json -> lane shapes --
    def on_event(self, e) -> None:
        et = e.get("type")
        if et == "run_start" and e.get("sessionId"):
            self.st["sessionId"] = e["sessionId"]
        elif et == "turn_start":
            self.st["turnsUsed"] = self.st.get("turnsUsed", 0) + 1
            self.st["lastActivity"] = f"step {self.st['turnsUsed']}"
        elif et == "tool_queued":
            inp = e.get("input") or ""
            self.st["lastActivity"] = f"{e.get('toolName')}: {str(inp)[:200]}"
            self.tl(kind="tool", step=self.st.get("turnsUsed", 0),
                    name=e.get("toolName"), input=str(inp)[:200])
        elif et == "message_end":
            text = "".join(c.get("text", "") for c in e.get("content", [])
                            if c.get("type") == "text")
            if text.strip():
                self.st["lastSaid"] = text.strip()[-300:]
                self.tl(kind="say", step=self.st.get("turnsUsed", 0),
                        text=text.strip()[:400])
                self.note("say", text=text.strip()[:1000])
                low = text.strip().lower()
                if "blocked:" in low[:200].lower() or low.startswith("blocked"):
                    self.note("blocker", text=text.strip()[:500])
        elif et == "model_request_end":
            u = e.get("usage") or {}
            t = self.st.setdefault("tokens", {"input": 0, "output": 0, "cacheRead": 0})
            t["input"] += u.get("inputTokens", 0)
            t["output"] += u.get("outputTokens", 0)
            t["cacheRead"] += u.get("cacheReadTokens", 0)
            self.st["model"] = e.get("model") or self.st.get("model")
            self.st["contextTokens"] = (u.get("inputTokens", 0) + u.get("cacheReadTokens", 0)
                                        + u.get("cacheWriteTokens", 0))
        elif et == "run_error":
            self.last_error = str(e.get("error", ""))[:500]
            self.tl(kind="error", error=self.last_error)

    def poll_control(self) -> list[str]:
        seen = self.st.get("controlSeen", 0)
        items = read_jsonl(self.d / "control.jsonl", seen)
        self.st["controlSeen"] = seen + len(items)
        steers = []
        for c in items:
            cmd = c.get("cmd")
            if cmd == "stop":
                self.stop_now = True
                self.tl(kind="control", cmd="stop")
            elif cmd == "steer" and c.get("text"):
                steers.append(c["text"])
                self.tl(kind="control", cmd="steer")
            elif cmd == "budget" and c.get("add"):
                self.meta["budget"] = self.meta.get("budget", 0) + int(c["add"])
                self.st["budget"] = self.meta["budget"]
                self.tl(kind="budget", add=c["add"], budget=self.meta["budget"])
        self.flush()
        return steers

    def budget_hit(self) -> bool:
        cap = (charter().get("budget") or {}).get("tokensPerLane") \
            or self.meta.get("budget")
        if not cap:
            return False
        t = self.st.get("tokens", {})
        return (t.get("input", 0) + t.get("output", 0)) >= cap

    def run_segment(self, prompt: str, max_steps: int):
        m = self.meta
        argv = opencode_run_argv(m, self.st.get("sessionId"))
        err = (self.d / "stderr.log").open("ab")
        self.child = subprocess.Popen(argv, cwd=m["cwd"], stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE, stderr=err,
                                      creationflags=CREATE_NO_WINDOW)
        self.st["childPid"] = self.child.pid
        self.flush()
        self.child.stdin.write(prompt.encode("utf-8"))
        self.child.stdin.close()

        steps, final_text, last_reason = 0, "", None
        stalled, capped = {"v": False}, {"v": False}
        done = threading.Event()

        def watchdog():
            while not done.wait(15):
                self.poll_control()
                idle = time.time() - self.last_event
                if self.stop_now or idle > m.get("stallMin", 20) * 60:
                    stalled["v"] = idle > m.get("stallMin", 20) * 60
                    kill_tree(self.child.pid)
                    return
        threading.Thread(target=watchdog, daemon=True).start()

        def emit(ev_obj):
            if ev_obj.get("type") not in DROP_EVENTS:
                append_jsonl(self.d / "events.jsonl",
                             {"seg": self.st.get("segment", 1), "ts": now_iso(), **ev_obj})
            self.on_event(ev_obj)

        for raw in self.child.stdout:
            line = raw.decode("utf-8", errors="replace").strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                continue
            self.last_event = time.time()
            self.st["lastEventAt"] = now_iso()
            if self.st.get("sessionId") is None and o.get("sessionID"):
                emit({"type": "run_start", "sessionId": o["sessionID"]})
            t = o.get("type")
            part = o.get("part") or {}
            if t == "step_start":
                steps += 1
                emit({"type": "turn_start", "step": steps})
                if steps >= max_steps:
                    capped["v"] = True  # clean boundary, like cmdc max-turns exit
                    kill_tree(self.child.pid)
                    break
            elif t == "text":
                text = part.get("text") or ""
                if text.strip():
                    final_text = text.strip()
                    emit({"type": "message_end",
                          "content": [{"type": "text", "text": text}]})
            elif t == "tool_use":
                state = part.get("state") or {}
                inp = state.get("input") or {}
                summ = (inp.get("command") or inp.get("filePath")
                        or inp.get("path") or inp.get("pattern")
                        or json.dumps(inp, ensure_ascii=False)) \
                    if isinstance(inp, dict) else str(inp)
                emit({"type": "tool_queued", "toolName": part.get("tool"),
                      "input": str(summ)[:200], "status": state.get("status")})
            elif t == "step_finish":
                toks = part.get("tokens") or {}
                cache = toks.get("cache") or {}
                last_reason = part.get("reason")
                emit({"type": "model_request_end",
                      "usage": {"inputTokens": toks.get("input", 0),
                                "outputTokens": toks.get("output", 0),
                                "cacheReadTokens": cache.get("read", 0),
                                "cacheWriteTokens": cache.get("write", 0)}})
            self.flush()
        rc = self.child.wait()
        done.set()
        err.close()
        self.st["childPid"] = None
        self.flush()
        if capped["v"]:
            return 8, final_text
        if run_segment_succeeded(rc, last_reason, final_text):
            return 0, final_text
        if self.last_error:
            e = self.last_error
            rc = (10 if QUOTA_ERR.search(e) else 1 if CONTEXT_ERR.search(e)
                  else 3 if FATAL_CFG_ERR.search(e) else 5)
        elif rc == 0:
            rc = 1  # stream ended without a stop
        return rc, final_text

    # -- verify: re-run brief commands + scope fence --
    def verify(self, commands=None) -> dict:
        m = self.meta
        cmds = commands if commands is not None else brief_verification(
            (self.d / "brief.md").read_text(encoding="utf-8"))
        per, ok = [], True
        for c in cmds:
            r = run_shell(c, m["cwd"], timeout=600)
            per.append({"command": c, "rc": r["rc"],
                        "tail": (r["out"] + r["err"])[-500:]})
            if r["rc"] != 0:
                ok = False
        try:
            changed = git(["status", "--porcelain"], m["cwd"], check=False).splitlines()
            diff = git(["diff", "--stat", m.get("base", "HEAD")], m["cwd"], check=False)
        except SystemExit:
            changed, diff = [], ""
        files = [ln[3:].strip().strip('"') for ln in changed if len(ln) > 3]
        oos = [f for f in files if not in_scope(f, m.get("allow", []))]
        if oos:
            ok = False
        report = {"pass": ok and not oos, "outOfScope": oos,
                  "commands": per, "changed": files, "diffstat": diff[-1000:]}
        write_json(self.d / "verify.json", report)
        return report

    def finish(self, state, report, final_text):
        m = self.meta
        verify_report = self.verify() if state in ("done", "partial") else None
        try:
            changed = git(["status", "--porcelain"], m["cwd"], check=False).splitlines()
            files = [ln[3:].strip().strip('"') for ln in changed if len(ln) > 3]
            diffstat = git(["diff", "--stat", m.get("base", "HEAD")], m["cwd"], check=False)
        except SystemExit:
            files, diffstat = [], ""
        result = {"state": state, "report": report,
                  "runnerVerify": verify_report,
                  "git": {"changed": files, "diffstat": diffstat[-2000:]},
                  "tokens": self.st.get("tokens", {})}
        write_json(self.d / "result.json", result)
        self.st.update({"state": state, "finishedAt": now_iso(), "childPid": None})
        self.tl(kind="finish", state=state)
        self.flush()
        self.log(f"finished {state}")

    def supervise(self):
        m = self.meta
        self.log(f"supervising {m['id']} (budget={m.get('budget')} steps/seg={m.get('segment')})")
        self.st.update({"state": "running", "segment": 1, "turnsUsed": 0,
                        "model": m.get("model"),
                        "tokens": {"input": 0, "output": 0, "cacheRead": 0}})
        self.flush()
        brief = (self.d / "brief.md").read_text(encoding="utf-8")
        ctx_items = read_jsonl(self.d / "context.jsonl")
        prompt = compose_prompt(brief, render_context(ctx_items))
        (self.d / "prompt.md").write_text(prompt, encoding="utf-8")
        nudges = 0
        while True:
            steers = self.poll_control()
            if steers:
                prompt = ("ORCHESTRATOR: " + "\nORCHESTRATOR: ".join(steers)
                          + "\n\n" + prompt)
            if self.stop_now:
                return self.finish("stopped", None, "")
            self.tl(kind="segment_start", seg=self.st.get("segment", 1))
            rc, final_text = self.run_segment(prompt, m.get("segment", 40))
            self.tl(kind="segment_end", seg=self.st.get("segment", 1), rc=rc)
            if self.stop_now:
                return self.finish("stopped", None, final_text)
            if self.budget_hit():
                return self.finish("budget_exhausted", parse_report(final_text), final_text)
            if rc == 10:
                self.st["state"] = "quota"
                self.flush()
                return self.finish("failed", parse_report(final_text), final_text)
            if rc == 8:  # segment cap: continue same session, fresh prompt slice
                self.st["segment"] = self.st.get("segment", 1) + 1
                prompt = ("Continue the brief. Your session memory is intact. "
                          "Make steady progress and re-state the <<<REPORT>>> block "
                          "when the task is complete.")
                self.flush()
                continue
            if rc != 0:
                self.log(f"segment rc={rc} err={self.last_error[:200]}")
                return self.finish("failed", parse_report(final_text), final_text)
            report = parse_report(final_text)
            if report is None and nudges < 2:
                nudges += 1
                prompt = ("Your last message did not end with a valid "
                          "<<<REPORT {...} REPORT>>> block. Reply with ONLY that block.")
                continue
            if report is None:
                return self.finish("partial", None, final_text)
            status = (report.get("status") or "done").lower()
            if status == "blocked":
                self.note("blocker", text=json.dumps(report.get("open_issues", []))[:500])
                return self.finish("blocked", report, final_text)
            return self.finish("done" if status == "done" else "partial",
                               report, final_text)


# ---------- operator commands ----------

def agent_dir(agent_id: str) -> Path:
    d = AGENTS / agent_id
    if not d.exists():
        raise SystemExit(f"no such agent: {agent_id}")
    return d


def cmd_spawn(args) -> None:
    if (r := charter_refusal()):
        raise SystemExit(f"refused: {r}")
    if (r := model_refusal(args.model)):
        raise SystemExit(f"refused: {r}")
    if not args.allow:
        print("WARNING: no --allow scope fence; verification will flag every change")
    d = AGENTS / args.id
    if d.exists():
        raise SystemExit(f"agent dir already exists: {d}")
    branch = f"opencode/{args.id}"
    wt = REPO / ".claude" / "worktrees" / f"opencode-{args.id}"
    existing = git(["branch", "--list", branch], REPO, check=False).strip()
    if existing:
        raise SystemExit(f"branch already exists: {branch}")
    base = args.base or "HEAD"
    git(["worktree", "add", str(wt), "-b", branch, base], REPO)
    try:
        if args.setup:
            r = run_shell(args.setup, str(wt), timeout=600)
            if r["rc"] != 0:
                raise SystemExit(f"setup failed rc={r['rc']}: {(r['out'] + r['err'])[-500:]}")
        # AGENTS.md is tracked, so the worktree already carries it (repo rule).
        d.mkdir(parents=True)
        Path(args.brief).resolve()  # fail early on missing brief
        shutil.copy(args.brief, d / "brief.md")
        ctx_src = Path(args.context) if args.context else None
        (d / "context.jsonl").write_text(
            ctx_src.read_text(encoding="utf-8") if ctx_src and ctx_src.exists() else "",
            encoding="utf-8")
        meta = {"id": args.id, "agent": "opencode", "model": args.model,
                "effort": args.effort, "budget": args.budget, "segment": args.segment,
                "cwd": str(wt), "branch": branch, "base": base,
                "allow": args.allow or [],
                "verify": [args.verify] if args.verify else [],
                "stallMin": args.stall_min, "timeoutMin": args.timeout_min,
                "spawnedAt": now_iso()}
        write_json(d / "meta.json", meta)
        write_json(d / "status.json",
                   {"state": "spawning", "segment": 0, "turnsUsed": 0,
                    "budget": args.budget, "sessionId": None, "childPid": None,
                    "controlSeen": 0, "tokens": {"input": 0, "output": 0, "cacheRead": 0},
                    "spawnedAt": now_iso()})
        with (d / "runner.log").open("w", encoding="utf-8") as fh:
            fh.write(f"{now_iso()} spawned {args.id}\n")
        sup = [sys.executable, str(ROOT / "scripts" / "opencode_lane.py"),
               "--_supervise", args.id]
        with (d / "supervisor.out").open("ab") as out:
            subprocess.Popen(sup, cwd=str(REPO), stdout=out, stderr=subprocess.STDOUT,
                             creationflags=CREATE_NO_WINDOW | DETACHED,
                             stdin=subprocess.DEVNULL, close_fds=True)
        print(json.dumps({"id": args.id, "dir": str(d), "cwd": str(wt),
                          "model": args.model, "branch": branch}))
    except BaseException:
        git(["worktree", "remove", "--force", str(wt)], REPO, check=False)
        git(["branch", "-D", branch], REPO, check=False)
        raise


def cmd_status(args) -> None:
    rows = []
    for child in sorted(AGENTS.iterdir()):
        if not child.is_dir() or (args.id and child.name != args.id):
            continue
        st = read_json(child / "status.json", {})
        meta = read_json(child / "meta.json", {})
        if not st and not meta:
            continue
        rows.append({"id": child.name, "state": st.get("state"),
                     "seg": st.get("segment"), "turns": st.get("turnsUsed"),
                     "tokens": st.get("tokens"), "last": st.get("lastActivity"),
                     "model": meta.get("model"), "childAlive": pid_alive(st.get("childPid"))})
    print(json.dumps(rows, ensure_ascii=False, indent=1))


def cmd_tail(args) -> None:
    d = agent_dir(args.id)
    if args.notes:
        items = read_jsonl(d / "notes.jsonl")
        for it in items[-args.n:]:
            print(f"[{it.get('ts', '')} {it.get('kind', '')}] "
                  f"{str(it.get('text', ''))[:400]}")
    else:
        lines = (d / "timeline.jsonl").read_text(encoding="utf-8").splitlines() \
            if (d / "timeline.jsonl").exists() else []
        for ln in lines[-args.n:]:
            print(ln[:300])


def cmd_control(args, cmd) -> None:
    d = agent_dir(args.id)
    obj = {"ts": now_iso(), "cmd": cmd}
    if cmd == "steer":
        obj["text"] = args.text
    if cmd == "budget":
        obj["add"] = args.add
    append_jsonl(d / "control.jsonl", obj)
    print(f"{cmd} queued for {args.id} (takes effect at segment boundary)")


def cmd_stop(args) -> None:
    d = agent_dir(args.id)
    append_jsonl(d / "control.jsonl", {"ts": now_iso(), "cmd": "stop"})
    if args.now:
        st = read_json(d / "status.json", {})
        if st.get("childPid"):
            kill_tree(st["childPid"])
    print(f"stop queued for {args.id}" + (" (child killed)" if args.now else ""))


def cmd_verify(args) -> None:
    d = agent_dir(args.id)
    sup = Supervisor(d)
    cmds = [args.command] if args.command else None
    print(json.dumps(sup.verify(cmds), ensure_ascii=False, indent=1))


def cmd_audit(args) -> None:
    """Detect layer: scope fence + evidence cross-check over events.jsonl."""
    d = agent_dir(args.id)
    meta = read_json(d / "meta.json", {})
    result = read_json(d / "result.json", {})
    findings = []
    changed = ((result.get("runnerVerify") or {}).get("changed")
               or (result.get("git") or {}).get("changed") or [])
    oos = [f for f in changed if not in_scope(f, meta.get("allow", []))]
    if oos:
        findings.append({"severity": "FAIL", "code": "protected-path-changed",
                         "detail": oos})
    events = read_jsonl(d / "events.jsonl")
    git_push = any(e.get("toolName") == "bash" and "push" in str(e.get("input", ""))[:200]
                   for e in events)
    if git_push:
        findings.append({"severity": "WARN", "code": "git-push",
                         "detail": "a git push ran (push stays owner-ask-only)"})
    report = result.get("report") or {}
    if report and report.get("status") == "done" and not changed and not meta.get("allow"):
        findings.append({"severity": "WARN", "code": "done-without-evidence",
                         "detail": "done with no recorded changes"})
    print(json.dumps({"id": args.id, "findings": findings,
                      "events": len(events)}, ensure_ascii=False, indent=1))


def cmd_harvest(args) -> None:
    d = agent_dir(args.id)
    meta = read_json(d / "meta.json", {})
    cwd = meta.get("cwd", REPO)
    out = d / "changes.patch"
    parts = [git(["diff", meta.get("base", "HEAD")], cwd, check=False)]
    porcelain = git(["status", "--porcelain"], cwd, check=False).splitlines()
    for ln in porcelain:
        if ln.startswith("??"):
            rel = ln[3:].strip().strip('"')
            parts.append(git(["diff", "--no-index", "--", "/dev/null", rel],
                             cwd, check=False))
    diff = "".join(parts)
    out.write_text(diff, encoding="utf-8")
    print(f"wrote {out} ({len(diff)} bytes). Apply in the main tree with "
          f"git apply --3way {out} after review, then commit explicit paths.")


def cmd_cleanup(args) -> None:
    d = agent_dir(args.id)
    meta = read_json(d / "meta.json", {})
    st = read_json(d / "status.json", {})
    if st.get("state") not in ("done", "partial", "blocked", "failed",
                               "stopped", "budget_exhausted", "quota"):
        raise SystemExit(f"refused: agent is {st.get('state')} (stop it first)")
    if st.get("childPid") and pid_alive(st["childPid"]):
        raise SystemExit("refused: child still alive")
    if meta.get("cwd"):
        git(["worktree", "remove", "--force", meta["cwd"]], REPO, check=False)
    if meta.get("branch"):
        git(["branch", "-D", meta["branch"]], REPO, check=False)
    if args.purge:
        shutil.rmtree(d)
        print(f"purged {args.id}")
    else:
        print(f"cleaned worktree+branch for {args.id} (agent dir kept)")


def main() -> None:
    ap = argparse.ArgumentParser(prog="opencode_lane.py")
    ap.add_argument("--_supervise", default=None)
    sub = ap.add_subparsers(dest="cmd", required=False)

    s = sub.add_parser("spawn")
    s.add_argument("--id", required=True)
    s.add_argument("--brief", required=True)
    s.add_argument("--context", default=None)
    s.add_argument("--allow", action="append", default=[])
    s.add_argument("--model", required=True)
    s.add_argument("--effort", default=None)
    s.add_argument("--verify", default=None)
    s.add_argument("--setup", default=None)
    s.add_argument("--budget", type=int, default=1500)
    s.add_argument("--segment", type=int, default=40)
    s.add_argument("--base", default="HEAD")
    s.add_argument("--stall-min", type=int, default=20)
    s.add_argument("--timeout-min", type=int, default=0)

    s = sub.add_parser("status")
    s.add_argument("--id", default=None)
    s = sub.add_parser("tail")
    s.add_argument("--id", required=True)
    s.add_argument("--notes", action="store_true")
    s.add_argument("-n", type=int, default=30)
    s = sub.add_parser("steer")
    s.add_argument("--id", required=True)
    s.add_argument("text")
    s = sub.add_parser("budget")
    s.add_argument("--id", required=True)
    s.add_argument("--add", type=int, required=True)
    s = sub.add_parser("stop")
    s.add_argument("--id", required=True)
    s.add_argument("--now", action="store_true")
    s = sub.add_parser("verify")
    s.add_argument("--id", required=True)
    s.add_argument("--command", default=None)
    s = sub.add_parser("audit")
    s.add_argument("--id", required=True)
    s = sub.add_parser("harvest")
    s.add_argument("--id", required=True)
    s = sub.add_parser("cleanup")
    s.add_argument("--id", required=True)
    s.add_argument("--purge", action="store_true")

    args = ap.parse_args()
    if args._supervise:
        Supervisor(agent_dir(args._supervise)).supervise()
        return
    if not args.cmd:
        ap.error("a subcommand is required (spawn|status|tail|steer|budget|stop|verify|audit|harvest|cleanup)")
    if args.cmd == "spawn":
        cmd_spawn(args)
    elif args.cmd == "status":
        cmd_status(args)
    elif args.cmd == "tail":
        cmd_tail(args)
    elif args.cmd == "steer":
        cmd_control(args, "steer")
    elif args.cmd == "budget":
        cmd_control(args, "budget")
    elif args.cmd == "stop":
        cmd_stop(args)
    elif args.cmd == "verify":
        cmd_verify(args)
    elif args.cmd == "audit":
        cmd_audit(args)
    elif args.cmd == "harvest":
        cmd_harvest(args)
    elif args.cmd == "cleanup":
        cmd_cleanup(args)


if __name__ == "__main__":
    main()
