# SP6.2 — `SpeciesLayerSubsystem` (`rpg.species-layer`, Order 100), registered through `ActorHubBootstrap.CreateDefault`

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The subsystem resolves rows at the ctx's Θ through `SpeciesLayerProjector.Resolve`; memoises per row-list reference and per Θ; never caches a Θ-resolved value past a Θ change; skips an empty SourceId | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesLayerSubsystem"` | **17/17 passed** | `gk-core/src/FusionRpg.Core/Stats/Derived/Subsystems/SpeciesLayerSubsystem.cs` (new), `tests/FusionRpg.Core.Tests/Stats/Derived/SpeciesLayerSubsystemTests.cs` (new) |
| `ActorHubBootstrap.CreateDefault` gains an opt-in `speciesLayers` delegate, same shape as `aptitudeAllocation`; no mode gets its own reader; omitting it registers nothing | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesLayerSubsystem"` (wiring tests included above) | passed | `gk-core/src/FusionRpg.Core/Stats/Derived/ActorHub.cs` |
| `guard-actor-hub.ps1` green | `.\scripts\guard-actor-hub.ps1` | **ACTOR-HUB GUARD OK** | command output |
| No regression in the wider ActorHub/derived-compose suite | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~FusionRpg.Core.Tests.ActorHub"` | **498/498 passed** | command output |

## What shipped

- `gk-core/src/FusionRpg.Core/Stats/Derived/Subsystems/SpeciesLayerSubsystem.cs` (new): `SubsystemId
  "rpg.species-layer"`, `Order 100` (the same progression band `rpg.aptitude` already uses — not a new
  band, `actor-hub-ssot.md` §6). Matches the spec's own given stub, with one addition the acceptance
  text requires and the stub's own inline code didn't spell out: the `foreach` loop over resolved mods
  skips a `string.IsNullOrWhiteSpace(m.SourceId)` row, the same defensive check `AtomDerivedSubsystem`
  already applies to its own externally-sourced rows — real rows minted by `SpeciesLayerProjector`'s own
  `ProjectBase`/`ProjectPlayerMod`/`ProjectEmpire` never carry an empty SourceId today, so this is
  defense-in-depth against whatever the injected `_rowsFor` delegate could someday hand back, not a
  currently-reachable path.
- The memo is keyed on the **`ProjectedLayerRow` list reference** (`ReferenceEqualityComparer.Instance`),
  never on `(Side, TypeId)` the way `AptitudeSubsystem`'s own memo is — the spec's own stub names why:
  every actor of the same `(empire, speciesId)` shares one rows-list instance handed out by the
  cache/assembly upstream, so keying on that reference collapses every such actor into one cached
  resolve, "never by actor count." Θ is compared on every read (never folded into the dictionary key,
  never stored past a Θ change) — `Theta_is_never_cached_in_species_layers` proves a Θ bump against the
  SAME rows reference recomputes.
- `gk-core/src/FusionRpg.Core/Stats/Derived/ActorHub.cs`: `ActorHubBootstrap.CreateDefault` gains
  `Func<StatContext, IReadOnlyList<Creatures.Layers.ProjectedLayerRow>>? speciesLayers = null`, the same
  opt-in shape as `aptitudeAllocation`/`boundDerivedAtoms`/`draughts` — omitting it registers no
  `SpeciesLayerSubsystem` at all, so every existing bare `CreateDefault()` caller (hundreds of tests) is
  unaffected. One `PowerLadder` is constructed from `PowerTuningHub.Tuning`, matching the
  `aptitudeTuning` arm's own construction.
- `tests/FusionRpg.Core.Tests/Stats/Derived/SpeciesLayerSubsystemTests.cs` (new): 17 tests mirroring
  `AptitudeSubsystemTests`'s own shape (registration, idempotence, double-registration safety, Θ
  sourcing, `CreateDefault` opt-in wiring), adapted for the rows-reference memo key, plus the two tests
  the acceptance text names directly (`Theta_is_never_cached_in_species_layers`,
  `AnEmptySourceId_isSkipped_neverMintsAnUnattributedContribution`) and a "no mode gets its own reader"
  proof (the same subsystem answers a plant and a zombie context identically off the same rows delegate).

## Notes

- A genuine C# name-resolution gotcha, not a design defect: this test file's namespace
  (`FusionRpg.Core.Tests.Stats.Derived`) has `FusionRpg.Core.Tests` as an ancestor, and
  `FusionRpg.Core.Tests.ActorHub` is a REAL sibling namespace (an existing test folder) — so a bare
  `ActorHub` reference resolves to that namespace before the `using FusionRpg.Core.Stats.Derived;`
  directive is even considered (CS0118). `AptitudeSubsystemTests.cs` already works around this the same
  way (fully-qualifying `FusionRpg.Core.Stats.Derived.ActorHub`); this file follows the same convention.
- Not a re-bless: no existing actor's composed value moves (`SpeciesLayerSubsystem` is a brand-new,
  opt-in contributor nothing referenced before this task), matching step 6.2's own spec table entry
  ("adds new layers' contributions (new SourceIds); not a re-bless").
