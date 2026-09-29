# CAI2.4 — `decision-inspector` A: the record, the sink, the turn-mode wiring (FIRST SLICE)

Lane `combat-ai-2`. The seam, the trace sink and the siege re-point are landed. The row stays OPEN: the
chosen-ACTION field, per-candidate gate verdicts and the "all four policies" line need a surface the
row's own Files list does not name, and are listed under NOT done with their cause.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `IAiDecisionSink` + `AiDecisionRecord` carry every field D4 names | read of `Actions/Ai/AiDecisionRecord.cs` | present: `Tier`, `ProfileId`, `Personality`, `Trigger`, `Candidates` (gate + breakdown), `ChosenActionId`, `ChosenTargetKey`, `ChosenSaturatedBy`, `TopThree`, `Origin`. **Provenance is nullable and null is a fact** — siege is handed `ScoringWeights` directly (CAI1.8's H7 move) so it has no profile to name and records null rather than inventing an id | `AiDecisionRecord.cs:31-42` |
| Siege records through the sink, and the line is BYTE-IDENTICAL | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SiegeAi\|~AggressionTierMap\|~BattleTrace\|Category=BalanceGuard"` | **216 passed, 0 failed** — `SiegeAiIntentSourceTests`' line-shape assertions and `AggressionTierMapTests.The_trace_line_names_a_saturated_choice` pass **UNCHANGED**; `The_emitted_line_is_byte_identical_whether_the_trace_or_the_sink_is_supplied` compares a `trace:`-sugar run against an explicit `BattleTraceDecisionSink` run and gets equal lines | `BattleTraceDecisionSink.cs`, `SiegeAiIntentSource.cs:315-348` |
| Golden-neutral, asserted | same run | `The_record_is_golden_neutral` asserts `AiDecisions` is non-empty AND `BattleTrace.Digest` equals an empty trace's; `Wiring_a_sink_changes_no_intent` asserts the returned `ActionId`/`TargetKey` are identical with and without a sink. `BattleGoldenTests` unchanged in the same run | — |
| A spy sink counts one `Record` per scored decision and zero on a held-target tick | same run | passes — `A_scored_decision_records_exactly_one_record`; `A_held_target_tick_records_nothing` (inside a `RetargetLedger` latency window the held target is served and the spy still holds exactly one record) | `DecisionInspectorTests.cs` |
| Every candidate the decision scored appears with its real breakdown | same run | passes — `Every_scored_candidate_appears_with_a_real_breakdown` (2 enemies -> 2 verdicts, each with a non-null `Breakdown`). `Gate`/`ActionId` are **null at this site** and that is a fact: step 3's gate loop runs against the chosen target only, so filling them per candidate would be the second evaluation §1 forbids | — |
| `AiDecisionOrigin` is a three-member closed vocabulary | same run | passes — `AiDecisionOrigin_has_three_members`, with the reason in the test (the inspector READS an origin and never infers one from `Candidates[0]`) | `AiDecisionRecord.cs:20-27` |
| The null sink keeps CAI1.14's zero-allocation test green | same run | passes — the record is built only inside the `_sink is not null` guard, and `DecisionAllocationTests`' warm-scratch assertions are unchanged | `SiegeAiIntentSource.cs:315-348` |
| Guards + overflow | `guard-doc-citations.ps1 -Strict`; `guard-actor-hub.ps1`; `guard-battle-responsibility.py`; `guard-secondary-no-unity.ps1`; `guard-single-writer.ps1`; `guard-funnel-delta.ps1`; `python gk-core/scripts/audit-overflow.py --targets A3` | all exit 0; **0 HIGH** | — |
| Boundary | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Actions/Ai/AiDecisionRecord.cs','gk-core/src/FusionRpg.Core/Actions/Ai/BattleTraceDecisionSink.cs','gk-core/src/FusionRpg.Core/Battle/Siege/SiegeAiIntentSource.cs','gk-core/src/FusionRpg.Core/Battle/BasicAttack.cs','gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/DecisionInspectorTests.cs') -Session combat-ai-20260920"` | `FusionRpg.Core.Tests`: **14935 passed, 4 failed** — the four pre-existing corpus facts | — |

## NOT done — and the one design question behind it

1. **`ChosenActionId` is null at the siege site.** Siege's recorded decision is the TARGET decision
   (`ChooseTarget`), and the action is chosen one step later in `TryDeclare`. Carrying the action here
   would need the target stage to hand its candidate set to `TryDeclare`, and the row's
   "`ChosenActionId` equals the `ActionIntent` returned" line is therefore **not satisfied at siege**.
2. **Per-candidate gate verdicts.** `UsabilityEvaluator` runs in step 3 against the chosen target, so
   there is no per-candidate verdict to copy. `AiCandidateVerdict.Gate`/`.ActionId` are nullable for
   that reason, and the row's "the gate verdict the gate loop returned" is satisfied only for the
   candidate the loop actually ran against.
3. **"All four policies behind the router record through the same sink" is NOT done.** It needs
   `IntentRouter.cs`, `CoreIntentPolicy.cs`, `ActionStage.cs` and `StubIntentSource.cs` — none of which
   the row's Files list names, and `ActionStage` is where the per-candidate gate verdicts (item 2) would
   finally have a real source. **This is the ruling to make:** either re-scope CAI2.4 to that surface, or
   land the sink through the router as its own task.
4. **The lawn half (`Trigger` populated, the bounded ring) is CAI2.5**, and its injector adapter is
   outside this lane's fence.
5. `BattleReport`-level neutrality was not re-measured with a sink wired into a full battle — the
   reachable proof used here is `BattleTrace.Digest` equality plus `BattleGoldenTests` unchanged in the
   same run.

