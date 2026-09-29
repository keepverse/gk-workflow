# Spec: `lead-relabel-pass`

**Program:** [`empire-progression`](../empire-progression-map.md) · **Wave B** · depends on:
[`per-species-lean`](spec-per-species-lean.md) (and through it `favour-detector`). **Rulings
honoured:** the owner's build favour pipeline (*"deterministic engine to second run (new pipeline) and
llm engine to solve diversity base on the original run"*, ideal §4a), R-Q6 (one-sided lead cap with
tolerance, paired with the shape histogram). **Status:** spec, not reviewed, no build authorized.

## Objective

Change **which aptitude a crowded species leads**, the one thing the deterministic planner is not
allowed to change, and then make convergence un-mergeable.

The ideal's diagnosis, verified in code: the lead is `AnchorRow.AptitudePrimary`
(`gk-core/src/FusionRpg.Core/Creatures/Generation/AnchorRow.cs:41`), authored by one model call per species
with no view of the corpus (`gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/prompts.py:167-193`),
and the planner only sizes it. So 42% of species lead one aptitude (a 2026-09-17 reading) because the
identity step converged and nothing downstream may disagree. **The gap is re-leading, not
re-sharing.**

## Design

### Four stages, only one of them a model

```
M  measure   (code, C#)     favour-detector's artifact: lead and shape histograms, current leans
L  label     (model)        for each species in an over-cap lead: "which aptitude should it lead?"
                            closed enum of 12, three samples, majority vote; staying put is legal
A  accept    (code, Python) deterministic quota: accept a re-label only while the source lead is
                            over the cap and the target lead stays under it; record every refusal
P  plan      (code, C#)     the unchanged planner re-runs on the re-led anchors; Phase 3 parity
                            still refuses; Phase 4 (new) lead cap and shape cap refuse
```

**The crowding figure is computed by code and handed to the model as a constraint.** The ideal is
specific that a model asked "make this one different" 904 times, one creature at a time, can converge on
a new dominant answer (Doshi and Hauser: individual novelty up, inter-item similarity up 10.7%). Two
things stop that here, and neither is the prompt:

1. **Stage A's quota.** Acceptances run in ordinal `speciesId` order. A re-label is accepted only if
   its source aptitude's running lead count is still above the cap and its target's running count plus
   one stays at or below it. So no pass can create a new over-cap lead, by construction.
2. **Phase 4's shape cap.** A pass that moves leads around while every species keeps one profile is
   refused by the planner.

**What the model may emit is unchanged: a label.** The schema is the pass-1 shape exactly: one property,
an enum of the twelve aptitude ids, `additionalProperties: false`, **wrapped in `_blocked_variant`**
(`gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/prompts.py:61-79`, applied to pass 1 at `:186`), and
audited by `audit_schema` (`gk-forge/tools/seedsmith/seedsmith/pipeline/model.py:112-115`). The wrapper is not
optional: `audit_schema` rejects a schema *"that offers it no way to decline"* (`gk-forge/tools/seedsmith/seedsmith/pipeline/model.py:115`, enforced at `:202`), so a bare
enum would fail the audit. A sample whose `blocked` is non-empty is **not a vote**; fewer than a majority
of real votes resolves as `unresolved` and keeps the current primary. The prompt may show numbers (the
measured crowding), and the output may not contain any. `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/schema.py:92-95`'s rule, *"never let the
model author posture/pure/basis/speciesKind"*, carries over: `posture` and `pure` are re-derived by code
after a re-label, and `speciesKind` does not read the primary — no `derive.py` anywhere in
`gk-forge/tools/seedsmith/seedsmith` handles `speciesKind` re-derivation at all, confirming there is no code
path to touch — so it is untouched.

### Who is asked

Only species whose current lead aptitude's corpus share is above `leadCapPermille`, read from the
measure artifact. Species in an under-cap lead are never re-labelled. That bounds model spend and keeps
the pass from touching species with no problem.

