# SP6.9 — Live proof of 1b + perf; hand over the T4.2 doc lines

**Partial: doc handover done; live-probe and perf portions BLOCKED, owner-only.**

| Criterion | Status | Evidence |
|---|---|---|
| A real fusion through `/execute`, on real-gameplay-minted specimens, changes a lawn actor's composed value, read back through `/derived`/the sheet | **BLOCKED — owner-only** | needs the owner's real running game/server; no local substitute reaches an actual lawn actor |
| `probe-perf.ps1 -Scenario <lawn 300z id> -DurationSec 60` stays within budget | **BLOCKED — owner-only** | needs the live game running |
| `spec-species-empire-scope.md:150-165` / `:175-179` handed over with map §9's amend-to text, or recorded under Checkpoint 3 | **DONE** | `docs/architecture/species-progression-map.md` §9, both rows |

## Why the live-probe/perf portions are blocked, not skipped

This mirrors the `goal-loop-owner-only-gate` precedent already established elsewhere in this program:
`live-probe-standard.md`'s own RPG Server scope requires a real running game/server driving a real
`/api/fusion/execute` call against a specimen real gameplay minted, with the result read back through
`/derived` or the sheet — **never from injector telemetry alone**, and never a debug-route or `test.*`
mint standing in for it. A background implementer session has no owner-machine game process to drive
this against. `FusionAptitudesBroadcastTests.cs` (SP6.5, extended by SP6.8's own DI fix) is the closest
available proxy — it drives a REAL `/api/fusion/execute` call against a REAL minted-and-fused specimen
and reads the result back through `RpgStore.ListSpeciesMods`/`SpeciesLayersForSpecimen` — but it is a
Server-only in-process host with no lawn actor, no injector, and no live game behind it. It proves the
SERVER-side half of this feature end to end; it is explicitly NOT the live-probe this acceptance line
asks for, and is not reported as one. `probe-perf.ps1` has the identical requirement (a real running
lawn) and is equally out of reach here.

## The doc handover (done)

`species-progression-map.md` §9's own header states the rule this task's acceptance follows: this
program reads `solid-remediation`'s documents and **never edits them** — each contradicted line "must
be amended by the session that owns it." `spec-species-empire-scope.md` is one of those documents, so
neither of its two named line ranges is edited here. Instead, per this task's own explicit "or recorded
under Checkpoint 3" alternative, `species-progression-map.md` §9's two rows for those line ranges are
updated to record that delivery 6.2 (SP6.2-SP6.8, all landed and re-verified this session) makes the
amend-to text TRUE and ready for `solid-remediation` to apply to its own file:

- **`:150-165`** ("that set is exactly `{Dave}`"; "added no fourth trigger"): now false as written —
  `speciesLayers.mod` (SP6.3) is keyed by every empire of the save with ledger rows, and the save switch
  IS now a real key-set trigger (SP6.6). The specific test the old line cites by name
  (`The_cache_holds_exactly_one_empires_rows_and_refuses_to_answer_for_another`) was itself REPLACED in
  SP6.6 by `The_cache_answers_each_side_from_its_own_empire_and_never_the_other`.
- **`:175-179`** ("a match edge is not a species trigger"): now true only with the one exception the
  amend-to text names — the `board.start` after a mid-run save switch (SP6.6's deferred-refresh
  mechanism). The specific test cited (`A_match_edge_is_not_a_species_trigger_and_the_trigger_set_was_not_copied`)
  was itself amended in SP6.6 to name that exception.

## Checkpoint 3's own two lines

- **"The per-path tests are green on all six paths... each has a test that fails when the wiring is
  removed."** DONE — `SpeciesLayerPathTests.cs` (SP6.8, 7 tests, one per `layer-source-selector` cell:
  lawn general plant/zombie, Bound unique, sheet, world-turn, web-squad, plus save isolation) and the
  19 trigger tests across `SpeciesAllocationCacheTriggerTests.cs`/`SpeciesLayerCacheTriggerTests.cs`
  (triggers 1-6, SP6.2-SP6.6) are all green (confirmed this session, both individually and in their
  whole-project runs).
- **"SP6.9's live read-back and perf reading are recorded. Any pin that moved in step 6.2 is listed as
  'new layer delivered'... never as a re-bless."** Recorded above as BLOCKED (owner-only). No pin moved
  in step 6.2 (SP6.2-SP6.8): every one of those tasks is additive — `rpg.species-layer` is a source
  nothing referenced before this wave, so nothing it contributes could have been an existing, moving
  golden. The one genuine re-bless in this program is step 6.1 (SP6.1), already closed, re-blessed in
  its own single commit, and recorded in Checkpoint 2 — a separate checkpoint from this one.

## Reviewed-vocabulary / closed-form note

No population-count or generated-text assertion is added or touched by this task.
