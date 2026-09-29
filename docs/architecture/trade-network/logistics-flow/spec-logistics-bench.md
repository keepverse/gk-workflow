# Spec: `logistics-bench`

**Status: written against code 2026-09-19** (branch `features/mega-merge`, `b82a4098`). Every
`file:line` below was opened in this session. Module id `logistics-bench`, row 12 of the
[logistics-flow map](../logistics-flow-map.md) (wave 4, **the gate** — the sub-program is not done until it
is green; depends on every module above and `trade-foundation` `step-benchmark`, `synthetic-graph`).
Ideal: [trade-network-ideal.md](../../trade-network-ideal.md) §9.2 rules 1, 2, 3, 7; §9.3 budgets; §14b
(*the budget covers the whole End Turn, not only the Logistics phase*). House style:
[spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Objective

Prove the performance design instead of asserting it. Two kinds of evidence, kept apart on purpose:

1. **Properties CI enforces** — in the ordinary test suite: the kernel allocates nothing after warm-up;
   stock volume changes no allocation and no iteration count; a turn with no topology change rebuilds
   nothing.
2. **Timings reported against targets** — in the Release-only bench: the Logistics phase at medium and
   giant tiers, a path-cache rebuild at giant, and the whole `Step` with the phase on and off.

Success looks like: the three properties are green in CI, and the bench report prints every §9.3 target
beside its reading. A missed target is a finding to fix, never a number bumped.

## Locked anchors

- **Nothing times a full `Step` today, and clocks are banned in the simulation trees**
  (`gk-core/tests/FusionRpg.Guard.Tests/WorldDeterminismGuardTests.cs:39-47`, `:253-266`). Timing lives in
  `gk-core/tests/FusionRpg.Bench`, outside `gk-core/src/FusionRpg.Core/World`. `trade-foundation` `step-benchmark` builds
  the `Step` harness; this module adds the logistics cases to it.
- **Allocation is measured with `GC.GetAllocatedBytesForCurrentThread` after a warm-up** — the bench
  precedent (`gk-core/tests/FusionRpg.Bench/AtomFormBench.cs:118-141`) and the in-suite precedent that asserts
  exactly 0 (`gk-core/tests/FusionRpg.Core.Tests/Actions/ActionCatalogTests.cs:405-411`).
- **The zero-allocation boundary is the kernel** (`spec-logistics-phase.md` §Design 5): the engine's state
  is immutable records, so writing a changed stock back allocates; that allocation must be proportional to
  rows that changed, never to quantities.
- **Readings are readings.** A timing is printed, not asserted — machine speed is not a contract
  (DESIGN-GATE §3 rule 7's spirit: assert the contract, report the scale).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| The Release-only bench project and its entry point | `gk-core/tests/FusionRpg.Bench/Program.cs:1-40` |
| Allocation measurement after warm-up | `gk-core/tests/FusionRpg.Bench/AtomFormBench.cs:118-141` |
| An in-suite zero-allocation assertion | `gk-core/tests/FusionRpg.Core.Tests/Actions/ActionCatalogTests.cs:405-411` |
| A world-graph write bench and its recorded readings | `gk-core/tests/FusionRpg.Bench/WorldGraphWriteBench.cs`; `docs/research/perf/02-world-graph-write.md` |
| Declared world size tiers | `gk-core/src/FusionRpg.Core/World/WorldSizeCatalog.cs:28-58` |

### Wiring gap

None.

### Real gap (this module closes it)

The logistics allocation, invariance and rebuild tests; the logistics bench cases; the recorded readings.

## Design

### 1. In-suite properties (`FusionRpg.Core.Tests`, CI)

On `trade-foundation`'s synthetic graph at the giant tier (≤ 144 sectors, ≤ 500 routes, ≤ 40 goods,
goods in transit, bank points, policies, hostile presence on lanes — map ask A1):

- **Kernel allocates 0 bytes.** Run two turns to warm the runtime; then run the kernel (L0 compare, L1/L4
  selection, L5 flow and movement, L6 loss, L7 refine — `LogisticsSteps` exposes a kernel-only entry that
  records into the runtime without writing back) on the same state and assert
  `GC.GetAllocatedBytesForCurrentThread` moved by exactly 0.
- **Write-back is proportional to change.** The full phase's allocation on a world and on the same world
  with every stock and packet quantity × 1000 are equal.
- **Volume invariance of work.** An instrumented runtime counts loop iterations (routes visited, lanes
  walked, packets moved); × 1000 volume changes none of the counts.
- **Rebuild only on change.** A turn with no topology-key change performs zero rebuilds
  (`PathCache.RebuildCount`).

### 2. Bench cases (`gk-core/tests/FusionRpg.Bench`, Release, not in CI)

| Case | Target (ideal §9.3) |
|---|---|
| Logistics phase, medium (≤ 18 sectors) | ≤ 1 ms |
| Logistics phase, giant — p99 over the run | ≤ 10 ms |
| Path-cache rebuild, giant | ≤ 5 ms |
| Whole `Step`, giant, phase off vs on (hash and diff included, through `step-benchmark`) | reported, with the phase's share |
| `LogisticsForecast.For`, giant | reported (it is one `Step`) |

Median of several runs, the precedent's discipline. The report prints each reading beside its target and
the environment line. Readings are recorded in `docs/research/perf/03-logistics-flow.md` (new), next to
`02-world-graph-write.md`.

### 3. What a miss means

A target missed is a defect in the module that owns the slow step, filed and fixed there; the bench's
targets are the ideal's and are not edited to pass. A reading that shows a target was mis-set (for
example, the phase dominated by write-back that the kernel cannot reach) is reported to the owner with
the numbers.

