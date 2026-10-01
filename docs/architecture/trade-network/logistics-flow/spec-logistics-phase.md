# Spec: `logistics-phase`

**Status: written against code 2026-09-19** (branch `features/mega-merge`, `b82a4098`). Every
`file:line` below was opened in this session. Module id `logistics-phase`, row 1 of the
[logistics-flow map](../logistics-flow-map.md) (wave 1; depends on `trade-foundation` `world-stamp`
and `sector-yield` `banking-fact`). Ideal: [trade-network-ideal.md](../../trade-network-ideal.md)
§3 principles 14, 17, 18; §8.7 (*where it runs*); §9.2. Owner decision recorded in the map
(2026-09-19): `sector-yield` `banking-fact` creates the `Logistics` phase; **this program owns the flow
steps, their order and the `trade.logistics` flag** (umbrella [trade-network-map.md](../../trade-network-map.md)
§1a CM4). House style: [spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Objective

Give the `Logistics` phase its flow steps and one fixed, tested order, and make every one of them run
only on a world whose stamp grants the flag of the **wave that ships it**. This module and
`logistics-canonical` are wave 1 and carry `trade.logistics`; later waves carry their own flags
(`trade.logisticsLanes`, `trade.logisticsPolicy`, `trade.laneLossPower`) — round 6 C1, rows 5, 6, 7 and 23
of [../landing-order.md](../landing-order.md) §2. A single `trade.logistics` over all four waves was the
audit's C1 defect: a world stamped after wave 1 would gain lane loss, transit buffers and the refine step
mid-life when waves 2 and 3 merged. The module owns no mechanics of its own: it is the sequencer and the
gate. Every other logistics-flow module plugs a step into the slot this module
defines, and nothing plugs in anywhere else.

Success looks like: a world stamped legacy or `trade.bankingPhase`-only produces, turn for turn, the
same state hash it produced before this module; a world stamped `trade.logistics` runs this wave's steps in
exactly this order every turn; and swapping two steps in code fails a test.

## Locked anchors

- **One phase in the one turn engine** (ideal §3 principle 17). No second turn loop, no second phase.
  `Step` runs ten phases today (`gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:191-207`, asserted by
  `gk-core/tests/FusionRpg.Core.Tests/World/TurnEngineTests.cs:107`). `banking-fact` adds the eleventh,
  `Logistics`, between `Production` (`TurnEngine.cs:196`) and `Growth` (`TurnEngine.cs:197`), and
  amends the `decisions.md` phase-order row in that change. This module adds calls inside that method.
- **The stamp is the gate, never the global constant.** `RulesetVersion` is one process-wide
  constant, 13 (`gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:125`; round 5 X6), and a stored turn's
  **report** stops being re-derived the moment it moves (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:759-760`
  returns `null` for a trimmed report logged under another ruleset). Gating logistics on the constant
  would therefore change every world's rules at once, old and new alike. `trade-foundation` `world-stamp` makes the per-world
  stamp the gate and its capability flags the rule switch (map C2; trade-foundation-map §2.4). This
  module registers the flag `trade.logistics` in that closed vocabulary (*"each flag is added by the
  sub-program that ships its behaviour"*, trade-foundation-map §2.4). **The flag's row is born with one
  `RulesetVersion` bump** (`trade-foundation/spec-world-stamp.md` §2, "The bump is mandatory"): the bump
  does not gate old worlds — their stamps do — but without it the row would sit at the current ruleset and
  be granted to worlds stamped before logistics existed. Its only cost is that trimmed turn reports logged
  before the bump are no longer re-derived; no world stops playing and no legacy hash moves. *(Corrected
  in the audit of 2026-09-20: this anchor said the constant never moves.)*
- **The engine writes nowhere but the report** (`gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs:33-35`).
  Every step is a pure function of `(state, revealed commands, seed, tuning)`.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| The phase pipeline: each phase is a static method threading an immutable `WorldState` | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:168-209` |
| Phase names are constants; the report records the order they ran | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:127-157`; `gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs:37-45` |
| The phase-list test pins the ten names in order | `gk-core/tests/FusionRpg.Core.Tests/World/TurnEngineTests.cs:107-108` |
| Production is one slot shared by several faucets — the precedent for one phase, several steps | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:302-314` |
| `Step` already takes optional injected collaborators (`resolver`, `powerTuning`) | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:168-170` |
| Two production callers of `Step`: the turn commit and the replay | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:601`, `:773` |
| Clock and RNG APIs are banned in `World`, `Battle`, `Effects` by a source scan | `gk-core/tests/FusionRpg.Guard.Tests/WorldDeterminismGuardTests.cs:39-47`, `:253-266` |

### Wiring gap

| Gap | Owner |
|---|---|
| `rpg_worlds.ruleset_version` exists (default 1) and world creation writes the literal 1; nothing reads it as a stamp | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:31`, `:244` — `trade-foundation` `world-stamp` wires it |

### Real gap (this module closes it)

| Gap | What this module builds |
|---|---|
| No `trade.logistics` flag | The flag, registered in `world-stamp`'s closed capability registry |
| No step order inside `Logistics` | `LogisticsSteps.Run` — the ordered step list below, one call per step |
| No runtime home for the path cache and the phase's scratch buffers | `LogisticsRuntime`, an optional `Step` collaborator (§Design 3) |

## Design

### 1. The step order (a contract)

Inside `Logistics`, on a world whose stamp grants `trade.logistics`, `LogisticsSteps.Run` calls, in
this order, each step reading the previous step's output:

| # | Step | Owning module | What it does |
|---|---|---|---|
| L0 | Refresh | `path-cache` | Compare the topology key; rebuild the path trees only if it moved |
| L1 | Arrivals | `transit-buffer` (+ `rift-trade` `crossing-handoff` rift arrivals, a reserved sub-step) | Deliver packets that reached a valid destination last turn, up to the destination's room; return cleared-route packets to their source. Rift arrivals land in the same step (rift-trade ask A11) |
| L2 | *(reserved)* load / unload | `fleet` `carried-goods` | Caravans load and unload at depots (fleet map module 1). Empty until `fleet` lands |
| L3 | Banking | `sector-yield` `banking-fact` | Goods in a bank point's warehouse leave the map, up to the Counting House tier's rate and above any hold (round 4; not this program's step — its position is fixed here) |
| L4 | Delivery overflow | `transit-buffer` | Packets still at the door first unload into room banking freed; what still cannot unload wastes `warehouse.deliveryOverflowWasteMilli` of itself |
| L4r | *(reserved)* rift departures | `rift-trade` `crossing-handoff` | Goods leave for another world after banking and before the lane-flow pass (rift-trade ask A11). Empty until `rift-trade` lands |
| L5 | Flow | `lane-flow` (+ `transit-buffer` movement, `auto-banking` destinations) | Departures under lane capacity, then movement of every packet along its route |
| L6 | Loss | `lane-loss` | Loss on every packet for each lane it occupied this turn |
| L7 | Refine | `construction-chain` | Working refineries turn rubble into ironwork |
| L8 | Facts | `logistics-facts` | The turn's logistics records become report entries, in a fixed order |
| A1 | *(after)* quote and settlement | `exchange` `order-book` | Its own pass, after the flow steps (ideal §8.7; exchange-map E-A3) |
| A2 | *(after)* clan economy | `counterparties` `clan-economy` | Clan consumption, **after** settlement (counterparties ask A12) |

On a world stamped `trade.bankingPhase` but not `trade.logistics`, only L3 runs — exactly the phase
`banking-fact`'s slot half shipped (and while `banking-fact`'s **step** half waits on save identity, round 6
C3, L3 is present and empty: goods reach a bank point and stay there). On a legacy stamp, nothing in this
module runs. The reserved rows (L1's rift sub-step, L2, L4r, A1, A2) are positions this module fixes and
other programs fill; each runs only under **its own wave's** capability flag — which is why the order table
is safe to fix now and fill later: a position is not a grant.

**One change from the map's draft order, and why.** The approved map lists *arrivals → delivery
overflow → banking*. This spec orders **banking before overflow** (L3 before L4). With overflow first, a
delivery that lands on a full bank point wastes a fraction before banking empties the warehouse the same
turn — so a bank point's warehouse capacity would destroy goods that were about to leave the map, and the
waste would be pure noise in the report. With banking first, L4 unloads waiting packets into the room
banking just freed before anything wastes, so a bank point overflows only when deliveries outrun its
Counting House tier's banking rate and its storage together (round 4 made banking rate-limited; the
first draft's *"a bank point never overflows"* no longer holds and is withdrawn). The map's own rule —
*"only deliveries waste"* (ideal §8.2) — is unchanged. The map's phase-internal order is corrected to this
table in the same reconciliation (logistics-flow-map, reconciliation 2026-09-19).

### 2. The gate

`LogisticsSteps.Run(world, report, commands, turn, runtime)` first reads the stamp's capability set
through `world-stamp`'s reader. The flag test happens **once per turn at phase entry**, never per
step, so no step can run on a world whose stamp denies it. The flag vocabulary is closed and its
cardinality is a reviewed change (`world-stamp` owns the registry; this module adds one member).

### 3. `LogisticsRuntime` — where the cache and scratch live

`Step` is a static function (`TurnEngine.cs:168`). The path cache and the phase's flat scratch arrays
must survive between turns to meet the zero-allocation and rebuild budgets (ideal §9.2 rules 3 and 7),
so they live in a `LogisticsRuntime` object passed to `Step` as one more optional collaborator, beside
`resolver` and `powerTuning`:

- **Default `null` → a fresh runtime for this call.** Correct, only slower: the cache is cold and every
  scratch array is allocated once. The replay caller (`RpgStore.WorldTurns.cs:773`) takes the default.
- **The commit caller** (`RpgStore.WorldTurns.cs:601`) passes the store's runtime for that world id,
  held in process memory, one per world. It is never persisted and never hashed.
- **Contract:** a runtime is a memo. Every output of `Step` is identical with a warm runtime, a cold
  one, or `null` (`path-cache`'s equivalence property is the proof). A runtime is not thread-safe; the
  store's commit path already serialises turns per world, and `forecast-facts` uses its own instance.

### 4. Determinism

- Each step iterates in stable ordinal order (sectors, lanes, factions, routes by id; packets by
  route id, then departure turn). No step reads a clock, `System.Random`, or a Data-side store.
- No step consumes the turn's RNG stream. Logistics is deterministic arithmetic (lane loss is a
  fraction, ideal §8.4), so adding the phase cannot shift any later phase's random draws — `Growth`,
  `Pressure` and `Events` see the same seed as on a world without the flag.
- Report entries are appended only in L8, in a fixed order (§`logistics-facts`), so the report's
  entry order is a function of state, never of which step noticed something first.

### 5. Zero allocation — the boundary

The ideal's target is *0 bytes allocated in the Logistics phase after warm-up* (§9.3). The engine's
state is immutable records (`gk-core/src/FusionRpg.Core/World/WorldState.cs:334-354`), and every phase that
changes a stock builds a new list (for example `gk-core/src/FusionRpg.Core/World/Siege/SiegeConstruction.cs:90-106`).
Writing a changed stock back therefore allocates, and a report entry is a record holding strings
(`gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs:31-32`). Literal zero for the whole phase is not reachable
without replacing the engine's state model, which this program does not do.

The contract this spec sets instead (and `logistics-bench` asserts):

1. **The kernel allocates 0 bytes after warm-up**: L0's key compare, L1 and L4's selection, L5's flow
   and movement, L6's loss and L7's refine all run over `LogisticsRuntime`'s flat arrays.
2. **Write-back allocates in proportion to rows that changed** — sectors whose stock moved, routes
   whose buffer moved, entries written — and never in proportion to quantities. Multiplying every stock
   by 1000 changes no allocation.

This is a contradiction with ideal §9.3 as written; it is reported, not hidden.

## Tunables

None owned. The phase reads no number; each step's module owns its keys.

## Numeric types

None introduced. Each step's module states its own.

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World.TurnEngineTests|FullyQualifiedName~World.Logistics"
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~WorldTurnCommit"
dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~WorldDeterminismGuard"
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <session id>
```

## Structure

```
src/FusionRpg.Core/World/Logistics/LogisticsSteps.cs     (new) — Run(): gate + L0..L8 in order
src/FusionRpg.Core/World/Logistics/LogisticsRuntime.cs   (new) — the memo: path cache + scratch
gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs              MODIFIED — Step gains `LogisticsRuntime? logistics = null`;
                                                          the Logistics method banking-fact adds calls LogisticsSteps.Run
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs         MODIFIED — commit path passes the per-world runtime
the world-stamp capability registry                       MODIFIED — + `trade.logistics`
tests/FusionRpg.Core.Tests/World/Logistics/LogisticsPhaseTests.cs (new)
```

## Testing strategy

- **Gate:** the same fixture world, three stamps (legacy, `trade.bankingPhase`, `trade.logistics`),
  twenty turns each. Legacy and phase-slot-only hash byte-identically to the same world run before
  this module landed; the logistics stamp diverges only when goods exist off a bank point.
- **Order is a contract:** an instrumented runtime records step ids as they run; the test asserts the
  exact sequence L0…L8. Swapping two calls in `LogisticsSteps.Run` fails it.
- **Runtime is a memo:** a scripted run with a warm runtime, a cold runtime per turn, and `null` per
  turn produce identical hashes and identical reports every turn.
- **Coexistence, order-independent:** legacy-, sector-yield- and logistics-stamped worlds created in
  one in-memory store in all six creation orders; every world replays byte-identically in each order.
- **Determinism guard:** every file under `src/FusionRpg.Core/World/Logistics/` is already inside the
  scanned `World` root (`WorldDeterminismGuardTests.cs:253-266`); no new guard is needed, one assertion
  proves the directory is covered.

Verification boundary: `verify-change.py` with the changed paths. This module crosses Core and Data
(the runtime is passed from the store), so the full suite runs once at module end (AGENTS.md
*Verification boundary*, point 2).

## Acceptance (contract)

1. A world without `trade.logistics` produces the same state hash, turn for turn, as before this
   module; L3 behaves exactly as `banking-fact` alone.
2. With the flag, L0…L8 run in the stated order every turn; the order is asserted, not inferred.
3. Every step is a pure function of state, revealed commands, seed and tuning; none reads a clock,
   ambient state or a Data-side store.
4. `Step` with a warm runtime, a cold runtime and `null` returns identical results.
5. Worlds of all three stamps coexist in one store and replay independent of creation order.
6. **Every goods move is recorded.** Over a scripted logistics run, `trade-foundation` `stock-deltas`'
   reconciliation is empty every turn for every located good, `rubble` and `ironwork`, with goods in
   transit counted on their route holder (`r:`); a step that moves goods without recording fails it. The
   recording is each step owner's (`transit-buffer`, `lane-loss`, `construction-chain`); this module
   asserts the whole phase closes.
7. **Ruleset:** `trade.logistics`' `IntroducedAtRuleset` is the value this change bumps
   `TurnEngine.RulesetVersion` to; a world stamped before it is not granted the flag
   (`spec-world-stamp.md` acceptance 11). This wave takes **one** bump, shared with `logistics-canonical`;
   waves 2, 3 and 5 take their own (round 6 C1).

## Hard edges

- **Ruleset stamp:** the flag is the gate (map C2). `trade-foundation` `world-stamp` §2 is that policy:
  each new capability row carries the `RulesetVersion` its change bumps to, so this module bumps the
  constant once, for `trade.logistics`, in the change that registers the row, and gates nothing on the
  constant itself. **A later logistics wave never widens `trade.logistics`** — it registers its own flag
  and bumps again (round 6 C1). The bump order for the family is
  [../landing-order.md](../landing-order.md) §2's, and a lane that bumps rebases onto the latest constant
  and takes the next integer.
- **Goldens:** no existing golden moves (acceptance 1 is the proof). New logistics-stamped fixtures are
  new files, not re-blessed ones.
- **Phase list:** the phase list itself is `banking-fact`'s change; this module adds no phase name.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| Step slots L0–L8 and their order | every logistics-flow module; `fleet` (L2); `exchange`, `counterparties` (after L8) |
| `trade.logistics` flag | `fleet`, `rift-trade`, `exchange` (gate their own steps on it or a later flag) |
| `LogisticsRuntime` | `path-cache`, `lane-flow`, `logistics-bench`, `forecast-facts` |

## Boundaries

- **Always:** one flag test per turn at phase entry; steps only inside `LogisticsSteps.Run`.
- **Ask first:** moving a step between phases; adding a step outside the table above.
- **Never:** a second phase; gating a step on the global `RulesetVersion` instead of the stamp; a
  capability row registered at the current ruleset without its bump; a step that reads a clock, RNG or
  store; persisting or hashing `LogisticsRuntime`.

## Design-gate checklist

```
[x] Subsystems: world turn engine (phase sequencing), world stamp (capability flag), Data commit path.
[~] Session boundary: record tasks/sessions/trade-network-idea-20260919.json covers
    docs/architecture/trade-network/**. scripts/session-boundary-check.py not run by this session
    (docs only, no commit); the record's notes log its known crossing.
[~] Read this session: logistics-flow-map.md, trade-network-map.md (incl. §1a), trade-network-ideal.md
    §3, §8, §9, §13-§15, sector-yield-map.md, fleet-map.md (§1-§3, escort and Q1 rows),
    trade-foundation-map.md §2.4, DESIGN-GATE.md, PRINCIPLES.md §5-§6 and §11, tunables-ssot.md
    §1-§3 and §7, ssot-power-scale.md §9.4, §10.2, §10.4, §11 (§11.3, §11.6), empire-resource-ssot.md
    §4, research/perf/02-world-graph-write.md. Gap: software-architecture.md, data-architecture.md,
    economy-principles.md, world-map-program.md and the world-map-runtime specs were not read in
    full this session; perf-probe-plan.md by heading only.
[x] decisions.md lock: the phase-order row is amended by banking-fact (map C1, ask A2); this module
    adds no phase.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file; no HIGH finding left.
[x] Verified against code: Step's signature and callers, the phase list test, the report shape, the
    immutable state model behind the zero-allocation boundary.
[x] Surrounding sections read: Step's doc comment, the Assaults no-bump note, TurnReport's class doc.
[x] Constraints tested, not assumed: none claimed; "no golden moves" is acceptance 1, to be proven.
[~] §2 invariants: none contradicted. One contradiction with ideal §9.3 named (whole-phase zero
    allocation is not reachable on immutable state; the kernel is).
[x] Corrections propagated: the L3/L4 order change is recorded here and in the session report; the
    map is not re-edited beyond its approval record.
[x] No population pinned. The step list is a closed sequence this module owns.
[x] Event-refreshed cache: none here (path-cache owns its trigger set).
[x] Orderings: stamp coexistence tested in all creation orders.
[x] Actor magnitudes: none.
[x] No SOLID fork: one phase, one sequencer, collaborators injected like `resolver`.
[ ] Registry row: the "steps only inside LogisticsSteps.Run" rule needs a guard or an
    unguardableReason row in gk-core/scripts/enforcement-registry.v1.json when the code lands.
```
