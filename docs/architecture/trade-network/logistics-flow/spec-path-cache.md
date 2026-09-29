# Spec: `path-cache`

**Status: written against code 2026-09-19** (branch `features/mega-merge`, `b82a4098`). Every
`file:line` below was opened in this session. Module id `path-cache`, row 3 of the
[logistics-flow map](../logistics-flow-map.md) (wave 2; depends on `logistics-canonical`, and reads
`sector-yield` `bank-points`, `counterparties` `diplomatic-stance` and `exchange` `trade-access` when they
exist). Ideal: [trade-network-ideal.md](../../trade-network-ideal.md) §7.6 (*own and unheld ground is
always open; foreign ground under `passage`*), §8.4 (*paths are cached and recomputed only when the
graph changes*), §9.2 rule 3, §9.3. DESIGN-GATE §2.16 (edge-refreshed caches). House style:
[spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Objective

For every faction with goods to move, know — without a search on the hot turn — the cheapest way from
any sector it could ship from to the destination its route wants: the nearest own bank point by default,
or a named own destination under a `route-set` policy. Rebuild only when something the answer depends
on has changed, and never through the O(V⁴) `ReconnectionCost`.

Success looks like: the cached answer equals a fresh uncached computation on every turn of any run; a
turn in which nothing topological changed performs zero rebuilds; and every change that should move an
answer does, including the ones that move **which** sectors the cache has answers for.

## Locked anchors

- **One traversal rule for goods and supply.** Goods use `LaneGraph`'s Supply lens: a severed lane, a
  shut gate, a `deep` rift and a `one-way` current carry no goods, exactly as they carry no supply
  (`gk-core/src/FusionRpg.Core/World/Topology/LaneGraph.cs:125-135`; lane types
  `gk-core/src/FusionRpg.Core/World/LaneTypeCatalog.cs:61-62`). Ideal §8.4 left this to the spec; one rule is
  chosen so the two never drift.
- **One edge cost.** `LaneCost.For` with no banner — goods have no element, so no ley discount
  (`gk-core/src/FusionRpg.Core/World/Movement/LaneCost.cs:134-147`).
- **One hostility rule.** A sector is a roadblock for a faction when a hostile projecting entity stands
  in it — the `SupplyGraph` rule (`gk-core/src/FusionRpg.Core/World/Movement/SupplyGraph.cs:30-31`) over
  `ZoneOfControl.IsHeldAgainst` (`gk-core/src/FusionRpg.Core/World/Movement/ZoneOfControl.cs:32-42`). Hostility
  itself is `ZoneOfControl.IsHostile` (`:15-16`) until `counterparties` turns it into a derived stance
  read from a logged per-turn band snapshot (umbrella §1a CM1).
- **Never `ReconnectionCost`** (ideal §9.2 rule 3). It is O(V⁴) and has three production callers
  (`gk-core/src/FusionRpg.Core/World/Topology/ReconnectionCost.cs:18-19`;
  `gk-core/src/FusionRpg.Core/World/Ai/SeveranceScore.cs:32`; `gk-core/src/FusionRpg.Core/World/Ai/ValueMap.cs:167`;
  `gk-core/src/FusionRpg.Server/WorldEndpoints.cs:864`). Every file of this module lives under
  `src/FusionRpg.Core/World/Logistics/`, which `trade-foundation`'s `routing-guard` scans.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Ordinal-ordered lane graph with a Supply and a March lens | `gk-core/src/FusionRpg.Core/World/Topology/LaneGraph.cs:20-27`, `:92-136` |
| The traversability predicate (severed, gated, supply-carrying) | `gk-core/src/FusionRpg.Core/World/Topology/LaneGraph.cs:125-135` (private today) |
| Supply reach as a plain traversal | `gk-core/src/FusionRpg.Core/World/Movement/SupplyReach.cs:24`, `:67` |
| Supply is recomputed every turn and never cached, on purpose | `gk-core/src/FusionRpg.Core/World/Movement/SupplyGraph.cs:7-11` |
| Every world collection is kept in stable id order | `gk-core/src/FusionRpg.Core/World/WorldState.cs:330-333` |
| A sector's owner is written in two places, both after `Production`: a claim settles in `Snapshot`, a fade or cede clears it in `Pressure` (a battle sets only a **slot** owner) | `gk-core/src/FusionRpg.Core/World/Movement/ClaimResolver.cs:101`; `gk-core/src/FusionRpg.Core/World/Loam/LoamPhases.cs:219`; slot owner `gk-core/src/FusionRpg.Core/World/Turn/BattleApplication.cs:161` |
| Presence changes on both sides of the phase: legions march in `Movement` (before it); the Unmade spawn a warband in `Pressure` (after it) | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:192`; `gk-core/src/FusionRpg.Core/World/Loam/LoamPhases.cs:300-306` |

### Wiring gap

None — the graph exists; nothing caches it.

### Real gap (this module closes it)

The topology key, the path trees, the rebuild, and the per-trigger tests.

## Design

### 1. What the cache holds

For each faction `f` that holds at least one sector, inside `LogisticsRuntime`:

- **One bank tree** — a multi-source shortest-path tree rooted at all of `f`'s bank points
  (`sector-yield` `bank-points`). For every sector it gives `dist` (path cost, `long`), the next lane
  and the next sector toward the **nearest** bank point, and which bank point that is.
- **One destination tree per distinct `route-set` destination** of `f` — same shape, single root.

A tree is flat arrays indexed by sector ordinal (`long[] dist`, `int[] nextLane`, `int[] nextSector`,
`int[] root`), grown only when the world grows. A packet in motion, a departure, and `forecast-facts`
all read the same arrays: the next hop from wherever the goods are, so a packet mid-route follows the
current best path without storing one.

### 2. Traversal

For faction `f`, a sector `s` is **open** when both hold:

1. `s` is own, unheld (`OwnerFactionId == null`), or owned by a faction that grants `f` `passage` or
   better (`exchange` `trade-access`; until that module lands the predicate is false and foreign ground
   is closed — today's rule); and
2. `s` is not held against `f` — no projecting entity hostile to `f` stands in it.

A lane is usable when `LaneGraph.IsTraversable(lane, LaneLens.Supply)` holds (this module makes the
existing private predicate `internal`, a visibility change only — never a copy) and both ends are open.
Sources and destinations must be own. Ground that stays closed — hostile, embargoed, contested — is
crossed only by a legion that fights through it (`fleet`).

**Search.** A reverse Dijkstra from the root set over usable lanes, with a binary heap on runtime arrays
keyed `(dist, sector ordinal)`. `nextLane[v]` is the usable lane from `v` to the neighbour `u`
minimising `dist[u] + cost`, ties broken by `u`'s ordinal and then by lane id — so the answer is a
function of state, never of heap internals. Nearest bank point ties break by sector id (the map's
acceptance). Path costs are `long`, `checked`.

### 3. When it rebuilds — the topology key (this replaces the map's hashed counter)

At L0 the step extracts, into runtime arrays, **every input the search reads** — this array set *is*
the key:

| Key part | Contents | Size |
|---|---|---|
| Index | the ordered faction id list and the ordered sector id list the other parts are indexed by (audit 2026-09-20: without it a faction or sector added or removed would shift every index and a compare could read equal arrays for different worlds) | factions + sectors |
| Lanes | per lane in id order: id, ends, `TypeId`, `Length`, `HazardMilli`, `State`, gate-shut flag | lanes |
| Owners | per sector: owner faction index (or none) | sectors |
| Presence | per sector: the sorted set of factions with a projecting entity standing there | ≤ entities |
| Relations | per faction pair: hostile bit, passage bit (from the one hostility predicate and `trade-access`) | factions² |
| Roots | per faction: sorted bank-point sectors; per faction: sorted distinct policy destinations | ≤ sectors + policies |

It compares the new arrays with the arrays the current trees were built from, element by element. Equal
→ reuse. Different → rebuild the trees of every faction whose slice changed (lanes, owners and relations
touch all factions; presence, roots and policies touch the factions they name) and swap the arrays.

Why a key and not the map's **hashed graph-version counter bumped at each mutating phase**: the search
reads the key and nothing else, so an input the key does not hold is an input the search cannot read —
a forgotten trigger is impossible by construction rather than caught by a test-mode fingerprint. It also
keeps this module out of `ClaimResolver`, `MovementPhase`, `LoamPhases`, `BuildResolver` and two
sibling programs' code, and it stores no derived value in hashed state
(`docs/architecture/world/spec-world-movement.md:150`). Filed asks A4 and A7 on the map shrink to one
requirement: whatever `counterparties` and `exchange` derive must be a pure function of hashed state or
of the logged per-turn input (CM1), which the umbrella already requires.

### 4. The trigger set (DESIGN-GATE §2.16), each mapped to the key part that sees it

| # | Trigger | Key part | Key set moves? |
|---|---|---|---|
| T1 | Lane `State` Open ↔ Severed | Lanes | No |
| T2 | Gate shut / opened (`GateKeyId`) | Lanes | No |
| T3 | Lane added or removed | Lanes | No |
| T4 | `Length`, `TypeId` or `HazardMilli` changes | Lanes | No |
| T5 | Sector owner changes (claim, cede, fade) | Owners | **Yes** — new own sources and destinations |
| T6 | A hostile projecting entity enters or leaves any sector | Presence | No |
| T7 | A bank point appears or disappears (a Counting House finishes its first build, is destroyed, or its sector changes owner — round 4 §B; a tier change is **not** a trigger) | Roots | **Yes** |
| T8 | A route policy is set, changed or cleared | Roots | **Yes** |
| T9 | Hostility between two factions changes | Relations | No |
| T10 | `passage` granted or withdrawn | Relations | **Yes** — foreign sectors join or leave the open set |
| T11 | The faction set changes (a faction is added to the world or removed from it — a new rival or clan, a destroyed empire) | Index, Relations, Roots | **Yes** — a faction gains or loses its trees |
| T12 | The sector set changes (a sector is added to the world) | Index, Owners, Presence; Lanes via T3 | **Yes** — a new sector gains a slot in every tree |

**The state-entry edges of the memo itself** (DESIGN-GATE §2.16 — the cache's own key set moves when the
*runtime* changes hands, not only when the world does). Each is covered by the exact key and each gets a
test, because a per-world memo that outlives a turn is exactly the shape that has shipped stale three
times:

| # | Edge | Why the exact key covers it |
|---|---|---|
| E1 | A commit that ran `Step` with the warm runtime **rolls back**, and the next attempt re-runs `Step` on the pre-turn world | The runtime now holds the rolled-back turn's key; L0 compares it with the pre-turn world's inputs, sees a difference and rebuilds |
| E2 | The runtime is **evicted or new** (server restart, first commit after load, a world woken from hibernation or idle) | An empty runtime has no key; L0 rebuilds everything (the cold path of `spec-logistics-phase.md` §Design 3) |
| E3 | A world **advanced outside `Step`** (a `world-continuity` coarse step on a hibernating world) comes back to the commit path | The inputs the coarse step changed differ from the memo's key; L0 rebuilds the slices that moved |
| E4 | The store is **reset** or the world id is **reused** for a new world | The key describes a different graph; L0 rebuilds. The store also drops the world's runtime on reset, but correctness does not depend on it |

*(T11, T12 and E1–E4 added in the audit of 2026-09-20: the enumerated set named ten triggers but not the
two that resize the key, nor the memo's own lifetime edges.)*

`Width` and `WardLevel` are **not** triggers: they change capacity and loss, never a path. A climate
change is not a trigger because goods carry no banner (§Locked anchors); if goods ever gain a banner,
climate joins the Lanes part in that change.

**When the change is seen.** L0 runs at the start of the Logistics phase. A change made earlier in the
same turn (a legion marching into a sector in `Movement`) is seen that turn; a change made after
Logistics (an owner change — a claim in `Snapshot`, a fade or cede in `Pressure` — or a warband spawned
in `Pressure`) is seen at the next turn's L0, the first flow that runs after it. No flow ever runs on a
stale answer.

### 5. Allocation and cost

A turn with no key change allocates nothing (the compare walks preallocated arrays). A rebuild reuses
the tree arrays and the heap; it allocates only when the world has grown past the arrays' size. Budget
(ideal §9.3): rebuild ≤ 5 ms at the giant tier, measured by `logistics-bench`.

## Tunables

None. Path cost is `LaneCost`'s, which is tuned where it lives.

## Numeric types

`dist` is `long`, `checked` accumulation of `int` lane costs. `LaneCost.For` already narrows its own
result to `int` with a floor of 1 (`gk-core/src/FusionRpg.Core/World/Movement/LaneCost.cs:146`); that narrowing
is `LaneCost`'s and is not changed here.

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World.Logistics.PathCache"
dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~Routing"
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <session id>
```

## Structure

```
src/FusionRpg.Core/World/Logistics/PathCache.cs          (new) — key extract/compare, rebuild, tree reads
src/FusionRpg.Core/World/Logistics/TopologyKey.cs        (new) — the key arrays
gk-core/src/FusionRpg.Core/World/Topology/LaneGraph.cs           MODIFIED — IsTraversable private → internal
tests/FusionRpg.Core.Tests/World/Logistics/PathCacheTests.cs              (new)
tests/FusionRpg.Core.Tests/World/Logistics/PathCacheTriggerTests.cs       (new) — one test per trigger
```

## Testing strategy

- **Equivalence (property):** for every turn of a scripted run and of seeded random runs on
  `trade-foundation`'s synthetic graph, the cached trees equal trees computed fresh with a cold runtime.
- **One test per trigger T1–T12**: the key moves, the affected faction's trees rebuild, and the answer
  changes as expected. T5, T7, T8, T10, T11 and T12 additionally assert that the **new key** — the newly
  owned sector, the new bank point, the new route source, the newly opened foreign sector, the new
  faction, the new sector — has an answer at the first L0 after the change.
- **One test per memo edge E1–E4** (rollback, cold runtime, coarse-step advance, reused world id).
- **Non-triggers:** a turn that changes only `Width`, `WardLevel` or stocks performs zero rebuilds.
- **Order-independent:** a claim and a bank-point activation landing in the same turn give the same
  trees whichever the fixture resolves first (both orders).
- **Seen when:** a hostile legion marching into a sector in `Movement` is visible at that turn's L0; a
  claim in `Snapshot` is visible at the next turn's L0, and no flow runs between them.
- **Traversal rules:** deep and one-way lanes carry nothing; unheld ground is open; a contested own
  sector is a roadblock; foreign ground is closed until `passage` is granted.
- **Ties:** equal-cost bank points resolve to the lower sector id; equal-cost parallel lanes to the lower
  lane id.

Verification boundary: `FusionRpg.Core.Tests` (World/Logistics); `FusionRpg.Guard.Tests` for
`routing-guard`.

## Acceptance (contract)

1. Cached trees equal a fresh computation on every turn (property test).
2. Each trigger T1–T12 has a test; the six key-set triggers (T5, T7, T8, T10, T11, T12) assert the new
   key's answer at the first L0 after the change.
3. A turn with no key change performs zero rebuilds.
4. A same-turn claim and bank-point activation are order-independent.
5. No file of this module references `ReconnectionCost` (covered by `routing-guard`).
6. **Memo edges:** each of E1–E4 has a test — a rolled-back turn re-run on the pre-turn world, a cold
   runtime, a world advanced by a coarse step, and a reused world id — and each ends with trees equal to a
   fresh computation.

## Hard edges

- **Ruleset / goldens:** none. The cache is a memo; it changes no output.
- **Deviation from the approved map:** the hashed graph-version counter and its fingerprint cross-check
  are replaced by the exact topology key (§Design 3). Reported to the owner.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `PathCache.Next(faction, destinationKey, sector)` → (lane, sector) or none | `transit-buffer` (movement), `forecast-facts`, `fleet` `trade-route-order` (its point query, fleet ask A9) |
| `PathCache.Dist(...)`, `PathCache.Root(...)` | `lane-flow` (transit time, destination), `auto-banking` (nearest bank point) |
| `PathCache.RebuildCount` (runtime, never hashed) | tests, `logistics-bench` |

## Boundaries

- **Always:** read inputs only through the key; stable ordinal order everywhere.
- **Ask first:** a second traversal lens for goods; caching anything outside `LogisticsRuntime`.
- **Never:** `ReconnectionCost`; a copy of `LaneGraph.IsTraversable`; hashing or persisting the cache.

## Design-gate checklist

```
[x] Subsystems: world topology, movement/supply traversal, turn engine (L0).
[~] Session boundary: covered by tasks/sessions/trade-network-idea-20260919.json;
    session-boundary-check.py not run (docs only).
[~] Read this session: as in spec-logistics-phase.md, plus spec-world-movement.md:150 (in context).
    Gap: spec-world-topology.md not read this session.
[x] decisions.md: no lock on goods routing.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run; no HIGH finding left.
[x] Verified against code: LaneGraph's predicate and ordering, LaneCost's narrowing, SupplyGraph's
    roadblock rule, both sector-owner writers (a battle writes only a slot owner), ReconnectionCost's
    callers.
[x] Surrounding sections read: LaneGraph's lens doc; SupplyGraph's "never cached" doc.
[x] Constraints tested, not assumed: none claimed.
[x] §2 invariants: none contradicted.
[x] Corrections propagated: the counter → key deviation is recorded here, in
    spec-logistics-canonical.md, and in the session report.
[x] No population pinned.
[x] Event-refreshed cache (§2.16): twelve triggers enumerated, six key-set edges named, plus the memo's
    four lifetime edges (E1-E4), one test each; the trigger set was derived from the search's inputs, not
    copied from SupplyGraph's (T11, T12, E1-E4 added in the audit of 2026-09-20).
[x] Orderings: same-turn claim + activation tested in both orders.
[x] Actor magnitudes: none.
[x] No SOLID fork: LaneGraph's predicate and LaneCost are reused, not copied.
[x] Registry row: routing-guard's row is trade-foundation's; nothing new owed here.
```
