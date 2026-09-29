# CAI2.5 — `decision-inspector` B: the lawn ring, default off (CORE HALF)

Lane `combat-ai-2`. The bounded ring's own logic lives in Core on purpose — the program's rule 4,
*"Logic lives in Core, because CI never builds the injector"* — so it is landed and tested here, while
the injector adapter and the `AiInspectFeature` switch are outside this lane's file fence and are filed.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The ring is bounded and evicts oldest first | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~AiDecisionRingTests"` | **8 passed, 0 failed** — `The_ring_is_bounded_and_evicts_oldest_first` (Cap+3 records leave Cap, oldest gone) and `The_cap_is_the_structural_eight` (pinned with the T2 reason) | `Actions/Ai/AiDecisionRing.cs:37-43` |
| The `last-per-actor` index SURVIVES eviction | same run | passes — `The_last_per_actor_index_survives_eviction`: the busy actor is absent from `Recent()` yet `LastFor` still answers. This is the ring+index pairing's whole reason — one busy actor must not evict everyone else's last decision | `:56-62`, `:72-79` |
| A read returns a copy; an unknown actor returns nothing | same run | passes — `A_read_returns_a_copy_of_the_ring` (clearing the returned list does not evict) and `Reading_an_unknown_actor_returns_nothing_never_a_synthesised_record` | `:49-53`, `:65-70` |
| Death/spawn edges are order-independent, and a reused ptr does not rewrite history | same run | passes — `Death_then_spawn_and_spawn_then_death_both_clear_the_index` and `A_reused_pointer_does_not_rewrite_an_already_recorded_entry` (the old entry keeps tick 5 while the index answers 40) | `:81-86` |
| Match end clears both | same run | passes — `Clear_empties_both_the_ring_and_the_index` | `:88-96` |
| Boundary | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Actions/Ai/AiDecisionRing.cs','gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/AiDecisionRingTests.cs') -Session combat-ai-20260920"` | `FusionRpg.Core.Tests`: **14943 passed, 4 failed** — the four pre-existing corpus facts | — |
| Guards | `guard-doc-citations.ps1 -Strict`; `guard-secondary-no-unity.ps1`; `guard-actor-hub.ps1` | all exit 0, 0 HIGH | — |

## NOT done — filed with `file:line` and the cause

1. **`AiInspectFeature` (the switch, default OFF) is outside this lane's fence.**
   `gk-fusion/src/FusionRpg.Injector/Effects/AiInspectFeature.cs` (new): `CheatToggleId = "AI-INSPECT"`,
   `EnvVar = "FUSIONRPG_AI_INSPECT"`, `DefaultEnabled = false`, and the three-layer precedence
   `!EnvForcedOff && (EnvForcedOn || (DebugOverride ?? DefaultEnabled))` — with the `CheatState.IsUserSet`
   gate `LawnBasicAttackFeature.cs:35-45` records, because a never-toggled `CheatState` must not supply a
   default. **Cause read:** no `gk-fusion/src/FusionRpg.Injector/**` in the lane's allowed paths.
2. **The lawn sink + the membership-edge wiring are outside the lane's fence.**
   `gk-fusion/src/FusionRpg.Injector/Effects/LawnAiDecisionObservability.cs` (new) adapting `AiDecisionRing` to the
   injector, plus the **additive** ring cleanup in `InjectorEntityRegistry.Remove`/`Clear`, plus
   `gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/AiDecisionRingTests.cs`'s Core-side cases (landed). **Cause
   read:** same fence; and the `InjectorEntityRegistry` edit must stay additive — CAI2.5's own acceptance
   says it "does not remove any drop already present".
3. **Consequence: no production host reaches the ring yet.** Per this repo's rule, that makes this a
   landed Core half rather than a finished task — hence the row stays open. The ring is reached the moment
   items 1-2 land, and nothing else is owed on the Core side.
4. The lawn-side `Trigger` population (`AiDecisionRecord.Trigger` reading a real
   `AiTriggerState` instead of `None`) is **CAI4.7**'s, as the record's own doc and the row both say.

**NOT proved.** The lawn's live behaviour (a real match recording, a death edge firing from the injector)
is not exercised here and is not claimed; the ring's contract is proven in isolation, which is what the
spec asks of the Core half.
