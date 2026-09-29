# EP4.x exhausted and re-verified at the merged head — the two remaining blockers

`features/mega-merge` merged again into `cmdc/ep-4` (head `c7ed894b8`), and every EP4.x row plus EP5.1/EP5.2
was re-verified there. EP4.18, the wave's last row, is landed; nothing under EP4.x is open. Session
`empire-progression-4` - branch `cmdc/ep-4`.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The merge's own change to my work: `ai.v3` reader re-landed, and now GUARDED | `dotnet test gk-core/tests/FusionRpg.Server.Tests -c Release --filter "FullyQualifiedName~ContentBootStartupWiring"` | `Passed: 13` in the server group below - `The_server_boot_reads_the_latest_revision_of_the_domains_it_owns` reads the latest `ai.v*`/`items.v*` revision ON DISK and asserts `Program.cs` names it, so a revert fails in a test instead of at boot (it cites the incident: `8b81e395d` + `WorldAiTuningRejection: ai tuning: missing or non-object 'buildScorer'`) | `gk-core/tests/FusionRpg.Server.Tests/ContentBootStartupWiringTests.cs`, `gk-core/src/FusionRpg.Server/Program.cs:285-298` |
| EP4.13-EP4.18 rows re-verified at this head | `dotnet test gk-core/tests/FusionRpg.Data.Tests -c Release --filter "(FullyQualifiedName~EmpireSpecies\|~ZombossCommanderPool\|~WorldTurnHubInputsFor\|~SpeciesProgression\|~EmpireLevel\|~AllocationStore)&(Category!=DiskSemantics&Category!=Heavy)"` | `Passed! - Failed: 0, Passed: 60, Skipped: 0, Total: 60` | `gk-core/tests/FusionRpg.Data.Tests/{EmpireSpeciesProgressionTests, ZombossCommanderPoolTests, WorldTurnHubInputsForTests}.cs` |
| EP5.1/EP5.2 rows re-verified | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --filter "FullyQualifiedName~BuildScorer\|~AiTuning\|~ProgressionLayerSelector\|~SpeciesAllocationSource\|~SpeciesLayerSource"` | `Passed! - Failed: 0, Passed: 68, Skipped: 0, Total: 68` | `gk-core/tests/FusionRpg.Core.Tests/World/Ai/{BuildScorerTests,WorldAiTuningTests}.cs` |
| The seams re-verified | `dotnet test gk-core/tests/FusionRpg.Server.Tests -c Release --filter "FullyQualifiedName~ProgressionLayerParity\|~ProgressionPowerIndexReload\|~ContentBootStartupWiring"` | `Passed! - Failed: 0, Passed: 13, Skipped: 0, Total: 13` | `gk-core/tests/FusionRpg.Server.Tests/{ProgressionLayerParityTests, ProgressionPowerIndexReloadTests, ContentBootStartupWiringTests}.cs` |
| The whole guard suite at this head | `dotnet test gk-core/tests/FusionRpg.Guard.Tests -c Release` | `Passed! - Failed: 0, Passed: 591, Skipped: 0, Total: 591` (4m57s) | - |

## The two remaining blockers (both external, both on EP5.3 — nothing under EP4.x is blocked)

1. **An owner/manager ruling on the wiring shape.** EP5.3 asks that the AI empire's species follow the
   scored rungs. Wired as written with today's beliefs it moves EVERY AI species build (`even` wins the
   committed ordinal tie-break where the ladder and today's baseline say `species-favour`), with no balance
   content to justify the move; wired the behaviour-preserving way it is a one-candidate mechanism with
   constant content, which is the failure mode the spec's own deferral names. The proof test stands:
   `Wiring_the_scorer_into_the_ai_species_default_needs_real_belief_content`.
2. **`sector-development`'s non-neutral `INeedVector`.** The belief inputs have no source: `UniformNeeds`
   (`INeedVector.cs:31-41`, constant 1000 on both axes) is still the only implementation in `src/`, `tests/`
   and `tools/`. The turn-report half is no longer a blocker — `CommitWorldTurn` already holds
   `result.Report`, so the `Considerations.Weakest` line is a Data-side write once the scorer runs there.

**NOT proved (environment, not program):** the monolithic `test-fast.ps1 -AllDefault` cannot complete here
(F6, ~600KB output ceiling — the default set was verified in bounded groups at the previous head and my own
rows re-verified above); `gk-fusion/src/FusionRpg.Injector/**` cannot be compiled without the game's loader refs
(structurally proven by `CommanderPoolTransportGuardTests`, 5/5 of the 591 above); no live probe.

**Follow-through on F7 (recorded so the loop closes):** the manager's board commit `c7ed894b8` records the
merge defect this lane caught, and the fix is systemic rather than a re-asserted line — a new guard now
pins the latest tuning revision for the domains the boot owns. F6 (the suite-output ceiling) is the only
finding from this lane still open with its owner.

---

## Second merge, same head discipline (2026-09-22, `086f43273` on `5da5c3a26`)

`features/mega-merge` advanced 21 commits (cai4/ssh4/overlay work), so the whole default set was re-run at
the new head rather than inheriting the previous head's numbers. **Everything is green except one
order-dependent E2E test**, which is not this program's path and is filed as F8:

| Suite | Result |
|---|---|
| `FusionRpg.Data.Tests` (default filter) | `Passed! - Failed: 0, Passed: 1784, Skipped: 0, Total: 1784` (10m58s) |
| `FusionRpg.Server.Tests` | `Passed! - Failed: 0, Passed: 806, Skipped: 0, Total: 806` |
| `FusionRpg.Core.Tests` | `Passed! - Failed: 0, Passed: 10722, Skipped: 0, Total: 10722` |
| `FusionRpg.Guard.Tests` | `Passed! - Failed: 0, Passed: 591, Skipped: 0, Total: 591` |
| every other default-set project (34 of them) | all green — ActorHub 498, Atoms 1351, Items 1402, Balance 299, ClassSystem 238, Events 95, Match 91, Hud 84, Commanders 64, Notify 41, MatchRuntime 40, ActorSurface 31, Aura 30, Expeditions 23, EffectOfflineKit 24, EffectScenarioRunner 20, Diagnostics 17, AchievementTitles 15, … |
| `FusionRpg.E2E.Tests` | `Failed! - Failed: 1, Passed: 230, Total: 231` — `UnlockTuningActivationTests.A_real_level_up_grants_a_real_action_row`, `System.InvalidOperationException: action unlock grant refused: BasicCollision` raised at `RpgStore.UniqueActors.cs:2134` inside `TryRollActionUnlocks`. **Re-run alone: `Passed! - Passed: 2, Total: 2`**, and `git log c7ed894b8..5da5c3a26 -- gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs gk-core/src/FusionRpg.Core/Actions/Unlock/ data/` is EMPTY — so it is an order/parallelism interaction between E2E test classes, not a regression from the merge and not this program's code (F8) |
| `guard-power.py` | `POWER GUARD OK — one ladder, pin holds, no private f(level)` |

## DECISION NEEDED — EP5.3's wiring shape (one word; stated here rather than idled on)

The blocker is a choice, not an unknown, so here are the options with their costs. EP5.3's other blocker
(`sector-development`'s non-neutral `INeedVector`) is a wait either way.

- **(A) one-candidate wiring** — run `BuildScorer` over the rungs the ladder can actually reach for the
  species context (today exactly `species-favour`), keep `SpeciesAllocation.Baseline` as the only
  allocation path, and write the `Considerations.Weakest` line into the turn report on that path. The
  allocation is byte-identical (no golden moves, proven by the same cases that prove EP4.15), the scorer
  runs in a real path, and the day the economy makes a second rung reachable the same code starts
  differing. Cost: today's answer is a constant, which is the mechanism the spec's own deferral warns
  about — so it needs an explicit ruling rather than a lane decision.
- **(B) defer** — leave EP5.3 open until `sector-development` ships real needs. Nothing lands now; the
  proof test and this note are the deliverable.
- **(C) full candidate set as written** — REJECTED by this lane and listed so the rejection is explicit:
  with neutral beliefs the committed ordinal tie-break returns `even` where the ladder and today's baseline
  say `species-favour`, i.e. it moves every AI species build with no balance justification.

This lane recommends **(A)** if a constant-answer mechanism is acceptable under an explicit ruling (its
allocation provably does not move), and **(B)** otherwise — either way the row needs your word, not more
work from the lane.
