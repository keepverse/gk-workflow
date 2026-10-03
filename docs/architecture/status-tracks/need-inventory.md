# Need inventory

A reading, not a build. Six candidate out-of-combat needs, each scored against the locked rules under
the written defaults in [packet](../../research/status-tracks/owner-decision-packet.md). The reasoning
is [ideal](../status-tracks-ideal.md); the build order is [map](../status-tracks-map.md). The rule
this file applies is [carrier-rule](carrier-rule.md).

Read [carrier-rule](carrier-rule.md) first: it is the deciding question, and this file is six
applications of it. Nothing here is a proposal to build; a row is an inventory reading.

## The two binding `Never` lists

Only these two rule sets bind a carrier choice. Quoted:

- `docs/architecture/party-dungeon/spec-delve-attrition.md:400-403` — *"**Never:** a wall clock,
  `ElapsedDays`, a due stamp or a scheduler for recovery; a hand-listed resource subset in code; a
  `nerve` pool or a seventh `ResourceIds` entry (spirit is the pool); per-room loyalty; `hp`
  exhaustion …"*.
- `docs/architecture/resource-hub-ssot.md:201-208` — *"**Six-coverage rule (owner, 2026-09-02) —
  normative.** Every derived-stat family that affects a resource MUST cover all six resources.
  `ResourceIds` is `{ hp, stamina, hunger, spirit, qi, poise }` and it is the only list. A family that
  covers a subset is a **defect, never a feature**…"*, extended at `:210-212` to *"every
  hand-maintained list, not just to registration"*.

Together they mean: a pool route is legal only as a **seventh** `ResourceIds` entry (an ADR,
`resource-hub-ssot.md:134`), and a projection route is legal only as a status ladder over a scalar
held in durable party state.

## Shared facts behind every row

Read once; the table below cites these.

- **Legal decay sources.** Per-room charge — `HungerCharge.ForRoom`
  (`gk-core/src/FusionRpg.Core/Delve/Attrition/HungerCharge.cs:27`), pure and clock-free. Per-delve
  decrement — `CloseDelve`'s recovery aging (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs:1152`).
- **There is no delve tick.** The spec states it: *"Between rooms no tick advances"*
  (`docs/architecture/party-dungeon/spec-delve-attrition.md:121-123`), and its own carry-in
  description passes `atTick: 0` (`:117`). In code the tick is a **parameter that defaults to
  whatever the caller passes**, not a fixed literal: `PartyPoolsCarry.BuildForBattle`
  (`gk-core/src/FusionRpg.Core/Delve/Attrition/PartyPoolsCarry.cs:44`) and `CarryOut` (`:58`) both
  take `long atTick`, and `RestResolver.Resolve` passes its own `atTick` through
  (`gk-core/src/FusionRpg.Core/Delve/Attrition/RestResolver.cs:49-58`). The *callers* supply `0` —
  and the shipped delve path has none, because `BuildForBattle`/`CarryOut` have zero production
  callers (`docs/architecture/deployment-hierarchy/spec-deploy-carry.md:65`). So "every call site
  passes `atTick: 0`" is true in effect and slightly wrong in mechanism: **no call site exists to
  pass anything**, and the only in-battle seeding is `BattleRunState`'s cost-ledger
  `ResourcePools.GetOrCreate(key, derived, NowTick)`
  (`gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs:733`), anchored on the battle's own tick.
  Either way there is no monotonic tick **between** rooms, so K1.2's conclusion is unchanged.
