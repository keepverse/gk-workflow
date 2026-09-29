# Lane brief — `ssh27c` (opencode continuation of `ssh27b`, SSH6.8 publish)

## Why this lane exists

`ssh27b` did the analysis (SSH6.5/SSH6.7 code-present, evidence fragment
`tasks/evidence-fragments/SSH6.8.md` drafted) and stopped on two true blocks:
this runtime has no shell, and its fence denied the BalanceGuard test path.
This lane inherits its tree (`--base opencode/ssh27b`), carries the widened
fence, and works under the no-shell protocol below.

⛔ Read `docs/DESIGN-GATE.md` §1 first and the documents its row names, in this
session, then verify against code. A comment is not evidence; open the file.

## No-shell protocol (binding — this runtime's bash refuses)

- You CANNOT run anything: no `dotnet`, no `pytest`, no `npm`, no `git`.
  Do all file work; for every gate, quote the EXACT command the orchestrator
  must run and mark it `UNPROVED-BY-LANE`.
- Never claim a run you did not make. A claim without a lane-run command is
  not evidence — it is a request for the orchestrator, labeled as such.
- The orchestrator runs verification manager-side and harvests. Your REPORT's
  `verification` section lists commands for the orchestrator, each tagged
  `UNPROVED-BY-LANE` unless you literally ran it (you cannot — so tag all).

## Goal

Close `tasks/strain-splice-host-todo.md` **SSH6.8** in ONE commit-shaped
change: publish `sockets` v3 `comboPricing` with the passing report's
provenance, plus the BalanceGuard test.

## Handover facts (already verified — confirm by read, do not re-derive)

- Merged `6fd030b4`: SSH5.10/5.11/6.1 reviewed at `4e94fd92`, merge `e78f4a12`,
  union-artifact fix `06a7c452`.
- SSH6.2/6.3/6.4 ticked done (evidence fragments exist). Verify SSH6.5/SSH6.7
  BY READ against their rows; if either is unmet, STOP and report it as the
  blocker instead of publishing. (`ssh27b` found both code-present; confirm.)
- Inherited tree already contains: the 11 WIP files from `16c578342`
  (Core Items tuning, Server `Program.cs`, `SocketMaxCheck.cs`, items
  adapters, `test_combogen.py`, 1 cross-program ledger line — rides along
  untouched) + the drafted `tasks/evidence-fragments/SSH6.8.md`.
- No hard progression ceilings; `long` + `checked`; tuning in `gk-core/data/tuning`,
  never code; never hand-edit generated trees.

## Allowed paths

- `gk-core/src/FusionRpg.Core/Items/**`
- `gk-core/src/FusionRpg.Server/Program.cs`
- `gk-forge/tools/ItemSeedValidator/**`
- `gk-forge/tools/seedsmith/seedsmith/adapters/items/**`
- `gk-forge/tools/seedsmith/tests/test_combogen.py`
- `gk-core/tests/FusionRpg.Core.Balance.Tests/**`
- `data/tuning/socket*.json`
- `data/tuning/sockets*.json`
- `docs/architecture/strain-splice-host/**`
- `tasks/strain-splice-host-*`
- `tasks/evidence-fragments/SSH6.8.md`
- `tasks/summoner-convergence-lane-c-ledger.jsonl`

## Off limits

`tests/**` outside `gk-core/tests/FusionRpg.Core.Balance.Tests/**` (especially
`gk-core/tests/FusionRpg.Core.Tests` root helpers owned by the keepverse L3b slice),
the rest of `src/**`, `gk-data/packs/fusion/data/seed/**` generated trees, keepverse and
content-stack todos/ledgers, `tasks/reports/**`, other lanes' exact files
(see `cs-rank-b` brief's list — symmetric). One commit-shaped change (code +
evidence + ledger + ticked row). Commit nothing, push nothing, create no
branches — leave the tree dirty.

## Definition of done

1. Inherited files confirmed present by read (11 WIP + evidence draft).
2. SSH6.5 + SSH6.7 confirmed met BY READ (file:line per acceptance) or named
   unmet as THE blocker.
3. SSH6.8 publish complete in-tree: `sockets` v3 `comboPricing` + report
   provenance + BalanceGuard test authored; row ticked;
   `tasks/evidence-fragments/SSH6.8.md` final with orchestrator-run commands
   tagged `UNPROVED-BY-LANE`.

## Verification (orchestrator-run; quote verbatim, tag UNPROVED-BY-LANE)

- The exact verify commands SSH6.5/SSH6.7/SSH6.8 name.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/run-guards.ps1 -Tier ci` — orchestrator reads the printed counts.

## Report

End your last message with the `<<<REPORT {...} REPORT>>>` block
(status/summary/changed_files/commits/verification/unproved), and every claim
in it must already be a change in this worktree; every gate tagged
`UNPROVED-BY-LANE`.
