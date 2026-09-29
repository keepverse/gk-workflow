# scope-side-wide SSW1 — the side-wide owner key (grammar)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| A side-wide plant key matches every plant regardless of type id | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~StatApplyScopeSideWide"` | PASS — 8/8, 0 failed; `A_side_wide_plant_key_matches_every_plant_regardless_of_type_id` (typeIds 0, 3, 999, null entityKey) | `gk-core/tests/FusionRpg.Core.Tests/Scope/StatApplyScopeSideWideTests.cs` |
| It never matches a zombie (and `zombie:*` never a plant) | same run | PASS — `A_side_wide_key_never_matches_the_other_side` | same |
| `match` still matches both sides; type-keyed arms not widened | same run | PASS — `Match_still_matches_both_sides`, `The_type_keyed_arms_are_not_widened_by_the_new_key` | same |
| The four gate functions agree: known grammar, NOT match-wide | same run | PASS — `A_side_wide_key_is_known_grammar_and_deliberately_not_match_wide` (`IsMatchWide("plant:*")=false`, `IsMatchWide("match")=true`) | `gk-core/src/FusionRpg.Core/Stats/StatApplyScope.cs` |
| Store-lookup widening answers one side only | same run | PASS — `OwnerKeyCovers_answers_a_same_side_lookup_and_nothing_else` (`plant:*`→`plant:999` true; →`match`, `entity:1a2b`, `zombie:0` false) | same |
| Real resolve gate, not just the helper | same run | PASS — `A_side_wide_modifier_resolves_on_plants_of_every_type_and_never_on_a_zombie` (15 / 15 / 10 / 10 Atk) | `tests/FusionRpg.Core.Tests/StatTests` (StatSystem) |
| Doc citations re-anchored for this change | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | exit 0 — 1679 documents, 24804 citations; D2 line-past-EOF 12, 0 HIGH | — |
| No golden moved | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden|FullyQualifiedName~Dominance|Category=BalanceGuard"` | PASS — 36/36, unchanged from the pre-change baseline | — |

Spelling decision (in `StatApplyScope`'s header, not just here): `plant:*` / `zombie:*` over
`side:plant` — the family already spells the side as the prefix, so the key slot widens instead of a
second axis appearing. `EffectOwnerKeys` (Contracts) was outside this lane's writable paths, so the
constants landed in Core's own `EffectOwnerKey`.
