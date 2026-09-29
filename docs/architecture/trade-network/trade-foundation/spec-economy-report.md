# Spec: `economy-report`

**Status: written against shipped code 2026-09-19.** Every `file:line` below was opened this session on
`features/mega-merge`. Module id `economy-report`, §2.9 of the
[trade-foundation map](../trade-foundation-map.md) (approved 2026-09-19; depends on `synthetic-graph`,
`stock-deltas`, `world-stamp`). Principles: [../../economy-principles.md](../../economy-principles.md)
§13 (*"A world economy report asserting the first two over a scripted campaign is a test, not a
dashboard"*), P1, P3/P4, P6, P8.

## Objective

Make the economy's health a test over the **real** turn engine. Run scripted multi-turn campaigns on
synthetic worlds with every faction driven by the shipped AI policies, read `TurnResult.StockDeltas`,
and compute: **P1** net flow per stock per turn, **P6** sink share by reason, **binding frequency**,
**P8** payback per building, and **win rate with trade on and off**. Assert only what §13 makes a test
(P1 and P6) plus the report's own arithmetic; print the rest with a verdict column. Each later
sub-program adds its rows in the change that adds its faucet or sink.

Success looks like: one test class that prints a readable per-stock table for `medium` and `giant`
worlds, fails when a stock's net flow is monotone positive or one sink reason dominates spend, and never
pins how big the run was.

## Scope and non-goals

In scope: the report model and its computation, the campaign runner around `SyntheticCampaign`, the
tuning block for the P6 ceiling and its loader, and the tests.

Not in scope: a player-facing dashboard; any gameplay number; the rows later sub-programs own (located
goods, lane loss, tariffs, AI treasuries, share of banked essence that came through trade).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Precedent harness: replays loam arithmetic over a hand-built fixture, asserts net flow is not monotone positive and a deficit floor, prints a table — and is *"deliberately not `loam-turn`"* | `gk-core/tests/FusionRpg.Core.Tests/World/Loam/EconomyHarnessTests.cs:8-19`, `:154-183` |
| Its P1 predicate: series non-decreasing **and** every value positive | `EconomyHarnessTests.cs:160-162` |
| §13's metric table: P1 "never monotone positive", P6 "no single sink above ~70% of spend", binding frequency, payback, income-vs-upkeep growth, yield concentration | `docs/architecture/economy-principles.md:306-323` |
| P6 and P8 rules | `economy-principles.md:124-133`, `:155-173` |
| Typed stock deltas on every `TurnResult`, and a synthetic campaign driver | `spec-stock-deltas.md`; `spec-synthetic-graph.md` §4 |
| Refusal reasons land in the turn report as `command.dropped` entries with a reason string | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:233-237`; `gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs:3-9` |
| Build spend is refused when carried loam is short | `gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:134` |
| Tuning files are versioned JSON published through `gk-core/tools/tuning/publish.py`; `data/tuning/trade.v*.json` does not exist yet | `gk-core/data/tuning/` listing this session |

### Real gap

Nothing runs an economy report over `TurnEngine.Step`.

## Design

### 1. Where it lives

`tests/FusionRpg.Core.Tests/World/Economy/` (new): `EconomyReport.cs` (model + computation, no xunit),
`EconomyReportTests.cs` (assertions + printing). Test-only; nothing in `src/` except the tuning loader
(§5).

### 2. Inputs

`EconomyRun.For(tier, seeds, turns, stamp)`: for each seed, `SyntheticGraph.Build(tier, seed)`, stamp it
(`world with { Stamp = stamp }`), then `SyntheticCampaign.Run`. The turn count and seed list are inputs
to the run, printed in the header, never asserted.

### 3. Metrics

All quantities `long`; shares in per-mille, integer division last.

| Metric | Computation | Asserted? |
|---|---|---|
| **P1 net flow** per `(stock, turn)` | Σ `StockDelta.Delta` for that stock over all holders, excluding `open` | **Yes**: for no stock is the per-turn series non-decreasing with every value > 0 over the run (the harness's predicate, `EconomyHarnessTests.cs:160-162`) |
| **P6 sink share** per `(stock, factKind)` | negative deltas by fact kind ÷ total negative deltas of that stock, ‰ | **Yes**: no reason above `report.sinkShareCeilingMilli` for any stock with at least two sink reasons observed; a stock with one sink reason is **printed** with a P6 warning (that is a design finding, not a flake) |
| Report arithmetic | per stock, sink shares sum to exactly 1000 ‰ (remainder assigned to the largest share, ordinal tie-break); Σ net flow over the run = Σ of that stock's deltas | **Yes** |
| **Binding frequency** per stock | `command.dropped` entries whose reason names a shortfall of that stock (a closed map of reason → stock kept in the report, e.g. build refused for carried loam), ÷ commands of that kind | Printed, verdict "binds sometimes / never / always" |
| **P8 payback** per structure id | turns until Σ of `produce` deltas attributable to the sector since the structure finished ≥ its build cost; `—` if never | Printed |
| **P2 income vs upkeep growth** per faction | for each faction, the least-squares slope over the run of Σ faucet deltas (`produce`, `income`, `pulse`) and of Σ upkeep deltas (`upkeep`, `burn`) against sectors held that turn (`long` sums; the slope ratio is a `double`, printed only) | Printed, verdict "same order / diverging" (economy-principles §13 row P2: *"divergence is the failure"*) |
| **P9 / P12 yield concentration** per faction | the best single sector's share of that faction's `produce` deltas per turn, ‰ | Printed, verdict "falls / flat" — a flat line means depletion (P9) is not wired for that faucet, which `sector-yield` records as a later change |
| **PS-5 pairing** per scaled loop | for each located family whose loop read is Content (`sector-yield` `essence-loop-read` §3), the ratio of the faucet's mean scale read to its sink's mean scale read over the run | Printed; a ratio that drifts with depth is the PS-5 finding to send to the loop's owner (the essence loop's faucet reads sector depth and its sink the fused creature's level, round 4 Q7 — this row is what measures that pairing) |
| **Win rate, trade on vs off** | per seed: *won* if the player holds the Zomboss-kind faction's capital at the end, *lost* if the player no longer holds its homeworld, else *undecided*; run once under `WorldStamp.Legacy` and once under the newest stamp | Printed; while `WorldCapabilityRegistry.Shipped` is empty the two runs are identical and the report prints *"no trade capability shipped — on/off identical"* |

### 4. Order and determinism

Stocks, fact kinds and seeds are iterated in ordinal / ascending order. The campaign is deterministic
(`synthetic-graph` criterion 6), so the report is too; the tests assert only predicates, never a
printed number.

### 5. Tunable — the P6 ceiling

`data/tuning/trade.v{n}.json`, block `report`:

| Key | Unit | Value | Why |
|---|---|---|---|
| `report.sinkShareCeilingMilli` | ‰ of a stock's spend | 700 | economy-principles §13 "~70%" |

Loaded by `TradeTuningLoader` (`src/FusionRpg.Core/World/Trade/TradeTuning.cs`, new — the one location for
the trade tuning record; `sector-yield`, `logistics-flow` and later sub-programs add their blocks to the
same loader, never a second `TradeTuning` elsewhere — reconciliation 2026-09-19 aligned
`sector-yield/spec-warehouse-axis.md` and `logistics-flow/spec-lane-flow.md` to this path). A
missing key is a load rejection. Published through `gk-core/tools/tuning/publish.py`, extending it for the
`trade` domain if it lacks support. **Creator (settled 2026-09-20, reconciliation R-19.3):** there is no
race. [landing-order.md](../landing-order.md) §5 fixes **this module** as the one creator of
`data/tuning/trade.v1.json`, of the `TradeTuning` record and loader, and of the `trade` domain in
`publish.py` — it is the earliest wave (row 0a) with keys. Every `sector-yield`, `logistics-flow`,
`fleet`, `counterparties`, `exchange` and `trade-surface` module publishes `v{n+1}` with its own keys,
never an in-place edit. Core never reads
the file; the test reads it through the loader the way the server will.

## Acceptance criteria (contract)

1. P1: over the scripted run on `medium` and `giant` synthetic worlds, no registered stock's net-flow
   series is monotone positive.
2. P6: no sink reason exceeds the tuned ceiling for any stock with two or more observed sink reasons;
   the ceiling is read from tuning, never a literal in the test.
3. Arithmetic: sink shares sum to 1000 ‰ per stock; per-stock net flow equals the sum of its deltas.
4. The test prints tier, seeds, turns, sectors, factions, and every metric table; it asserts no count of
   sectors, turns, buildings, goods or rows.
5. With the capability registry empty, the on and off runs produce identical state-hash sequences, and
   the report says so.
6. An unknown or missing `report.sinkShareCeilingMilli` fails the load.
7. The P2, P9 and PS-5 pairing rows are **printed with a verdict, never asserted** (economy-principles §13
   makes only P1 and P6 a test); each row states the faucet and sink fact kinds it read, so a reader can
   check it against the ledger.

## Test plan and verification boundary

- `tests/FusionRpg.Core.Tests/World/Economy/EconomyReportTests.cs`,
  `[Trait("VerificationId", "core.world-economy-report")]`; loader tests in
  `tests/FusionRpg.Core.Tests/World/Trade/TradeTuningTests.cs`.
- `gk-core/scripts/verification-boundaries.v1.json` owner row `core-world-economy-report`: paths
  `tests/FusionRpg.Core.Tests/World/Economy/**`, project `core`. The loader file is new under
  `src/FusionRpg.Core/World/Trade/`; give it an owner row `core-trade-tuning` with verificationId
  `core.trade-tuning` whose paths are `src/FusionRpg.Core/World/Trade/**`,
  `tests/FusionRpg.Core.Tests/World/Trade/**` **and every published `data/tuning/trade.v{n}.json`, one exact
  path per version** — the matcher takes exact paths and `dir/**` only (`scripts/verify-change.ps1:70-75`),
  so each `publish.py trade` change adds its new file to the row, the way `materials-tuning` lists v1–v3. The tuning file needs the
  row: `gk-core/data/tuning/**` has no fallback mapping, and `verify-change.ps1 -PlanOnly -AllowUnscoped -Paths
  gk-core/data/tuning/world.v6.json` stops with *"VERIFICATION BOUNDARY MISSING"* (run in the audit of
  2026-09-20). Whichever trade module creates `trade.v1.json` lands this row; every later publish of
  `trade.v{n+1}` adds its path to the same row.
- Run cost: a `giant` campaign is slow; the test runs a short scripted length by default and the length
  is an input, not a pinned property. It is **not** named `*Bench` because it asserts P1/P6.
- Verify: `.\scripts\verify-change.ps1 -Paths <changed files> -Session <id>`;
  `python gk-core/scripts/audit-magic-numbers.py` for the loader.

## Hard edges

- **Tuning publish order** with `sector-yield` (§5).
- A P1 or P6 failure on the shipped economy is a **finding**, not a test to loosen: it goes to the owner
  of the failing faucet/sink with the printed table. This module does not tune anything to pass.
- No golden, no ruleset stamp, no schema.

## Boundaries

- **Always:** read the ceiling from tuning; print scale; assert predicates.
- **Ask first:** asserting a third metric (binding, payback, win rate) — §13 makes only two a test.
- **Never:** pin a run's size or a printed number; hand-edit a published tuning file.

## Dependencies and interface

**Depends on:** `synthetic-graph`, `stock-deltas`, `world-stamp` (the trade on/off switch).

| Exposed | Consumer |
|---|---|
| `EconomyReport` rows and the P1/P6 tests | every later sub-program adds its rows (located goods, lane loss, tariffs, AI treasuries, banked-through-trade share) in its own change; `rift-trade` (consignments) |
| `TradeTuningLoader` | `sector-yield`, `logistics-flow`, `exchange` |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world turn engine (read), economy instrumentation, tunables.
[~] Session boundary: trade-network-idea-20260919 covers this doc; boundary check not re-run.
[x] Read this session: economy-principles P1, P6, P8, §12, §13; EconomyHarnessTests; trade-foundation map
    §2.9 and §4. tunables-ssot.md not read in full (rules from PRINCIPLES §5).
[x] decisions.md: magic-numbers/tuning rows via PRINCIPLES; no lock on test reports.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file; see the session report.
[x] Verified against code: the harness's P1 predicate, refusal reporting shape, trade tuning absence.
[x] Surrounding sections read (§13's closing paragraph on what is a test).
[x] No untested constraint claimed; a P1/P6 failure is declared a finding, not predicted.
[x] No §2 invariant contradicted.
[x] Corrections propagated: none owed beyond the map.
[x] No population pinned (criterion 4).
[x] No event-refreshed cache.
[x] Order-independent: metrics are sums; iteration order is fixed and ordinal.
[x] ActorHub: not touched.
[x] No SOLID fork: one report extended by later sub-programs; one trade tuning loader.
[x] No new guarded rule.
```