**Rows marked `speciesKind: excluded` are never asked and never counted.** `creature-seed` R-CS4 marks a
phantom row *"NOT a creature. Never spawn, never draw, never count as roster"*
(`gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/schema.py:64-73`). The filter lives once, in
`favour-detector`'s measure; stage A's lead counts are read from that measure and its candidate list is
drawn from the measured population, so an excluded row is never asked and never counted, and the cap is
never judged on creatures that do not exist.

**Landing order against `creature-seed`.** The `creature-seed-rederive` session (active 2026-09-18) owns
`gk-data/packs/fusion/data/seed/creatures/species/**` and `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/**` in its session paths.
This pass writes the same anchors through the same adapter tree, so it runs only after that session's
re-derivation is committed and its record is closed, and starts from that commit.

### Where the answer lives (map D4)

The re-label is written **into the anchor**, through seedsmith's existing emit
(`gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/emit.py:20`, `entry_for`), with provenance:

```json
"provenance": {
  "relead": {
    "fromPrimary": "Onslaught",
    "promptVersion": 1,
    "votes": ["Pierce", "Pierce", "Onslaught"],
    "confidence": "split",
    "measureHash": "<sha256 of the measure artifact it read>",
    "outcome": "accepted"
  }
}
```

An overlay file was considered and rejected: seven C# tools call `AnchorRowReader.ReadAll`
(`gk-forge/tools/CreatureBuildPlanGen/Program.cs:86`, `gk-forge/tools/CreatureSpeciesGen/Program.cs:85`,
`gk-forge/tools/CreatureSpeciesImport/Program.cs:83`, `gk-forge/tools/CreatureQualityReport/Program.cs:80`,
`gk-forge/tools/CreatureRecipeDistributionIndex/Program.cs:71`, `gk-forge/tools/CreatureRecipeReconcileInput/Program.cs:77`,
`gk-core/src/FusionRpg.Core/Delve/Encounter/EncounterCorpusBuilder.cs:39`), and each would have to apply it.
Writing the anchor gives every consumer one truth with no code change.

**Staleness.** A re-label is invalid if pass 1 re-ran for that species: its `aptitude-primary` prompt
version or its dump hash changed (`gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/emit.py:71`, `stale_fields`). Then the relead block is dropped, the
pass-1 answer stands, and the species is queued for pass 2 again. So pass 1 can always run, and pass 2
always runs after it.

**Secondary.** If the new primary equals the current secondary, the two swap, so no species ends with
primary == secondary (the corruption `SpeciesBuildPlanner.cs:110-115` guards against). Otherwise the
secondary stays.

### Phase 4 — the gate

Added to `SpeciesBuildPlanner.Plan` after Phase 3, reading `BuildFavourMeasurer`'s output:

- `MaxLeadPermille ≤ leadCapPermille + leadCapTolerancePermille`, else `SpeciesBuildRefusal`.
- `LargestShapePermille ≤ shapeCapPermille`, else `SpeciesBuildRefusal`.
- **No floor on any aptitude** (R-Q6). A test pins that absence (Testing 6).

It lands in the **same commit** as the regenerated green corpus, so `main` never carries a red gate.

## Seedsmith / generator