- **A status can never publish a meter — because the meter vocabulary is the resource vocabulary.**
  `ui.present`'s `meterId` param declares `Vocabulary: ResourceChannels`
  (`gk-core/src/FusionRpg.Core/Effects/Atoms/AtomKindRegistry.cs:939-940`), and
  `ResourceChannels()` is *the same live function* `resource.delta`'s own `channel` param reads
  (`gk-core/src/FusionRpg.Core/Effects/Atoms/AtomKindRegistry.cs:116-120`) — one SSOT, not a copy,
  so the vocabulary widens the day a seventh resource lands with **zero edits to this kind**. The
  generic enforcement loop (`gk-core/src/FusionRpg.Core/Effects/Atoms/AtomKindRegistry.cs:301-319`)
  refuses any value outside a declared vocabulary at **load**: a `meterId` that is not a
  `ResourceIds` member is an `AtomRejection` (`BadParamValue`), not a silently accepted string.

  ⚠️ **A weaker version of this claim was written here first and removed.** It pointed at
  `ActorHudMeterOverride.Set`, which does accept any non-empty string
  (`gk-fusion/src/FusionRpg.Injector/Hud/ActorHudMeterOverride.cs:24`) — but that is the *runtime
  sink*, downstream of the load-time refusal, and generalising from it produced the opposite
  conclusion. The limit is real and enforced at authoring time; the enforcement lives one layer
  earlier than the sink that would have suggested otherwise.

## The six needs

### thirst

- **What it would be.** A monotone drain with a threshold consequence — the same shape as `hunger`,
  which is already a shipped pool. Distinct from hunger only in flavour unless a rule binds it.
- **Carrier under K1.1.** **Projection**, by default. Nothing spends thirst; its consequence is
  thresholded. A ladder of three staged ids is the `nerve.*` shape exactly
  (`StatusCategoryRegistry.cs:32-34`, `NerveLadder.cs:15`).
- **Never clauses.** A seventh pool violates `spec-delve-attrition.md:401-402` and breaks
  six-coverage `resource-hub-ssot.md:203-208`. A projection violates none, provided its scalar lives
  in party state and not on the status.
- **HUD surface.** Token only, per the correction above.
- **Decay source.** Per-room charge, `HungerCharge.ForRoom` shape (`HungerCharge.cs:27`) — thirst
  would need its own `hazardBand` term, which is content, not mechanism.
- **Honest note.** Thirst is the **weakest** of the six as a *new* need: it is `hunger` renamed, and
  shipping it is a case for not shipping it. It is in this inventory because it was a named
  candidate, not because it is well-argued.

### temperature

- **What it would be.** **Two-sided and signed** — hypothermia below neutral, hyperthermia above.
  Neither shipped ladder does this: `NerveLadder.StageFor(int stacks, long spiritResolved,
  IReadOnlyList<int> thresholds)` (`gk-core/src/FusionRpg.Core/Delve/Attrition/NerveLadder.cs:15-22`)
  walks a one-sided list — `stage = -1`, then "highest stage whose threshold ≤ stacks" (`:20`).
  It has no notion of a value *below* neutral mapping to a different id, and no negative-stack input
  path.
- **Carrier under K1.1.** **Bad fit, stated plainly.** A ladder in both directions is a new
  resolver, not a new data row, and the shipped `NerveLadder` does not express it. Modelling
  temperature as a *signed scalar* + a ladder that branches on sign would work; modelling it as one
  one-sided ladder silently loses half the range, which is worse than not shipping it.
- **Never clauses.** Same as thirst for the pool route. The projection route additionally strains
  `NerveLadder`'s one-sided contract — a convention, not a `Never` clause, but a real one.
- **HUD surface.** Token only, and a token cannot express "which side of neutral" — a second id
  would be needed per stage *and* per side, which is the `nerve.*`-shaped cost with double the
  registration surface.
- **Decay source.** Per-room charge, driven by a room climate the graph already rolls. Legal.
- **Verdict.** Needs the ladder resolver reworked first. Cheapest honest answer is a **second
  one-sided ladder per side**, not a signed one — but that is a design decision, not a reading.

### morale

- **What it would be.** A tiered consequence with **nothing spending it** — purely thresholded, and
  two-sided in the good direction (a bonus, not a drain).
- **Carrier under K1.1.** **Projection**, unambiguously. This is the ideal §4 case.
- **Never clauses.** None for the projection route. A pool would violate both binding lists.
- **HUD surface.** Token only.
- **Decay source.** Per-room charge is the natural fit — morale moves on rooms, not minutes.
- **Precedent.** The `wound.*` shape (ideal §0) is a good tier, not a drain.

### disease

