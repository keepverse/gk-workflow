# Spec: `lawn-action-base` — the lawn hit reads the action's base

**Program:** [`action-enrich`](../action-enrich-map.md). **Depends on:** [`action-base`](spec-action-base.md).
**Delivers:** the lawn half of the spec `solid-enforcement` SE5.1 names.

## Objective

The lawn already resolves every hit through the basic action: lawn-combat-wire T10 (`62ec0b9ee`) binds
`act.attack`'s `fx.overlay_damage` grant per actor at spawn (`BasicAttackGrantBuilder.cs:49-80`, called
from `LawnBasicAttackGrantBinder.cs:164`) with a hybrid element payload from the owner's species element.
The one number that still comes from the host is the magnitude: the def (`gk-data/packs/fusion/data/seed/atoms/fx-core.json:33`)
reads `"amount": {"eventField":"damage","multiplierMilli":-1000}` (`fx-core.json:40`), resolved at hit
time from the event's amount (`DamagePacketBuilder.cs:63-96`).

After this module the grant carries the action's base as a plain `amount`, so the same action at the same
`Θ` deals the same base on the lawn and in battle. PvZ supplies only the trigger.

## Design

```
amount = -ActionBaseMath.BasePerHit(ActionBaseDerivation.BasePowerMilli(Basic, ...), P(Θ_owner))   (negative = damage)
```

- **Where:** `BasicAttackGrantBuilder.Build` gains a `long amount` parameter and writes it into the grant
  overlay. `resource.delta` already allows an `amount` overlay (`EffectProcAndOwner.cs:247`), and
  `EffectBag` merges grant overlay over def params (`EffectBag.cs:487`). A plain number resolves through
  `DamagePacketBuilder.ResolveAmount`'s plain branch (`DamagePacketBuilder.cs:95`). **No change to the
  def or to generated atoms.** The lawn's action is always the basic attack (rung 0), so no rung table is
  read on the lawn.
- **`Θ_owner` — the same value the Hub carries, read once per bind, never per hit.** The binder reads
  `CheatState.PowerIndex.ActorIndex(ctx)` with `ctx.PlayerId = CheatState.CurrentPlayerId` — the key
  both hydration and every lawn resolve use (`CheatState.cs:258-272`; the provider keys by player only,
  `IPowerIndexProvider.cs:76`, so both lawn sides read the commander's `Θ`, as `lawn-tuning-profile`
  decided 2026-09-16). This is the provider `RpgProgressionSubsystem` writes into `progression.power`
  verbatim with a `Replace` op and no other contributor (`RpgProgressionSubsystem.cs:44-48`), so it is
  the Hub's value, not a private fold — and a parity test (below) fails the day a second contributor
  joins that channel. `P(Θ)` through the same `PowerLadder` (`PowerTuningHub.Tuning`).
- **Host configuration.** `RpgHost.Initialize` configures `ActionBaseTuningHub` from the same
  `action-base.v{n}.json` `Program.cs` loads, beside its existing `RungPolicy.Configure`
  (`RpgHost.cs:225-227`). Missing it is the exact "Server does this, the injector's own copy was missed"
  defect that silently zeroed lawn swing charging on 2026-09-14 (the comment at `RpgHost.cs:214-224`).
  Both hosts name one version — asserted by `action-skill-tiers` ST5's tuning-version agreement guard,
  which is written parameterised by domain and carries an `action-base` row (ST5 contract 3).

### Instakill refusal — one owner: the overlay filter grammar

A lawnmower or board-wipe hit (`EffectEventDto.InstakillShaped`, `EffectDtos.cs:229-234`, set by
`EventDrain.cs:634`) must not ride the basic-attack rider. Today the event-field branch refuses it
(`DamagePacketBuilder.cs:77-78`); with a plain amount that branch is never entered, so the guard is gone.

