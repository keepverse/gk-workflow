# Spec: `logistics-canonical`

**Status: written against code 2026-09-19** (branch `features/mega-merge`, `b82a4098`). Every
`file:line` below was opened in this session. Module id `logistics-canonical`, row 2 of the
[logistics-flow map](../logistics-flow-map.md) (wave 1; depends on `logistics-phase`). Ideal:
[trade-network-ideal.md](../../trade-network-ideal.md) §9.2 rules 6 and 8, §14b (*"a sparse canonical
form (non-zero entries only) and one packed row per sector"*). House style:
[spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Objective

Own the hashed and persisted form of every piece of **state** logistics-flow adds, and nothing that can
be recomputed. Two records, both sparse:

1. **Transit packets** — goods in motion on a route (the shape `transit-buffer` defines).
2. **Route policies** — a faction's standing `route-set` for one (source sector, good) (the shape
   `auto-banking` defines).

Success looks like: a world with no packets and no policies writes byte-identical canonical text to
today's; hashing and persistence cost grow with what is actually moving; save → load → hash
round-trips exactly.

## Locked anchors

- **No storage of anything recomputable** (`docs/architecture/world/spec-world-movement.md:150`: *"No
  storage of anything recomputable — `banner element`, `in supply`, and `claimable` are all
  computed"*). A value that is a pure function of hashed state is computed, never stored.
- **Conditional canonical rows keep old hashes still.** A new field at its zero value writes nothing,
  the precedent the rubble and ironwork rows set (`gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:119-128`).
- **The diff writer writes only changed rows** (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldGraphDiff.cs:45-54`),
  and a debug equivalence check re-reads the graph and compares hashes (`:56-68`). Every new field must
  therefore load back, or that check fails — the write-only-field lesson is enforced, not assumed.

## Two deviations from the approved map, and why

The map lists three kinds of state here: a **graph-version counter**, per-route **transit buffers**, and
per-lane per-turn **flow records**. This spec keeps only the buffers (plus the route policies the map
assigns to `auto-banking` but stores "through `logistics-canonical`").

| Map item | Decision here | Reason |
|---|---|---|
| Hashed graph-version counter | **Not stored.** `path-cache` keeps the exact topology key it was built from inside `LogisticsRuntime` and compares it at L0 (see [spec-path-cache.md](spec-path-cache.md)) | A counter bumped at mutation sites is derived state that can only be *wrong* (a forgotten bump), and it would spread one-line edits into `ClaimResolver`, `MovementPhase`, `LoamPhases`, `BuildResolver` and two sibling programs. The key comparison is exact, allocation-free and cannot miss a trigger that feeds the path computation |
| Per-lane per-turn flow records | **Not stored.** Utilisation and bottleneck reasons are report entries (`logistics-facts`), and the next-turn view is `forecast-facts`' dry run | They are outputs of the step, recomputable from the state before it. The report is already the log (`gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs:33-35`) |

Both deviations remove hashed state; neither adds any. They are reported to the owner.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Canonical writer: one text row per record, fixed column order | `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:40-67` |
| Conditional rows for sparse stocks (zero writes nothing) | `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:119-128` |
| The hash is SHA-256 over the whole canonical text, every turn | `gk-core/src/FusionRpg.Core/World/Turn/StateHasher.cs:15-24` |
| Diff writer, one function per table, plus the read-back equivalence check | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldGraphDiff.cs:45-68` |
| Full write and load of the world graph | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:272`, `:461` |
| New tables keyed by world instance, no owner column, when the row belongs to a world graph | `docs/architecture/solid-enforcement/spec-save-identity.md:594-603` (instance-keyed class) |

### Wiring gap

None.

### Real gap (this module closes it)

| Gap | What this module builds |
|---|---|
| No place in `WorldState` for goods in motion or route policies | Two ordered lists on `WorldState` (§Design 1) |
| No canonical rows for them | Two conditional row kinds (§Design 2) |
| No persistence | Two tables, packed per route; diff and load functions (§Design 3) |

## Design

### 1. State shape

```csharp
// On WorldState, beside Entities. Both lists are ordered and empty by default.
public IReadOnlyList<TransitPacket> Transit { get; init; } = Array.Empty<TransitPacket>();
public IReadOnlyList<RoutePolicy>   RoutePolicies { get; init; } = Array.Empty<RoutePolicy>();

public sealed record TransitPacket
{
    public string FactionId { get; init; } = "";
    public string SourceSectorId { get; init; } = "";   // route key part 1
    public string GoodId { get; init; } = "";           // route key part 2
    public int DepartTurn { get; init; }                // packet key within the route
    public long Qty { get; init; }                      // goods, whole units
    public long Load { get; init; }                     // load units fixed at departure (lane-flow)
    public string LaneId { get; init; } = "";           // the lane it is on
    public string TowardSectorId { get; init; } = "";   // the end it is heading to
    public long ProgressCost { get; init; }             // LaneCost units along LaneId
    public TransitStatus Status { get; init; }          // Moving, AtDoor, Stranded, Returning
}

public sealed record RoutePolicy
{
    public string FactionId { get; init; } = "";
    public string SourceSectorId { get; init; } = "";
    public string GoodId { get; init; } = "";
    public string DestinationSectorId { get; init; } = "";
    public int Priority { get; init; }
}
```

`TransitStatus` is a closed enum, persisted and hashed **by name** (the `SectorPhase` precedent,
`gk-core/src/FusionRpg.Core/World/WorldState.cs:5-15`). Ordering: `Transit` by (`FactionId`, `SourceSectorId`,
`GoodId`, `DepartTurn`) ordinal; `RoutePolicies` by (`FactionId`, `SourceSectorId`, `GoodId`). A route
has at most one policy. `Qty > 0` for every stored packet — an emptied packet is removed, never kept at
zero.

### 2. Canonical rows

Appended after the rubble/ironwork rows, conditional by construction (an empty list writes nothing):

```
transit      faction, source, good, departTurn, qty, load, lane, toward, progress, status
route-policy faction, source, good, destination, priority
```

The canonical text of a world with no packets and no policies is byte-identical to today's. Adding a
good id that is zero everywhere writes nothing, so text length is invariant under unused goods.

### 3. Persistence — packed per route, through the diff writer

| Table | Key | Payload |
|---|---|---|
| `rpg_world_transit` | `(world_id, faction_id, source_sector_id, good_id)` | `packets_json` — the route's packets, ordered by `DepartTurn` |
| `rpg_world_route_policies` | `(world_id, faction_id, source_sector_id, good_id)` | `destination_sector_id`, `priority` |

Both are world-graph instance tables (no `save_id`/`empire_id` column — the world id is the instance,
the same class as the existing world-graph tables; `spec-save-identity.md:594-603`). One packed row
per route keeps a turn's write proportional to routes whose packets changed (ideal §14b; §9.2 rule 8).
`DiffTransit` and `DiffRoutePolicies` join the seven existing diff functions and follow their contract:
DELETE a row that vanished, INSERT OR REPLACE a row whose bytes changed, nothing for an unchanged row.
`LoadWorldGraphUnlocked` and `WriteWorldGraphUnlocked` read and write both tables, so the equivalence
check at `RpgStore.WorldGraphDiff.cs:56-68` covers them. All SQL stays in `FusionRpg.Data`.

### 4. Determinism and numbers

Canonical rows are written in the lists' stable order. `Qty`, `Load` and `ProgressCost` are `long`;
the canonical writer formats them invariant-culture like every other `long` field. No `double` is
stored.

## Tunables

None.

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World.Logistics.LogisticsCanonical"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~WorldGraphDiff|FullyQualifiedName~WorldStore"
python gk-core/scripts/guard-dal.py
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <session id>
```

## Structure

```
gk-core/src/FusionRpg.Core/World/WorldState.cs                 MODIFIED — Transit, RoutePolicies (+ records, TransitStatus)
gk-core/src/FusionRpg.Core/World/WorldCanonical.cs             MODIFIED — two conditional row kinds
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs            MODIFIED — two tables; write + load
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldGraphDiff.cs   MODIFIED — DiffTransit, DiffRoutePolicies
tests/FusionRpg.Core.Tests/World/Logistics/LogisticsCanonicalTests.cs   (new)
gk-core/tests/FusionRpg.Data.Tests/  (WorldGraphDiff / WorldStore test classes)  EXTEND
```

## Testing strategy

- **Invisible at zero:** every existing world fixture hashes byte-identically with both lists empty.
- **Sparse:** two worlds differing only in a good id that is zero everywhere produce identical text.
- **Round trip:** a world with packets in every `TransitStatus` and two policies saves, loads and
  hashes identically (in-memory store, per the test-substrate rule).
- **Diff proportional to change:** a turn that changes one route's packets writes exactly that route's
  `rpg_world_transit` row and no other transit or policy row (row-count probe on the in-memory store).
- **Equivalence check covers the new tables:** a deliberately broken loader (drops `status`) fails the
  debug read-back hash check — proves the check sees the new rows.
- **Invariant:** constructing a packet with `Qty <= 0` in the canonical writer throws.

Verification boundary: Core (canonical) plus Data (tables, diff) — `verify-change.py` with the changed
paths selects both; `guard-dal.py` for the SQL.

## Acceptance (contract)

1. A world with no packets and no policies writes byte-identical canonical text to today's.
2. Canonical length is invariant under adding goods that are zero everywhere.
3. Save → load → hash round-trips byte-identically for a world with packets and policies.
4. A turn that changes one route writes exactly that route's row; unchanged routes write nothing.
5. No graph-version counter and no flow record is hashed or persisted (a source scan of
   `WorldCanonical.cs` for row kinds asserts the two new kinds and only those).

## Hard edges

- **Schema:** two new tables, created by the store's existing schema-setup path; no migration of any
  existing table and no backfill (both start empty on every existing world).
- **Goldens:** none move (acceptance 1).
- **Ruleset:** this module ships in `logistics-flow` **wave 1** and shares that wave's single
  `RulesetVersion` bump with `logistics-phase`, which registers `trade.logistics` (round 6 C1; row 5 of
  [../landing-order.md](../landing-order.md) §2). It registers no row of its own and takes no second bump.
  The canonical rows only appear on worlds whose `trade.logistics` steps write packets.
- **Append slot (audit M3).** Four modules append a conditional row after the `sector-ironwork` loop
  (`gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:123-129`), and the canonical text is hashed, so their
  relative order is part of every later golden. The family order is fixed once, in
  [../landing-order.md](../landing-order.md) §4: `world-stamp`'s stamp row, `sector-yield` `located-stock`,
  **this module**, `fleet` `carried-goods`. The rule each spec states is *"after the last conditional row
  present at landing"* — never an absolute position — and **only one module at a time appends**.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `WorldState.Transit`, `TransitPacket`, `TransitStatus` | `transit-buffer`, `lane-flow`, `lane-loss`, `logistics-facts`, `forecast-facts`; `fleet` (reads, never writes, packets) |
| `WorldState.RoutePolicies`, `RoutePolicy` | `auto-banking` (writes), `path-cache` (reads for its key), `construction-chain` |

## Boundaries

- **Always:** conditional rows; name-persisted enums; one packed row per route.
- **Ask first:** storing any derived value (a counter, a total, a utilisation).
- **Never:** SQL outside `FusionRpg.Data`; a column-appended change to an existing canonical row kind;
  a zero-quantity packet in state.

## Design-gate checklist

```
[x] Subsystems: world state model, canonical hash, world store (schema, diff writer).
[~] Session boundary: record tasks/sessions/trade-network-idea-20260919.json covers this path;
    session-boundary-check.py not run by this session (docs only).
[~] Read this session: as listed in spec-logistics-phase.md, plus spec-save-identity.md §"The rule
    for a table created after this module" and research/perf/02-world-graph-write.md. Gap:
    data-architecture.md not read in full.
[x] decisions.md: no lock on logistics state; World store rows unchanged.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run; no HIGH finding left.
[x] Verified against code: the conditional-row precedent, the diff writer's function list and its
    read-back check, the world-graph write/load entry points.
[x] Surrounding sections read: WorldCanonical's rubble/ironwork comment; the diff writer's doc.
[x] Constraints tested, not assumed: no golden claim beyond acceptance 1, which a test proves.
[x] §2 invariants: none contradicted (SQL in Data; no derived storage).
[x] Corrections propagated: the two deviations are stated here, in spec-path-cache.md, and in the
    session report.
[x] No population pinned: the two row kinds are a closed vocabulary this module owns.
[x] Event-refreshed cache: not here.
[x] Orderings: list order is total and stated.
[x] Actor magnitudes: none.
[x] No SOLID fork: the existing canonical writer and diff writer are extended, not copied.
[x] Registry row: none owed by this module.
```
