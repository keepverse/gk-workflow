# opencode backend spec — third lane runtime beside cmdc/pi

Status: contract spec + working probe. The production wire-in (a third branch in
`cmdc_agent.py`) is owner-applied; the v2.0.16 invocation and terminal-result
behavior below were measured on 2026-09-24, not inferred from docs.

Prior art: `cmdc -p --output-format json` (NDJSON, `result` line) and
`pi -p --mode json -a` (normalised onto cmdc shapes in
`run_segment_pi`, cmdc_agent.py:1159-1270). opencode follows the pi pattern:
no `--max-turns`, so segments end by killing at a step boundary (rc 8, same
contract as cmdc's max-turns exit).

## 1. Invocation (measured)

```
opencode run --format json <worktree> [--model provider/model[#variant]] [--session <opencode-session-id>]
```

- Prompt goes on **stdin** (verified: piped prompt answered, new session started).
  This matches the runner's stdin delivery and avoids argv length limits.
- The worktree is a positional directory argument; OpenCode v2 treats it as the project root,
  so its `read`/`edit`/`write`/`bash`/`glob`/`grep` operate inside the fence by default.
- `--model` takes `provider/model` or `provider/model#variant` (OpenCode v2 native form,
  e.g. whatever `opencode models` lists). Charter entries for this runtime therefore use
  opencode model ids, **not** `opencode-go/*` (that prefix is the pi-bundle form,
  profiles.json:57).
- Resume: `--session <id>` continues the same `sessionID` in a new process
  (verified: second invocation emitted the same `sessionID` with a new
  `messageID`, exit 0).
- Success exit: `0` with a clean terminal result. The legacy backend emitted a
  terminal `step_finish` with `reason: "stop"`; OpenCode v2.0.16 can instead end
  with exit `0` after a final `text` event, with the preceding tool step carrying
  `reason: "tool-calls"`. The runner accepts either shape. A non-zero exit,
  missing session, or stream ending without a terminal result is an error and
  maps onto the runner's existing rc classes (quota/context/fatal regexes
  unchanged — they classify message text, which is backend-agnostic).

## 2. Event normalisation (measured shapes → cmdc shapes)

opencode `--format json` emits one JSON object per line. Every object carries
`sessionID`; the first one seen becomes `run_start.sessionId`
(same role as pi's `session` event, cmdc_agent.py:1214-1215).

| opencode `type` | key fields (measured) | cmdc shape to emit |
|---|---|---|
| `step_start` | — (one per assistant step) | `turn_start` (count toward `turnsUsed`; segment cap checked here) |
| `text` | `part.text` | `message_end` with `content:[{type:text,text}]`, only when non-empty |
| `tool_use` | `part.tool`, `part.callID`, `state.status`, `state.input` | `tool_queued` with `toolName=part.tool`, `input=state.input` (native names kept: `read edit write bash glob grep …`; no rename map needed — `on_event` only displays them) |
| `step_finish` | `part.reason` (`stop`\|`tool-calls`), `part.tokens{total,input,output,reasoning,cache{read,write}}` | `model_request_end` with `usage{inputTokens,outputTokens,cacheReadTokens,cacheWriteTokens}`; accumulate into `status.tokens` exactly as `on_event` does (cmdc_agent.py:1362-1371) |
| (stream end) | legacy `step_finish.reason == "stop"`, or v2 clean exit after a non-empty final `text` | `result` success, `finalText` = last non-empty assistant text |

Segment cap: when `step_start` count exceeds the segment budget, kill the child
at that clean boundary and return rc 8 — identical to the pi branch
(cmdc_agent.py:1237-1240,1260-1261). Never kill mid-`tool_use`.

Error text for quota classification: opencode surfaces provider errors as
assistant/error text in the stream; the existing `QUOTA_ERR`/`CONTEXT_ERR`/
`FATAL_CFG_ERR` regexes (cmdc_agent.py:810-815) apply unchanged. Residual: the
exact opencode error envelope for a quota stop was not triggered in probing
(owner quota is live); first quota hit on this backend should confirm the text
matches before trusting auto-fallback.

## 3. Production wire-in (owner-applied, minimal diff)

In `cmdc_agent.py`, mirroring the pi precedent:

1. `opencode_argv()` beside `cmdc_argv()`/`pi_argv()` (cmdc_agent.py:780-804):
   resolve `opencode` off PATH (`OPENCODE_ENTRY` override), no `.cmd` shim,
   same Windows reasoning.
2. `run_segment_opencode()` beside `run_segment_pi()`: argv from §1, stdin
   prompt, normalisation from §2, kill-at-step cap → rc 8. Dispatch in
   `run_segment()` on `meta["agent"] == "opencode"` (cmdc_agent.py:1273-1276).
3. `--agent` choices gain `"opencode"` (cmdc_agent.py:2130,2250); spawn/continue/
   tune validation accepts it; `_fallbackModelsOpencode` mirrors
   `_fallbackModelsPi` (empty until the owner names one — no implicit fallback,
   charter hard rule).
4. Charter: `allowed-models.json` gains `models.opencode: [...]` (+ mirrored
   top-level `opencode: [...]`); `model_refusal()` already parameterises on the
   agent name (cmdc_agent.py:72), no change needed beyond the list.
5. Profiles: add `coder-opencode` mirroring `coder-pi` (profiles.json:54-61)
   with an opencode-native model id the owner names.
6. Guard: opencode has no PreToolUse hook equivalent verified in this session.
   v1 posture = cwd jail (positional worktree) + the unchanged detect layer
   (`verify_agent` scope check + `audit_agent` over the normalised
   `events.jsonl`). A pre-tool deny hook (opencode plugin) is future work, named
   here so nobody assumes it exists.

No change to `on_event`, `verify_agent`, `audit_agent`, `lane-signals.py`, or
the agent-dir contract (`brief.md`/`status.json`/`notes.jsonl`/`timeline.jsonl`/
`result.json`, `<<<REPORT … REPORT>>>` block). The backend is a producer of the
same shapes, never a second contract (SOLID: one lane contract,
DESIGN-GATE §2.15).

## 4. Proof in this session

- `scripts/opencode_probe.py` runs one headless segment through §1+§2 and
  prints the normalised summary. It is the executable form of this spec.
- `proof-notes.md` records the measured runs (event samples, resume, stdin,
  exit codes, token counts).
