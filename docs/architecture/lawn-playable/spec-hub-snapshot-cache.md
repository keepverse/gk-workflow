# Spec: `hub-snapshot-cache` (lawn-playable module 2)

**Program:** [lawn-playable](../lawn-playable-map.md) · **Depends on:** `actor-liveness-refresh` ·
**Unblocks:** `rider-hit-cost`, `rider-default-on`
**Status:** spec, 2026-09-16. Not built.

## Objective

Stop recomposing an actor's 261 derived channels on every hit.

`ActorHub.ResolveDerived` says so in its own doc comment — *"L2b Apply-scoped derived compose — **fresh
per call in v1**"* (`ActorHub.cs:52`) — and the lawn's rider path calls it per hit through
`LawnBasicAttackCostCharger.DerivedFor(ptr)` and `InjectorCombatBridge`. Measured at 300 zombies, one
~4 s window:

```
hub.resolveDerived   count 286   totalMs 464.5   maxMs 15.3   avgUs 1624.2
```

1.6 ms per compose, on the Unity main thread, inside a frame that is already 65 ms. This is the single
largest lever in the 26.7% → target budget, and it is the one that requires no design change to what the
RPG *does* — the same compose, run once per change instead of once per hit.

## Tech stack

`FusionRpg.Core` (`ActorHub`), `FusionRpg.Injector` (`InjectorStatusBridge`, `CheatState`). No new
dependency. The cache lives beside the Hub, never inside a mode.

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ActorHub|SnapshotCache"
python gk-core/scripts/guard-actor-hub.py
.\scripts\verify-change.ps1 -Paths <changed files> -Session <session id>
# the measurement that decides the module:
python gk-core/scripts/probe_perf.py --scenario lcw-300z-env-on-cache --duration-sec 60
```

## Project structure

| What | Where |
|---|---|
| The cache | `src/FusionRpg.Core/Stats/Derived/ActorSnapshotCache.cs` (new) |
| Wiring | `ActorHub.ResolveDerived` consults it; `InjectorStatusBridge` passes the revision |
| Tests | `tests/FusionRpg.Core.Tests/Stats/ActorSnapshotCacheTests.cs` |
| Baseline | `docs/research/perf/_baseline-lcw-300z-env-on-cache.json` |

## The shape

1. **Key: `(actorKey, ActorLivenessRevision)`** from module 1. A hit on an unchanged actor is a
   dictionary lookup; a changed actor recomposes once and replaces its entry.
2. **The cache is a cache, never a second source of truth.** A miss composes through the identical path
   the uncached call uses — same subsystems, same order, same `DerivedComposer`. There is exactly one
   compose in this codebase and this module does not add a second (`guard-actor-hub.py`).
3. **Bounded and scoped to the session.** Entries are dropped when the entity dies and when the match
   ends; the bound is structural (board size), stated in a comment as the no-ceilings rule requires.
4. **Off is identical to on.** A kill switch (`FUSIONRPG_HUB_CACHE=0`) composes fresh every call, so a
   suspected staleness bug is one env var away from being ruled out — the same posture the rider's own
   switch uses.
5. **Status cannot simply be left out — correcting this spec's own first draft.** The injector's Hub
   registers `statusDerivedMods: StatusDerivedMods.For` (`CheatState.cs:74`) as a real
   `IActorStatSubsystem`, which is what makes a status's `stat.combat.*` write reach the composed value
   at all (mechanism-wiring G1). Dropping it from the cached fold would silently delete every status
   contribution from every cached read — a combat correctness bug strictly worse than the cost this
   module exists to remove. Two admissible shapes, and the module must pick one **with a measurement**,
   not by preference:
   - **(a) Split fold.** Cache the durable part (progression, aptitude, atoms, tree, resource baseline)
     and add the status contribution live on top of the cached base. Correct by construction; the saving
     is whatever the durable part costs, which is most of it.
   - **(b) Status revision.** Give status its own monotonic counter, bumped by `StatusRuntime` on apply
     and withdraw, and include it in the key. One cache, but the key moves on every DoT tick, so on a
     busy board it may degenerate to no cache at all.
   Default until measured: **(a)**, because its worst case is "saves less" while (b)'s worst case is
   "saves nothing and is more code".

6. **The aptitude lookup is already memoised, so it is not where the 1.6 ms goes.**
   `AptitudeSubsystem` carries a memo keyed by `(Side, TypeId, Θ)` with allocation reference equality
   and its own doc says the resolve it guards is ~25,000 lookups. The remaining cost is the fold itself
   — 261 channels through `DerivedComposer` — which is exactly what this module caches. A module that
   re-optimises the allocation lookup is optimising the part that is already done.

## Testing strategy

- ✅ Cached and uncached composes are **equal channel for channel** for the same revision — the
  identity property, asserted over the whole snapshot, not a sampled channel.
- ✅ A revision bump produces a different snapshot when an input changed, and an identical one when
  nothing did.
- ✅ Death and match end evict; a re-used pointer never reads the previous entity's snapshot (address
  reuse is real here — `lawn-combat-wire` L-N27 measured 46 zombie and 55 plant reused addresses in one
  run).
- ✅ With the kill switch off, behaviour is byte-identical to today.
- ❌ Never assert a hit count, a hit rate, or a µs figure in a test. The µs number is the module's
  acceptance, measured by `gk-core/scripts/probe_perf.py`, never pinned by a unit test.

**Mutants to kill:** never evict on death; ignore the revision in the key; cache the status
contribution. Each must fail a test.

## Boundaries

- **Always:** identical output to the uncached path; evict on death and match end; keep the switch.
- **Ask first:** nothing.
- **Never:** cache across a match boundary; cache by pointer alone (address reuse); let a cache miss
  take a different code path from a cache-disabled compose — that is how two behaviours appear under one
  name.

## Numeric types

No magnitude introduced. The revision is `long` (module 1).

## ActorHub gate

**Contributes nothing, composes nothing new.** This is memoisation of the existing single compose, and
`guard-actor-hub.py` must stay green precisely because no second composer appears.

## Success criteria

1. `hub.resolveDerived` `avgUs` at 300z drops by at least an order of magnitude against
   `_baseline-lcw-300z-env-on-post-ln37.json`'s 1624.2 µs, measured on the same scenario.
2. Cached and uncached snapshots are proven equal in test, not sampled.
3. `guard-actor-hub.py` green; no new `*Composer*`.
4. A live A/B on one board shows identical `attack`/`maxHp` readings with the cache on and off.

## Open questions

None for the owner. The (a)/(b) choice above is settled by a measurement this module takes in its first
step, with (a) as the stated default if the measurement is inconclusive.
