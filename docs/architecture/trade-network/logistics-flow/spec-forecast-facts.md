# Spec: `forecast-facts`

**Status: written against code 2026-09-19** (branch `features/mega-merge`, `b82a4098`). Every
`file:line` below was opened in this session. Module id `forecast-facts`, row 11 of the
[logistics-flow map](../logistics-flow-map.md) (wave 4; depends on `logistics-facts`, `auto-banking`,
`construction-chain`; `sector-yield` halt rule and production). Ideal:
[trade-network-ideal.md](../../trade-network-ideal.md) §14b (*"the turn cluster shows a throttle forecast
— 'next turn a sector halts: 40 fire essence has nowhere to go' — with two or three one-click answers"*),
§8.5 (per-lane flow, utilisation and bottleneck reason every turn). House style:
[spec-budget-debit.md](../../world-action-economy/spec-budget-debit.md).

## Objective

Tell a commander, before they press End Turn, what logistics will do to them if they give no orders:
which sectors will halt, which goods will strand or waste, which flows will fall short and why, how busy
each lane will be — and, for each, which commands would answer it. The read model behind
`trade-surface`'s throttle forecast and flow lens. It must never disagree with what the turn actually does.

Success looks like: committing the next turn with no new orders produces exactly the facts the forecast
named, and nothing it did not name; the committed state is untouched by asking.

## Locked anchors

- **One copy of the rules.** The forecast calls the engine; it never re-implements a step. The
  precedent is `LoamForecast`, the one place both the engine and the player-facing projection call
  (`gk-core/src/FusionRpg.Core/World/Loam/LoamForecast.cs:3-9`).
- **The engine is pure.** `TurnEngine.Step` takes state and commands and returns a new state, report
  and hash (`gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:168-209`); state is immutable records
  (`gk-core/src/FusionRpg.Core/World/WorldState.cs:334-354`). A dry run cannot touch the committed world.
- **The commit and the replay call `Step` with the world's header seed** (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:601`,
  `:773`). The forecast uses the same inputs, so it is the same computation.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| The shared-projection precedent | `gk-core/src/FusionRpg.Core/World/Loam/LoamForecast.cs:3-9` |
| `Step`'s signature and purity | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:168-209` |
| `Step`'s two production call sites and their seed | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:601`, `:773` |

### Wiring gap

None.

### Real gap (this module closes it)

The dry run, the per-sector fact records, the answer table, and the utilisation read model.

## Design

### 1. The dry run is the turn

`LogisticsForecast.For(world, seed, resolver, powerTuning)` runs `TurnEngine.Step(world, commands: [],
seed, …)` with **its own** `LogisticsRuntime` (never the commit's — runtimes are not thread-safe, and a
forecast request can arrive during a commit). It returns:

- **Facts** — the next turn's report entries of the `logistics-facts` kinds, plus `sector-yield`
  `production-halt`'s halt entries, grouped by sector and filtered to the asking faction's `Audience`.
- **Utilisation** — per lane the faction's committed load and the lane capacity, read from the runtime's
  L5 records after the run (the flow lens; not a report entry, `spec-logistics-facts.md` §1).
- **Answers** — for each fact, the command kinds that address it, from a closed table.

**The same logged inputs the commit would pass (audit 2026-09-20).** `Step` takes per-turn inputs beside
the commands: the pending `located_income` list (`sector-yield` `income-parity` §3) and, once
`counterparties` lands, the logged band snapshot (umbrella §1a CM1). The forecast receives **exactly the
list the next commit would pass** — the server's read endpoint gathers them through the same Data
function the commit calls, never a second query — or "faithful" fails the first turn a delve drop or a
band change is pending. `LogisticsForecast.For` therefore takes them as parameters and never reads a store.

Running the whole `Step` rather than the Logistics phase alone is deliberate: halts come from
`Production`, which runs before `Logistics`; owner changes in `Pressure` and `Snapshot` shape the turn
after; and the only way to be faithful to "commit with no orders" by construction is to run that commit's
computation. "No new orders" means no orders from anyone — AI commanders included.

### 2. The answer table (closed)

Each answer is a command kind plus, for `build`, the **sector feature** it builds or upgrades
(`trade-foundation` `sector-features`), so the surface can offer *"build a Counting House"* as one click
(round 4 Q3):

| Fact | Answers (command kind [feature]) — first row is the recommended one |
|---|---|
| `logistics.short` / `no-path` — **the first throttle: no path to a bank point** | `build` [`banking`] at the source (a Counting House makes it a bank point), `route-set` |
| halt, base yard full, no storage building (round 5 A2: every held sector has a small base yard) | `build` [`storage`] (a Storehouse) |
| halt, warehouse full, nothing flows | `route-set`, `widen`, `build` [`storage`] (the next storage tier) |
| halt at a bank point, banking rate binding | `build` [`banking`] (the next Counting House tier) |
| `logistics.short` / `lane-capacity` | `widen`, `route-set` (priority) |
| `logistics.short` / `contested` | `route-set` |
| `logistics.short` / `too-far`, `buffer-full` | `route-set`, `route-clear`, `build` [`banking`] nearer the source |
| `lane.cut`, `logistics.strand` | `route-clear` |
| `logistics.loss` / `hazard`, `hostile-presence` | `ward` |
| `logistics.overflow` | `route-set`, `build` [`storage`] at the destination |

