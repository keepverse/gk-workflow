# Close-out: the lane's filed findings, the three reachable checkpoints, and the Landing numbers

Lane `cs-rank` (session `creature-seed-rank`, branch `cmdc/cs-rank`), 2026-09-23, at the integration tip
`d4ec51ffd` (merged forward this segment). No production code changed in this increment: it converts
already-verified state into ticked rows, each with its own fresh command, and closes the three findings this
lane filed or re-confirmed. The checkpoints that cannot pass yet are named at the bottom with exactly what
blocks each.

| Row / checkpoint | Command run now | Result |
|---|---|---|
| **CS-R2** — ci-tier `population-pin` red on `ActionUnlockGrantServiceTests.cs:220` | `python gk-core/scripts/guard-population-pin.py` | **`total 0 finding(s)`** — fixed at the tip by the owning lane (`c9af301b2`); the row is closed and the file was never this lane's |
| **TVB-F22** row (the same defect as this lane's CS-R1, filed independently by `test-verification-boundary`) | `python gk-core/scripts/guard-verification-boundaries.py` and `verify-change.ps1 -Paths gk-core/data/tuning/creature-rank.v1.json --plan-only -AllowUnscoped` | **`VERIFICATION BOUNDARY GUARD OK`** and the plan reads **`creature-rank-tuning (module)`** — closed by the manager's `67abbcefb` |
| **CS-R3** — action-layer purity red on `Cost/ExhaustionEdgeDetector.cs:85` | `dotnet test gk-core/tests/FusionRpg.Core.Tests --nologo --verbosity quiet` after merging the owning lane's fix | **EXIT=0 — 9705 passed / 0 failed, 1 m 17 s**, with `ActionsPurityGuardTests` green inside it. The lawn lane's `497bfa182` replaced `WindowCount`'s `.Values` enumeration with `TrackedActors => _byPtr.Count`. Row closed. |
| **Checkpoint: Seed side** | Task 4's own evidence (`tasks/reports/creature-seed-rank-t4.md`) | 904/904 anchors carry the table's rank; a second `creatures run refresh-rank` reports 0 changes and the tree sha256 `cd1ffeb4…` is unchanged; the 549-file diff was reviewed with 0 unexpected differences. Ticked. |
| **Checkpoint: Flow** | Tasks 5-7's evidence (`-t5.md`, `-t6.md`, `-t7.md`) + the sharded Data run | Committed-tree path carries rank (T5 field, T6 `Canonical` + optional read, proven over the real 904-file tree); store-backed path carries it (T7 nullable column, null-safe read-back, `SameContent`, `CreatureSpeciesDef`, Mapper); Core green across all three and Data green through `verify-change` (4 shards, 1732 tests at that point, exit 0). Ticked. |
| **Checkpoint: Landing** | the four commands below | all green — ticked (see the table) |

| Landing prerequisite | Command run now | Result |
|---|---|---|
| Full Core suite | `dotnet test gk-core/tests/FusionRpg.Core.Tests --nologo --verbosity quiet` | **EXIT=0 — Passed! Failed 0, Passed 9705, Skipped 0, Total 9705, 1 m 17 s** |
| Full Data suite | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Species.cs','gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Fusion.cs','gk-core/tests/FusionRpg.Data.Tests/SpeciesImportStoreTests.cs','gk-core/tests/FusionRpg.Data.Tests/FusionStoreTests.cs') -Session creature-seed-rank"` | **EXIT=0 — `TEST-SHARDED OK: 4 shards, 1752 tests, no overlap`** (every shard exit 0) |
| Full Guard tier | `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci` | **EXIT=0 — `GUARDS OK - 25 guard(s) run, 0 red`** |
| audit-magic-numbers | `python gk-core/scripts/audit-magic-numbers.py` | **M1=0 M2=0 M3=0 M4=0, total 0 finding(s)** |
| Zero golden moves | `dotnet run --project gk-forge/tools/CreatureSpeciesGen -- --check` | **`--check: clean, 904 species match`** — the concrete tree still matches its generator; the expedition tier goldens were proven unchanged by Task 10, and no test golden moved in any of this lane's increments |

## Still-open acceptance checkpoints — exactly what blocks each

- **Checkpoint: Complete** (`All acceptance criteria met; all suites green; ready for review`) — **not
  ticked.** Tasks 8, 9 and 12 are open on denied paths, all three re-proven this segment with
  `path is outside session scope (creature-seed-rank)`: `gk-core/src/FusionRpg.Server/CreatureEndpoints.cs`
  (T9's payloads), `gk-core/src/FusionRpg.Server/FusionEndpoints.cs` (T8's preview parity, plus the boots'
  `CreatureRankFloors.Configure` wire in Server/Injector for T8/T10/T11/T12) and
  `gk-core/src/FusionRpg.Contracts/CreatureDtos.cs` (the `CreatureProfileDto` field T9 needs). TB-H1's box 3
  belongs to `party-dungeon`'s own six-domain run. No amount of in-fence work can tick this checkpoint.

## Process note

Nothing outside `tasks/**` changed in this increment, so the commands above are its entire verification, and
each is the row's or the checkpoint's own nominal command. `gk-core/tests/FusionRpg.Core.Tests` is the *residual*
Core project; the split per-subsystem projects run in CI and through `verify-change`'s group run.
