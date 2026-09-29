# actor-hud LIVE eyeball (3 owner-run checkboxes)

**Claim:** on a real lab-overlay lawn board, `ActorHudPool`'s world-space health/shield bars and
status tokens render above live entities; the shield row matches the old `ShieldBarPool`'s look; no
double shield bar exists.

## Real finding, before any visual could be judged: the world HUD is default-OFF

`POST /api/debug/shield/bar-status` (the injector's own one-shot pipeline audit,
`CheatCommandRunner.cs:1292`) on a fresh lab-overlay board with a live plant+zombie read:

```json
"lastDraw": { "early": "world-hud-off", "hudSlots": 0, "shaderOk": false }
```

`gk-fusion/src/FusionRpg.Injector/Hud/ActorHudPool.cs:101`: `WorldHudEnabled` defaults to `false` — an owner
decision ("check it can improve or else... we will disable a default and add user setting on the web
FE", perf-driven, `perf-probe-plan.md` §0's 2 ms/frame budget) — the player turns it on from the web
FE, which sends the setting `lawn.worldHud` through `PUT /api/settings`. **A live probe (or anyone
driving the game purely through the debug API rather than the web FE) that never flips this setting
will see nothing, every time**, which is very likely why these three checkboxes have sat unticked —
not because the HUD is broken, but because nothing in the debug tooling flips this switch for you.

## After enabling it through the real production setting

`PUT /api/settings {"key":"lawn.worldHud","value":true}` (the real endpoint a player's web FE uses) →
`200 {"ok":true,"key":"lawn.worldHud","value":true}`. Re-ran the same diagnostic:

```json
"lastDraw": { "early": "no-shield", "hudSlots": 2, "shaderOk": true }
```

`hudSlots` moved 0 → 2 (tracking the live plant + zombie), `shaderOk` moved `false` → `true`. The pool
is now genuinely active and resolving real entities.

## Visual read (screenshot, 960x531 — the debug screenshot's native resolution)

With `lawn.worldHud` on and two real zombies attacking a real Peashooter: small floating `1` numerals
above the plant and one zombie, and a small light square icon above the other zombie's head. At this
resolution I cannot conclusively tell a health/shield BAR apart from a PvZ-native damage floater or a
status-token icon. **The screenshot this read was taken from is not in this repository**: it was named
`tasks/evidence-fragments/screenshots/actor-hud-damage.png`, that directory was never committed, nothing is
tracked under it, and no copy of the image survives on this machine — so the read below cannot be
re-verified from the tree, and the visual claim still needs a closer/zoomed capture than this debug
primitive gives to sign off with confidence. What *is* landed is
`tasks/reports/actor-hud-unity-live-20260926.md`, whose per-frame table records each capture with its
timestamp and what it showed. `hasInstances:false` for the
shield-grant test specifically (`item.fx-shield-grant`'s atoms are `OnDamageDealt`/`OnTimer`/`OnSpawn`
triggered, not an instant grant — none fired before I read the diagnostic), so the shield-bar-parity
half of the claim (items 2/3) could not be visually confirmed either way in this pass.

## Verdict

**Not a clean PASS or FAIL — a real, previously-undocumented precondition found and cleared.** The
`world-hud-off` default is the actual reason these three checkboxes were never signed off by a
debug-driven probe; ticking them now requires either a human eyeballing the web FE (where the setting
is a visible toggle a real player would find), or a follow-up live-qa pass with a higher-resolution
screenshot capture after `lawn.worldHud` is on. Recorded rather than ticked — an honest "not proven"
per this session's own standard, not a fabricated pass.

## Worth landing as a repeatable check

`gk-core/scripts/prove_actor_hud_live.py` already exists for this program — it should set
`lawn.worldHud=true` via `PUT /api/settings` as its own first step, so a future run of it does not
need to rediscover this gate.
