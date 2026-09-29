# Empire economy SSOT — loam, the Fracture, and what a map is worth

**Status:** **Consolidated design, 2026-08-23.** This is what holds. It supersedes
[empire-economy-ideal.md](empire-economy-ideal.md), which is retained **only as the reasoning
trail** — that document accumulated four layers of retraction across a day of design and a reader
starting at its §1 absorbs superseded claims before reaching the corrections. Where the two disagree,
**this file wins.** (Capability-map finding A6; same pattern `resource-hub-ssot.md` used with its own
ideal.)

**Tests any of this must pass:** [economy-principles.md](economy-principles.md).
**Build order and audit:** [loam-map.md](loam-map.md). **Module specs:** [loam/](loam/).

---

## 1. Vocabulary — settled, and each one avoids a real collision

| Term | Means | Why not the obvious word |
|---|---|---|
| **stock** | An empire quantity — loam, essence, souls, rubble, ironwork, recruits; the full list is [empire-resource-ssot.md](empire-resource-ssot.md) | `resource` is taken by `resource-hub-ssot.md` for the **actor pools**; different scope entirely. **Corrected 2026-09-04: there are six, not five** — `poise` was registered 2026-08-26 (class-system, `poise-resource`), three days after this document was written, and the count was never re-checked. The *distinction* this row draws is the load-bearing part and it stands; see §8's narrowed rejection, which this row is the evidence for |
| **loam** | The stock that keeps ground real | New. Collides with nothing in `src/`, the web app, or `docs/` |
| **the Fracture** | The force that unmakes unanchored ground | `chaos` collides with the `chaos-marked` creature trait (`TraitBattleCatalog.cs:86`), and "fracture" is already the codebase's word (`SectorTypeCatalog.cs:8`) |
| **rootworks** | `StructureKind.LoamSource` — the category of things that make loam | `anchor` is the effect-atom layer's (`AnchorResolver`, `AnchorOrigin`, 20 files) |
| **handicap** | A declared per-faction balance multiplier | `cheat` is `FusionRpg.CheatCore`'s — and a hidden fudge cannot survive replay |
| **world** | One map run. Ending one and starting another **is** the progression loop | No new noun needed — `rpg_worlds.state` already exists |

**Rift shards from the old ideal are cancelled.** `shard.common…legendary` already means rarity shards
for fusion, in the same table a map currency would have used. Loam absorbed that role.

---

## 2. Three stocks, and only three

> ### ⛔ Count superseded 2026-09-16 — see [empire-resource-ssot.md](empire-resource-ssot.md)
>
> The P4 test below was run on 2026-08-23 over five loam-only buildings, and its answer (three) was
> right for that input. Later programs ran P4 on their own costs and added quantities —
> rubble and ironwork (base-defense decision 16, *"from three stocks to five"*), per-sector recruit
> accrual, and the item materials classes — without updating this heading. **The rules in this
> section still hold; the count does not.** Every quantity, its class and its faucet/sink now lives
> in the registry, and a new one must pass P4 and P6 and land a row there in the same change.

| Stock | Buys | Scope |
|---|---|---|
| **Loam** | Position — holding ground, and eventually building on it | **World.** Never banks |
| **Souls** | Roster power — summons, contracts, rituals | **Player.** `rpg_soul_ledger` |
| **Essence** ×6 | Fusion, element-matched and deliberately non-substitutable | **Player.** `rpg_creature_materials` |

### The P4 test, run — and the answer is three (2026-08-23)

This was deferred as *"needs build costs, so it cannot be run yet."* That was wrong: the buildings are
designed, so their costs can be drafted, and **P4 only needs five real costs to look at.**

| Building | Cost |
|---|---|
| Well (on a rootbed) | loam + turns |
| Waystation | loam + turns |
| Granary | loam + turns |
| Deep root | loam + turns |
| Soul conduit | loam + turns |

**Not one bottleneck pair anywhere** — every cost is "loam and time", and time is not a stock. So a
fourth material would be a currency wearing a costume, and **P4 says no.**

But the test also shows what is *missing*: with a single build currency there is never a moment where
having more of one thing cannot rescue you from lacking another, which is the tension P4 exists to
find. The fix is not a new stock — it is a **compound cost on the stocks we already have**:

