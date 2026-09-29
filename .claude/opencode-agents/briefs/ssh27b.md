# Lane brief — `ssh27b` (opencode continuation of `cmdc/ssh27`, SSH6.8 publish)

## Why this lane exists

`cmdc/ssh27` (pi, 62 segments) stalled with SSH6.8 unstarted and publish-prep
WIP in its tree, adopted as `16c578342` on `cmdc/ssh27`. Adopt that commit,
then land the publish. Do NOT re-do the merged review below; it is handover
fact.

⛔ Read `docs/DESIGN-GATE.md` §1 first and the documents its row names, in this
session, then verify against code. A comment is not evidence; open the file.

## Goal

Close `tasks/strain-splice-host-todo.md` **SSH6.8** in ONE commit: publish
`sockets` v3 `comboPricing` with the passing report's provenance, plus the
BalanceGuard test.

## Handover facts (already verified — confirm at adopt time, do not re-derive)

- Merged `6fd030b4`: SSH5.10/5.11/6.1 reviewed at `4e94fd92`, merge `e78f4a12`,
  union-artifact fix `06a7c452`.
- SSH6.2/6.3/6.4 are ticked done in the todo (evidence fragments
  `tasks/evidence-fragments/SSH6.2.md` etc.). The predecessor's "SSH6.4 next"
  note is STALE — trust the todo rows, then verify SSH6.5/SSH6.7 yourself:
  if either is unmet, STOP and report it as the blocker instead of
  publishing.
- Adopted WIP (`16c578342`, 11 files): `RarityBudgetKeys.cs`,
  `Sockets/SocketTuning.cs`, `Sockets/StrainSpliceTuning.cs`, Server
  `Program.cs`, `SocketMaxCheck.cs`, the items `basetypegen`/`combogen`
  (incl. `tuning.py`)`/`gemgen` adapters, `test_combogen.py`, plus one
  cross-program ledger line (`tasks/summoner-convergence-lane-c-ledger.jsonl`)
  that rides along untouched.
- No hard progression ceilings: a cap is removed or made a configurable soft
  cap; an absolute bound is derived and throws, never clamps. Magnitudes are
  `long` with `checked` arithmetic; tuning numbers live in `gk-core/data/tuning`,
  never in code. Guard-population pins are forbidden.

## Allowed paths

- `gk-core/src/FusionRpg.Core/Items/**`
- `gk-core/src/FusionRpg.Server/Program.cs`
- `gk-forge/tools/ItemSeedValidator/**`
- `gk-forge/tools/seedsmith/seedsmith/adapters/items/**`
- `gk-forge/tools/seedsmith/tests/test_combogen.py`
- `data/tuning/socket*.json`
- `data/tuning/sockets*.json`
- `docs/architecture/strain-splice-host/**`
- `tasks/strain-splice-host-*`
- `tasks/evidence-fragments/SSH6.8.md`
- `tasks/summoner-convergence-lane-c-ledger.jsonl`

## Off limits

`tests/**` (run them, do not edit — especially `gk-core/tests/FusionRpg.Core.Tests`
root helpers owned by the keepverse L3b slice landing in parallel), the rest
of `src/**`, `gk-data/packs/fusion/data/seed/**` generated trees (never hand-edit; regenerate),
keepverse and content-stack todos/ledgers, `tasks/reports/**`, other lanes'
files. One commit for the publish (code + evidence + ledger + ticked row
together). Commit nothing yourself, push nothing, create no branches — leave
the tree dirty; the orchestrator harvests and commits.

## Definition of done

1. WIP `16c578342` adopted (all 11 files present with their content).
2. SSH6.5 + SSH6.7 verified met (command + numbers) or named unmet as THE
   blocker with the exact failing line.
3. SSH6.8 published in one commit-shaped change: `sockets` v3 `comboPricing`
   + report provenance + BalanceGuard test green; row ticked with
   `tasks/evidence-fragments/SSH6.8.md`.

## Verification

- `git log --oneline -3` and `git show 16c578342 --stat` — confirm what you adopt first.
- The exact verify commands SSH6.5/SSH6.7/SSH6.8 name (run them verbatim).
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/run-guards.ps1 -Tier ci` — read the printed counts, not the exit code.

## Report

End your last message with the `<<<REPORT {...} REPORT>>>` block
(status/summary/changed_files/commits/verification/unproved), and every claim
in it must already be a change in this worktree.
