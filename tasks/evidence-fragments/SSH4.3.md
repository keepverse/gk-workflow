# SSH4.3 — `ComboContainerBuild` and the load-time tier bound (F7)

## What changed

- `gk-core/src/FusionRpg.Core/Items/Sockets/ComboContainerBuild.cs` (new) — `TryBuild(comboId, grants, tier,
  lookups, out refusalReason)`: id `{comboId}-t{tier}`, one fixed `AtomRow.DeriveId(family, "", tier)`
  atom per grant, `Kind = Combo`, `PrefixRolls`/`SuffixRolls` 0, empty pool. A grant whose derived atom
  is absent is refused by name (family + derived id); an empty grant list is refused too.
- `gk-core/src/FusionRpg.Core/Items/Sockets/StrainSpliceTuning.cs` — `Validate` throws when
  `max(baseTier) + attunedTierBonus > FamilyExpansion.TierCount` (F7). A throw at load, never a clamp
  at bind.
- `tests/FusionRpg.Core.Tests/Items/ComboContainerBuildTests.cs` (new).

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| `TryBuild` shape (id, fixed atoms, zero pool rolls) | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ComboContainerBuild\|FullyQualifiedName~StrainSpliceGrid"` | 26 passed, 0 failed |
| `a_grant_family_without_an_atom_is_refused_by_name` | same run | reason names `atom.savagery` and `atom.savagery.t2` |
| `a_granted_tier_above_the_atom_ladder_throws_at_load` | same run | `TierCount + 1` throws "above the atom ladder"; `TierCount - attunedTierBonus` loads |
| doc citations | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | exit 0, 0 HIGH |
