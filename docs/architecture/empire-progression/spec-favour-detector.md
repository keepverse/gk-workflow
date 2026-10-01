# Spec: `favour-detector`

**Program:** [`empire-progression`](../empire-progression-map.md) · **Wave B** · depends on: nothing.
**Rulings honoured:** R-Q6 (*"assert a maximum share per lead, with tolerance. No floor"*, paired with
the shape histogram), and the ideal's §5 *"Ship the detector, not the best build"*. **Status:** spec,
not reviewed, no build authorized.

## Objective

Make build-favour convergence **visible and, later, un-mergeable**, measured the one way the ideal
proved is honest.

The ideal's central measurement: the committed plan passes every check its generator makes and is still
converged, because the generator gates **point parity** while the convergence is in **which aptitude
leads** and **which shape a vector has**. Its warning, quoted because it is the design constraint:

> *"The obvious diversity metric would pass this corpus forever. Distinct exact share vectors reads 769
> of 904 — 85% unique … Any diversity assertion this program ships must measure the shape and the lead
> distribution, never vector distinctness."*

The figures above are a reading from 2026-09-17, not constants. This module reproduces them in code on
every regeneration, so no one has to count again.

## Design

### What is measured

A pure function over the planner's output. It knows nothing about files or models.

```csharp
namespace FusionRpg.Core.Creatures.Generation;

public sealed record BuildFavourMeasure(                                   // (new)
    long SpeciesCount,                                           // a reading, reported, never asserted
    IReadOnlyDictionary<string, long> LeadCountByAptitude,       // top share per species; tie → ordinal id
    long MaxLeadPermille,                                        // max(lead count) × 1000 / species
    string MaxLeadAptitude,
    IReadOnlyDictionary<string, long> ShapeCount,                // key: sorted-desc shares, "350,163,163,162,162"
    long LargestShapePermille,
    IReadOnlyDictionary<string, IReadOnlyDictionary<long, long>> LeanByPrimary);
                                                                 // the lean each primary received:
                                                                 // lean permille → species count

public static class BuildFavourMeasurer                                    // (new)
{
    public static BuildFavourMeasure Measure(SpeciesBuildResult plan, IReadOnlyList<AnchorRow> species);
}
```

> **Erratum, 2026-09-20 (EP2.2).** `LeanByPrimary` was declared above as `IReadOnlyDictionary<string, long>`
> — one lean per primary. That is a scalar over a quantity `per-species-lean` makes plural: once the
> lean is keyed to the species, one primary receives several leans at once, and this program's own
> success criterion is *"the measure shows leans varying within a primary"* — which a scalar cannot
> show, nor `per-species-lean`'s test 7 read. The field keeps its name and now carries the
> distribution (lean permille → species count). Today, with the lean still per primary, it has exactly
> one bucket per primary: the before-image the balance publish is judged against.

- **Lead** = the aptitude holding a species' largest share. Today that is always the primary (the lean
  is at least `leanMinPermille` 350‰, and the secondary gets at most 30% of the remaining 650‰, i.e.
  195‰). The measure still reads the vector, not the anchor, so it stays correct if a later tuning
  publish changes either value.
- **Shape** = the vector's non-zero shares sorted descending, ignoring which aptitude holds which. Two
  species with the same build *profile* on different aptitudes share a shape.
- **Distinctness of exact vectors is deliberately not measured.** Adding it later would re-open the
  trap the ideal named, so the record has no field for it.
