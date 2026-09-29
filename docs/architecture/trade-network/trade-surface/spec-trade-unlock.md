# Spec: `trade-unlock`

**Status: written 2026-09-19 against the approved map** ([trade-surface-map.md](../trade-surface-map.md),
APPROVED 2026-09-19, module 10, wave 2). **UI-gate (teaching copy placement only):** the milestones,
capability flags, the first-throttle guarantee and the teach-once record are fixed here; where the one
explanation renders is not (see *Layout pending `/idea-ui`*). Every `file:line` below was opened this
session. Docs only.

## Objective

Nothing trade adds is present on a player's first turn (GG-44). Each trade surface appears when its
mechanic first matters, says what unlocks it while locked (GG-17), and is explained once, in place, the
first time it is met (GG-45). Every unlock is a world-state fact that replays identically, and every step
of the ladder is proved reachable by real commands.

**Round 4 (2026-09-19, [decisions-round-4.md](../decisions-round-4.md)) is binding here:** the unlock
ladder is **building-driven** — *a feature unlocks when its building exists* (§B). The two milestones
stay, but only for **teaching** (when to explain) and for the Diplomacy layer's first appearance; every
feature flag is now derived from the faction's buildings (§2). The first-throttle answer is *"build a
Counting House"* (Q3, §3).

This spec also **resolves the map's contradiction 2** (owner decision OD-6, 2026-09-19): *"lanes never
bind on a player's first world"* (trade-network ideal §8.6) and *"a first throttle is guaranteed on a
first world"* (§14b) both hold, because the guaranteed throttle is named below and is not a lane-capacity
throttle.

## Locked anchors

- **Milestones are hashed world-state facts**, monotonic per faction per world, derived inside the step —
  never from unhashed presentation state — so a replay reaches the same unlock on the same turn.
- **The rail derives from state, never a constant** (`gk-web/web/fusion-rpg-web/src/shell/railState.ts:1-6`,
  GG-44). The same rule now applies to lenses (`flow-lens`) and trade sections.
- **Owner decision OD-1 (2026-09-19):** treaties get a new **Diplomacy** rail layer, unlocked at **first
  contact**. This module owns the first-contact fact and the `diplomacy` capability; `treaty-screen` owns
  the layer.
- **Owner decision OD-6 (2026-09-19):** the first throttle's source is named in this spec (Design 3).
- **Teach once** is a save-scoped fact in the one story ledger, not a third store.
- **No debug fabrication in reachability** ([live-probe-standard.md](../../../contributing/live-probe-standard.md)
  scope rule): reachability is proved by admitted world commands only.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| State-derived unlock ladder with a required locked reason | `gk-web/web/fusion-rpg-web/src/shell/railState.ts:65-74` (ladder with reasons), `:76-93` (`isUnlocked` from inputs) |
| Intel memory reaching `Watched` for a sector seen this turn | `gk-core/src/FusionRpg.Core/World/Intel/FactionIntel.cs:169` |
| `Clan` and `Rival` faction kinds | `gk-core/src/FusionRpg.Core/World/FactionKindCatalog.cs:13,15` |
| The shipped first-world template id | `gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:15` (`first-light`) |
| A domain-ledger precedent for a once-only fact (not generic) | `gk-core/src/FusionRpg.Core/Items/Surfaces/CompendiumReveal.cs:16` |

### Wiring gap

| What | Where | Closed by |
|---|---|---|
| Lenses are a compile-time constant, so none can be locked | `gk-web/web/fusion-rpg-web/src/stages/world/lenses/LensPicker.tsx:33` | `flow-lens`, reading this module's flags |

### Real gap

No milestone fact, no capability flag, no first-throttle guarantee in any template, no generic taught
record. The empire-development milestone the ideal names is undefined in specifics
(`docs/architecture/empire-development-map.md:76-84`: *"settled in direction, open in specifics"*).

## Design

### 1. Milestone facts (Core, hashed)

```csharp
// src/FusionRpg.Core/World/Trade/TradeMilestones.cs (new)
public enum TradeMilestone { FirstThrottle, FirstContact }   // closed; wire ids "first-throttle", "first-contact"
// WorldState gains a sparse, append-only per-faction set: (factionId, milestone, turnReached).
```

Written by the step in Snapshot (after Intel is known for the turn).

