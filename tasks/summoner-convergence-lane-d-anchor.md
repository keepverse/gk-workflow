# Anchor: summoner-convergence — lane D (infrastructure)

Maps: [test-verification-boundary-map.md](../docs/architecture/test-verification-boundary-map.md) ·
[solid-enforcement-map.md](../docs/architecture/solid-enforcement-map.md) ·
[notification-ssot-map.md](../docs/architecture/notification-ssot-map.md) · Parent:
[summoner-convergence-plan.md](summoner-convergence-plan.md) (lane D; hard edges H4, H5).

Plan/todo pairs (the lane's scope, in order):
- **SCOPE CHANGE (manager, mid-SE1.6, 2026-09-19): lane narrowed to `solid-enforcement` waves 1–3
  ONLY (`SE1.6`–`SE3.13`, `SECP0`–`SECP3`).** TVB (all waves) and NS moved to two other agents
  running in parallel — do not start them. SE0.1–SE0.8 and TVB0.1–TVB0.4 stay done (already
  committed before the scope change; no uncommitted TVB work existed at the change).
- ~~[test-verification-boundary-plan.md](test-verification-boundary-plan.md) / [-todo.md](test-verification-boundary-todo.md) — `TVB0.1`–`TVB6.4`, all waves.~~ moved off this lane.
- [solid-enforcement-plan.md](solid-enforcement-plan.md) / [-todo.md](solid-enforcement-todo.md) — **waves 1–3 only** (wave 0 already done): `SE1.x`–`SE3.x`. Wave 4 (identity) is lane B's; `SE4.5`–`SE4.10` (file budget) also wait on lane B.
- ~~[notification-ssot-plan.md](notification-ssot-plan.md) / [-todo.md](notification-ssot-todo.md) — `NS*`~~ moved off this lane.

Specs (per task): `docs/architecture/test-verification-boundary/spec-*.md` (8),
`docs/architecture/solid-enforcement/**`, `docs/architecture/notification-ssot/**`.

Session: `summoner-convergence-lane-d-20260919` (worktree, `cmdc/lane-d`) · Paths: `.github/workflows/**`,
`scripts/**`, `tests/**`, `tools/**`, `src/**`, `docs/**`, `data/**`, `web/**`, plus this lane's `tasks/` files.

Standards: `docs/PRINCIPLES.md` + DESIGN-GATE §1 rows (Testing and verification · Guard scripts ·
Data and generated content · Numbers) + `decisions.md` locks — read in this session.

H-edges honoured: **H4** TVB0.3's CI pytest step lands only after TVB0.2 drops the stale
`test_resource_ownership` pins; **H5** SE0.7 (registry schema 2) before TVB2.1 (schema 3);
manifest-review **Checkpoint M** before TVB5.7; `AE1.4`'s atk list (read from
`tasks/evidence-fragments/AE1.4.md`) feeds SE1.6. SE0.8 → TVB3.4 (kind pin 3→4→5).

Queue (ordered; ids only, hard edges first — narrowed 2026-09-19 to SE waves 1-3 per manager scope
change; TVB0.1-TVB0.4/SE0.1-SE0.8 already done, TVB1.x+ and NS moved off this lane):
`SE1.6 SE1.7 SE2.1 SE2.2 SE2.3 SE2.4 SE2.5 SE2.6 SE2.7 SE3.1 SE3.2 SE3.3 SE3.4 SE3.5 SE3.6 SE3.7
SE3.8 SE3.9 SE3.10 SE3.11 SE3.12 SE3.13 SECP0 SECP1 SECP2 SECP3`

Next: `SE1.6` (already started; regenerated creatures + ledger uncommitted from before handover).

Peers: | Peer | Anchor | Provides | Consumes |
|---|---|---|---|---|
| lane A `action-enrich` | `tasks/action-enrich-anchor.md` | `AE1.4.md` atk-granting list → SE1.6 | — |
| lane B `solid-enforcement` wave 4 | lane B's anchor | `SE4.11`–`SE4.43` (not this lane) | SE0.x spine |
| lane C `species-gear-chain` | lane C's anchor | — | TVB registry (schema) |

Drift gates: `python scripts/session-boundary-check.py` ·
`.\scripts\verify-change.ps1 -Paths <changed> -Session summoner-convergence-lane-d-20260919`
(`-PlanOnly` to preview) · per-task `Verify:` line.

Evidence: `tasks/evidence-fragments/<task-id>.md` per task (`| Criterion | Command | Result | Artifact |`).
Ledger: `tasks/summoner-convergence-lane-d-ledger.jsonl` — every event through
`python gk-core/scripts/anchor-ledger.py <ledger> ...`; `resume` is the first command after a fresh start;
`check` must exit 0.

Verify (cadence): the task's focused `dotnet test --filter` / `pytest` / `npm test` + its guards,
never the full suite by default. Full-suite runs (`test-fast.ps1 -AllDefault`) and live probes are
**orchestrator gates**: record the item `blocked` with the dependency named and continue.

Commits: plain `git add <explicit paths>` + `git commit` on `cmdc/lane-d` (the git gate was retired
2026-09-19; never `-A`/`-a`); one task, one cause; tick the todo checkbox in the same commit. Never
push/merge/PR.