> **Some buildings cost essence alongside loam.** A soul conduit wants `essence.dark`; an ice-climate
> waystation wants `essence.ice`.

That earns its keep three ways: it creates real bottleneck pairs (`min(loam, essence.dark)` — **P4**);
it gives **essence a second sink**, since fusion was its only one and **P6** requires two that compete;
and it makes an element-typed sector matter for *building*, not only for fusion, which is **P12**
doing more work than it was. Three stocks, no fourth, and the dimensionality comes from compound costs
rather than from more currencies.

It is not a conversion, so **P5** is untouched.

---

## 3. Anchoring — the spine

**Nothing outside your own ground is really there.** What you hold, you hold by force of reality, and
reality has to be supplied.

- A holding with a working **loam source** is anchored. Without one it **fades**, gradually and
  visibly, and is finally **lost**.
- Fading destroys **structures**, never a **natural rootbed** — so rootbed sectors are permanent
  strategic features, and seatland must be founded again from nothing.
- **The fade is its own enforcement.** A claim on barren ground is *allowed*, warned, and fades. That
  keeps corridor-seizing as a real play and closes the reclaim loophole for free.
- **Loam is fungible within a connected component** of your territory. Sources produce locally and
  unconditionally; upkeep is paid from the component's pool; **severing splits the pool.** One rule
  gives automatic flow, makes severing economic warfare, and needs no routing algorithm.
- When a component cannot pay, the **weakest contributor** is released first — worst net balance,
  ordinal tiebreak. The player never distributes loam; they only choose what to give up.

### Three kinds of ground

| Ground | You can |
|---|---|
| **Rootbed** | Settle from anywhere. Rare. The prizes |
| **Seatland** | Settle if you can reach it — a waystation must be founded within range of anchored ground |
| **Barren** | Never keep it. Take it, fight on it, watch it fade |

Two expansion styles fall out: **creep** (waystation by waystation, continuous, safe) and **leap**
(take a rootbed, found an isolated colony). Most 4X games offer one.

### Upkeep is local, and most ground loses money

```
upkeep(sector) = ( base + Σ structures + Σ garrison + f(development, danger) )
                 × FractureIntensityMilli / 1000
                 × UpkeepHandicapMilli / 1000
```

**No distance term** — intensity carries remoteness, and two multipliers make a stalled empire
unfalsifiable.

**The baseline is a deficit.** Profit comes from concentration, not breadth, so expansion is a
loss-making act justified by what it *reaches*. That is what makes upkeep a tax rather than a filter,
and it satisfies **P3** permanently: there is no empire size at which you are comfortable.

**Zomboss runs exactly this economy.** No asymmetry, no second mechanism. You can starve him, and
taking his capital collapses him.

---

## 4. What a world is worth — the progression loop

**This is the frame everything else sits inside**, and the storage seam built for determinism turns
out to be the same line that decides it.

> **You keep who you are. The worlds you leave keep going.**

*Amended 2026-09-19 (world-continuity, owner-approved): worlds no longer end.
[world-continuity-ideal.md](world-continuity-ideal.md) §6, [world-continuity-map.md](world-continuity-map.md).*

| Crosses to the next world | Stays with its world |
|---|---|
| Creatures, roster, contracts, codex | Territory and every structure on it — the world persists |
| Souls, essence, materials — **banked** | Loam (never crosses), recruits, and any world stock not carried as cargo |
| Legions and their cargo, up to the **carry limit** (rubble and ironwork only as cargo) | Anything beyond the carry limit |

- **World states.** Two columns on `rpg_worlds`: `state` (`active | hibernating | idle`, exactly one
  `active` map world per save) and `outcome` (`contested | won | fallen`).
- **Success = take the seat of the world's dominant enemy empire.** The world becomes `won`
  (*developing*): the full step keeps running, the other enemy empires keep acting, escalation slows.
  Not conquest: a deficit baseline gives every empire a natural equilibrium size. A target, not a
  checklist.
- **Failure = lose your own seat.** That world becomes `fallen` — hostile ground, revisitable, never
  deleted — and the save continues. Nothing already banked is lost.
- **Advance** is allowed at any time and moves the player to a new world at a **higher size tier and
  a higher base Fracture intensity** — the two difficulty axes that already exist as data. Winning
  first raises the carry limit. The world left behind **hibernates** (lazy coarse steps on the
  world-turn clock) or, with a warden stationed, goes **idle** (the expedition wall clock, capped).