**Which stamp gates it (settled 2026-09-20, reconciliation R-16).** This module registers **no capability
flag of its own** — `trade-surface` registers no stamp capability anywhere, and its `TradeCapabilities` are
milestone UI unlocks derived from present state, not stamp rows
([../landing-order.md](../landing-order.md) §2 row 24, §10 R-16). It is gated all the same, by the
**producers'** flags: every milestone is reached only through a producer's behaviour (`first-throttle`
through `production-halt` and the logistics entries; `first-contact` through a seeded treat-capable
faction), so **a world whose stamp grants none of the producers' flags has an empty milestone set**, and
**an empty milestone set emits no canonical row at all**. That is why a world stamped before this module
replays byte-identically: emptiness, not a flag of this module's own. The milestone row is a **sparse**
conditional `WorldCanonical` row and takes its slot under landing-order §4's sparse-row clause — after the
last conditional row present at landing — and, because it emits nothing for a world without the producers'
flags, it moves no existing hash and owes no re-bless.

| Milestone | Becomes true on the first turn that… |
|---|---|
| `first-throttle` | the faction's committed report carries a `production-halt` fact, a `logistics.overflow`, `logistics.strand` or `lane.cut` entry, **or** `forecast-facts`' pure dry run, taken **inside the step** over the state after Snapshot, names a throttle — whichever is earlier (audit 2026-09-20: this read "post-commit", but a hashed milestone may only depend on what `Step` computes from hashed state, P13) |
| `first-contact` | the faction's intel reaches `Watched` (`FactionIntel.cs:169`) on a sector held by a faction of kind `Clan` or `Rival` |

`first-contact` reads *treat-capable* factions only: the dominant enemy empire is present from turn 0 and
never treats with the player (decided: round 4 Q4), so counting it would unlock an empty
layer on turn 1. This is the reading of OD-1's "first contact" this spec adopts; it matches the ideal's
§8.6 *"first clan contact"*. Once written, a milestone is never removed (monotonic by construction:
append-only, sparse, no step deletes a row).

### 2. Capability flags (pure derivation) — building-driven since round 4

```csharp
public sealed record TradeCapabilities(
    bool Logistics, bool Diplomacy,                  // milestones (teaching, first appearance)
    int TradeTier, int DiplomacyTier, int BankingTier, int CaravanTier, int StorageTier); // buildings
public static TradeCapabilities For(WorldState world, string factionId);
```

The tiers are `trade-foundation` `sector-features`' `FactionTier(world, faction, feature)` for the
features `trade`, `diplomacy`, `banking`, `caravans`, `storage` — each the faction's highest **active**
tier in this world (`Hubs.TradeTier` and `DiplomacyGate.TierOf` are thin wrappers over it).

- **The split-owner rule is inside that read (round 6 S1).** *"A building whose sector and slot have different
  owners counts for nobody until one faction owns both."* `FactionTier` answers **0** for such a building, so
  the flag locks and the player sees the lock's own reason — this surface never compares a slot owner with a
  sector owner, and never softens the rule to "nearly unlocked".
- **The rows are loadable at all only because of round 6 C2.** Until C2 the feature buildings were emitted
  `structureKind: none`, which never loads, so every tier here would have read 0 for ever and every building
  flag would have been permanently locked (global audit C2). The neutral `StructureKind.Feature` is what makes
  this section real, and this surface's landing therefore follows the wave that lands `sector-features` and the
  member ([../landing-order.md](../landing-order.md)).
- **A ninth feature exists after round 6 L6** (`standard`, the Standard Hall). It is deliberately **not** a
  flag here: forging standards is `legion-build`'s surface, not the trade rail's, and this spec's flag list
  stays the five trade/logistics ladders plus the two milestones. When a legion surface wants it, it reads the
  same `FactionTier(standard)` — never a copy of this record.

| Flag | Derived from | Unlocks | Locked reason (catalog copy) |
|---|---|---|---|
| `Logistics` | `first-throttle` milestone | status strip, forecast chip and nag, flow lens, the trade panel's warehouse and flow rows (goods flow home with no building, so these are teaching unlocks) | *Unlocks when your goods first have nowhere to go* |
| `TradeTier ≥ 1` | a Trading Post (on a Wildland or Market Square slot, round 5 B1) — the trader's best tier anywhere in the world counts at a clan hub (round 5 B4) | the trade panel's hub section; hub order policy (clan barter) in the policy editor; `trade-away` answers at clan hubs | *Build a Trading Post to trade with clans* |
| `TradeTier ≥ 2` | a Market | empire market orders | *Upgrade to a Market to trade with empires* |
| `TradeTier ≥ 3` | an Exchange | preferential and bloc proposals on the treaty screen | *Upgrade to an Exchange for preferential terms and blocs* |
| `CaravanTier ≥ 1` | a Caravan Yard | the legion sheet's `route` tab (caravan standing route) | *Build a Caravan Yard to send caravans* |
| `BankingTier ≥ 2` | a Treasury | the per-good hold control (round 4 Q2) | *Upgrade to a Treasury to hold goods for sale* |
| `Diplomacy` | `first-contact` milestone | the Diplomacy rail layer appears (OD-1): relations, clan access, embargoes shown | *Unlocks when you first meet a clan or rival* |
| `DiplomacyTier ≥ 1` | an Embassy | treaty proposals with empires on the treaty screen | *Build an Embassy to make treaties with empires* |
| `DiplomacyTier ≥ 2` | a Consulate | bloc and embargo verbs | *Upgrade to a Consulate for blocs and embargoes* |

