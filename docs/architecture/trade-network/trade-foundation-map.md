# Capability map: `trade-foundation` (trade-network sub-program 1)

**Status:** APPROVED 2026-09-19. Module specs written 2026-09-19 under
`trade-network/trade-foundation/spec-<module-id>.md` (all eleven; see §7 for what they corrected here).
**Reconciled with the round-4 owner decisions** ([decisions-round-4.md](decisions-round-4.md)) on
2026-09-19 — §8 lists what changed; where §1–§7 and §8 differ, §8 and the specs win.
**Umbrella:** [../trade-network-map.md](../trade-network-map.md) — its §5 invariants bind every module
here and are not repeated. **Ideal:** [../trade-network-ideal.md](../trade-network-ideal.md) §9, §11
row 1, §14 D-C, §14b.
**Specs land:** `docs/architecture/trade-network/trade-foundation/spec-<module-id>.md`.
**Plan / tasks:** `tasks/trade-network-trade-foundation-plan.md` / `-todo.md`.

> **The sub-program in one sentence.** Before any goods move, make End Turn measurable, make every
> world say which rules it runs on, make every banked and world-stock mutation a ledger row, and make
> the economy's health a test — so every later sub-program is built against numbers, not hopes.

Nothing in this sub-program changes a gameplay number. Every module except `world-stamp` is either
test-only, a guard, or an append-only record beside behaviour that already exists.

---

## 1. What already exists (read in code this session)

| Fact | Where |
|---|---|
| `TurnEngine.Step` is pure: `(world, commands, seed, resolver, powerTuning, …) → TurnResult(World, Report, StateHash)` | `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:8`, `:168-209` |
| Phase calls in order, including `Assaults` | `TurnEngine.cs:191-207` |
| `RulesetVersion = 13` (bumped by warden-freeze-fix after these specs were first written), `EngineVersion = 1` | `TurnEngine.cs:125`, `:20` |
| The hash rewrites the whole canonical text every turn | `gk-core/src/FusionRpg.Core/World/Turn/StateHasher.cs:17`; `gk-core/src/FusionRpg.Core/World/WorldCanonical.cs:20` |
| Banned in `World`, `Battle`, `Effects`: `DateTime.Now/UtcNow`, `DateTimeOffset.Now/UtcNow`, `Stopwatch`, `System.Random`, `new Random(` | `gk-core/tests/FusionRpg.Guard.Tests/WorldDeterminismGuardTests.cs:39-48`, scope `:253-266` |
| `PerfProbe` — allocation-free counters, `Measure(PerfSection)` returns a disposable scope; the `Stopwatch` lives in `Core/Diagnostics`, outside the guarded tree; already called from inside `Effects` (`gk-core/src/FusionRpg.Core/Effects/EffectBag.cs:362`) and `ActorHub` | `gk-core/src/FusionRpg.Core/Diagnostics/PerfProbe.cs:48`, `:111-112` |
| Benchmark precedents: `ReconnectionCostBench` (an xunit class named `*Bench` that measures and never asserts a timing, `gk-core/tests/FusionRpg.Core.Tests/World/Topology/ReconnectionCostBench.cs:9-17`); `gk-core/tests/FusionRpg.Bench` (Release-only exe with `WorldGraphWriteBench.cs`) | as cited |
| Hand-built graph shapes (raw `WorldState`, not validated) | `gk-core/tests/FusionRpg.Core.Tests/World/Topology/GraphShapes.cs:17-95` |
| `ReconnectionCost.For` callers: `SeveranceScore.cs:32`, `ValueMap.cs:167`, and one per map-view request in `WorldEndpoints.cs:864` | `gk-core/src/FusionRpg.Core/World/Ai/SeveranceScore.cs:32`; `gk-core/src/FusionRpg.Core/World/Ai/ValueMap.cs:167`; `gk-core/src/FusionRpg.Server/WorldEndpoints.cs:864` |
| Measured: the O(V⁴) sweep takes 606.5–700.0 ms at 128 nodes | `docs/architecture/world/spec-world-topology.md:57-63` |
| World size tiers read node bounds from tuning; `large`, `huge`, `giant` are `Available = false` | `gk-core/src/FusionRpg.Core/World/WorldSizeCatalog.cs:48-58` (bounds from tuning, not literals) |
| `rpg_worlds` carries `engine_version` and `ruleset_version` (default 1), `state`, `mode`, `catch_up_cap` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:20-35` |
| World creation writes `ruleset_version` as the literal 1; the turn log writes the live `TurnEngine.RulesetVersion` | `RpgStore.World.cs:241-247`; `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:668-675` |
| Replay refuses on an engine or ruleset mismatch and refuses delve worlds | `RpgStore.WorldTurns.cs:759-767` |
| Tuning is loaded once per process into static policies (loam v5, world v6, power-scale v2, materials v2, …) | `gk-core/src/FusionRpg.Server/Program.cs:36`, `:48`, `:243`, `:316` |
| The turn commit: `Step`, then the diff writer, relic spend and cargo pass in one transaction | `RpgStore.WorldTurns.cs:493`, `:601-615` |
| World stocks (`LoamStock`, `RubbleStock`, `IronworkStock`, `RecruitStock`) are `long` fields on `WorldSector`, persisted only through the diff writer — no other SQL updates `rpg_world_sectors` | `gk-core/src/FusionRpg.Core/World/WorldState.cs:173`, `:181`, `:187`, `:234`; `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldGraphDiff.cs:140-155` |
| The soul ledger — the P14 pattern: `UNIQUE(player_id, reason, dedupe_key)`, `INSERT OR IGNORE`, watermarked balance | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:684-699`; `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Souls.cs:139-168` |
| Materials have **no ledger**: `rpg_creature_materials(player_id, material_id, qty)` is written by upsert or conditional decrement at four sites | DDL `RpgStore.cs:764-770`; writers `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Materials.cs:191`, `:307`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs:233`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Fusion.cs:545` |
| A spend log exists beside it (`rpg_material_spend_log`, recipe spends only) | `RpgStore.Materials.cs:13`, `:60` |
| Economy harness precedent: `EconomyHarnessTests` — a test-shaped tool replaying loam arithmetic over a hand-built fixture; asserts net flow is not monotone positive and a deficit floor; prints the table | `gk-core/tests/FusionRpg.Core.Tests/World/Loam/EconomyHarnessTests.cs:8-19`, `:154-183` |
| New tables are born Tier A `(save_id, empire_id, …)`; `empire_id` shares the world `faction_id` id space | `docs/architecture/solid-enforcement/spec-save-identity.md:594-603`, `:77` |
| `save-identity` progress: SE4.11 done; SE4.12 (`rpg_save_empires`, `HumanEmpireOf`, `EmpiresOf`) and SE4.38 (Tier B typing of the materials store) open; lane B of summoner-convergence is building them | `tasks/solid-enforcement-todo.md:339`, `:352`, `:634` |

