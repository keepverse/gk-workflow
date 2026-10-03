# Ideal: status tracks

**Objective — one mechanism, two drives.** A player-facing status is either doing damage over time
inside a fight, or projecting a counter that lives outside one. Those are two *tracks*, not two
*systems*. The whole shape of this program is that they share `StatusRuntime`, share the
`entity:{ptr}` bag, and share one vocabulary — and differ only in **who calls `Sync`** and **which
clock answers the decay**.

This document is the reasoning. The locked rules live in
[decisions/combat.md](decisions/combat.md) (row *Status tracks — combat and out-of-combat*) and the
existing [status-ssot.md](status-ssot.md); the build order lives in
[status-tracks-map.md](status-tracks-map.md).

## 0. What already ships (do not rebuild)

Measured against `gk-core/src` on 2026-10-02, not inferred:

- **`StatusRuntime`** ([status-ssot.md](status-ssot.md)) — instance bag, lifecycle, status ICD,
  Apply-time resistance/immunity, contagion hops. 24 registered ids.
- **DoT and HoT are one payload.** `PulseHp` with a negative magnitude is damage, a positive one is
  regen (`StatusRuntime.cs:407`, `BattleModels.cs:259`). Regeneration is *not* a separate mechanism.
- **CC gating is live.** `IsCrowdControl` is derived from the def's **category**
  (`StatusRuntime.cs:286`) and read by the seat check (`BasicAttack.cs:145`) — eight ids genuinely
  prevent acting today.
- **Stat mods are live.** `ModifyStat` → `StatusStatPayload` → the battle ledger, withdrawable on
  expiry, across 23 primary channels and the registered `combat.*` set.
- **Two out-of-combat projections already work in spirit**: `nerve.*` (`NervePolicy.cs:92`) and
  `exhaustion.{resourceId}` (`ExhaustionPolicy.cs:99`). A third, `wound.*`, was **approved as a
  decision on 2026-09-13** (`decisions/combat.md` Status SSOT row) but has **no shipped id yet** —
  it is module 2 (`injury-tiers`) of `deployment-hierarchy-map.md:110`, still proposed.

  *Corrected 2026-10-02:* this bullet previously read "A third, `wound.*`, **landed** 2026-09-13",
  inside a section headed "What already ships (do not rebuild)". Checked against the code and it is
  false as a shipping claim: there is no `wound.*` entry in `status-catalog.v1.json`, in
  `StatusCatalogBootstrap.RegisterAll`, or in `StatusCategoryRegistry`'s map — the registry's 24 ids
  are the same 24 the bootstrap registers. What landed on 2026-09-13 is the **decision row**, not the
  statuses. A stale positive here is the dangerous direction: it invites a reader to treat a planned
  family as existing precedent they need not build.

So the engine question is settled: **there is no second status engine to build, in this engine or in
any other.** The gap is authoring surface on one side and a missing *drive* on the other.

## 1. The distinction that actually matters

A combat status **pulses**: it has a `periodMs`, the runtime calls it, and it emits a damage packet.
An out-of-combat status **projects**: a counter somewhere else changes, and a `Sync` writes the
status that describes it.

The consequences are structural, not cosmetic:

| | Combat track | Out-of-combat track |
|---|---|---|
| Driver | `StatusRuntime.Tick(now, …)` off the battle's virtual clock | a caller's `Sync(runtime, hostPtr, value, now)` |
| Clock | battle ticks, 1 tick = 1 ms (`BattleEngine.cs:456`) | **none** — counted in events, never wall time |
| Lifetime | `ExpiresAt` from `durationMs` | `BaseDuration 0` → `ExpiresAt = MaxValue`, persists until withdrawn |
| Magnitude | `EffectiveMagnitude`, read by the pulse | inert (`1.0`) — the payload is `StatMods` |
| Source of truth | the instance | **a scalar in durable state**; the status is its mirror |

That last row is the one that gets forgotten. `StatusInstance` has no count
(`StatusRuntime.cs:8-62`) and `Refresh`/`Replace`/`Coexist` are re-apply policies
(`StatusRuntime.cs:303`), so **nothing on the status is a counter**. The projection pattern exists
precisely to keep the truth off the status — `NervePolicy.cs:22-28` states it as the reason the
build exists.

## 2. Why the out-of-combat track has no clock, and what it uses instead

