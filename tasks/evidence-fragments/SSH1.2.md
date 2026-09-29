# SSH1.2 — `host-gate` b: fix first (F5) — one host builder `SocketHostFor`

Task: tasks/strain-splice-host-todo.md SSH1.2 · spec: docs/architecture/strain-splice-host/spec-host-gate.md §3

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `RpgStore.SocketHostFor(instanceId, socketMaxFor)` extracted from `RpgStore.ItemCard.cs`'s own inline host construction; `ItemSurfaceEndpoints.cs:183` calls it; hard-coded `ArmamentPrimary`, empty frame, set flag deleted | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~SocketHostFor"` | exit=0 :: 3 passed | `RpgStore.ItemCard.cs`, `ItemSurfaceEndpoints.cs` |
| `the_combinations_endpoint_reads_the_real_role_frame_and_set_flag`: a core-guard humanoid host previews a core-guard-pinned Splice as reachable, and a set piece never previews a Strain | same file, both new HTTP-level tests | passed | `SocketHostForTests.cs` |
| Regression: item card, insert-element, gem-tier, preview endpoints | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~ItemInsertElement\|~ItemCardEndpoints\|~SocketHostFor\|~GemTier\|~ItemPreviewEndpoints"` | exit=0 :: 52 passed | — |
| Verification boundary | `verify-change.ps1 -PlanOnly` | `RpgStore.ItemCard.cs` -> `data-item-card` (focused, `data.item-card`) + `guard-dal`/`guard-test-substrate`; `ItemSurfaceEndpoints.cs`/`SocketHostForTests.cs` -> broad server fallback | — |
| Full Server.Tests | `dotnet test gk-core/tests/FusionRpg.Server.Tests -c Release` | exit=0 :: 584/584 | — |
| Scoped Data.Tests (`data.item-card`) | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "VerificationId=data.item-card"` | exit=0 :: 23/23 | — |
| Guards | `guard-dal.ps1`; `guard-test-substrate.py` | both clean | — |
| Audits | `audit-overflow.py --targets <2 files>`; `audit-magic-numbers.py --targets <2 files>` | both clean, 0 findings | — |
| Full Data.Tests (informational — beyond the scoped boundary above) | `dotnet test gk-core/tests/FusionRpg.Data.Tests -c Release` | 1626/1627 — the ONE failure (`CreatureSpeciesImportCliTests.A_real_import_against_the_real_committed_tree_succeeds_and_writes_a_real_store`) is confirmed, isolated re-run, unrelated: `gk-data/packs/fusion/data/generated/creatures` is 11 species stale against its own source tree, a generator-drift defect in an unrelated subsystem this task never touches (no creature/species file appears in this task's diff). Not this task's to fix. | — |

## The real defect, proven live

`ItemSurfaceEndpoints.cs`'s `/api/items/{instanceId}/combinations` route built its `SocketHost` with
`new SocketHost(instance.ContainerId, ItemRole.ArmamentPrimary, "", slots.Count)` for EVERY item,
regardless of the item's real role, frame, or set membership — while `RpgStore.ItemCard.cs`'s own item
card built the real one, separately. A helm previewed a weapon's own role-pinned Strains/Splices as
reachable and never applied D21's set-piece exclusion to any real item. `SocketHostForTests.cs` drives
this live through the real HTTP route: a `core-guard`-pinned Splice, unreachable under the old
hard-coded host, now fires (`Active`) on a real `core-guard` item; the identical fully-satisfied Strain
that would be `Active` on any ordinary host (proven by the sibling test on the same fill) is completely
absent from a real set piece's response — `Active` bypasses the compendium's reveal rule entirely
(`CompendiumReveal.Render` never gates it on held stock), so the only way it renders is if D21's
exclusion never reached the evaluator, and the only way it is absent is if it did.

## `SocketHostFor` is self-contained by design

Its signature is `(string instanceId, Func<string,int?> socketMaxFor)` — no corpus delegate. It reads
`GetItemGeneration(instanceId)` for the mint-time-fixed role and frame (the same base type a corpus's
`LookupBaseType` would resolve, but off SQL alone), `GetSockets(instanceId)` for the real socket count,
and `ListSets()` for D21's set-piece flag. This lets `ItemSurfaceEndpoints.cs` — which had no corpus
delegate on hand at all — build a fully real host with nothing but the instance id.

## `socketMaxFor` is a named, honest stub for now

SSH1.3 is where `SocketHost.Capacity` is added and where `SocketHostFor` starts actually reading
`socketMaxFor` (per spec §2/§3, filled from `BaseTypeSocketMaxCorpus`'s lookup). Neither SSH1.2's nor
SSH1.3's own Files list touches `Program.cs`, yet `BaseTypeSocketMaxCorpus.Load`'s only existing call
site (`Program.cs`, inside the workbench's own `if (recipeCatalog is { } workbenchRecipes)` block) is
out of scope for `ItemCardEndpoints`/`ItemSurfaceEndpoints`'s own registration — a real, if minor,
pre-existing wiring gap the plan's Files lists did not name. Since `socketMaxFor` has NOTHING to do
yet (`Capacity` does not exist on `SocketHost` until SSH1.3), passing `_ => null` at both new call sites
is behaviourally identical to any other value today, and is documented at both sites as a deliberate,
temporary stub — not a silent gap. **Flagged for SSH1.3**: hoisting `socketMaxForBaseType`'s
declaration out of the workbench's own `if` block (matching `gemInserts`'/`itemBaseTypes`' own
top-level placement) is the real remaining step to give it a genuine value; SSH1.3 is where that stops
being free to defer, since `Capacity`'s own construction invariant (`0 <= SocketCount <= Capacity`)
is meaningless against a lookup that always returns null.

## Test file location

The todo's own Files line names `gk-core/tests/FusionRpg.Server.Tests/ItemPreviewEndpointsTests.cs`, which
tests a DIFFERENT route entirely (the unsaved-item atom preview, `item-content` module T8) and contains
no reference to `/combinations`, `SocketHost`, or `MapItemSurfaces`. The real existing test for this
route is `ItemInsertElementTests.cs` (confirmed via `grep` for `/combinations`/`CombinationRowDto`
before writing anything) — the new tests live in a new file, `SocketHostForTests.cs`, alongside it,
following the actual shipped convention over the todo's stale path (the same correction T45 made
earlier this program for its own test file).

## Status

All SSH1.2 acceptance criteria met. Ledger marked done; todo checkbox ticked.