The refusal moves to the grant, through the grammar that already decides whether a grant fires for an
event: `EffectProcAndOwner.PassesOverlayFilters` (`EffectProcAndOwner.cs:146-180`, keys `side`, `typeId`,
`actorIsKiller`). It gains **one** filter key, `excludeInstakill` (bool): when true and
`ev.InstakillShaped`, the grant does not fire. `BasicAttackGrantBuilder.Build` writes
`filters: { excludeInstakill: true }`. Rejected alternatives: a check in the binder (the binder runs at
spawn, not per event — it cannot see the hit); a check in `DamagePacketBuilder`'s plain branch for every
plain amount (would silently change every other plain-amount rider's lawnmower behaviour); keying on the
grant id prefix (a special case outside the grammar). The existing event-field refusal stays for the
proportional riders it was written for.

### Refresh triggers (DESIGN-GATE §2 invariant 16 — every edge that changes the baked amount)

The baked amount depends on three inputs: the owner's `Θ`, `basicAttack.basePowerMilli`, and the set of
live bound ptrs (the key set). Every edge:

| Trigger | Input it moves | Code today | Action |
|---|---|---|---|
| Actor spawn (key-set entry) | a new ptr enters the bound set | `QueueSpawn` from `MatchHost.cs:152` / `InjectorEntityRegistry.cs:76,97`, drained by `Tick` (`LawnBasicAttackGrantBinder.cs:78-113`) | build with the current `Θ` at drain |
| Session start | `Θ` hydrated | `RpgClient.StartAsync` → `RefreshPowerIndexAsync` (`RpgClient.cs:81`) → `ApplyPowerSnapshot` | mark dirty; rebind at next drain |
| SignalR reconnect | `Θ` re-hydrated | `RpgClient.cs:163` → same path | same |
| `power.index.reload` overlay command | `Θ` re-hydrated on demand | `CheatCommandRunner.cs:101-105` → same path | same |
| Player identity change | `CurrentPlayerId`, hence the ctx key | set by the same `ApplyPowerSnapshot` call (`CheatState.cs:252-257`) | same (one hook covers it) |
| Basic attack switched **off** mid-match | key set emptied | `SwitchEdge.TurnedOff` → `WithdrawAllBound` (`LawnBasicAttackGrantBinder.cs:92-93`, `b3a1ec02`) | none — no grant, no amount |
| Tuning change of `action-base` | base | tuning is loaded once in `RpgHost.Initialize`; there is no hot reload in the injector | none in-process; a new version needs a host restart, whose spawns are the first row |

**Record-then-drain (invariant 2).** `ApplyPowerSnapshot` runs on an async continuation, not the Unity
main thread. It therefore only **records**: one call, `LawnBasicAttackGrantBinder.MarkThetaDirty()`
(lock-protected flag, O(1)). The next main-thread `Tick` drains it by rebuilding every live grant the
builder owns (enumerated exactly as `WithdrawAllBound` does, by `IsBasicAttackGrantId`,
`LawnBasicAttackGrantBinder.cs:63-75`), re-running `Bind(ptr)` for each — the deterministic `GrantId`
(`BasicAttackGrantBuilder.cs:45-47,84`) makes it an idempotent upsert. `CheatState` depends on the binder
only through that one method; the binder never reaches into `CheatState` beyond reading `Θ`.

**Order-independent:** bind-then-snapshot, snapshot-then-bind, and snapshot-between-queue-and-drain must
yield the same amount; all three are tested.

**Pre-existing gap, named not fixed here.** Switching the basic attack **on** mid-match binds nothing
for actors already on the board: `Tick` only withdraws on the off edge, and a spawn that arrived while
the switch was off was drained and discarded (`LawnBasicAttackGrantBinder.cs:103-106`). That is a missing
key-set entry edge of `lawn-combat-wire`'s binder, independent of the amount; it is reported to that
program, not built here.

**Future key edge (R3, named).** `spec-rulings-2026-09-18.md` R3 gives Zomboss its own empire under a
save identity. When `save-identity` lands, the zombie side's `Θ` source changes; the rebind path above
reads whatever ctx→`Θ` mapping is current, so that change needs one more row here (the edge where the
zombie side's owner is hydrated), written with `save-identity`'s build.

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~BasicAttackGrant|FullyQualifiedName~OverlayFilterInstakill"
dotnet test tests\FusionRpg.Injector.Tests --filter "FullyQualifiedName~LawnBasicAttackGrantBinder"   # new tests; needs interop refs; not in CI
.\scripts\verify-change.ps1 -Paths <every changed file> -Session <session-id>
python scripts\deploy-play.py --no-server --paths <every changed file>
python gk-fusion/scripts/guard-single-writer.py; python gk-fusion/scripts/guard-funnel-delta.py; python gk-core/scripts/guard-secondary-no-unity.py
```

## Project structure

```
gk-core/src/FusionRpg.Core/Combat/BasicAttackGrantBuilder.cs          + amount parameter, + filters.excludeInstakill
gk-core/src/FusionRpg.Core/Effects/EffectProcAndOwner.cs              PassesOverlayFilters: + excludeInstakill
gk-fusion/src/FusionRpg.Injector/Effects/LawnBasicAttackGrantBinder.cs  compute amount at bind; MarkThetaDirty + drain rebind
gk-fusion/src/FusionRpg.Injector/CheatState.cs                          ApplyPowerSnapshot calls MarkThetaDirty (records only)
gk-fusion/src/FusionRpg.Injector/Host/RpgHost.cs                        ActionBaseTuningHub.Configure
gk-core/tests/FusionRpg.Core.Tests/Combat/BasicAttackGrantBuilderTests.cs   (extend)
gk-core/tests/FusionRpg.Core.Effects.Tests/Effects/OverlayFilterInstakillTests.cs    (new)
gk-fusion/tests/FusionRpg.Injector.Tests/…LawnBasicAttackGrantBinderRefreshTests.cs (new)
```

## Code style

Pure builder in Core, Unity-free (the class's existing rule, `BasicAttackGrantBuilder.cs:19-20`); the
injector only resolves `Θ` and calls it. Long math through `ActionBaseMath.BasePerHit`, never re-derived.

## Testing strategy

| Case | Expect |
|---|---|
| Built grant | overlay `amount` equals `-BasePerHit(base, P(Θ))` for the given `Θ`; `elementPayload` and `icd_ms` unchanged; `filters.excludeInstakill` true |
| Parity with battle | same action, same `Θ`: lawn rider base == battle `BaseOverlayDamage` before defense (shared `ActionBaseMath` and `ActionBaseDerivation`) |
| `Θ` parity with the Hub | for a hydrated player, the binder's `Θ` == `CheatState.ActorHub.ResolveDerived(ctx).Get(progression.power)`; **planted violation:** a second contributor to `progression.power` in a fixture hub fails it |
| Each refresh trigger | one test per row of the trigger table: spawn binds; each of session start / reconnect / reload / identity change marks dirty and the next drain rebinds every live grant to the new `Θ`; off-switch leaves nothing to rebind |
| Record-then-drain | `MarkThetaDirty` performs no grant call; the rebind happens only inside `Tick` |
| Order independence | bind→snapshot, snapshot→bind and snapshot-between-queue-and-drain agree |
| Idempotent rebind | two dirty drains in a row leave exactly one grant per ptr with the same amount |
| Instakill event | the grant does not fire on an `InstakillShaped` event; the same grant fires on an ordinary hit; an unrelated plain-amount grant without the filter is unchanged on an instakill event |
| Neutral owner (no element) | amount applies, no `elementPayload` (existing degenerate case) |
| Unconfigured `ActionBaseTuningHub` in the injector | bind throws naming the file (caught and reported by `TryBindOrRequeue`'s existing error path, never a silent zero) |

**Live probe** (per `docs/contributing/live-probe-standard.md`, RPG Server scope for `Θ`): read the
commander's `Θ` from the RPG Server's normal query path, then compare a real lawn hit's delta in real
injector telemetry against `BasePerHit(base, P(Θ))` before defense. Then change `Θ` through the real
progression path and confirm, without respawning, that the next hit follows. A debug-bound grant proves
nothing.

## Boundaries

- **Always:** refresh on every trigger listed; record on the snapshot edge and rebind in the drain;
  share `ActionBaseMath`/`ActionBaseDerivation` with battle.
- **Ask first:** changing the `fx.overlay_damage` def itself.
- **Never:** read PvZ's current state for the amount; write a Unity attack field; a per-mode base; a
  server round-trip on the hit path; grant calls off the main thread.

## Success criteria

Checkpoint 2 of the map: lawn rider base equals the battle base for the same action and `Θ`; every
trigger tested; instakill refused through the filter grammar; guards green; live probe per the standard.

## Open questions

None.
