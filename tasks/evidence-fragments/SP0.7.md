# SP0.7 — Coordination: hand over the map §9 lines owned by other sessions

Spec: species-mod-ledger; species-progression-map.md §9 ("Amendments owed by other sessions"). This
program edits none of the files below — this fragment IS the hand-over message, and
`tasks/species-progression-todo.md`'s own SP0.7 row records that it was sent, per this task's own
"Files" line.

## Spot-check: no drift since the map §9 table was written (2026-09-18)

Every cited line was re-read against the current worktree before this hand-over. All five are still
in their original, unamended state — the hand-over is still owed, not stale:

- `docs/architecture/solid-remediation-map.md:109` — still `| S5 | fixed | T4.5 — **premise corrected**...`
- `tasks/solid-remediation-todo.md:697` — still `[x] T4.5 ... "It was never lost."`
- `tasks/solid-remediation-todo.md:963` — still ticks "Fusion picks change a player's actors" against T4.6
- `docs/architecture/solid-remediation/spec-species-carrier.md:16` — still `S5 | ... MaterialisePlayerSpecies lost its only caller`
- `docs/architecture/solid-remediation/spec-species-carrier.md:38-50,65,84,187` — still describes the eager `Program.cs` caller as the fix, and still checklists `[ ] MaterialisePlayerSpecies has a production caller...`
- `docs/architecture/creature-seed/spec-player-materialise.md:52` — still `"the new ones are rolled on next load and appended"`
- `docs/architecture/solid-remediation/spec-species-empire-scope.md:75` — still `SpeciesAllocation.ScopeKey(playerId, empire, speciesId)`, Zomboss under the human's `playerId`

Confirmed, not re-requested (acceptance bullet 2): `decisions.md:52`/`:119` (old line numbers) have
already landed — map §9 itself marks both "✅ landed ... 2026-09-18". No action owed there.

## Rows handed over (exact amend-to text from map §9)

| File:line | Owner / when | Amend to |
|---|---|---|
| `docs/architecture/solid-remediation-map.md:109` | solid-remediation session; **now** | S5 re-darkened by T4.5 (picks refused); closed by `species-mod-ledger` |
| `tasks/solid-remediation-todo.md:697`, `:963` | solid-remediation session; **now** | note the re-darkening and the owning fix |
| `docs/architecture/solid-remediation/spec-species-carrier.md:16`, `:38-50`, `:65`, `:84`, `:187` | solid-remediation session; **with module 4** | T4.5's eager caller superseded; S5 closed by `species-mod-ledger` (delayed preview + ledger) |
| `docs/architecture/creature-seed/spec-player-materialise.md:52` | creature-seed program; **with module 4** (no active session claims `creature-seed` — owed to whoever next claims it) | superseded: no eager roll; the delayed preview |
| `docs/architecture/solid-remediation/spec-species-empire-scope.md:75` | `SE save-identity` session; **now, to land together with that migration** | re-keyed by `save-identity` (`EmpireRef` encoder; the persisted strings stay) |

**Module 4 (wave 0) is CLOSED as of this commit** (SP0.1-SP0.6 done, SP0.7 in progress, Checkpoint 0
next) — so the three "with module 4" rows above are now actionable immediately, not blocked on future
work in this program.

## Disposition list carried alongside (spec's own "Tests to rewrite" table, current status)

| Test (file:line) | Disposition (spec) | Actual status in this lane |
|---|---|---|
| `PlayerSpeciesMaterialiseCallerGuardTests` `:27`,`:37`,`:58` | retired; replaced by `No_production_code_writes_layer_1b_outside_the_ledger_append` + `No_production_code_rolls_a_players_species_eagerly` | **done** — SP0.5 (`630f6b0e`) |
| same file, `.The_rolled_species_instance_reaches_a_composer` (`:76`) | rewritten by `species-layer-delivery` step 6.2 | **interim done** — SP0.5 repointed it to `GetSpecimenLedgerRoll`; the spec's own module name ("species-layer-delivery step 6.2") reads as this program's SP3.6/SP6.8 in the current todo numbering — a naming drift between this older spec text and the todo, not a substance conflict. Final replacement still owed to SP3.6/SP6.8 |
| same file, `.The_nine_pick_refusal_codes_are_a_closed_vocabulary` (`:91`), `.The_status_clock_costs_no_round_trip_on_the_injector_hot_path` (`:130`) | kept unchanged | **confirmed unchanged**, still green |
| `PlayerMaterialiseTests` (whole file) | rolled into `SpeciesRollPreviewTests` | **done** — SP0.2 (prior session) + SP0.6 retired the file outright (`80559a75`) |
| `SpecimenMaterialisedRollTests` | restated on the preview + ledger | **done** — SP0.5/SP0.6 (`630f6b0e`, `80559a75`) |
| `FusionInheritancePicksTests` | picks land in the ledger | **done** — SP0.3 (prior session), re-verified green in SP0.5/SP0.6 |
| `ReforgeWorldEndpointTests` `:130`,`:141-146`,`:198-213` | "the species step's assertions are removed with the step; the endpoint's other steps keep their tests" | **stronger than planned, with a correction**: the endpoint had no other steps — its ENTIRE body was the species reforge — so SP0.6 retired the whole file, not just the species-step assertions (recorded as a correction in `tasks/evidence-fragments/SP0.6.md`) |
| `LawnElementResolverTests` `:553-560` | rewritten to assert the handler does not touch species rows | **stronger than planned**: rewritten to assert the route no longer exists at all (SP0.6) |
| `SpeciesPassiveAtomSourceTests` | moved to module 3 | **not started — correctly out of this wave's scope.** File exists untouched at `tests/FusionRpg.Core.Tests/Battle/SpeciesPassiveAtomSourceTests.cs`; owed to whichever session builds module 3 |

`tests/**`'s fence is crossed with the owner's knowledge per this note: SP0.5/SP0.6 edited
`PlayerSpeciesMaterialiseCallerGuardTests.cs`, `SpecimenMaterialisedRollTests.cs`,
`LawnElementResolverTests.cs`, and deleted `PlayerMaterialiseTests.cs` / `ReforgeWorldEndpointTests.cs`
— every one of them named in the spec's own "Tests to rewrite" table, so none of this was an
unplanned crossing.

| Criterion | Result |
|---|---|
| Each row handed to its owning session with the exact amend-to text | done — table above, verbatim from map §9 |
| Confirmed, not re-requested: `decisions.md:52`/`:119` | confirmed landed, no action |
| Every row still open at Checkpoint 0 listed under it with its owner | done — five doc/task rows + nine test-table rows, all above |
| `python scripts/session-boundary-check.py` clean | pass — only pre-existing DRIFT entries for unrelated abandoned worktrees (see the anchor's own Peers line); nothing naming this session's own paths |
