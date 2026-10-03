# Capability map: status tracks

Source: [status-tracks-ideal.md](status-tracks-ideal.md). **Status: proposed, pending owner
approval.** The locked rules are already in place — [decisions/combat.md](decisions/combat.md) row
*Status tracks — combat and out-of-combat* — and this program implements and extends them; it does
not relitigate them.

## What this program is

Not a new engine. It is the **authoring surface and the drive** for two tracks that today share a
runtime and share nothing else: combat statuses that pulse on the battle clock, and out-of-combat
statuses that project a counter held in durable state.

## What this program is not

- **Not a second status system.** `StatusRuntime` is the single mechanism, per
  [battle-engine-ssot.md](battle-engine-ssot.md) ("a mode may own its loop, never a mechanism").
- **Not the `buff-debuff-scope` program.** That one answers *which population an effect reaches*
  (WHERE × WHO). This one answers *what state an actor is in*. They are adjacent and neither
  subsumes the other; `buff-debuff-scope-map.md` is proposed and still pending approval.
- **Not the shield program.** `ShieldRuntime` is deliberately a separate subsystem
  ([decisions/combat.md](decisions/combat.md) *Shield layer*), and a shield is not a status.
- **Not a new resource.** A seventh `ResourceIds` pool is an owner ADR, not this program's call
  (see `K1` in the plan's decision packet).

## Modules

| Module id | Responsibility | Depends on |
|---|---|---|
| `track-contract` | **Nothing to build — the contract this program conforms to.** Pins the two tracks' shapes in tests: a combat status pulses on the battle clock; a projection writes on transition only, attacker-less, `BaseDuration 0`, and is idempotent. Asserts the negative rules the ideal locks (no counter field on `StatusInstance`, no second `Tick` owner outside the two known call sites). This is the module that makes a later regression a red test rather than a review comment | — |
| `combat-track-authoring` | The **catalog-row + grant-overlay** path, end to end, for combat statuses: the three registration points that must agree (`StatusCategoryRegistry`, `StatusCatalogBootstrap`, `status-catalog.v{n}.json`), the overlay keys `StatusEffectBridge.BuildApplyInput` actually reads, and the parity tests that fail when they drift. Ships **no new status id** — it makes the next one a row | `track-contract` |
| `projection-host` | The **missing drive.** A reusable `Sync` host for out-of-combat tracks: it owns the apply/withdraw/idempotence dance once, so a new track is a ladder function plus a caller rather than a fourth copy of `ExhaustionPolicy.Sync`. Includes the self-regen-cycle refusal every projection policy repeats | `track-contract` |
| `track-catalogue` | Read-only inventory of which candidate needs are **affordable under the locked rules** — thirst, temperature, morale, disease, sleep/fatigue, environmental poison — each scored pool-vs-projection against its own `Never` violations, with the HUD surface it can actually reach. A reading, not a build | `track-contract`, `projection-host` |

### Why `track-contract` is first

Both other buildable modules are unmeasurable without it: `combat-track-authoring` cannot prove its
parity is total until the contract test exists, and `projection-host` has nothing to host against.
Matches this repo's own "no seam, this one really is first" pattern (`action-plan.md` §1.1).

## Build order

`track-contract` → {`combat-track-authoring`, `projection-host`} → `track-catalogue`.

The two middle modules are parallel-safe: one touches the catalog surface, the other a new Core
host. Neither imports the other.

## Deliberately deferred (not in any module here)

Choosing **which** need ships first; the balance numbers for any track; the content authoring of
individual stage containers; reviving any removed need (sleep/fatigue); a `slow`/`haste` status
category.

**Corrected 2026-10-02 — the D1 claim this map used to carry is wrong.** It named battle-engine
defect D1 (status pulses bypassing the combat resolver) as a live gap "belonging to the
battle-engine owner". D1 is **already fixed**: `BattleRunState.cs:469-497` wires `Bag.CombatMath`,
`Bag.ActorResolve` and a battle-seeded `effect-combat` RNG stream (solid-remediation T2.5), so a DoT
resolves through the same math as a swing. The companion claim that haste is inert was true only of
`classic-round`; `BattleModeProfile.Delve` sets `ordersBySpeed: true`
(`BattleModeProfile.cs:295-300`). What genuinely remains is that **no tuning row in
`gk-core/data/tuning/*.json` sets an orders-by-speed flag**, so the profile surface for it is
unwritten — a battle-**profile** gap owned by battle-tempo, still not this program's. Both errors
were the same shape: a fact about one profile stated as a fact about the system.

## The owner gate — resolved by default, not by a human

`K1` asked whether a seventh `ResourceIds` pool may exist. The packet
([research/status-tracks/owner-decision-packet.md](../research/status-tracks/owner-decision-packet.md))
states a default for every row precisely so nothing waits silently, and those defaults are what this
program was built under:

- **K1.1 — no seventh pool.** Every out-of-combat need ships as a **projection**, following the
  `nerve.*` precedent. (The packet also names `wound.*`, which is **approved but unbuilt** — see
  `status-tracks-ideal.md` §0; it is precedent by decision, not by shipped ids.) The pool question
  stays open only for a need that becomes an action cost.
- **K1.2 — no wall-clock-decaying need.** A need ships only if re-expressible as an event charge
  (`HungerCharge.ForRoom`'s shape); otherwise not at all.
- **K1.3 — deferral is correct.** The scalar is authoritative; the status is refreshed whenever a
  runtime exists to receive it.

So `track-catalogue` is **unblocked and built** ([status-tracks/need-inventory.md](status-tracks/need-inventory.md),
[carrier-rule.md](status-tracks/carrier-rule.md)). An owner who later wants a seventh pool changes
`K1.1`, and the affected needs are re-scored — the inventory is written so that re-score is a
per-need edit, not a rewrite.