# creature-standalone-todo.md PT7 — patron aura LIVE gate: mixed result, one real defect found

**Claim:** the patron-creature spec's own LIVE checklist (`docs/architecture/creatures/spec-
patron-creature.md:114`, criterion 4) — the aura visibly, correctly, and cheaply works in a real match.

## Live sequence (real game, real server, real player 2, real roster specimens)

1. `POST /api/patron/set {"playerId":2,"instanceId":"032cdc9a...","correlationId":"live-qa-pt7-1"}` →
   `200`, computed aura `elementPrimary:"fire", powerMilli:47, defenseMilli:23`.
2. Clean full game relaunch (`debug_restart_game`) + fresh `debug_lawn_setup` (`entered:true`, a real
   `board.start`) — needed because a prior match was already running before patron was designated, and
   "takes effect next match" (spec line 14) means I needed a genuinely NEW board.start to observe it.
3. **Criterion 1 — session grant appears at board.start:** `GET /api/debug/effects/session-grants` →
   `count:1, grants:[{"grantId":"patron:aura","effectId":"fx.patron_aura",...}]`. Confirmed independently
   on the injector's own local view too: `debug.effect.list` → `grantIds:["patron:aura"]`. **PASS.**
4. **Criterion 2 — damage/power shifts by the aura:** `POST /api/debug/actor-derived {"ptr":"<plant>"}`,
   read back via `GET /api/debug/events?kinds=debug.actor-derived`: `combat.power.fire: {"value":47}` —
   the exact `powerMilli` computed in step 1. Confirmed non-fabricated by re-reading after allowing the
   sync to settle (a first read immediately after board entry raced ahead and showed `0` — a timing
   note, not a bug: the compiled atom catalog push and the match-start grant land a moment apart).
   **The magnitude is real and exact. But see the defect below — this criterion does not actually pass
   as specified.**
5. **Criterion 3 — board.end withdraws the grant:** `POST /api/debug/leave-board` (real menu-exit
   sequence, waits for the injector's own ack that the Board is destroyed) → `ok:true`. Re-read
   `GET /api/debug/effects/session-grants` → `count:0`. **PASS.**
6. **Criterion 4 — no new hot-path cost:** `GET /api/perf/recent` throughout: `kernel.tick avgUs:1.8`,
   `kernel.drain avgUs:0.6`, steady 60fps — unchanged from the pre-patron baseline (same numbers as the
   T11 probe run minutes earlier). The aura rides the same `GrantedDerivedAtomReader` path every other
   match-scoped grant already uses — not a new polled mechanism. **PASS.**
7. **Criterion 5 — mid-match patron switch is frozen until the next match:** attempted
   `POST /api/patron/set` (a different roster specimen) mid-match → `{"reason":"souls.insufficient"}`
   (switch costs 100 Souls; this live-probe player had none). `POST /api/test/seed-souls-demo` — the
   real SIM-only top-up route — correctly returned 405 (falls through to the SPA), because
   `SimFlags.Enabled` is off for this real, non-SIM run (`gk-core/src/FusionRpg.Server/Program.cs:1874`:
   `if (SimFlags.Enabled) app.MapSimAndProbes();`). Not a bug: the SIM-only seed route is correctly
   absent from a genuine live run, and spending real Souls to reproduce a currency-gated flow is out of
   this probe's scope (same call made for Fusion Checkpoint F2's `execute`). **Not tested** — needs
   either the owner's own played-up Soul balance, or a disposable test player already holding ≥100.

## Real defect found: the aura is not plant-side-only, contradicting the spec's own line

`docs/architecture/creatures/spec-patron-creature.md:27`: *"The aura lands on the patron's primary
element as `combat.power.{elem}` and half-strength `combat.defense.{elem}` deltas **for plant-side
reads**"* — explicitly plant-side only.

Live proof it is not: `POST /api/debug/actor-derived` for the **zombie** target ptr in the SAME live
match returned the identical `combat.power.fire: {"value":47}` — the exact same magnitude, on the
enemy side, that the plant received. **The patron aura is currently buffing the zombies too.**

Root cause, read (not guessed):
- `gk-core/src/FusionRpg.Core/Effects/Plugins/PatronSecondaryPlugin.cs` grants `OwnerKey =
  EffectOwnerKeys.Match` — the broadest scope key that exists.
- `gk-core/src/FusionRpg.Core/Stats/StatApplyScope.cs:52-53` — `Matches` returns `true` unconditionally for
  the `"match"` key, for **any** `side` (Plant or Zombie), by design: `if (key == "match") return
  true;` runs before any side check at all.
- The scope grammar (same file, lines 55-69) does have `plant:{typeId}` and `zombie:{typeId}` keys, but
  **no side-wide key exists** ("every plant regardless of species," as opposed to one named typeId) —
  so there is no drop-in fix by simply changing the owner key to an existing one.

This is why it is reported, not patched here: the real fix is either (a) adding a new side-wide owner
key to the shared scope grammar (`EffectOwnerKeys`/`StatApplyScope.Matches`) — a change to a primitive
every other match-scoped grant in the codebase also depends on, or (b) re-platforming the patron aura
onto `BattlefieldOwnSideReactor` (buff-debuff-scope's own relation-gated own-side mechanism, proven
correctly side-scoped in this same session's T11 probe: `tasks/evidence-fragments/
buff-debuff-scope-t11-live.md`) instead of a raw match-wide grant. Either is a real design decision
belonging to `spec-patron-creature.md`'s or `buff-debuff-scope`'s own program, not a same-session patch.

## Verdict

**3 of 5 criteria PASS clean (1, 3, 4). Criterion 2's magnitude is exactly correct but its SCOPE is
wrong** — a confirmed, live, spec-contradicting defect (buffs the enemy). **Criterion 5 not tested**
(blocked on a real Soul balance; the SIM-only seed route is correctly unavailable in live mode, not a
bug). PT7 does not close clean — reporting the defect with file:line rather than patching a shared
scope-grammar primitive in this pass.