### World sizes

Ids are plain; display names are content (`resource-hub-ssot.md` §3). That also dodges two collisions:
`reach` is 31 source files (`ReachMap`, `SupplyReach`) and `hollow` is already a sector id.

| Id | Display | Nodes | Availability |
|---|---|---|---|
| `small` | Pocket | ~8 | `first-light` |
| `medium` | Fragment | ~14–18 | **`two-hearths`, the gate map** |
| `large` | Expanse | ~32 | Gated on `world-generator` — not hand-authorable at ~33 lines per sector |
| `huge` | Abyss | ~64 | Same, **and** blocked until `ReconnectionCost`'s `O(V⁴)` is measured rather than asserted |
| `giant` | Maelstrom | ~128 | Same, **and** needs the Tarjan-first optimisation `spec-world-topology.md:52` already describes |

**What this builds on:**

1. **`rpg_worlds.state` already defaults to `'active'`.** Nothing wrote it after insert, so the world
   lifecycle was modelled and unused (`world-continuity-map.md` contradiction 10); `world-continuity`
   `world-state-vocabulary` makes it a closed vocabulary plus an `outcome` column.
2. **Banking stays a real decision.** Unbanked haul is not lost any more, but it is stranded: world
   stocks and background yield sit in that world's warehouses until collected by visiting, by cargo
   or by a cross-world route (`rift-trade`), and an unguarded old world can fall with them on it.
3. **The 500-hour problem needs a new cure** (§7), because bounded worlds no longer dissolve it.

---

## 5. The reward layer — what territory actually pays

Held ground yields **souls, essence and materials** through structures, into the **player** treasury.
This closes the reward hole that would otherwise make the map a cost with no payoff.

**Banking is conditional on connection, not on a convoy.** Haul banks automatically from any sector in
the same component as your capital; a severed sector accumulates locally and is at risk. That reuses
`TerritoryComponents` a third time and needs no new entity kind. Caravans stay a later option, not a
prerequisite.

### The soul conduit — the original request, answered

A **soul conduit** is a plain building that yields souls. No converter, no daily cap, no separate
currency.

It needs no artificial throttle because **loam is the throttle.** A conduit occupies a slot that could
have been something else, and it pays loam upkeep like everything else — so souls-per-world is bounded
by how much habitable, affordable ground you can dedicate to it. That is **P6** (competing sinks) and
**P2** (a territorial faucet paid for by a territorial cost), satisfied by the mechanism rather than
by a rule bolted on top.

**`spec-soul-economy.md`'s "never earn from anything but recorded Activity facts" survives intact**:
a world turn is a durable, uniquely-identified record — one row per `(world_id, turn)` — which is
exactly the dedupe key the ledger demands. Replay re-derives the same key and earns nothing new.

> **The unifying statement: loam is the throttle on every faucet the map has.** That is what the whole
> anchoring design buys, and it is why the economy needed designing before the buildings.

---

## 6. Storage and logistics — never trade, only movement

| | Answers | Effect on the constraint |
|---|---|---|
| A market | *"I need loam, I'll buy some"* | **Destroys it** |
| Logistics | *"I have loam there and need it here"* | **Preserves it** |

**Loam is never converted, only moved.** Every answer to a shortage is route, timing, capacity, risk.

- **Sector storage** (granary) turns a flow problem into a buffer problem — without it, income and
  spend must match every turn and no plan is longer than one. Overflow is waste; a stockpile is a
  target.
- **Legion storage** comes from **bearers** — a role on `WorldEntityMember`. Every slot spent carrying
  is a slot not spent fighting, which produces a deep-expedition and a strike-force archetype with
  nothing authored, and gives duplicate commons a job.
  - Capacity scaling with *every* member is degenerate: if capacity and burn both scale with headcount,
    range = `capacity/burn` is constant and the logistics layer evaporates.
- **A legion may spend carried loam to hold the ground it stands on** — which is how the first
  rootworks in a new sector ever gets built, and it makes planting a colony the tensest moment in the
  game.
- **Marching past your loam is warned, never refused** for the player (a suicide march to sever a chain
  is a real play) and **hard-gated for the AI**.

---

## 7. The 500-hour test — and the persistent-world cure

