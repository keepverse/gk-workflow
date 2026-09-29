# CAI4.7 — `lawn-cast-trigger` A: trigger, budget, token pool (Core half)

Lane `cai4` (session `combat-ai-4`), 2026-09-22. Row: `tasks/combat-ai-todo.md` CAI4.7.
Spec: `docs/architecture/combat-ai/spec-lawn-cast-trigger.md`.

Three new files under `gk-core/src/FusionRpg.Core/Match/Ai/` — `LawnDecisionTrigger`, `LawnDecisionBudget`,
`LawnCastTokenPool` — and 33 tests in `tests/FusionRpg.Core.Balance.Tests/CombatAi/` (the in-fence
test project; `gk-core/tests/FusionRpg.Core.Tests/**` is outside this lane).

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Exactly `N` first-of-swing records ⇒ one edge; `N-1` ⇒ none | `dotnet test gk-core/tests/FusionRpg.Core.Balance.Tests --filter "FullyQualifiedName~LawnDecisionTrigger\|FullyQualifiedName~LawnDecisionBudget\|FullyQualifiedName~LawnCastTokenPool"` | 33 passed / 0 failed | `Exactly_N_first_of_swing_records_produce_exactly_one_edge_and_N_minus_one_produce_none`, `The_edge_arrives_exactly_N_minus_the_seeded_offset_swings_later` |
| `IsFirstOfSwing == false`, `CastOrigin == true`, unknown ptr each increment nothing | same | 33 passed / 0 failed | `A_non_first_record_a_cast_origin_record_and_an_unknown_ptr_each_increment_nothing`, `An_unknown_ptr_is_never_due` |
| Hold at N; next frame serves it with no further swings | same | 33 passed / 0 failed | `A_refused_decision_at_N_leaves_the_actor_due_with_no_further_swings` |
| `3N` swings during a lock ⇒ one cast; carry lower bound at `Swings = 2, N = 7` ⇒ `Swings == 0`, next edge exactly `N` later | same | 33 passed / 0 failed | `Three_N_swings_accumulated_during_a_lock_produce_one_cast_not_three`, `A_cast_committed_below_N_leaves_the_counter_at_zero_and_the_next_edge_exactly_N_swings_later` |
| No edge inside `L`, edge at `L+1`, counter advanced through the lock | same | 33 passed / 0 failed | `No_edge_inside_the_lock_an_edge_at_L_plus_one_and_the_counter_does_advance_through_it` |
| Same `(matchSeed, actorKey)` ⇒ same offset; two keys differ | same | 33 passed / 0 failed | `The_seeded_offset_is_reproducible_and_matches_the_documented_derivation`, `Two_different_ptrs_get_different_offsets` |
| Budget: `B` due, `b < B` ⇒ `b` per frame, FIFO, no wait > `ceil(B/b)` frames | same | 33 passed / 0 failed (300 due / 8 per frame) | `More_due_actors_than_the_budget_are_served_fifo_over_successive_frames`, `The_whole_queue_is_served_in_order_and_nobody_waits_longer_than_ceil_due_over_budget` |
| Token timeout reclaims; release idempotent, never negative | same | 33 passed / 0 failed | `A_token_never_released_is_reclaimed_at_the_timeout_and_not_before`, `Release_is_idempotent_and_a_second_release_never_goes_negative` |
| Death/ptr reuse leaves no stale counter, lock or token; switch-off drops everything | same | 33 passed / 0 failed | `Death_drops_the_state_and_a_reused_ptr_starts_at_zero_swings_and_no_lock`, `Death_releases_the_token_...`, `Clear_drops_every_actor_and_the_edge_with_it`, `Clear_releases_every_lease_at_once` |
| **Planted violations** — drop the `CastOrigin` check; `CarryCasts = 2`; `Math.Min` for the carry | each planted, run, reverted | **1 red**, **2 red**, **1 red** respectively; 33/33 green after revert | see commit body |
| Golden: byte-identical | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden"` | 5 passed / 0 failed | `PerfProbe` not touched, no battle/siege/delve file touched |
| Row Verify line: `verify-change` | `verify-change.ps1 -Paths @(<6 paths>) -Session combat-ai-4` | exit 0, **15626 passed / 0 failed** across 35 runs | `core-fallback` + `core-balance` |
| `audit-overflow.py --targets A3`; `guard-actor-hub.ps1`; `CombatFanout`; Balance project | see commit body | A3 exit 0 (no finding); actor-hub OK; 5/0; 254/0 | — |

**Still owed, both outside this lane's fence — the row stays open:**

1. `PerfSection.LawnAiDecide` / `SectionCount` / `"lawn.ai.decide"` in
   `gk-core/src/FusionRpg.Core/Diagnostics/PerfProbe.cs`. The row's acceptance reads `26`/`27`; **`CAI-perf-1`
   is right that the residue it presupposes (`AiDecide = 25`, `SectionCount = 26`) is still unlanded** —
   measured today, `PerfProbe.cs` ends at `LawnMoveDrain = 24` with `SectionCount = 25`.
2. `data/tuning/combat-ai.v3.json`'s lawn section. **H7 forbids this lane from publishing it:** both
   readers name their file by hand and both are out of fence — `gk-core/src/FusionRpg.Server/Program.cs:248` and
   `gk-fusion/src/FusionRpg.Injector/Host/RpgHost.cs:89` both read `combat-ai.v1.json`. The four balance values
   therefore arrive as **constructor parameters** of `LawnDecisionTrigger` (documented with their tuning
   key names), so no balance number lives in code; the four structural values are code `const`s, each
   carrying the `tunables-ssot.md` §1 comment.
3. The injector half (feature switch, frame slot, swing feed, registry drops) is CAI4.8's.
