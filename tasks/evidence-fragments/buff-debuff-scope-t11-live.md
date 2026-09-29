# buff-debuff-scope-todo.md T11 — LIVE gate, all 5 acceptance criteria proven

**Claim:** `BattlefieldOwnSideReactor`, wired to a real match via `DebugScopeRuntime` (T11a), grants
and withdraws an own-side effect correctly against real membership transitions on the live game, and
refuses a G8-shaped kind rather than granting it — the todo's own five acceptance criteria.

## Blocker closed first: T11a's server route was never added

`gk-core/src/FusionRpg.Server/DebugEndpoints.cs` had `debug.scope.start-own-side` / `debug.scope.stop-own-side`
built in the injector (T11a) but no `MapPost` exposing them over HTTP — T11 was unreachable through
any normal path. Added the two missing routes (same pattern as the adjacent `/effect/dots`,
`/effect/counters` lines). `guard-debug-scope.py`: both classify `[GameInjectorDebug]`, 104 routes,
0 mismatches. Build: 0 errors.

## Correcting my own first attempt

First pass started the scope then spawned a **vanilla** plant (`POST /api/debug/spawn-plant`) and saw
`grants:0` — reading `UniqueBindings.cs` showed why: `MembershipChanged` fires only from
`UniqueBindings` (`Bound`/`Cleared`/`MindControlToggled`), a real **unique-bound specimen**
lifecycle, never an ordinary plant/zombie placement. Re-ran against the real precondition: a unique
specimen minted via `POST /api/creatures/debug/grant`, deployed via `POST /api/unique/actors/{id}/deploy`.

## Live sequence and evidence (real match `2d67f971-b80c-4ecb-8405-11c413c0b2f0`, real HTTP, read back
via `GET /api/debug/events`, never the fire-and-forget call's own `{"queued":1}` body)

1. Started scope: `POST /api/debug/scope/start-own-side {"effectId":"fx.passive_atk_flat","relation":"ally","host":"live"}` → injector log confirms received, no error.
2. Deployed roster specimen `653f6cb0...` (AllPeater, typeId 1347) into the live match:
   `POST /api/unique/actors/653f6cb0.../deploy {"col":6,"row":2,"matchKey":"2d67f971-..."}` →
   read back `GET /api/unique/actors/{id}`: `phase:"ActiveBound"`, `lastPtr:"20E78C35240"`.
3. **Criterion 1 + 2 — one correctly-named grant, mid-match, no restart:** `debug.effect.list` (event
   id 45013) right after: `grants:3, grantIds:["debugscope:debug-scope:20E78C35240",
   "lawn-basic-attack@20e78c35240","lawn-basic-attack@20e78c35480"]` — the own-side grant landed on
   the JUST-bound specimen only, not on the pre-existing vanilla Peashooter. **PASS.**
4. **Criterion 3 — leaving loses it:** `POST /api/debug/kill-plant {"ptr":"20E78C35240"}` → real
   `plant.die` event (id 45071, `reasonName:"BySelf"`) → unique row read back
   (`GET /api/unique/actors/{id}`): `phase:"ActiveBound"` → **`"Roster"`**. Next `debug.effect.list`
   (id 45095): `grants:1, grantIds:["lawn-basic-attack@20e78c35480"]` — the own-side grant is gone,
   only the unrelated vanilla plant's baseline grant remains. **PASS.**
5. **Criterion 4 — G8-shaped kind refused, not granted:**
   `POST /api/debug/scope/start-own-side {"effectId":"fx.passive_atk_flat","atomKindId":"stat.modify","channel":"defense","host":"live"}`
   → `cheat.apply` event (id 45142): `"note":"ERR debug.scope.start-own-side: ScopeUnsupported —
   ScopeUnsupported: stat.modify at (battlefield, relation, live) has no compatibility entry."` —
   confirmed by reading `DebugScopeRuntime.StartOwnSide`: the reactor's constructor validates via
   `ScopeCompatibility` and throws **before** subscribing, so nothing was granted and nothing needed
   unsubscribing. Following `debug.effect.list` (id 45148): `grants:1` — unchanged, no new grant.
   **PASS.**
6. **Criterion 5 — no new hot-path cost:** `GET /api/perf/recent` during the whole sequence:
   `kernel.tick avgUs:1.9`, `kernel.drain avgUs:0.8`, `kernel.schedule avgUs:0.1`, steady 60fps
   (`frames.maxMs:16.73`, `gte33ms:0`). No new per-frame section appeared for the scope reactor,
   because the mechanism is event-subscription only (`MembershipChanged +=`), never a polled tick —
   confirmed by reading the source, not inferred from perf numbers alone. **PASS.**

## Verdict

**All 5 acceptance criteria PASS, live, against real production paths** (real unique-actor mint/
deploy/death, real `ScopeCompatibility` refusal, real perf window) — not Game Injector Debug
telemetry standing in for proof of itself: every read-back used `GET /api/unique/actors/{id}`,
`GET /api/debug/events`, or `GET /api/perf/recent`, never the triggering call's own response body.

**Correction to the todo's own 2026-08-29 note.** That note reads *"the assistant session cannot
execute or observe this gate... no amount of further building changes that,"* reasoning from "needs a
human watching a real rendered game window." That premise does not hold for any of the five criteria
as written — all five are grant/state/perf facts already exposed on the normal debug-event and REST
surface, which is exactly what this probe read. The rendered game window was never in the loop.

## Left as-is

Own-side scope stopped clean (`StartOwnSide` calls `StopOwnSide()` first; the failed G8 attempt threw
before assigning `_active`, so nothing needed unsubscribing — confirmed by reading the source, not
assumed). `debug.effect.list` after the sequence: `grants:1` (only the unrelated vanilla plant's own
baseline grant) — board left in a clean state.
