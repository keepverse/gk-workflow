# SSH4.8 — every trigger refreshes the binding set: **MECHANISM LANDED, ROW OPEN on its three tests**

- `RpgStore.SpecimensWearing(instanceId)` (new, in `RpgStore.EquipCombinations.cs`): the `rolled`
  assignments whose `ref_id` is this host — the reverse lookup the refresh needs.
- `ItemWorkbench.RefreshCombinationBindings(hostInstanceId)`: for every wearer, calls
  `MaterializeRolledEquipRuntime(specimen, actor.Level)` — the same projection, so the word binds
  without a re-equip.
- Called from `ApplySocketWrite` after `applied.Ok`, which is the ONE commit point all three socket
  verbs funnel through (`socket-add` :1277, `socket-insert` :1337, `socket-imbue` :1453). A discrete
  trigger, never a poll; the read side self-corrects removals but not additions, which is why this is
  the addition edge.

| Criterion | Command | Result |
|---|---|---|
| the row's verify filter | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~ItemWorkbenchEndpoints\|FullyQualifiedName~ItemEquipEndpoints"` | **99 passed / 0** |
| build | `dotnet build gk-core/src/FusionRpg.Server/FusionRpg.Server.csproj` | Build succeeded |

## DONE — the three tests landed

`Completing_a_word_on_an_equipped_host_binds_it_without_a_re_equip` equips the host and projects it with
no word, then fills through the REAL `socket-insert` verb and asserts the `cmb:{host}#c0:…-t1` binding
appears with no further equip call; `Fill_then_equip_and_equip_then_fill_reach_the_same_bindings` drives
both orders (a second host off `SeedHostAt`) and both land on the same word container; and
`Imbuing_an_equipped_host_rebinds_at_the_attuned_tier` bores a crafted socket, imbues fire, fills, and
asserts the binding moves from `-t1` to `-t2`.

**Fixture notes worth keeping:** the wearer must be a REAL unique actor (`CreateUniqueActor`) because
`RefreshCombinationBindings` looks it up through `GetUniqueActor` — a synthetic `"specimen-1"` is
skipped; and the combo container's grant atom is the variant-"" row the build derives, not the
fixture's `fire`-variant ember atom.

| Criterion | Command | Result |
|---|---|---|
| the three tests | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~Completing_a_word_on_an_equipped_host\|FullyQualifiedName~Fill_then_equip_and_equip_then_fill\|FullyQualifiedName~Imbuing_an_equipped_host_rebinds"` | **3 passed / 0** |
| the row's verify filter | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~ItemWorkbenchEndpoints\|FullyQualifiedName~ItemEquipEndpoints"` | **102 passed / 0** |
| scoped verifier | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EquipCombinations.cs','gk-core/src/FusionRpg.Server/ItemWorkbench.cs','gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchEndpointsTests.cs') -Session strain-splice-host-20260922"` | **exit 0** — DAL OK, test-substrate OK, Server.Tests 803/0 |

**Row CLOSED.** `SSH4.9` (the live probe) and `SSH5.9` remain.
