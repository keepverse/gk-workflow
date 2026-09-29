# spec — `species-layer-projector`

**Module 3 of `species-progression`** ([map](../species-progression-map.md)). Depends on
`layer-source-selector`, `ladder-scale-parity`. Status: spec, 2026-09-18, strengthened the same day
(`EmpireId` typing, projector revision, full §8.1 owed list). No build authorized until the map is
reviewed.

## Objective

Build the ideal's **one projector mechanism** (R-S3: *"One projector mechanism serving 1a, 1b and 2b,
rather than two passes over the same machinery"*): a pure Core component that turns the numeric state
behind a species layer into **projected rows** — `(channel, op, value, sourceId)` where the value is
either a fixed number or a Θ-free ladder coefficient — and turns a set of rows into a persistable
`ContainerRow`. Three inputs, one output shape:

| Layer | Input | What the projector emits |
|---|---|---|
| **1a** (species-passive core only) | the generator's `species-passive.{speciesId}` container | its fixed `atoms` (`stat.derived` only), definition values, `species-base:{speciesId}` |
| **1b** | one ledger instance (module 4) + its template container | the instance's **non-core** atoms (pool rolls and forced picks), instance values first, `species-player:{speciesId}:{mechanism}` |
| **2b** | one 2b `AptitudeAllocation` — the species term **alone**, never merged with the commander (R2, 2026-09-18; module 5 builds it) | one row per funded aptitude edge: contest edges as fixed values, magnitude edges as `kMicro` ladder coefficients, `species-empire:{empireToken}:{speciesId}:{aptitudeId}` |

**Why it exists.** Three half-mechanisms already exist and none is the whole
(ideal R3): `TreeBoundAtoms` projects numeric state but emits atoms, not a container; the magnitude
synthesizer (`RpgStore.Species.cs:227-255`, `BuildMagnitudeAtoms`) builds a container but lives in the
Data layer and serves one input; `SpeciesPassiveAtomSource` (`SpeciesPassiveAtomSource.cs:49-77`, gone — retired by SP3.6) parses
an instance but mints its SourceId outside the grammar (map **C3**). One Core projector replaces the
parsing and building halves; the stores keep only persistence.

**The invariant that makes 2b honest.** For every species-only allocation `A` (only `CreatureType`
points) and every `Θ`, `Resolve(ProjectEmpire(A), P(Θ))` equals
`AptitudeResolver.Resolve(A, tuning, ladder, Θ, registry)` (`AptitudeResolver.cs:23-64`) channel for
channel, op for op, value for value — only the SourceId differs, by design. Module 2 is what makes the
magnitude half exact, and it is what makes `species-layer-delivery` step 6.3 value-neutral. A merged
allocation is never an input: R2 hands the projector the species term alone.

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesLayerProjector|FullyQualifiedName~ContributionSourceIds|FullyQualifiedName~SpeciesPassiveAtomSource|FullyQualifiedName~ContainerValidator"
dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~SpeciesMagnitudeSynth|FullyQualifiedName~CreatureLawnDeployMagnitude"
python gk-core/scripts/guard-actor-hub.py
.\scripts\verify-change.ps1 -Paths <every changed file> -Session <session-id>
```

## Project Structure

| Path | Change |
|---|---|
| `gk-core/src/FusionRpg.Core/Creatures/Layers/SpeciesLayerProjector.cs` | **(new)** `ProjectBase`, `ProjectPlayerMod`, `ProjectEmpire`, `Resolve`, `ToContainer` |
| `gk-core/src/FusionRpg.Core/Creatures/Layers/ProjectedLayerRow.cs` | **(new)** the row shape |
| `gk-core/src/FusionRpg.Core/Stats/Aptitudes/AptitudeAllocation.cs` | `ShareWithinScope(scope, aptitudeId)` (new, pure addition — no existing reader changes; `species-layer-delivery` step 6.1 later makes it the resolver's only share) |
| `gk-core/src/FusionRpg.Core/Effects/Atoms/SyntheticStatDerivedAtoms.cs` | **(new)** the atom-row builder moved out of `RpgStore.Species.cs:227-260` (`BuildMagnitudeAtoms`, `Kebab`); the magnitude synthesizer calls it — one builder |
| `src/FusionRpg.Core/Battle/SpeciesPassiveAtomSource.cs` | **retired**; its parse rules (instance values first, three refusals) move into `ProjectPlayerMod`/`ProjectBase` |
| `gk-core/src/FusionRpg.Core/Stats/Derived/ContributionSourceIds.cs` | three helpers + `FictionLabel` arms |
| `gk-core/src/FusionRpg.Core/Effects/Atoms/ContainerRow.cs`, `ContainerValidator.cs:35`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Containers.cs:573` | `ContainerKind.SpeciesProgression`, prefix `species-progression` |
| `gk-core/tests/FusionRpg.Core.Tests/Creatures/Layers/SpeciesLayerProjectorTests.cs` | **(new)** |

