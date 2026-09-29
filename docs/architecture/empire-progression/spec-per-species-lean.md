# Spec: `per-species-lean`

**Program:** [`empire-progression`](../empire-progression-map.md) · **Wave B** · depends on:
[`favour-detector`](spec-favour-detector.md). **Ruling honoured:** R-Q8 (*"replace population-crowding
with a per-species signal"*; `crowdingFactor` *"stays in the file as a value that may fall to 0
rather than being deleted"*). **Status:** spec, not reviewed, no build authorized.

## Objective

Make a species' build **say something about that species.** Today the lean (how much of a species'
build sits on its primary aptitude) is a function of one thing, how crowded that primary is across the
corpus:

```csharp
// gk-core/src/FusionRpg.Core/Creatures/Generation/SpeciesBuildPlanner.cs:43-51 — the PRE-EP2.5 shape (a lean
// per primary). EP2.5 keyed the lean to the species; the current formula is at :59-79 and this quote
// is kept as the defect's own evidence, not as a description of HEAD.
crowdingPermille = count * 1000 / speciesCount;
contribution     = tuning.CrowdingFactor * crowdingPermille / 1000;
lean = Math.Clamp(tuning.LeanMaxPermille - contribution, tuning.LeanMinPermille, tuning.LeanMaxPermille);
```

So the corpus carries exactly one lean per primary aptitude, twelve values in all, and the crowding
term runs backwards for identity: the most typical creatures get the flattest builds. R-Q8 rules the
fix: key the lean to the species.

**Point parity is not touched.** The ideal is explicit (*"Do not design a fix that redistributes
points. That job is done, it is gated"*). Phase 2 (filler against the running deficit) and Phase 3 (the
`[parityFloorPermille, parityCeilingPermille]` refusal) run unchanged, and Phase 3 still refuses any
plan the new leans push out of band.

## Design

### Signals — a closed set, each a per-mille index in `[0, 1000]`

| Signal | Meaning | Computed from | Ready? |
|---|---|---|---|
| `specialisation` | How lopsided the species' own base stats are: a glass cannon or a wall is a specialist, a middling shooter is not | `abs(rank(attackBase) − rank(hpBase))` within its side, as per-mille ranks over the side's species, from `gk-data/packs/fusion/data/seed/creatures/_dump/type-base-stats.json` joined on `(side, gameTypeId)` | yes: the dump is committed (911 entries on 2026-09-17, a reading) |
| `pure` | The anchor's own "no distinct secondary" | `AnchorRow.Pure` (`gk-core/src/FusionRpg.Core/Creatures/Generation/AnchorRow.cs:41`), 1000 or 0 | yes |
| `threatRung` | How far up the threat ladder it sits | the rung's **ordinal** in `creature-threat.v{n}.json` `thresholds`, `(rung − 1) × 1000 / (rungs − 1)`; never its `thetaOffset`, which is a `Θ` quantity | yes. R6: a higher rung **does** sharpen the default build; ships at weight 0 until a tuning publish turns it on |
| `crowding` | Today's term, kept | unchanged | yes |

**Ranks, not raw values**, on purpose. Measured plant `hpBase` spans 300 to 640,000 (the ideal's
§"Closed by measurement"). A raw ratio would let a handful of giants define the scale for everyone,
the "fitted curve puts most of the roster in two rungs" failure that `threat-band` already hit and
fixed with a table. A per-mille rank is bounded and spreads by construction.

**A missing signal is neutral and recorded, never a failure.** A species with no base-stat row gets
`specialisation = 500` and appears in the measure artifact's `leanSignalsMissing` list. The same holds
for `threatRung` when the anchor's band is `unresolved` or names no rung in the loaded
`creature-threat.v{n}.json`: 500, listed. Rows marked `speciesKind: excluded` (`creature-seed` R-CS4) are
not in the rank population, so a phantom row cannot shift a real species' rank. The population comes from
`favour-detector`'s one filter (that spec says who adds the C# `speciesKind` read); this module never
re-filters. That is the
item ladder's *"never reject; narrow and record"* (`EnvelopeNarrowing.Apply`), as the ideal suggests.

### The formula — byte-identical at zero weights

```
penalty  = Σ over signals s ∈ {specialisation, pure, threatRung}:  w_s × (1000 − s) / 1000
lean     = clamp( leanMax − crowdingFactor × crowding / 1000 − penalty,  leanMin,  leanMax )
```

- With every new weight at 0, `penalty = 0` and the lean is **exactly today's** formula. The first
  commit ships the mechanism with zero weights and must leave `_species-build-plan.json` byte-identical.
  That is the refactor's proof.