**Real gaps this sub-program closes:** nothing times a full `Step`; nothing builds a valid world at the
`giant` tier; a world does not record which rules it runs on; materials and world stocks have no P14
ledger; there is no world economy report over the real turn engine.

---

## 2. Modules

Ordered model-free first. Each is independently testable.

### 2.1 `synthetic-graph`

**Capability.** A **test-only** builder that produces a valid, deterministic `WorldState` of any size
tier — sectors, lanes of every lane type, factions (a player, exactly one dominant `Zomboss` empire,
N `Rival` empires, M clans — counterparties ask A4), slots and a homeworld — from `(tier, seed)`, so medium- and giant-tier behaviour is measurable before the
world generator exists. It extends the `GraphShapes` idea (hand-built shapes) to worlds that pass
`WorldValidation`, and it is never reachable from production code.

- **State:** real gap. `GraphShapes` builds raw, unvalidated graphs (`GraphShapes.cs:12-15`);
  `ReconnectionCostBench` builds a ring with chords, lanes only (`ReconnectionCostBench.cs:22-23`).
- **Depends on:** —
- **Touches:** `tests/FusionRpg.Core.Tests/World/Synthetic/` (new); reads `WorldSizeCatalog`,
  `LaneTypeCatalog`, `SlotTypeCatalog`, `FactionKindCatalog`.
- **Acceptance (contract):** every generated world passes `WorldValidation.Validate`; the same
  `(tier, seed)` yields a byte-identical `WorldCanonical.Write`; the sector count lies inside the
  tier's tuned `[MinNodes, MaxNodes]`, read from the catalog, never a literal; every lane type in the
  closed catalog appears at least once at the giant tier; the graph is connected. It prints its scale;
  it asserts no count of its own choosing.
- **Verification:** `gk-core/tests/FusionRpg.Core.Tests` (`--filter FullyQualifiedName~Synthetic`).

### 2.2 `step-benchmark`

**Capability.** Time a full End Turn: `TurnEngine.Step` on synthetic medium and giant worlds with a
scripted command load, reporting p50/p99 for the whole step and per phase, plus allocated bytes per
phase. Per-phase timing uses **`PerfProbe` itself** — new `PerfSection` values for the world phases,
wrapped around each phase call in `Step` — not a second timing facade. The `Stopwatch` stays in
`Core/Diagnostics`, which the determinism guard does not scan, exactly as `EffectBag` already does.
Nothing the probe records ever reaches world state.

- **State:** real gap. *"Nothing times a full `TurnEngine.Step`"* (ideal §9.1) — confirmed: no bench
  references `TurnEngine` (`gk-core/tests/FusionRpg.Bench/` holds `AtomFormBench.cs`, `WorldGraphWriteBench.cs`).
- **Depends on:** `synthetic-graph`.
- **Touches:** `gk-core/src/FusionRpg.Core/Diagnostics/PerfProbe.cs` (section enum),
  `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs` (one `using var _ = PerfProbe.Measure(...)` per phase
  call), `tests/FusionRpg.Core.Tests/World/Turn/TurnStepBench.cs` (new), optionally a
  `tests/FusionRpg.Bench/TurnStepBench.cs` (new) for a Release run.
- **Acceptance (contract):** with the probe enabled and disabled, the same world, commands and seed
  produce the same `StateHash` (the probe is invisible to the simulation); the determinism guard stays
  green with no new exemption; the bench covers the medium and giant tiers and every phase `Step`
  runs; timings are **printed, never asserted** in a pass/fail test (a wall clock on a busy machine is
  a flaky test — the `ReconnectionCostBench` rule). The ideal §9.3 budgets are compared by an explicit
  Release run of `gk-core/tests/FusionRpg.Bench` that prints the verdict per budget line; that run is evidence
  for `logistics-flow`'s gate, not a CI test.
- **Verification:** `gk-core/tests/FusionRpg.Core.Tests` (World/Turn) and `gk-core/tests/FusionRpg.Guard.Tests`
  (`WorldDeterminismGuardTests`).

### 2.3 `routing-guard`

**Capability.** A source-scan guard that fails when any file under the logistics namespace
`logistics-flow` will create (`src/FusionRpg.Core/World/Logistics/**`) references `ReconnectionCost`,
with the three current callers allow-listed by path so the list can only shrink. It lands before the
namespace exists, so the first routing file is born under it.

- **State:** real gap (no guard names `ReconnectionCost`).
- **Depends on:** —
- **Touches:** `tests/FusionRpg.Guard.Tests/LogisticsRoutingGuardTests.cs` (new),
  `gk-core/scripts/enforcement-registry.v1.json` (one row).
- **Acceptance (contract):** a falsifier file containing `ReconnectionCost.For(` under the guarded
  path fails the guard; a comment mentioning it does not (the comment-stripping rule
  `WorldDeterminismGuardTests` already uses); the allow-list names paths, not counts; the registry row
  exists and the enforcement meta-test passes.
- **Verification:** `gk-core/tests/FusionRpg.Guard.Tests`.

### 2.4 `world-stamp`

**Capability.** One per-world **stamp** record — ruleset version, template id and template version,
the version of every tuning file the step reads, and the difficulty profile id — written when a map
world is created, carried on `WorldState`, and read by `Step` as **capability flags** (for example
`trade.sectorYield`, `trade.logistics`), so a phase added by a later sub-program runs only on worlds
whose stamp grants it. Existing worlds are migrated once to a **legacy** stamp that grants no trade
capability. This is the umbrella's one irreversible gate (ideal §14 D-C): a world keeps the rules it
started on. The stamp's home is `rpg_worlds.ruleset_version` plus sibling columns on the same row.

- **State:** wiring gap for the column (exists, default 1, never meaningful — `RpgStore.World.cs:31`,
  `:244`); real gap for the record, the capability flags and the difficulty profile id (no
  difficulty profile exists anywhere in `src/`; the only per-faction knob is `UpkeepHandicapMilli`,
  `gk-core/src/FusionRpg.Core/World/Loam/LoamPhases.cs:154`).
- **Depends on:** — (world-continuity owns the difficulty profile **catalog**; v1 ships one default
  id, `world-continuity-ideal.md` §6.10).
- **Touches:** `gk-core/src/FusionRpg.Core/World/WorldState.cs` (stamp field), `WorldCanonical.cs`,
  `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs` (capability read), `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs`
  (columns, create path), `RpgStore.WorldTurns.cs` (replay check), a one-time migration beside the
  store's schema setup.
