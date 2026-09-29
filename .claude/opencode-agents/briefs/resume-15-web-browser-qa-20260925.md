# Fresh bounded browser QA — accepted web recovery

The previous browser worker stalled after the build and was stopped without evidence. Re-run the proof
in a fresh lane with a hard boundary: do not wait indefinitely for a browser/tool process.

## Allowed write
- `tasks/reports/resume-15-web-browser-qa-20260925.md`
- ignored web/server build outputs needed for the local run

No product/test/CI/generated/tuning edits; no commit/push/merge.

## Procedure
1. From this worktree run `npm ci` and `npm run build` in `gk-web/web/fusion-rpg-web`.
2. If `Get-NetTCPConnection -LocalPort 5088 -State Listen` is occupied, do not kill it; record BLOCKED.
3. Otherwise set `FUSIONRPG_DATA` to this worktree's server data directory and start the Server as a
   detached process using the local-web-review procedure. Poll `/health` for at most 60 seconds.
4. Require `GET /` HTTP 200 and a real `index.html`; use `playwright-cli` against
   `http://127.0.0.1:5088/#/sanctum` (or the relevant route) with a bounded command timeout.
5. Capture snapshot, screenshot, console/network failures, and the exact recovery/match-isolation
   behavior actually observed. Do not fabricate an active match or use debug-only data as browser proof.
6. Close the browser and stop only the server PID you started. If any step times out, stop and report
   the exact blocker rather than waiting.

## Report
Include commands/results, URLs/status, evidence paths, process lifecycle, what was proven/not proven,
and next steps. End with a valid `<<<REPORT {json} REPORT>>>`. Use only
`opencode/space-bunny-free#max`, uncapped input/output, no fallback, no subagent, no external reads.