- A specialist (signal near 1000) loses nothing; a generalist loses up to `w_s`. So sharp builds belong
  to sharp creatures, which is the inversion R-Q8 exists to fix.
- The ruling's second step is a **tuning publish**, not code: weights up, `crowdingFactor` down (to 0
  if the measure says so). Revertible by publishing the previous values.
- `leanMin`/`leanMax` stay the clamp, so every lean remains inside the band the parity gate was sized
  for.

This is not a power curve and not an `f(level)`. It is a share, and it reads no level.

### Phase ordering inside the planner

Phase 1 becomes "one lean per **species**" and moves inside the Phase 2 loop's input, computed before
the loop from signals that do not depend on processing order. So the plan stays input-order
independent, a property the planner's tests already pin.

## Seedsmith / generator

| Item | Value |
|---|---|
| Generator | `gk-forge/tools/CreatureBuildPlanGen` (C#) + `SpeciesBuildPlanner` (`gk-core/src/FusionRpg.Core/Creatures/Generation/SpeciesBuildPlanner.cs:44-79`, Phase 1). Not seedsmith |
| New inputs | the committed base-stat dump (read-only, captured by the game hook, not model output) and `creature-threat.v{n}.json` rung order |
| New seed fields | **none.** Every signal is derived by code from fields that already exist. No model authors a lean, a weight or a signal (P1; `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/schema.py:92-95` already forbids the model authoring `pure`) |
| Tuning owning magnitudes | `data/tuning/species-build.v{n}.json` |
| Regenerate | `dotnet run --project gk-forge/tools/CreatureBuildPlanGen`, then the downstream cascade below |
| Check | `dotnet run --project gk-forge/tools/CreatureBuildPlanGen -- --check` |
| Pytest | none; no Python changes |

**Cascade.** The plan feeds species allocation at runtime and is read directly, so a plan change needs
no species re-import. The measure artifact is regenerated in the same run.

**Cross-session note.** On 2026-09-18 an active session (`creature-seed-rederive`) holds
`gk-data/packs/fusion/data/seed/creatures/_dump/type-base-stats.json` in its paths. This module only reads the file, but its
build must start from whatever that session commits.

## Tunables

Two publishes to `species-build.v{n}.json`, both through the tool:

```powershell
# 1. mechanism, zero weights (plan byte-identical)
python gk-core/tools/tuning/publish.py species-build --label "R-Q8 lean signals, zero weights" `
  --add-key ':leanSignalWeights={"specialisation":0,"pure":0,"threatRung":0}'
# 2. the balance step, values chosen against the measure artifact (a first guess is sanctioned by the
#    file's own _meta; calling it balance is not)
python gk-core/tools/tuning/publish.py species-build --label "R-Q8 per-species lean" `
  "leanSignalWeights.specialisation=<w>" "leanSignalWeights.pure=<w>" "crowdingFactor=<c>"
```

- `leanSignalWeights.*`: `long`, permille of lean, ≥ 0. Missing key is a load rejection naming it.
- `threatRung` ships at **0**. R6 ([spec-rulings-2026-09-18.md](../spec-rulings-2026-09-18.md)) ruled the direction: *"Yes. The signal still ships at weight
  0; a tuning publish turns it on."* So its eventual weight is **positive**: a species on a higher rung
  has a larger `s`, pays a smaller `(1000 − s)` penalty, and keeps its lean nearer `leanMax`, which is
  the sharper build. Turning it on is a balance publish
  through `gk-core/tools/tuning/publish.py`, not a code change and not a new question. A negative weight is out
  of bounds (`leanSignalWeights.*` ≥ 0 above).
- Version numbers are the next free ones at landing; the map's "Tuning version sequence" table orders
  every `species-build` publish in this program (Wave A's `specimen-respec-price` normally takes the
  first). Each publish moves every pin of the version it replaces (`rg -l "species-build\.v[0-9]+\.json"
  src tools tests --glob "*.cs"`, which includes `gk-core/tests/FusionRpg.Core.Tests/Creatures/SpeciesBuildPlannerTests.cs:182`).

## ActorHub gate

**Not applicable at generation.** The plan reaches actors only as allocation shares through the existing
species and unique seams.

## Integer widths and the power ladder

`long` throughout, `checked` on every `w × signal` product (≤ 1000 × 1000 per term, far inside range).
No level input, so no `Θ` or `P(Θ)` read, and the threat rung is used as an **ordinal**, not as its
`thetaOffset`, precisely so this does not become a second consumer of a power quantity.

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~SpeciesBuildPlanner|FullyQualifiedName~LeanSignal"
dotnet run --project gk-forge/tools/CreatureBuildPlanGen
dotnet run --project gk-forge/tools/CreatureBuildPlanGen -- --check
.\scripts\verify-change.ps1 -Paths <every touched path> -Session <session-id>
```

## Project structure

| Path | Change |
|---|---|
| `gk-core/src/FusionRpg.Core/Creatures/Generation/SpeciesBuildPlanner.cs` | per-species lean |
| `gk-core/src/FusionRpg.Core/Creatures/Generation/LeanSignals.cs` (new) | the closed signal set and rank computation |
| `gk-core/src/FusionRpg.Core/Creatures/Generation/SpeciesBuildTuning.cs` | `LeanSignalWeights` |
| `gk-forge/tools/CreatureBuildPlanGen/Program.cs` | reads the base-stat dump and threat rung order |
| `data/tuning/species-build.v{n}.json` (new) | two publishes |
| `gk-data/packs/fusion/data/generated/creatures/_species-build-plan.json`, `gk-data/packs/fusion/data/generated/creatures/_species-build-measure.json` | regenerated |
| `gk-core/tests/FusionRpg.Core.Tests/Creatures/SpeciesBuildPlannerTests.cs`, `gk-core/tests/FusionRpg.Core.Tests/Creatures/LeanSignalsTests.cs` (new) | below |

## Code style

```csharp
static long LeanFor(AnchorRow s, LeanSignalSet signals, long crowdingPermille, SpeciesBuildTuning t)
{
    long penalty = 0;
    foreach (var (name, weight) in t.LeanSignalWeights)          // closed set, validated at load
        checked { penalty += weight * (1000 - signals.For(s.SpeciesId, name)) / 1000; }
    long crowding;
    checked { crowding = t.CrowdingFactor * crowdingPermille / 1000; }
    return Math.Clamp(t.LeanMaxPermille - crowding - penalty, t.LeanMinPermille, t.LeanMaxPermille);
}
```

## Testing strategy

1. **Byte-identical at zero weights.** Planning a fixed synthetic corpus with all new weights at 0
   yields exactly the pre-change vectors (captured once as expected values in the test, derived from the
   old formula in the test body, not pasted literals).
2. **Specialists lean sharper.** In a synthetic corpus sharing one primary, the species with the higher
   `specialisation` gets the higher lean once its weight is non-zero.
3. **Ranks are bounded.** Every signal lies in `[0, 1000]` for any input, including extreme hp values.
4. **Missing input is neutral and recorded.** A species with no base-stat row gets 500 and is listed.
5. **Parity still refuses.** A weight large enough to push an aptitude out of the parity band makes
   `Plan` throw `SpeciesBuildRefusal`, unchanged.
6. **Order independence** of the whole plan, the planner's existing property, still holds.
7. **The lean spread widens.** On the committed corpus after the balance publish, the measure reports
   more than one lean per primary. Asserted as a relation on the artifact ("some primary has ≥ 2 leans"),
   never a count.

## Boundaries

- **Always:** ship the mechanism byte-identical first; balance by publish.
- **Ask first:** a new signal (it is a closed set). A non-zero `threatRung` weight needs no ruling (R6
  gave the direction); it is a balance publish chosen against the measure artifact, like the others.
- **Never:** redistribute points; use `thetaOffset` or any `Θ` value as a lean input; delete
  `crowdingFactor`.

## Success criteria

- [ ] Mechanism merged with the plan byte-identical.
- [ ] Balance publish merged; the measure shows leans varying within a primary.
- [ ] Parity gate still green; `--check` green.

## Open questions

None.

## Rulings applied 2026-09-18

- **R6** ([spec-rulings-2026-09-18.md](../spec-rulings-2026-09-18.md)), was map question 3: a higher threat rung makes a species' default build sharper. The
  signal ships at weight 0 (mechanism byte-identical); the direction is recorded above, and a tuning
  publish turns it on.

## Self-audit — the debate

- **"Rank-based specialisation throws away real magnitude."** On purpose. The lean is a share of a
  build, not a power number; the magnitude already reaches the actor through `P(Θ)` and the base-stat
  bake. Using it twice would double-count power into shape.
- **"Zombies and plants have different stat meanings."** Ranks are taken within a side, so a zombie is
  compared with zombies.
- **"This could flatten the lead histogram's benefit later."** It does the opposite: the map orders it
  before `lead-relabel-pass` precisely because with crowding still in the lean, a flatter lead would
  flatten every lean with it.