## The row and the three projections

```csharp
namespace FusionRpg.Core.Creatures.Layers;

public abstract record LayerValue
{
    public sealed record Fixed(double Amount) : LayerValue;        // resolved now: contest reads, 1a/1b atoms
    public sealed record LadderMicro(long KMicro) : LayerValue;    // resolved at the reader's Θ via LadderScale.Micro
}

public sealed record ProjectedLayerRow(string Channel, DerivedModifierOp Op, LayerValue Value, string SourceId);

public static class SpeciesLayerProjector
{
    /// Bumped only when the projection's arithmetic changes (e.g. ladder-scale-parity). Part of module 5's
    /// input digest so a stored container can never outlive the arithmetic that produced it. Structural,
    /// not tunable: it versions code, not balance.
    public const int Revision = 1;

    public static IReadOnlyList<ProjectedLayerRow> ProjectEmpire(
        EmpireId empire, string speciesId, AptitudeAllocation allocation,
        AptitudeTuning tuning, DerivedStatRegistry registry)
    {
        var rows = new List<ProjectedLayerRow>();
        foreach (var edge in tuning.Edges)
        {
            // A 2b allocation holds one scope (CreatureType), so its share within that scope is the
            // same number species-layer-delivery step 6.1's per-scope resolver computes.
            var share = allocation.ShareWithinScope(AllocationScope.CreatureType, edge.Source);
            if (share <= 0.0) continue;                               // same skip as AptitudeResolver.cs:36-37
            if (!registry.TryResolveChannel(edge.Channel, out var def))
                throw new InvalidOperationException($"aptitude edge targets unregistered channel '{edge.Channel}'");
            var kMilli = AptitudeResolver.EffectiveKMilli(tuning, edge);   // the SAME coefficient rule, made internal-visible, not copied
            var op = def.Compose == DerivedComposeKind.SumIncreased ? DerivedModifierOp.Increased : DerivedModifierOp.Flat;
            LayerValue value = edge.Mode == AptitudeReadMode.Contest
                ? new LayerValue.Fixed(AptitudeReadFunctions.Contest(kMilli, share,
                      tuning.Read.Contest.ShareExponentMilli, tuning.Read.Contest.SpanPointsMilli))
                : new LayerValue.LadderMicro(checked(kMilli * AptitudeReadFunctions.SharePowMilli(
                      share, tuning.Read.Magnitude.ShareExponentMilli)));
            rows.Add(new ProjectedLayerRow(edge.Channel, op, value,
                ContributionSourceIds.SpeciesEmpire(empire, speciesId, edge.Source)));
        }
        return rows;
    }

    public static IReadOnlyList<DerivedModifier> Resolve(IReadOnlyList<ProjectedLayerRow> rows, long pTheta) =>
        rows.Select(r => new DerivedModifier(r.Channel, r.Op, r.Value switch
        {
            LayerValue.Fixed f => f.Amount,
            LayerValue.LadderMicro l => LadderScale.Micro(l.KMicro, pTheta),
            _ => throw new ArgumentOutOfRangeException(nameof(rows)),
        }, SourceId: r.SourceId)).ToList();
}
```

