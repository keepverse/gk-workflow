# BCU4.2 — `creature-progression` D2.3: the blocker was a stale premise; re-checked and routed

The row was marked blocked because D2.2 looked incomplete — three unchecked boxes in
`creature-progression-todo.md`. A box is not evidence. Read the code: **D2.2 is done-in-code**, so
D2.3 is unblocked, its already-shipped clause is green, and the residual is the owning program's.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| D2.2 criterion 1, checked in code | `sed -n '328,340p' gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs` | `:332-336` — *"Expedition rewards level the specimen only; species progression is awarded by its own general-spawn activity projector"* | `RpgStore.Expeditions.cs` |
| D2.2 criterion 2 | same block | `:330` calls `TryRollActionUnlocks(..., tx)` inside the reward transaction | same |
| D2.2 criterion 3 | `rg -n "INSERT OR IGNORE INTO rpg_xp_ledger" gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Progression.cs` | `:284`; the species row is discovery-only, deduped on `species:{id}` at `RpgStore.Expeditions.cs:347-355` | those two files |
| Stale boxes corrected | `git diff tasks/creature-progression-todo.md` | D2.2's header → done-in-code, 3 boxes ticked with citations; D2.3's header → unblocked, clause 2 ticked with its guards named | `tasks/creature-progression-todo.md` |
| D2.3 clause 2 is already enforced | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~ProgressionLayerSelectorGuard\|FullyQualifiedName~SpeciesAllocationSeam"` | **Passed — 6/6** | `ProgressionLayerSelectorGuardTests.cs`, `SpeciesAllocationSeamTests.cs` |
| Residual stays with its owner, named | `git diff tasks/creature-progression-todo.md` | D2.3 clauses 1 and 3 marked *remaining*, with the reason (they span `gk-core/src/FusionRpg.Data/**` / `gk-core/src/FusionRpg.Server/**`, outside this lane's fence) | same file |
| `verify-change.ps1` | `pwsh -NoProfile -Command "& './scripts/verify-change.ps1' -Paths @('tasks/creature-progression-todo.md','tasks/backlog-clean-up-todo.md') -Session bcu8"` | see commit body | — |

No code changed. This is the fourth stale premise this run found by reading code instead of a status
line (after the P11 gate, the naming-grammar "NOT-BUILT" row, and the `cmdc/lane-c` fence) — worth the
manager's attention as a class, not four coincidences.