- **The population is real creatures only.** A row marked `speciesKind: excluded` (`creature-seed`
  R-CS4, `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/schema.py:64-73`: *"never count as roster"*)
  is left out of every count and histogram; `SpeciesCount` is the count measured. The C# anchor reader
  carries `speciesKind` (landed by `creature-seed` CS13, commit `be3ac8a6`, as a raw string); the
  generation layer reads it through `AnchorSpeciesKind` (EP2.1), which names the vocabulary's three
  members — `creature` · `mimic` · `excluded` — and pins them, so `mimic` counts as roster and only
  `excluded` is left out. Every downstream consumer (`per-species-lean`'s ranks,
  `lead-relabel-pass`'s stage A, Phase 4) takes the population from this one measure, never re-filters.

### The artifact

`gk-forge/tools/CreatureBuildPlanGen` writes the measure beside the plan:

| File | Content | Gate |
|---|---|---|
| `gk-data/packs/fusion/data/generated/creatures/_species-build-plan.json` | unchanged | `--check` byte-compare (`gk-core/.github/workflows/ci.yml:129`) |
| `gk-data/packs/fusion/data/generated/creatures/_species-build-measure.json` (new) | the `BuildFavourMeasure`, canonically serialised | the same `--check` byte-compare |

Both are generated output, never hand-edited. `lead-relabel-pass` **reads** the measure; it never
recomputes crowding in Python. One implementation, in C#, where the planner already lives (S in SOLID).

### Report-only here; gating in `lead-relabel-pass`

The committed corpus fails any sensible lead cap today, which is the point of the program. Following the
repo's "green first, then gate" ruling (`solid-enforcement-map.md` ruling 2):

1. **This module:** measure, write, print a summary on every run. No threshold exists yet, so nothing
   can refuse.
2. **`lead-relabel-pass`:** once the corpus is green, it publishes the thresholds and adds planner
   Phase 4, which refuses a plan that breaks them (`SpeciesBuildRefusal`, the same type Phase 3 uses at
   `gk-core/src/FusionRpg.Core/Creatures/Generation/SpeciesBuildPlanner.cs:171-175`).

The report-only state is a step inside the program, never a finishing state.

### Why a one-sided cap, recorded so it is not "fixed" later

R-Q6 rejects a floor: *"the problem is the pvz design, if we have more strictly that become really
weird when we force a lot of attacker become tanker or support."* PvZ's roster is attack-heavy. So the
gate is a **per-aptitude** maximum, never a per-posture one: many offensive species may lead
Onslaught, Pierce, Precision, Might or Ferocity between them, and no aptitude is required to be common.
The shape cap then catches the failure a lead cap alone cannot see: a pass that trades one dominant
aptitude for another while every species keeps the same profile.

## Seedsmith / generator

| Item | Value |
|---|---|
| Generator | `gk-forge/tools/CreatureBuildPlanGen` (C#), not seedsmith. It gains one output file |
| Stage | after `SpeciesBuildPlanner.Plan` (`gk-forge/tools/CreatureBuildPlanGen/Program.cs`, the plan-write step) |
| New seed fields | none. The measure is derived output |
| Tuning owning magnitudes | none here. Thresholds are published by `lead-relabel-pass` into `species-build.v{n}.json` |
| Regenerate | `dotnet run --project gk-forge/tools/CreatureBuildPlanGen` |
| Check | `dotnet run --project gk-forge/tools/CreatureBuildPlanGen -- --check` |
| Python consumer | `lead-relabel-pass`'s new seedsmith stage reads the artifact; its tests live in `gk-forge/tools/seedsmith/tests/test_build_favour_relead.py` (new) |

## Tunables

None in this module (see above).

## ActorHub gate

**Not applicable.** Offline generation; no actor number.

## Integer widths and the power ladder

`long` counts and permille; `checked` on `count × 1000`. No level input.

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~BuildFavourMeasure|FullyQualifiedName~SpeciesBuildPlanner"
dotnet run --project gk-forge/tools/CreatureBuildPlanGen
dotnet run --project gk-forge/tools/CreatureBuildPlanGen -- --check
.\scripts\verify-change.ps1 -Paths <every touched path> -Session <session-id>
```

## Project structure

| Path | Change |
|---|---|
| `gk-core/src/FusionRpg.Core/Creatures/Generation/BuildFavourMeasure.cs` (new) | record + measurer |
| `gk-forge/tools/CreatureBuildPlanGen/Program.cs` | write and `--check` the measure |
| `gk-data/packs/fusion/data/generated/creatures/_species-build-measure.json` (new) | generated, committed |
| `gk-core/tests/FusionRpg.Core.Tests/Creatures/BuildFavourMeasureTests.cs` (new) | contract tests |

## Code style

```csharp
// Shape key: the profile, not the owner. Ordinal, invariant, deterministic.
static string ShapeKey(IReadOnlyDictionary<string, long> vector) =>
    string.Join(",", vector.Values.Where(v => v > 0).OrderByDescending(v => v));
```

## Testing strategy

All synthetic corpora, built in the test. **No test reads the size or counts of the real corpus.**

1. **Lead:** a corpus where one aptitude leads every species reports `MaxLeadPermille = 1000`; a
   corpus with twelve leads spread evenly reports the matching share.
2. **Shape is owner-blind:** two species with identical profiles on different aptitudes share one
   shape key.
3. **Ties are ordinal:** a vector with two equal top shares counts toward the ordinal-smaller id, stable
   across runs.
4. **Determinism:** input order does not change the artifact bytes (the planner's own property, extended
   to the measure).
5. **No distinctness field:** a reflection test asserts the record has no exact-vector uniqueness
   member. It pins the ideal's warning as a contract.
6. **The real corpus, contract only:** `--check` passes, and the committed measure reconciles with the
   committed plan (`Σ LeadCountByAptitude = Σ ShapeCount = SpeciesCount`). Internal reconciliation, the
   validation-ssot pattern, never a literal.

## Boundaries

- **Always:** measure lead and shape; write through the generator; keep the measure in C#.
- **Ask first:** turning the report into a gate before `lead-relabel-pass` (that is its job).
- **Never:** assert vector distinctness; pin a species or shape count; hand-edit either artifact.

## Success criteria

- [ ] The measure artifact is generated, committed, and `--check`ed in CI.
- [ ] Its figures reproduce the ideal's reading on today's corpus (verified once by hand at build, then
      never asserted).
- [ ] Contract tests 1 to 6 green.

## Open questions

None.

## Self-audit — the debate

- **"The lead is always the primary, so measure the anchor."** True under today's tuning. It is a
  property of two tunable values, not of the design, so reading the vector keeps the measure honest if a
  balance pass moves them.
- **"A generated artifact nobody gates is noise."** It is the before-image `per-species-lean` and
  `lead-relabel-pass` are judged against, and `--check` already gates that it is current.
