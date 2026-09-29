# EP5.1 - `BuildScorer` over `Considerations.Score` (no arithmetic of its own)

`gk-core/src/FusionRpg.Core/World/Ai/BuildScorer.cs` (new): `BuildRung(ruleId, needFit, counterFit)` →
three considerations (`needFit` Linear, `counterFit` Smoothstep, `continuity` Threshold at the cooldown) →
`Considerations.Score` → argmax, ties by ordinal rule id. `BuildChoice` carries the winner, its score, its
considerations and `Considerations.Weakest` (EP5.3's turn-report line). The two belief inputs are
SUPPLIED, never derived here — the rung→need mapping is the part the spec defers to the economy.
Commit `@EP5.1` - session `empire-progression-4` - branch `cmdc/ep-4`.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| test 1: a reflection test - the scorer computes no product itself (it calls `Considerations.Score`) | `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~BuildScorer|FullyQualifiedName~Consideration"` | `Passed! - Failed: 0, Passed: 26, Skipped: 0, Total: 26` - `The_scorer_computes_no_product_itself` (source scan: the one scoring call is `Considerations.Score(considerations)`, no `Compensate(`, no `*` in the file, and the ordinal tie-break pinned) | `gk-core/src/FusionRpg.Core/World/Ai/BuildScorer.cs` (new), `gk-core/tests/FusionRpg.Core.Tests/World/Ai/BuildScorerTests.cs` (new) |
| test 2: a zero on continuity vetoes the rung | same | `Passed: 26` - `A_zero_on_continuity_vetoes_the_rung_whatever_its_other_scores`: the STRONGER rung (1000/1000) loses to 300/300 at 0 turns elapsed, and wins at the cooldown — so the veto is the cause; the vetoed pick's score is asserted lower | same |
| test 3: with `UniformNeeds` it picks the ladder's rung | same | `Passed: 26` - `With_uniform_needs_it_picks_the_ladders_rung`: the rung comes from `AssignLadder.Suggest` on the AI's own context (asserted `even`, not assumed) and is compared against the scorer's pick over the five distribution rungs; the tie-break's part in it is stated | same |
| test 4: the same belief and tuning give the same pick, with an ordinal tie-break | same | `Passed: 26` - `The_same_belief_and_tuning_give_the_same_pick_with_an_ordinal_tie_break` (repeat + reversed candidate order identical; `aaa` beats `zzz`; the winner's weakest axis is one of the three) | same |
| Scoped verification | `pwsh -NoProfile -Command "& './scripts/verify-change.ps1' -Paths 'gk-core/src/FusionRpg.Core/World/Ai/BuildScorer.cs','gk-core/tests/FusionRpg.Core.Tests/World/Ai/BuildScorerTests.cs' -Session empire-progression-4"` | `EXIT=0` - core fallback green; `Core.Tests` `Passed! - Failed: 0, Passed: 11059, Skipped: 0, Total: 11059` (+4 over the 11055 before this row) | - |

**Decision (the dependency, re-read).** My earlier reading - EP5.1 blocked until `sector-development`
gives `INeedVector` real values - was superseded by the orchestrator, and the row's own acceptance
supports the ruling: test 3 is written *with* `UniformNeeds`, so the mechanism is provable over the
neutral stub. What stays deferred is the rung→need MAPPING, which is an input here (and is exactly what
the spec's seedsmith note says would need the real economy).

**NOT proved:** no production host calls `BuildScorer` yet - feeding the chosen rung into the allocation
path is EP5.3's own row (`ai-empire-species`'s default + the turn report), and the tuning it reads is
EP5.2's publish.
