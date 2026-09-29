# Task 11 — Wave-band rank floor

Lane `cs-rank` (session `creature-seed-rank`, branch `cmdc/cs-rank`), 2026-09-23.
Row: `tasks/creature-seed-todo.md` Task 11. Spec: `docs/architecture/creature-seed/spec-species-rank.md` §6.
Edited: `gk-core/src/FusionRpg.Core/Battle/WaveCatalog.cs` (`Band`), `gk-core/tests/FusionRpg.Core.Tests/Battle/WaveSpeciesRollTests.cs`
(3 new tests). The worktree also merged `features/mega-merge` first, so this increment sits on the current head.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Floor on band membership | `dotnet test gk-core/tests/FusionRpg.Core.Tests --nologo --verbosity quiet --filter "FullyQualifiedName~WaveSpeciesRollTests\|FullyQualifiedName~WaveCatalogLoaderTests"` | **Passed! — Failed 0, Passed 23, Total 23, 100 ms** | `WaveCatalog.cs` |
| No-acquisition-filter behaviour preserved | same run, plus the new `A_raised_floor_never_adds_an_acquisition_rule_of_its_own` | with the floor at the TOP rung, `capture` (CaptureOnly) and `event` (EventOnly) are still refused and only `plain` survives — so the refusal is `CreatureAdmission.ForWave`'s, not rank's; the file's four pre-existing acquisition tests (`A_synthetic_summonable_eventonly_species_is_refused`, `An_eventonly_species_first_alphabetically_is_still_absent`, `Captureonly_is_refused_in_a_wave_but_summonable_captureonly_is_admitted`, …) stay green unchanged | same |
| Pass-through proof | same run, `At_the_shipped_bottom_floor_a_skipped_rank_is_admitted_and_nothing_narrows` | at the shipped bottom floors the band is EXACTLY the window + admission result: a rank-less species, a `Chaff`-ranked one and an above-floor ranked one all survive in SpeciesId order. Corroborated by the whole file: every other test there builds rank-less synthetic species and passes untouched, which is only possible if the predicate admits a null rank at bottom | same |
| A raised floor narrows, and a skipped rank is NOT admitted | same run, `A_raised_wave_band_floor_excludes_below_floor_and_skipped_ranks_only` | at a Heirloom floor the pool is `["above", "at"]` — the below-floor and the **rank-skipped** species are both gone, because null maps to the bottom rung at the gate rather than being waved through | same |
| No regression in the rest of Core | `dotnet test gk-core/tests/FusionRpg.Core.Tests --nologo --verbosity quiet` | **EXIT=0 — Passed! Failed 0, Passed 9594, Skipped 0, Total 9594, 1 m 19 s** | — |
| Static guards | `guard-magic-numbers` · `guard-population-pin` · `guard-test-substrate` | `M1=0 M2=0 M3=0 M4=0` · `total 0 finding(s)` · `TEST SUBSTRATE GUARD OK` | — |

## NOT proved / declared gaps

- **The spec's own Task 11 note about this filter is stale, and the code wins:** `spec-species-rank.md`'s
  gate table says `Band` "has no acquisition filter — CaptureOnly can march: pinned, not fixed here".
  Measured 2026-09-23: `WaveCatalog.Band` applies `CreatureAdmission.ForWave`, which requires
  `Summonable` and refuses `EventOnly` (`gk-core/src/FusionRpg.Core/Creatures/CreatureAdmission.cs:27-28`), so
  CaptureOnly does NOT march. The stale sentence is a doc erratum outside this lane's fence
  (`docs/**`), filed as **T11-N**.
- No wave-composition hash golden exists to compare against (unlike T10's expedition tier goldens), so the
  pass-through is proven by the band's own contents at bottom (above) rather than by a byte-level hash.
- The compiled roster's own `Build()` and the data-sourced loader agreement are unchanged and green
  (`WaveCatalogLoaderTests`), but that pair compares two sides that BOTH run through `Band`, so it is not
  by itself a pre-rank/post-rank proof — the bottom-floor membership test above is.
- The floor is configured process-wide by tests only; as with T8/T10, no production host calls
  `CreatureRankFloors.Configure` yet (that wire is on the denied `gk-core/src/FusionRpg.Server/**` /
  `gk-fusion/src/FusionRpg.Injector/**` paths), so a floor tuned above bottom has no production effect today.