| Item | Value |
|---|---|
| Adapter | `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/build_favour/` (new): `relead.py` (pipeline spec, brief, schema), `accept.py` (stage A, pure), `run.py` (orchestration) |
| Model stage | one `PipelineSpec` in the pass-1 shape (`gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/prompts.py:177-193`), **not** added to `PIPELINES`. `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/prompts.py:469` asserts that dict has eight members, and `gk-forge/tools/seedsmith/tests/test_classify_pipelines.py:57` pins it too: a closed vocabulary. Pass 2 is a separate pass, not a ninth classifier, so neither pin moves; a test asserts the relead spec's id is not a `PIPELINES` key |
| Vote | `resolve_vote` (`gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/vote.py:26`); unresolved keeps the current primary |
| New seed fields | `provenance.relead` (above). Labels only: `fromPrimary`, the vote values and `outcome` are closed enums; `promptVersion` is an index; `measureHash` is an identifier. **No model-chosen number** (P1, enforced by `audit_schema`) |
| Changed seed field | `aptitudePrimary` (and `aptitudeSecondary` on a swap), classified by pass 2 instead of pass 1, with the pass-1 value kept in provenance |
| Derived fields re-derived | `posture`, `pure` (`gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/derive.py`) |
| CLI | `python -m seedsmith creatures build-favour` (new verb under the creatures parser, `gk-forge/tools/seedsmith/seedsmith/report/cli.py:2685`), with `--dry-run` and `--limit` like its siblings |
| Tuning owning magnitudes | `data/tuning/species-build.v{n}.json`: the caps below. The pass reads them; the model never sees them as something it may change |
| Pytest | `gk-forge/tools/seedsmith/tests/test_build_favour_relead.py` (new), `gk-forge/tools/seedsmith/tests/test_anchor_emit.py` (provenance round-trip) |
| Preflight | the `seedsmith-preflight` skill before any run that calls a model |

**Regenerate, in order** (the anchor cascade; a partial run leaves downstream seeds stale):

```powershell
dotnet run --project gk-forge/tools/CreatureBuildPlanGen                   # refresh the measure pass 2 reads
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m seedsmith creatures build-favour
dotnet run --project gk-forge/tools/CreatureSpeciesGen                      # anchors feed species defs
dotnet run --project gk-forge/tools/CreatureBuildPlanGen                    # plan + measure on re-led anchors
dotnet run --project gk-forge/tools/CreatureRecipeReconcileInput
dotnet run --project gk-forge/tools/CreatureRecipeDistributionIndex
# then every one of the above with --check, as CI runs them
```

## Tunables

Published to `species-build.v{n}.json` **before** stage L runs (the pass needs the target), and read by
the planner's Phase 4 from the commit that adds it:

```powershell
python gk-core/tools/tuning/publish.py species-build --label "R-Q6 lead and shape caps (working values)" `
  --add-key ":leadCapPermille=<cap>" --add-key ":leadCapTolerancePermille=<tol>" --add-key ":shapeCapPermille=<cap>"
```

- All `long`, permille of species. First values are a guess the file's own `_meta` sanctions (*"shipping
  a guess is fine, calling it balance is not"*), chosen at build from the measure artifact and recorded
  with that label.
- They sit beside `parityFloorPermille`/`parityCeilingPermille`, which gate a different axis (points),
  as the ideal's Tunables table specifies.

## ActorHub gate

**Not applicable at generation.** The re-led plan reaches actors only as allocation shares through the
species and unique seams.

## Integer widths and the power ladder

`long` permille and counts; `checked` on `count × 1000`. No level input.

## Commands

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_build_favour_relead.py gk-forge/tools/seedsmith/tests/test_anchor_emit.py -q
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesBuildPlanner|FullyQualifiedName~BuildFavourMeasure"
dotnet run --project gk-forge/tools/CreatureBuildPlanGen -- --check
.\scripts\verify-change.ps1 -Paths <every touched path> -Session <session-id>
```

## Project structure

| Path | Change |
|---|---|
| `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/build_favour/relead.py` (new) | pipeline spec, brief, schema |
| `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/build_favour/accept.py` (new) | stage A, pure |
| `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/build_favour/run.py` (new) | orchestration, stale handling |
| `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/provenance.py` | `relead` block |
| `gk-forge/tools/seedsmith/seedsmith/report/cli.py` | `creatures build-favour` verb |
| `gk-core/src/FusionRpg.Core/Creatures/Generation/SpeciesBuildPlanner.cs` | Phase 4 |
| `gk-core/src/FusionRpg.Core/Creatures/Generation/SpeciesBuildTuning.cs` | three caps |
| `gk-data/packs/fusion/data/seed/creatures/species/**` | regenerated by the pass, never hand-edited |
| `gk-data/packs/fusion/data/generated/creatures/**` | regenerated by the cascade |
| `gk-forge/tools/seedsmith/tests/test_build_favour_relead.py` (new) | below |

