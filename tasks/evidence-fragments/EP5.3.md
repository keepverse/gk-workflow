# EP5.3 - blocked as written, with the proof

**Row NOT closed.** Its first clause cannot pass as written on this tree, and shipping it either way
would break a named rule. What lands here is the PROOF test and the blocker record; a ruling is needed.
Session `empire-progression-4` - branch `cmdc/ep-4`.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Proof: wiring the scorer into the AI species default is not a no-op on today's beliefs | `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~BuildScorer"` | `Passed! - Failed: 0, Passed: 5, Skipped: 0, Total: 5` - `Wiring_the_scorer_into_the_ai_species_default_needs_real_belief_content`: the ladder's own rung for a species context (plan row present, favour allowed) is `species-favour` (`Assert.Equal` against `AssignLadder.Suggest`), the SAME candidate set scored with neutral inputs returns `even` (`Assert.NotEqual`), and giving the ladder's rung a real need edge makes it win on SCORE with no tie-break — i.e. the difference is the missing content, not the scorer | `gk-core/tests/FusionRpg.Core.Tests/World/Ai/BuildScorerTests.cs` |
| Scoped verification of the new test | `pwsh -NoProfile -Command "& './scripts/verify-change.ps1' -Paths 'gk-core/tests/FusionRpg.Core.Tests/World/Ai/BuildScorerTests.cs' -Session empire-progression-4"` | `EXIT=0` - core fallback green | - |

**Why the row cannot be closed, read in code (three causes, not a symptom):**

1. **The belief inputs have no source.** `BuildRung`'s `NeedFit` is "how badly this empire wants what
   this rung's lean produces". The only `INeedVector` in the tree is `UniformNeeds`
   (`gk-core/src/FusionRpg.Core/World/Ai/INeedVector.cs:31-41`), constant 1000, and its two axes are
   `ForSlotKind`/`ForElement` — sector/economy needs, with no mapping to an aptitude rung. The spec's own
   note (`spec-ai-build-scorer.md`, §Seedsmith) says that mapping is a future seedsmith stage; supplying
   it from code would be a balance constant on the balance surface.
2. **Neutral inputs CHANGE the AI species build.** With `NeedFit`/`CounterFit` neutral, every candidate
   ties and the committed ordinal tie-break (`BuildScorer.Choose`, EP5.1) returns `even` — but the
   ladder's rung for a species context is `species-favour`, which is what the AI species baseline
   materialises today (`SpeciesAllocation.Baseline(SpeciesBuildPlanCatalog.SharesFor(speciesId), …)`).
   So the wiring as written would move every AI species' build, with no balance justification, and would
   owe the H1 golden commit a list of moved pins.
3. **The alternative is the repo's named failure mode.** Wiring only the rungs the ladder can actually
   reach (one candidate: `species-favour`) preserves behaviour byte for byte and is the "same allocation
   path, no new path" the acceptance asks for — but it is a complete, tested mechanism with constant
   content, which is precisely why this module was deferred ("Do not ship a fourth neutral-constant
   weight table") and the reason given in EP4.17's own family of rulings.

**What the erratum should decide:** either (a) accept the behaviour-preserving wiring (the scorer runs a
one-candidate set and the turn report carries `Considerations.Weakest`), and say so as the intended shape
until `sector-development` lands; or (b) leave EP5.3 open with EP5.1/EP5.2 landed as the mechanism, which
is where this lane stopped. The turn-report half needs its own ruling too: `DistrictAssaultResolver`
(Core) has no `TurnReport` handle (`HubInputsFor` returns `BattleHubInputs`), so naming `Weakest` on a
turn needs a new field on that Core record plus a report kind, i.e. more than the row's "S".
