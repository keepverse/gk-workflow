# Lane brief — `cs-rank-b` (opencode continuation of `cmdc/cs-rank`, Tasks 8/9/12 caller wires)

## Why this lane exists

`cmdc/cs-rank` (pi, 31 segments) landed every in-fence half and stopped at
three denied-path blockers it named exactly. The owner granted the fence
(2026-09-23): `gk-core/src/FusionRpg.Server/**` + `gk-fusion/src/FusionRpg.Injector/**` +
`gk-core/src/FusionRpg.Contracts/**`. Its worktree is adopted as `1577091a6` on
`cmdc/cs-rank`. Do NOT re-land the in-fence halves; close the three rows.

⛔ Read `docs/DESIGN-GATE.md` §1 first and the documents its row names, in this
session, then verify against code. A comment is not evidence; open the file.

## Goal

Close `tasks/creature-seed-todo.md` Tasks 8, 9, 12 by landing exactly the
wires the rows name as blockers. Evidence so far lives in
`tasks/reports/creature-seed-rank-t8.md`, `-t9.md`, `-t12.md` — read all three
before touching the tree.

## The three wires (one per row, each independently provable)

### Task 8 — Fusion preview parity + boot wire
- `gk-core/src/FusionRpg.Server/FusionEndpoints.cs`: the two preview sites call
  `CreatureRankFloors.Passes(<gate>, CreatureSpeciesCatalog.Get(speciesId)?.Rank)`.
- Boot: one host calls
  `CreatureRankFloors.Configure(CreatureRankTuningLoader.Parse(…))` at boot
  (Server or Injector — say which and why); a floor above bottom must have
  production effect. Missing gate refused at `Configure`, never defaulted.
- Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Fusion"`; behavior identical to pre-rank.

### Task 9 — Display payloads + quality line
- `gk-core/src/FusionRpg.Server/CreatureEndpoints.cs` + `gk-core/src/FusionRpg.Contracts/CreatureDtos.cs`:
  catalog projection and roster/codex/summon/preview payloads carry rank id +
  display name (copy from the catalog file). `RpgStore.Creatures.cs` is
  already in fence for the store half.
- `gk-forge/tools/CreatureQualityReport/**`: rank-coverage line + explicit
  `ReportDiversity("rank", …)` dimension (measured `grep -c rank` = 0 — the
  diversity section does NOT read the tuning vocab generically).
- Verify: endpoint payload checks; `dotnet run --project gk-forge/tools/CreatureQualityReport`.

### Task 12 — Cage caller wire
- The Delve wild endpoint under `gk-core/src/FusionRpg.Server/**` passes a rank into
  `Cage.OccupantEligible` (REQUIRED `CreatureRank?` already landed); pricing
  stays rank-blind (rarity-keyed).
- Verify: focused Delve/wild tests green + pass-through proof.

## Allowed paths

- `gk-core/src/FusionRpg.Core/**`
- `gk-core/src/FusionRpg.Data/**`
- `gk-core/src/FusionRpg.Server/**`
- `gk-fusion/src/FusionRpg.Injector/**`
- `gk-core/src/FusionRpg.Contracts/**`
- `gk-forge/tools/seedsmith/**`
- `gk-forge/tools/CreatureQualityReport/**`
- `tests/**`
- `gk-data/packs/fusion/data/seed/creatures/**`
- `gk-core/data/tuning/**`
- `tasks/creature-seed-todo.md`
- `tasks/creature-seed-ledger.jsonl`
- `tasks/reports/creature-seed-*`

## Off limits (other running lanes' exact files — never touch)

- `tasks/keepverse-split-todo.md`, `tasks/keepverse-split-ledger.jsonl`,
  `tasks/content-stack-todo.md`, `tasks/content-stack-ledger.jsonl`
  (findings-2b), and any `gk-core/tests/FusionRpg.Core.Tests` root-helper file it edits.
- `gk-core/src/FusionRpg.Core/Delve/Encounter/EncounterPreflight.cs`,
  `gk-core/tests/FusionRpg.Core.Tests/Delve/Domains/DomainEncounterPreflightBridgeTests.cs`,
  `gk-core/tests/FusionRpg.Core.Tests/Delve/Encounter/EncounterPreflightTests.cs`,
  `tasks/party-dungeon-todo.md`, `tasks/party-dungeon-ledger.jsonl` (pd-d3b).
- `gk-core/src/FusionRpg.Core/Items/Sockets/StrainSpliceTuning.cs`,
  `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py`,
  `gk-forge/tools/seedsmith/tests/test_combogen.py` (ssh27b).
- `gk-core/tools/ip-censor/**`, `tasks/ip-censor-*` (ipc-3b).
- Never widen a guard, never add a `knownRed`, never pin a population count.
  Commit nothing, push nothing, create no branches — leave the tree dirty; the
  orchestrator harvests.

## Definition of done

1. WIP `1577091a6` adopted (all 15 files present with their content).
2. Tasks 8, 9, 12 ticked with evidence fragments (exact command text +
   printed numbers); each wire proved by its row's Verify line, not by
   association with the landed halves.
3. No golden moves (`CreatureSpeciesGen --check` clean); guards green.

## Verification

- `git log --oneline -3` and `git show 1577091a6 --stat` — confirm what you adopt first.
- Each row's Verify line, verbatim from the row.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/run-guards.ps1 -Tier ci` — read the printed counts, not the exit code.

## Report

End your last message with the `<<<REPORT {...} REPORT>>>` block
(status/summary/changed_files/commits/verification/unproved), and every claim
in it must already be a change in this worktree.