## Code style

```python
def accept(candidates, lead_counts, cap_count):
    """Stage A. Pure and deterministic: ordinal order, running counts, every outcome recorded."""
    counts = dict(lead_counts)
    decisions = []
    for c in sorted(candidates, key=lambda c: c.species_id):
        if c.voted is None:
            decisions.append(Decision(c.species_id, c.current, "unresolved"))
        elif c.voted == c.current:
            decisions.append(Decision(c.species_id, c.current, "kept-by-vote"))
        elif counts[c.current] <= cap_count:
            decisions.append(Decision(c.species_id, c.current, "source-under-cap"))
        elif counts[c.voted] + 1 > cap_count:
            decisions.append(Decision(c.species_id, c.current, "target-full"))
        else:
            counts[c.current] -= 1
            counts[c.voted] += 1
            decisions.append(Decision(c.species_id, c.voted, "accepted"))
    return decisions
```

## Testing strategy

All pytest and C# tests use synthetic corpora; none reads the real species count.

1. **Schema carries no number and can decline.** `audit_schema` passes on the pass-2 schema; a variant
   with a numeric property fails it; a variant without the `_blocked_variant` wrapper fails it. A sample
   with a non-empty `blocked` counts as no vote.
1b. **Excluded rows.** A synthetic corpus with a `speciesKind: excluded` row in an over-cap lead: the row
   is never a candidate and never counted by stage A.
2. **Quota is a hard bound.** For any candidate list and any votes, stage A never leaves a target above
   `cap_count`, and never moves a species out of an under-cap source. Property-tested over random
   inputs with a fixed seed.
3. **Determinism.** The same candidates, votes and counts give byte-identical decisions whatever the
   input order.
4. **Unresolved keeps.** A 1-1-1 vote keeps the current primary with outcome `unresolved`.
5. **Staleness.** Bumping the `aptitude-primary` prompt version for a species drops its relead block and
   queues it.
6. **No floor.** A Phase 4 test with one aptitude led by zero species passes; only the maxima refuse.
7. **Phase 4 refuses.** A synthetic corpus over the lead cap, and one over the shape cap, each throw
   `SpeciesBuildRefusal` naming the cap.
8. **The committed corpus, as a contract.** `--check` passes with Phase 4 on; every `relead` block's
   `fromPrimary`, votes and outcome are legal enum members; every accepted row's `aptitudePrimary`
   equals its winning vote.

## Boundaries

- **Always:** code computes crowding and quotas; the model returns a label; every refusal is recorded;
  run the whole cascade.
- **Ask first:** re-labelling species in under-cap leads; a floor; letting the model see or change a
  cap; adding pass 2 to `PIPELINES`.
- **Never:** a model call at runtime or in CI; hand-editing any anchor or generated file; a re-label
  without provenance.

## Success criteria

- [ ] Pass 2 runs end to end with preflight, and its answers are committed with provenance.
- [ ] Phase 4 gates in CI with the corpus green.
- [ ] Parity (Phase 3) still gates and passes.
- [ ] The measure artifact shows no aptitude above cap + tolerance and no shape above its cap.

## Open questions

None. The cap values are a sanctioned first guess recorded as working values; R-Q6 left them as a task.

## Self-audit — the debate

- **"Stage A can refuse the model's best answer."** Yes, and it records why. The model judges fit;
  code judges the corpus. That is the ideal's division of labour, and it is what makes the pass unable
  to trade one 42% lead for another.
- **"Ordinal acceptance order favours species early in the alphabet."** It is a deterministic tie-break
  on who gets a scarce target slot, the same ordinal tie-break the planner already uses in Phase 2. A
  fairer order would need a second criterion nobody has ruled; the alternative, randomness, would break
  byte-identical regeneration.
- **"If most crowded species vote to stay, the gate stays red."** Then the cap is a balance number the
  corpus cannot meet by relabelling, and the right move is a tuning publish, recorded, not a forced
  relabel. The build reports this instead of shipping a red gate.
