# SP6.5 — Triggers 4 and 5: a species level-up and a fusion append broadcast `AptitudesUpdated(kind "species")`

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| After commit, `EventIngest` broadcasts through the one emitter `AptitudeEndpoints.BroadcastBestEffort` when the dirty set holds a `Species`-kind level change | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~SpeciesLayerCacheTrigger"` | **7/7 passed** | `gk-core/src/FusionRpg.Server/EventIngest.cs`, `gk-core/tests/FusionRpg.Guard.Tests/SpeciesLayerCacheTriggerTests.cs` |
| `/execute` (`FusionEndpoints.cs`) broadcasts after a ledger append; the Data layer never broadcasts | same command | passed | `gk-core/src/FusionRpg.Server/FusionEndpoints.cs` |
| `A_species_level_up_mid_run_reaches_actors_already_on_the_board` / `A_fusion_pick_reaches_actors_already_spawned` pass, and fail when the wiring is removed | text-scan proofs (see above); manually confirmed each fails if the `AptitudeEndpoints.BroadcastBestEffort(` line is removed from its method | passed | same test file |
| Real, non-replayed fusion execute broadcasts `AptitudesUpdated` to both SignalR groups; a replay does not re-broadcast | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~FusionAptitudesBroadcastTests"` | **2/2 passed** | `gk-core/tests/FusionRpg.Server.Tests/FusionAptitudesBroadcastTests.cs` (new) |
| No regression in the wider Fusion / Guard.Tests suites | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~Fusion"` (594/594); `dotnet test gk-core/tests/FusionRpg.Guard.Tests` (450/451, the one failure PRE-EXISTING and unrelated — SP3.6) | green | command output |

## What shipped

- `gk-core/src/FusionRpg.Server/EventIngest.cs`: `BroadcastProgressionAsync` — for each dirty progression row
  whose `Kind == RpgActorKinds.Species`, calls `AptitudeEndpoints.BroadcastBestEffort` with
  `scope: "species"`, additive to the existing `RpgProgressionUpdated` broadcast (which the web FE still
  reads for its own progression UI; this is a SECOND, independent broadcast for a different consumer).
  The injector's ALREADY-EXISTING trigger-3 handler (`_hub.On<object>("AptitudesUpdated", _ => ...)`,
  which ignores the payload and unconditionally enqueues `aptitudes.allocation.reload` ->
  `RefreshCommanderAllocationAsync()`) needed NO change — SP6.4 already extended that fetch to carry
  `speciesLayers`, so simply emitting this broadcast at the right two points is the whole remaining
  wire.
- `gk-core/src/FusionRpg.Server/FusionEndpoints.cs`: `/api/fusion/execute`'s existing `if (!outcome!.Replayed)`
  block (which already broadcasts `CreaturesUpdated`/`SoulsUpdated`) gains the SAME
  `AptitudeEndpoints.BroadcastBestEffort` call. Gated on the SAME `!Replayed` check for the SAME
  reason: `AppendSpeciesModUnlocked` is `INSERT OR IGNORE` on the correlation id, so a replay appends
  no new ledger row and there is nothing new for an already-spawned actor to pick up.
- `gk-core/tests/FusionRpg.Guard.Tests/SpeciesLayerCacheTriggerTests.cs`: two new text-scan proofs, matching
  the acceptance's own named test methods exactly (`A_species_level_up_mid_run_reaches_actors_already_on_the_board`,
  `A_fusion_pick_reaches_actors_already_spawned`) — `EventIngest`/`FusionEndpoints` are Server-layer
  and DO compile/run in this session (unlike the Injector), so these could have been real tests, but
  are text-scans here specifically to prove the WIRING independent of the fully-real proof below, the
  SAME reason `SpeciesAllocationCacheTriggerTests`'s own trigger-1/2/3 tests are text-scans even though
  parts of that chain are also Server-layer.
- `gk-core/tests/FusionRpg.Server.Tests/FusionAptitudesBroadcastTests.cs` (new): a REAL end-to-end proof —
  builds a real `WebApplication` + SignalR hub, joins the injector group with a real
  `HubConnectionBuilder` client, drives a REAL `/api/fusion/execute` call (a hand-built minimal
  `CreatureRecipeDef` from the compiled species default plus a real pooled species-passive container
  and a real forced inheritance pick — `RpgStore.Fusion.cs` only appends a 1b ledger row when the
  request carries at least one pick), and asserts the client actually receives `AptitudesUpdated`.
  A second test proves a replay (same correlationId) does NOT re-broadcast.

## A real, narrow architecture boundary respected, not bent

`CreatureRecipeCatalog.BuildDeterministicOnly()` (the test-safe recipe builder `FusionInheritancePicksTests.cs`
uses in Data.Tests) is `internal`, granted only to `FusionRpg.Data.Tests`/`FusionRpg.E2E.Tests` via a
deliberate C# assembly attribute (`InternalsVisibleTo.Fusion.cs`) — its own comment records that a
prior attempt to grant this more broadly (via the csproj) broke a real Core/Data separation guard.
Rather than widen that narrow grant to `FusionRpg.Server.Tests` for this task's own convenience, this
test calls the SAME PUBLIC `CreatureRecipeCatalog.Configure(IReadOnlyList<CreatureRecipeDef>)`
`Program.cs` itself calls, with one hand-built minimal recipe.

## Reviewed-vocabulary / closed-form note

No population-count or generated-text assertion is added or touched by this task.
