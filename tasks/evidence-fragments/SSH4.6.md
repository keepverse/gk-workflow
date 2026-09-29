# SSH4.6 — the arm-2 projection bind: **CORE SEAM LANDED, ROW STILL OPEN**

Landed (this commit): the projector's half of spec-combo-bind §2.

- `ComboBindTarget(CombinationResult Result, int Circuit, string ComboInstanceId)` and
  `ComboBindTargets.InstanceId(hostInstanceId, circuit, containerId)` = `cmb:{host}#c{circuit}:{containerId}`
  in `gk-core/src/FusionRpg.Core/Items/EquipProjector.cs` — one place the id's shape lives.
- `EquipProjector` gains the optional `combosOf(EquipAssignment, IReadOnlyList<SocketSlot>)` delegate and
  adds one `EquipAssignment(host role, rolled, ComboInstanceId)` per target **after** the insert bindings,
  for the same reason the inserts do: `ApplyEquipProjection` reaps any binding the desired set omits.
  ⛔ No per-actor count (R12): every target binds; the only "at most one" is one identity per circuit,
  enforced inside the evaluator.

| Criterion | Command | Result |
|---|---|---|
| projection contract | `dotnet test gk-core/tests/FusionRpg.Core.Items.Tests --filter "FullyQualifiedName~EquipProjectionSockets"` | **11 passed / 0** (6 pre-existing + 5 new) |
| new tests | (above) | `a_firing_strain_binds_its_container_through_the_projection`, `every_firing_combination_binds_with_no_actor_wide_count` (8 targets → 9 bindings, nothing suppressed), `reprojecting_unchanged_state_writes_no_new_instance` (id is content-derived), `binding_set_is_independent_of_loadout_iteration_order`, `unequipping_the_host_withdraws_the_combination` (no assignment → the evaluator is never consulted) |

**NOT done — the row stays OPEN.** No production host reaches the seam: `RpgStore.MaterializeRolledEquipRuntime`
still constructs the projector without `combosOf`, and `Instantiator.TryInstantiate` is never called on a
combo container. Remaining work, read from the spec and the call sites:

1. `MaterializeRolledEquipRuntime` (and its commander twin) gains a `combosOf` parameter, passed to the
   projector; the Server supplies it because it owns the catalog + tuning.
2. The Server's `combosOf` needs `SocketTuning` + the gem insert lookup, neither of which
   `ItemEquipService`/`WebMatchService` hold today (`ItemSurfaceEndpoints.cs:192-206` already has the
   evaluate pattern: `GetComboRecipes()` + `SocketHostFor` + `InsertOf`); thread them through
   `ItemEquipService`'s construction (`Program.cs:1184`) and `WebMatchService`.
3. Ensure the instance exists: `Instantiator.TryInstantiate` on the built combo container (zero pool
   rolls), then `SaveInstance`, before `ApplyEquipProjection`.
4. The Data-level acceptance tests (`the_host_fingerprint_is_unchanged_by_binding`,
   `removing_one_ingredient_withdraws_the_combination`) belong with that wiring.

`SSH4.7`, `SSH4.8`, `SSH4.9` and `SSH5.9` all sit on this caller and are not started.

## 2026-09-22 (same lane) — the PRODUCTION CALLER is wired

- New `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EquipCombinations.cs`: `EquipCombinationInputs(SocketTuning,
  LookupInsert)`, `UseEquipCombinationEvaluation` (boot-set, idempotent, unset = the pre-SSH4.6 shape)
  and `ComboTargetsFor(assignment, slots)` — builds the fills from the host's own socket rows, runs the
  ONE evaluator over the ONE catalog, and ensures each target's container instance with
  `Instantiator.TryInstantiate` (zero pool rolls, `InstanceOrigin.Craft`) before the projection binds it.
- `RpgStore.MaterializeRolledEquipRuntime` passes `combosOf: ComboTargetsFor`.
- `Program.cs` sets the inputs at boot from the same `socketTuning` + `itemCardCorpus.LookupInsert` the
  card path uses, so a host's combinations evaluate against exactly the corpus the card renders.

| Criterion | Command | Result |
|---|---|---|
| Core projection contract | `dotnet test gk-core/tests/FusionRpg.Core.Items.Tests --filter "FullyQualifiedName~EquipProjectionSockets"` | **11 passed / 0** |
| Data projection contract | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~EquipProjectionSockets\|FullyQualifiedName~EquipRuntimeStore"` | **10 passed / 0** |
| ActorHub boundary | `pwsh -NoProfile -File scripts/guard-actor-hub.ps1` | ACTOR-HUB GUARD OK |
| single-writer boundary | `pwsh -NoProfile -File scripts/guard-single-writer.ps1` | SINGLE-WRITER GUARD OK |

**STILL OPEN — two acceptance tests, and they need a fixture the Data tests do not yet build:**
`removing_one_ingredient_withdraws_the_combination` and `the_host_fingerprint_is_unchanged_by_binding`.
Both drive `MaterializeRolledEquipRuntime` over a real host, and `RpgStore.SocketHostFor` requires an
`item_generation` row (`RpgStore.ItemCard.cs:404`) which the existing Data fixture never saves — the
Server's `SocketHostForTests.SeedItem` has that plumbing and is the shape to copy. Until those land, the
caller is wired and reachable but the rows' Data-level acceptance is unproven. `SSH4.7`, `SSH4.8`,
`SSH4.9` and `SSH5.9` follow.

## 2026-09-22 — DONE: the two Data acceptance tests, and the whole verify line green

Ported `SocketHostForTests.SeedItem`'s `item_generation` plumbing into the Data fixture (`RpgStore.SocketHostFor`
returns null without a generation row — `RpgStore.ItemCard.cs:404`), then added three Data tests that enter
through the REAL store method:

- `A_firing_strain_binds_its_container_through_the_data_projection` — a socketed host whose fill satisfies a
  seeded Strain binds `cmb:{host}#c0:combo.strain-combo-probe-t1` at the host's role.
- `Removing_one_ingredient_withdraws_the_combination` — the socket is emptied, the next projection produces
  no target, and the reaper withdraws the binding in the same reconcile.
- `The_host_fingerprint_is_unchanged_by_binding` — `ContentFingerprint()` is identical before and after the
  bind (a combination binds; it never rewrites the host).

| Criterion | Command | Result |
|---|---|---|
| the whole verify line | `dotnet test gk-core/tests/FusionRpg.Core.Items.Tests --filter "FullyQualifiedName~EquipProjectionSockets"` | **11 passed / 0** |
| | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~EquipProjectionSockets\|FullyQualifiedName~EquipRuntimeStore"` | **13 passed / 0** |
| | `pwsh -NoProfile -File scripts/guard-actor-hub.ps1` | ACTOR-HUB GUARD OK |
| | `pwsh -NoProfile -File scripts/guard-single-writer.ps1` | SINGLE-WRITER GUARD OK |
| | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @(<6 paths>) -Session strain-splice-host-20260922"` | **exit 0** — Core.Items.Tests 1402/0, Server.Tests 799/0, all guards green |

**Row CLOSED.** `SSH4.7`, `SSH4.8`, `SSH4.9` and `SSH5.9` are the remaining strain-splice-host work.
