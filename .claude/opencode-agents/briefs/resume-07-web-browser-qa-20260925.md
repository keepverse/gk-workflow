# Web/browser QA — accepted recovery contract

Produce browser evidence for the already-merged web recovery/match-isolation change. This is a QA
producer lane, not an implementation lane.

## Rules

- Read the current repository state and the accepted web report/artifact.
- Do not edit product code, tests, generated data, tuning, CI, or verification scripts.
- The only tracked write allowed is `tasks/reports/resume-07-web-browser-qa-20260925.md` plus the
  session record managed by the runner.
- Do not fabricate a player, match, snapshot, event, or server result. Use only real local server
  routes and real records/IDs created by normal server behavior. If no active match exists, document
  the exact boundary instead of inventing one.
- Do not kill unrelated processes. If port 5088 is occupied, record it and stop rather than claiming
  browser proof.

## Procedure

1. In this worktree, run `npm ci` and `npm run build` from `gk-web/web/fusion-rpg-web`.
2. Before starting the server, check `Get-NetTCPConnection -LocalPort 5088 -State Listen`. If free,
   set `FUSIONRPG_DATA` to this worktree's server data directory and start the server as its own
   detached process using the local-web-review procedure. Poll `/health` until it returns JSON.
3. Read back `GET /` and require HTTP 200; a healthy API with a 404 FE is not browser evidence.
4. Use the repository's `playwright-cli` skill/CLI against `http://127.0.0.1:5088/#/sanctum` (or the
   relevant route). Capture a snapshot, screenshot, console output, and request/failure summary.
5. Exercise only real recovery/reconnect/match-isolation behavior available from the local server and
   browser. If a live SignalR match cannot be created without a game, state that exact blocker and
   separate static/browser page evidence from unproven recovery semantics.
6. Close the browser and stop only the server process you started. Record the exact commands, URLs,
   HTTP results, screenshot/evidence locations, what the browser proved, and what it did not prove.

## Report

Write a disk-backed report with status, worktree/head, commands/results, browser evidence paths,
server process lifecycle, observed console/network failures, open blockers, and next steps. End with a
valid `<<<REPORT {json} REPORT>>>` block. Use only OpenCode CLI `opencode/space-bunny-free#max`,
uncapped input/output, no fallback, no subagent, and no external-directory reads.
