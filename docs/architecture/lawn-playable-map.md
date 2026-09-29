# Capability map: `lawn-playable`

**Plan:** [tasks/lawn-plan.md](../../tasks/lawn-plan.md) · **Tasks:** [tasks/lawn-todo.md](../../tasks/lawn-todo.md)
(one plan over `lawn-playable` + `lawn-tuning-profile`, written 2026-09-20 by `backlog-clean-up`
`orphan-plan-authoring` BCU2.4 — the per-module plan/todo pair this line originally promised was
never written and is superseded by the shared `lawn` plan above).
**Status:** capability map proposed 2026-09-16, from measured live evidence gathered the same day.
**Owner framing (2026-09-16):** *"this program is fundamental, wire our rpg to pvz and make it playable
before we ship new feature so at least the combat loop and soul earn need to wire."*

---

## What this program is for

The RPG layer is **built** on the lawn, and — corrected 2026-09-20 (`backlog-clean-up`
`lawn-signal-ownership`, `program-pipeline-audit-2026-09-20.md` revision 3) — **on by default**. Every
piece exists — riders, elements, stamina, Hub-composed stats, equip bindings, soul earn — and
`lawn-combat-wire` proved each one live. This map originally read the loop as shipping behind a kill
switch, **defaulted off** (`LawnBasicAttackFeature.DefaultEnabled = false`), because at 300 zombies it
took **26.7–27.2%** of the pipeline against a 6% ceiling, and about **37%** after the L-N36
rider-cooldown fix (`docs/research/perf/_baseline-lcw-300z-env-*.json`; fps 17.8 on vs 31.1–38.6 off).
**That is stale.** `LawnBasicAttackFeature.cs:56` has read `DefaultEnabled = true` since `9f985313`
(2026-09-16, owner decision). An owner-directed perf pass (`83054adb`, `5a3e941c`, `b48f0e7e`) then
brought `effect.onCapture` to **3.46% of wall at 59.7 fps**, under the 6% ceiling — so P1's cost defect
below is closed, and `hub-snapshot-cache`/`rider-hit-cost` are superseded by that pass. The **scale**
gate (`lawn-tuning-profile`'s `lawn-scale-live-proof`, M2 stamina) never ran, so `rider-default-on` is
only partly satisfied: cost is proven, scale is not. The build order and the lawn plan (`tasks/lawn-plan.md`,
`backlog-clean-up` `orphan-plan-authoring`) carry the up-to-date module list; this section keeps the
history because the "why it shipped off, then on" reasoning still matters.

So today a player who installs this mod gets the RPG combat loop live on the lawn, cost-affordable but
not yet scale-proven. The remaining gap is freshness (P3/P4) and the two silent failures (P5/P5a), not
whether the loop runs at all.

**This program makes the remaining gaps closable.** It is not new features. It is: make an actor's live
state actually follow the player's state, and stop the two places where a real player's own actions
silently produce nothing. (Its per-hit cost work is done; see above.)

### What is already wired — do not re-litigate these

| | Evidence |
|---|---|
| Soul earn, end to end | 2026-09-16, fresh player 7: one real Adventure-2 board paid **78 kill souls + 100 victory**, ledger joined 1:1 to `ZombieKilled` facts, `killSoulsByOrigin{Game:78, Debug:0, Cheat:0}` |
| Progression from real play | Same board took Dave level 1 → 5, which fired the level-4 onboarding item grant |
| Hub numbers reach Unity | Bound specimen: Hub `progression.bonus.atk 3115` / `maxHp 3672` vs live `attack 3116` / `maxHp 4672`, control plant at 2939, no revert after a forced reapply |
| Equip binds and pushes | `atoms-preview`: 1 accepted, 0 refused; `effects.grants.apply` lands on the bound ptr |
| Riders, elements, drain attribution | `lawn-combat-wire` proofs 1, 2, 3, 4, 6, 7 — all closed live |

The gap is never "does the mechanism exist". It is **cost, freshness, and two silent failures.**

## The five measured defects this program owns

| # | Defect | Evidence (all 2026-09-16 unless noted) |
|---|---|---|
| P1 | `hub.resolveDerived` composes **fresh per call** (`ActorHub.cs:52` — *"fresh per call in v1"*) and the rider path calls it per hit (`LawnBasicAttackCostCharger.DerivedFor`) — **286 calls, 464 ms, avg 1624 µs** in one 4 s window at 300z | `_baseline-lcw-300z-env-on-post-ln37.json` |
| P2 | `effect.onCapture` **129 calls, 543 ms, avg 4214 µs**; the drain cannot keep up — `carried 5320`, `maxLatencyFrames 47`, observer `droppedRecords 369` in the same window | same file |
| P3 | Θ never moves after the injector connects: player levelled 1 → 5, server read `theta 7`, every injector trace still read `theta 1` (live-probe Task 25) | injector `debug.aptitude-trace` |
| P4 | A player switch never reaches the injector (Task 24); a post-deploy allocation never reaches a Bound entity (Task 23); a mid-session commander allocation did not reach freshly spawned plants at all | live traces, control-plant comparison |
| P5a | Exhaustion is invisible: the lawn's entire consequence is `_exhaustionEvents++`, a process-wide counter with no actor, no resource, no transition — and it counts **refusals**, not edges (`ExhaustionEvents` **591** over `totalHits` **551**, which more events than hits proves). `ExhaustionPolicy` — the status, the debuff payload, the scoped grant id, the anti-spiral validation — exists in Core with **zero lawn callers** | `LawnBasicAttackCostCharger.cs:164`, `_lawn-combat-proof4-exhaustion-clean-player.json`, `ExhaustionPolicy.cs` |
| P5 | A real summon can roll a species this build cannot plant — **3 of 5 clean pulls** (`Synergy_蘑菇岛`, `Synergy_爆破王`, `Synergy_磁力科技`) — and the injector's `CreatePlant.SetPlant` NullReferenceException is never reported back, so the deploy just times out (Task 22) | injector log + probe runs |

P3/P4 are the same missing thing as P1's blocker: **nothing invalidates anything.** That is why the
freshness module comes before the cache module — caching a value that already never refreshes would
freeze the bug permanently instead of exposing it.

## Modules

| Module id | Responsibility | Depends on |
|---|---|---|
| [`actor-liveness-refresh`](lawn-playable/spec-actor-liveness-refresh.md) | One typed invalidation channel server → injector, and one per-actor revision that every cache keys on. Fixes P3 and P4: a player switch, a level-up, an allocation, an equip and a deploy each bump what they actually change, and the injector refreshes exactly that. | — |
| [`hub-snapshot-cache`](lawn-playable/spec-hub-snapshot-cache.md) | Cache the composed `ActorDerivedSnapshot` per actor against that revision, so the per-hit path stops recomposing 261 channels. Fixes P1. | `actor-liveness-refresh` |
| [`rider-hit-cost`](lawn-playable/spec-rider-hit-cost.md) | Bound the per-hit work in `EffectRuntime.OnDrained`/`OnCapture` and make the drain keep up at 300z — the 4.2 ms average and the 5320 carried records. Fixes P2. | `hub-snapshot-cache` |
| [`summon-pool-integrity`](lawn-playable/spec-summon-pool-integrity.md) | A summonable species is one this build can actually plant (generator + corpus guard), and an injector-side spawn failure answers the deploy correlation instead of timing out. Fixes P5. | — |
| [`exhaustion-event`](lawn-playable/spec-exhaustion-event.md) | Exhaustion becomes something that happens to an actor: one edge-triggered `actor.exhausted`/`actor.recovered` per window (not one per refused swing), the already-built `ExhaustionPolicy` status lifecycle wired with an empty payload so VFX/HUD have something real to bind to, and per-actor transition rows for the observer. Fixes P5a. | — |
| [`rider-default-on`](lawn-playable/spec-rider-default-on.md) | Flip the kill switch to on **only** when the same isolated 300z A/B that measured the breach measures under the ceiling. The ceiling becomes a tunable, not a number in a task file. | every module above |

## Signal ownership: `PUT /api/players/current` (recorded 2026-09-20, `backlog-clean-up` `lawn-signal-ownership`)

`actor-liveness-refresh` (module above) owns defect P4, part of which is "a player switch never reaches
the injector." **`SP6.6`** (`summoner-convergence` lane B, `species-progression-todo.md`) is the **one**
generic server → injector notice on `PUT /api/players/current` — the parent convergence plan's own §3
rule ("`SP6.6` builds the one server→injector notice… nothing here adds a second"), which
`solid-enforcement` and `notification-ssot` already reuse rather than duplicate.

`actor-liveness-refresh` **extends `SP6.6`'s notice; it never adds a second `Player`-kind channel.** Its
own closed vocabulary (`Ladder`, `CommanderAllocation`, `UniqueAllocation`, `Equip`, `Tree`, in
`spec-actor-liveness-refresh.md`) rides the same transport `SP6.6` establishes, plus a field `SP6.6`'s
payload reserves for it: `empireId`, so `SE4.31`–`SE4.36` (save-identity's SignalR empireId work) never
has to retrofit the shape once it ships. This is the hard edge E1/E2 in `backlog-clean-up-plan.md`: no
lawn build task starts before this note lands, and no lawn module ever ships its own `Player`-kind
notice.

**Build order**

```
actor-liveness-refresh ──► hub-snapshot-cache ──► rider-hit-cost ──┐
summon-pool-integrity ─────────────────────────────────────────────┤
exhaustion-event ──────────────────────────────────────────────────┼─► rider-default-on
lawn-tuning-profile: … ──► lawn-scale-live-proof ──────────────────┘   (cross-program gate)
```

`summon-pool-integrity` and `exhaustion-event` are independent of the cost chain and of each other, so
all three can run in parallel. `exhaustion-event` is also the instrument `lawn-tuning-profile`'s
`lawn-scale-live-proof` reads proof 5 from, and it pairs with that program's `lawn-resource-scale`,
which is what makes exhaustion reachable at every build rather than only at zero allocation.

## Audit, 2026-09-16 — what the adversarial pass changed

Three corrections, all from reading code the first draft had asserted about rather than opened:

1. **`hub-snapshot-cache` proposed a correctness bug.** Its first draft excluded the status subsystem
   from the cached fold. The injector's Hub registers `statusDerivedMods` as a real
   `IActorStatSubsystem` (`CheatState.cs:74`) — that registration is what makes a status's
   `stat.combat.*` write reach the composed value at all — so excluding it would silently delete every
   status contribution from every cached read. Replaced with two admissible shapes and a default.
2. **`actor-liveness-refresh` filed a design decision as a bug.**
   `MatchCommanderSnapshotHolder.ResolveAllocation` is documented as *"frozen snapshot during a match,
   live cache outside"*. A commander allocation genuinely does not apply mid-match, on purpose. The
   module's real work there is to make the freeze **legible** instead of indistinguishable from a
   failure; live-probe Task 23's note is corrected in place.
3. **`rider-default-on` gated on the wrong half.** It depended only on the cost chain, which would have
   allowed the switch to default on while a pea still hits for 2,939. It now also gates on
   `lawn-tuning-profile`'s `lawn-scale-live-proof`: affordable is not sufficient, the lawn has to be a
   game too.

A fourth, smaller one: the aptitude lookup is already memoised (`AptitudeSubsystem`, keyed
`(Side, TypeId, Θ)`), so the 1,624 µs is the 261-channel fold itself — a module that re-optimises the
allocation lookup would be optimising the part that is already done.

## Proof 5 / L-N2 is not in this program

`lawn-combat-wire` proof 5 — *"an exhausted actor's own Hub-composed `attackDamage`/`maxHp` stay intact
while exhausted"* — cannot be observed while **any** aptitude allocation makes the stamina pool
unemptiable (`ExhaustionEvents` 0 with three points; 591 with none). That is a scale defect, and it is
owned by [`lawn-tuning-profile`](lawn-tuning-profile-map.md), which now carries the specs for the chain
that unblocks it:

```
mode-profile ──► base-relative-read ──┐
                                      ├─► lawn-scale-live-proof   (proof 5 / L-N2 lands here)
regen-unit-trace ──► lawn-resource-scale ──► basic-attack-cost-scale ─┘
```

This program and that one are independent: a cheaper rider does not change the scale, and a fixed scale
does not change the cost. Both must land before the switch defaults on for a real player — one so the
lawn is affordable, the other so it is a game rather than an all-or-nothing gate.

## What this program does not own

- **New features.** The owner's own framing: nothing new ships until the loop is playable.
- **Balance numbers.** Every number this program touches is a cost or a budget; the game's feel is
  `lawn-tuning-profile`'s.
- **VFX.** Already built and tested (owner ruling 2026-09-16) — this program wires, never rebuilds.
  `exhaustion-event` is the clearest case: it ships the status lifecycle a VFX or HUD cue can bind to,
  and authors no cue itself.
- **The exhaustion debuff's payload.** `exhaustion-event` ships the status with an empty stat-mod list
  on purpose; which channels an exhausted actor loses, and by how much, is authored balance and belongs
  to `lawn-tuning-profile`.
- **The species corpus's content.** `summon-pool-integrity` fixes the *flag* through the generator that
  emits it; it authors no species.

## Open questions

None. Every module's acceptance is a measurement that already has a baseline to compare against.