Rules:

1. **No second copy of the aptitude math.** `EffectiveKMilli` (`AptitudeResolver.cs:66+`) and the
   `sharePowMilli` rounding (`AptitudeReadFunctions.cs:55-57`) are exposed as single functions both
   resolvers call; nothing is re-typed.
2. **1a/1b parse rules carried over from T4.6, unchanged:** instance `values_json` before definition
   `params_json`; skip (never coerce) a non-`stat.derived` atom, an unknown op
   (`AtomDerivedSubsystem.TryParseOp`, `AtomDerivedSubsystem.cs:72-82`), and a ValueSpec-object amount.
3. **1b never repeats 1a.** The instantiator keeps the fixed core at its authored `seq`
   (`Instantiator.cs:120-128`) and numbers pool rolls after the core's highest `seq`
   (`Instantiator.cs:133-143`). `ProjectPlayerMod` drops every instance row whose `seq` is a core `seq` of
   the template; `ProjectBase` emits exactly those core atoms. So a fused species composes its core once
   (1a) and its rolls and picks once (1b).
4. **2b never reads 1a or 1b.** `ProjectEmpire`'s inputs are an allocation and tuning — no composed value
   (ideal, *"What a downstream session must not do"*, first bullet).
5. **`ToContainer(rows)`** builds a `ContainerRow` of kind `SpeciesProgression` plus synthetic
   `stat.derived` atoms through `SyntheticStatDerivedAtoms` — a `LadderMicro` value serialises as the
   existing ValueSpec `{"powerLadder": true, "kMicro": K}` (`AtomJson.cs:77-83`), so a persisted container
   is readable by every existing container tool; a `Fixed` value as a literal `amount`.

## SourceIds — the §8.1 amendment this module owes

`actor-hub-ssot.md` §8.1 is a reviewed grammar; each new producer row is an amendment recorded there in
the same change (that file is outside this spec session's paths; the build session edits it). This
program owes **two** §8.1 amendments, in build order: this module's three rows below, and
`species-layer-delivery` step 6.1's per-scope aptitude row (`aptitude.{scopeText}.{Share}` beside the
unchanged `aptitude.{Share}`, with its `FictionLabel` arm). §8.2's *"`commander + UniqueCreature(instanceId)`"*
is amended by step 6.1 as well (R16). The map §9 lists all three with their lines.

| Producer | SourceId | Fiction label |
|---|---|---|
| Species base (1a, species-passive core) | `species-base:{speciesId}` | `Species · {speciesId}` |
| Player-modified species (1b) | `species-player:{speciesId}:{mechanism}` | `Your species · {speciesId} ({mechanism})` |
| Empire species progression (2b) | `species-empire:{empireToken}:{speciesId}:{aptitudeId}` | `Empire species · {speciesId} · {aptitudeId}` |

Grammar safety: species ids cannot contain `:` where they enter a progression source
(`CreatureProgressionSource.cs:59-66`); the helpers assert it rather than trusting it. `empireToken` is
the `EmpireId`'s own value (`commander-identity`), which carries today's lower-case tokens
(`SpeciesAllocation.cs:42-47`, `"dave"` / `"zomboss"`) unchanged — never re-spelled. The save is not in
the id: an actor composes inside exactly one save, so two saves' rows never meet in one fold. T4.6's
`species-passive:{speciesId}` is retired: it could not tell 1a from 1b.

## Closed vocabularies touched (reviewed changes)

- `ContainerKind` gains **`SpeciesProgression`**, prefix `species-progression` — a new container kind is
  a closed-vocabulary change (`decisions.md` Actor layer stack: *"open to EXTENSION, closed to INVENTION"*).
  2b cannot reuse `species-passive`: that kind is frozen generator output, and frozen and
  player-mutable state cannot share a carrier (DESIGN-GATE §1 actor-layer row).
- `ContributionSourceIds` gains three producer rows (above).

## Testing Strategy

