# Wave 5 (`empire-species-container`, SP5.1-SP5.5) — BLOCKED on a real, unbuilt cross-program dependency

## What was checked before concluding this (DESIGN-GATE: verify against code, not the spec's own
## assumed-future shape)

Read `docs/architecture/species-progression/spec-empire-species-container.md` in full. Its own Code
Style section (the `ReprojectEmpireSpeciesUnlocked` pseudocode) calls
`EffectiveSpeciesAllocationUnlocked(db, owner, speciesId, tuning)` where `owner` is an `EmpireRef`, and
reads `source_level` "through `SpeciesLevelOf`" (`ai-empire-species`'s own function,
`SaveId, EmpireId, typeId) -> level`). The spec itself flags this as forward-looking in its own prose
("Today's `EffectiveSpeciesAllocationUnlocked` takes `(playerId, speciesId, tuning, CommanderId)`
... its re-key to `EmpireRef` is `save-identity`'s migration, and its level read goes through
`ai-empire-species`'s `SpeciesLevelOf`") but the todo's own SP5.1 `deps:` line only lists `SE4.20,
SE4.21, SP3.7` — it does NOT list the `ai-empire-species` module (`empire-progression` `EP4.13`) that
the spec's own pseudocode actually requires.

Verified directly against the real, current tree (commit `8feb189f`), not assumed:

1. **`EffectiveSpeciesAllocationUnlocked` is NOT re-keyed to `EmpireRef` yet**
   (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Aptitudes.cs:210-239`). Its real signature is still
   `(SqliteConnection db, long playerId, string speciesId, AptitudeTuning tuning, EmpireId empire)`,
   and its own body's comment says outright: *"the species LEVEL row is per-player, and no Zomboss
   species level exists anywhere, so a non-Dave ask resolves Empty rather than the human player's
   progression."* SE4.20/SE4.21 (confirmed landed, `tasks/evidence-fragments/SE4.20.md`/`SE4.21.md`)
   re-keyed the Tier A tables (`rpg_actor_progression`, `rpg_xp_ledger`) to `(save_id, empire_id)` and
   re-typed `TryApplyXpUnlocked` to take an `EmpireRef` — but did NOT touch this specific read path.
2. **`SpeciesLevelOf(SaveId, EmpireId, typeId)` does not exist anywhere in `src/`** —
   `grep -rn "SpeciesLevelOf" src/ tests/` returns zero hits. It is `empire-progression`
   `tasks/empire-progression-todo.md:648`'s own `EP4.13` (`spec: ai-empire-species`, deps `SE4.21,
   SE4.4`), and no `EP4.x` task has an evidence fragment yet (`ls tasks/evidence-fragments/ | grep
   "^EP4\."` — zero) — confirming `empire-progression` has not been started by any lane.
3. The map's own module table (`docs/architecture/species-progression-map.md` row 5) states module 5's
   own dependency plainly: *"1, 3; external `save-identity`"* — but the spec body's own pseudocode
   additionally, silently, needs `ai-empire-species`'s reader. This is exactly the kind of wiring gap
   DESIGN-GATE names: the map's dependency ROW under-states what the spec's own CODE actually calls.

## Why this is not built around

Building SP5.1 today would require either:
- **(a)** a Zomboss-unaware, human-player-only `ReprojectEmpireSpeciesUnlocked` that reads the level via
  today's `playerId`-only path — this directly contradicts R1 ("zombie species XP credits Zomboss's
  empire... trigger 1 fires for them exactly as for the player's") and Success Criterion "Every levelled
  `(empire, species)` has exactly one container" (Zomboss is an empire; this shape cannot produce one for
  him). It would also need REDOING once `EP4.13` lands — a partial ordering this session's own hard-edge
  discipline (H1/H2/H7 plus "no partial ordering") exists to prevent.
- **(b)** building `EP4.13`/`ai-empire-species`'s reader myself, out of the `species-progression` ->
  `empire-progression` -> `build-preset` program order the coordinator's own brief set, and inside a
  DIFFERENT program's todo file no session has claimed.

Neither is taken. Per this session's own contract ("If the spec cannot be satisfied without breaking an
edge, stop and record a blocker naming the edge. Do not ship a partial ordering."), wave 5 (SP5.1
through SP5.5, all of which build on SP5.1's own reprojection function) is recorded **blocked** here and
skipped in full, rather than partially built.

## What is NOT blocked, and continues

The species-progression map's own module 6 (`species-layer-delivery`) dependency row states step 6.1
depends on module 1 (done) + `action-base`'s re-bless, and step 6.2 depends on module 4 (done). Only
step 6.3 (the 2b cutover, `SP6.10`-`SP6.11`) depends on module 5. Wave 6 steps 6.1 (`SP6.0`-`SP6.1`) and
6.2 (`SP6.2`-`SP6.9`) proceed now; step 6.3 (`SP6.10`-`SP6.11`) is recorded blocked on the same
`EP4.13`/module-5 dependency when reached.

## Resolution path (for whoever unblocks this)

Once `empire-progression`'s `EP4.13` (`SpeciesLevelOf(SaveId, EmpireId, typeId)`) lands and
`EffectiveSpeciesAllocationUnlocked` is re-keyed to take an `EmpireRef` (both named in the spec's own
Code Style section), wave 5 (SP5.1-SP5.5) can build exactly as specified — nothing else in this
session's work needs to change first.
