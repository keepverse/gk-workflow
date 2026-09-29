# CAI1.14 — `decision-perf`: five allocation sites, the O(n²) cap, `ai.decide` (PARTIAL slice)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Site 1: `CostLedger.RowsFor` no longer allocates a `List<ActionCostRow>` per `Check` | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~DecisionAllocationTests"` | 4 passed, 0 failed — `CostLedger_Check_allocates_zero_bytes_of_its_own`: the **no-rows path is exactly 0 bytes** (three warm passes + collect + `GetAllocatedBytesForCurrentThread`, production collaborators: a real `CostLedger`, real rows, a real `ActorResourcePools`) | `gk-core/src/FusionRpg.Core/Actions/Cost/CostLedger.cs` |
| Identity: the precomputed rows equal the filtering implementation, same order | same run | passes — `RowsFor_returns_the_same_rows_in_the_same_order_as_the_filtering_implementation` (the FIRST unaffordable OnCommit row in authored order is what `Check` reports) | — |
| Identity: `Argmax` equals the LINQ chain over shuffled inputs | same run | passes — `Argmax_picks_the_same_candidate_as_the_LINQ_chain_over_shuffled_inputs`, 4 rotations incl. a deliberate score tie | `Actions/Ai/CandidateScorer.cs` |
| Identity: the cap equals `Take(n)` and counts post-filter candidates only | same run | passes — `Capping_the_candidate_loop_yields_the_identical_set_Take_produced` | `Actions/Ai/TargetStage.cs` |
| Golden / kernel allocation | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden\|FullyQualifiedName~ExpeditionResolver\|FullyQualifiedName~KernelAllocationTests"` | **22 passed, 0 failed** — nothing re-blessed | — |
| `CostLedgerTests` (the site's own suite) | `dotnet test … --filter "FullyQualifiedName~CostLedgerTests"` | 12 passed, 0 failed (16 with the 4 above) | — |

## Second slice (in-fence remainder)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Site 4: `TopThree` has no LINQ and writes into a caller-supplied 3-slot buffer | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~DecisionAllocationTests"` | 6 passed, 0 failed — `A_battle_with_a_trace_still_records_the_same_top_three` compares `TopThreeInto`/`FormatTopThree` against the LINQ chain it replaced (`Select`/`OrderByDescending`/`ThenBy`/`Take`), including a deliberate score tie, and against the short-candidate-set case | `Actions/Ai/CandidateScorer.cs:294-365` |
| Site 4 caller: one reusable buffer per source, formats only the slots written | same run | passes — `SiegeAiIntentSource` now holds `(string, ScoreBreakdown)[3]` for its life and calls `FormatTopThree(buffer, count)`; `AggressionTierMapTests.The_trace_line_names_a_saturated_choice` still passes unchanged | `Battle/Siege/SiegeAiIntentSource.cs:345-364` |
| Site 1 second half: `TryPay`'s reusable scratch + the re-entry guard | same run | passes — `Re_entering_a_reused_decision_buffer_throws_instead_of_sharing_it` drives a re-entrant `TryPay` through the real `poolsFor` seam and asserts `InvalidOperationException`, then that the ledger is usable again | `Actions/Cost/CostLedger.cs:126-185` |
| `CostLedgerTests` + the whole siege/scorer suite unaffected | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~CostLedgerTests\|FullyQualifiedName~SiegeAiTests\|FullyQualifiedName~CandidateScorerTests\|FullyQualifiedName~AggressionTierMapTests\|FullyQualifiedName~TargetStageCapTests\|FullyQualifiedName~DecisionAllocationTests"` | **59 passed, 0 failed** | — |
| Golden / kernel allocation | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden\|FullyQualifiedName~ExpeditionResolver\|Category=BalanceGuard\|FullyQualifiedName~KernelAllocationTests"` | **47 passed, 0 failed** — nothing re-blessed | — |
| Guards | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` / `guard-battle-responsibility.py` / `guard-actor-hub.ps1` | all exit 0 | — |

Doc re-anchoring (rules.md rule 3): `TopThree`/`TopThreeInto`/`FormatTopThree`, `CostLedger.RowsFor`/`TryPay`
and siege's trace site all moved, so the citations into them in `spec-decision-perf.md` and
`spec-decision-inspector.md` were re-anchored in this same commit. `guard-doc-citations.ps1 -Strict` exit 0.

| `verify-change.ps1` (boundary command) | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Actions/Cost/CostLedger.cs','gk-core/src/FusionRpg.Core/Actions/Ai/CandidateScorer.cs','gk-core/src/FusionRpg.Core/Battle/Siege/SiegeAiIntentSource.cs','gk-core/tests/FusionRpg.Core.Tests/Actions/DecisionAllocationTests.cs') -Session combat-ai-build-20260920"` | `core-fallback` + `core-tests-fallback`, guards `battle-responsibility` + `funnel-delta` OK → `FusionRpg.Core.Tests`: **14863 passed, 4 failed**. All 4 are the same pre-existing `e0f1375d` Items/Atoms corpus failures (untracked `data/seed/items/socket-words/sockwords.json`; no local edit under `data/`), unrelated to these paths | — |

## CAI1.12 rulings recorded here (erratum + handoff)

- **ERRATUM GRANTED** on `No_file_under_data_tuning_names_an_opcode`; the achievable
  `No_file_under_data_tuning_authors_a_place_allowlist` stands as the criterion's intent. Recorded on the
  CAI1.12 row; not re-opened.
- **The injector/lawn half is handed to the `cai-sink` lane**, which owns
  `gk-core/src/FusionRpg.Core/Effects/**` and `gk-fusion/src/FusionRpg.Injector/**`: move `IDeclaresExecution` into
  `EffectModels.cs`, declare `InjectorEffectActionSink`, add the lawn source-scan test. Recorded on the
  CAI1.12 row as a pointer; no longer this lane's blocker.

## NOT done — filed, with the cause read (rules.md rule 2)

1. **Channel-id interning is blocked by this lane's fence.**
   `gk-core/src/FusionRpg.Core/Stats/Derived/DerivedStatChannels.cs:539` builds `$"resource.max.{resourceId}"` on
   every call, and `ResourceChannelReader.Max` reaches it from `ActorResourcePools.Resolve` on the
   decision path — so `Resolving_a_pool_allocates_no_channel_id_string` and
   `The_interned_channel_id_equals_the_formatted_one_for_every_registered_resource` cannot be satisfied:
   `gk-core/src/FusionRpg.Core/Stats/**` is outside this lane's allowed paths. Filed in
   `tasks/derived-stats-todo.md` → "Post-program corrections".
2. **`PerfProbe` is blocked by the same fence.** `PerfSection.AiDecide = 25`, `SectionCount = 26` and the
   `"ai.decide"` name must land in `gk-core/src/FusionRpg.Core/Diagnostics/PerfProbe.cs`, which is also outside
   this lane's allowed paths. Filed in `tasks/combat-ai-todo.md`.
3. **The with-rows residual is measured, not asserted.** `Check` over two OnCommit rows costs **40 bytes**
   beyond the two `ActorResourcePools.Resolve` calls it has to make (264 bytes, dominated by the
   uninterned channel id in (1)). The rows-list allocation is provably gone (the no-rows path is 0); the
   residual's remaining contributors are `RungPolicy.Table.TryResolve` / `CurveTable.ApplyMilli`
   (`Actions/Rungs/**`) and the channel id in (1). Not asserted here — an assertion I cannot make is not
   a test; recorded in the evidence and filed.
4. **`Re_entering_a_reused_decision_buffer_throws_instead_of_sharing_it`** and the remaining
   `DecisionAllocationTests` acceptance rows (the core smart/performance tier, the router with the
   bloodthirsty decorator, the siege policy) are not built — they need the interning fix first for their
   zero-byte assertions to be satisfiable at all.

## Doc re-anchoring (rules.md rule 3)

`CostLedger.cs`, `CandidateScorer.cs` and `TargetStage.cs` line numbers shifted; no citation into them
exists in `docs/architecture/combat-ai/**`, and `guard-doc-citations.ps1 -Strict` exits 0.

## Third slice — site 4: the selection pipeline is allocation-free into a caller scratch

The row's PARTIAL note claimed site 4 was already done ("Argmax and TargetStage were already indexed/capped
... no rewrite needed"). That claim was wrong: `CandidateScorer.ChooseTarget` still allocated FOUR lists per
decision (`Take` + `inTier` + `survivors` + `cut`, `CandidateScorer.cs:175-225` at the pre-change tip), and
the weighted mode allocated a `List.Sort` delegate as well. Rewritten here.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Site 4: rank/cut/select allocates nothing once warm | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~DecisionAllocationTests"` | **9 passed, 0 failed** — `Selection_into_a_warm_scratch_allocates_zero_bytes` measures **0 bytes** over `ChooseTargetInto` with a warm `SelectionScratch` (24 candidates, `MaxCandidatesScored` 32, Argmax, trace-free) | `Actions/Ai/CandidateScorer.cs:188` (`ChooseTargetInto`), `:434` (`SelectionScratch`) |
| Identity: same winner as the allocating overload, every rotation, both modes, over-cap pool | same run | passes — `ChooseTarget_into_a_reused_scratch_matches_the_allocating_overload`: 5 selection policies × 9 rotations of a 9-candidate pool with `MaxCandidatesScored` 4 (so `Take`'s replacement, `poolCount`, is exercised on a rotating window), each compared to `ChooseTarget` | — |
| Identity: Argmax still matches the LINQ chain, ties included | same run | passes — pre-existing `Argmax_picks_the_same_candidate_as_the_LINQ_chain_over_shuffled_inputs` unchanged | — |
| Re-entry guard, asserted not assumed | same run | passes — `Re_entering_a_selection_scratch_throws_instead_of_sharing_it` drives a nested `ChooseTargetInto` through the same scratch from the candidates list's own indexer and asserts `InvalidOperationException`, then that the outer decision still completes and the scratch is reusable | `SelectionScratch.Begin/End` |
| Golden / kernel allocation | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden\|FullyQualifiedName~ExpeditionResolver\|FullyQualifiedName~KernelAllocation\|FullyQualifiedName~SiegeAiLiveWiring\|FullyQualifiedName~CandidateScorer\|FullyQualifiedName~TargetStage\|Category=BalanceGuard"` | **61 passed, 0 failed** — nothing re-blessed | — |
| Doc citations re-anchored (code moved `+32` after the rewritten block) | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | exit 0, **0 HIGH** (`D2 12` = 0 HIGH; `D1 938`, `D3 57` — unchanged pre-existing) | `spec-decision-perf.md`, `spec-decision-inspector.md` |
| Boundary | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Actions/Ai/CandidateScorer.cs','gk-core/tests/FusionRpg.Core.Tests/Actions/DecisionAllocationTests.cs') -Session combat-ai-20260920"` | `FusionRpg.Core.Tests`: **14900 passed, 4 failed** — the same four pre-existing corpus facts named below; unrelated paths | — |

**NOT proved.** `PerfSection.AiDecide = 25` / `SectionCount = 26` and `Resolving_a_pool_allocates_no_channel_id_string`
(site 5) remain unbuilt: `gk-core/src/FusionRpg.Core/Diagnostics/**` and `gk-core/src/FusionRpg.Core/Stats/Derived/**` are
outside this lane's fence (filed). The per-policy zero-byte round tests still cannot go green until site 5
lands, so they are not written. Site 3 (siege closures/buffers) and site 2 (bloodthirsty view) are this
row's next slices, not this one's.

**Pre-existing citation drift, NOT introduced here.** `spec-core-scorer.md` (`:147-149`, `:151-156`,
`:151-203`, `:191-203`, `:199`, `:251`, `:97-110`, `:102-108`), `spec-intent-router.md:201,203`,
`spec-aggression-tier-map.md:20,78,307`, `spec-auto-policy-switch.md:268` and `spec-decision-inspector.md:272,301`
cite pre-CAI1.1 line numbers that did not resolve to the named symbol at the pre-change tip either (checked
before editing: `:147-149` and `:151-156` are doc-comment lines, `:251` is `WeightedPick`, `:242-251/275` are
`WeightedPick`/`Take`). They stay part of the filed mechanical sweep and were deliberately not re-pointed here.

## Fourth slice — site 3: the decision's closures and buffers are caller-owned scratch

Site 3's second half was still open at the pre-change tip: `TargetStage.BuildCapped` allocated the
`eligible` and `result` lists on every decision; the retarget callback
`candidateKey => IsStillScoreable(candidateKey, mySide, liveActorKeys)` allocated a display class and a
delegate; and `SiegeAiIntentSource`'s phase-C local function (plus `CoreIntentPolicy`'s two lambdas)
did the same. All four are gone.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Site 3: the stage writes into a caller-owned pair, zero bytes once warm | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~DecisionAllocationTests"` | **10 passed, 0 failed** — `BuildCappedInto_allocates_zero_bytes_once_warm` measures **0 bytes** (41 live keys, cap 32, collaborators pre-bound as production binds them) and counts the phase-C callback at exactly 32 | `Actions/Ai/TargetStage.cs:84` (`BuildCappedInto`), `:57` (`BuildCapped` overload) |
| Site 3: both deciders use it, plus the cached delegates and a selection scratch | same run | passes — `SiegeAiIntentSource` (`:254` `BuildCappedInto`, `:271` `ChooseTargetInto`) and `CoreIntentPolicy.ScoredTarget` (`:321`) each own a warm pair; the four per-decision delegates are bound once (`SiegeAiIntentSource.cs:169-171` ctor) | — |
| Re-entry guard, asserted not assumed | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Re_entering"` | **2 passed, 0 failed** — `Re_entering_the_siege_decision_throws_instead_of_sharing_its_scratch` (driven from the view's own `DerivedOf`, i.e. inside the guarded window; the outer decision still completes and the source is reusable) and the `SelectionScratch` test from the third slice | `SiegeAiIntentSourceTests.cs` |
| Behaviour identity, whole siege + policy surface | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Siege\|...\|Category=BalanceGuard"` | **461 passed, 0 failed** — `SiegeAiIntentSourceTests`, `SiegeAiLiveWiringTests`, `CoreIntentPolicyTests`, `IntentRouterTests`, `CandidateScorerTests`, `TargetStageCapTests`, `BattleGoldenTests`, `ExpeditionResolverTests`, `KernelAllocationTests` all unedited and green | — |
| `ToScoringWeights`/`ToSelectionPolicy` no longer allocate per decision | read + the 461-run above | moved into `PerActorState` (`CoreIntentPolicy.cs:76`) — "resolved once per actor", the posture that file already had | `CoreIntentPolicy.cs:258` |
| Guards + overflow audit | `pwsh -NoProfile -File scripts/guard-actor-hub.ps1` / `guard-battle-responsibility.py` / `guard-secondary-no-unity.ps1` / `guard-doc-citations.ps1 -Strict` / `guard-single-writer.ps1` / `guard-funnel-delta.ps1`; `python gk-core/scripts/audit-overflow.py --targets A3` | **all exit 0**; doc-citations **0 HIGH**; audit-overflow exit 0 | — |
| Boundary | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Actions/Ai/TargetStage.cs','gk-core/src/FusionRpg.Core/Actions/Ai/CoreIntentPolicy.cs','gk-core/src/FusionRpg.Core/Battle/Siege/SiegeAiIntentSource.cs','gk-core/tests/FusionRpg.Core.Tests/Actions/DecisionAllocationTests.cs','gk-core/tests/FusionRpg.Core.Tests/Battle/Siege/SiegeAiIntentSourceTests.cs') -Session combat-ai-20260920"` | `FusionRpg.Core.Tests`: **14902 passed, 4 failed** — the same four pre-existing corpus facts (SocketOperationsTests x2, UniqueCorpusTests, FamilyExpansionTests) | — |

**NOT proved.** The per-policy zero-byte ROUND tests still cannot be written — site 5 (channel-id
interning, `gk-core/src/FusionRpg.Core/Stats/Derived/DerivedStatChannels.cs:539`) and `PerfProbe.cs` are outside
this lane's fence, and every policy round passes gate 3 -> `ActorResourcePools.Resolve` -> the uninterned
`$"resource.max.{id}"`. Both stay filed in `tasks/derived-stats-todo.md` and this todo's follow-ups.

**Still open in-fence, site 2.** `BasicAttack.cs:582-608`'s `BloodthirstyView` still allocates a
`List<string>` sized to the live board plus the view object, once per decision, in both
`BloodthirstyViewFor` call paths (`BasicAttack.cs:495-507` and the decorator at `:521-532`). Filed on this
row rather than silently dropped: its reusable form has to live where both call paths can reach it (the
decorator is built once per battle, but `DeclareBasicAttack`/`TimelineDispatch` call `BloodthirstyViewFor`
directly), which is a `BattleRunState`-level change with golden risk — the one site this lane left.

**Doc citations re-anchored (this commit).** `SiegeAiIntentSource.cs` grew 393 -> 467 lines and
`CoreIntentPolicy.cs` gained a `PerActorState` member, so the citations that pointed correctly before were
re-pointed: the trace/record site `:345-364` -> `:310-328` (`spec-decision-inspector.md` x3,
`spec-decision-perf.md`), the choice-before-trace region `:341-355`/`:341` -> `:303-328`/`:307`
(`spec-aggression-tier-map.md`), the BaseTier/Aggression comments `:312-317`/`:322` -> `:426-431`/`:436`,
the checked threat sums `:243-245` -> `:421-423`, the site-3 region `:167-281` -> `:220-441`, the O(n^2)
region `:181-262` -> `:254-437`, the cap filters -> `TargetStage.cs:98-107` and the threat loop -> `:410-424`,
and the objective/threat-radius reads `:200-206`/`:241` -> `:357-364`/`:419`. Pre-existing drift in
`spec-core-scorer.md`, `spec-intent-router.md`, `spec-siege-loadout-wiring.md`,
`spec-action-schedule-twin.md`, `spec-delve-automated-wiring.md` and `combat-ai-ideal.md:119-120,137`
(the last two still name `SiegeAiIntentSource.cs:316-351` for a `RetargetLedger` that CAI1.4 moved to
`Actions/Ai/`) was already stale at the pre-change tip and remains part of the filed sweep.

## Fifth slice — site 1 closed hard, site 2 landed, the cap/scan lines pinned

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Site 1: `CostLedger.Check` adds **zero** bytes of its own, with rows AND without | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~CostLedger_Check_allocates_zero_bytes_of_its_own"` | **1 passed, 0 failed** — the no-rows branch is a hard 0, and the with-rows branch is now ASSERTED DIFFERENTIALLY: `Check` over two OnCommit rows must equal the cost of the two `ActorResourcePools.Resolve` calls it makes, exactly. It does. The residual the previous slice measured (40 bytes) was the `foreach` over `RowsFor`'s `IReadOnlyList<ActionCostRow>`, which boxes an `IEnumerator<T>` per gate-3 call; `Check` now uses an indexed `for` | `Actions/Cost/CostLedger.cs:110-121` |
| Site 2: the bloodthirsty view is refilled, not rebuilt | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Trait|FullyQualifiedName~BasicAttack|FullyQualifiedName~Siege\|Category=BalanceGuard"` | **562 passed, 0 failed** — behaviour identity (the existing `TraitBattleTests` "bloodthirsty should kill the weakest first" case, the siege suites and the battle goldens) unchanged | `Battle/BasicAttack.cs:543-566` (`BloodthirstyDecorator` owns one `BloodthirstyView`), `:607-633` (`Refill`) |
| The cap counts only post-filter candidates | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~The_cap_counts_only_candidates_that_passed_the_skip_filters"` | passes — six skipped keys (self, three allies, two unreadable) placed BEFORE five readable enemies, cap 2, and the built set is `e1, e2` | `DecisionAllocationTests.cs` |
| No LINQ on a decision path | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~No_LINQ_remains_on_a_decision_path"` | passes — a focused source scan over the seven decision-path files, comment lines stripped, `.Max(`/`.Min(` excluded because they match `Math.Max`/`Math.Min` (not LINQ) | — |
| Whole decision-perf + policy + golden surface | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~DecisionAllocationTests\|~CostLedger\|~Siege\|~BattleGolden\|~ExpeditionResolver\|~KernelAllocation\|~Trait\|~IntentRouter\|~CoreIntentPolicy\|~CandidateScorer\|~TargetStage\|~ActionSelection\|~BasicAttack\|Category=BalanceGuard"` | **562 passed, 0 failed** | — |
| The row's own Verify line | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Actions/Cost/CostLedger.cs','gk-core/src/FusionRpg.Core/Battle/BasicAttack.cs','gk-core/tests/FusionRpg.Core.Tests/Actions/DecisionAllocationTests.cs') -Session combat-ai-20260920"`; `python gk-core/scripts/audit-overflow.py --targets A3`; `python gk-core/scripts/guard-battle-responsibility.py` | verify-change: **14917 passed, 4 failed** (the four pre-existing corpus facts); audit-overflow **exit 0**; guard-battle-responsibility **exit 0**; guard-actor-hub and guard-doc-citations also **exit 0** | — |
| Doc citations re-anchored (`BasicAttack.cs` 610 -> 643; +22 from 499, +25 from 582) | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict`; `python scripts/audit-doc-citations.py --scope docs/architecture/combat-ai --summary` | exit 0, **0 HIGH**; the combat-ai scope reports 0 HIGH too. Five citations re-pointed (`spec-decision-perf.md` x2, `spec-delve-automated-wiring.md`, `spec-intent-router.md` x3) | — |

### ERRATUM REQUESTED — two acceptance lines this lane cannot close

Both are blocked by the lane's file fence, and both were filed before this slice in "Deferred / named
follow-ups". Requesting a manager ruling rather than reopening the substitute:

1. **Site 5 is `gk-core/src/FusionRpg.Core/Stats/Derived/`**, which this lane's allowed paths exclude — and the
   interning cannot be moved into the fence, because the single reader on the pool path
   (`ResourceChannelReader`) also lives under `Stats/Derived`. A false start that put an interned table
   under `Actions/Cost/` was deleted before commit: it would have been a second type with the same name
   and a second copy of the round-to-long boundary. **Strongest check run instead:** the differential
   assertion above, which proves `Check`'s OWN budget is 0 and attributes the residual to the pool read.
2. **`PerfSection.AiDecide = 25` / `SectionCount = 26` / `"ai.decide"`** live in
   `gk-core/src/FusionRpg.Core/Diagnostics/PerfProbe.cs`, also outside the fence. **Strongest check run
   instead:** the golden/kernel suites and `audit-overflow`, both green; no `PerfSection` member is added
   or renumbered, so nothing downstream breaks.

**NOT proved.** (a) `Resolving_a_pool_allocates_no_channel_id_string` and
`The_interned_channel_id_equals_the_formatted_one_for_every_registered_resource` — both need site 5.
(b) The five per-policy zero-byte ROUND tests — every round passes gate 3 -> `ActorResourcePools.Resolve`
-> the uninterned channel id, so they cannot go green until site 5 lands; the row's own Text
acknowledged this before this lane started. (c) **Site 2's allocation is not measured** — the decorator
is reachable only through a live `BattleRunState`, and no test constructs one (the fixture is built
inside `BattleEngine`), so the claim resting on it is "the mechanism is a retained-capacity refill",
established by reading, not by a byte count. (d) The two direct `BloodthirstyViewFor` call sites
(`BasicAttack.cs:152`, `TimelineDispatch.cs:75`, which build the stub fallback's view) still allocate a
view per decision; reusing there needs the view to live on `BattleRunState`, which the private nested
type cannot do without a move. Both (c) and (d) are named on the row.
