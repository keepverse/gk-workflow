# SP3.7 — `ToContainer`: projected rows persist as a valid `species-progression` container

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `ToContainer(rows)` builds a `SpeciesProgression` `ContainerRow` through `SyntheticStatDerivedAtoms`. A `LadderMicro` value serialises as `{"powerLadder": true, "kMicro": K}`, a `Fixed` value as a literal amount. Output passes `ContainerValidator` | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesLayerProjector\|FullyQualifiedName~ContainerValidator"` | **56/56 passed** | `gk-core/tests/FusionRpg.Core.Tests/Creatures/Layers/SpeciesLayerProjectorTests.cs` (`SpeciesLayerProjectorToContainerTests`, new) |
| Reading the container back resolves to the same modifiers as `Resolve(rows, P(Θ))` | same run, `Reading_the_container_back_through_the_real_ValueSpec_parser_resolves_to_the_same_modifiers_as_Resolve` | pass, at three Θ values (1, 1000, 500000) | same file |
| `solid-remediation/spec-species-carrier.md:150` (GG-49 `species-passive:` retired) handed over / recorded | doc note | done | this fragment + `ToContainer`'s own doc comment |
| Core builds clean | `dotnet build gk-core/src/FusionRpg.Core/FusionRpg.Core.csproj` | 0 errors | build log |

## What shipped

`SpeciesLayerProjector.ToContainer(containerId, rows) -> (ContainerRow Container, IReadOnlyList<AtomRow> Atoms)`:
pure Core, no I/O — mirrors the split `BuildMagnitudeAtoms`/`SynthesizeMagnitudeContainerUnlocked`
already establishes (`RpgStore.Species.cs`): the returned atoms and container are values: a Data-layer
caller upserts them through its own store (not built in this task — the projector's rows only reach a
real fold through module 6's registered `IActorStatSubsystem`, per the spec's own "ActorHub gate").

- A `LayerValue.Fixed` amount serialises as a literal JSON number.
- A `LayerValue.LadderMicro` amount serialises as `{"powerLadder":true,"kMicro":K}` — the existing
  ValueSpec grammar `AtomJson.cs` already parses, so no new grammar is invented.
- Two rows sharing a channel (legitimate for `ProjectEmpire`: two aptitude edges CAN target the same
  channel) still get distinct atom ids — the row's own position in the list disambiguates the variant,
  unlike `BuildMagnitudeAtoms`'s dictionary-keyed input which structurally cannot collide.
- `containerId` is caller-supplied, never derived here — the container-id scheme for a 2b (per
  empire+species) vs. a 1a/1b (per species) carrier is `solid-remediation/spec-species-carrier.md:150`'s
  own open line, explicitly deferred rather than invented by this pure builder (matching the todo's own
  "hand over the carrier-spec line" acceptance wording).

## The round-trip proof, and why it uses the real parsers

"Reading the container back through the atom path" is proven by parsing each atom's own `ParamsJson`
through `AtomJson.TryReadValueSpec` (the SAME grammar parser every other `stat.modify`/`stat.derived`
atom's `amount` field goes through) and `AtomDerivedSubsystem.TryParseOp` (the SAME op parser
`ProjectBase`/`ProjectPlayerMod` already reuse), then resolving a `LadderMicro`-shaped `ValueSpec` via
`LadderScale.Micro` — the identical function `SpeciesLayerProjector.Resolve` calls. This is real
production parsing code, not a throwaway re-implementation, and it is checked at three different `Θ`
values to prove the round trip survives the *serialized `kMicro`*, not merely one already-resolved
number.

This deliberately does NOT go through `AtomCompiler.Compile` (the production `stat.modify` compile
pipeline) — `stat.derived` atoms are read by `AtomDerivedSubsystem`, a different pipeline entirely, and
`AtomCompiler.cs`'s own `powerLadder`/`kMicro` branch is SP2.2's still-blocked, separate rounding
question (confirmed via the SP2.2 correction: no committed content exercises that branch at all).
Conflating the two would have either accidentally re-litigated SP2.2's Ask-first block or produced a
misleading pass/fail depending on rounding-boundary luck.

## Known limitation, named rather than silently handled

`AtomJson.TryReadValueSpec`'s plain-number branch requires a 32-bit integer (`el.TryGetInt32`) — never
a fraction. 1a/1b's `Fixed` values are always whole numbers (sourced from a `long` definition amount),
so this holds for them. A `ProjectEmpire` Contest-mode row's `Fixed` value is a genuine `double`
(`AptitudeReadFunctions.Contest`) and could carry a fraction; feeding one to `ToContainer` today would
produce an atom a real `AtomJson` parse would reject. No caller does this yet (2b's contest edges are
consumed as `DerivedModifier`s via `Resolve`, never persisted through this method) — recorded in the
method's own doc comment rather than guessed at with a premature rounding rule nobody asked for.