The repo refuses wall time here on purpose, and the refusal is load-bearing, not incidental:
recovery is counted in delves, the pool tables carry **no `*_utc` column** (`RpgStore.cs:670-672`),
`guard-clock-seam.py` fails the build on a stray `UtcNow`, and the spec's owner rationale is that
wall-clock meters read as a paywall (`spec-delve-attrition.md` §7 R6, `:45-47`).

Three legal decay sources, all shipped patterns:

- **Per-room charge** — `HungerCharge.ForRoom` (`HungerCharge.cs:27`), charged on room entry from
  the archetype's hazard band. No clock, fully deterministic, already the shallow-farm throttle.
- **Per-delve-crossing** — the `CloseDelve` recovery decrement, inside the same transaction
  (`RpgStore.Delve.cs:1152`). Counter, never a due stamp.
- **A virtual `long atTick` you advance yourself** — legal in principle, but note the delve's pool
  API takes the tick as a parameter and **no shipped caller supplies one**: `PartyPoolsCarry.BuildForBattle`
  (`PartyPoolsCarry.cs:44`) and `CarryOut` (`:58`) both take `long atTick`, and so does
  `RestResolver.Heal` (`RestResolver.cs:36-58`) and `DelveResourceDelta.Apply` (`DelveResourceDelta.cs:35`),
  but `PartyPoolsCarry`'s three entry points have **zero production callers** — the live delve path
  (`FusionRpg.Server/DelveBattleSession.cs`) never reaches them, and `RestResolver.Resolve`'s own
  call site is recorded as unbuilt (`EventDeck.cs:374-378`). The spec says the same outright
  ("between rooms no tick advances", `spec-delve-attrition.md:120-123`). Building it means a new
  monotonic integer in party state. Possible, not free.

  *Corrected 2026-10-02:* this bullet previously read "every pool call site passes `atTick: 0`". Checked
  against the source, **no call site passes `atTick: 0`** — there are no call sites to pass it. `atTick`
  is a *parameter* of five pure, clock-free functions, all of which are unwired in production. The stale
  form was the same failure as §5.1's: a true fact about the parameter's contract ("nothing reads wall
  time") stated as a fact about the call graph.

**The consequence for design:** a new out-of-combat need must be chargeable *by an event*. A need
that only makes sense decaying with elapsed real time has no legal home, and that is a product
answer to get before the code, not a coding problem.

## 3. Pool or projection? — the honest split

Both are legal. They are not symmetric, and the deciding question is **"does anything spend it?"**

**A seventh `ActorResourcePool`** — when the need is a spendable 0..max scalar with an action-cost
meaning and a live HUD meter. Cost is real but *procedural*: append one id to
`DerivedStatChannels.ResourceIds`, add a row to `resource-catalog.v1.json` and the seed roster,
add `battle-resources.v2.json` rows, regenerate the aptitude edges (24 new ones — measured,
`action-corpus-ideal.md:1029-1043`), and let the parity guards fail until each is satisfied. Four
locked tests go red on purpose: the resource-count pin, the decisions-doc assertion, the aptitude
six-coverage check, and the catalog parity. It is **an ADR** (`resource-hub-ssot.md:134`), and the
repo has walked it once cleanly (`poise`, 2026-08-26).

**A status projection** — when the need is graded and thresholded with tiered consequences. No ADR,
no locked count to move, no aptitude work. Cost is ~5 small files: a ladder function, a `Sync`
policy, a registry line per stage, a catalog row per stage, a caller. `nerve.*` is that shape today,
and the approved-but-unbuilt `wound.*` is specified to follow it exactly
(`deployment-hierarchy-map.md:110`).

**The asymmetry worth stating plainly:** the projection is strictly more code for a *number*, and
strictly cheaper for a *tier*. If the design wants a bar on the HUD that fills up, only the pool
reaches it. `ActorHudResources.Meters` **is** wired — `ActorHudBuilder.cs:51-54` is its first-ever
producer, E41 — so the "no meter exists" reading is wrong; but that producer is a
**per-ptr atom-authored store** (`ActorHudMeterOverride`), fed only by an `ui.present` atom whose
`op` is `meter` (`EffectBag.cs:779-798`), and its `meterId` vocabulary is *literally*
`DerivedStatChannels.ResourceIds` (`AtomKindRegistry.cs:935-940` reads the same live list
`resource.delta`'s `channel` does, not a copy). So a status still cannot publish a ratio — the meter
channel is resource-shaped by construction, and widening it is the same ADR as a seventh pool.

## 4. What a track is allowed to be

Given the above, the candidate needs fall out rather than being chosen:

- **Thirst** — a drain with a threshold consequence. Projection, unless it becomes an action cost.
- **Temperature** — two-sided and signed. Neither carrier fits cleanly; a ladder of stages is the
  only honest representation, and it is a ladder in *both* directions, which the shipped
  `NerveLadder` does not do (its thresholds are one-sided).
- **Morale** — tiered consequences, nothing spends it. Projection.
- **Disease** — escalation with contagion semantics. `StatusRuntime` already owns contagion, so
  projection is the native home.
- **Sleep / fatigue** — historically *removed* from this game for the paywall-adjacency reason
  above. Any revival is a product decision first.
- **Poison exposure** — already shipped as a combat status (`poison`). Only the environmental
  accumulation is new.

## 5. The drive is the real work

The sharpest finding of the audit, and the thing a plan built from the engine's surface would miss:

- **`NervePolicy.Sync` has zero production callers.** Its only call sites are tests. The spec
  describes a loop ("at room entry, after every carry-out and after every rest") that was written
  before the caller existed.
- **`ExhaustionPolicy.Sync` has exactly one**, and it is in the PvZ lawn
  (`LawnExhaustionLifecycle.cs:93`), driven by an **edge detector** that fires only when the
  boolean answer flips.

So the pattern's *mechanisms* are built and tested, but the *drive* for a pure out-of-combat track
does not exist. `EventOutcomeDispatch.cs:66-77` says why, and its answer is the right one: without a
live `StatusRuntime`/`hostPtr`, move the scalar with plain arithmetic and **defer the projection to
whichever room's battle setup runs next**.

That is not a limitation to route around. It is the shape: **the scalar is authoritative and always
updatable; the status is a rendered projection of it, refreshed whenever a runtime exists to
receive it.** A track that needs the status to be correct at every instant, in a place with no
runtime, is asking for a second engine — which is the one thing this program refuses.

### 5.1 Two "combat gaps" this program does NOT own — corrected 2026-10-02

An earlier draft of this document named two combat-status gaps. **Both claims were checked against
the code and both were wrong.** They are recorded here rather than deleted, because a stale claim
that survives is how a reader learns the wrong thing.

- **D1 is already fixed.** The conformance table once reported that battle's `EffectBag` never set
  `CombatMath`, so every effect-driven hit — DoT tick, on-hit rider, atom damage — applied its
  authored number verbatim with no hit roll, crit, matchup, penetration, parry or block.
  `BattleRunState.cs:469-497` (solid-remediation T2.5) wires `Bag.CombatMath` through
  `OverlayCombatMath.Create(resolveActor, rng: effectCombatRng)`, together with the
  `ActorResolve` and the battle-seeded `effect-combat` RNG stream it needs. A status pulse now
  resolves through the same math as a swing.
- **Speed ordering is not inert everywhere.** The claim was that `turn.haste` is legal but
  `classic-round` never reads it, because `BattleEngine` orders by speed only when a profile sets
  `OrdersBySpeed`. That is true *of `classic-round`* and false as a general statement:
  `BattleModeProfile.Delve` is built with `ordersBySpeed: true` (`BattleModeProfile.cs:295-300`), so
  the delve profile — the one this program is about — does read readiness, and haste is live there.

What survives is narrower and more honest: **no shipped `data/tuning` profile row sets an
orders-by-speed flag at all** (`ordersBySpeed` appears nowhere in `gk-core/data/tuning/*.json`), so
the tuning surface for it is unwritten even though the code path exists and the delve's own
hard-coded profile exercises it. That is a content gap in a battle-**profile**, owned by
battle-tempo, not a status gap and not this program's.

## 6. Boundaries

- **Never** a second status runtime, bag, tick loop or catalog. A track needing one is a defect.
- **Never** a counter on `StatusInstance`, or `Coexist` siblings presented as stacks.
- **Never** a clock in an out-of-combat track: no wall time, no `ElapsedDays`, no due stamp, no
  scheduler, no `*_utc` column.
- **Never** a second actor compose or a private derived fold — contributions go through the Actor
  Hub, or consume Hub output.
- **Never** a new `StatusKind` or `StatusPayloadKind` to express one of these tracks. The enums are
  closed; a widen is a reviewed change with both count lines moved in the same commit.
- **Never** "only in battle" / "only on the lawn" as a reason for a status mechanism to exist.
- **Ask first** a seventh `ResourceIds` entry, a `burden`-polarity resource, a new status category,
  and any revival of a removed need.