## Tunables

None. The tier sizes come from `trade-foundation` `synthetic-graph`.

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World.Logistics.LogisticsAllocation"
dotnet run -c Release --project tests\FusionRpg.Bench
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <session id>
```

## Structure

```
tests/FusionRpg.Core.Tests/World/Logistics/LogisticsAllocationTests.cs   (new) — the four properties
tests/FusionRpg.Bench/LogisticsBench.cs                                   (new) — the bench cases
gk-core/tests/FusionRpg.Bench/Program.cs                                          MODIFIED — one more section
docs/research/perf/03-logistics-flow.md                                   (new) — recorded readings
```

## Testing strategy

This module is tests. Its own check: each property test fails when its property is broken on purpose — a
`new List<>` inside the kernel fails the allocation test; a per-unit loop fails the invariance test; a
forced rebuild fails the rebuild test (mutation-style, run once when the module lands).

Verification boundary: `FusionRpg.Core.Tests` (World/Logistics). The bench is not in CI; this module is
the sub-program's last checkpoint, so the full suite runs once when it lands (AGENTS.md *Verification
boundary*, point 1).

**The bench file needs its own mapping (audit 2026-09-20).** `gk-core/tests/FusionRpg.Bench/**` has no fallback
row: `verify-change.ps1 -PlanOnly -AllowUnscoped -Paths gk-core/tests/FusionRpg.Bench/AtomFormBench.cs` stops with
*"VERIFICATION BOUNDARY MISSING"* (run in the audit). `trade-foundation` `step-benchmark` maps only its own
bench files (`spec-step-benchmark.md` Test plan) and `Program.cs`. This module adds an owner row
`logistics-bench` whose paths are `tests/FusionRpg.Bench/LogisticsBench.cs` and
`tests/FusionRpg.Core.Tests/World/Logistics/LogisticsAllocationTests.cs`, project `core`, verificationId
`core.logistics-bench` (the allocation tests carry that trait). `docs/research/perf/03-logistics-flow.md`
falls to the existing docs boundary.

**Tier sizes are read, not typed.** "Medium" and "giant" are `SyntheticGraph.Build(tier, seed)` at the
tier's tuned node range (`WorldSizeCatalog`, `spec-synthetic-graph.md` §2); the "≤ 144 sectors, ≤ 500
routes, ≤ 40 goods" figures above are the ideal's §9.3 envelope, printed beside the run's actual counts,
never asserted.

## Acceptance (contract)

1. After warm-up, the Logistics kernel on the giant synthetic graph allocates 0 bytes (asserted in CI).
2. × 1000 volume changes neither allocation nor iteration counts (asserted in CI).
3. A turn with no topology change performs zero path rebuilds (asserted in CI).
4. The bench prints medium and giant phase times, rebuild time, and whole-`Step` time with the phase on and
   off, each beside its §9.3 target, and the readings are recorded.

## Hard edges

- **Ruleset / goldens:** none.
- **Deviation from the map and the ideal:** the zero-allocation assertion covers the kernel, not the
  whole phase (`spec-logistics-phase.md` §Design 5). Reported.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| The recorded readings | `trade-foundation` `economy-report` and the umbrella's budget review; `fleet` and `exchange` add their passes' cases here when they land |

## Boundaries

- **Always:** properties in CI, timings in the bench; targets printed beside readings.
- **Ask first:** changing a §9.3 target.
- **Never:** a timing asserted in CI; a clock in `gk-core/src/FusionRpg.Core/World`; bumping a target to pass.

## Design-gate checklist

```
[x] Subsystems: performance (bench, allocation), turn engine (measured, not changed).
[~] Session boundary: covered by tasks/sessions/trade-network-idea-20260919.json;
    session-boundary-check.py not run (docs only).
[~] Read this session: research/perf/02-world-graph-write.md, the bench project, the in-suite
    allocation precedent. Gap: runbook/perf-probe-plan.md by heading only; research/perf/00-baseline.md
    not read (it covers the lawn hot path, not the world turn).
[x] decisions.md: no lock on world-turn budgets beyond the ideal's targets.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run; no HIGH finding left.
[x] Verified against code: the determinism guard's banned symbols and roots; both allocation precedents;
    the bench entry point.
[x] Surrounding sections read: AtomFormBench's allocation helper in full.
[x] Constraints tested, not assumed: all four properties are tests; no reading is claimed.
[~] §2 invariants: none contradicted; the whole-phase zero-allocation target is reported as unreachable
    on immutable state and replaced by the kernel property.
[x] Corrections propagated: stated here and in spec-logistics-phase.md.
[x] No population pinned: tier sizes are inputs, readings are printed.
[x] Event-refreshed cache: rebuild-only-on-change is property 3.
[x] Orderings: none.
[x] Actor magnitudes: none.
[x] No SOLID fork: trade-foundation's step-benchmark and synthetic-graph are reused, not copied.
[x] Registry row: none owed.
```