- **Parity (the load-bearing test):** for a grid of species-only allocations (single share, mixed shares, empty) and
  `Θ` values including one where the old `kMicro` path would overflow, `Resolve(ProjectEmpire(A), P(Θ))`
  equals `AptitudeResolver.Resolve(A, …, Θ, …)` on `(Channel, Op, Value)` for every row.
- **Empty in, empty out:** an empty allocation projects zero rows, never zero-valued rows
  (`AptitudeResolver`'s own contract).
- **1a/1b split:** a fused instance with a core of two atoms and three rolls projects two `species-base`
  rows and three `species-player` rows; the union equals what T4.6's `SpeciesPassiveAtomSource` emitted
  for the same instance (proves nothing was lost in the move).
- **Refusals:** the three T4.6 refusals, one test each.
- **SourceIds:** every emitted id round-trips through `FictionLabel` to a non-raw label; a species id
  containing `:` throws.
- **Synthesizer regression:** `SpeciesMagnitudeSynthTests` and `CreatureLawnDeployMagnitudeTests` stay
  green with the builder moved to Core (byte-identical atom ids and params).
- **Container validity:** `ToContainer` output passes `ContainerValidator` for the new kind.
- No test asserts how many species, containers or atoms exist.

## Numeric

`LadderMicro.KMicro` is `long`, computed `checked(kMilli * sharePowMilli)`; resolution goes through
`LadderScale.Micro` (decimal-widened, throws past `long`). `Fixed` contest values are `double`, as the
live contest read already is (`AptitudeReadFunctions.cs:33-44`) — floating point is allowed
(owner ruling 2026-09-15) and contests are Θ-free.

## Tunables

None new. The projector reads `aptitudes.v{n}.json` (edges, read exponents) and the plan shares; every
number it emits comes from them.

## Seedsmith / generator

Consumer only, no generator change:

| Input | Generator | Stage |
|---|---|---|
| `species-passive.{id}` containers (1a core, 1b template) | seedsmith `species-effects` | `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/effects/prompts.py:114` (`entry_for`), id prefix `:24` |
| plan shares behind a 2b allocation | `gk-forge/tools/CreatureBuildPlanGen` | `SpeciesBuildPlanner`, `--check` in CI |

The core/roll distinction is read from the container's existing `atoms`/`pool` split — **no new seed
field**, no model-chosen number (P1). Magnitudes stay table-owned: the atoms' own values and
`aptitudes.v{n}.json` edges. Input checks to run when either generator's output changes (they guard the
inputs, not this module):

```powershell
dotnet run --project gk-forge/tools/CreatureBuildPlanGen -- --check
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_species_effects.py -q
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesBuildPlanner"
``` `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/**` is owned by the active
`creature-seed-rederive-20260918` session; this module needs nothing from it.

## ActorHub gate

The projector composes nothing. Its rows reach the fold only through module 6's registered
`IActorStatSubsystem`, each carrying a non-empty GG-49 SourceId minted by `ContributionSourceIds`.

## Boundaries

- **Always:** call the existing aptitude functions, never re-type them; pin the parity test.
- **Ask first:** the `ContainerKind` addition and the §8.1 amendment (both reviewed vocabulary changes).
- **Never:** let a projection read a composed snapshot; mint a SourceId outside `ContributionSourceIds`;
  keep `SpeciesPassiveAtomSource` alongside the projector.

## Success Criteria

- [ ] One Core projector serves 1a (core), 1b and 2b; `SpeciesPassiveAtomSource` and the Data-layer
      atom builder are gone.
- [ ] Parity with `AptitudeResolver` is exact over the tested grid.
- [ ] 1a and 1b partition a fused instance with no overlap and no loss.
- [ ] Three SourceId helpers with labels; §8.1 amended in the same change.

## Open Questions

None for this module.

## Rulings applied 2026-09-18

- **R2** ([spec-rulings-2026-09-18.md](../spec-rulings-2026-09-18.md)), was OWNER Q1: module 5 hands
  `ProjectEmpire` the species allocation alone. The projector was indifferent to the answer and is
  unchanged.
