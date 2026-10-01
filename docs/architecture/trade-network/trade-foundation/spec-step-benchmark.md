# Spec: `step-benchmark`

**Status: written against shipped code 2026-09-19.** Every `file:line` below was opened this session on
`features/mega-merge`. Module id `step-benchmark`, §2.2 of the
[trade-foundation map](../trade-foundation-map.md) (approved 2026-09-19; depends on `synthetic-graph`).
Ideal: [../../trade-network-ideal.md](../../trade-network-ideal.md) §9.1 ("nothing times a full
`TurnEngine.Step`"), §9.2 rule 1 and rule 7, §9.3 budgets.

## Objective

Make End Turn measurable before the `Logistics` phase exists. Time `TurnEngine.Step` as a whole and
per phase, with allocated bytes per phase, on synthetic `medium` and `giant` worlds under a scripted
command load, and print p50/p99. Timing uses **`PerfProbe` itself** — new `PerfSection` members
wrapped around each phase call — not a second timing facade. Nothing the probe records ever reaches
world state.

Success looks like: a Release run prints, per tier, a table of `world.step` and each phase's p50, p99
and bytes allocated, plus a verdict line per ideal §9.3 budget; the same world, commands and seed hash
identically with the probe on and off.

## Scope and non-goals

In scope: eleven `PerfSection` members; one `using` scope per phase call in `Step`; opt-in allocation
tracking in `PerfScope`; an xunit bench that prints; a Release bench entry; one verification-boundary
row.

Not in scope: asserting a timing in a pass/fail test; optimising any phase; server-side flushing of
world-phase counters (the server never ships its in-process `PerfProbe` windows today — only the
injector's arrive at `POST /api/perf`; a world-phase window endpoint is a later, separate change).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| `Step` calls ten phase functions in the locked order, then hashes | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:168-210` (calls `:191-207`, hash `:209`) |
| Phase names | `TurnEngine.cs:127-157` |
| `PerfSection` has 25 members; `SectionCount` is a structural const that must equal the member count; names are a parallel array | `gk-core/src/FusionRpg.Core/Diagnostics/PerfProbe.cs:6-41`, `:51`, `:53-80` |
| `Measure` returns an allocation-free struct scope; disabled probe returns an inert default | `PerfProbe.cs:108-112`, `:257-274` |
| Probe records count, total and max ticks only — no samples, no per-section allocation | `PerfProbe.cs:114-121`, `:172-251` |
| The `Stopwatch` lives in `Core/Diagnostics` | `PerfProbe.cs:1`, `:102`, `:112` |
| The determinism guard scans `Core/World`, `Core/Battle`, `Core/Effects` only; `Stopwatch` and `Environment.TickCount` are banned there; comment text is stripped | `gk-core/tests/FusionRpg.Guard.Tests/WorldDeterminismGuardTests.cs:39-49`, `:254-267` |
| Precedent for a probe scope inside a guarded tree | `gk-core/src/FusionRpg.Core/Effects/EffectBag.cs:362` |
| Bench precedent: an xunit class named `*Bench` that prints and never asserts timing; `coverage.py` excludes `*Bench` | `gk-core/tests/FusionRpg.Core.Tests/World/Topology/ReconnectionCostBench.cs:9-17`; `gk-core/scripts/coverage.py:63` |
| Release-only bench exe, runs every bench in sequence, no argument parsing | `gk-core/tests/FusionRpg.Bench/FusionRpg.Bench.csproj:3-11`; `gk-core/tests/FusionRpg.Bench/Program.cs:1-40` |

### Real gap

No bench references `TurnEngine` (the bench project holds `AtomFormBench.cs`, `WorldGraphWriteBench.cs`,
`Corpus.cs`, `Program.cs`). `PerfProbe` cannot report a percentile or a per-phase allocation.

### Found this session

`gk-core/tests/FusionRpg.Bench/**` has **no verification boundary**: `verify-change.ps1 -PlanOnly -AllowUnscoped
-Paths gk-core/tests/FusionRpg.Bench/WorldGraphWriteBench.cs` stops with *"VERIFICATION BOUNDARY MISSING"*.
This module maps the files it touches; the pre-existing bench files stay the gap of their owners.

## Design

### 1. Sections

Appended after `LawnMoveDrain = 24` (`PerfProbe.cs:40`), with the matching names and
`SectionCount` moved to 36 (structural: it must equal the member count, the existing comment's rule):

| Member | Name | Wraps |
|---|---|---|
| `WorldStep = 25` | `world.step` | the whole `Step` body |
| `WorldReveal = 26` … `WorldIntel = 35` | `world.reveal`, `world.movement`, `world.sieges`, `world.assaults`, `world.production`, `world.growth`, `world.pressure`, `world.events`, `world.snapshot`, `world.intel` | one call each at `TurnEngine.cs:191-207` |

The member order follows `TurnEngine.Phases`, so a reader maps one list to the other. A new phase (the
`Logistics` slot `sector-yield` creates) adds its section in the change that adds the phase.

### 2. The change inside `Step`

```csharp
using var _step = PerfProbe.Measure(PerfSection.WorldStep);
…
List<WorldCommand> revealed;
using (PerfProbe.Measure(PerfSection.WorldReveal)) revealed = Reveal(opening, commands, recovering, report);
```

One scope per phase call, nothing else. `Step`'s signature, return value, phase order and every phase
body are unchanged. The `Stopwatch` read happens inside `Core/Diagnostics`, so the guard's banned-symbol
scan sees no new symbol in `Core/World` and needs **no new exemption**.

### 3. Opt-in allocation tracking

`PerfProbe.TrackAllocations` (static bool, default `false`). When true, `PerfScope` captures
`GC.GetAllocatedBytesForCurrentThread()` at open and adds the difference to a per-section
`AllocBytes` counter on dispose; `SnapshotAndReset` reports `allocBytes` per section. When false, the
scope does exactly what it does today, so the injector's hot path pays one predictable branch. The
counter is thread-local by construction of the call it reads; the bench runs `Step` on one thread.

### 4. Samples and percentiles

`PerfProbe` stays an aggregate counter. The bench gets per-step samples by calling
`PerfProbe.SnapshotAndReset()` **after every `Step`** (it allocates, but outside `Step`), reading each
section's `totalMs` and `allocBytes` as one sample, and computing p50 and p99 over the run. The first
`warmupTurns` steps are discarded, so JIT and first-touch allocation do not pollute the percentile
(ideal §9.2 rule 7 counts allocation "after warm-up").

### 5. The two runs

- **xunit bench** — `tests/FusionRpg.Core.Tests/World/Turn/TurnStepBench.cs`. Builds `medium` and
  `giant` worlds with `SyntheticGraph.Build`, drives them with `SyntheticCampaign.Run`, prints the table
  through `ITestOutputHelper`. Timing is printed, never asserted.
- **Release bench** — `tests/FusionRpg.Bench/TurnStepBench.cs`, compiled against the same builder by
  source link (`<Compile Include="..\FusionRpg.Core.Tests\World\Synthetic\*.cs" LinkBase="Synthetic" />`
  in `FusionRpg.Bench.csproj`), so there is one builder, not two. `Program.cs` gains an optional
  `--only <name>` filter; with no argument it runs every bench as it does today. The Release run prints a
  verdict per ideal §9.3 line. Lines that name the `Logistics` phase print `n/a — phase not built`
  until `logistics-flow` lands; the whole-step line is the baseline those budgets are later read
  against. That output is evidence for `logistics-flow`'s gate, not a CI test.

### 6. Determinism

Nothing in `Step` reads the probe. The only new code in `Core/World` is `using` scopes whose `Dispose`
writes to static counters in `Core/Diagnostics`. The probe-on / probe-off equality test proves it.

## Tunables

None. `warmupTurns` and the scripted run length are bench inputs, not balance numbers. The §9.3 budget
values are printed from the ideal as targets; they become assertions nowhere.

## Acceptance criteria (contract)

1. With `PerfProbe.Enabled` true and false (and `TrackAllocations` true and false), the same world,
   commands and seed produce the same `StateHash` every turn, over a scripted multi-turn run on a
   synthetic world.
2. `WorldDeterminismGuardTests` stays green with no new exemption and no edit to its banned list.
3. After one `Step` with the probe enabled, `SnapshotAndReset()["sections"]` holds an entry for
   `world.step` and for every phase name in `TurnEngine.Phases` — the list is read from `Phases`, never
   written out in the test.
4. `PerfSection`'s member count equals `SectionCount` and the names array's length (the closed-vocabulary
   rule the existing comment states; pinned by reading the enum, not by a literal).
5. The bench covers the `medium` and `giant` tiers. Timings and allocations are **printed**, never
   asserted.
6. With `TrackAllocations` false, a `PerfScope` records no allocation figure (the injector path is
   unchanged).

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Turn/TurnStepBench.cs` (prints) and
  `tests/FusionRpg.Core.Diagnostics.Tests/Diagnostics/PerfProbeWorldSectionTests.cs` (criteria 1, 3, 4, 6), both
  `[Trait("VerificationId", "core.turn-step-bench")]`.
- `gk-core/scripts/verification-boundaries.v1.json` gains owner row `turn-step-bench`: paths the two test files,
  `tests/FusionRpg.Bench/TurnStepBench.cs` and `gk-core/tests/FusionRpg.Bench/Program.cs`, project `core`,
  verificationId `core.turn-step-bench`. `gk-core/src/FusionRpg.Core/Diagnostics/PerfProbe.cs` and
  `TurnEngine.cs` stay on `core-fallback` (module level), which is correct: a probe change can move any
  Core caller.
- The guard run: `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~WorldDeterminismGuardTests"`.
- The Release run (evidence, manual): `dotnet run -c Release --project tests\FusionRpg.Bench -- --only turn-step`.
- Verify: `.\scripts\verify-change.ps1 -Paths <changed files> -Session <id>`.

## Hard edges

- **No golden moves and no `RulesetVersion` bump**: `Step`'s output is unchanged by construction;
  criterion 1 is the proof, and the Core world goldens run under `core-fallback` in the same change.
- `SectionCount` and the names array move together or `Record` silently drops the new sections
  (`PerfProbe.cs:116`).

## Boundaries

- **Always:** one scope per phase call; the `Stopwatch` stays in `Core/Diagnostics`.
- **Ask first:** shipping world-phase windows from the server to `/api/perf`.
- **Never:** assert a wall-clock number in a pass/fail test; read the probe from simulation code; add a
  guard exemption.

## Dependencies and interface

**Depends on:** `synthetic-graph`.

| Exposed | Consumer |
|---|---|
| `PerfSection.World*` and `TrackAllocations` | `logistics-flow` (`logistics-bench`, the §9.3 zero-allocation budget), any later phase |
| `TurnStepBench` printed baseline | `logistics-flow`'s performance gate |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world turn engine (instrumentation only), perf probe, determinism guard, bench harness.
[~] Session boundary: trade-network-idea-20260919 covers this file; session-boundary-check.py not
    re-run for this doc (known crossing recorded in the session file).
[x] Read this session: trade-foundation map §2.2, ideal §9, DESIGN-GATE Performance row (via
    PRINCIPLES §3 "Perf is a main-thread problem"); runbook/perf-probe-plan.md NOT read this session —
    PerfProbe's contract was read in code instead.
[x] decisions.md: phase-order row (:7) — no phase added or moved.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file; see the session report.
[x] Verified against code: the guard scope and banned list, PerfProbe's aggregates-only shape, the
    missing Bench verification boundary (verify-change -PlanOnly run this session).
[x] Surrounding sections read (the guard's scope doc comment; SectionCount's structural comment).
[x] Constraint tested, not assumed: "no golden moves" is acceptance criterion 1, proven by test.
[x] No §2 invariant contradicted: the simulation reads nothing from the probe.
[x] Corrections propagated: the missing Bench boundary is recorded in the map's corrections section.
[x] No population pinned; the section count is a closed enum read from the enum itself.
[x] No event-refreshed cache.
[x] No ordering-fixed criterion.
[x] ActorHub: not touched.
[x] No SOLID fork: PerfProbe is extended, not duplicated; one synthetic builder is source-linked into the
    Release bench instead of copied.
[x] No new rule, so no registry row.
```
