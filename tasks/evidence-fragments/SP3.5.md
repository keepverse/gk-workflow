# SP3.5 — `ProjectBase` + `ProjectPlayerMod`: 1a and 1b partition a fused instance

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| T4.6's parse rules carry over unchanged: instance `values_json` before definition `params_json`; a non-`stat.derived` atom, an unknown op, a ValueSpec-object amount are each skipped, never coerced, one test each | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesLayerProjector\|FullyQualifiedName~SpeciesPassiveAtomSource"` | **25/25 passed** | `gk-core/tests/FusionRpg.Core.Tests/Creatures/Layers/SpeciesLayerProjectorTests.cs` (`SpeciesLayerProjectorOneTwoBTests`, new) |
| A fused instance with a 2-atom core and 3 rolls gives 2 `species-base:` rows and 3 `species-player:` rows; their union equals what `SpeciesPassiveAtomSource` emits for the same instance | same run, `A_fused_instance_partitions_with_no_overlap_and_no_loss` | pass | same file |
| Core builds clean | `dotnet build gk-core/src/FusionRpg.Core/FusionRpg.Core.csproj` | 0 errors | build log |

## What shipped

`gk-core/src/FusionRpg.Core/Creatures/Layers/SpeciesLayerProjector.cs` gains:

- `ProjectBase(speciesId, ContainerRow template, Func<string, AtomRow?> resolveAtom)`: 1a — the
  template's own fixed core atoms (`stat.derived` only), read at their DEFINITION values (`E2`'s own
  override slot read first, then the definition — generalising T4.6's "instance/override wins" rule to
  1a's currently-unused override field rather than silently ignoring it). Emits `LayerValue.Fixed`
  rows with `ContributionSourceIds.SpeciesBase(speciesId)`.
- `ProjectPlayerMod(speciesId, mechanism, ContainerRow template, InstanceRow instance, Func<string, AtomRow?> resolveAtom)`:
  1b — every instance row whose `Seq` is NOT one of the template's own core seqs (the instantiator
  numbers rolled rows strictly after the core's highest seq, `Instantiator.cs:120-143` — "1b never
  repeats 1a"), read instance-values-first-then-definition, exactly T4.6's rule. Emits `LayerValue.Fixed`
  rows with `ContributionSourceIds.SpeciesPlayer(speciesId, mechanism)`.
- Shared private parse helpers (`SafeReadJson`, `TryChannelOpAmount`, `TryString`, `TryAmount`) —
  the same shape `SpeciesPassiveAtomSource`'s own private statics already used, so both new methods
  share ONE parse implementation between them rather than each re-typing it. `SpeciesPassiveAtomSource`
  itself is untouched here (its own retirement is SP3.6) — this is an interim duplication the spec's
  own Project Structure table anticipates ("its parse rules move into `ProjectPlayerMod`/`ProjectBase`"),
  not a permanent second copy.

`tests/.../SpeciesLayerProjectorTests.cs` gains a new `SpeciesLayerProjectorOneTwoBTests` class: reads
definition values (`ProjectBase`), instance-wins-over-definition (`ProjectPlayerMod`), the 2-core/3-roll
partition proof against the legacy `SpeciesPassiveAtomSource.DerivedAtomsFor` output (channel/op/amount
set equality, SourceId prefix asserted separately since it legitimately differs), the three T4.6
refusals (non-derived atom, unknown op, ValueSpec-object amount), a missing-definition skip, and
null-argument guards.