**Start kit (round 5 A1).** Every empire's seat starts with a tier-1 Counting House and a tier-1
Storehouse (`world-continuity` `world-creation` §5a), so `BankingTier` and `StorageTier` are 1 from turn 0
and no lock above reads them at 1; the Treasury row (`BankingTier ≥ 2`) is the first banking lock a player
meets. The first-throttle sector (§3) is therefore **never the seat**: the seat is a bank point from turn 0.

The old `Routes` flag (first contact) is **retired**: own-route redirects (`route-set` to a bank point)
ride `Logistics`, clan barter rides the Trading Post, caravans ride the Caravan Yard. **Building flags are
not monotonic**, by the register's rule: lose your only Trading Post and clan barter locks again, with its
reason. The two milestones stay monotonic.

**Capability flags here are not the world stamp's capability rows (round 6 C1).** Two different things share
the word: the **stamp's** rows (`trade.logistics`, `trade.exchange`, …) are what a world's *rules* grant, one
row and one `RulesetVersion` bump per landing wave (C1), registered by the module that owns the wave; the flags
in this section are a **pure derivation over present state** for the *surface* — what this faction can do
right now, given its buildings. This module registers no stamp row and takes no bump. Where the two meet: a
surface flag can only ever be true if the stamp also grants the rules behind it, so `For()` reads the stamp
first and returns every building tier as 0 on a world whose stamp lacks the feature's wave — otherwise the rail
would offer a control admission must refuse (the TC6 shape). That check is a stamp read, not a second flag.

The flags ship on `WorldTradeDto.Capabilities` (`trade-wire`) and into the rail's unlock inputs as a new
`hasFirstContact` field for `treaty-screen`'s rail entry.

### 3. The guaranteed first throttle — its source, named (OD-6)

**The source is a production halt with bottleneck reason `no-path`, produced by template placement, not
by lane capacity.** On a first world:

1. The template places a yield structure in a sector the player **holds from turn 0**, and that sector
   has **no Supply-lens path to any bank point** at creation. The path is closed by placement — its only
   connection to the capital is a `deep` lane (which carries no goods, `logistics-flow` `path-cache`), a
   keyed gate, or ground held against the player — never by a lane that is too narrow.
2. With default auto-banking the goods stay in that sector's warehouse; `production-halt`
   (`sector-yield`) stops production on the turn the warehouse fills; `forecast-facts` names the halt one
   turn earlier with reason `no-path`.
3. **Template constraint (checkable):** the earliest turn any legal command sequence can open a path from
   that sector to a bank point is **later** than the turn the forecast first names the halt, and that
   forecast turn is ≤ `teach.firstThrottleByTurn`. So the throttle is reached whatever the player does.
4. **Lanes never bind on a first world:** every lane in a first-world template carries at least the
   template's total opening production (a width constraint on the template), so no `lane-capacity`
   bottleneck arises in the teaching window.

**Round 4 Q3: the answer is "build a Counting House".** The teaching row carries the **one explanation**
and `throttle-forecast`'s fifth answer, `build-feature` [`banking`] from `logistics-flow` `forecast-facts`
§2, naming a **Counting House** in the halted sector: it makes
that sector a bank point, so its goods bank where they are. One click files `build` when an own legion
stands there with the loam; otherwise one click sends the nearest idle legion and the next turn's row
offers the build (`throttle-forecast` §2). The earlier "show me" focus action is kept as a secondary view
action (it files nothing), no longer the row's only affordance.

