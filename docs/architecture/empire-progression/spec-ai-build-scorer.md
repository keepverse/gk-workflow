# Spec: `ai-build-scorer`

**Program:** [`empire-progression`](../empire-progression-map.md) · **Wave D, deferred** · depends on:
[`ai-empire-species`](spec-ai-empire-species.md); external `sector-development` (an economy to score
against). **Ruling honoured:** R-Q5 (*"multiplicative with a zero-veto and a compensation factor, in
the new scorer only"*; existing additive scorers migrate nothing). **Status:** spec, BUILT IN PART
(2026-09-21, ep-4): EP5.1 (`BuildScorer`, over `Considerations.Score`) and EP5.2 (the published
`buildScorer` block, `ai.v2` -> `ai.v3`) landed on the orchestrator's ruling, because EP5.1's own
acceptance tests with `UniformNeeds`; EP5.3 (feeding the chosen rung into the allocation path and the
turn report) is still open, and the rung-to-need MAPPING it will read is the part that needs the real
economy — see the program todo.

## Objective

Let an AI empire choose **which build rung** a species should follow (favour, a posture lean, a preset
the AI holds) from its own situation, instead of always taking the ladder's first legal rung. This is
the "AI decision weights" question the ideal says becomes interesting only after its questions 1 to 3.

## The finding that shapes this spec (map X2)

R-Q5 was ruled as if the repo had no multiplicative scorer. It has one, shipped and inert:

| Property R-Q5 asks for | Already in `Considerations` |
|---|---|
| Product of considerations | `gk-core/src/FusionRpg.Core/World/Ai/Utility/Consideration.cs:37-53` |
| Zero is a hard veto with an early-out | `Consideration.cs:44-48` |
| Arity compensation, Dave Mark's form | `Consideration.cs:61-75` (`modifier = 1000 − 1000/n`, make-up scaled by the score) |
| Response curves | six integer curves, `gk-core/src/FusionRpg.Core/World/Ai/Utility/ResponseCurves.cs:4-55` (no logistic, on purpose: integer determinism) |
| "Why did it choose that" | `Considerations.Weakest`, `Consideration.cs:83-98` |
| Its own comment on why it waits | `Consideration.cs:23`: *"Nothing calls this yet … scoring wants an economy to score against and there is not one until `sector-development`."* |

So this module **consumes** `Considerations.Score` and writes no arithmetic. Writing a second scorer for
the same shape would be the parallel-path defect (map D6).

## Why it is deferred, not built now

The ideal's own rule: *"Do not ship a fourth neutral-constant weight table."* A build scorer's
considerations would read the empire's needs, and `INeedVector`'s only implementation returns 1000 for
everything (`gk-core/src/FusionRpg.Core/World/Ai/INeedVector.cs:31-41`). A scorer over neutral needs picks the
same rung as the ladder every time: a complete, tested mechanism with constant content, the repo's named
failure mode. It becomes buildable when `sector-development` gives `INeedVector` real values.

## Design (for when it is unblocked)

```
for each candidate rung r available to the species (favour, posture-force/finesse/bastion, held preset):
    considerations(r) = [
        need fit       : ResponseCurve.Linear   over the empire's need for what r's lean produces
        counter fit    : ResponseCurve.Smoothstep over how well r counters the enemy's observed posture
        continuity     : ResponseCurve.Threshold  vetoes a change within the re-pattern cooldown
    ]
    score(r) = Considerations.Score(considerations(r))
choose argmax score; ties by ordinal rule id; record Considerations.Weakest for the turn report
```

- **Determinism.** Pure function of fogged belief and tuning, as `FrontierRulesPolicy` is. No seed is
  consumed; no model call ever.
- **Rate limit.** The continuity veto reuses `zomboss-adaptive`'s cooldown idea
  (`docs/architecture/species-build/spec-zomboss-adaptive.md`, *"the rate limit is not optional"*) so an
  AI that re-builds every turn cannot converge on "every player build is equally bad".
- **Fairness.** The scorer only picks among distributions the ladder could already produce, at the same
  budget. *"A harder Zomboss is a higher `Θ` or a better allocation, never a stat nobody could have
  had"* (`class-system-ideal.md` §6.1, quoted in `spec-zomboss-adaptive.md`).
- The chosen rung feeds `ai-empire-species`'s default in place of the ladder's first legal rung. No new
  allocation path.

## Seedsmith / generator

**None now.** If considerations ever need per-species weights (for example, which need a species' build
serves), they are emitted by a seedsmith **deterministic** stage in the `type-weights.json` family
(largest remainder, sums to 1000, `--check`), never by a model: *"Model calls: none — permanently, not
provisionally"* (`gk-forge/tools/seedsmith/seedsmith/adapters/actions/distribution_planner/derive.py` precedent,
cited in the ideal). That stage would be specified with this module's unblocking, against the real
economy.

