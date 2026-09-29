# AE2.4 — live probe: BLOCKED (owner-run)

**Status: BLOCKED.** This item cannot be cleared from an agent session: it needs the game running
with the injector attached and the RPG Server up on a real save, and starting those (and leaving them
running) is the owner's call. Nothing here was skipped — the probe procedure and the acceptance
criteria are written out below so it is a single run when the environment is up.

## Why it is blocked, measured

`debug_preflight` (read-only), this session:

```
live.ready = false
  server    : reachable = false  (timed out; :5088 free)
  gameProcess: running  = false
  injector  : connected = false
  board     : observed  = false
also FAIL: game-dir (no FUSIONRPG_ML_GAMEDIR / FUSIONRPG_GAME_DIR / .env default),
           interop-refs, dll-freshness, data-dir (no dist/FusionRpg.Server/data/rpg-hot.sqlite),
           node-modules
```

So no live evidence can be produced from here. Per the lane's own rule, an owner-only item is
recorded BLOCKED rather than skipped.

## Prerequisites (owner)

1. Server: `Start-Process dist\FusionRpg.Server\FusionRpg.Server.exe` — started as its own process,
   never from an agent tool call (a server started under an agent's process tree dies with it and
   looks like a mid-run crash; `docs/runbook/local-dev.md`).
2. Game: launch the MelonLoader host with the injector deployed (`.\scripts\deploy-play.ps1 -NoServer`
   from the owner's own terminal). Default pack: `H:\Games\PVZ-Fusion-3.9_MelonLoader`.
3. A real save with a real commander, so `Θ` is a real hydrated value rather than 0.

## The probe, exactly as the acceptance words it

Per `docs/contributing/live-probe-standard.md`. **Scope must be named on every number** — this is the
incident the standard was written for (a probe that fabricated its own result and read it back):

1. **Θ through the RPG Server's NORMAL query path** (scope: RPG Server) — the real
   `/api/...` read, never a debug-fabricated value. Record the commander's `Θ`.
2. **One real lawn hit's delta** from real injector telemetry (scope: Game Injector) — a real swing on
   the board, not a debug-bound grant. `BasePerHit(base, P(Θ))` must equal that delta *before defense*.
   `base` is `action-base.v2.json`'s `basicAttack.basePowerMilli` (140); `P(Θ)` is `BattleRuleset.PowerValue`.
3. **Change Θ through the real progression path** (never a debug write), then confirm the NEXT hit
   follows the new value **without a respawn** — that is AE2.3's drain, observed end to end.
4. Read the changed state back through the normal path; a response body is never proof on its own.

Evidence lands as `docs/research/action-enrich/live-probe-<date>.md`, quoting the decisive lines and
naming the scope of each number.

## Also required by this item's acceptance

- The full suite green first: `.\scripts\test-fast.ps1 -AllDefault` (the AGENTS.md "immediately before a
  live probe" point). Not run here: the probe it gates cannot run, so running the ~9-minute cross-program
  suite now would produce evidence nobody can consume.

## What is already proven, so the probe is the only gap

AE2.1-AE2.3 are green and committed: the instakill refusal, the parity between the lawn's baked amount
and the battle's own base expression (`TheBakedAmountIsTheBattleBaseForTheSameTheta...`), the planted
Theta-contributor falsifier (`LawnGrantThetaParityTests`, 3/3), and the record-then-drain refresh
(`LawnBasicAttackGrantBinderRefreshTests`, 6/6). AE2.4 is the only item in the lawn half that requires
the live pair.
