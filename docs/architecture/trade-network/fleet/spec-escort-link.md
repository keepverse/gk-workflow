# Spec: `escort-link`

**Status: written against shipped code 2026-09-19** (HEAD `b82a4098`); **reconciled with the round-4
owner decisions 2026-09-19** ([decisions-round-4.md](../decisions-round-4.md) P: escort strength comes from
the power roll-up — §3 below). Every `file:line` below was opened in this session. Module id `escort-link`, row 5 of the [fleet map](../fleet-map.md) (wave 3; depends on
`trade-route-order`, `legion-build` `escort-stance`, `logistics-flow` `lane-loss`). Ideal:
[trade-network-ideal.md](../../trade-network-ideal.md) §8.3 (*"an escort is a legion in the `escort`
stance. No special case"*), §14b (the throttle forecast's *escort* answer);
[legion-build-ideal.md](../../legion-build-ideal.md) §6.4, §6.5. House style:
[spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Objective

Make `legion-build`'s `escort` stance work for a caravan without a caravan branch. `escort-stance` owns
the stance, the following and the escort's presence in its charge's battles
(`legion-build-map.md` §5.9). This module owns only what a **caravan** adds to that contract and the two
trade-side hooks:

1. **The hold contract.** A caravan does not march every turn — it stands at a site while loading,
   unloading or idle. An escort of a caravan must stand with it on those turns and move with it on the
   others.
2. **The forecast answer.** `trade-surface`'s throttle forecast offers *escort* as a one-click answer; the
   command it files is `legion-build`'s escort command targeting the caravan — built here as a pure
   function, never a second command kind.
3. **The lane-loss row — read, not published** (corrected 2026-09-19, C21). `logistics-flow` `lane-loss`
   weights own legions posted on a lane by a stance-weight table and rejects a stance with no row. That
   module **owns the key family** and states that the `escort` row is published in the change that adds
   the stance (`legion-build` `escort-stance`), and that `escort-link` *"reads it and publishes nothing"*
   (`logistics-flow/spec-lane-loss.md` Tunables). This module's first draft also claimed to publish it —
   a double claim on one key, withdrawn here.

Success looks like: an escort assigned to a caravan ends every turn of a full loop where the caravan
ends, or the report says why; the forecast's escort answer is an ordinary escort order; posting the
escort never raises lane loss.

## Locked anchors

- **One legion architecture, no caravan branch** (owner ruling L3). Every behaviour below is asserted
  through `escort-stance`'s general rule, applied to a charge that happens to be a caravan.
- **Stances are loop behaviour; a stance's combat effect is an atom** (legion-build ideal §6.4). Nothing
  here changes combat.
- **The escort answer is `legion-build`'s command.** The target field already exists
  (`gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:192-194`, `TargetEntityId`).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Stances are a closed list of four; `escort` is not one | `gk-core/src/FusionRpg.Core/World/Movement/LaneCost.cs:10-25` |
| Stance budgets come from one function | `gk-core/src/FusionRpg.Core/World/Movement/LaneCost.cs:50-60` |
| A lane meeting builds one `Lane` request between the two crossing entities; a sector contact one `Sector` request | `gk-core/src/FusionRpg.Core/World/Movement/MovementPhase.cs:145-156,276-286` |
| **A battle request names exactly one attacker and at most one defender**, and the combatant list handed to the resolver is exactly those two | `gk-core/src/FusionRpg.Core/World/Turn/BattleSeam.cs:39-55`; `gk-core/src/FusionRpg.Core/World/Turn/BattleReporting.cs:40-56` |

### Correction to the map

The map's first draft listed as **Built**: *"battle requests gather every entity at the contact
location"*. They do not — the request is pairwise and `BattleReporting.Fight` builds the combatant list
from the two named ids only (`BattleReporting.cs:44-54`). An escort's presence in its charge's battle is
therefore a **real gap**, owned by `legion-build` (`escort-stance` names it; the multi-entity side needs
the request and the resolver input widened, which is `field-battle-kinds`' seam). Recorded in the map as
C10 and filed as ask A8.

### Real gap (this module closes it)

The hold contract's acceptance over a caravan loop and the forecast answer builder. (The `escort`
lane-loss row is `lane-loss`'s, C21.)

## Design

### 1. The hold contract

`escort-stance`'s emitter decides the escort's command from its charge's command for the same turn. The
contract this module requires of it (map ask A3), and tests over a caravan loop:

| Charge's emitted command this turn | Escort's emitted command |
|---|---|
| `move` with path *P* | `move` along *P* from the escort's own position (resumed mid-lane by `MarchResolver`) |
| none (charge loading, unloading, idle, or stalled) | none, if the escort already stands with the charge; else `move` to the charge's sector |
| charge routed (its command dropped at Reveal) | the escort's own command is not dropped — it is not routed — and it follows the rule above next turn |

Nothing in this table knows the charge is a caravan: "the charge emitted nothing" is the general case.
The escort is **not re-bound** when a caravan's loop restarts — the escort names the charge's entity id,
which a loop never changes (the map's "re-bound on restart" line is dropped, C11).

### 2. The forecast answer

```
EscortAnswer.For(world, caravanId, escortCandidateId) -> WorldCommand
  = legion-build's escort-set command { EntityId = candidate, TargetEntityId = caravanId, Stance = "escort" }
```

A pure builder over committed state. It files nothing itself: `trade-surface` shows it and the player's
click submits it through the ordinary submit path. Candidates are the faction's own legions not already
escorting or on a trade route; the forecast ranks them (a `trade-surface` concern).

### 3. The `escort` lane-loss row (owned by `lane-loss`; stated here for the caravan's sake)

`lane.stanceEscortMilli.escort` is `lane-loss`'s row, published with `legion-build` `escort-stance`'s change.
This module reads its effect and adds nothing to the file. `logistics-flow` OD1's v1 rule (presence by
stance, no strength read) applies.

**Round 4 (P) decides the later form.** Escort strength in lane loss is the **power roll-up** — a legion's
power is the sum of its stacks' ActorHub power (unit power × count) plus attached uniques, summing Hub
output only, never a second composer (`decisions-round-4.md` P; the leaf is
`gk-core/src/FusionRpg.Core/Stats/Derived/CombatPowerMembership.cs`). It **replaces** the v1 stance count once the
roll-up and its contest row in `docs/architecture/power/ssot-power-scale.md` §10 land; until then the v1
count stands. **Round 5 X7:** the roll-up is `legion-build` `legion-power`'s (`LegionPower.Of`,
[../../legion-build/spec-legion-power.md](../../legion-build/spec-legion-power.md)); `lane-loss` cites it. The read lives in `logistics-flow` `lane-loss`, not here. The
`escort` stance row (which still decides *who* counts as posted) is `lane-loss`'s key, published with
`escort-stance` (C21); this module publishes nothing and adds no strength read of its own. *(Audit
2026-09-20: this sentence said "this module keeps publishing the `escort` stance row", contradicting §3's
heading and the Tunables section.)*

**Round 6 C1 and D2, both in one line each.** The switch from the v1 count to the roll-up is **its own
wave**, `trade.laneLossPower`, with its own `RulesetVersion` bump — `logistics-flow` wave 5, row 23 of
[../landing-order.md](../landing-order.md) §2 — so a stamped world never changes its loss rule mid-life;
this module (fleet wave 3, `trade.fleetEscort`, row 14) does not gate on it and does not wait for it. And the
lane's own resistance term is `world.hazard.resist`, one of round 6 D2's six world channels, read as **Hub
output rolled up per legion the way `legion-power` is** with a **stated default of 0 until `world-derived`
ships** (`../logistics-flow/spec-lane-loss.md` §4a). This module reads neither number: it decides only
*which* legion is posted as an escort.

Note what the row does and does not do. Lane loss applies to **lane flow** (`logistics-flow-map.md`
module 6), not to a caravan's carried goods (`spec-trade-route-order.md` §7). An escort therefore
protects a caravan in battle and protects lane flow on its lane by presence — two effects of one stance.

## Tunables

None. `lane.stanceEscortMilli.escort` is `lane-loss`'s key (published with `escort-stance`); this module
owns no tuning key (C21).

## Numeric types

The row is `int` per-mille, a bounded ratio feeding a clamp `lane-loss` owns.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <active-session-id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World.Logistics.Fleet|FullyQualifiedName~StanceTests"
```

## Structure

```
src/FusionRpg.Core/World/Logistics/Fleet/EscortLink.cs     (new) — EscortAnswer.For; loop fixtures' shared helpers
tests/FusionRpg.Core.Tests/World/Logistics/Fleet/EscortLinkTests.cs (new)
```

## Testing strategy

- **Co-location over a loop:** a caravan on a fixture route through load, march, unload, march; an escort
  assigned before the first march ends every turn on the caravan's lane or sector; when its own budget
  cannot keep up, the turn report carries the reason `escort-stance` defines for it (this test asserts
  an entry exists; the token is `legion-build`'s).
- **Battle presence — gated:** at every contact the caravan meets, the escort is in the battle's combatant
  set (asserted on the request/combatants, never the winner). Marked skipped with the reason
  *"awaits legion-build multi-entity sides (map A8)"* until that lands; the skip is the visible gap.
- **Lane loss monotone:** with the escort posted on the lane, loss ≤ loss without it, over a property sweep
  (through `lane-loss`'s monotonicity).
- **Order-independent:** escort assigned before vs after the caravan's trade-route order is set gives the
  same first escorted turn (both orders tested — the key-set edge is the caravan acquiring its order).
- **Forecast answer:** the builder's command is admitted by the ordinary admission and equals a
  hand-built escort order field for field.
- *(The "row present" load test is `lane-loss`'s, run in `escort-stance`'s change — not duplicated here.)*

## Boundaries

- **Always:** go through `escort-stance`'s rule; file escort answers as `legion-build`'s command.
- **Ask first:** any caravan-specific escort behaviour.
- **Never (round 4 P):** an escort strength read other than the power roll-up, and never in this module —
  `lane-loss` reads it.
- **Never:** a caravan branch in movement or contact; a second escort command; lane loss on carried goods.

## Success criteria (contract)

1. Over a full loop the escort ends each turn with the caravan, or the report says why.
2. At every contact the caravan meets, the escort is in the same battle (once legion-build's
   multi-entity sides land; skipped and visible until then).
3. Lane loss with the escort posted never exceeds loss without it.
4. Escort assignment order does not change the first escorted turn.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `EscortAnswer.For` | `trade-surface` `throttle-forecast` (its gap row "needs `fleet` first" — map A7) |

| Escorted-caravan facts (via `escort-stance`) | `trade-stories` `trade-quests` (`escort` template) |

## Dependencies

`trade-route-order`; `legion-build` `escort-stance` (and, for battle presence, its multi-entity side —
ask A8); `logistics-flow` `lane-loss`.

## Hard edges

- None of its own. The ordering hazard the first draft named (a stance with no row fails every boot) is
  closed by `lane-loss`'s rule: the row lands in the same change that adds `escort` to
  `MovementPolicy.Stances` (`legion-build` `escort-stance`).

## DESIGN-GATE §5 checklist

```
[x] Subsystems: stances (legion-build), movement and contact, battle seam (read only), lane loss, tunables.
[~] Session boundary: trade-network-idea-20260919 covers this path; check script not run by me.
[x] Read this session: as spec-carried-goods.md; battle-engine-ssot.md §1, §5; legion-build-map §5.9, §5.16.
[x] decisions.md: Battle engine is the SSOT (this module adds no mechanism).
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope: no HIGH finding.
[x] Verified against code: the pairwise request and combatant list (the map's Built claim was wrong).
[x] Surrounding sections read: BattleReporting.Fight in full; MovementPhase crossing and contact blocks.
[~] Constraints tested: none claimed.
[x] No §2 invariant contradicted; battle-engine §5 answered: no mechanism, loop only (who stands where).
[x] Corrections propagated: C10, C11, C21 in fleet-map.md.
[x] No population pinned.
[x] No event-refreshed cache.
[x] Orderings: escort-then-order and order-then-escort both tested.
[x] No actor magnitude (presence, not strength). The round-4 strength form is the P roll-up over Hub
    output, read by lane-loss — never composed here.
[x] No SOLID fork: one escort command, one stance rule, one loss table, one owner per tuning key.
[x] Registry rows: none new.
```

## Audit 2026-09-20

Fixed here: §3 claimed this module "keeps publishing" the `escort` lane-loss row, contradicting C21 and its
own Tunables section; `lane-loss` owns and publishes it. Checked and clean: no battle mechanism (battle
presence is `legion-build`'s multi-entity side, ask A8, skipped visibly until it lands); no actor magnitude
(strength is `legion-build` `legion-power`'s roll-up of Hub output, read by `lane-loss`); both assignment
orders tested. **Verification boundary:** the `core-world-logistics-fleet` owner boundary
(`spec-carried-goods.md` Hard edges).
