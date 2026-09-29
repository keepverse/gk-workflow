# SP3.2 follow-up — update the 5 pre-existing ContainerKind member-count pins

Found by the coordinator's requested whole-project re-verification (`dotnet test
gk-core/tests/FusionRpg.Core.Tests`, no filter): SP3.2's `ContainerKind.SpeciesProgression` addition (14 -> 15
members) was not caught by that task's own scoped Verify command
(`FullyQualifiedName~ContainerValidator`), because these 5 tests live in unrelated files/namespaces and
pin the OLD member count as a closed-vocabulary literal — exactly the CLAUDE.md-sanctioned pattern
("pin a literal only for a closed vocabulary... and say why", "a sixth is a reviewed change").

| Test | File | Old -> New |
|---|---|---|
| `ContainerKind_has_fourteen_members_with_Relic_last` (renamed `..._fifteen_members_with_SpeciesProgression_last`) | `gk-core/tests/FusionRpg.Core.Tests/Items/RelicTests.cs` | 14 -> 15; `Relic` no longer last, `SpeciesProgression` is |
| `A_wrong_container_kind_is_refused_BY_NAME_now_that_X7_has_minted_Consumable` | `tests/FusionRpg.Core.Tests/Items/ConsumableTests.cs` | 14 -> 15 |
| `An_insert_charm_or_consumable_entry_is_refused_by_name_until_seed_to_concrete_lands` | `gk-core/tests/FusionRpg.Core.Tests/Items/DropVolumeCorpusTests.cs` | 14 -> 15 |
| `This_module_adds_no_container_kind_and_no_atom_kind` | `gk-core/tests/FusionRpg.Core.Tests/Items/UniqueTests.cs` | 14 -> 15 |
| `There_are_now_exactly_fourteen_container_kinds` (renamed `..._fifteen_...`) | `gk-core/tests/FusionRpg.Core.Tests/Delve/Encounter/EliteAffixTests.cs` | 14 -> 15 |

Each file's own running "history of counts" comment gets one more line naming
`species-progression SP3.2` and `ContainerKind.SpeciesProgression`, matching the exact narrative style
every prior addition (X7, achievement-title T3, empire-development Task 1.3a) already used there —
these are NOT Guard.Tests files, so the add-only restriction does not apply; updating them is squarely
in scope for the task that added the enum member.

`RelicTests.cs`'s test additionally asserted `Relic` is the LAST member (append-only, no reorder) —
since `SpeciesProgression` is now appended after it, the test is updated to assert `Relic`'s own
ordinal is unchanged (13) and `SpeciesProgression` is now last, preserving the actual invariant the
test protects (append-only, never a reorder) rather than a claim that is only true until the next
append.

Verify: `dotnet test gk-core/tests/FusionRpg.Core.Tests` (whole suite) — **14330/14330 passed** (was 14325/14330
with these 5 failing before the fix).