**Any permanent solution to a recurring cost is eventually free.** In an endless game that is fatal —
which is why every mechanic gets asked what it looks like after 500 hours.

*Amended 2026-09-19 (world-continuity): worlds persist, so "lost at map end" no longer cures anything.
The cure is [world-continuity-ideal.md](world-continuity-ideal.md) §6.6:*

1. **Background yield runs below 1** — hibernating and idle worlds produce at a per-mille multiplier
   that **decays as more worlds hibernate** (a soft curve, tunable; world-continuity `background-yield`).
2. **Background yield must be collected** — it lands in that world's warehouses and reaches the wallet
   only by visiting, by cargo or by a cross-world trade route, never straight into a wallet.
3. **Old worlds keep enemy pressure and upkeep**, so a permanent structure is never free: holding it
   needs a warden or attention, and neglect can lose the world.

| Mechanic | Verdict |
|---|---|
| **Deep root**, **scorched root**, granaries, waystations | **Cured by upkeep and pressure.** World-scoped, and the world persists; an old world keeps paying upkeep and can fall |
| **Wardens** | **Resumed with a new job and a new cost:** a commander and legion stationed on an old world, paying upkeep every period and unavailable in the active world. They lower loss odds and **never freeze decay**. The shipped per-sector freeze is withdrawn (`warden-mortality-ideal.md`) and retired by world-continuity `world-warden` |
| **The Unmade** | **Closed — see §7a.** They *are* a farm, deliberately. Throttled by loam (farming burns it), by depletion, and by their own spread |
| **Soul conduits** | **Safe.** Throttled by loam (§5) |

---

## 7a. The Unmade — your failed frontier becomes your grinding ground

**Owner decision, 2026-08-23: they are content, and farming them is a strategy.** My recommendation
was the opposite and it was wrong-genre — I argued from 4X instincts, where paying a player to give up
ground opposes a mechanic built on holding it. **This is an endless-grind RPG, and renewable content
is the point.** Anchoring is the strategy layer; the Unmade are the RPG layer. They coexist as long as
the economics do not invert.

**The rule that keeps them from inverting:**

> **Farming costs loam, exactly like holding does.** A legion parked in barren ground to cull Unmade is
> out of supply and burning what it carries, every turn. So farming is not free income — it is another
> way to spend the same scarce thing, and choosing between farming and holding is the same allocation
> decision the whole game is about.

That is the unifying statement doing its work again: **loam is the throttle on every faucet the map
has**, and farming is now one of them.

### The design

| Rule | Why |
|---|---|
| Faded ground spawns Unmade **at a rate, indefinitely** | Renewable, because the genre wants a farm. Bounded by time, not by a total, which is how grind economies are throttled |
| **They never drop loam** | The single most important rule here. A farm that funds its own upkeep is self-sustaining, and loam stops being the throttle. They pay in Tier-2 goods — the things that carry between worlds, which is what grinding is *for* |
| **They spread if not culled** | Neglect still compounds: an unfarmed faded sector raises intensity in its neighbours and eventually pushes into held ground. The farm fights back, so farming is maintenance rather than free income |
| **Spawn rate depletes locally and recovers slowly** | **P9.** Stops one legion parking forever on the single best spot; `DepletionMilli` is the field for it, already shipped and still unread |
| **Deeper ground spawns stronger Unmade with better drops** | The risk/reward gradient follows the chaos gradient, so `FractureIntensityMilli` gets a second job — and **barren deep ground becomes worth visiting even though it can never be held**, which is the best answer yet to "what is unheld territory for" |

### What this settles

- **A1's last open cure is found.** The 500-hour test asked what stops abandonment becoming optimal;
  the answer is that abandonment is not free, because farming costs loam and the farm depletes.
- **It partially fills the reward hole (G-F)** — post-gate, once `combat-handoff` decides what a world
  battle pays. Territory you *cannot* hold finally has a use.
- **A constraint lands on `combat-handoff`:** world-battle rewards must be Tier-2 only. If a world
  battle ever pays loam, this entire throttle collapses in one line of a different module's spec.

---

## 8. Sub-mechanisms — kept, and rejected

**Kept:** the Unmade (§7a — content, farmable, loam-throttled; reuses `WorldFactionKind.Wild`, no new AI) ·
fade contagion (reuses `PressureMilli`) · wardens · prospecting (hidden rootbeds — and it fixes the
observed defect where `Explore` fired three times and then never again) · deep tap · scorched root ·
reavers · Fracture surges (`TurnCalendar` already rolls `Plague`, pure in `(turn, seed)`, and its
effects have never landed).