**The template constraint gains two clauses (round 4):** the throttle sector — a held sector other than
the seat, which is a bank point from turn 0 by the round-5 A1 start kit — holds a free slot a Counting
House row allows (so the answer is admissible), and the player's starting forces include a legion that can
reach that sector by the forecast turn with the loam the Counting House costs (so the one-click answer is
real, not a dead button). Clause 3 above now reads: the earliest turn any legal sequence can open a path **or
make the sector a bank point** is later than the forecast turn — a Counting House started early still
cannot be **active** before the halt is forecast, because construction takes turns (a checkable clause on
the template, part of the same search in Acceptance 2).

Filed as a constraint on world-map-program's templates (today `first-light`) and on the world generator's
constraint table for first worlds.

### 4. Teach once

A save-scoped story-ledger fact `flag.set` with subject `taught:trade.<topic>` (the existing
`flag.set` member of npc-story-events' `StoryFactKind`, `spec-narrative-vocabulary.md` §3 — no new kind).
Topics are a closed list declared here: `first-throttle`, `flow-lens`, `routes`, `diplomacy`. A surface
shows its one explanation only when the fact is absent, and appends it when the explanation is shown.
Save scope, so a second world does not re-teach. The write goes through `story-ledger`'s
`AppendStoryFact` (idempotent on its dedupe key).

## Tunables

`data/tuning/trade.v1.json` (new): `teach.firstThrottleByTurn` (world turns, `int`; starting value by
principle: inside the first session's opening, a handful of turns).

## Numeric types

Turns are `int` (world turns already are). No magnitude.

## Contract exposed

| Member | Consumer |
|---|---|
| `TradeMilestone`, the per-faction milestone set, `TradeCapabilities.For` | `trade-wire`, `flow-lens`, `trade-panel`, `trade-policy-editor`, `treaty-screen`, `trade-status`, `throttle-forecast` |
| Teach-once topics and the `taught:trade.*` flag convention | every trade surface that explains itself |
| First-throttle template constraint | world-map-program templates, world generator |

## Acceptance (contract level)

1. **Reachability:** on each first-world template, a scripted sequence of admitted commands reaches the
   `first-throttle` milestone by `teach.firstThrottleByTurn` and reaches `first-contact`; each milestone is
   false the turn before and true at that turn. No debug endpoint is used. **Round 4:** the same script then
   files the forecast's `build-feature` answer and the halt clears once the Counting House is active; and a script
   that builds a Trading Post reaches `TradeTier ≥ 1` and a filled clan order (the reachability case that
   replaces exchange ask E-A9).
2. **Guarantee:** a **relaxed reachability bound** proves no legal command sequence opens a path from the
   throttle sector to a bank point, or makes it one, before the forecast turn: every own legion moves at
   its best speed, every build starts at the earliest admissible turn and pays nothing, and the earliest
   turn a path could open or a Counting House could complete is still later than the forecast turn. The
   relaxation over-approximates every real sequence, so the bound is sound and runs in time polynomial in
   the template, where the literal "search over every sequence" was exponential (audit 2026-09-20). The
   halt's bottleneck reason is `no-path`, never `lane-capacity`.
3. **Monotonic:** once true, a milestone stays true for that faction in that world in every later state.
   **Building flags follow the buildings:** razing the only Trading Post locks clan barter the same turn
   with its reason, and rebuilding unlocks it (both edges tested).
4. **Replay:** recomputing from the command log yields the same unlock turn and the same state hash.
5. **Old stamp:** a world stamped before this module hashes byte-identically (no milestone rows written).
6. **Teach once:** the explanation renders on the first throttle, never on a later one, and not in a
   second world of the same save.
7. **Locked states say why:** every locked trade surface renders its reason (GG-17); none is invisible.

## Layout pending `/idea-ui`

Not decided here: where the one explanation renders on each surface (inline row, callout, inspector
paragraph), the "show me" affordance's piece, and the locked-state pieces. Through
[idea-ui-phase.md](../../idea-ui-phase.md) before build.

## Test plan and verification boundary

- Core: milestone derivation, monotonicity, replay, old-stamp hash, template-constraint search —
  `core-fallback`.
- Data: teach-once append idempotence through `story-ledger` — `data-fallback`.
- Web: locked reasons and teach-once rendering — vitest. **Gap, stated:** no `web/` verification
  boundary (`gk-core/scripts/verification-boundaries.v1.json`); report, never run the full suite instead.

## Hard edges

- **FE stack (map §3 principle 13, audit 2026-09-20).** Chrome copy goes through Lingui macros and `npm run extract`; content words (goods, causes, kinds, building names) come from `trade-lexicon` / structure rows, never a Lingui key per id and never an id; glyphs map catalog `icon` keys to `lucide-react` with the GG-58 fallback; meters and charts are kit pieces or the locked libraries, never hand-rolled; pieces never fetch; folds are pure; the bus is closed.
- **A `WorldState` addition is gated by the producers' stamps, not by a flag of this module's** (corrected
  2026-09-20, reconciliation R-16 — this line used to read *"is stamp-gated"*, which implied a flag row 24
  never grants). The canonical form writes nothing when the set is empty, and the set is empty on a world
  whose stamp grants no producer's flag. See §Design 1.
- Template edits are world-map-program's; this spec files the constraint.
- The first-contact reading excludes the dominant enemy empire; if `counterparties` Q1 lands differently
  (peace with the dominant empire possible), the dominant empire joins the predicate as a reviewed change.

## Dependencies

`trade-wire`; `sector-yield` (`production-halt`, `bank-points`); `logistics-flow` (`path-cache`,
`logistics-facts`, `forecast-facts`); `counterparties` (clans and rivals are seeded — `clan-seeding`,
`empire-roster`); npc-story-events `story-ledger`; world-map-program templates (ask);
`trade-foundation` `world-stamp`.

**Closed-cycle landing note (global audit M1).** `trade-wire` ↔ `trade-unlock` is a cycle inside this
sub-program: the flags ship on `WorldTradeDto.Capabilities` (`trade-wire`'s payload) while `trade-wire`'s
unlock inputs read this module's flags. **One line closes it:** `trade-wire` lands **first** with the
`Capabilities` field **present and every flag false** (a wire contract addition, additive, no FE consumer yet);
this module lands next and fills it, and its acceptance asserts the field it fills is the one `trade-wire`
already ships. Neither is written against the other's unlanded code, and the FE gate reads whatever the wire
carries, so an intermediate state is a rail with everything locked — correct, not broken.

## Boundaries

- **Always:** facts in hashed state; reasons on every lock; real commands in reachability.
- **Ask first:** unlocking anything on the empire-development milestone before that program defines it.
- **Never:** unlock from unhashed UI state; re-teach; a lane-capacity throttle on a first world.

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world state (hashed facts), intel, templates, story ledger, rail/IA unlock ladder.
[~] Session boundary: trade-network-idea-20260919 record; check script not re-run (docs only).
[x] Read: IA §3/§5/§7, game-gui-principles GG-17/43/44/45, logistics-flow-map §3 (path-cache
    traversability), sector-yield-map §2.5/§2.8, npc spec-narrative-vocabulary §3, live-probe-standard rule.
[x] decisions.md: Game GUI (:110) — the Diplomacy layer amendment is treaty-screen's requirement.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run; no HIGH finding.
[x] Verified in code: railState ladder, FactionIntel Watched, faction kinds, template id.
[x] Surrounding sections read (path-cache traversability table; empire-development milestone paragraph).
[x] No untested constraint claimed; the guarantee is an acceptance search, not an assertion.
[x] No §2 invariant contradicted (determinism, standalone).
[x] Corrections propagated: contradiction 2 resolved in the map with a pointer here.
[x] No population pinned: 2 milestones, 3 flags, 4 topics are declarations with reasons.
[x] Cache: the capability flags change trade-wire's key set; that edge is in trade-wire's trigger list.
[x] Ordering: unlock asserted at a turn bound, not a sequence.
[x] No actor magnitude.
[x] No parallel path: taught facts in the one story ledger; rail unlock through railState.
[ ] Registry row: "no lane-capacity throttle on a first world" template constraint needs a guard row when built.
[x] Round 4 reconciliation (2026-09-19): building-driven flags (§2), Routes retired, Q3 answer and its
    two template clauses (§3), non-monotonic building flags; decisions-round-4.md read whole.
[x] Round 5 (2026-09-20): A1 start kit (BankingTier/StorageTier are 1 from turn 0; the throttle
    sector is never the seat); B1 and B4 noted on the TradeTier row.
[x] Round 6 (2026-09-20): S1 — the split-owner rule is read from sector-features, never re-derived (§2);
    C2 — the flags are only real because the rows now load under the neutral Feature kind (§2); C1 — surface
    flags are not stamp rows; this module registers none and takes no bump, and it returns 0 on a world whose
    stamp lacks the wave (§2); L6 — the ninth feature (`standard`) is deliberately not a rail flag; M1 — the
    trade-wire ↔ trade-unlock cycle has a one-line landing note (Dependencies).
```