A later program adds its own answers by adding rows when its kinds exist (`fleet`'s escort, `exchange`'s
sell — map ask A6); a row may name only a kind present in `WorldCommandKinds.All`
(`gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:123-128`) and only a feature in `SectorFeature`, asserted
by join tests. A `build` answer names the feature, not a structure id: which row carries the feature, and
whether the sector has a legion and a free or upgradable slot to issue it, is the surface's lookup
(`trade-surface` `throttle-forecast` renders it; its closed answer vocabulary needs a `build-feature`
answer — reported to that program).

### 3. Cost

One `Step` per request. `logistics-bench` measures the whole `Step` at the giant tier (with the phase on),
which is this call's cost; the server-side caching of a forecast per (world, turn) is `trade-surface`'s
read-endpoint concern, not this module's.

## Tunables

None.

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World.Logistics.LogisticsForecast"
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <session id>
```

## Structure

```
src/FusionRpg.Core/World/Logistics/LogisticsForecast.cs    (new) — dry run, facts, answers, utilisation
tests/FusionRpg.Core.Tests/World/Logistics/LogisticsForecastTests.cs   (new)
```

## Testing strategy

- **Faithful, both directions:** for fixture worlds and seeded runs, commit the next turn with no orders;
  the committed report's logistics and halt entries equal the forecast's facts exactly — nothing missing,
  nothing extra.
- **Pure:** the input world's hash is identical before and after the forecast; the commit's runtime is
  untouched (its rebuild count does not move).
- **One copy:** a changed tuning value (for example `lane.throughputPerWidth`) moves the forecast and the
  committed turn identically.
- **Answers:** every fact kind and reason has at least one answer row; every answer names a kind in
  `WorldCommandKinds.All`.
- **Fog:** a faction's forecast contains no other faction's entries or lanes it has no flow on.

Verification boundary: `FusionRpg.Core.Tests` (World/Logistics).

## Acceptance (contract)

1. Committing the next turn with no new orders produces exactly the halts, strands, losses, shorts and
   waste the forecast named, and nothing it did not name.
2. The committed state's hash is unchanged by a forecast.
3. The forecast and the phase share every rule: a tuning change moves both identically.
4. Every fact carries answers from the closed table, and every answer is a real command kind (and, for
   `build`, a real `SectorFeature`).
5. A source with no reachable bank point forecasts `logistics.short` / `no-path` with `build` [`banking`]
   as its first answer.
6. **Faithful with pending inputs:** with a pending located income and (once it exists) a changed band
   snapshot, the forecast still equals the committed turn — both are fed the same logged inputs.

## Hard edges

- **Ruleset / goldens:** none; the forecast writes nothing.
- **Deviation from the map:** the map says "a dry run of the Logistics step on a copy of the committed
  state"; this spec runs the whole `Step`, because halts and next-turn shape come from phases outside
  `Logistics` and faithfulness must hold by construction. Reported.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `LogisticsForecast.For` → facts, utilisation, answers | `trade-surface` `throttle-forecast` (UI) and flow lens; `trade-ai` (reads the same model to decide) |

## Boundaries

- **Always:** its own runtime; the whole `Step`; the asking faction's audience only.
- **Ask first:** a partial-phase dry run; caching inside Core.
- **Never:** a second copy of any flow, loss, transit or halt rule; writing to any store.

## Design-gate checklist

```
[x] Subsystems: turn engine (called), logistics read model.
[~] Session boundary: covered by tasks/sessions/trade-network-idea-20260919.json;
    session-boundary-check.py not run (docs only).
[~] Read this session: as in spec-logistics-phase.md. Gap: trade-surface-map.md not read this session.
[x] decisions.md: no lock on forecasts.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run; no HIGH finding left.
[x] Verified against code: Step's purity and inputs; both call sites' seed; LoamForecast's shape.
[x] Surrounding sections read: LoamForecast's class doc.
[x] Constraints tested, not assumed: faithfulness is acceptance 1, proven in both directions.
[x] §2 invariants: none contradicted.
[x] Corrections propagated: the whole-Step deviation is here and in the session report.
[x] No population pinned; the answer table is closed and joined against the kind list.
[x] Event-refreshed cache: none (its own cold-or-warm runtime is a memo).
[x] Orderings: none.
[x] Actor magnitudes: none.
[x] No SOLID fork: one Step, no copied rule.
[x] Registry row: none owed.
```