> ### ⛔ Correction 2026-09-04 — the "loam as a battle resource" rejection was over-broad
>
> **Owner call, and this document's own §1 is the evidence.** The rejection below reads *"loam as a
> battle resource (scope collision with the actor hub)"*. §1 of this same file states that a **stock**
> and an **actor pool** are *"different scope entirely"* — so a stock being spent during a battle
> cannot collide with the actor hub unless it is modelled *as* an actor pool, which nothing proposed.
>
> **What actually collides, and what the rejection should have said:** loam as a **seventh actor
> pool**, sitting beside `stamina`/`qi` on `resource-hub-ssot.md`'s closed six-value set. That would
> collide, and it stays rejected.
>
> **What does not collide, and is now permitted:** a **side-scoped, transient battle budget** —
> seeded from world stock when the battle is requested, spent inside the board, and reconciled back
> through the outcome record. No actor ever holds loam; no pool is added. This is the **depot**
> pattern already named in `world-graph-ideal.md:458` (*"depot (starting resource for the fight)"*),
> and it is how `base-defense-ideal.md` §5.13 prices in-battle construction.
>
> **Two things that make this a defect rather than a judgement call**, recorded so the correction is
> auditable:
> 1. It contradicts §1 of its own document.
> 2. It is the **only** entry in the rejected list with no principle behind it — its siblings cite
>    **P5**, **P7**, **P4**, or a stated mechanism. A four-word parenthetical was doing the work of a
>    tested conclusion.
>
> **The `combat-handoff` constraint in §9 is untouched and still binding:** a world battle must never
> **pay** loam. Spending is a sink and drains; paying is a faucet and would collapse §7a's farming
> throttle. The guardrail that keeps the two apart: **destroying a building never refunds loam.**

**Rejected, with cause:** a loam market (**P5**) · **loam as a seventh actor pool** — *narrowed
2026-09-04 from "loam as a battle resource (scope collision with the actor hub)", see the box above;
a side-scoped battle budget is permitted, a per-actor pool is not* · loam grades or tiers (**P7**,
and no `min(x,y)` bottleneck so also **P4**) · the Fracture
as a commanding faction (a third brain to produce what a spread pass gives free — it is a *field*) ·
per-creature loam upkeep (contracts already charge a daily soul tribute) · randomised yields (determinism
survives it; *planning* does not — variance belongs in announced surges).

**Territory is light in the dark.** `StabilityMilli` is a shipped 0–1000 per sector that already
hashes and replays; render it directly and the map's whole mood is one field. **Fading and barren must
never look alike** — one is a problem you can solve, the other was never yours to keep.

---

## 9. Still open — one item, with a method attached

**Every number.** Deliberately, and it is not a question: `loam-calc` builds the harness precisely so
they can be *measured* against a real map rather than argued over. Choosing them here would be guessing
with extra steps, and §13 of the principles already says which measurements decide them.

Everything else that was open is closed and recorded where it belongs — the P4 test in §2, the
progression loop in §4, the soul conduit in §5, the 500-hour cures in §7, the Unmade in §7a, and
G-F's framing as the playtest brief in `spec-loam-maps.md` rather than as something to remember.

### Constraints this design lands on modules outside it

Recorded here because a constraint nobody wrote down is a constraint that gets broken by someone who
never read this file.

| Module | Constraint |
|---|---|
| `combat-handoff` | **World-battle rewards are Tier-2 only.** If a world battle ever pays loam, §7a's farming throttle collapses in one line of another program's spec |
| `world-generator` | Zomboss's capital must be **reachable and takeable at equilibrium empire size** — very different from "the map must be holdable" (§4). And a map must mix habitable and barren ground, or the settlement rule has no teeth |
| `sector-development` | Development must raise yield **faster** than it raises upkeep, or nobody will ever develop (**A8**) |
| `creature-contracts` | *Superseded 2026-09-19 (world-continuity):* the per-sector warden's permanent binding slot is no longer the cure — once worlds persist it would be lost forever. Wardens are now world wardens paying upkeep (§7); existing bindings are released and their slots freed by world-continuity `world-warden` |
