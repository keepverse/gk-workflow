"""One headless opencode segment, normalised onto the cmdc lane event shapes.

Executable form of ../opencode-backend-spec.md. stdlib only. Foreground by
design (repo rule: foreground commands only — rules.md:39-41).

Usage:
    python opencode_probe.py --dir <workdir> [--model provider/model]
        [--session <opencode-session-id>] [--max-steps N]
        [--events-out <path>] [--prompt <text> | stdin]

Exit codes mirror the runner contract: 0 = clean terminal result
(legacy reason "stop" or v2 final text); 8 = capped at --max-steps (clean
step boundary); 1 = error (non-zero child, no terminal result, or protocol
failure).
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

CREATE_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0


def opencode_argv():
    if os.environ.get("OPENCODE_ENTRY"):
        return [os.environ["OPENCODE_ENTRY"]]
    exe = shutil.which("opencode")
    if not exe:
        raise SystemExit("opencode not found on PATH")
    return [exe]


def segment_succeeded(rc: int, last_reason: str | None, final_text: str) -> bool:
    """Accept v2's clean exit after final text and the legacy stop event."""
    return rc == 0 and (last_reason == "stop" or bool((final_text or "").strip()))


def summarize_input(inp):
    if not isinstance(inp, dict):
        return str(inp)[:200]
    for k in ("command", "filePath", "file_path", "path", "pattern"):
        if inp.get(k):
            return str(inp[k])[:200]
    return json.dumps(inp, ensure_ascii=False)[:200]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--model", default=None)
    ap.add_argument("--session", default=None)
    ap.add_argument("--max-steps", type=int, default=30)
    ap.add_argument("--events-out", default=None)
    ap.add_argument("--prompt", default=None)
    args = ap.parse_args()

    if args.prompt is not None:
        prompt = args.prompt
    else:
        prompt = sys.stdin.read()
    if not prompt.strip():
        raise SystemExit("empty prompt (pass --prompt or pipe stdin)")

    argv = opencode_argv() + ["run", "--format", "json", args.dir]
    if args.model:
        argv += ["--model", args.model]
    if args.session:
        argv += ["--session", args.session]

    child = subprocess.Popen(
        argv,
        cwd=args.dir,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=CREATE_NO_WINDOW,
    )
    assert child.stdin and child.stdout and child.stderr
    child.stdin.write(prompt.encode("utf-8"))
    child.stdin.close()

    events_out = Path(args.events_out) if args.events_out else Path(args.dir) / "events-opencode.jsonl"
    session_id = None
    steps = 0
    capped = False
    tools = []
    tokens = {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0}
    final_text = ""
    last_reason = None

    def note(obj):
        with events_out.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(obj, ensure_ascii=False) + "\n")

    assert child.stdout is not None
    for raw in child.stdout:
        line = raw.decode("utf-8", errors="replace").strip()
        if not line:
            continue
        try:
            o = json.loads(line)
        except json.JSONDecodeError:
            continue
        if session_id is None and o.get("sessionID"):
            session_id = o["sessionID"]
            note({"type": "run_start", "sessionId": session_id})
        t = o.get("type")
        part = o.get("part") or {}
        if t == "step_start":
            steps += 1
            note({"type": "turn_start", "step": steps})
            if steps > args.max_steps:
                capped = True
                child.kill()
                break
        elif t == "text":
            text = part.get("text") or ""
            if text.strip():
                final_text = text.strip()
                note({"type": "message_end",
                      "content": [{"type": "text", "text": text}]})
        elif t == "tool_use":
            name = part.get("tool")
            state = part.get("state") or {}
            tools.append(name)
            note({"type": "tool_queued", "toolName": name,
                  "input": summarize_input(state.get("input")),
                  "status": state.get("status")})
        elif t == "step_finish":
            toks = part.get("tokens") or {}
            cache = toks.get("cache") or {}
            last_reason = part.get("reason")
            u = {"inputTokens": toks.get("input", 0),
                 "outputTokens": toks.get("output", 0),
                 "cacheReadTokens": cache.get("read", 0),
                 "cacheWriteTokens": cache.get("write", 0)}
            tokens["input"] += u["inputTokens"]
            tokens["output"] += u["outputTokens"]
            tokens["cacheRead"] += u["cacheReadTokens"]
            tokens["cacheWrite"] += u["cacheWriteTokens"]
            note({"type": "model_request_end", "usage": u,
                  "reason": last_reason})

    rc = child.wait()
    err_tail = (child.stderr.read().decode("utf-8", errors="replace") or "")[-500:]

    summary = {
        "sessionId": session_id,
        "steps": steps,
        "tools": tools,
        "tokens": tokens,
        "lastReason": last_reason,
        "finalTextTail": final_text[-300:],
        "childRc": rc,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    if err_tail.strip():
        print("STDERR-TAIL: " + err_tail.strip()[-300:], file=sys.stderr)

    if capped:
        print("SEGMENT_CAPPED at clean step boundary (runner rc 8)")
        return 8
    if segment_succeeded(rc, last_reason, final_text) and session_id:
        note({"type": "result", "subtype": "success",
              "sessionId": session_id, "finalText": final_text})
        return 0
    print("SEGMENT_ERROR: no clean terminal result (see STDERR-TAIL)", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
