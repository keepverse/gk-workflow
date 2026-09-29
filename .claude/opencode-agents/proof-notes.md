# Proof notes — opencode headless lane transport (measured 2026-09-23)

Tool: `opencode 1.18.32`. Scratch: `%TEMP%\opencode\probe1` (outside the repo;
nothing committed from there). Spend: four tiny runs, ~15k input tokens each
(mostly opencode's own system context), negligible output. Cost meter read 0.

## P1 — text reply over `--format json`

`opencode run "reply with exactly: ok" --format json --dir <scratch>` →
three NDJSON lines: `step_start`, `text` (`part.text == "ok"`),
`step_finish` (`reason: "stop"`, `tokens: {total:14476, input:14309,
output:11, reasoning:43, cache:{write:0, read:113}}`, `cost: 0`).
Every line carries `sessionID: ses_f32d9d637ffeELgFZCQV91A5y0`.

## P2 — tool use shapes

Prompt asked to read `probe-in.txt`, write uppercased `probe-out.txt`, reply
DONE. Stream showed the repeating triple per step:
`step_start` → `tool_use` (`part.tool` ∈ {read, bash, write},
`part.callID`, `state: {status: "completed", input: {...}}`) →
`step_finish` (`reason: "tool-calls"`, per-step `tokens`). Final triple ended
`text: "DONE"` + `step_finish` `reason: "stop"` (`tokens.total: 16902`).
`probe-out.txt` on disk contained `HELLO LANE` — the tools really ran.

## P3 — resume continues the session

`opencode run --session ses_f32d9905bffeiTMgSWqNDWhNQT "reply with exactly:
resumed" --format json` → events carried the **same** `sessionID` with a new
`messageID`, exit 0. Segment chaining via `--session` works; no re-brief cost
beyond normal context.

## P4 — stdin prompt delivery

`"reply with exactly: via-stdin" | opencode run --format json` (no positional
message) → answered `via-stdin` in a new session, exit 0. Long briefs can ride
stdin exactly like the cmdc/pi runner does.

## P5 — probe script (this repo)

`.claude/opencode-agents/scripts/opencode_probe.py` replays P1-shape traffic
through the §1+§2 normalisation and exits 0/8/1 on the runner contract.
Its run output is the acceptance evidence for the adapter task.

## P6 — first repo-runner lane `smoke-1` (2026-09-23, end to end)

Charter: `opencode/muse-spark-1.3-contributor-free`, 100k tokens (owner grant
this session). Task: write `lane-smoke.txt == smoke-ok` in its own worktree
(branch `opencode/smoke-1`), reply REPORT.

- `spawn` created branch + worktree, ran setup, detached supervisor.
- Supervisor arg bug found live (`--_supervise` vs required subcommand —
  argparse exited in `supervisor.out`); fixed, relaunched, 12/12 offline tests
  green after updating the charter test to the approved state.
- Lane finished `done`: 1 segment, 3 steps, input 42904 + output 313 = 43217
  ≤ 100k budget. REPORT parsed with matching command; `runnerVerify.pass:
  true` (assert re-run rc 0, `outOfScope: []`, `changed:
  ["lane-smoke.txt"]`); `audit` zero findings over 11 events.
- Independent read-back: worktree `lane-smoke.txt` == `'smoke-ok'`.
- `harvest` wrote a 0-byte patch (untracked-only changes missing from
  `git diff`); fixed to append `git diff --no-index /dev/null` per untracked
  file, proven in a scratch repo (155 bytes, names the file).
- `cleanup --purge` removed worktree + branch + agent dir; branch list clean.

## Residuals (honest gaps)

- Quota/error envelope: no quota stop was triggered, so the opencode-specific
  error text is unconfirmed against `QUOTA_ERR`/`CONTEXT_ERR`/`FATAL_CFG_ERR`
  (spec §2). First live quota hit must confirm before trusting auto-fallback.
- No pre-tool hook was found/verified for opencode; v1 posture is cwd jail +
  post-hoc scope verify + audit (spec §3.6).