- **Acceptance (contract):**
  - A world created after the change stores the live `TurnEngine.RulesetVersion`, never the literal
    1, and the tuning versions the server actually loaded.
  - The migration backs up the database first, runs in one transaction, is idempotent, and gives
    every existing `kind='map'` world the legacy stamp. It never reads the old `ruleset_version`
    value as a real ruleset (X3 in the umbrella map). Delve worlds are untouched (`Step` never runs on
    them, `RpgStore.WorldTurns.cs:762-767`).
  - **A legacy-stamped world hashes byte-identically to today**: the canonical writer emits the stamp
    only when it is not legacy, so no existing golden moves. A non-legacy stamp changes the hash.
  - `Step` on a legacy world never runs a trade phase, whatever the loaded tuning says; the same world
    with a trade-granting stamp does.
  - Replay refuses, with a reason, when the recorded stamp's ruleset or any recorded tuning version
    differs from what is loaded — the same honest refusal `RpgStore.WorldTurns.cs:759-760` gives today.
  - The capability-flag vocabulary is closed (a C# registry); each flag is added by the sub-program
    that ships its behaviour, and its count is a reviewed change.
- **Assumption, not an owner question (umbrella X4):** "old worlds keep their rules" means capability
  flags. Tuning is process-global (`gk-core/src/FusionRpg.Server/Program.cs`, `:48`); a balance publish applies to every world,
  as today. The stamp records tuning versions so a mismatch is detected, not so two versions run side
  by side.
- **Verification:** `gk-core/tests/FusionRpg.Core.Tests` (World), `gk-core/tests/FusionRpg.Data.Tests` (migration,
  create, replay refusal). Crosses Core and Data: the full suite once at module end (AGENTS.md
  verification point 2).

### 2.5 `ledger-keys`

**Capability.** The one dedupe-key grammar and the closed **fact-kind** vocabulary for every trade
ledger row, in Core: `(save_id, owner_id, world_id, turn, factKind, sector_id, good_id)` encoded to one
stable string, with `factKind` drawn from a closed registry (`produce`, `upkeep`, `construct`, `burn`,
`refine`, `bank`, `halt`, `deliver`, `loss`, `settle`, …; each later sub-program widens it by a
reviewed change). Pure, no I/O.

- **State:** real gap. The soul ledger keys on `(player_id, reason, dedupe_key)` with a free-text key
  (`RpgStore.cs:684-695`); nothing defines a grammar for world facts.
- **Depends on:** — (types only; the `save_id`/`empire_id` values come from `save-identity`'s
  `SaveId`/`EmpireRef`, SE4.11, done).
- **Touches:** `src/FusionRpg.Core/World/Ledger/` (new).
- **Acceptance (contract):** encoding is injective (two different tuples never produce one key) and
  round-trips; the `factKind` vocabulary is closed and its count is pinned **with the reason** (a
  closed vocabulary the code owns — validation-ssot allows exactly this); an unknown kind throws.
- **Spec-time decision, recommendation included:** the ideal names the owner column `empire_id`, but
  clans are factions, not save empires (`spec-save-identity.md:96-100` binds only faction ids that
  name an empire). Recommendation: the key carries the world **faction id** (the same id space as
  `empire_id`, `spec-save-identity.md:77`), and the ledger table's closure contract resolves it to a
  save empire when the faction is an empire and to `rpg_world_factions` otherwise. Decided by the spec,
  not the owner — it changes no behaviour.
- **Verification:** `gk-core/tests/FusionRpg.Core.Tests`.

### 2.6 `stock-deltas`

**Capability.** `Step` reports every change it makes to a world stock as a typed **stock delta** —
`(sector, stock, delta, factKind)` — on `TurnResult`, through one recorder threaded like
`TurnReport`, emitted by each phase that mutates a stock (loam production, upkeep and march burn,
rubble and ironwork production, recruit accrual, construction spend). A reconciliation check proves
the record is complete: for every sector and stock, the sum of its deltas equals post-step minus
pre-step. This is the pure half of the world-stock ledger, and the source the economy report reads.

- **State:** real gap. Stock changes today surface only as free-text report lines where a phase chose
  to write one (for example `loam.overflow`, `LoamPhases.cs:64`).
- **Depends on:** `ledger-keys`.
- **Touches:** `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs` (`TurnResult`), the stock-mutating phases
  (`Loam/LoamPhases.cs`, `Loam/LegionSupply.cs`, `Siege/SiegeConstruction.cs`, `Growth/`,
  `Movement/BuildResolver.cs`).
- **Acceptance (contract):** reconciliation holds for every sector and every registered world stock
  over a scripted multi-turn run on a synthetic world (a mutation site that forgets to record fails
  it); deltas are emitted in stable (sector, stock, factKind) order; `StateHash` is unchanged by the
  recorder; the stock list the check walks is the registry's world-stock rows, so a new world stock
  that ships without deltas fails the check.
- **Verification:** `gk-core/tests/FusionRpg.Core.Tests` (World).

### 2.7 `world-stock-ledger`

**Capability.** An append-only ledger table for world stocks, **born Tier A**, written inside the turn
commit transaction from `TurnResult`'s stock deltas, one row per non-zero delta, deduped on the
`ledger-keys` key. The balance stays the hashed field on `WorldSector`; the ledger is the audit and
the input to reports, and a replay or re-commit of the same turn inserts nothing new. Later
sub-programs write located-goods, banking, delivery and settlement facts through the same table and
key.

- **State:** real gap (no world-stock ledger).
- **Depends on:** `stock-deltas`; external `save-identity` **SE4.12** (`rpg_save_empires`,
  `HumanEmpireOf`, `EmpiresOf`) for the owner columns. Activation of Tier A keying (SE4.20) is not
  needed: a new table is born with its columns.
- **Touches:** `src/FusionRpg.Data/Sqlite/RpgStore.WorldLedger.cs` (new), `RpgStore.WorldTurns.cs`
  (commit), schema setup.
- **Acceptance (contract):** committing a turn writes exactly one row per non-zero delta; committing
  the same `(world, turn)` twice writes nothing the second time; for every sector and stock, the sum of
  ledger rows since world creation equals the persisted stock; every row's owner resolves (closure);
  rows are written in the same transaction as the diff, so a failed commit leaves neither. Store tests
  run in memory.
- **Verification:** `gk-core/tests/FusionRpg.Data.Tests`.

### 2.8 `material-ledger`

**Capability.** Put banked materials on the P14 pattern: one ledger-first verb that appends a
deduped row and moves the balance, and the four existing writers of `rpg_creature_materials` routed
through it. The balance table stays the read model. Banking facts from `sector-yield` credit
materials through this verb and nothing else.

- **State:** real gap (no ledger; four direct writers, listed in §1).
- **Depends on:** `ledger-keys`; external `save-identity` **SE4.38** (Tier B typing of the materials
  store to `EmpireRef`) — landing after it avoids touching the same four sites twice. The ruled but
  unscheduled `rpg_creature_materials → rpg_materials` rename (`RpgStore.Materials.cs:20-24`) is not
  this module's; the ledger works under either name.
- **Touches:** `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Materials.cs`, `RpgStore.Expeditions.cs`,
  `RpgStore.Fusion.cs`, schema setup.
- **Acceptance (contract):** no SQL outside the ledger verb writes the materials balance table (a
  guard-style source scan); a repeated dedupe key changes nothing; for every (save, material) the
  balance equals the sum of its ledger rows; an unknown material id still throws at the write
  boundary (`RpgStore.Materials.cs:187-188`); existing fusion, salvage and expedition tests stay green
  with no expected value changed.
- **Verification:** `gk-core/tests/FusionRpg.Data.Tests`; `gk-core/scripts/guard-dal.py`.

### 2.9 `economy-report`

**Capability.** The **world economy report**, run as a test (economy-principles §13): scripted
multi-turn campaigns on synthetic worlds, every faction driven by the shipped AI command policy,
reading `TurnResult` stock deltas and (once `sector-yield` lands) banking facts. It computes **P1** net
flow per stock per turn, **P6** sink share by reason, **binding frequency** (which stock blocks an
action and how often), **P8** payback per building, and **win rate with trade on and off** (the same
campaign under a legacy stamp and a trade-granting stamp). Each later sub-program adds its rows —
located goods, lane loss, tariffs, AI treasuries — in the change that adds the faucet or sink.

- **State:** partial precedent — `EconomyHarnessTests` replays loam arithmetic by hand and is
  *"deliberately not `loam-turn`"* (`EconomyHarnessTests.cs:14-16`). Nothing runs the report over the
  real `Step`.
- **Depends on:** `synthetic-graph`, `stock-deltas`, `world-stamp` (the trade on/off switch).
- **Touches:** `tests/FusionRpg.Core.Tests/World/Economy/` (new).
- **Acceptance (contract):** asserts only what economy-principles §13 makes a test — **P1**: no
  stock's net flow is monotone positive over the scripted run; **P6**: no single sink reason exceeds
  the ceiling share read from the report's tuning (a soft threshold, not a literal); plus the report's
  own arithmetic (sink shares sum to 1000‰; per-stock net flow equals the stock-delta sum). Binding
  frequency, payback and win rate are **printed with a verdict column, never asserted**. It never pins
  how many sectors, turns, buildings or goods the run had — it prints them. Until a trade capability
  ships, the on/off runs are identical and the report says so.
- **Verification:** `gk-core/tests/FusionRpg.Core.Tests` (World/Economy).

---

### 2.10 `system-commands`

**Capability.** The one shared path for **system-issued** world commands (round 4 Q10): a closed
system-kind registry, a command `Origin` (never on the wire), an admission arm that refuses system kinds
from every commander (`kind.system-only`), one Data filing function inside the caller's transaction that
bypasses only `world-continuity`'s not-active gate, and deterministic command ids. Reused by
`world-continuity` (`release-warden`) and `rift-trade` (`rift-window`, `rift-arrive`) — the whole closed set
(round 5 X11); `depart` and `advance` are the player's own orders.

- **State:** real gap (no system command exists; two programs each specified a different owner).
- **Depends on:** —
- **Spec:** [trade-foundation/spec-system-commands.md](trade-foundation/spec-system-commands.md).

### 2.11 `sector-features`

**Capability.** Round-4 principle B in one place: a closed `SectorFeature` vocabulary (storage, banking,
trade, caravans, cross-world, diplomacy, legion-equipment, plus `none` — `empire-seed`'s `featureUnlock`),
`StructureDef.FeatureUnlock`, tiers resolved from one
row's `variants`, a hashed per-slot tier, the `build`-on-own-slot upgrade, and one query
`SectorFeatures.TierOf(sector, feature)` / `FactionTier(world, faction, feature)` that every trade feature
gates on (answers `exchange` E-A14 and `fleet` A11). Here because `legion-build`
depends on this sub-program and not on `sector-yield`.

- **State:** real gap (Core ignores `anchor.variants`; no feature field).
- **Depends on:** — (external: `empire-seed` `band-reader`, `trade-structure-rows` for the `feature` key
  and per-variant bands).
- **Spec:** [trade-foundation/spec-sector-features.md](trade-foundation/spec-sector-features.md).

## 3. Dependency graph and build order

```text
synthetic-graph ---> step-benchmark
        |
        +------------------------------------------+
                                                   v
ledger-keys ---> stock-deltas ---> world-stock-ledger      economy-report
      |                |                ^  (SE4.12)            ^   ^
      |                +----------------|----------------------+   |
      |                                                             |
      +---> material-ledger (SE4.38)                                |
                                                                    |
routing-guard                     world-stamp ----------------------+

system-commands                   sector-features   (both independent; round 4)
```

**Build order:** `synthetic-graph`, `routing-guard`, `ledger-keys`, `world-stamp`, `system-commands`,
`sector-features` (independent, any order) → `step-benchmark`, `stock-deltas` → `economy-report` →
`world-stock-ledger` (it no longer waits for SE4.12, §7 S10) → `material-ledger` (when SE4.38 has landed).
`system-commands` must land before `world-continuity`'s `world-warden` migration and `rift-trade`'s
`rift-route`; `sector-features` before `sector-yield`'s `warehouse-axis` and `bank-points`.

`sector-yield` needs `world-stamp` (its behaviour is capability-gated), `ledger-keys`, `stock-deltas`
and `world-stock-ledger` (banking facts), `material-ledger` (crediting banked materials) and
`sector-features` (storage and banking tiers).

## 4. Tunables

This sub-program sets no balance number. The economy report's health ceilings (P6 share) are read
from a report tuning block in `data/tuning/trade.v1.json` (proposed; the file does not exist yet).
The one `TradeTuning` record and loader live at `src/FusionRpg.Core/World/Trade/TradeTuning.cs`; every
trade sub-program adds its block there (§8 R6). Tier costs and feature bands are `empire-seed`'s.

## 5. Owner questions

None. D-C (the stamp) is closed; the tuning-version meaning (X4) and the ledger owner column are
decided by principle above and stated as such.

**Owner-decided items recorded 2026-09-19 (map approval):**

1. **Stamp retirement (world-continuity's ask, `world-continuity-map.md` note 6).** Old ruleset code —
   the branch a capability flag replaces — retires only when **no world in any state** carries a stamp
   below that capability's ruleset. Hibernating and idle worlds keep their stamps; no world's stamp is
   migrated forward, on waking or otherwise. Decided by principle (a world keeps the rules it started
   on, D-C). Consequence: saves are local and there is no telemetry, so in practice a pre-capability
   branch is kept for the life of the product (`spec-world-stamp.md` §2). This supersedes the ideal's
   wording *"retires when no active world carries it"* (`trade-network-ideal.md` §14b).
2. **The difficulty profile id lives on this program's stamp** (`world-stamp`, column
   `difficulty_profile_id`); `world-continuity` `world-difficulty-profile` owns the catalog and its
   knobs.

## 6. DESIGN-GATE §5 checklist

```
[x] Subsystems: world turn engine, determinism guard, perf probe, world store, materials store,
    save identity keying, economy instrumentation.
[~] Session boundary: tasks/sessions/trade-network-idea-20260919.json covers docs/architecture/
    trade-network/**. session-boundary-check.py exits 1 on the crossing already recorded in that
    file (broad worktree lanes); this file is new.
[x] Read this session: economy-principles P13, P14, §12-§13; empire-resource-ssot; ssot-power-scale
    §10.4; spec-save-identity (new-table rule, classification, cross-program sweep); decisions.md rows
    :7, :80, :92, :108. Not read in full: data-architecture.md, software-architecture.md,
    tunables-ssot.md (rules taken from PRINCIPLES.md §5-§6).
[x] decisions.md checked: phase order lock (:7) — no phase is added here; stamp and ledgers add none.
[x] Every factual claim cites file:line (§1 table).
[x] audit-doc-citations.py --scope (2026-09-19): 0 HIGH on this map and on all nine specs; D1 hits are
    files the modules will create.
[x] Verified against code: PerfProbe's Stopwatch location, the guard's banned list, the four material
    writers, the ruleset literal, the replay refusal, the absence of other rpg_world_sectors writers.
[x] Surrounding sections read (the guard's scope comment; the replay refusal's delve branch).
[x] Constraints tested, not assumed: "a legacy stamp moves no golden" is an acceptance criterion to
    be proven by the suite, not a claim made here.
[x] No §2 invariant contradicted: timing lives outside the guarded tree; nothing reads the probe.
[x] Corrections propagated: umbrella map X3/X4 carry the stamp findings.
[x] No population pinned: the synthetic builder and the report print scale; only the closed factKind
    and capability-flag vocabularies are pinned, with their reason.
[x] No event-refreshed cache introduced.
[x] No ordering-fixed criterion: ledger idempotency is tested for re-commit in any order.
[x] ActorHub: not touched.
[x] No SOLID fork: PerfProbe is reused (no second timing facade); one ledger key grammar; the soul
    ledger pattern is reused, not re-invented.
[x] New rules with registry rows: routing-guard adds one; material-ledger's single-writer scan adds
    one. Both land with their modules.
```

## 7. Corrections found at spec time (2026-09-19)

Each was read in code while writing the module specs. The text in §1–§2 above is kept as approved; the
specs are authoritative where they differ.

| # | This map said | The code says | Resolved in |
|---|---|---|---|
| S1 | Synthetic worlds pass `WorldValidation.Validate` | Rule 13 resolves the tier from `WorldTemplateCatalog.SizeIdOf`, which throws for any non-shipped template id (`gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:25-30`) | `spec-synthetic-graph.md` §3: validate with `Map with { RequireTemplateSize = false }` and assert the tier range directly |
| S2 | — | A shape-only `SyntheticWorld` class already exists in the Release bench (`gk-core/tests/FusionRpg.Bench/WorldGraphWriteBench.cs:553`); the bench has no `InternalsVisibleTo` | the builder is named `SyntheticGraph`, uses public API only, and is source-linked into the bench |
| S3 | — | `gk-core/tests/FusionRpg.Bench/**` has no verification boundary (`verify-change.ps1 -PlanOnly` stops on it) | `spec-step-benchmark.md` maps its own files; the older bench files stay their owners' gap |
| S4 | The routing guard is an xunit test with one registry row | Enforcement-registry guards resolve to `scripts/guard-*.ps1` only (`gk-core/tests/FusionRpg.Guard.Tests/EnforcementRegistryGuardTests.cs:53`) | `spec-routing-guard.md`: a script + JSON registry; the xunit file holds falsifiers |
| S5 | "A non-legacy stamp changes the hash" | Hashing provenance would move every store-created world's hash for values `Step` never reads, and break Data tests comparing a commit with a pure `Step` (`WorldCanonical.cs:90-94` records this failure once already) | `spec-world-stamp.md` §3: hash only the granted capability set and a non-default difficulty; no hash moves until the first capability ships |
| S6 | The stamp migration backs up the database and runs in one transaction | Nothing is rewritten: additive columns whose defaults read `legacy`; `decisions.md:90` reserves backup + marker for key-widening | `spec-world-stamp.md` §4 |
| S7 | Replay "refuses, with a reason" | `GetWorldTurnReport` returns `null` with no reason (`RpgStore.WorldTurns.cs:759-760`) | a pure `WorldReplayGate` with a closed reason enum; the store keeps its `null` contract |
| S8 | — | The diff writer's equivalence guard copies four header fields onto the reloaded world (`RpgStore.WorldGraphDiff.cs:58-61`) | it must copy `Stamp` too, or the first capability row trips its assert (`spec-world-stamp.md` §4) |
| S9 | Ledger key `(…, sector, good)` | Legions hold loam too (`WorldState.cs:327`) | `spec-ledger-keys.md`: `sector` widened to **holder** (`s:`/`e:`) |
| S10 | `world-stock-ledger` needs SE4.12 for owner columns | With the owner as a world faction id and the save as `rpg_worlds.player_id`, no `rpg_save_empires` row is needed to write; the empire half of closure is SE4.41's | `spec-world-stock-ledger.md`: can land before SE4.12 |
| S11 | Four writers of `rpg_creature_materials` | Six SQL writes: the four runtime writers, the `ShardRungs` migration (`gk-core/src/FusionRpg.Data/Sqlite/Migrations/ShardRungs.cs:60-99`) and the `Reset` wipe (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:1032`) | `spec-material-ledger.md` routes the migration through the verb and allow-lists the reset `DELETE` |
| S12 | The determinism guard bans five symbols | It bans eight, including `Environment.TickCount` (`WorldDeterminismGuardTests.cs:39-49`) | no design change |
| S13 | `RulesetVersion = 12` at `TurnEngine.cs:114` | `RulesetVersion = 13` at `TurnEngine.cs:125` (warden-freeze-fix, `d6931e43`); every `TurnEngine.cs` line after `:21` moved by +11 (+13 after the old `:425`) | Citations in this map and its specs re-pointed (§8 R7) |

## 8. Reconciliation 2026-09-19 (round 4)

Applied from [decisions-round-4.md](decisions-round-4.md), which wins over any spec. Cross-checked against
every other trade-network, `world-continuity`, `legion-build` and `empire-seed` spec.

| # | Change | Where |
|---|---|---|
| R1 | **New module `system-commands`** (Q10): the one system-issued command path — closed kind registry, `Origin`, `kind.system-only` admission, `FileSystemCommandUnlocked`, deterministic ids. Reused by `world-continuity` and `rift-trade` | §2.10; `spec-system-commands.md` |
| R2 | **New module `sector-features`** (principle B): one feature vocabulary, tiers as one row's variants, the per-slot tier, the upgrade rule, `TierOf` — the single gate every building-unlocked feature reads | §2.11; `spec-sector-features.md` |
| R3 | `ledger-keys` lists every fact kind other programs asked for (`bank`, `income`, `deliver`, `loss`, `refine`, `carry`, `consume`, `sink`, `collapse`, `settle-buy`, `settle-sell`, `fee`, `tariff-grant`, `tariff-sink`, `rift-depart`, `rift-arrive`) and accepts a third holder `f:` for faction-held stocks (counterparties A10) | `spec-ledger-keys.md` §4a |
| R4 | `world-stamp` lists every requested capability flag, adds `trade.incomeParity` (ordered after `trade.logistics`), and separates stamp capabilities from `trade-surface`'s UI `TradeCapabilities` | `spec-world-stamp.md` interface |
| R5 | `synthetic-graph` text here aligned with its spec: exactly one dominant `Zomboss` empire plus N rivals and M clans (counterparties A4) | §2.1 |
| R6 | One `TradeTuning` location (`World/Trade/TradeTuning.cs`); three specs had named three paths | `spec-economy-report.md`; sector-yield `warehouse-axis`; logistics-flow `lane-flow` |
| R7 | Stale `TurnEngine.cs` citations re-pointed after the `RulesetVersion` 13 bump; `WorldCommand.cs`, `WorldCommandAdmission.cs`, `WorldState.cs`, `LoamPhases.cs`, `WorldDtos.cs` line drift fixed the same way | this map and its specs (S13) |
| R8 | `stock-deltas` answers `world-continuity` `coarse-step`: production and upkeep are already separable by fact kind | `spec-stock-deltas.md` §5 |

**Closed vocabularies this reconciliation widens or creates** (each pinned with its reason, each moved
only by a reviewed change): `SectorFeature` (new, 8 members: `none` + seven features); `SystemCommandKinds` (new, shipped empty;
members added by `world-continuity` and `rift-trade`); `CommandOrigin` (new, 2); `FactKinds` (§4a list, each
with its emitter); `StockHolderKind` (+`Faction`, with `empire-treasury`) and the ledger holder prefix `f:`;
`WorldCapabilityRegistry` (+`trade.incomeParity` and the rows in `spec-world-stamp.md`); build refusal
reason `build.max-tier`; admission reasons `kind.system-only`, `kind.not-system`.

**Cross-cluster items this map cannot fix (other owners' files):**

- *(Resolved concurrently, verified 2026-09-19.)* `world-continuity/spec-world-state-vocabulary.md` §5,
  `spec-coarse-step.md` §3, `rift-trade/spec-rift-route.md` and `spec-crossing-handoff.md` now cite this
  sub-program's one system-command path (Q10). `rift-trade-map.md` A7 is retargeted too and says the module id does not
  exist yet: it is `system-commands` (§2.10); A7 can cite it.
- `counterparties/spec-empire-treasury.md` uses one `settle` kind; `exchange/spec-settlement-payment.md` asks
  for five settlement kinds. Recommended: exchange's kinds; the treasury re-points. *(Ruled 2026-09-20, X2:
  exchange's five kinds; `empire-treasury` re-pointed in round 5.)*
- `empire-seed/spec-trade-structure-rows.md` (updated concurrently) now emits the seven feature rows with
  `featureUnlock` and closed tier `variants`; `sector-features` adopts its names. It leaves the **upgrade
  verb** out of scope — `sector-features` §4 specifies it (`build` on the own slot); the world-map owner of
  `BuildResolver` should confirm. *(Ruled 2026-09-20, X8: `build` on the own slot; world-map confirms.)*
- **One gate, not a `StructureKind` per building:** `exchange` (`StructureKind.Exchange`, `Hubs.TradeTier`),
  `fleet` (`StructureKind.Depot`, `BestTier`), `counterparties` (`StructureKind.Embassy`,
  `DiplomacyGate.TierOf`) and `rift-trade` (`StructureKind.RiftAnchor`) each name their own kind and tier
  read. Recommended: their tier reads delegate to `SectorFeatures.TierOf`/`FactionTier` (which `exchange`
  E-A14 and `fleet` A11 asked for); a new `StructureKind` only where the loam/siege economy needs one.
  *(Ruled 2026-09-20, X1: every feature gate reads `sector-features`; `fleet`, `counterparties` and
  `rift-trade` re-pointed in round 5; `exchange` is its own session's.)*
- *(Fixed 2026-09-20, X6.)* The umbrella placed income parity in `logistics-flow` (§1) and cited
  `RulesetVersion` 12 at `:114` (X3); it now names `sector-yield` and `RulesetVersion` 13 at
  `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:125`.
- `trade-surface/spec-trade-unlock.md`'s `TradeCapabilities` names should not reuse stamp capability names.

**Owner questions:** none new here. The feature vocabulary and the upgrade rule follow the round-4 table
directly; their owner-facing questions (start-of-play buildings, no base storage) are asked in
[sector-yield-map.md](sector-yield-map.md) §5c.

## Round 5 (2026-09-20)

Applied from [decisions-round-4.md](decisions-round-4.md) "Round 5" (R5-A, R5-X), which wins over any spec.
Code citations touched were re-opened on `features/mega-merge`.

| # | Change | Where |
|---|---|---|
| F5-1 | **X1:** `sector-features` is the one gate every building-unlocked feature reads (`TierOf`, `FactionTier`); a new `StructureKind` only for loam/siege behaviour. Consumer specs in `fleet`, `counterparties`, `rift-trade` and `sector-yield` now delegate to it | `spec-sector-features.md` header; §2.11 |
| F5-2 | **X8:** the upgrade verb is `build` on the building's own slot; the `world-map` owner of `BuildResolver` is asked to confirm | `spec-sector-features.md` §4 |
| F5-3 | **B1/B2 (noted):** a row allowed on several slot kinds needs `RequiredSlotKind` widened to a set (`gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:82-89`) — `empire-seed` and `world-map`'s change; the upgrade arm never re-checks the slot kind | `spec-sector-features.md` §4 |
| F5-4 | **X11:** `SystemCommandKinds` is exactly `release-warden`, `rift-window`, `rift-arrive` once all owners ship; `depart` and `advance` are player orders and never members (asserted) | `spec-system-commands.md` §2, acceptance 8; §2.10 |
| F5-5 | **X2:** the ledger's settlement fact kinds are `exchange`'s five (`settle-buy`, `settle-sell`, `fee`, `tariff-grant`, `tariff-sink`), already listed in `spec-ledger-keys.md` §4a; no one-kind `settle` | cross-cluster note above |

**Closed vocabularies:** `SystemCommandKinds` is now a closed set of three (was "shipped empty; members
added by owners" — still shipped empty, but its full membership is ruled).

**Still other owners' files:** `world-continuity` must drop the `advance-carry` departure as a system kind
(X11) and place the A1 seat start kit at world creation; `world-map` confirms the upgrade verb (X8).

## Audit 2026-09-20

An independent audit of this map and its eleven specs against CLAUDE.md, AGENTS.md, DESIGN-GATE §2–§5,
PRINCIPLES, tunables-ssot, validation-ssot, the test-substrate standard, economy-principles,
`ssot-power-scale.md` §10–§11 and the round-4/5 register, with the load-bearing claims re-opened in code on
`features/mega-merge`. `audit-doc-citations.py --scope` reported 0 HIGH on every file before and after
the edits. Specs win over §1–§8 where they differ; the rows below say where each fix landed.

| # | Severity | Finding | Fix |
|---|---|---|---|
| TF-A1 | Critical | `world-stamp` grants a capability when `stamp.RulesetVersion >= IntroducedAtRuleset`, but `sector-yield` `banking-fact` and `logistics-flow` `logistics-phase` said their capabilities ship **without** a `RulesetVersion` bump. Followed literally, the row would sit at the current ruleset and every world already stamped at it — created before the behaviour existed — would gain it mid-life and move its hash: the D-C breach the stamp exists to stop | `spec-world-stamp.md` §2 "The bump is mandatory" and acceptance 11 (no retroactive grant, both directions tested); the consumer specs corrected (see the sector-yield and logistics-flow audits). Owner question OQ1 below asks whether to keep this model or store the capability set |
| TF-A2 | Critical | Nothing recorded goods **in transit**: a logistics departure would take stock out of a warehouse with no holder to receive it, so `stock-deltas`' reconciliation and `world-stock-ledger`'s per-holder sums would fail on the first logistics turn, and lane loss and waste had no ledger trace | `spec-ledger-keys.md` §4a: route holder `r:` (injective, length-prefixed body) and kinds `depart`, `deliver`, `waste`, `return`; `spec-stock-deltas.md` §5: `StockHolderKind.Route`, `Holdings` walk `WorldState.Transit`. The recording lands in `logistics-flow` (`transit-buffer` §5a) |
| TF-A3 | Major | `sector-features` stored one tier per slot and reused `ConstructionTurnsRemaining` for upgrades without saying what the tier means mid-upgrade, so "first build" and "upgrade" were indistinguishable; and every existing active-structure gate (`LoamProduction.cs:34`, `:51`; `LoamPhases.cs:92`; `SectorItemCapacity.cs:20`; `WonderEmpireEffects.cs:25`; `Habitability.cs:22-23`; `GrowthPhases.cs:92`) treats a counter above 0 as **off**, contradicting §4's "an upgrade never switches a building off" | `spec-sector-features.md` §3: `StructureTier` is the target tier; one `ActiveTier(slot)` read; every gate moves to `ActiveTier >= 1` in the upgrade change (identical at tier 1, so no golden moves); acceptance 7 and 10 |
| TF-A4 | Major | A cleared or replaced structure kept its tier: `LoamPhases.cs:224` (sector lost) and `BattleApplication.cs:165-172` (an assault destroys or places a structure) set `StructureId` with no tier rule, so a rebuilt building would inherit a stale tier | `spec-sector-features.md` §3 reset rule; acceptance 8 with a source scan |
| TF-A5 | Major | `gk-core/data/tuning/**` has **no** verification boundary (`verify-change.ps1 -PlanOnly -AllowUnscoped -Paths gk-core/data/tuning/world.v6.json` stops with *"VERIFICATION BOUNDARY MISSING"*, run in this audit), so the first `trade.v1.json` publish would stop at verification; the matcher takes exact paths and `dir/**` only (`scripts/verify-change.ps1:70-75`) | `spec-economy-report.md` Test plan: owner row `core-trade-tuning` listing each published `trade.v{n}.json` as an exact path; `sector-yield` `warehouse-axis` repeats it for whichever module creates the file |
| TF-A6 | Major | A banking credit of materials had no account-scope grammar: `material-ledger`'s `source_kind` list had no banking source, and `banking-fact` keyed its material credit with a **world** key | `spec-ledger-keys.md` §4a and `spec-material-ledger.md` §3: account fact `grant` / `world-bank` / sourceId = the world `bank` key; `source_kind` pinned as a closed vocabulary |
| TF-A7 | Major | `economy-report` computed only P1, P6, binding, P8 and win rate; economy-principles §13 also names **P2** (income vs upkeep growth, the rule the territorial economy rests on) and **P9/P12** yield concentration, and nothing measured the PS-5 pairing of the essence loop, whose faucet and sink read different Θ indices (round 4 Q7) | `spec-economy-report.md` §3: three printed rows with verdicts (never asserted: §13 makes only P1 and P6 a test); acceptance 7 |
| TF-A8 | Minor | `ledger-keys` still carried a stale "Conflict, not resolved here … reported for adjudication" paragraph after X2 resolved it, listed `settle` (no longer a kind) in §4, and acceptance 3 named only `s:`/`e:` | Rewritten to the resolved state; acceptance 3 reads "a registered prefix" |
| TF-A9 | Minor | `sector-features` said "null feature" where the vocabulary has `none`, and its checklist called an eight-member vocabulary "seven-member"; its registry row was an unticked box | Wording fixed; a concrete guard `feature-gate-one-read` and invariant `tn-feature-gate-one-read` specified (acceptance 9); `Unlocks` and `ActiveTier` added so a summing consumer never reads the raw fields |
| TF-A10 | Minor | `world-stamp`'s Dependencies table was split by a prose paragraph, leaving four interface rows orphaned below it | Rows moved back into the table |
| TF-A11 | Minor | `stock-deltas` did not say what a holder-keyed ledger cannot answer: a capture moves no stock, so a per-owner balance is not derivable from deltas | `spec-stock-deltas.md` §5 "What the record does not answer"; `spec-world-stock-ledger.md` acceptance 8 (per holder, not per owner) |
| TF-A12 | Minor | §2.5 of this map still lists `halt` and `settle` as fact kinds | Superseded by `spec-ledger-keys.md` §4 and §4a (a halt moves no stock; X2 retired `settle`); the approved text is left as it is and recorded here |
| TF-A13 | Minor | `world-stock-ledger`'s checklist said "no new guarded rule", while `material-ledger`'s `ledger-writers` registry already lists `rpg_world_stock_ledger` | Checklist corrected to cite that row |

**Checked and found sound** (no change): the no-timing-assert rule and determinism proof in
`step-benchmark` (the `Stopwatch` stays in `Core/Diagnostics`, `gk-core/src/FusionRpg.Core/Diagnostics/PerfProbe.cs:1`,
`:112`); the routing guard's shrink-only allow-list; in-memory store tests and the failed-delete rule in
every Data spec; `long`, `checked` and divide-last in every quantity; closed vocabularies pinned with a
reason and no population pinned anywhere; `system-commands`' admission-only enforcement; the synthetic
builder's catalog-read ranges. Everything here is RPG layer only; nothing touches PvZ, ActorHub or the
Funnel.

**Could not fix here (other owners' files):**

- `docs/architecture/decisions.md:7` cites `TurnEngine.cs:180-195` for the phase list; the calls are at
  `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:191-207` today. `sector-yield` `banking-fact` amends that row,
  so it should re-point the citation in the same change.
- The active-gate moves of TF-A3 touch world-map, loam and siege files (`LoamProduction.cs`, `LoamPhases.cs`,
  `SectorItemCapacity.cs`, `WonderEmpireEffects.cs`, `Habitability.cs`, `GrowthPhases.cs`,
  `BattleApplication.cs`); `sector-features` makes them in its change with those owners' agreement.

**Owner question raised by this audit:**

- **OQ1 — How does a world's stamp say which capabilities it has?** (a) **Keep the ruleset model**
  (`world-stamp` as written, now with the mandatory bump): each capability ships with one `RulesetVersion`
  bump; the cost is that trimmed turn reports logged before a bump are no longer re-derived, the cost every
  earlier bump paid (twelve, from ruleset 1 to 13). (b) **Store the granted set on the stamp** at world creation (a
  `stamp_capabilities` column): no bump is ever needed and no report stops re-deriving, at the price of a
  second column and restating the recorded retirement rule as "no world whose stamp lacks the capability".
  (c) A hybrid: the ruleset gates code changes, the stored set gates trade capabilities.
  **Recommendation: (a).** It is what the approved `world-stamp` and the owner's recorded retirement rule
  (§5 item 1, phrased in rulesets) already describe, its only cost is one this repo has accepted at every
  earlier bump, and the specs are now consistent with it.

---

## Round 6 (2026-09-20)

Applied from [decisions-round-4.md](decisions-round-4.md) "Round 6", which binds this map and its eleven
specs. The family's single landing order is [landing-order.md](landing-order.md); this sub-program is row
0a of its §2 (plus `material-ledger` at row 0f).

| # | Decision | What changed here |
|---|---|---|
| **C1** | One capability flag and one ruleset bump per wave | `spec-world-stamp.md`'s requested-rows table is replaced: one flag per wave, its owner and its landing-order row, with the two rules (a flag never spans waves; a wave takes exactly one bump, shared by its rows). The 2026-09-19 list — one `trade.sectorYield` over four sector-yield waves, one `trade.logistics` over four, one `counterparties.clans` over two, one `counterparties.diplomacy` over two — is withdrawn and the withdrawals are named. **This answers OQ1 as option (a)**: the ruleset model stays, with per-wave bumps; `spec-world-stamp.md` §Hard edges now orders the re-bless per wave |
| **C2** | One neutral `StructureKind.Feature`; `StructureKind.Exchange` withdrawn | `spec-sector-features.md` §Dependencies: the *"Not a `StructureKind`"* block is rewritten. A row cannot load without a kind (`gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:51`, `gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:65`, `:330` for `IsKnown`), so all feature rows load as `Feature`, whose precedent is `Obstacle` (`gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:38`). **X1's amended wording is quoted there**, for every spec that cites the rule: *a new `StructureKind` only where loam or siege rules need one — plus the one neutral `Feature` kind, which no gate reads* |
| **C3** | Banking waits on the save-identity re-key | `spec-material-ledger.md` §Dependencies: the landing order (SE4.12 → SE4.38 → this module → `banking-fact`'s step half), the refusal of the audit's option (b) (no double-edited writer sites), and the interim behaviour — nothing leaves the map, `economy-report` prints a banked zero **with the reason**, `bank-points` keeps answering so the first-throttle answer stays buildable |
| **S1** | A building counts for nobody until one faction owns both its sector and its slot | `spec-sector-features.md` new §5a: `CountsFor` and `TierFor` over `WorldSlot.OwnerFactionId` (`gk-core/src/FusionRpg.Core/World/WorldState.cs:105`) and `WorldSector.OwnerFactionId` (`:158`). **Every gate in the family reads `TierFor`/`FactionTier`**; bare `TierOf` stays for non-gate ground reads (report, inspector, editor, the *build a Counting House here* answer) and a gate that uses it is a defect. Acceptance 2a |
| **L6** | Forging a standard needs its own building | `spec-sector-features.md` §1: the closed vocabulary becomes **nine** members (`standards` added, the Standard Hall's feature); acceptance 1 updated. Its maximum tier is `legion-build` `legion-standards`' to state — an ask, not a number invented here |
| **D2** | Six `world.*` channels compose in `ActorHub` | Nothing in this sub-program reads them. `sector-features` is a structure query; the consumers that read a world channel (`fleet` `crew`/`depot`/`carried-goods`, `logistics-flow` `lane-loss`, `rift-trade` `crossing-anchor`) state their default in their own specs |

**Not changed, and why.** `world-stamp` still takes no bump of its own (R3 of the landing order: the
registry ships empty, so `GrantedBy` is empty and no hash moves, `spec-world-stamp.md` §3).
`step-benchmark` and `stock-deltas` keep their *"no `RulesetVersion` bump"* lines: those waves grant no
capability, which is the one case the landing order still allows the phrase.

**Build order correction (audit M5).** `sector-features` is **not** "independent, any order": it depends on
`empire-seed` `band-reader` and on the `featureUnlock` / `variants` / `requiredSlotKinds` schema widening,
and its acceptance 1 is a join against that vocabulary. The widening is split out of
`trade-structure-rows` as its own step and lands first (landing order rows 0b → 0a's `sector-features` →
0c). §3's *"(independent, any order)"* covers `synthetic-graph`, `routing-guard`, `ledger-keys`,
`world-stamp` and `system-commands` only.
