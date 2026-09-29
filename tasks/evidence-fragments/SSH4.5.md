# SSH4.5 — `ContributionSourceIds.Combo` + the `EquipAtomSource` mint (arm 2)

## What changed

- `gk-core/src/FusionRpg.Core/Stats/Derived/ContributionSourceIds.cs` — `Combo(role, hostItemRefId,
  comboId, circuit)` → `combo:{role}:{hostItemRef}:{comboId}#c{circuit}` (a negative circuit throws),
  plus the `FictionLabel` arm beside `Insert`'s.
- `gk-core/src/FusionRpg.Core/Battle/EquipAtomSource.cs` — `EquippedAtomInput` gains `ComboId` and `Circuit`
  (the spec named only `Circuit`; the comboId has no other carrier), and `MintSourceId` mints `Combo`
  when `ComboId` is set, else the unchanged `Insert` / `Equip` arms.
- `docs/architecture/actor-hub-ssot.md` §8.1 — the reserved `combo:` row is amended with `#c{circuit}`
  and marked minted; the producer table gains the Combination row (the ask-first one-suffix diff).
- `gk-core/tests/FusionRpg.Core.Tests/{Stats/ContributionSourceIdsTests.cs,Battle/EquipAtomSourceIdTests.cs}`.
- Citations into the two files, displaced by the insertions, re-anchored across `docs/architecture/**`
  and `tasks/`.

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| grammar + display arm + `FictionLabel` | `dotnet test tests.FusionRpg.Core.Tests --filter "FullyQualifiedName~ContributionSourceIds\|FullyQualifiedName~EquipAtomSourceId"` | 17 passed, 0 failed |
| `the_combination_contributes_under_its_own_source_id` | same run | `combo:armament-primary:item-stem:combo.strain-might-offense#c1` read back from the mint |
| §8.1 amended in the same commit | `docs/architecture/actor-hub-ssot.md` §8.1 header + table row | one suffix `#c{circuit}`, marked minted |
| no private fold | `pwsh -NoProfile -File scripts/guard-actor-hub.ps1` | exit 0, `ACTOR-HUB GUARD OK` |
| doc citations | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | exit 0, 0 HIGH |
