# Task 10 — Expedition wild-band rank floor

Lane `cs-rank` (session `creature-seed-rank`, branch `cmdc/cs-rank`), 2026-09-23.
Row: `tasks/creature-seed-todo.md` Task 10. Spec: `docs/architecture/creature-seed/spec-species-rank.md` §6.
Edited: `gk-core/src/FusionRpg.Core/Expeditions/ExpeditionResolver.cs` (`WildBand` + the band fallback),
`gk-core/tests/FusionRpg.Core.Expeditions.Tests/Expeditions/ExpeditionResolverTests.cs` (2 new tests).

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Floor on the `WildBand` filter | `dotnet test gk-core/tests/FusionRpg.Core.Expeditions.Tests --nologo --verbosity quiet` | **Passed! — Failed 0, Passed 38, Total 38, 482 ms** | `ExpeditionResolver.cs` |
| Pass-through proof — byte level | same run, `Tier_goldens_are_locked` | the four tier goldens are UNCHANGED. They are coupled to the band's own contents (`ExpeditionResolverTests.cs`'s own comment: "coupled to roster SIZE… moves every time species are added"), so a rank predicate that altered membership would move all four hashes | same |
| Pass-through proof — semantic level | same run, `The_shipped_bottom_floor_admits_exactly_what_the_two_rules_admit` | over 40 seeds of `hunt-8h`, every wild creature the resolver actually meets clears the shipped floor, is never `CaptureOnly` and is never `Sunwoven` — read from the resolver's own public output (`tick.WildSpeciesId`) | same |
| Sunwoven exclusion + EventOnly admission preserved | same run | the predicate is additive beside both rules (rank can only narrow); `EventOnly` still passes because the rule is `Acquisition != CaptureOnly`, and the met-species test asserts both | same |
| A floor that empties every band refuses by name | same run, `A_floor_that_empties_every_wild_band_refuses_by_name_rather_than_indexing_nothing` | with `expeditionWildBand` at the top rung the resolver throws `InvalidOperationException` naming `expeditionWildBand` and the floor | same |
| No regression in the rest of Core | `dotnet test gk-core/tests/FusionRpg.Core.Tests --nologo --verbosity quiet` | **EXIT=0 — Passed! Failed 0, Passed 9587, Skipped 0, Total 9587, 1 m 20 s** | — |
| Static guards | `guard-magic-numbers` · `guard-population-pin` · `guard-test-substrate` | `M1=0 M2=0 M3=0 M4=0` · `total 0 finding(s)` · `TEST SUBSTRATE GUARD OK` | — |

## A defect this task would otherwise have introduced (found and fixed here)

`RollWildSpecies`'s empty-band fallback was a **fixed** `WildBand(Chaff)` lookup. That is only correct
while the floor sits at the bottom rung: a floor above the Chaff band empties that band too, so the old
two-step fell through to `band[rng.NextInt(0)]` — an index into nothing, at runtime, for a species the
wild roll was about to hand a player. The fallback now walks `CreatureRarityLadder.All` and takes the
lowest rung that still holds wild species *after the floor*, and refuses by name when no rung does.
At the shipped floors this is behaviour-identical (the walk starts at Chaff), which the tier goldens
prove.

## NOT proved / declared gaps

- The `EventOnly` admission claim is asserted through the resolver's own met-species set on the real
  compiled catalog; the predicate itself never reads `Acquisition` (it is `!= CaptureOnly`, untouched),
  so the two halves of the claim are the same line and the test's own assertion.
- No raised-floor *selection* test (a floor at, say, `grafted` narrowing the wild pool) is included: the
  compiled roster carries no ranks, so any raised floor empties every band and exercises the refusal path
  instead. Narrowing is proven at the policy level (`FusionRankFloorTests`, `EligibleOutputs`) and for the
  fusion gates (T8); the expedition band's own narrowing would need a ranked scoped catalog, which this
  project does not build.
- Task 9's remaining clauses (Server payloads, Contracts DTO, quality-report line) stay open on their own
  denied paths — they are not this row's dependency in practice: rank reaches this gate through
  `CreatureSpeciesDef.Rank`, which Task 7 wired.
- **CS-R2 is now closed at the integration tip** (the repair commit fixed the `Assert.Equal(500, …)` pin):
  `guard-population-pin` reads `total 0 finding(s)` after merging `features/mega-merge`.