## Tunables

`data/tuning/ai.v{n}.json` (new version), a `buildScorer` block: one curve id and one threshold per
consideration, and the continuity cooldown. Global defaults with per-empire overrides, per the ideal's
Zubek note. Published by `gk-core/tools/tuning/publish.py`, never hand-edited.

## ActorHub gate

**Neither.** The scorer picks a distribution. The resulting allocation reaches Hub through
`ai-empire-species`'s existing species seam.

## Integer widths and the power ladder

Per-mille `int` in `[0, 1000]`, the bounded range `ResponseCurves` already uses; the product is widened
to `long` before multiplying (`Consideration.cs:41,49`). No level-derived number.

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Consideration|FullyQualifiedName~BuildScorer"
```

## Project structure

| Path | Change |
|---|---|
| `gk-core/src/FusionRpg.Core/World/Ai/BuildScorer.cs` (new) | candidate rungs → considerations → `Considerations.Score` |
| `gk-core/data/tuning/ai.v3.json` (new) | `buildScorer` block — LANDED: `python gk-core/tools/tuning/publish.py ai --add-key ':buildScorer={...}' --add-key '_meta:buildScorerNote="..."'` (v2 -> v3) |
| `gk-core/tests/FusionRpg.Core.Tests/World/Ai/BuildScorerTests.cs` (new) | below |

## Code style

```csharp
var best = candidates
    .Select(r => (Rule: r, Score: Considerations.Score(ConsiderationsFor(r, belief, tuning))))
    .OrderByDescending(x => x.Score)
    .ThenBy(x => x.Rule, StringComparer.Ordinal)
    .First();
```

## Testing strategy

1. **Reuse, not rewrite.** A reflection test asserts `BuildScorer` computes no product itself (it calls
   `Considerations.Score`).
2. **Veto.** A zero on continuity removes a rung whatever its other scores.
3. **Neutral needs make no difference.** With `UniformNeeds`, the scorer picks the ladder's rung. This
   is the test that documents why the module waited.
4. **Determinism.** Same belief and tuning, same pick; ordinal tie-break.

## Boundaries

- **Always:** consume `Considerations`; stay deterministic; pick only ladder distributions.
- **Ask first:** building before `INeedVector` carries real values.
- **Never:** a second product or compensation function; a model call; migrating `ValueMap` or `SiegeAi`
  to multiplicative (R-Q5: *"Migrate nothing"*).

## Success criteria (at unblocking)

- [ ] `INeedVector` has a non-neutral implementation from `sector-development`.
- [ ] The AI empire's species follow scored rungs, with the weakest consideration in the turn report.

## Open questions

None. The blocker is an unbuilt economy, named as a dependency.

## Self-audit — the debate

- **"R-Q5 says 'in the new scorer only'; reusing an existing scorer contradicts it."** The ruling's
  substance is the arithmetic and the scope (no migration of the additive scorers). `Considerations` is
  that arithmetic, unused by anything, and is not one of the additive scorers. Reusing it satisfies both
  halves; writing a twin would violate the S in SOLID.
