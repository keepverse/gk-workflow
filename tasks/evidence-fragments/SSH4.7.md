# SSH4.7 — the read side recognises combo bindings per host: **IMPLEMENTED, ROW OPEN on its test**

Landed: `EquippedBoundAtoms.InputsFromStore` now recognises a combination binding.

- A binding whose `InstanceId` starts `cmb:` is checked against the host's **current** targets, resolved
  through the SAME evaluator the projection uses (`store.ComboTargetsFor(hostRef, hostSockets)` — the
  read side never re-folds a combination; `guard-actor-hub.ps1` is green).
- A recognised target contributes `EquippedAtomInput(role, hostRef, atom, SocketIndex: null,
  ComboId: result.ComboId, Circuit: result.Circuit)`, which `EquipAtomSource.MintSourceId` renders as
  `combo:{role}:{host}:{comboId}#c{circuit}` (SSH4.5's arm).
- A `cmb:` binding with NO current target contributes nothing (`continue`) — the stale-binding rule.
- `RpgStore.ComboTargetsFor(hostInstanceId, slots)` is now public (was assignment-shaped); the projector
  wiring passes `(a, slots) => ComboTargetsFor(a.RefId, slots)`.

| Criterion | Command | Result |
|---|---|---|
| the row's verify line | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~ItemEquipEndpoints"` | **34 passed / 0** |
| ActorHub boundary | `pwsh -NoProfile -File scripts/guard-actor-hub.ps1` | ACTOR-HUB GUARD OK |
| scoped verifier | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Server/EquippedBoundAtoms.cs','gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EquipCombinations.cs','gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Items.cs') -Session strain-splice-host-20260922"` | **exit 0** — DAL OK, test-substrate OK, Server.Tests 799/0 |

## DONE — the Server test landed, and the fixture obstacle is named

`A_combo_binding_is_recognised_per_host_with_its_circuit_and_a_stale_one_is_not` drives
`EquippedBoundAtoms.InputsFromStore` over a real bound combination: the combo input is recognised with
its `ComboId`, `Circuit` 0, the host's role and the host as `ItemRefId`; emptying the socket leaves no
combo input at all.

**Root cause of the earlier null generation (now known, and worth keeping):** `SeedItem` in that file
reuses ONE manifest id (`"eq-drop"`) for every item it seeds, so only its FIRST call's
`item_generation` row is written — `GetItemGeneration(_helmId)` is null and `SocketHostFor` never
resolves a host there. The test seeds its own host with a unique manifest id (`combo-read-drop-{instance}`),
which is the fix, local to the test.

| Criterion | Command | Result |
|---|---|---|
| the row's verify line | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~ItemEquipEndpoints"` | **35 passed / 0** |
| ActorHub boundary | `pwsh -NoProfile -File scripts/guard-actor-hub.ps1` | ACTOR-HUB GUARD OK |
| scoped verifier | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Server/EquippedBoundAtoms.cs','gk-core/tests/FusionRpg.Server.Tests/ItemEquipEndpointsTests.cs') -Session strain-splice-host-20260922"` | **exit 0** — DAL OK, Server.Tests 800/0 |

**Row CLOSED.** `SSH4.8`, `SSH4.9` and `SSH5.9` remain.
