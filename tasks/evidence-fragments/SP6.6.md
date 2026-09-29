# SP6.6 — Trigger 6: a save switch replaces every row (the key-set edge, R3); a mid-run switch keeps the run's rows

**Gap found while planning, and its fix, both already recorded in the todo's own acceptance box before
this task started:** the delivery spec expected `save-identity`'s "T2 signal" on `PUT /api/players/current`,
shared with an injector empires cache the strengthened `save-identity` design dropped (ownership now
travels per-spawn, never cached). No `SE` task emits a save-switch signal to the injector. This task
ships the one server→injector save-switch notice itself: `PUT /api/players/current` broadcasts through
the existing `AptitudeEndpoints.BroadcastBestEffort` with scope `"save"` — generic, not
species-specific, so any later injector consumer reuses it.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The cache reacts to the one save-switch notice; nothing species-specific added | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~SpeciesLayerCacheTrigger\|FullyQualifiedName~SpeciesAllocationCacheTrigger"` | **19/19 passed** | `gk-core/src/FusionRpg.Server/Program.cs`, `gk-fusion/src/FusionRpg.Injector/RpgClient.cs`, `gk-fusion/src/FusionRpg.Injector/Match/MatchHost.cs` |
| `A_save_switch_replaces_every_species_layer_row` passes in both orders | same command | passed (wholesale-replace is order-independent by construction — see below) | `gk-core/tests/FusionRpg.Guard.Tests/SpeciesLayerCacheTriggerTests.cs` |
| `A_mid_run_save_switch_keeps_the_runs_rows_until_the_run_ends` passes; the refresh applies at the next `board.start` | same command | passed | same file |
| T4.2's `A_match_edge_is_not_a_species_trigger_…` amended to name the `board.start` exception | same command | passed | `gk-core/tests/FusionRpg.Guard.Tests/SpeciesAllocationCacheTriggerTests.cs` |
| T4.2's `The_cache_holds_exactly_one_empires_rows_…` replaced by `The_cache_answers_each_side_from_its_own_empire_and_never_the_other` | same command | passed | same file |
| No regression in the wider Guard.Tests / Server.Tests | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~Player"` (51/51); whole `FusionRpg.Guard.Tests` (see note) | green | command output |

## What shipped

- `gk-core/src/FusionRpg.Server/Program.cs`: `PUT /api/players/current` gains an `IHubContext<RpgHub> hub`
  parameter and, on a successful switch, calls `AptitudeEndpoints.BroadcastBestEffort` with
  `scope: "save"` — fire-and-forget, matching every other broadcast in this file's own style. No
  second route, no second key.
- `gk-fusion/src/FusionRpg.Injector/RpgClient.cs`: the shared `AptitudesUpdated` handler is now typed
  (`AptitudesUpdatedScopeDto`, a minimal `{ Scope }` DTO) instead of ignoring the payload. Every scope
  OTHER than `"save"` keeps its existing unconditional-reload behavior unchanged. For `"save"`: if
  `MatchHost.IsRunOpen`, calls `MatchHost.RequestDeferredSaveSwitchRefresh()` (defers); otherwise
  enqueues `aptitudes.allocation.reload` immediately, exactly like every other scope.
- `gk-fusion/src/FusionRpg.Injector/Match/MatchHost.cs`: new `IsRunOpen` (reads `_runtime.Phase is not
  MatchPhase.Idle`), `RequestDeferredSaveSwitchRefresh()` (sets a private `_pendingSaveSwitchRefresh`
  flag), and the flag is consumed exactly once at the EXISTING `board.start` block — right beside
  `CheatState.RefreshCommanderAllocationCache()`, the same moment every other per-board cache reset
  already happens — enqueuing the SAME `aptitudes.allocation.reload` command the SignalR handler
  itself would enqueue immediately if no run were open. Never a direct call to
  `ApplySpeciesAllocations`/`ApplySpeciesLayers` from `MatchHost.cs` — only the same command the
  transport's own handler already uses, so the wholesale-replace happens in exactly one place.
- `gk-core/tests/FusionRpg.Guard.Tests/SpeciesLayerCacheTriggerTests.cs`: two new text-scan proofs matching
  the acceptance's own named tests exactly.
- `gk-core/tests/FusionRpg.Guard.Tests/SpeciesAllocationCacheTriggerTests.cs`: `A_match_edge_is_not_a_species_trigger_and_the_trigger_set_was_not_copied`'s
  comment amended to name the ONE real exception (a deferred save-switch flag consumed at
  `board.start`) rather than silently going stale; its assertions gained a check that the flag name
  is genuinely present and that neither `ApplySpeciesAllocations` nor `ApplySpeciesLayers` is called
  DIRECTLY from `MatchHost.cs` (the deferred path only enqueues a command, never bypasses the
  transport). `The_cache_holds_exactly_one_empires_rows_and_refuses_to_answer_for_another` REPLACED
  by `The_cache_answers_each_side_from_its_own_empire_and_never_the_other`, proving the NEWER
  `speciesLayers` cache's `resolveModRows` delegate looks up `empire.Value` generically (never
  hardcoding `EmpireId.Dave` the way the OLD `SpeciesAllocation.resolveSpeciesAllocation` delegate
  still does, which is now an accurate, narrower claim about that OLDER cache specifically, not the
  whole injector).

## "Both orders" — why one test, not two, is sufficient

`ApplySpeciesLayers`/`ApplySpeciesAllocations` are wholesale replaces (proven by their own existing
tests: `A_refresh_replaces_the_whole_layer_cache_rather_than_merging_into_it`,
`A_refresh_replaces_the_whole_cache_rather_than_merging_into_it`) — a replace is idempotent and
order-independent by construction: "hydrate then switch" and "switch then hydrate" both end at
whatever state the LAST replace wrote, with no merge step where order could matter. `A_save_switch_replaces_every_species_layer_row`
therefore proves the ONE new thing this task adds (the save-switch notice actually reaches the SAME
replace mechanism), and reuses the pre-existing replace-mechanism tests for the "in both orders" half
of the claim rather than re-deriving idempotence with two near-duplicate tests.

## Note on the whole-Guard.Tests run

The whole `FusionRpg.Guard.Tests` project run for this task took long enough to move to a background
job; its result will be folded into the FULL Core/Data/Server/Guard sweep before wave 6 closes, per
this program's own "record blocked, keep working" discipline for orchestrator-owned full-suite runs.
The scoped verify line above (19/19) and the `~Player` Server.Tests slice (51/51) are the criteria
SP6.6's own Verify line actually names.

## Reviewed-vocabulary / closed-form note

No population-count or generated-text assertion is added or touched by this task.