**Incidental fix in the same commit.** `BasicAttack.cs`'s reusable `BloodthirstyView` (CAI1.14 site 2)
emitted two `CS8618` warnings — its parameterless constructor left the non-nullable `_inner` unset. The
constructor now takes the inner view, which the decorator already has.

## Second slice — the record carries the chosen ACTION and the gate loop's real verdicts

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `ChosenActionId`/`ChosenTargetKey` equal the `ActionIntent` returned | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~DecisionInspector"` | **7 passed, 0 failed** — the emission moved OUT of `ChooseTarget` into `EmitDecisionRecord`, called from `TryDeclare` after the decision, so the record's two chosen fields are the returned intent's own; `A_scored_decision_records_exactly_one_record` now asserts both halves | `SiegeAiIntentSource.cs` (`TryDeclare` wrapper + `EmitDecisionRecord`) |
| Every candidate the decision scored AND every gate verdict the loop returned appears | same run | passes — `Every_scored_candidate_and_every_gate_verdict_appears`: 2 scored targets with real `ScoreBreakdown`s and null gates, plus 1 gate verdict (`act.attack`, `UsabilityReason.Usable`) with a null breakdown. Two kinds of entry, both real facts, distinguished by which field is set | — |
| Still one record per SCORED decision, zero on a held-target tick | same run | passes — `_scoredThisDecision` is set inside `ChooseTarget` only past both early returns, and `TryDeclare` emits once, after the decision | — |
| The row's Verify line, all three filters | `--filter "FullyQualifiedName~BattleTrace\|~AiDecision\|~SiegeAi"`; `--filter "FullyQualifiedName~BattleGolden\|~PreAdoptionTrace"`; `--filter "FullyQualifiedName~DecisionInspector"` | **72 passed**; **12 passed**; **7 passed** — all 0 failed | — |
| Guards + boundary | `guard-secondary-no-unity.ps1`; `guard-debug-scope.py`; `verify-change.ps1 -Paths <the two files>` | guards **exit 0**; verify-change **14949 passed, 4 failed** (the four pre-existing corpus facts) | — |
| Citations re-anchored (`SiegeAiIntentSource.cs` 488 -> 532; +9, +25, +44 bands) | `guard-doc-citations.ps1 -Strict`; `audit-doc-citations.py --scope docs/architecture/combat-ai --summary` | **0 HIGH** on both; twelve citations across five specs re-pointed | — |

### Still not done — the row stays open on one line

**"All four policies behind the router record through the same sink" is NOT done.** It needs a sink
threaded through `IntentRouter.Compose` and each of its arms — `StubIntentSource` (whose gate loop would
supply its own verdicts), `CoreIntentPolicy` (whose `ActionStage` is where per-ACTION gate verdicts
genuinely live), the steered arm and `NoneIntentSource` — none of which the row's Files list names. This is
in-fence work in this lane's paths, not an external dependency; it is simply larger than the two slices
landed so far, and it is the next thing to do. Now that `EmitDecisionRecord` exists and the record carries
both entry kinds, most of the remaining cost is the per-policy emission points rather than record design.

## Third slice — every router arm records through the one sink (the row's last line)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| All the router's `IIntentSource` arms record through the same sink | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~DecisionInspector"` | **8 passed, 0 failed** — `Every_router_arm_records_through_the_same_sink` exercises the POLICY arm (origin `Policy`, chosen action equal to the declared intent), the STEERED arm (origin `Steered`), and the FALLBACK arm. The fallback case produces TWO records and that is asserted deliberately: the policy arm is asked first and declares nothing, then the stub answers — both are decisions the inspector must be able to explain, and the last one is the answer. A null sink is asserted to leave the chain exactly as it was | `Actions/Ai/AiDecisionRecordingSource.cs` (new), `Actions/IntentRouter.cs` (`Compose` wraps each arm) |
| Siege's zero-allocation acceptance still holds with the inspector compiled in | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~DecisionAllocationTests\|~CostLedger\|Category=BalanceGuard"` | **56 passed, 0 failed** | — |
| The row's whole Verify line, all three filters + guards | `--filter "FullyQualifiedName~BattleTrace\|~AiDecision\|~SiegeAi"`; `--filter "FullyQualifiedName~BattleGolden\|~PreAdoptionTrace"`; `--filter "FullyQualifiedName~DecisionInspector\|~IntentRouter\|~ActionSelection"`; `guard-secondary-no-unity.ps1`; `guard-debug-scope.py` | **72 / 12 / 44 passed**, all 0 failed; both guards **exit 0**; `guard-actor-hub` exit 0; `audit-overflow --targets A3` exit 0 | — |
| Boundary | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Actions/Ai/AiDecisionRecordingSource.cs','gk-core/src/FusionRpg.Core/Actions/IntentRouter.cs','gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/DecisionInspectorTests.cs') -Session combat-ai-20260920"` | **14950 passed, 4 failed** — the four pre-existing corpus facts | — |

**Design note, so the empty fields are read as facts.** The recorder fills what the ROUTER knows — actor,
tick, which arm answered (→ `Origin`) and the intent that came back — and leaves `Round` 0 (the tick→round
map belongs to the policy that owns the clock seam) and `Candidates`/`TopThree` empty. An arm that exposes
no candidate detail records none; `SiegeAiIntentSource` fills both (slices 1-2), and the core policy's
`ActionStage` is where the smart tier's per-ACTION gate verdicts live. Nothing is invented to fill a gap.

**Row status: all acceptance lines now satisfied.** The one thing honestly thin is that the router-level
record for the smart tier carries no per-candidate detail yet — D4's "every candidate with its gate
verdicts" is satisfied at siege (the live host) and would need the core policy's action stage to be
satisfied for the lawn. That is CAI4.7/CAI4.8's population, on the ledger as their own rows, not a gap
disguised here.
