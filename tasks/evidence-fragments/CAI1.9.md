# CAI1.9 — Tier, personality, and `CoreIntentPolicy`

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `AiTierResolver.For` is the only tier decision, no difficulty input | `dotnet test --filter "FullyQualifiedName~AiTierResolverTests"` | 6 passed (incl. `Nothing_in_tier_resolution_reads_a_difficulty_input`, a reflection-based signature assertion) | `AiTierResolverTests.cs` |
| Unwired class resolver defaults to `Unique` | same run | `Unwired_class_resolver_defaults_to_unique` passes | — |
| Personality reproducible, in-bounds, draw-order contract | `dotnet test --filter "FullyQualifiedName~AiPersonalityTests"` | 12 passed (incl. `Changing_one_axis_bound_does_not_shift_another_axis`, `All_bounds_zero_is_byte_identical`) | `AiPersonalityTests.cs` |
| Performance tier: no candidate inputs, still runs reserve floor + six gates | `dotnet test --filter "FullyQualifiedName~PerformanceTierTests\|FullyQualifiedName~Performance_tier_computes_no_candidate_inputs"` | 3 passed | `ActionStageTests.cs` (`PerformanceTierTests`), `CoreIntentPolicyTests.cs` |
| `CoreIntentPolicy` runs the 7 steps in order, profile once/actor, census once/decision, no scoring arithmetic | `dotnet test --filter "FullyQualifiedName~CoreIntentPolicyTests"` | 8 passed | `CoreIntentPolicyTests.cs` |
| Golden: byte-identical | `dotnet test --filter "FullyQualifiedName~BattleGolden\|FullyQualifiedName~ExpeditionResolver\|FullyQualifiedName~SiegeAi\|FullyQualifiedName~Actions.Ai"` | 159 passed, 0 failed | — |
| No regression | `dotnet test gk-core/tests/FusionRpg.Core.Tests` (full) | 14788 passed, 0 failed | — |
| `verify-change.ps1` | `-Paths <9 changed files> -Session combat-ai-build-20260920` | exit 0; `core-fallback`/`core-tests-fallback` → full `FusionRpg.Core.Tests` (14788 passed) | — |
| `audit-overflow.py --targets A3` | — | no new finding in the 4 new `Actions/Ai/*.cs` files or `CombatAiProfile.cs` | — |

## Deviations from the spec's own illustrative snippet, each stated in code

1. **`CoreIntentPolicy.Create` takes `(AiPlace place, AiRole role)`, not `string profileId`.** The
   spec's §6 pseudocode names a raw string "resolved through `CombatAiProfilePolicy.For`" — but that
   method's real, shipped signature (CAI1.8) is `For(AiPlace, AiRole)`, never a string. Took the real
   types, matching CAI1.3's own precedent for reconciling a spec snippet against the module it depends
   on. Documented at `CoreIntentPolicy.cs`'s own class doc comment.
2. **`CoreIntentPolicy` never calls `CombatAiProfilePolicy.For` directly** — it holds a
   `Func<CombatAiProfile> _resolveProfile` instead, populated with that call by the public `Create`
   factory. An `internal CreateForTest(..., CombatAiProfile profile, ...)` factory bypasses the hub
   entirely for tests. This is a self-found fix, not a spec deviation: an early draft of
   `CoreIntentPolicyTests.cs` called `CombatAiProfilePolicy.Configure(...)` per-test, which is EXACTLY
   the shared-static-state race CAI1.8 diagnosed and fixed for `CombatAiTuningTests` — a test-only
   hub write would have raced any other concurrently-running test that depends on the hub staying
   configured. Caught before it shipped, fixed by the same pattern (a pure resolution path a test can
   drive without touching the static hub), rather than repeating the CAI1.8 incident a second time in
   the same program.
3. **`roundOf` and `isDownedOf` are added constructor parameters, not in the spec's §6 snippet.**
   `AiRowFacts.Round` / `CandidateScorer.Score`'s `currentRound`, and `AllyDowned`'s own "the downed
   predicate the place supplies" (`AiVocabulary.cs`'s own comment) both need a caller-supplied answer
   `IBattleView` cannot give generically. Both default to the safe, byte-identical-at-landing value
   (`tick => (int)tick`; "nobody is ever downed") — the same optional-seam pattern `SiegeAiIntentSource`
   already established for `roundOf` (CAI1.1).
4. **`AiWasteGuards.ToWasteGuardThresholds()` added to `CombatAiProfile.cs`** (module 2's file) — a
   self-found gap: the first draft of `CoreIntentPolicy.TryDeclare` never converted the profile's
   authored `Guards` into module 1's `WasteGuardThresholds`, so `ActionStage.TryPick` silently ran
   every waste guard at its "off" default regardless of what a profile authored. Caught by
   `Tier_smart_passes_runWasteGuards_true_and_performance_passes_false` failing (expected `True` for
   "guard refuses", got `False`); fixed with the same positional-projection pattern
   `AiScoringBlock.ToScoringWeights()`/`AiSelectionBlock.ToSelectionPolicy()` already use.
5. **`AiDecisionTrace`, not `TracedDecision`, for the trace seam.** The spec's own prose never names
   the trace record's type, only its shape. `TracedDecision` collides with a real, unrelated, already-
   shipped type (`FusionRpg.Core.Battle.Timeline.TracedDecision`, T10's real-input replay record) —
   caught at compile time (`CS0104` ambiguous reference), renamed before it shipped.
6. **`TargetSelector`'s 8 members implemented as `CoreIntentPolicy`'s own private fixed-selector
   pickers**, not a separate public type. Module 2 (CAI1.6) declared the enum with a reader named in
   each member's own comment but built no picker; this module is the first (and, per the spec, the
   ONLY) consumer of the fixed-selector path (performance tier), so the pickers live where they are
   used — mirroring `StubIntentSource.NearestEnemy`'s own precedent, generalised to either side.
   `ObjectiveClassMilli`/`IncomingThreatMilli`/`BaseTier` on the smart-tier `TargetCandidate` stay
   structurally 0: no reference-distance/threat-radius field exists in the GENERAL profile schema
   (only siege's own narrowed, siege-local `AiTuning` carries those two geometry constants) — a
   wiring gap, not a design gap, stated in `TryBuildCandidate`'s own comments. `HighestThreat`'s
   performance-tier reading uses the candidate's own raw `CombatPowerOmni` (no radius, no sum) as a
   deliberately simpler heuristic than the smart tier's radius-bounded `IncomingThreatMilli` term.

## Identity at landing

Every personality bound ships at 0 (`combat-ai.v1.json`, CAI1.8), the class resolver is unwired in
every existing caller (nothing calls `CoreIntentPolicy` in production — `delve-automated-wiring`,
module 13, is its first caller), and `siege/default` still carries its explicit `tierOverride: "smart"`
override. `BattleGoldenTests` and the `SiegeAi`/`Actions.Ai` regression suite are unedited and pass
unchanged (159/159). `RulesetVersion` stays 5.