- **What it would be.** **Escalation with contagion semantics** — the one candidate whose semantics
  an existing mechanism already owns.
- **Carrier under K1.1.** **Projection, and it is the strongest fit in this table.** `StatusRuntime`
  already owns contagion hops and apply-time immunity; a disease that escalates is a stage ladder
  whose top stage is a `contagion`-category status. The categories are `dot`/`cc`/`contagion`
  (`gk-core/src/FusionRpg.Core/Status/StatusPolicy.cs:70-75`) and the registry picks the resist axis
  (`StatusCategoryRegistry.cs:64-68`), so escalation *is* expressible without a new category.
- **Never clauses.** None, **provided** disease escalation never introduces a new status category —
  `StatusCategoryRegistry.Register` throws on anything but the three
  (`gk-core/src/FusionRpg.Core/Status/StatusCategoryRegistry.cs:49-50`).
- **HUD surface.** Token only.
- **Decay source.** The awkward one. A disease with an incubation period wants a *timer*; under K1.2
  that is out, so incubation must be charged per room or per delve-crossing instead. **That is the
  design tension, not a mechanism gap.**
- **Honest note.** Disease is the candidate most likely to become a **second clock** the moment it
  wants to be realistic. K1.2's default is what stops it; honour it deliberately.

### sleep / fatigue

- **What it would be.** Historically a wall-clock decay — which is precisely why it is gone.
- **Carrier under K1.1.** **Excluded, and excluded before any carrier question.** The need was
  **removed** on paywall-adjacency grounds: the survey notes *"the ones that were wall-clock (P3's
  fatigue) were removed"*, and the reason is that *"a meter the player cannot choose what to spend on
  reads as a wall"* (`docs/architecture/party-dungeon-ideal.md:343-344`). The repo's own ruling is
  quoted at `:1788`: *"this game is not a paywall game; we don't limit players by a stamina system
  like some cheap mobile game."* Sleep as a *need* is therefore not merely unbuilt — it is **refused**.
- **Never clauses.** K1.2 **and** the refusal both apply. Reviving it is a product decision first
  (ideal §6, *"Ask first … any revival of a removed need"*).
- **Re-expressible?** Only as an **event charge** — the `HungerCharge.ForRoom` shape — e.g. resting in
  a `rest` archetype grants it. That is a *different need* (a spendable rest-benefit), not sleep. Any
  proposal to revive fatigue should be renamed to what it actually is, or refused.
- **HUD surface.** N/A.
- **Verdict.** **Excluded.** No revival, no carrier, no amount of projection work.

### environmental poison accumulation

- **What it would be.** A monotone accumulation that *hands off* to an existing combat status once
  the actor is in a fight. The out-of-combat part is a charge; the consequence is already shipped.
- **Carrier under K1.1.** **Projection**, and it is the **smallest** of the six: the escalation
  target already exists.
- **Never clauses.** None. Note the naming hazard, though — see the correction below.
- **HUD surface.** Token only, and only while the projection is live.
- **Decay source.** Per-room charge, scaled by the room's hazard band — the `HungerCharge.ForRoom`
  shape verbatim.
- **Precedent.** **`poison` is already a shipped combat status** — `["poison"] =
  StatusL2bCategory.Dot` (`gk-core/src/FusionRpg.Core/Status/StatusCategoryRegistry.cs:9`), inside
  the locked 24. **Only the environmental accumulation is new.** Do not re-register `poison`, and do
  not read its presence in the registry as the out-of-combat half being built.

## Summary

| Need | Carrier | One-line reason |
|---|---|---|
| thirst | projection | `hunger`'s twin; `HungerCharge` charge |
| temperature | **bad fit** | two-sided; `NerveLadder` is one-sided |
| morale | projection | tiered, nothing spends it |
| disease | projection | `StatusRuntime` already owns contagion |
| sleep / fatigue | **excluded** | removed as paywall-adjacent |
| environmental poison | projection | escalation target already ships |

**No need in this table needs a pool under the K1.1 default.** The pool question stays open for a
need that becomes an action cost — that is the *only* trigger that reopens K1.1, and none of these six
is it.