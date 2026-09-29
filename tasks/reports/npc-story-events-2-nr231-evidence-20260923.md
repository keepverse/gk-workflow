# Evidence — npc-story-events NR2.31 (the `anomaly` allow-list, catalog half)

Lane `npc-story-events-2`, worktree `.claude/worktrees/cmdc-npc-story-events-2`, branch
`cmdc/npc-story-events-2` (integration head merged this segment). Program `npc-story-events`; row
`tasks/npc-story-events-todo.md` NR2.31; spec `spec-world-anomaly-sites.md` §1, §3, reviewed with world-map-program,
which owns `SectorTypeCatalog`.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `anomaly` is allowed on exactly the three reviewed types, with the reason recorded per type | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --nologo --verbosity quiet --filter "FullyQualifiedName~AnomalySiteTests"` | `Failed: 0, Passed: 6, Total: 6` (42 ms) — the set is asserted equal to `barren`, `nexus`, `storm`; `stable` and `boss-lair` keep `vault` and gain no second study site | `gk-core/src/FusionRpg.Core/World/SectorTypeCatalog.cs` |
| A `stable` sector with an `anomaly` slot is refused by `WorldValidation` | same run (`A_stable_sector_with_an_anomaly_slot_is_refused_by_validation`) | pass — `InvalidOperationException` naming the sector id and `anomaly`; the same edit on a `barren` sector validates (the positive control) | same |
| The list is validation only: every existing world test and golden is byte-identical | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --nologo --verbosity quiet` | `Failed: 0, Passed: 9588, Total: 9588` (1 m) — the whole project, world goldens included | — |
| No shipped template places an `anomaly` slot yet (measured, not assumed) | same filtered run (`No_shipped_template_places_an_anomaly_slot_yet`) | pass for both templates; the template half is NR2.32 | same |
| The two cross-project readers of `SectorTypeCatalog` still pass | `dotnet test gk-core/tests/FusionRpg.Core.Items.Tests -c Release --nologo --verbosity quiet` · `dotnet test gk-core/tests/FusionRpg.Server.Tests -c Release --nologo --verbosity quiet --filter "FullyQualifiedName~World"` · `dotnet test gk-core/tests/FusionRpg.Data.Tests -c Release --nologo --verbosity quiet --filter "FullyQualifiedName~LoamPersistence"` | `Failed: 0, Passed: 1468, Total: 1468` (7 s) · `Failed: 0, Passed: 93, Total: 93` (14 s) · `Failed: 0, Passed: 2, Total: 2` (357 ms) | — |
| No overflow in the touched file | `python gk-core/scripts/audit-overflow.py` | `total 0 finding(s), 0 critical` | — |

**Printed readings, in full:**

- `pwsh … scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/World/SectorTypeCatalog.cs','gk-core/tests/FusionRpg.Core.Tests/World/AnomalySiteTests.cs') -AllowUnscoped -PlanOnly` → both paths resolve to `core-fallback` / `core-tests-fallback` (module), i.e. the registry's own selection for them is the whole 67-project `core`
  group. The evidence above ran the primary project in full plus every other project that references `SectorTypeCatalog`
  (found by `grep -rln "AllowedSlotTypes\|SectorTypeCatalog" tests/`, excluding `obj`/`bin`) instead of the group in one
  pass; the remaining core projects cannot read the list (they do not reference it).
- A correction rides in this segment as its own commit (`a60b4b187`): NR2.19's expedition tuning shape change had left
  **two forked copies** of `ContractTuningTestBootstrap.cs` (`gk-core/tests/FusionRpg.Data.Tests`, `gk-core/tests/FusionRpg.E2E.Tests`)
  constructing the old record, so both projects stopped compiling on the merged head. Fixed by mirroring the same four
  danger bands and the encounter block; measured, `gk-core/tests/FusionRpg.Data.Tests` builds again (2/2) and
  `gk-core/tests/FusionRpg.E2E.Tests` builds with `0 Error(s)`.

**NOT proved / named deviations.**

- **The row's own Verify line is run renamed.** `-Session <sid>` cannot resolve in this lane (no session record;
  `tasks/sessions/**` is outside its allowed paths), so the plan call passes `-AllowUnscoped`.
- **The `core` group was not run as one pass** — see the printed plan above; the three projects that can read the
  catalog were run in full instead. The registry's `core-fallback` row is the defect the plan's NR0.2 owns and it
  predates this row.
- **The template half (NR2.32) is not touched**: no template places an `anomaly` slot, which is asserted by the new
  test so a later placement cannot silently ride in on this row.
- No server was started and no live probe was run.
