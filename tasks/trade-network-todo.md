# Trade-network family — build todo

**Program:** `trade-network` (the umbrella; the family also covers `world-continuity`, `legion-build` and
`empire-seed`) · **Written** 2026-09-20 · **162 tasks** · Plan:
[trade-network-plan.md](trade-network-plan.md)

This is the family's implementable task list: one task per module landing, each with its spec, its wave and
the flag and ruleset bump that wave carries, its dependencies, the acceptance criteria its spec states, the
exact `verify-change.ps1` line that proves it, the shared files it touches and the notes a lane needs at the
keyboard. It decides nothing on its own. **[docs/architecture/trade-network/landing-order.md](../docs/architecture/trade-network/landing-order.md)
owns the order** — the wave sequence, one capability flag and one ruleset bump per wave, the shared-file
landing order, one creator per tuning file, the golden re-bless points and the cross-program blockers — and
**[trade-network-plan.md](trade-network-plan.md) owns the phases and the checkpoints**, whose pass conditions
are quoted below rather than reworded. Where a sub-program map disagrees with the landing order about order,
the landing order wins; the map wins about what a module does. The twenty reconciliation rulings this file was
assembled under are recorded in landing-order §10, and every task that one of them changed says so in its own
Notes.

**Bump ordinals are ordinals, never literals.** The trade-network spine reads `N+1` … `N+25`, the
legion-build lane `L1` … `L10` and the world-continuity lane `C1` … `C4`; `empire-seed` bumps nowhere. A lane
that bumps **rebases onto the live `TurnEngine.RulesetVersion` and takes the next integer**, and its
capability row references that constant. The ordinal fixes the order, which is what a stamped world's rules
depend on.

## Task-id index

| Phase | Landing-order rows | Task-id range | Tasks |
|---|---|---|---|
| **0 — Foundation and content** | 0a, 0b, 0c, 0d, 0e, 0f, 0g, and the lane waves ES2–ES6, L2–L5, L8, L9, WC2–WC4 | `0a.1`–`0a.9`, `0b.1`–`0b.10`, `0c.1`, `0d.1`, `0e.1`–`0e.3`, `0f.1`–`0f.3`, `0g.1`, `ES2.1`–`ES6.1`, `L2.1`–`L5.1`, `L8.1`, `L9.1`, `WC2.1`–`WC4.2` | **53** |
| **1 — The sector economy** | 1, 2, 3, 4, and lane wave L6 | `1.1`–`1.6`, `L6.1`–`L6.2`, `2.1`, `3.1`, `4.1` | **11** |
| **2 — The lane layer** | 5, 6, 7, 9 | `5.1`–`5.2`, `6.1`–`6.5`, `7.1`–`7.3`, `9.1`–`9.2` | **12** |
| **3 — Outflow** | 8, and lane wave L10 | `8.1`, `L10.1`–`L10.2` | **3** |
| **4 — Located income and fleet** | 10, 11, 12, 13, 14, and lane wave L7 | `10.1`, `11.1`, `L7.1`, `12.1`–`12.2`, `13.1`–`13.2`, `14.1`–`14.3` | **10** |
| **5 — Counterparties** | 15, 16, 17, and lane waves WC5–WC8 | `15.1`–`15.5`, `16.1`–`16.3`, `WC5.1`–`WC5.2`, `WC6.1`–`WC6.3`, `WC7.1`, `WC8.1`, `17.1`–`17.3` | **18** |
| **6 — Market and AI** | 18a–18d, 19a–19e | `18a.1`–`18a.5`, `18b.1`–`18b.2`, `18c.1`–`18c.4`, `18d.1`, `19a.1`–`19a.3`, `19b.1`–`19b.2`, `19c.1`–`19c.2`, `19d.1`, `19e.1`–`19e.2` | **22** |
| **7 — Cross-world** | 20, 21, 22, 23 | `20.1`–`20.3`, `21.1`–`21.2`, `22.1`–`22.3`, `23.1` | **9** |
| **8 — Surface and stories** | 24a–24e, 25a–25d | `24a.1`–`24a.2`, `24b.1`–`24b.4`, `24c.1`–`24c.3`, `24d.1`–`24d.3`, `24e.1`–`24e.2`, `25a.1`, `25b.1`–`25b.4`, `25c.1`–`25c.3`, `25d.1`–`25d.2` | **24** |
| | | | **162** |

Three things the index will not tell you, so they are here:

- **A task id is the landing-order row plus an index inside it**, not a global sequence. `0d.1` is the only
  task of row 0d; `L4.3` is the third task of legion wave L4. Reconciliation R-1 renumbered the phase-0 rows,
  so `sector-features` is `0d.1` (it was `0a.10`), legion W1 is `0e.*`, world-continuity W1 is `0f.*` and
  `material-ledger` is `0g.1`.
- **Ids are never renumbered to match a landing order.** Inside wave 19a the landing order is
  `19a.1 → 19a.3 → 19a.2`, because R-4 made `ai-spend-limit` the creator of `gk-core/data/tuning/ai.v3.json` and a
  publisher cannot precede its creator. Read the order the file presents, not the numbers.
- **The lane waves run in parallel with the trade spine.** They appear in the phase whose stretch of the
  landing order contains them, but a lane wave is **not** a condition of that phase's checkpoint unless the
  plan's §3 names it.

## How to pick up a task

1. **Read the spec** the task names, whole. The acceptance bullets here are compressed from it and are not a
   substitute for it.
2. **Read the `DESIGN-GATE.md` §1 row for its subsystem** — in this session, not from a summary. The
   sequence is read → verify against code → change. Then complete the §5 checklist before you present
   anything; an honest gap costs a sentence.
3. **Record the session boundary** in `tasks/sessions/<session>.json` before the first edit, with `paths`
   fenced to the wave you are landing, and validate with `python scripts/session-boundary-check.py`. Several
   programs share this tree: never `git add -A`, never stash or reset around another session's dirty files.
4. **Land the wave's one bump by rebasing.** Read the live `TurnEngine.RulesetVersion`
   (`gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:125`), take the next integer, and have every capability row
   the wave registers reference that constant — never a literal, and never the `N+k` or `L`/`C` ordinal from
   this file. One wave at a time on that file; if another wave landed while you worked, rebase again.
5. **Run the task's own `Verify` line** — `.\scripts\verify-change.ps1 -Paths <every added or modified path>
   -Session <session-id>` — plus any guard or audit the task names. That is the default for every ordinary
   edit. An unmapped path is a verification-boundary defect to fix **in the task** (add the owner row; it is
   this family's own work under R-17), never a reason to widen the suite. The full suite runs at three points
   only: finishing a phase, a change that genuinely crosses program boundaries, and immediately before a
   live probe.
6. **Commit with explicit paths**, one logical change per task: code, evidence and the ledger line together.
   Plain `git`, never `git add -A`, never amend, no attribution trailer. Push and PR only when asked.
7. **Tick the checkbox here in that same commit**, and if what you verified contradicts a spec, a map or this
   file, fix that text in the same change. Never leave a known-stale claim for the next session.

---

## PHASE 0 — Foundation and content

Landing-order rows **0a–0g**, plus the `empire-seed`, `legion-build` and `world-continuity` lane waves
that anchor in this stretch (**ES2–ES6**, **L2–L5**, **L8–L9**, **WC2–WC4**). 53 tasks.

The lane waves run **in parallel** with the trade spine — nothing in rows 1–25 waits for them and they do
not wait for each other beyond the *Lands after* column of landing-order §2. They are **not** conditions of
Checkpoint 0: the plan's §3 phase-0 condition is about the registry, the feature rows, the start kit and the
verification boundaries.

---

## Row 0a — `trade-foundation` W0 (measurement, stamp, ledgers)

Whole row: **no capability flag, no ruleset bump** (landing order §2 row 0a — the capability registry ships
empty, so `GrantedBy` is empty and no hash moves). Each task restates its own R3 reason.

### [ ] 0a.1 `synthetic-graph` — a valid deterministic world at any size tier, plus a campaign driver
- **Spec:** docs/architecture/trade-network/trade-foundation/spec-synthetic-graph.md
- **Wave:** row 0a · no flag, no bump (R3: test-only builder; nothing in `src/` changes)
- **Depends on:** nothing
- **Acceptance:** every tier's `Build` passes `WorldValidation.Validate(world, SyntheticGraph.Profile)` with the sector count inside the tier's catalog-read `[MinNodes, MaxNodes]` · same `(tier, seed, options)` gives byte-identical `WorldCanonical.Write`, a different seed does not · at `giant` every `LaneTypeCatalog.All` id appears and exactly one `Zomboss` faction exists whatever `RivalEmpires` is; counts are printed, never asserted.
- **Verify:** `.\scripts\verify-change.ps1 -Paths tests/FusionRpg.Core.Tests/World/Synthetic/SyntheticGraph.cs,tests/FusionRpg.Core.Tests/World/Synthetic/SyntheticCampaign.cs,tests/FusionRpg.Core.Tests/World/Synthetic/SyntheticGraphTests.cs,gk-core/scripts/verification-boundaries.v1.json -Session <session-id>`
- **Shared files:** none
- **Notes:** lands the `world-synthetic` owner row (else the path falls to `core-tests-fallback`, the whole Core suite). Rule 13 is skipped by `Map with { RequireTemplateSize = false }`, never by registering a synthetic id in `WorldTemplateCatalog`.

### [ ] 0a.2 `routing-guard` — the logistics namespace is born unable to call `ReconnectionCost`
- **Spec:** docs/architecture/trade-network/trade-foundation/spec-routing-guard.md
- **Wave:** row 0a · no flag, no bump (R3: a source-scan guard, no runtime code)
- **Depends on:** nothing
- **Acceptance:** a fixture file with `ReconnectionCost.For(` under a guarded path exits 1 and names the file; the same text in a `//`, `///`, `/* */` or string literal exits 0 · a caller outside every guarded path and absent from `allowedCallers` exits 1, and an `allowedCallers` entry with no remaining reference also exits 1 (shrink-only) · on the real tree it exits 0, and `EnforcementRegistryGuardTests` R1/R5/R6/R8 pass with the new guard and invariant row.
- **Verify:** `.\scripts\verify-change.ps1 -Paths scripts/guard-logistics-routing.ps1,scripts/logistics-routing.v1.json,gk-core/scripts/enforcement-registry.v1.json,tests/FusionRpg.Guard.Tests/LogisticsRoutingGuardTests.cs,gk-core/scripts/verification-boundaries.v1.json -Session <session-id>` then `.\scripts\guard-logistics-routing.ps1`
- **Shared files:** none
- **Notes:** `scripts/guard-*.ps1` has **no** owner mapping today (checked: `guard-dal.ps1` and `guard-actor-hub.ps1` both resolve to nothing), so the `guard-logistics-routing` owner row is part of this task. The map's "xunit guard with one registry row" is corrected in the spec: registry ids resolve only to `scripts/guard-*.ps1`.

### [ ] 0a.3 `ledger-keys` — one dedupe-key grammar and one closed fact-kind vocabulary
- **Spec:** docs/architecture/trade-network/trade-foundation/spec-ledger-keys.md
- **Wave:** row 0a · no flag, no bump (R3: pure Core types, no I/O, nothing hashed)
- **Depends on:** nothing (`SaveId` from save-identity SE4.11, done)
- **Acceptance:** injective over generated facts including ids containing `|`, `:`, `-`, empty strings and nulls · `Decode(Encode(f)) == f` for every valid fact, and a truncated or altered key throws · `Encode` throws for an unknown kind, a kind in the wrong scope, a missing required field, a field of the other scope, a negative turn or a holder without a registered prefix; keys are identical under two `CultureInfo`s.
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Ledger/LedgerFact.cs,src/FusionRpg.Core/World/Ledger/LedgerKey.cs,src/FusionRpg.Core/World/Ledger/FactKinds.cs,tests/FusionRpg.Core.Tests/World/Ledger/LedgerKeyTests.cs,gk-core/scripts/verification-boundaries.v1.json -Session <session-id>`
- **Shared files:** none
- **Notes:** `FactKinds` and `LedgerScope` counts are pinned **with the closed-vocabulary reason**; every later widening (`bank`, `income`, `depart`/`deliver`/`waste`/`return`, the `f:`/`r:` holder prefixes) moves the pin in the change that ships its emitter, not here.

### [ ] 0a.4 `world-stamp` — every world says which rules it runs on
- **Spec:** docs/architecture/trade-network/trade-foundation/spec-world-stamp.md
- **Wave:** row 0a · no flag, no bump (R3: `WorldCapabilityRegistry.Shipped` is empty, so no capability is granted and no hash moves — spec §3)
- **Depends on:** nothing
- **Acceptance:** a world created through `CreateWorld` stores `stamp_kind='stamped'`, `ruleset_version = TurnEngine.RulesetVersion` (read, never a literal), the loaded manifest's canonical text and the template's current version; `CreateWorld` refuses a legacy or out-of-range stamp and writes nothing · after `EnsureColumn` every pre-existing map and delve world loads as `WorldStamp.Legacy`, schema setup twice changes nothing, and a legacy world — and a stamped world granting nothing at the default difficulty — hashes byte-identically with every existing golden green unedited · no retroactive grant: for every row `0 < IntroducedAtRuleset <= TurnEngine.RulesetVersion`, a world stamped at *N−1* is not granted a row introduced at *N* and one stamped at *N* is (both directions).
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Stamp/WorldStamp.cs,src/FusionRpg.Core/World/Stamp/WorldCapabilityRegistry.cs,src/FusionRpg.Core/World/Stamp/WorldReplayGate.cs,gk-core/src/FusionRpg.Core/World/WorldState.cs,gk-core/src/FusionRpg.Core/World/WorldCanonical.cs,gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldGraphDiff.cs,gk-core/src/FusionRpg.Server/Program.cs,tests/FusionRpg.Core.Tests/World/Stamp/WorldStampTests.cs,tests/FusionRpg.Data.Tests/World/WorldStampStoreTests.cs -Session <session-id>` then `.\scripts\guard-dal.ps1`
- **Shared files:** WorldState.cs (`Stamp` field, 0a) · WorldCanonical.cs (**slot 1** of §4: the stamp row, after the `sector-ironwork` loop) · TurnEngine.cs (capability read) · RpgStore.WorldTurns.cs (replay, `tuning_digest`)
- **Notes:** crosses Core + Data + Server — full suite once at module end. The diff writer's equivalence guard and `LoadWorldState` must copy `Stamp` with the four header fields they already copy, or the first capability row trips the assert.

### [ ] 0a.5 `system-commands` — one path for a system-issued world order
- **Spec:** docs/architecture/trade-network/trade-foundation/spec-system-commands.md
- **Wave:** row 0a · no flag, no bump (R3: the kind registry ships empty; `Origin` is not hashed, and the admitted commands are what the hash already reflects)
- **Depends on:** nothing
- **Acceptance:** a player submission or AI policy order of a system kind is refused `kind.system-only` on every path (submit, policy commit, `Reveal`), and `FileSystemCommandUnlocked` refuses an ordinary kind `kind.not-system` and writes nothing · filing the same logical event twice writes one row (deterministic id + `CommandExistsUnlocked`); the function files into a non-active world and still runs admission · every existing command row reads back `Origin = Commander` and every existing world replays byte-identically; `SystemCommandKinds.All ⊆ WorldCommandKinds.All`, with neither `depart` nor `advance` ever a member.
- **Verify:** `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs,gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs,src/FusionRpg.Core/World/Turn/SystemCommandKinds.cs,src/FusionRpg.Core/World/Turn/SystemCommandId.cs,src/FusionRpg.Data/Sqlite/RpgStore.SystemCommands.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs,tests/FusionRpg.Core.Tests/World/Turn/SystemCommandAdmissionTests.cs,tests/FusionRpg.Data.Tests/World/SystemCommandFilingTests.cs -Session <session-id>` then `.\scripts\guard-dal.ps1`
- **Shared files:** WorldCommand.cs (the system-command path lands once here, §4, with the closed set `release-warden`, `rift-window`, `rift-arrive`) · RpgStore.WorldTurns.cs (`origin` column, insert, hydrate)
- **Notes:** the closed-set half of acceptance 8 ("membership is exactly the three") can only be proven once `world-continuity` and `rift-trade` have shipped their kinds; this task proves the subset join, the never-`depart`/`advance` assertion and the fixture-kind behaviour.

### [ ] 0a.6 `step-benchmark` — End Turn is measurable before the `Logistics` phase exists
- **Spec:** docs/architecture/trade-network/trade-foundation/spec-step-benchmark.md
- **Wave:** row 0a · no flag, no bump (R3: instrumentation only; `Step`'s output is unchanged by construction)
- **Depends on:** 0a.1
- **Acceptance:** with `PerfProbe.Enabled` and `TrackAllocations` each true and false, the same world, commands and seed produce the same `StateHash` every turn over a scripted run, and `WorldDeterminismGuardTests` stays green with no new exemption and no edit to its banned list · after one `Step` the snapshot holds an entry for `world.step` and for every name in `TurnEngine.Phases`, the list read from `Phases` · `PerfSection`'s member count equals `SectionCount` and the names array length (read from the enum, not a literal); timings and allocations are printed, never asserted.
- **Verify:** `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Diagnostics/PerfProbe.cs,gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs,tests/FusionRpg.Core.Tests/World/Turn/TurnStepBench.cs,tests/FusionRpg.Core.Tests/Diagnostics/PerfProbeWorldSectionTests.cs,tests/FusionRpg.Bench/TurnStepBench.cs,gk-core/tests/FusionRpg.Bench/Program.cs,gk-core/tests/FusionRpg.Bench/FusionRpg.Bench.csproj,gk-core/scripts/verification-boundaries.v1.json -Session <session-id>`
- **Shared files:** TurnEngine.cs (one `using` scope per phase call at `:191-207`; no signature, order or body change)
- **Notes:** `gk-core/tests/FusionRpg.Bench/**` has **no** owner mapping today (verified), so the `turn-step-bench` row covering the two bench files is part of this task; the pre-existing bench files stay their owners' gap. `SectionCount` and the names array move together or `Record` silently drops the new sections.

### [ ] 0a.7 `stock-deltas` — `Step` reports every world-stock change it makes
- **Spec:** docs/architecture/trade-network/trade-foundation/spec-stock-deltas.md
- **Wave:** row 0a · no flag, no bump (R3: the recorder is write-only from inside `Step`, read only after it returns; no phase reads it)
- **Depends on:** 0a.3, 0a.1 (the synthetic campaign the reconciliation runs on)
- **Acceptance:** over a scripted multi-turn synthetic `medium` run and a `two-hearths` run, `StockReconciliation.Check` is empty **every turn** for every registered stock and holder, and a falsifier that changes `LoamStock` without recording makes `Check` report that sector and stock · the same world, commands and seed produce the same `StateHash` as before this module · `Deltas` is ordered by `(HolderKind, HolderId, StockId, FactKind, OwnerId)` with no zero and no duplicate key, and a legion destroyed in a phase yields exactly one `lost` delta equal to what it held at that moment whether or not it was topped up earlier in the same turn (both orders).
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Ledger/StockDelta.cs,src/FusionRpg.Core/World/Ledger/StockDeltaRecorder.cs,src/FusionRpg.Core/World/Ledger/WorldStockRegistry.cs,src/FusionRpg.Core/World/Ledger/StockReconciliation.cs,gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs,gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs,gk-core/src/FusionRpg.Core/World/Loam/LoamPhases.cs,gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs,gk-core/src/FusionRpg.Core/World/Movement/SustainResolver.cs,gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs,gk-core/src/FusionRpg.Core/World/Growth/DevelopResolver.cs,gk-core/src/FusionRpg.Core/World/Growth/GrowthPhases.cs,gk-core/src/FusionRpg.Core/World/Growth/RaiseResolver.cs,gk-core/src/FusionRpg.Core/World/Siege/SiegeConstruction.cs,tests/FusionRpg.Core.Tests/World/Ledger/StockDeltaTests.cs,tests/FusionRpg.Core.Tests/World/Ledger/StockReconciliationTests.cs -Session <session-id>`
- **Shared files:** TurnEngine.cs (`TurnResult.StockDeltas`; the phase-boundary `lost` rule) · TurnReport.cs (carries the recorder)
- **Notes:** `DrawProportionally` is shared by upkeep and top-up — its signature change updates both callers in one commit. `WorldStockRegistry.All`'s ids and `StockHolderKind`'s two members are pinned with the closed-vocabulary reason; `Faction` and `Route` move the pin in their own changes.

### [ ] 0a.8 `economy-report` — the economy's health is a test over the real turn engine
- **Spec:** docs/architecture/trade-network/trade-foundation/spec-economy-report.md
- **Wave:** row 0a · no flag, no bump (R3: a test-only report plus a pure tuning loader; Core reads no file)
- **Depends on:** 0a.1, 0a.7, 0a.4
- **Acceptance:** **P1** — over the scripted run on `medium` and `giant` synthetic worlds, no registered stock's net-flow series is monotone positive · **P6** — no sink reason exceeds `report.sinkShareCeilingMilli` for any stock with two or more observed sink reasons, the ceiling read from tuning and never a literal, and a missing or unknown key fails the load · arithmetic — sink shares sum to exactly 1000‰ per stock and per-stock net flow equals the sum of its deltas; P2, P9/P12, PS-5 pairing, binding, payback and win rate are printed with a verdict, never asserted, and no count of sectors, turns, buildings, goods or rows is pinned.
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Trade/TradeTuning.cs,data/tuning/trade.v1.json,gk-core/tools/tuning/publish.py,tests/FusionRpg.Core.Tests/World/Economy/EconomyReport.cs,tests/FusionRpg.Core.Tests/World/Economy/EconomyReportTests.cs,tests/FusionRpg.Core.Tests/World/Trade/TradeTuningTests.cs,gk-core/scripts/verification-boundaries.v1.json -Session <session-id>` then `python gk-core/scripts/audit-magic-numbers.py --summary`
- **Shared files:** none
- **Notes:** **this task is the one creator of `data/tuning/trade.v1.json`** and of the `TradeTuning` record, loader and the `trade` domain in `publish.py` (landing order §5 — the ~15 specs writing "`trade.v1.json` (new)" mean "the `trade` domain"). `gk-core/data/tuning/**` has **no** owner mapping (verified), so the `core-trade-tuning` owner row listing each published `trade.v{n}.json` as an exact path lands here (ask X-18); every later publish adds its path to that row. A P1/P6 failure is a finding for the owning faucet/sink, never a test to loosen.

### [ ] 0a.9 `world-stock-ledger` — an append-only world-stock ledger inside the turn commit
- **Spec:** docs/architecture/trade-network/trade-foundation/spec-world-stock-ledger.md
- **Wave:** row 0a · no flag, no bump (R3: a ledger table; nothing hashed changes)
- **Depends on:** 0a.7, 0a.3
- **Acceptance:** committing a turn writes exactly one row per `StockDelta` plus the opening rows on a world's first ledgered commit, and re-running the append for the same `(world, turn)` inserts nothing · after a scripted multi-turn `two-hearths` campaign, `SumWorldStockLedger` equals the persisted value for every sector, entity and registered stock (a holder that no longer exists sums to 0), asserted **per holder, not per owner**, and a world created before this module reconciles after its first ledgered commit · closure — every non-null `owner_faction_id` exists in `rpg_world_factions`, every `stock_id` is a registry id, every `fact_kind` is a world-scope member, no row has `delta = 0`; an injected failure before `tx.Commit()` leaves no ledger row and no diff write, and no test pins a row count.
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Data/Sqlite/RpgStore.WorldLedger.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs,tests/FusionRpg.Data.Tests/World/WorldStockLedgerTests.cs,gk-core/scripts/verification-boundaries.v1.json -Session <session-id>` then `.\scripts\guard-dal.ps1` and `python gk-core/scripts/guard-test-substrate.py`
- **Shared files:** RpgStore.WorldTurns.cs (**first** of §4's ledger tables, appended right after `DiffWorldGraphUnlocked`, same transaction)
- **Notes:** it needs no `save-identity` SE4.12 — the owner is a world faction id and the save is `rpg_worlds.player_id` (a map correction, §Dependencies), so this lands inside row 0a. Store tests in memory; a failed temp-delete is a failure.

---

## Row 0b — `empire-seed` W1 (one SSOT for structure seeds)

Ten tasks. **No flag, no bump for the whole wave** (R3): seed content, tuning bands, a load-time reader, test
builders, pure queries and report text. Nothing `TurnEngine.Step` or the canonical projection reads changes.
`world-name-index` (0b.8) and `corpus-metrics` (0b.9) joined this row in reconciliation **R-2**.

### [ ] 0b.1 verification boundaries for seedsmith, the structure corpus and the seed tuning files
- **Spec:** ask X-18, `docs/architecture/trade-network/landing-order.md §7 (ask X-18)` (no module spec owns it)
- **Wave:** row 0b, **first task** · no flag, no bump (R3: a verification mapping, nothing the game reads)
- **Depends on:** nothing — it is the blocker `landing-order.md §7 (ask X-18)` puts in front of the whole of row 0b
- **Acceptance:** `verify-change.ps1` no longer throws `VERIFICATION BOUNDARY MISSING` (`scripts/verify-change.ps1:118`) for `gk-forge/tools/seedsmith/**`, `gk-data/packs/fusion/data/seed/structures/**` or `data/tuning/structure-seed.v*.json` · each new row names the focused pytest/dotnet command, not a full suite · an unmapped path anywhere in this cluster still fails loudly
- **Verify:** `.\scripts\verify-change.ps1 -Paths gk-core/scripts/verification-boundaries.v1.json -Session <session-id>` then re-run it with `-Paths gk-forge/tools/seedsmith/seedsmith/adapters/structures/planner.py,gk-data/packs/fusion/data/seed/structures/_plan.json`
- **Shared files:** none from landing-order §4
- **Notes:** **Settled by reconciliation R-17:** adding owner rows to `gk-core/scripts/verification-boundaries.v1.json` is **this family's own work**, in the task that first needs the path. `AGENTS.md` is explicit that an unmapped production path is a verification-boundary defect to add or repair, never something to compensate for by widening the suite, and §7 blocked row 0b on exactly these rows — so the prohibition and the blocker could not both stand. `empire-seed-map.md:709`'s prohibition is **overruled for that file only** and has been annotated there; `test-verification-boundary` still owns the tool, the registry's schema and its guard. This task adds the rows it names and no later task re-adds them: a second overlapping row at the same specificity makes `verify-change.ps1` throw `VERIFICATION BOUNDARY AMBIGUOUS`.

### [ ] 0b.2 `structures-adapter` — the corpus becomes visible to the generic seedsmith core
- **Spec:** docs/architecture/empire-seed/spec-structures-adapter.md
- **Wave:** row 0b · no flag, no bump (R3: an adapter and a regenerated plan; no game-readable change)
- **Depends on:** 0b.1
- **Acceptance:** `isinstance(resolve_adapter("structures"), SeedAdapter)`, `channels()` asserted empty, and `legal_combinations()` returns `False` for at least one real `(role, requiredSlotKind)` pair · **reconciliation, not a count:** `sum(plan["actualCounts"].values()) == len(load_rows(root))` and equals the non-exemplar `structure-anchor` entries the test walks independently · the regenerated `_plan.json` is byte-identical across two runs, and `check --adapter actions` / `--adapter dungeon` return the findings they returned before
- **Verify:** `$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_structure_planner.py gk-forge/tools/seedsmith/tests/test_structure_metrics.py tools/seedsmith/tests/test_structures_adapter.py -q` and `.\scripts\verify-change.ps1 -Paths gk-forge/tools/seedsmith/seedsmith/adapters/registry.py,gk-forge/tools/seedsmith/seedsmith/adapters/structures/__init__.py,gk-forge/tools/seedsmith/seedsmith/adapters/structures/planner.py,gk-forge/tools/seedsmith/seedsmith/adapters/structures/metrics.py,gk-data/packs/fusion/data/seed/structures/_plan.json -Session <session-id>`
- **Shared files:** none from landing-order §4
- **Notes:** `gk-data/packs/fusion/data/seed/structures/_plan.json` is generator output — regenerate it through the planner in this commit, never hand-edit it.

### [ ] 0b.3 `band-reader` — one C# seed-plus-bands reader, host-fed
- **Spec:** docs/architecture/empire-seed/spec-band-reader.md
- **Wave:** row 0b · no flag, no bump (R3: a load-time reader; the resolved catalog is byte-identical)
- **Depends on:** 0b.1 (its C# paths are mapped already; the seed paths are not)
- **Acceptance:** no `File.`/`Directory.` token under `src/FusionRpg.Core/Seeds/**` or `gk-core/src/FusionRpg.Core/World/StructureSeed/**`, proven by a source-scan test (tunables-ssot T8) · an ordinal with no band row, an axis with no table, or a VALIDATED value outside its registry throws naming family, entry, axis and value · shuffling the `SeedSource` list gives an identical `Rows` sequence, `_exemplars/` rows are absent, `Resolve` returns `long` and narrowing into an `int` `StructureDef` field throws `OverflowException`
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/Seeds/SeedBandResolver.cs,gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs,gk-core/src/FusionRpg.Core/World/StructureCatalog.cs,gk-core/src/FusionRpg.Server/Program.cs,gk-core/tests/FusionRpg.Core.Tests/World/StructureCatalogTestBootstrap.cs,gk-core/tests/FusionRpg.Data.Tests/StructureCatalogTestBootstrap.cs -Session <session-id>`
- **Shared files:** none from landing-order §4 (it touches `gk-core/src/FusionRpg.Server/Program.cs`, which that table does not govern)
- **Notes:** deletes `gk-core/src/FusionRpg.Core/World/Bands.cs`, so the tier ladder has one source (`data/tuning/structure-seed.v*.json` `bands.tierLadder`). Ten roles are pinned here as a closed vocabulary; the eleventh is 0b.6's reviewed change. Crosses Core, Data and Server test projects — AGENTS.md "Verification boundary" point 2, so the full suite runs once at the end of this task.

### [ ] 0b.4 `world-budgets` — every corpus target is a tuning value
- **Spec:** docs/architecture/empire-seed/spec-world-budgets.md
- **Wave:** row 0b · no flag, no bump (R3: tuning keys and test assertions only)
- **Depends on:** 0b.2
- **Acceptance:** a source scan of the three structure test files finds no `2.4`/`4.0`/`2400`/`4000` and no `len(...) == <integer literal>` over a row collection — the scan is itself a test · a fixture tuning whose `densityBand` excludes the current density fails both the density test and `check_plan`, and the published band passes both, so the verdict moves with data only · a fixture budget naming a role outside `ROLE`, or missing one in `ROLE`, raises `PlanCheckFailure` naming it
- **Verify:** `$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_structure_corpus.py gk-forge/tools/seedsmith/tests/test_structure_planner.py gk-forge/tools/seedsmith/tests/test_structure_metrics.py -q` and `.\scripts\verify-change.ps1 -Paths data/tuning/structure-seed.v2.json,gk-forge/tools/seedsmith/seedsmith/adapters/structures/metrics.py -Session <session-id>`
- **Shared files:** none from landing-order §4
- **Notes:** turns the two population pins (`len(DUMPED_ROWS) == 8`, `== 17`, `== 25`) into reconciliations — a corpus size is a reading, never a constant. Publishes `structure-seed.v2` through `gk-core/tools/tuning/publish.py`, extending the tool if `set` refuses a new key (never an in-place edit); the `Exchange` budget row lands with the role in 0b.6, not here (spec §3 / S3).

### [ ] 0b.5 `structure-bands` — every structure number leaves the seed
- **Spec:** docs/architecture/empire-seed/spec-structure-bands.md
- **Wave:** row 0b · no flag, no bump (R3: a refactor — the resolved catalog is byte-identical, T7)
- **Depends on:** 0b.3, 0b.2, 0b.4
- **Acceptance:** `StructureCatalog.All`, serialized field by field in id order, hashes the same before and after, and the guard snapshot is then deleted · a walk over every JSON document under `gk-data/packs/fusion/data/seed/structures/` (excluding `_plan.json` and `_registry/`) finds no JSON number anywhere in the row, and `numeric_audit` reports no defect on all four smuggling shapes · one writer: the non-`_plan`/`_registry`/`_exemplars` `.json` set equals `file_tree()`, `LoamPolicy` exposes only `WaystationRangeHops` from `Structures`, `ROLE_TO_STRUCTURE_KIND` is gone, and `audit-magic-numbers.py` shows no new balance-surface literal
- **Verify:** `.\scripts\verify-change.ps1 -Paths gk-forge/tools/seedsmith/seedsmith/adapters/structures/generate_corpus.py,gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/schema.py,gk-core/src/FusionRpg.Core/World/StructureCatalog.cs,gk-core/src/FusionRpg.Core/World/Loam/LoamPolicy.cs,gk-core/src/FusionRpg.Core/World/Loam/LoamTuning.cs,gk-core/src/FusionRpg.Core/World/Loam/WonderTuning.cs,data/tuning/structure-seed.v3.json,data/tuning/loam.v6.json -Session <session-id>` plus `python -m pytest gk-forge/tools/seedsmith/tests/test_structure_corpus.py -q`, then the full suite once (Core + Data + Server, AGENTS.md point 2)
- **Shared files:** none from landing-order §4
- **Notes:** **§5 tuning owner:** this task publishes the next `data/tuning/structure-seed.v{n+1}.json` and authors the **consumer-added anchor fields** table (field, shape, band axis, consumer module, landing order — audit M7, `empire-seed-map.md:1050-1059`); every later consumer publishes `v{n+1}` in its own wave and regenerates the corpus in the same commit. Regenerates `gk-data/packs/fusion/data/seed/structures/**` through `generate_corpus.py` (committed tree, CI fails on drift) and folds the three hand-authored rows into the generator's source (map §12 question 1). Also republishes `loam.v{n+1}` without the structures block and corrects the two stale notes (obligation 6).

### [ ] 0b.6 `exchange-role` — one reviewed widening of the closed role list
- **Spec:** docs/architecture/empire-seed/spec-exchange-role.md
- **Wave:** row 0b · no flag, no bump (R3: a closed vocabulary member plus a budget row)
- **Depends on:** 0b.5, 0b.4
- **Acceptance:** the role registry has exactly eleven members — the ten existing plus `Exchange` — and Python `ROLE` equals the C# vocabulary; **pinned as a closed vocabulary** because a twelfth role is a reviewed change · every role has a description with a negative clause, a budget target and at least one legal slot kind, and a C# row whose `role` is outside the registry is a load rejection naming the value · `("Exchange","Market")` and `("Exchange","Wildland")` are in the regenerated `legalRoleSlotPairs` and `("Exchange","Rootbed")` is `False`; the rewritten role-coverage test passes with **zero** `Exchange` rows and would fail if `Exchange` left the plan's work
- **Verify:** `$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_structure_corpus.py gk-forge/tools/seedsmith/tests/test_structure_planner.py -q` and `.\scripts\verify-change.ps1 -Paths gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/schema.py,gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/descriptions.py,data/seed/structures/_registry/roles.v2.json,data/tuning/structure-seed.v4.json,gk-core/src/FusionRpg.Core/World/StructureCatalog.cs -Session <session-id>`
- **Shared files:** none from landing-order §4
- **Notes:** red-by-design is not allowed, so the coverage contract is "filled or planned" (S4). `Enable`'s description gains the *"or agreed"* clause in the same `roles.v2.json` publish (round 5 X16); no twelfth role. Publishes `structure-seed.v{n+1}` with the `Exchange` budget row and annotates the four documents that enumerate ten roles; `audit-doc-citations.py --scope` must report no HIGH for each.

### [ ] 0b.7 `world-exemplars` — a hand-authored distribution and the shared tone brief
- **Spec:** docs/architecture/empire-seed/spec-world-exemplars.md
- **Wave:** row 0b · no flag, no bump (R3: authored exemplars, a brief and a schema field)
- **Depends on:** 0b.6
- **Acceptance:** every role in the registry has at least one exemplar and every exemplar passes `ExemplarConformance`; no exemplar id or name equals a corpus id or name, a normalised almanac type name, or an avoid-list term · `load_rows` and the C# `StructureCorpus` both contain no exemplar (0b.3's skip test extended to a real exemplar file) · the tone section renders into a brief, passes the citation check, is byte-identical across two renders, contains no digit, and its avoid list is either empty or exactly `ip-censor`'s rendered terms — never hand-typed
- **Verify:** `$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest tools/seedsmith/tests/test_structure_exemplars.py gk-forge/tools/seedsmith/tests/test_structure_corpus.py -q` and `.\scripts\verify-change.ps1 -Paths data/seed/structures/_exemplars,data/seed/structures/_registry/tone.v1.json,gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/schema.py,gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs -Session <session-id>`
- **Shared files:** none from landing-order §4
- **Notes:** exemplars and `_registry/**` are the hand-authored exception to the generated-data rule, so authoring them here is sanctioned; the corpus itself is still generator output. Owns the `flavor` schema widening (S7), because an exemplar must validate against the schema first. The tone brief carries the owner's vocabulary rule — "unit", "enemy empires", a difficulty profile; no IP words, no named actors — and C4's rule that a building never takes a slot's display name.

### [ ] 0b.8 `world-name-index` — one cross-corpus dedup and block input
- **Spec:** docs/architecture/empire-seed/spec-world-name-index.md
- **Wave:** row 0b · no flag, no bump (R3: a pure query over the committed corpora)
- **Depends on:** 0b.2, 0b.7
- **Acceptance:** **reconciliation:** the index key set equals `normalize_name(name)` over every entry and exemplar of every adapter with a `corpus_root`, the test walking the roots independently · two builds render byte-identically and shuffling adapter registration order changes nothing; the suite runs with the transport stubbed to raise and the network guard active · one normaliser — the decision-43 test imports `normalize_name` and no second `re.sub(r"[^a-z0-9]"` over names exists under `gk-forge/tools/seedsmith/`; `--check` exits non-zero after a corpus name changes and before `--write`
- **Verify:** `$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest tools/seedsmith/tests/test_world_name_index.py gk-forge/tools/seedsmith/tests/test_offline_guarantee.py -q` and `.\scripts\verify-change.ps1 -Paths tools/seedsmith/seedsmith/briefkit/names.py -Session <session-id>`
- **Shared files:** none from landing-order §4
- **Notes:** **Added to row 0b by reconciliation R-2**, because row 0c cannot be verified without it: `spec-trade-structure-rows.md:5` names it as a dependency and its acceptance 8 asserts name uniqueness *through* this index. It takes no flag and no bump, so the only cost was ordering.

### [ ] 0b.9 `corpus-metrics` — close the metric set over the committed corpus
- **Spec:** docs/architecture/empire-seed/spec-corpus-metrics.md
- **Wave:** row 0b · no flag, no bump (R3: report text and review queues)
- **Depends on:** 0b.2, 0b.5, 0b.4, 0b.8
- **Acceptance:** every registered metric declares a loop and every closed metric a target, with the registration error kept and tested; for every open metric, a fixture that makes it report its worst value leaves `Report.passed` **true** · `bands_resolve` fails on a fixture row whose ordinal has no band row and passes on the committed corpus; `name_unique_across_corpora` fails when a fixture row takes another corpus entry's normalised name · the readings block exists and **no test asserts any value in it**; the whole suite runs with the transport stubbed to raise
- **Verify:** `$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_structure_metrics.py -q` and `.\scripts\verify-change.ps1 -Paths gk-forge/tools/seedsmith/seedsmith/adapters/structures/metrics.py -Session <session-id>`
- **Shared files:** none from landing-order §4
- **Notes:** **Added to row 0b by reconciliation R-2**, because row 0c's own "done means" requires the closed-loop metric set and `bands_resolve` is what proves every loadable feature row resolves (`spec-trade-structure-rows.md` §5.4 item 4). No flag, no bump — ordering only. The "every good has two or more producers" metric stays declared and unmeasured until `sector-yield` defines goods chains (family row 1).

### [ ] 0b.10 anchor schema widening — the M5 half of `trade-structure-rows`
- **Spec:** docs/architecture/empire-seed/spec-trade-structure-rows.md §5.4 (items 1–4; the rows are 0c.1)
- **Wave:** row 0b · no flag, no bump (R3: schema columns and closed vocabularies; the C# members are `sector-features`')
- **Depends on:** 0b.5, 0b.6, 0b.7
- **Acceptance:** `featureUnlock` exists as a VALIDATED nine-member closed vocabulary (`none · storage · banking · trade · caravans · cross-world · diplomacy · legion-equipment · standard`) with a negative clause, and an unknown value is refused by the anchor audit — pinned as a closed vocabulary because a new feature building is a reviewed change to round 4 §B · the `variants` item shape is closed (`variantId, name, costProfile, strengthBand, footprint`), carries no numeric field and no `tier` key, and the tier is the list position · `requiredSlotKinds` is optional, non-empty, duplicate-free, its first entry equals `requiredSlotKind`, and every entry is legal for the row's role; the planner's pair derivation and the adapter dimension read every entry
- **Verify:** `$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_structure_corpus.py gk-forge/tools/seedsmith/tests/test_structure_planner.py -q` and `.\scripts\verify-change.ps1 -Paths gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/schema.py,gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/audit.py,gk-forge/tools/seedsmith/seedsmith/adapters/structures/planner.py -Session <session-id>`
- **Shared files:** none from landing-order §4
- **Notes:** **Resolved by reconciliation R-1:** `spec-trade-structure-rows.md` §5.4 and `empire-seed-map.md:676-678,1038` were right — this widening lands **before** `trade-foundation` `sector-features`, which has moved out of row 0a into its own **row 0d**, after this row and after 0c. As the order stood, `sector-features` would have landed `StructureDef.FeatureUnlock` and `StructureKind.Feature` against an anchor schema that had neither field. Also corrects `planner.py:52`'s wrong comment that the variant bound of 4 mirrors a three-rung ladder.

---

## Row 0c — `empire-seed` `trade-structure-rows` (the eight feature building rows)

One task. **No flag, no bump** (R3): authored seed content. What each tier *does* is the consuming mechanism's,
and the flag that makes these rows readable is `sector-features`' at row 0d.

### [ ] 0c.1 `trade-structure-rows` — the eight feature rows, the feature-rows half
- **Spec:** docs/architecture/empire-seed/spec-trade-structure-rows.md (§5.1–§5.3, §5.5–§5.7; §5.4 is 0b.10)
- **Wave:** row 0c · no flag, no bump (R3: authored seed content; nothing `Step` reads)
- **Depends on:** 0b.10 (the schema widening), 0b.5 (the band tables), 0b.6 (`Exchange` and the `Enable` clause), 0b.8 (name uniqueness), 0b.9 (`bands_resolve`)
- **Acceptance:** for every `featureUnlock` value other than `none`, **exactly one** row carries it (a contract over the closed vocabulary, not a population pin), each row's `variants` list is in tier order and every item validates against the closed shape · every one of the eight rows is loadable: `structureKind: Feature`, a non-`none` `featureUnlock`, present in `StructureCatalog.All`, answered by `IsKnown`, no per-building kind and no withdrawn `Exchange` kind · no row id `convoy-depot` exists, `caravan-yard` carries a `convoy-depot` variant, `workshop` is a `Refine` row in `refine/`, per-role counts meet the published budget within tolerance with `targetNewRows = 0`, and a regeneration is byte-identical with **zero** model calls
- **Verify:** `python gk-core/tools/tuning/publish.py structure-seed <budget keys> --label "trade-structure-rows"`, then `$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m seedsmith.adapters.structures.generate_corpus; python -m seedsmith.adapters.structures.planner; python -m pytest gk-forge/tools/seedsmith/tests/test_structure_corpus.py gk-forge/tools/seedsmith/tests/test_structure_planner.py gk-forge/tools/seedsmith/tests/test_structure_metrics.py -q`, then `.\scripts\verify-change.ps1 -Paths gk-forge/tools/seedsmith/seedsmith/adapters/structures/generate_corpus.py,gk-data/packs/fusion/data/seed/structures,data/tuning/structure-seed.v5.json,gk-core/tests/FusionRpg.Core.Tests/World/StructureCatalogImportTests.cs -Session <session-id>`
- **Shared files:** none from landing-order §4
- **Notes:** **Golden re-bless this task shares:** the A1 start kit (round 5 A1) moves the template-created world goldens, and `landing-order.md §6` makes that **one shared re-bless** with `counterparties` `empire-roster` (row 15), `clan-seeding` (row 16) and `world-continuity` `world-creation` (WC5.1) — whichever lands last re-blesses, nobody batches another wave's goldens in. Regenerates `gk-data/packs/fusion/data/seed/structures/**` and `_plan.json` through the generator in the same commit (CI fails on drift). **Blocked by X-11** (`landing-order.md §7 (ask X-11)`): the multi-slot `BuildResolver` arms are world-map's and must land before the Trading Post's two slot kinds and the upgrade verb mean anything. Publishes `structure-seed.v{n+1}` for the budget floors; every authored building and variant name passes the release scan against `ip-censor`'s `avoid-list` (advisory, m20).

---

## Row 0d — `trade-foundation` `sector-features` (the family's first flag and first bump)

One task, one flag, one bump: **`trade.sectorFeatures`, ordinal N+1**. It is its own row because it lands
`StructureDef.FeatureUnlock` and `StructureKind.Feature` and the anchor-schema widening that adds those
fields is row 0b (reconciliation **R-1**); it takes a flag because its `build`-on-own-slot upgrade arm
changes how an existing world's stored order resolves (**R-1b**).

### [ ] 0d.1 `sector-features` — one building-tier gate for every feature in five programs
- **Spec:** docs/architecture/trade-network/trade-foundation/spec-sector-features.md
- **Wave:** row 0d · flag **`trade.sectorFeatures`** (this task registers it) · bump **N+1** — the family's **first** flag and **first** bump (landing order §1 R7, §2 row 0d, §10 R-1b). Row 0a's *"the registry ships empty"* exemption does not cover this module: `spec-sector-features.md:152-160` turns a `build` order naming the structure already on the slot into an **upgrade** instead of a `build.occupied` refusal, which changes how an existing world's stored order resolves. No shipped template places a structure, so no golden moves today — that is luck, not a licence, and R1 forbids shipping it unflagged
- **Depends on:** row 0b (`empire-seed` `band-reader` + the `featureUnlock` / closed `variants` / `requiredSlotKinds` schema widening split out of `trade-structure-rows`, M5 — tasks 0b.3 and 0b.10), row 0c (0c.1, the eight feature rows this reads), row 0a (`world-stamp`, for the capability registry). **This module moved out of row 0a into its own row 0d by reconciliation R-1**, because it lands `StructureDef.FeatureUnlock` and `StructureKind.Feature` and the schema that adds those fields is row 0b
- **Acceptance:** `SectorFeature` has exactly nine members (closed vocabulary, pinned with the reason) equal to `empire-seed`'s `featureUnlock` vocabulary by a join; a loaded row whose feature is not `none` has at most its feature's maximum tiers and a `none` row uses no variant as a tier, both asserted per row over the real corpus, never by count · **S1** — `TierFor` is 0 when the slot's and the sector's owners differ, when either is unowned, or when neither is the asked faction, and equals `TierOf` when one faction owns both; a sector flipping owner while its slot does not gives **both** sides 0 in the same turn, and every gate in the family is asserted to call `TierFor`/`FactionTier` rather than `TierOf` · a world with every slot at tier 1 hashes byte-identically and a tier above 1 round-trips; `ActiveTier` is 0 for an empty slot and a first build, `n` for a finished tier-`n` structure and `n` mid-upgrade to `n+1`; a clear or replace (`LoamPhases.cs:224`, `BattleApplication.cs:165-172`) leaves `StructureTier == 1`; an upgrade never switches a building off in any of the gates §3 lists (one test per gate).
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Structures/SectorFeatures.cs,gk-core/src/FusionRpg.Core/World/StructureCatalog.cs,gk-core/src/FusionRpg.Core/World/WorldState.cs,gk-core/src/FusionRpg.Core/World/WorldCanonical.cs,gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs,gk-core/src/FusionRpg.Core/World/Loam/LoamPhases.cs,gk-core/src/FusionRpg.Core/World/Loam/LoamProduction.cs,gk-core/src/FusionRpg.Core/World/Loam/WonderEmpireEffects.cs,gk-core/src/FusionRpg.Core/World/Loam/Habitability.cs,gk-core/src/FusionRpg.Core/World/SectorItemCapacity.cs,gk-core/src/FusionRpg.Core/World/Growth/GrowthPhases.cs,gk-core/src/FusionRpg.Core/World/Turn/BattleApplication.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldGraphDiff.cs,scripts/guard-feature-gate.ps1,gk-core/scripts/enforcement-registry.v1.json,tests/FusionRpg.Core.Tests/World/Structures/SectorFeaturesTests.cs,tests/FusionRpg.Core.Tests/World/BuildResolverTests.cs,tests/FusionRpg.Data.Tests/World/SlotTierPersistenceTests.cs,gk-core/scripts/verification-boundaries.v1.json -Session <session-id>`
- **Shared files:** WorldState.cs (`WorldSlot.StructureTier`) · WorldCanonical.cs (a conditional `slot-tier` row after `slot-depletion` — a **slot** row, outside §4's sector-row sequence, and now named in §4's sparse-row clause, R-11; sparse, so no existing hash moves) · BuildResolver.cs, WorldValidation.cs, SlotTypeCatalog.cs are **world-map's** — asks X-11 and X-14
- **Notes:** blocked on X-11 (multi-slot `BuildResolver` accepting a kind in `RequiredSlotKinds`, plus the `build`-on-own-slot upgrade arm at `BuildResolver.cs:84` / `WorldValidation.cs:411`) — world-map lands those two arms first. Lands the `feature-gate-one-read` guard + `tn-feature-gate-one-read` invariant, and its own owner row (`scripts/guard-*.ps1` is unmapped today). The §3 active-gate moves touch loam, growth, wonder, habitability and the siege battle seam with those owners' agreement recorded in the change. **The "no flag, no bump" question is answered:** this row takes the family's first flag and first bump (R-1b), which is what makes the upgrade arm legal to ship.

---

## Row 0e — `legion-build` W1 (the member row becomes a stack)

One flag, `legion.rolePlacement`, registered by 0e.3; one bump, **`L1`** in the legion lane. `member-stack`
cannot own a flag here: the only producer of `Count > 1` lands in wave L2, and a flag never spans waves (R1).
Reconciliation **R-13** accepted this answer and closed audit M2.

### [ ] 0e.1 `member-stack` — a member row is a species × a living count
- **Spec:** docs/architecture/legion-build/spec-member-stack.md
- **Wave:** 0e (after family row 0d) · registers no flag (R1: its stack capability is unreachable until L2) · rides wave 0e's one bump `L1`, mints none
- **Depends on:** row 0a (`world-stamp`, the record a saved world is migrated under)
- **Acceptance:** (1) every headcount site in the spec's wiring-gap table returns `Σ Count`, proven by the expansion property against a world expanded to one row per unit, member order shuffled on both sides; (2) a `Count = 1` world resolves **and hashes** byte-identically and no golden is re-blessed (`count=`/`id=` emitted only when non-default); (3) `MemberId` is unique within a legion and unchanged by a battle, a recovery or a reorder, and the migration is idempotent when run twice.
- **Verify:** `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/World/WorldState.cs,gk-core/src/FusionRpg.Core/World/WorldCanonical.cs,src/FusionRpg.Core/Battle/StackArithmetic.cs,src/FusionRpg.Core/World/WorldEntityUnits.cs,gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs,gk-core/src/FusionRpg.Core/World/Loam/LoamUpkeep.cs,gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs,gk-core/src/FusionRpg.Core/World/Movement/LaneCost.cs,gk-core/src/FusionRpg.Core/World/Movement/SupplyGraph.cs,gk-core/src/FusionRpg.Core/World/Intel/FactionIntel.cs,gk-core/src/FusionRpg.Core/World/LegionCargo/ScopedInventoryPolicy.cs,gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultResolver.cs,gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs,gk-core/src/FusionRpg.Core/World/Growth/RaiseResolver.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldGraphDiff.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.LegionCargo.cs,gk-core/src/FusionRpg.Contracts/WorldDtos.cs,gk-core/src/FusionRpg.Server/WorldEndpoints.cs -Session <session-id>` plus `python gk-core/scripts/audit-overflow.py --targets A3`
- **Shared files:** `WorldState.cs` — the first field addition after 0a's `Stamp`; `WorldCanonical.cs` — **no append slot consumed**: `count=`/`id=` are default-suppressed fields on the existing `member` row, not a new conditional row, so `located-stock` still takes slot 2 at row 1; `RpgStore.World.cs` two `EnsureColumn`s + the unique index
- **Notes:** the web contract paths (`gk-web/web/fusion-rpg-web/src/contract/{types,adapt}.ts` + fixtures) have **no verification-boundary owner** — `verify-change.ps1:118` throws `VERIFICATION BOUNDARY MISSING`, so adding the `web/**` owner mapping is part of this task — X-18 is this family's own work (R-17), this is the first task to touch `web/**`, and no later task may re-add an overlapping row. The spec's Structure also modifies `WorldValidation.cs`, which landing-order §4 fences as world-map's. Reconciliation **R-20** files that edit as an **extension of ask X-11**, with the stated default that **this task ships without it**: the four member-row rules are asserted in the module's own tests, and the validation arm follows when world-map lands its arms. Do not edit that file here, and do not treat the fence question as settled — it is world-map's to answer. Files the `deployment-hierarchy-map.md:106` wording amendment (X7).

### [ ] 0e.2 `caravan-kind-retire` — a caravan is a legion on an order, not a kind
- **Spec:** docs/architecture/legion-build/spec-caravan-kind-retire.md
- **Wave:** 0e (after family row 0d) · registers no flag and grants no capability, so it adds nothing to bump `L1` and claims none of its own
- **Depends on:** 0e.1 (same `WorldState.cs`; one edit at a time)
- **Acceptance:** (1) nothing in `src/`, `tests/` or `web/` names `Caravan`; (2) every world golden and store round-trip is green with no re-bless — the kind is persisted and hashed by name and no row ever held it; (3) a membership test pins `WorldEntityKind` to the members it holds at landing with the stated reason (a closed vocabulary the code owns, never a population).
- **Verify:** `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/World/WorldState.cs,gk-core/src/FusionRpg.Core/World/EntityNaming.cs,gk-core/tests/FusionRpg.Core.Tests/World/EntityNamingTests.cs,gk-web/web/fusion-rpg-web/src/ui/world/worldEnums.ts,gk-web/web/fusion-rpg-web/src/ui/world/worldEnums.test.ts -Session <session-id>`
- **Shared files:** `WorldState.cs` only, after 0e.1
- **Notes:** the two `web/` paths are unmapped as in 0e.1 (X-18). The FE comment is re-pointed at the symbol rather than a line so it cannot drift again.

### [ ] 0e.3 `role-aware-placement` — only fighting roles take a battle cell
- **Spec:** docs/architecture/legion-build/spec-role-aware-placement.md
- **Wave:** 0e (after family row 0d) · flag `legion.rolePlacement` (this task registers it) · bump `L1`, the wave's one, taken at landing
- **Depends on:** 0e.1; external `empire-progression` `legion-commander` for the `Commander` arm only (the enum member is the landed signal, so it blocks nothing)
- **Acceptance:** (1) one `Fights` predicate decides placement for every battle kind, with exactly one production call site (source scan) and a throwing default so a new role must answer; (2) each row of the bearer-fate table has its own test, including a bearer-only attacker refused winnerless and a bearer-only defender losing its bearers; (3) no golden without a bearer present moves.
- **Verify:** `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/World/WorldState.cs,gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultResolver.cs,gk-core/tests/FusionRpg.Core.Tests/World/Turn/DistrictAssaultResolverTests.cs -Session <session-id>`
- **Shared files:** none of §4's five.
- **Notes:** this task owns the wave's flag **and** its bump because it is the only wave-0e change that makes an existing world resolve the same command log differently — a template world with a bearer in a siege (`WorldTemplateCatalog.cs:196`) moves, which is exactly the mid-life rule change R1 exists to stop. It carries that one golden re-bless with the reason, and owes the enforcement-registry row *"placement only through `Fights`"*. **Reconciliation R-13 accepted this answer and closed audit M2:** §2 row 0e now carries `legion.rolePlacement` and bump `L1`, `member-stack` rides it and registers nothing, and C1's question is recorded as being asked **per wave**, not per module.

---

## Row 0f — `world-continuity` W1 (state vocabulary, the seat detector, the documents)

Three tasks. **No flag, no bump** (R3): a schema column, two closed vocabularies, a pure detector and a
documents-only amendment. `state` is never hashed and `outcome` stays at its default here, so no world's
`StateHash` moves.

### [ ] 0f.1 `world-state-vocabulary` — two closed axes and one active map world per save
- **Spec:** docs/architecture/world-continuity/spec-world-state-vocabulary.md
- **Wave:** row 0f · no flag, no bump (R3: schema column + closed vocabularies; nothing hashed changes)
- **Depends on:** family row 0a (`trade-foundation` `system-commands`, which owns the system-kind set this module no longer defines)
- **Acceptance:** both vocabularies are closed enums, pinned at 3 and 3 with the reason "closed vocabulary the code owns", and an unknown stored id throws `world.state-unknown` / `world.outcome-unknown`; `LabelOf` is tested exhaustively over the nine pairs (a closed product, not a population) · a second `active` map world for one save is refused by the partial index and surfaced as a named reason; `GetActiveWorld` returns the unique active map row or `null`, and a delve id that sorts first never wins · `SelectWorld` swaps attention in one transaction, is idempotent, refuses a fallen or unknown world and is **order-independent** (both orders tested); submit and commit on a non-active map world return `world.not-active` and write nothing, verified by row counts
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/WorldAttention.cs,src/FusionRpg.Core/World/WorldOutcome.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs,gk-core/src/FusionRpg.Server/WorldEndpoints.cs,tests/FusionRpg.Data.Tests/World/WorldStateVocabularyTests.cs,docs/architecture/decisions.md -Session <session-id>`
- **Shared files:** `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs` — landing-order §4's slot for this wave is a **commit/submit gate, no new packed row and no new column**; `RpgStore.World.cs` (the `outcome` column and the partial unique index) is not in that table
- **Notes:** owes two `gk-core/scripts/enforcement-registry.v1.json` rows (one active map world per save — the partial index is the guard; `outcome` written only by the step) and a `decisions.md` row amending `:134`. Store tests build their store in memory (program rule R2, testing-standard R1).

### [ ] 0f.2 `seat-outcome` — one pure detector for victory and fall
- **Spec:** docs/architecture/world-continuity/spec-seat-outcome.md
- **Wave:** row 0f · no flag, no bump (R3: a pure query over a committed `WorldState`)
- **Depends on:** — (independent of 0f.1)
- **Acceptance:** `Read` is pure — identical inputs give identical output and the file holds no store, clock or RNG reference, covered by the world determinism guard · for every continuity template, taking the declared seat reads `SeatTaken`, losing `Home` reads `SeatLost` for both causes (capture and fade), and both at once reads `SeatLost` · `ValidateDeclaration` refuses with a named reason a template with no declared seat, an unknown seat id, a seat equal to `Home`, or a seat owned at creation by a `Player`, `Wild`, `Clan` or `Rival` faction, while `first-light`'s unowned `black-gate` passes and `Build` is unchanged
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/SeatOutcome.cs,gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs,tests/FusionRpg.Core.Tests/World/SeatOutcomeTests.cs,gk-core/tests/FusionRpg.Guard.Tests/WorldDeterminismGuardTests.cs -Session <session-id>`
- **Shared files:** none from landing-order §4
- **Notes:** the dominant enemy is the one `Zomboss`-kind faction (`counterparties` `empire-roster` rule 1) and a clan's seat never validates as the dominant seat, so `counterparties`' clan template versions (family rows 15–16) stay off the win path. No content is added to `first-light`: the existing guarded, unowned `black-gate` is declared, so **no golden moves** (R4-5).

### [ ] 0f.3 `continuity-doc-amendment` — the twelve document rows, in one change
- **Spec:** docs/architecture/world-continuity/spec-continuity-doc-amendment.md
- **Wave:** row 0f (**now part of the row**: §2's row 0f names all three modules since reconciliation R-14 — documents only, no golden, no flag, no bump)
- **Depends on:** 0f.1 (the vocabulary the prose describes)
- **Acceptance:** the acceptance search — *"lose where you were"*, *"dies with the map"*, *"die with the map"*, *"into the next world"* across `docs/` — returns only historical or superseded contexts that say so · `python docs/guide/mechanisms/_render.py --check` passes for every rendered page touched · `audit-doc-citations.py --scope <each doc>` reports no HIGH finding
- **Verify:** `python docs/guide/mechanisms/_render.py --check`, `python scripts/audit-doc-citations.py --scope docs/guide/the-loops.md` (once per edited document), then `.\scripts\verify-change.ps1 -Paths docs/guide/the-game.md,docs/guide/the-loops.md,docs/guide/mechanisms/_content/new-world-prestige.json,docs/architecture/empire-resource-ssot.md,docs/architecture/empire-economy-ssot.md,docs/PRINCIPLES.md -Session <session-id>`
- **Shared files:** none from landing-order §4
- **Notes:** acceptance 1 is **not met today** — the spec's own table lists eight owners still carrying stale lines, several outside this cluster's fence (`base-defense-ideal.md`, `loam-map.md`, `ssot-power-scale.md:239`, `npc-story-events*`, `trade-stories`). Round 6 S2 changes the sentence this task writes: world stocks cross **only over a `rift-trade` route**, never "as cargo" and never on an advance. Keep the owner's vocabulary: "unit", "enemy empires", a difficulty profile; no IP words, no named actors.

---

## Row 0g — `trade-foundation` `material-ledger`

One task, **no flag and no bump** (a ledger-first verb), and the family's one **gate**: it starts after the
save-identity re-key (X-1, round 6 C3 = *wait*).

### [ ] 0g.1 `material-ledger` — banked materials on the P14 ledger-first pattern
- **Spec:** docs/architecture/trade-network/trade-foundation/spec-material-ledger.md
- **Wave:** row 0g · no flag, no bump (landing order §2: a ledger-first verb; nothing hashed changes)
- **Depends on:** 0a.3; external `save-identity` SE4.12 → SE4.38 (ask X-1)
- **Acceptance:** `guard-ledger-writers.ps1` exits 0 on the real tree and 1 on fixtures with a write to a registered table outside its writers and with a non-`DELETE` in a reset-only file, while the same statement in a comment exits 0 · for every `(save, material)` the balance equals `SUM(delta)` of that save's human empire's ledger rows, asserted after a scripted loot/salvage/expedition/fusion/recipe sequence **in more than one order**; the same `(sourceKind, sourceId, lines)` twice returns `Replayed` and changes neither table, and a spend larger than the balance returns `Insufficient` and leaves both unchanged after rollback · opening: a store seeded with balances and no ledger reconciles after `Init`, a second `Init` writes nothing, a legacy shard stack renames through the ledger and still reconciles; every existing fusion, salvage, expedition, loot, workbench, shard-rung and recipe test passes **with no expected value changed**, and no test pins a row count or a material population.
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Data/Sqlite/RpgStore.MaterialLedger.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Materials.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Fusion.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Loot.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Workbench.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs,gk-core/src/FusionRpg.Data/Sqlite/Migrations/ShardRungs.cs,scripts/guard-ledger-writers.ps1,scripts/ledger-writers.v1.json,gk-core/scripts/enforcement-registry.v1.json,tests/FusionRpg.Data.Tests/Materials/MaterialLedgerTests.cs,tests/FusionRpg.Guard.Tests/LedgerWritersGuardTests.cs,gk-core/scripts/verification-boundaries.v1.json -Session <session-id>` then `.\scripts\guard-dal.ps1` and `.\scripts\guard-ledger-writers.ps1`
- **Shared files:** RpgStore.WorldTurns.cs is untouched here; `RpgStore.cs` gains the `Init` opening step and the `Reset` delete
- **Notes:** **blocker X-1, round 6 C3 = wait** — this starts after the save-identity re-key (SE4.12 → SE4.38, `tasks/solid-enforcement-todo.md:634`) finishes; the audit's option (b) (land on today's Tier B `player_id` key and re-point) is refused, so the verb is written once against the re-keyed store. Interim, stated in the spec: nothing leaves the map, `economy-report` prints a banked total of **zero with that reason**, `bank-points` keeps answering so *build a Counting House* stays buildable. Order at `Init`: opening **before** `ShardRungs.Migrate`, or a renamed stack has no opening row. Lands the `ledger-writers` guard + `tn-ledger-before-balance` invariant, which also covers `rpg_world_stock_ledger` (0a.9) from the day both land, and its own guard-script owner row.

---

## Wave ES2 — `empire-seed` W2 (the call budget and the ownership revision)

Two tasks. **No flag, no bump** (R3): a planner budget whose dry run calls nothing, and a documents-only
ownership revision. Lands after row 0c.

### [ ] ES2.1 `call-budget-dry-run` — the invention-shaped budget, proven before any token is spent
- **Spec:** docs/architecture/empire-seed/spec-call-budget-dry-run.md
- **Wave:** ES2 · no flag, no bump (R3: planner output and rendered prompts; zero model calls)
- **Depends on:** 0b.7, 0b.8, 0b.9
- **Acceptance:** `estimatedCalls.min`/`.max` equal the §5.2 formula over the plan's own recorded terms, recomputed by the test with no literals · **reconciliation:** `len(plannedEntries) + Σ unplannedDeficits.count == Σ_role max(0, budget[role] − actual[role])`, and every planned entry would carry `structureKind != none` and is not field-for-field a renamed existing row of its role · the dry run writes exactly one prompt per planned entry and makes **zero** model calls (the stub raises, the offline guard is active), two runs are byte-identical, and no test asserts prompt text beyond structural presence
- **Verify:** `$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_structure_planner.py tools/seedsmith/tests/test_structure_dry_run.py gk-forge/tools/seedsmith/tests/test_offline_guarantee.py -q` and `.\scripts\verify-change.ps1 -Paths gk-forge/tools/seedsmith/seedsmith/adapters/structures/planner.py,gk-forge/tools/seedsmith/seedsmith/report/cli.py -Session <session-id>`
- **Shared files:** none from landing-order §4
- **Notes:** `voteFields` is `[]` with a stated reason, because every enum here is planner-fixed. The call count is a **reading** printed by the dry run, never an asserted constant — the whole point of this task is to state Wave ES3's cost before the owner approves spending it.

### [ ] ES2.2 `decision-45-revision` — structure-corpus ownership moves to `empire-seed` (D-E2)
- **Spec:** docs/architecture/empire-seed/spec-decision-45-revision.md
- **Wave:** ES2 · no flag, no bump (R3: documents only)
- **Depends on:** owner approval of `empire-seed-map.md` (already given, 2026-09-19); no code edge
- **Acceptance:** every row of the spec's §5 table carries its revision, walked by the review · no sentence in an edited document still states **as current fact** that `base-defense` owns the structure corpus — the grep `structure-seed.*(module set|folds into)` hits only annotated historical lines · `audit-doc-citations.py` reports no HIGH finding for each edited file, and no shipped base-defense spec, evidence line or checkbox changes meaning
- **Verify:** `python scripts/audit-doc-citations.py --scope docs/architecture/base-defense-ideal.md` (and once per edited document), then `.\scripts\verify-change.ps1 -Paths docs/architecture/decisions.md,docs/DESIGN-GATE.md,docs/architecture/base-defense-map.md,docs/architecture/structure-seed-ideal.md,docs/architecture/trade-network-ideal.md -Session <session-id>`
- **Shared files:** none from landing-order §4
- **Notes:** adds the `decisions.md` ownership row carrying D-E1 and D-E2 and the `DESIGN-GATE.md` §1 row for structure and empire content generation — that row is missing today (`empire-seed-map.md:408`), so no future session is gated on reading this cluster's documents until this task lands. History is annotated, never rewritten.

---

## Wave ES3 — `empire-seed` W3 (the one model stage)

### [ ] ES3.1 `world-namer` — identity text only, frozen ids, byte-identical reruns
- **Spec:** docs/architecture/empire-seed/spec-world-namer.md
- **Wave:** ES3 · no flag, no bump (R3: seed content; the corpus is data the catalog loads, not a rule)
- **Depends on:** ES2.1, 0b.9, 0b.7, 0b.8
- **Acceptance:** a draft with a digit, an empty field, a role-word echo, a taken name or an over-bound length is rejected with the defect named, repaired at most `maxRepairs` times, then `unresolved` — never emitted, never given a fallback · the proof call runs before any naming call; a transient error resumes without a new call for completed entries; a rerun over unchanged inputs makes **zero** calls and leaves the accepted store and the tree byte-identical · **ids are frozen:** regenerating a stale entry with a different name keeps its `id` byte-identical and a fixture save referencing it still loads its structure (A-ES1)
- **Verify:** `$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest tools/seedsmith/tests/test_structure_namer.py gk-forge/tools/seedsmith/tests/test_offline_guarantee.py -q` and `.\scripts\verify-change.ps1 -Paths tools/seedsmith/seedsmith/adapters/structures/naming.py,gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/schema.py,gk-data/packs/fusion/data/seed/structures -Session <session-id>`
- **Shared files:** none from landing-order §4
- **Notes:** the eight owner-named feature rows never pass through here; this task names only a planner deficit outside them, and flavour text. The avoid-list is **advisory** in the brief and never causes a rejection (IC-3 / S6) — the release scan is the gate. First batch small and reviewed before any larger run (the owner's standing phased-rollout rule). `max_heal`'s shipped default of 3 is overridden to the two-repair bound (S8).

---

## Wave ES4 — `empire-seed` W4 (legion seed contracts)

Lands after ES3 and after `legion-build`'s three **approved specs** — approved specs, not built code, so the
two programs do not wait on each other.

### [ ] ES4.1 `legion-seed-contract` — the `legion` adapter and four number-free schemas
- **Spec:** docs/architecture/empire-seed/spec-legion-seed-contract.md
- **Wave:** ES4 · no flag, no bump (R3: schemas, a registry and hand-authored exemplars)
- **Depends on:** 0b.3, 0b.7; cross-cluster: family row 0f (`legion-build` W1) plus the **approved specs** for `legion-equipment` (the legion slot list), `legion-traditions` (trigger facts) and `legion-standards` (carrier roles) — approved specs, not built code, so the two programs do not wait on each other
- **Acceptance:** `numeric_audit` reports nothing for each of the four schemas and a fixture schema with each of the four smuggling shapes is rejected; every field has exactly one ownership level and a negative clause · every closed enum admits `none` or states why not, a missing key fails validation, and every VALIDATED value in every exemplar joins its registry (elements, the atom namespace, `MaterialCatalog.All`, `vocab.v1.json`) · no set/socket/affix-pool/roll property exists on `legion-equipment` at any depth and no inheritance-shaped field on `legion-standard`/`legion-tradition`; the C# parse rejects an unknown VALIDATED value naming the field
- **Verify:** `$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest tools/seedsmith/tests/test_legion_contract.py -q` and `.\scripts\verify-change.ps1 -Paths tools/seedsmith/seedsmith/adapters/legion,gk-forge/tools/seedsmith/seedsmith/adapters/registry.py,data/seed/legion/_registry/vocab.v1.json,data/seed/legion/_exemplars -Session <session-id>`
- **Shared files:** none from landing-order §4
- **Notes:** `data/seed/legion/_registry/vocab.v1.json` is the **one** shared legion vocabulary registry (round 4 Q12); `legion-build`'s C# enums are validated against it at load, and each list is pinned as a closed vocabulary naming the `legion-build` spec that decided it. `rankNames[]` is one-or-more and independent of tuning, so a balance publish never invalidates a generated seed (A-ES3). `pieceId` is DERIVED, minted once per plan key and frozen (A-ES1). This cluster must **not** invent any of the three `legion-build` vocabularies. `data/seed/legion/**` needs its own verification-boundary row (R3-style obligation; `empire-seed-map.md:1015` leaves it with `python-test-lane`).

---

## Wave ES5 — `empire-seed` W5 (legion seed bands)

### [ ] ES5.1 `legion-bands` — legion ordinals resolve to numbers, identically for every player
- **Spec:** docs/architecture/empire-seed/spec-legion-bands.md
- **Wave:** ES5 · no flag, no bump (R3: a tuning file and a load-time resolver)
- **Depends on:** ES4.1, 0b.3
- **Acceptance:** two catalog builds from equal inputs give deeply equal `LegionPieceDef` sequences and the function's parameters contain no player, world or seed · every committed piece's `spentAeHundredths` is strictly below `allowance × shareMilli / 1000` at its reference rung, with `0 < shareMilli < 1000` validated at load; a missing rung, reference rarity, atom-at-tier or an `atomFamilies` overrun each throw naming the key · every budget is `long` and `checked` (`long.MaxValue` into the share product throws `OverflowException`), a piece's atom value is the **midpoint** of its generated range, and a family whose atom kind the legion readers do not deliver is a load rejection
- **Verify:** `.\scripts\verify-change.ps1 -Paths data/tuning/legion-seed.v1.json,src/FusionRpg.Core/World/Legion/LegionEquipmentCatalog.cs,gk-core/scripts/verification-boundaries.v1.json,tests/FusionRpg.Core.Tests/World/Legion/LegionBandsTests.cs -Session <session-id>` and `python -m pytest tools/seedsmith/tests/test_legion_contract.py -q`
- **Shared files:** none from landing-order §4
- **Notes:** **§5 tuning creator:** this task authors `data/tuning/legion-seed.v1.json` (`landing-order.md §5`) — seed magnitudes only; every mechanic stays in `legion-build`'s `legion.v1.json`, and no key is in both. `publish.py` cannot create a first version of a new domain (`gk-core/tools/tuning/publish.py:60-68`), so extend the tool here rather than hand-writing the file, and add its verification-boundary row in the same change (R3 / M6). **Gated:** the standard tier and tradition rank multiplier ladders are **not published** until their `ssot-power-scale.md` §10.2 rows exist (A-ES2 / A-LB4). The standard ladder is three rungs (Banner Yard → Standard Hall → Hall of Triumphs, owner 2026-09-20) — the rung count is fixed here, the multipliers wait.

---

## Wave ES6 — `empire-seed` W6 (legion seed rows)

Lands after ES5 **and** after wave L7's shipped mechanics — a catalog for a mechanic that does not exist is
content nobody reads.

### [ ] ES6.1 `legion-seed-rows` — planner-first legion seeds over the closed grids
- **Spec:** docs/architecture/empire-seed/spec-legion-seed-rows.md
- **Wave:** ES6 · no flag, no bump (R3: generated seed content)
- **Depends on:** ES5.1, ES3.1; cross-cluster: `legion-build`'s shipped mechanics (layer 5c binder and reader, `OwnerKind.Legion`, stack `Count`, the stack-scoped equipment layer) — a catalog for a mechanic that does not exist is content nobody reads
- **Acceptance:** every planned entry ends as an accepted seed in the tree **or** `unresolved` in the ledger, never both and never neither, and every seed passes the ES4.1 contract and every closed-loop metric · per-cell counts sit inside the published band read from tuning and no cell exceeds the published maximum; `LegionEquipmentCatalog` builds from the tree and every piece stays under the share bound · a rerun makes zero calls and the tree is byte-identical, the planner's output is byte-identical across two builds, and shuffling input file order changes nothing
- **Verify:** `$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest tools/seedsmith/tests/test_legion_rows.py gk-forge/tools/seedsmith/tests/test_offline_guarantee.py -q` and `.\scripts\verify-change.ps1 -Paths data/seed/legion,src/FusionRpg.Core/World/Legion/LegionEquipmentCatalog.cs -Session <session-id>`
- **Shared files:** none from landing-order §4
- **Notes:** generated tree — regenerate and commit the diff; never hand-edit a row to make a test pass. No test pins a seed count or asserts a generated string; per-cell coverage is checked against the published band and the rest is printed as a reading.

---

## Wave L2 — `legion-build` W2 (the stack fights, and a legion runs itself)

Two capability rows on one bump **`L2`**: `legion.stacks` (L2.1, with L2.2 as its only producer) and
`legion.standingOrders` (L2.4). Two rows sharing one bump is landing-order R2, the precedent being family
row 15's four rows. Lands after row 0e.

### [ ] L2.1 `stack-combatant` — a stack of N enters the engine as one combatant
- **Spec:** docs/architecture/legion-build/spec-stack-combatant.md
- **Wave:** L2 (after family row 0e) · flag `legion.stacks` (this task registers it) · bump `L2`, the wave's one
- **Depends on:** 0e.1, 0e.3
- **Acceptance:** (1) every existing battle, delve, siege, expedition and web golden is byte-identical while no setup carries a count (run, not argued); (2) a stack's hit is exactly `LivingUnits ×` the single-unit damage for the same RNG draw, overflow kills whole units before wounding the next, `UnitsRemaining ≤ UnitCount`, and a heal restores the top unit without raising the living count; (3) register row 21 (*"Stack body"*) lands in `battle-engine-ssot.md` §3b in the same change, and one conformance test drives a stacked setup through battle, siege and delve to the same `UnitsRemaining` for one seed.
- **Verify:** `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Battle/BattleModels.cs,src/FusionRpg.Core/Battle/StackBody.cs,gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs,gk-core/src/FusionRpg.Core/Battle/BattleEngine.cs,gk-core/src/FusionRpg.Core/Combat/DamageApplyPipeline.cs,gk-core/src/FusionRpg.Core/Combat/Shield/ShieldGate.cs,gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultResolver.cs,docs/architecture/battle-engine-ssot.md -Session <session-id>` plus `.\scripts\guard-actor-hub.ps1`
- **Shared files:** none of §4's five.
- **Notes:** amends a closed register (reviewed change, owner Q1); widens `hitCount` to `long` at both sites so a large stack cannot throw mid-battle (A-LB9); flips `StackCombatantLanded` in the commit that proves the scaling tests.

### [ ] L2.2 `raise-choice` — a raise names its species, size and role
- **Spec:** docs/architecture/legion-build/spec-raise-choice.md
- **Wave:** L2 (after family row 0e) · rides `legion.stacks` (it is that flag's producer half) · rides bump `L2`
- **Depends on:** 0e.1, L2.1 (lifts the `Count > 1` gate)
- **Acceptance:** (1) a raise carrying none of the three new optional fields behaves byte-identically to today; (2) a legal raise founds exactly the stack it names and spends exactly `raiseCostPoints` per unit, while an illegal species, size or role is dropped with its own named reason; (3) `Bearer` becomes producible in play and replay derives the same entity and member ids.
- **Verify:** `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs,gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs,gk-core/src/FusionRpg.Core/World/Growth/RaiseResolver.cs,gk-core/src/FusionRpg.Core/Actions/CrossProgramLandedFlags.cs,gk-core/src/FusionRpg.Contracts/WorldDtos.cs,gk-core/src/FusionRpg.Server/WorldEndpoints.cs -Session <session-id>`
- **Shared files:** `WorldCommand.cs` — the L2 slot: three optional fields on the existing `raise` arm, adding no command kind
- **Notes:** the pool is the raising faction's own side plus the sector's pool, both climate-filtered (round 4 Q6); sector-specific recruit/train/hire buildings stay out (round 4 §U). Web contract fixture paths are unmapped (X-18, as 0e.1).

### [ ] L2.3 `legion-owner-scope` — layer 5c and the one legion reader
- **Spec:** docs/architecture/legion-build/spec-legion-owner-scope.md
- **Wave:** L2 (after family row 0e) · registers no flag; it grants no player-facing capability of its own (its dependents do), so it adds nothing to bump `L2`
- **Depends on:** 0e.1, 0e.3
- **Acceptance:** (1) `OwnerKind.Legion` is durable, world-qualified (`legion:{worldId}/{entityId}`) and gated on a world host; a bound `world-buff` container contributes to every fighting member of that legion and to no other actor, each contribution carrying a non-empty SourceId `FictionLabel` explains; (2) the reconcile is idempotent and leaves bindings equal to the desired set at **every** trigger T1–T5, including a world created with legions and a legion arriving by advance, with one test each and a source scan that every world-graph writer calls it; (3) the three register rows (`decisions.md` 5c, `definitions.md` §6, `actor-hub-ssot.md` §8.1) and the enforcement row land in the same change, `guard-actor-hub.ps1` green.
- **Verify:** `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Effects/Atoms/OwnerScope.cs,gk-core/src/FusionRpg.Core/Effects/Atoms/BindGate.cs,src/FusionRpg.Core/World/Legion/LegionBuffSources.cs,gk-core/src/FusionRpg.Core/Stats/Derived/ContributionSourceIds.cs,src/FusionRpg.Data/Sqlite/RpgStore.LegionBuffs.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs,gk-core/scripts/enforcement-registry.v1.json,docs/architecture/decisions.md -Session <session-id>`
- **Shared files:** `RpgStore.WorldTurns.cs` — the L2 slot: the reconcile call in the commit transaction, additive, no column
- **Notes:** ships with an **empty** contributor list, so nothing binds until L4 and no golden moves — which is also why it grants nothing here. `world-continuity`'s `world-creation`, `advance-carry` and `coarse-step` owe the same reconcile call in their own specs (A-LB1, cross-program obligation).

### [ ] L2.4 `standing-orders` — one stored order per legion, re-emitted each turn
- **Spec:** docs/architecture/legion-build/spec-standing-orders.md
- **Wave:** L2 (after family row 0e) · flag `legion.standingOrders` (this task registers it; second row on bump `L2`, R2) · rides bump `L2`
- **Depends on:** nothing in this cluster; `fleet` (rows 12–13) waits on it, so it is the wave's priority
- **Acceptance:** (1) an emitted command is indistinguishable from the same command filed by hand — same admission, same drops, same report lines — and an explicit order for that legion this turn wins, tested in **both** submission orders; (2) a world where no legion holds an order hashes byte-identically and replay needs no emitter; (3) the kind seam is live with `repeat` registered here, and the emitter walks `(Pass, EntityId)` so a charge's command is always resolved before its escort's.
- **Verify:** `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/World/WorldState.cs,src/FusionRpg.Core/World/Orders/StandingOrder.cs,src/FusionRpg.Core/World/Orders/RepeatOrderResolver.cs,src/FusionRpg.Core/World/Orders/StandingOrderEmitter.cs,gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs,gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs,gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs,gk-core/src/FusionRpg.Core/World/WorldCanonical.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldGraphDiff.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs,gk-core/src/FusionRpg.Contracts/WorldDtos.cs,gk-core/src/FusionRpg.Server/WorldEndpoints.cs -Session <session-id>`
- **Shared files:** `WorldState.cs` (after 0e.2); `WorldCanonical.cs` — an `order` row present only for holders, so no append slot is consumed; `WorldCommand.cs` — `set-order` and `clear-order` with one admission arm each (row 7's five verbs are the precedent for a pair in one wave); `TurnEngine.cs` — Snapshot set/clear, and where bump `L2` lands; `RpgStore.World.cs` one nullable column
- **Notes:** the spec's Hard edges still claim *"no bump and no re-bless"* — superseded by round 6 C1: it grants a feature, so it rides the wave's bump. **The spec correction landed** in the reconciliation (R-19.4): `spec-standing-orders.md` Hard edges now reads *new hashed state, no re-bless, but it does ride its wave's bump*.

---

## Wave L3 — `legion-build` W3 (a general member composes through ActorHub)

Its own wave, not part of L2, because it waits on another program's landing and its re-bless must be ordered
after that program's — a shared bump would hold wave L2 hostage to `species-progression`.

### [ ] L3.1 `general-member-hub` — a general world member reads its empire's layer 2b
- **Spec:** docs/architecture/legion-build/spec-general-member-hub.md
- **Wave:** L3 (after family row 0e) · flag `legion.generalHub` (this task registers it) · bump `L3`, its own
- **Depends on:** 0e.1; external `species-progression` `layer-source-selector` (must land first, X4), `empire-species-container`, `species-layer-delivery` 6.1, `empire-progression` `ai-empire-species`
- **Acceptance:** (1) for the same `(empire, species, level)` a general world member and a general lawn actor resolve the same 2b contribution by channel and SourceId, reading the empire that owns the legion (owner Q2); (2) a general member never receives a 2a or a commander allocation term, and a Wild/Clan/Rival force carries no 2b; (3) with 2b empty siege results are unchanged, `guard-actor-hub.ps1` is green and no second composer exists; a trimmed turn whose stored report holds a store-composed battle **refuses** re-derivation rather than fabricating flat-stat results.
- **Verify:** `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultResolver.cs,src/FusionRpg.Core/World/LegionEmpire.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs -Session <session-id>` plus `.\scripts\guard-actor-hub.ps1`
- **Shared files:** `RpgStore.WorldTurns.cs` — the L3 slot: the general branch of the Hub-inputs provider, the `LegionMemberAtoms` join and the composed-battle boolean on the stored turn log
- **Notes:** owns a siege golden re-bless for general members, ordered **after** `species-progression`'s own so no value moves twice. Four cross-doc corrections are owed by their owners (the `decisions.md` *Actor layer stack* row, `spec-layer-source-selector.md` rule 2, `spec-species-layer-delivery.md:28`, `spec-legion-commander.md:117-121`).

---

## Wave L4 — `legion-build` W4 (the legion's own identity layer)

Two capability rows on one bump **`L4`**: `legion.escortStance` (L4.1) and `legion.traditions` (L4.3). The
other three land inert — L4.2 with empty bands, L4.4 with a flat curve, L4.5 read by nothing in `Step` — so
under R3 they grant no capability and add nothing to the bump.

### [ ] L4.1 `escort-stance` — a legion moves with and screens its charge
- **Spec:** docs/architecture/legion-build/spec-escort-stance.md
- **Wave:** L4 (after family row 0e) · flag `legion.escortStance` (this task registers it) · rides bump `L4`
- **Depends on:** L2.4 (the kind seam and the barrier emitter); the join clause's integration waits on L5.1
- **Acceptance:** (1) the hold contract holds for every row of the spec's table, including a caravan's whole loading loop — an escort never outpaces or strands its charge; (2) losing the charge ends the order with a named reason; (3) a world with no escort resolves byte-identically, and the stance membership test names whatever `MovementPolicy.Stances` holds at landing (`world-continuity` widens the same list, so no `4 → 5` count).
- **Verify:** `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/World/Movement/LaneCost.cs,gk-core/src/FusionRpg.Core/World/Movement/MovementPhase.cs,gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs,src/FusionRpg.Core/World/Orders/EscortOrderResolver.cs,src/FusionRpg.Core/World/Orders/StandingOrder.cs,src/FusionRpg.Core/World/Turn/EscortJoin.cs -Session <session-id>`
- **Shared files:** none of §4's five.
- **Notes:** lands with its battle-presence clause **inert** — no sector, lane or guard fight resolves yet, so the `BattleSeam` refusal stands; L5.1 wires the join predicate and carries that re-bless (map §14 closed-cycle note). Its FE stance word is a `web/` path with no boundary owner (X-18).

### [ ] L4.2 `legion-cohesion` (code half) — the band reader, bands empty
- **Spec:** docs/architecture/legion-build/spec-legion-cohesion.md
- **Wave:** L4 (after family row 0e) · registers no flag: with empty bands nothing contributes, so R3 applies — it adds nothing to bump `L4`; the behaviour is granted by L8.1
- **Depends on:** 0e.1, 0e.3, L2.3
- **Acceptance:** (1) the band reader is a pure, order-free function of the fighting roster's count-weighted element spread — reordering members never changes it; (2) band containers are projected from tuning, and a binding appears or disappears in the same commit the roster crosses a band edge; (3) the empty first publish moves nothing — no contribution, no golden.
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Legion/LegionCohesion.cs,src/FusionRpg.Core/World/Legion/LegionTuning.cs,src/FusionRpg.Core/World/Legion/LegionBuffSources.cs,data/tuning/legion.v1.json,gk-core/tools/tuning/publish.py,gk-core/scripts/verification-boundaries.v1.json -Session <session-id>`
- **Shared files:** none of §4's five. **Tuning:** this task is the single creator of `data/tuning/legion.v1.json` (landing-order §5); every later legion module publishes `v{n+1}`, and seed magnitudes stay in `empire-seed`'s `legion-seed.v1.json` (round 4 Q12) behind one shared legion vocabulary registry.
- **Notes:** `data/tuning/legion.v*.json` has **no** verification-boundary owner today, so `verify-change.ps1:118` throws — adding the mapping is part of this task (ask X-18, program rule R3). Core parses a string; the host reads the file (A-LB14).

### [ ] L4.3 `legion-traditions` — a legion earns ranks from its own history
- **Spec:** docs/architecture/legion-build/spec-legion-traditions.md
- **Wave:** L4 (after family row 0e) · flag `legion.traditions` (this task registers it) · rides bump `L4`
- **Depends on:** 0e.1, L2.3
- **Acceptance:** (1) each counter advances from exactly one kind of world fact, once per fact; (2) rank thresholds come from tuning on a soft curve extended past its last authored point by the last segment's slope — no top rank, no cap, and a finite name list is presentation only; (3) rout and disband wipe the history totally and every contribution follows in the same commit; the `triggerKind` list is pinned as a closed vocabulary with its stated reason.
- **Verify:** `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/World/WorldState.cs,src/FusionRpg.Core/World/Legion/LegionHistory.cs,gk-core/src/FusionRpg.Core/World/Turn/BattleApplication.cs,gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs,gk-core/src/FusionRpg.Core/World/Movement/MovementPhase.cs,gk-core/src/FusionRpg.Core/World/WorldCanonical.cs,data/tuning/legion.v2.json -Session <session-id>`
- **Shared files:** `WorldState.cs` (the L4 slot); `WorldCanonical.cs` — a `history` row only when non-empty, so no append slot is consumed; `TurnEngine.cs` — the claim-settle observe and where bump `L4` lands. **Tuning:** `legion.v{n+1}` (`traditions.rankThresholds`).
- **Notes:** carries a **large** re-bless — every legion that fights accumulates hashed history, so every world golden with a battle moves; one explained re-bless in this commit. Binds rank 1 only until the two `ssot-power-scale.md` §10.2 rows land (A-LB4, requested from the power program).

### [ ] L4.4 `legion-count-cost` (code half) — the curve term, flat
- **Spec:** docs/architecture/legion-build/spec-legion-count-cost.md
- **Wave:** L4 (after family row 0e) · registers no flag: at 1000‰ everywhere burn is exactly today's, so R3 applies and it adds nothing to bump `L4`; the behaviour is granted by L9.1
- **Depends on:** 0e.1, L4.2 (the `legion` tuning domain and its parser)
- **Acceptance:** (1) with the curve flat at 1000‰ the burn is exactly today's value; (2) the curve is validated monotone non-decreasing with its first point ≥ 1000‰ and extends past its last authored point by the last segment's slope, so there is no count at which a legion cannot be fielded; (3) exactly one term inside the existing legion burn — no new quantity, no second pricer.
- **Verify:** `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs,gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs,gk-core/src/FusionRpg.Server/WorldEndpoints.cs,data/tuning/legion.v3.json -Session <session-id>`
- **Shared files:** none of §4's five. **Tuning:** `legion.v{n+1}` (`countCost.curve`).
- **Notes:** it reads legion **count**, not level, so it is not a power-ladder curve and owes no `ssot-power-scale.md` §10 row — the spec states that rather than leaving it implied. A clamped tail would be a cap on a scaling sink (A-LB5).

### [ ] L4.5 `legion-power` — one roll-up, summed from Hub output only
- **Spec:** docs/architecture/legion-build/spec-legion-power.md
- **Wave:** L4 (after family row 0e) · registers no flag; nothing in `Step` reads it until a consumer lands, so it adds nothing to bump `L4` and claims none of its own
- **Depends on:** 0e.1, 0e.3, L3.1 (the world member's Hub inputs)
- **Acceptance:** (1) one Standing algorithm serves the sheet and the world, with sheet output byte-identical (leaf-identity test); (2) `legionPower` = Σ over fighting members of `unit Standing label × Count` — order-independent, `long` and `checked` with no clamp, a bearer adding 0 to combat power while still carrying and burning; (3) the six `world.*` channels roll up **only** through `LegionWorldChannels` with §6's per-channel aggregators (Σ for carry and burn, min for march and hazard, max for sight, `world.upkeep.discount` per unit and divided last), proven by a source scan that finds no other fold, and no file or type is named `*Composer*`.
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/Stats/Derived/StandingProjection.cs,gk-core/src/FusionRpg.Server/UniqueActorHubCompose.cs,gk-core/src/FusionRpg.Core/Battle/BattleHubCompose.cs,src/FusionRpg.Core/World/Legion/LegionPower.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs -Session <session-id>` plus `.\scripts\guard-actor-hub.ps1`
- **Shared files:** `RpgStore.WorldTurns.cs` — the `LegionPowerFor` delegate built in the commit transaction, after L3.1's provider branch
- **Notes:** blocked-consumer rule from cross-program ask **X-2**: no consumer turns two rolled-up powers into odds until the `ssot-power-scale.md` §10 contest row lands — until then the warden defence term is **0** and escort strength stays the v1 stance count. Reconciliation **R-9** narrowed X-2's blocking list to exactly those two — row 23 and `world-warden`'s defence term; `deal-valuation` (19a.2) and `ai-trade-buildings` (19d.1) read this roll-up **to choose** and are not blocked by it. `world-derived` (round 6 D2) registers the six channels; consumers read the stated defaults until it ships. `PowerVector`'s `int` fields are the effect-atom program's E9 ask.

---

## Wave L5 — `legion-build` W5 (field battles become real)

### [ ] L5.1 `field-battle-kinds` — sector, lane and guard fights resolve in the engine
- **Spec:** docs/architecture/legion-build/spec-field-battle-kinds.md
- **Wave:** L5 (after family row 0e) · flag `legion.fieldBattles` (this task registers it) · bump `L5`, its own — the wave is one module
- **Depends on:** 0e.3, L2.1, L3.1, L4.1 (the join predicate)
- **Acceptance:** (1) all four kinds resolve through the one `BattleEngine.Resolve` entry and a district assault is unchanged; (2) a fight with no living attacker is still refused rather than invented, and the field board **grows to fit** so no force is too large to intercept — the tuned size is a minimum, never a ceiling; (3) replay is byte-identical and multi-entity sides resolve per entity (fleet ask A8 closed).
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Turn/WorldBattleResolver.cs,src/FusionRpg.Core/World/District/FieldLayout.cs,gk-core/src/FusionRpg.Core/World/Turn/BattleSeam.cs,gk-core/src/FusionRpg.Core/World/Turn/BattleReporting.cs,gk-core/src/FusionRpg.Core/World/Turn/BattleApplication.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs,data/tuning/legion.v4.json -DeletedPaths gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultResolver.cs -Session <session-id>`
- **Shared files:** `RpgStore.WorldTurns.cs` — constructs the renamed resolver. **Tuning:** `legion.v{n+1}` (`field.boardRows`/`boardCols` minimums).
- **Notes:** carries the turn-golden re-bless wherever a refused fight becomes a real one, and wires L4.1's inert join clause. This is one of the three points where the **full** suite is the right call (a change crossing module boundaries). Retires the `world-actor-combat` track id — a line owed in the solid-fixing program's docs, not made here.

---

## Wave L8 — `legion-build` W8 (the cohesion band publish)

A tuning-only publish that makes an inert term real is its own landing, with its own flag and bump — a flag
is never registered before the behaviour it gates exists (round 6 C1).

### [ ] L8.1 `legion-cohesion` (band publish half) — the bands get atoms
- **Spec:** docs/architecture/legion-build/spec-legion-cohesion.md (Hard edges, *"two-step landing"*)
- **Wave:** L8 (after family row 0e; only L4.2 binds it) · flag `legion.cohesionBands` (this task registers it) · bump `L8`, its own — round 6 C1: a flag is never registered before the behaviour it gates exists
- **Depends on:** L4.2
- **Acceptance:** (1) the bands ship as `legion.v{n+1}` through `gk-core/tools/tuning/publish.py` — never a hand edit of a published file; (2) band magnitudes are scaled exactly once, by `legion-owner-scope`'s reader (`ContentScale.Apply`), with no literal in code and no second scaling; (3) the siege goldens this publish moves are re-blessed with the reason in the publishing commit, and a world stamped before this wave never gains the bands mid-life.
- **Verify:** `.\scripts\verify-change.ps1 -Paths data/tuning/legion.v8.json,gk-core/tools/tuning/publish.py -Session <session-id>` (the boundary mapping added by L4.2 is what selects a suite here)
- **Shared files:** `TurnEngine.cs` — where bump `L8` lands.
- **Notes:** the W58 precedent — a tuning-only publish that makes an inert term real is its own landing. `minShareMilli`'s first value is decided by principle at the publish, not asked of the owner (tunables are not an owner question).

---

## Wave L9 — `legion-build` W9 (the legion-count cost curve publish)

### [ ] L9.1 `legion-count-cost` (curve publish half) — the curve bends
- **Spec:** docs/architecture/legion-build/spec-legion-count-cost.md (Hard edges, *"two landings, two bumps"*)
- **Wave:** L9 (after family row 0e; only L4.4 binds it) · flag `legion.countCostCurve` (this task registers it) · bump `L9`, its own
- **Depends on:** L4.4
- **Acceptance:** (1) published as `legion.v{n+1}` through `gk-core/tools/tuning/publish.py`; (2) the published points are monotone non-decreasing, the first ≥ 1000‰, and the tail extends by the last segment's slope — no flat tail on an upkeep facing a scaling sink; (3) the loam goldens it moves are re-blessed with the reason in the publishing commit.
- **Verify:** `.\scripts\verify-change.ps1 -Paths data/tuning/legion.v9.json,gk-core/tools/tuning/publish.py -Session <session-id>` plus `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~World.Loam"`
- **Shared files:** `TurnEngine.cs` — where bump `L9` lands.
- **Notes:** A-LB5 is the reason this is a publish and not a default: a curve that bends changes every faction's burn, which is behaviour, so it needs its own flag and bump rather than riding L4's.

---

## Wave WC2 — `world-continuity` W2 (the save-scoped End Turn counter)

One task, **no flag and no bump** (R3). It fixes the shipped cross-world decay-tick collision, so it lands
before any save can hold a second world.

### [ ] WC2.1 `hibernation-clock` — pending turns are a subtraction, and decay ticks stop colliding
- **Spec:** docs/architecture/world-continuity/spec-hibernation-clock.md
- **Wave:** WC2 · no flag, no bump (R3: a save-scoped counter column and a ledger tick re-key; acceptance 6 pins that no world's `StateHash` moves and a one-world save's decay outcomes are unchanged)
- **Depends on:** 0f.1
- **Acceptance:** committing N advancing turns in the active world raises `Pending` of every hibernating world of that save by N, up to the window, with **zero** writes to their rows (row `revision` unchanged); a `waiting` commit does not advance the counter · `Pending` never exceeds `catchUpCapTurns` and a negative raw value throws · decay ticks are unique per `(cache, save counter)` whichever world committed — switching A→B→A across commits rolls each cache exactly once per End Turn, tested in both switch orders — and the migration is idempotent, with a one-world save's post-migration decay outcomes equal to the pre-change ones
- **Verify:** `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CacheDecay.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs,gk-core/tools/tuning/publish.py,data/tuning/world-continuity.v1.json,gk-core/scripts/verification-boundaries.v1.json,tests/FusionRpg.Data.Tests/World/HibernationClockTests.cs -Session <session-id>`
- **Shared files:** `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs` — an additive `EnsureColumn` for the save counter, taken in §4's order after row 0a's ledger tables; no existing column changes meaning
- **Notes:** **§5 tuning creator:** this task authors `data/tuning/world-continuity.v1.json` (`landing-order.md §5`) with `catchUpCapTurns`, and every later continuity module publishes `v{n+1}`. `publish.py` cannot create a first version of a new domain (`gk-core/tools/tuning/publish.py:60-68`), so extend the tool here (tunables-ssot T4) and add the file's verification-boundary row in the same change (program rule R3, A-WC13). `catchUpCapTurns` gets a `ssot-power-scale.md` §11 row as a **structural** bound, commented as such; `rpg_worlds.catch_up_cap` stays unread and is documented as reserved. Fixes the shipped cross-world decay-tick collision, so it lands before any save can hold a second world.

---

## Wave WC3 — `world-continuity` W3 (outcome, the coarse step and the fall)

Three tasks, **one flag `continuity.worldOutcome` and the wave's one bump, ordinal `C1`**, shared by all
three and taken at landing — exactly the sharing round 6 C1 names.

### [ ] WC3.1 `world-victory` — `outcome → won`, one durable fact, an escalation knob
- **Spec:** docs/architecture/world-continuity/spec-world-victory.md
- **Wave:** wave WC3 · flag `continuity.worldOutcome` (registered by this task) · the wave's one bump, ordinal **C1** in the world-continuity lane — accepted by reconciliation R-14 and now §2 row WC3
- **Depends on:** 0f.1, 0f.2
- **Acceptance:** taking the declared seat sets `Outcome = Won` and `OutcomeTurn = WonAtTurn = turn` in the same `Step`, with one `world.won` report entry, and `won` never becomes `contested` again · exactly one won-fact row per world — replaying or re-committing the turn inserts nothing — and `rpg_worlds.outcome` always equals `WorldState.Outcome` after a commit · a world that never takes the seat hashes byte-identically before and after (the outcome row is emitted only when not contested); a log that takes the seat moves hash, which is what the wave's bump covers; the escalation knob is monotone and equals today's orders at 1000‰
- **Verify:** `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/World/WorldState.cs,gk-core/src/FusionRpg.Core/World/WorldCanonical.cs,gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs,tests/FusionRpg.Core.Tests/World/WorldVictoryTests.cs,data/tuning/world-continuity.v2.json -Session <session-id>`
- **Shared files:** `WorldCanonical.cs` — the `Outcome` conditional row appends **after the last conditional row present at landing** (§4's order: `world-stamp`, `located-stock`, `logistics-canonical`, `carried-goods`, then later rows in §2 order); `WorldState.cs` — one additive record field; `TurnEngine.cs` — the wave's single `RulesetVersion` bump, one wave at a time; `RpgStore.WorldTurns.cs` — the won-fact row
- **Notes:** **Golden re-bless this task owns:** the `WorldCanonical` append-order goldens for worlds whose outcome is not `contested`, plus the fixtures that build a world at the live `RulesetVersion` and then grant the flag — re-blessed in this wave's own change, never batched with another wave's (`landing-order.md §6`). Publishes `world-continuity.v{n+1}` for `escalationAfterVictoryMilli` (a bounded per-mille ratio, commented as exempt).

### [ ] WC3.2 `coarse-step` — a closed form that composes `Step`'s own rule functions
- **Spec:** docs/architecture/world-continuity/spec-coarse-step.md
- **Wave:** wave WC3 · rides `continuity.worldOutcome` and the wave's one bump (ordinal **C1**) · `CoarseVersion` stays a separate refusal key
- **Depends on:** WC2.1, 0f.2, WC3.1; cross-cluster: family row 0a (`trade-foundation` `world-stamp` and `stock-deltas` — the rate source, which must name every hashed field each measured phase writes)
- **Acceptance:** determinism — the same `(world, seed, n, stamp, inputs)` gives a byte-identical `CoarseResult` and hash; **cost independent of `n`** — with `ICoarseTrace` attached the rule-function evaluation count for `n = 1` equals that for `n = catchUpCapTurns` on an event-free world (a structural assertion, never a timing); no wall clock inside · additivity on an event-free window (`Run(a)` then `Run(b)` equals `Run(a+b)` on every stock and stability field), `FadePolicy.ApplyN(x,b,n) == Apply^n(x,b)`, and production-side deltas strictly below `n` full steps' while upkeep is not reduced · **closed-form completeness** — a fixture phase writing a hashed field with no registered closed-form advance makes `CoarseStep` refuse at construction, `SlotDepletionMilli` advances and exhausts exactly as `n` full steps would, the loss-draw edges (`p ≤ 0`, `p ≥ 1`, `u = 0`) each have a test, and no hibernating world's pending ever exceeds `catchUpCapTurns` in normal play
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Turn/CoarseStep.cs,gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs,tests/FusionRpg.Core.Tests/World/Turn/CoarseStepTests.cs,gk-core/tests/FusionRpg.Guard.Tests/WorldDeterminismGuardTests.cs,data/tuning/world-continuity.v3.json -Session <session-id>`
- **Shared files:** `TurnEngine.cs` — composes its rule functions and shares WC3.1's single bump (no second bump in this wave); `RpgStore.WorldTurns.cs` — the coarse-record kind and the replay interleave
- **Notes:** owes four `enforcement-registry.v1.json` rows (no wall clock in `CoarseStep`; no loop over `n`; closed-form completeness; the one-record race guard). Replay is scoped to logs with no composed-battle flag — a flagged row **refuses by name**, never diverges silently (A-WC11). Publishes `world-continuity.v{n+1}` for `backgroundCatchUpsPerEndTurn` (a structural perf bound, commented) and the background keys it reads.

### [ ] WC3.3 `world-fall` — `outcome → fallen`, reported loss by loss
- **Spec:** docs/architecture/world-continuity/spec-world-fall.md
- **Wave:** wave WC3 · rides `continuity.worldOutcome` and the wave's one bump (ordinal **C1**)
- **Depends on:** 0f.2, WC3.2, WC3.1
- **Acceptance:** losing `Home` (capture or fade) sets `Outcome = Fallen` in that full step, or at the end of that coarse record, and the rule is **identical** for the active world and an old world (one helper, tested through both `Step` and `CoarseStep`) · `fallen` is terminal — retaking `Home` leaves `Fallen`, and `WonAtTurn` survives a fall · every sector lost in a coarse record appears as one fact in capture order before `world.fallen`; an active fallen world accepts End Turn while a non-active one refuses select and idle with named reasons; **no row is deleted** by a fall, asserted by row counts
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/WorldFall.cs,src/FusionRpg.Core/World/Turn/CoarseStep.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs,tests/FusionRpg.Core.Tests/World/WorldFallTests.cs,tests/FusionRpg.Data.Tests/World/WorldFallStoreTests.cs -Session <session-id>`
- **Shared files:** `WorldState.cs`/`WorldCanonical.cs` — no new row: `Fallen` is a value of WC3.1's `Outcome` field, so nothing new is appended
- **Notes:** nothing is deleted, so `world-reclaim` (reserved, not in this build) can still read a fallen world's history. Losing the **active** world is the same rule and the save never ends (owner Q2); a fallen world advances at the not-won carry weight, which WC5.2 reads.

---

## Wave WC4 — `world-continuity` W4 (the world warden and the idle world)

Two tasks, **one flag `continuity.warden` and the wave's one bump, ordinal `C2`**. Both modules grant a
player-facing feature, so neither claims "no bump".

### [ ] WC4.1 `world-warden` — a commander and legion holding a world, with no free freeze
- **Spec:** docs/architecture/world-continuity/spec-world-warden.md
- **Wave:** wave WC4 · flag `continuity.warden` (registered here) · the wave's one bump, ordinal **C2** (R-14, §2 row WC4)
- **Depends on:** WC3.2; cross-cluster: family row 0a (`system-commands`, which registers `release-warden`), `legion-build`'s `warden` stance (a reviewed widening in its vocabulary) and `legion-power`
- **Acceptance:** with a binding present, `StabilityMilli` moves exactly as without one (the freeze is gone), and a log recorded under ruleset 13 replays to its stored hashes · no route accepts `bind-warden` (the endpoint is 404 and admission's shipped `warden.retired` is the only refusal); after the idempotent migration and one resolution per world no sector holds a `WardenBindingId`, every former warden contract is unbound with `warden = 0`, loyalty unchanged and no soul-ledger row written · warden strength is the **logged** `legion-power` roll-up read from Hub output only (a replay with the Hub delegate absent succeeds), `defenceΘ` is 0 while no §10 row exists, loss odds with a warden are ≤ without for every Θ gap, and each warden legion pays its own garrison upkeep every turn in full and coarse steps alike
- **Verify:** `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/World/Loam/LoamPhases.cs,gk-core/src/FusionRpg.Core/World/Loam/LoamForecast.cs,gk-core/src/FusionRpg.Core/World/Movement/WardenResolver.cs,gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Contracts.cs,gk-core/src/FusionRpg.Server/WorldWardenEndpoint.cs,gk-web/web/fusion-rpg-web/src/stages/world/confirms/BindWardenDialog.tsx,data/tuning/world-continuity.v4.json -Session <session-id>`, plus `.\scripts\guard-actor-hub.ps1`
- **Shared files:** `gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs` — `release-warden` is registered in `trade-foundation`'s closed system set at row 0a (X11), so this task adds **no** command kind of its own; `TurnEngine.cs` — the wave's one bump
- **Notes:** **Golden re-bless this task owns:** the world goldens the retirement moves, plus the flagged fixtures, in this wave's own change. **Blocked in part by X-2** (`landing-order.md §7 (ask X-2)`): until the power program's `ContestTheta` row for a rolled-up power lands, the warden defence term is **0** — that is a wiring gap the acceptance states, not a reason to hold the wave. Owes an `enforcement-registry.v1.json` row (no Data-side write to `WardenBindingId`). Publishes `world-continuity.v{n+1}` for `wardenDefenceWeightMilli` and the upkeep keys.

### [ ] WC4.2 `idle-world` — the expedition wall clock, with a capped credited window
- **Spec:** docs/architecture/world-continuity/spec-idle-world.md
- **Wave:** wave WC4 · rides `continuity.warden` and the wave's one bump (ordinal **C2**)
- **Depends on:** WC4.1, WC3.2, WC2.1
- **Acceptance:** entering idle without a stationed warden, or on a fallen world, is refused with a named reason, and clock skew backwards yields 0 periods · credited periods never exceed `idleCreditedWindowPeriods` and the excess is forfeited **and reported**; resolution is pure over `(world, seed, periods, stamp, inputs)`, asserted by calling `CoarseStep.Run` in the test rather than a copy · a collect is idempotent (a retry resolves the same periods, a second collect in the same period writes nothing), idle never pays more per period than hibernating for the same world (load-time check plus test), and leaving idle starts hibernating pending at 0
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Turn/CoarseStep.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs,gk-core/src/FusionRpg.Server/WorldEndpoints.cs,tests/FusionRpg.Core.Tests/World/IdleWorldTests.cs,tests/FusionRpg.Server.Tests/IdleWorldEndpointTests.cs,data/tuning/world-continuity.v5.json -Session <session-id>`
- **Shared files:** none from landing-order §4 (`RpgStore.World.cs`'s idle anchor is outside that table)
- **Notes:** `turn_period_seconds` exists and is unread today; the idle period is a **tunable**, so that column stays unread rather than becoming a second home for one number. No second simulation: idle resolution calls the same `CoarseStep`. Publishes `world-continuity.v{n+1}` for `idlePeriodSeconds` and the window; `idleCreditedWindowPeriods` is registered as a bounded/structural limit with a comment.

---

## CHECKPOINT 0 — Foundation and content

**Rows 0a–0g** (the plan's §3 names them as 0a–0f; reconciliation R-1 added row 0g by renumbering
`material-ledger`). The lane waves in this stretch are not conditions of this checkpoint.

**Pass condition, from `tasks/trade-network-plan.md` §3:** the registry ships empty and no hash moves
(`GrantedBy` empty). The eight feature rows load under the neutral `StructureKind.Feature`, regenerated not
hand-edited, with the corpus `--check` gate green. The seat start kit (a tier-1 Counting House and a tier-1
Storehouse) re-blesses the template world goldens **once**, shared with `empire-roster` and `clan-seeding`.
Verification boundaries exist for `gk-forge/tools/seedsmith/**`, `gk-data/packs/fusion/data/seed/structures/**` and
`gk-core/data/tuning/<domain>.v*.json`. `material-ledger` is the only item that may still be open.

---

## PHASE 1 — The sector economy

Landing-order rows **1–4**, plus legion wave **L6**, which lands after row 1. 11 tasks.

---

## Row 1 — `sector-yield` W1 (stocks, capacity, halt, bank-point query)

Whole row: flag **`trade.sectorYield`**, registered by **1.4** with the **one bump N+2** the wave takes and
shared by every row it gates (R1/R2). Each task below gates on that flag; none registers a second.

### [ ] 1.1 `located-goods-registry` — a registry class for a banked good still on the map
- **Spec:** docs/architecture/trade-network/sector-yield/spec-located-goods-registry.md
- **Wave:** row 1 · flag `trade.sectorYield` (registered by 1.4) · bump N+2 (the wave's, taken by 1.4)
- **Depends on:** nothing
- **Acceptance:** every `MaterialCatalog.All` id appears in `LocatedGoodCatalog.All` exactly once as `Material` with `BankedId` equal to its own id, and `souls` exactly once as `Souls` — asserted as a join, never as a count · no located id is `loam`, `rubble`, `ironwork`, `recruit` or any world stock / accrual meter; the located→banked mapping is total over every banking kind and injective, `Get` on an unknown id throws, and `All` is in ordinal id order · `LocatedGoodKind` has exactly three members (closed vocabulary, pinned with its reason) and the registry's §2 class and §3 row land in the same change, stating P4 and P6.
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Goods/LocatedGoodCatalog.cs,tests/FusionRpg.Core.Tests/World/Goods/LocatedGoodCatalogTests.cs,docs/architecture/empire-resource-ssot.md -Session <session-id>` then `python scripts/audit-doc-citations.py --scope docs/architecture/empire-resource-ssot.md`
- **Shared files:** none
- **Notes:** first task of the row — the ideal and the map both require the class to be in before any other sector-yield module merges. The catalog's size is a reading; no test asserts it.

### [ ] 1.2 `essence-loop-read` — one scale read for located goods, both halves of the essence loop
- **Spec:** docs/architecture/trade-network/sector-yield/spec-essence-loop-read.md
- **Wave:** row 1 · flag `trade.sectorYield` (registered by 1.4) · bump N+2 (the wave's)
- **Depends on:** 0a.4; external `power` program's §10 row (ask X-4) and the `EssenceCount` widening (ask X-5)
- **Acceptance:** `LocatedScale.Milli` at `dangerBand` 4 (`MapLevel` 20, the pin) is exactly 1000, is positive and never throws at band 0, and a test feeding one sector through both the yield and the capacity paths fails if either used a different factor · `LoopScale` has exactly two members (closed, pinned with its reason), every family maps to exactly one loop read, and `souls` maps to Flat with a test that fails if it moves to Content while any call site still prices at `SoulSinkPolicy.VanillaPvzTheta` · a yield band naming an `essence.*` good is a load rejection until the sink half merges; with the sink merged a fusion at `Θ_sink` = 20 costs exactly today's essence count and the expedition faucet produces exactly today's amounts; `python gk-core/scripts/audit-overflow.py` reports no new finding.
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Goods/LocatedScale.cs,gk-core/src/FusionRpg.Core/Creatures/Fusion/FusionTuning.cs,gk-core/src/FusionRpg.Core/Creatures/Fusion/StarPolicy.cs,gk-core/src/FusionRpg.Core/Expeditions/ExpeditionResolver.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Fusion.cs,docs/architecture/power/ssot-power-scale.md,tests/FusionRpg.Core.Tests/World/Goods/LocatedScaleTests.cs -Session <session-id>` then `python gk-core/scripts/audit-overflow.py` and `python gk-core/scripts/guard-power.py`
- **Shared files:** none in §4; **cross-program:** `FusionTuning.cs`, `StarPolicy.cs`, `RpgStore.Fusion.cs`, `ExpeditionResolver.cs` are the creature and expedition programs' — the change carries their sign-off on `Θ_sink` (round 4 Q7)
- **Notes:** **blocker X-5** — *"Fusion essence cost scales by level"* (`EssenceCount` widens `int` → `long`) blocks this module and therefore row 1 as a whole: the spec will not ship one half of the PS-5 loop. Authors the located-goods-scale §10.2 row and the §10.4 line (part of ask X-4). Crosses Core + Data (fusion spend) — full suite once at module end. Recorded, not resolved: §10.4 ("materials must scale") vs §10.2 row 37 (crafting legs are rung coefficients) keeps shard/substrate/catalyst Flat.

### [ ] 1.3 `bank-points` — which sectors are a faction's bank points, as a pure query
- **Spec:** docs/architecture/trade-network/sector-yield/spec-bank-points.md
- **Wave:** row 1 · flag `trade.sectorYield` (registered by 1.4) · bump N+2 (the wave's)
- **Depends on:** 0d.1; external `empire-seed` `trade-structure-rows` (row 0c — the Counting House row with `featureUnlock: banking` and its tier variants)
- **Acceptance:** a sector holding an active banking building of any tier is in its owner's result, and after capture in the captor's and not the loser's; a building under first construction or unknown to the catalog grants nothing, while an upgrade in progress keeps the sector a bank point · an owned `Home` or `Boss` sector **without** a banking building is not a bank point, and no `bank`-role row makes one by its role (the soul conduit's sector is not one) · the result is in ordinal sector-id order with no duplicates, and two factions with identical holdings get identical results whatever their `WorldFactionKind`.
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Goods/BankPoints.cs,tests/FusionRpg.Core.Tests/World/Goods/BankPointsTests.cs -Session <session-id>`
- **Shared files:** none
- **Notes:** reads `SectorFeatures.TierFor` (round 6 S1), never `TierOf` and never an owner test of its own; recomputed per call, never cached. Tests run against a **fixture** banking row — no banking row is generated until row 0c, so the real-corpus proof is row 0c's, not this task's. Places no starting building: the A1 seat kit (tier-1 Counting House + Storehouse) is `world-continuity` `world-creation` and `counterparties` `empire-roster`/`clan-seeding`.

### [ ] 1.4 `located-stock` — a hashed pooled stock per (sector, located good), and the wave's flag
- **Spec:** docs/architecture/trade-network/sector-yield/spec-located-stock.md
- **Wave:** row 1 · flag `trade.sectorYield` — **this task registers it** · **bump N+2**, taken once here and shared by 1.1, 1.2, 1.3, 1.5, 1.6
- **Depends on:** 1.1, 0a.7 (and 0a.3 through it), 0a.4
- **Acceptance:** a world with no located stock produces canonical text **byte-identical** to today's for the same world, template and command log, while a non-empty stock changes the hash and two worlds differing only in one sector's stock hash differently · save → load round-trips the stock exactly, the diff writer writes a sector's row when and only when its stock (or another sector field) changed, and the equivalence guard passes on a turn that changes stock · every `LocatedStockOps.Add` produces exactly one stock delta and the reconciliation holds per sector and good; `Add` below zero throws leaving the sector unchanged, a zero result removes the entry, `Unpack` of a malformed string or unknown id throws, and no code outside `World/Goods/` assigns `LocatedStock` except the Data load path.
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Goods/LocatedStock.cs,src/FusionRpg.Core/World/Goods/LocatedStockOps.cs,gk-core/src/FusionRpg.Core/World/WorldState.cs,gk-core/src/FusionRpg.Core/World/WorldCanonical.cs,src/FusionRpg.Core/World/Ledger/WorldStockRegistry.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldGraphDiff.cs,tests/FusionRpg.Core.Tests/World/Goods/LocatedStockTests.cs,tests/FusionRpg.Data.Tests/World/LocatedStockPersistenceTests.cs,gk-core/scripts/enforcement-registry.v1.json -Session <session-id>` then `.\scripts\guard-dal.ps1` and `python gk-core/scripts/guard-test-substrate.py`
- **Shared files:** WorldState.cs (`WorldSector.LocatedStock`) · WorldCanonical.cs (**slot 2** of §4 — after the last conditional row present at landing, i.e. after 0a.4's stamp row) · RpgStore.World.cs + RpgStore.WorldGraphDiff.cs (column, equality, upsert, load — all four sites in this change, the rubble lesson)
- **Notes:** **golden re-bless owned here:** the `WorldCanonical` append-order goldens for row 1 (landing order §6), plus the fixtures/Data tests that build a world at the live `RulesetVersion` and then grant `trade.sectorYield` — re-blessed in this wave's own change, never batched with another wave's. Acceptance 1 says no *other* golden moves; one that does is a defect in this change. Widens `stock-deltas`' reconciliation walk to the **Located good** class (a one-line change in 0a.7's registry, named here so the gap cannot hide). Crosses Core + Data — full suite once at module end.

### [ ] 1.5 `warehouse-axis` — a third capacity axis for located goods
- **Spec:** docs/architecture/trade-network/sector-yield/spec-warehouse-axis.md
- **Wave:** row 1 · flag `trade.sectorYield` (registered by 1.4) · bump N+2 (the wave's)
- **Depends on:** 1.2, 0d.1, 0a.8 (the `trade` tuning file and loader); external `empire-seed` `band-reader` (I2) and `structure-bands` (I3), row 0b, plus the storage row of row 0c
- **Acceptance:** `SectorWarehouse` is the only reader of `WarehouseCapacityBonus`; the loam and item readers return the same value whether or not a structure carries a warehouse bonus, and `SectorWarehouse` returns the same value whatever `CapacityBonus`/`ItemStorageCapacityBonus` are (one test per direction) · a held sector with no warehouse-carrying active structure has exactly the scaled `warehouse.baseYard`, an unowned sector 0, development adds nothing without a storage building, each storage tier strictly raises capacity, and capacity never decreases when a structure is added, a tier rises or development rises · at the pin capacity equals the authored sum exactly and at every other band `LocatedScale.Apply(authored, Milli(sector))`; a missing `warehouse.*` key or a `warehouseBand` ordinal with no band row is a load rejection; `Occupancy` equals `LocatedStock.Total` plus every registered term.
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/SectorWarehouse.cs,gk-core/src/FusionRpg.Core/World/StructureCatalog.cs,src/FusionRpg.Core/World/Trade/TradeTuning.cs,data/tuning/trade.v2.json,scripts/guard-warehouse-single-reader.ps1,gk-core/scripts/enforcement-registry.v1.json,tests/FusionRpg.Core.Tests/World/SectorWarehouseTests.cs,gk-core/scripts/verification-boundaries.v1.json -Session <session-id>` then `python -m pytest gk-core/tools/tuning -q` and `python gk-core/scripts/audit-magic-numbers.py --summary`
- **Shared files:** none in §4 · `data/tuning/trade.v{n+1}.json` (publishes `warehouse.baseYard`, `capacityByTier`, `capacityByLevel`, `deliveryOverflowWasteMilli`) and `data/tuning/structure-seed.v{n+1}.json` (the `warehouseBand` table, published by `empire-seed` `structure-bands`)
- **Notes:** it **publishes v{n+1}**, it does not create the trade file — landing order §5 fixes the creator as 0a.8 (the spec's "whichever lands first creates it" is superseded). Its exact new tuning path is added to 0a.8's `core-trade-tuning` owner row in this change (`gk-core/data/tuning/**` is unmapped), and `gk-data/packs/fusion/data/seed/structures/**` is likewise unmapped — the regenerated corpus for the `warehouseBand` ordinal needs its own boundary (ask X-18). Lands the `warehouse-single-reader` guard + `tn-warehouse-single-reader` invariant. Blocked with the row on X-4 (the warehouse-capacity §10 row: faucet and sink must read one scale, PS-5). Corpus regeneration is `empire-seed`'s generator — never a hand edit.

### [ ] 1.6 `production-halt` — decision 22 wired: at capacity, production stops and nothing is wasted
- **Spec:** docs/architecture/trade-network/sector-yield/spec-production-halt.md
- **Wave:** row 1 · flag `trade.sectorYield` (registered by 1.4) · bump N+2 (the wave's)
- **Depends on:** 1.4, 1.5
- **Acceptance:** at capacity credited is 0 for every good with one halt fact per yielding good (and likewise for a capacity-0 sector); below capacity with `want <= room` every good is credited in full with no halt fact · with `want > room` credited sums to exactly `room`, each good gets its pro-rata floor share plus at most one remainder unit in ordinal id order, and the rest is **not produced** — no `*.overflow` line, no negative or waste delta; stock already above capacity is never reduced · **order-independent resume:** "halt then build capacity" and "build capacity then reach the old limit" both produce next turn (both tested); a halt leaves the next turn's yields, capacity and depletion exactly as they would be without it; two identical sectors owned by different faction kinds credit identically; `LoamPhasesTests` stay green with no expected value changed.
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Goods/LocatedProduction.cs,gk-core/src/FusionRpg.Core/World/StructurePolicy.cs,gk-core/scripts/enforcement-registry.v1.json,tests/FusionRpg.Core.Tests/World/Goods/LocatedProductionTests.cs -Session <session-id>`
- **Shared files:** none
- **Notes:** the **one credit function** for every located yield — `CreditMode.FullCredit` exists only for `income-parity` (10.1) and a source scan asserts no other caller passes it. Loam keeps its shipped clamp-and-overflow rule; rubble and ironwork stay uncapped. The one-credit-function rule owes an enforcement-registry row (guard or `unguardableReason`) in this change.

---

## Wave L6 — `legion-build` W6 (standards and doctrine, once goods are located)

Two capability rows, `legion.standards` and `legion.doctrine`, on one bump **`L6`**. Both spend located stock
inside `Step`, so the wave waits on row 1 (`located-stock`), row 0d (`sector-features`) and row 0c (the
`standard-hall` and Workshop rows). `legion-doctrine` is the third module of landing-order §3 edge 7 since
reconciliation **R-12**.

### [ ] L6.1 `legion-standards` — one standard per legion, forged at a Standard Hall
- **Spec:** docs/architecture/legion-build/spec-legion-standards.md
- **Wave:** L6 (after family row 1) · flag `legion.standards` (this task registers it) · rides bump `L6`
- **Depends on:** 0e.1, 0e.3, L2.3, row 1 (`located-stock`), row 0d (`sector-features`), row 0c (`trade-structure-rows`, the `standard-hall` row)
- **Acceptance:** (1) at most one standard per legion, carried by a row that meets `carrierRequirement` (otherwise a named refusal), forged by spending located stock through `LocatedStockOps.Add` **inside `Step`** — no Data-side gate and no Data-side spend, proven by a replay test and a source scan; (2) forging in a sector with no Standard Hall drops `standard.no-hall` and above the hall's tier drops `standard.tier-too-high`, both read through `SectorFeatures.TierOf` with no re-derived building ownership (round 6 L6, S1); (3) carrier loss, rout and disband each remove every standard contribution in the same commit, and no world without a standard changes hash.
- **Verify:** `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/World/WorldState.cs,src/FusionRpg.Core/World/Legion/LegionStandards.cs,gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs,gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs,gk-core/src/FusionRpg.Core/World/WorldCanonical.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs,data/tuning/legion.v5.json -Session <session-id>`
- **Shared files:** `WorldState.cs`; `WorldCanonical.cs` — a `standard` row only when present, after row 1's `located-stock` append; `WorldCommand.cs` — `forge-standard`, `assign-standard` with their admission arms; `RpgStore.World.cs` — the `standard_json` column. **Tuning:** `legion.v{n+1}` (`standards.forgeQtyPerTier`).
- **Notes:** the rung **count** is authored — three (Banner Yard → Standard Hall → Hall of Triumphs, owner 2026-09-20) — so only the multipliers wait: `legion-bands` publishes no tier multiplier and this module's containers carry tier 1 only until the `ssot-power-scale.md` §10.2 row lands (A-LB4). Validation asserts the seed contract, never how many standards exist.

### [ ] L6.2 `legion-doctrine` — one doctrine, one pricer term, a standing goods cost
- **Spec:** docs/architecture/legion-build/spec-legion-doctrine.md
- **Wave:** L6 (after family row 1) · flag `legion.doctrine` (this task registers it) · rides bump `L6`
- **Depends on:** L2.3, row 1 (`located-stock`) — the per-turn upkeep is paid from located stock inside `Step`
- **Acceptance:** (1) with no doctrine each of the four existing pricers returns exactly today's value, and a doctrine changes exactly **one** of them by one signed tuned term — never a second pricer; (2) holding a doctrine costs `doctrine.upkeepGoodsPerUnitPerTurn × Σ Count` every turn (a rate proportional to the army, never a cap), and when it cannot be paid the doctrine **lapses** with a `doctrine.lapsed` line and its 5c container withdrawn in the same commit — never a silent debt, never a clamp, never a free turn; (3) nothing reads the owner's faction kind: the same test runs twice, player-owned and AI-owned, with the same result.
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Legion/LegionDoctrine.cs,gk-core/src/FusionRpg.Core/World/Movement/LaneCost.cs,gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs,gk-core/src/FusionRpg.Core/World/Intel/Visibility.cs,gk-core/src/FusionRpg.Core/World/LegionCargo/ScopedInventoryPolicy.cs,gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs,gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs,gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs,data/tuning/legion.v6.json -Session <session-id>`
- **Shared files:** `WorldCommand.cs` — the adopt/switch kinds and their admission arms; `TurnEngine.cs` — where bump `L6` lands. **Tuning:** `legion.v{n+1}` (`doctrine.termMilli`, `doctrine.upkeepGoodsPerUnitPerTurn`, `doctrine.bankedDrawPremiumMilli`).
- **Notes:** the landing order's §3 edge 7 names only `legion-equipment` and `legion-standards` as `sector-yield`-dependent; round 6 CQ2's located-stock upkeep makes this module a third, and **§3 edge 7 now names it** (reconciliation R-12) — so this wave's dependency on row 1 is recorded in the family order, not only here. Its banked top-up half is L10.2. The four pricer terms are D2's stated default until `world-derived` registers the channels.

---

## Row 2 — `sector-yield` W2 (the structure loam term)

### [ ] 2.1 `structure-upkeep` — the missing structure term in `LoamUpkeep`
- **Spec:** docs/architecture/trade-network/sector-yield/spec-structure-upkeep.md
- **Wave:** row 2 · flag **`trade.structureUpkeep`** (this task registers it) · bump **N+3**
- **Depends on:** 0a.4, 0a.8 (the trade tuning file and loader), 0d.1 (`ActiveTier`)
- **Acceptance:** with every role's term at 0, upkeep is byte-identical to today on any stamp for every sector of every shipped template over a scripted run (`LoamUpkeepTests`, `WonderUpkeepTests`, `LoamUpkeepSeasonCallSiteTests` green with no expected value changed), and on a legacy stamp the term is 0 whatever the tuning says with `TradeTuning` never read on that path · on a `trade.structureUpkeep` stamp each active structure adds exactly its role's term to `Sum` **once**, `BreakdownFor(...).Total == LoamUpkeep.For(...)` still holds, a structure under construction adds nothing and starts paying the turn it becomes active · a tuning file missing any role is a load rejection naming the role; the W10 DTO carries the term and its value equals the breakdown's; `StructureDef.Role` equals the corpus row's role for every loaded row (per row, not by count).
- **Verify:** `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/World/Loam/LoamUpkeep.cs,gk-core/src/FusionRpg.Core/World/StructureCatalog.cs,gk-core/src/FusionRpg.Contracts/WorldDtos.cs,gk-core/src/FusionRpg.Server/WorldEndpoints.cs,data/tuning/trade.v3.json,tests/FusionRpg.Core.Tests/World/Loam/StructureUpkeepTests.cs,gk-core/scripts/verification-boundaries.v1.json -Session <session-id>` then `python gk-core/scripts/audit-magic-numbers.py --summary`
- **Shared files:** none in §4 · `data/tuning/trade.v{n+1}.json` (`upkeep.structureTermByRole`, every role keyed, no default)
- **Notes:** with its own flag and bump this wave's *"it can land first"* claim is true as written (audit SY-A1 / build-readiness) — it is independent of every goods module and needs only the stamp, the tuning file and `ActiveTier`. Golden re-bless owned here: the fixtures/Data tests that grant this flag at the live ruleset; **no legacy golden may move**. It **publishes** the trade tuning file at v{n+1} and adds its exact path to 0a.8's `core-trade-tuning` row (landing order §5). Loam stays Θ-invariant — the term is flat, never scaled.

---

## Row 3 — `sector-yield` W3 (structures yield goods)

### [ ] 3.1 `yield-structures` — held ground pays located goods
- **Spec:** docs/architecture/trade-network/sector-yield/spec-yield-structures.md
- **Wave:** row 3 · flag **`trade.yieldStructures`** (this task registers it) · bump **N+4**
- **Depends on:** 1.6, 1.2, 1.5, 2.1 (P2 — a yield building never ships without its loam upkeep term), 0a.4, 0a.7, 0a.8; external `empire-seed` `band-reader`, `structure-bands`, `trade-structure-rows` (the generator emits `locatedYields`)
- **Acceptance:** on a `trade.yieldStructures` stamp a sector with one active yield structure gains exactly its scaled yield each turn — or less at capacity, then a halt fact — and the gain appears as a stock delta with factKind `produce`; a soul conduit yields souls and adds no loam from its flat field, while a structure with no located yields keeps its flat loam add · on a legacy stamp the same world's state hash matches today turn for turn and a conduit's sector gains exactly its `FlatYieldPerTurn` · a structure under first construction or on an unowned sector yields nothing and one mid-upgrade yields exactly what it did before the upgrade; two identical sectors owned by different faction kinds end with identical stock; every `good` in every `LocatedYields` resolves in `LocatedGoodCatalog`, is not a `LegionPiece` and is not Content-pending, a violating row being a load rejection asserted per row over the real corpus, never by count.
- **Verify:** `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/World/StructureCatalog.cs,src/FusionRpg.Core/World/Goods/LocatedYieldPhase.cs,gk-core/src/FusionRpg.Core/World/Loam/LoamProduction.cs,gk-core/src/FusionRpg.Core/World/Loam/LoamPhases.cs,gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs,tests/FusionRpg.Core.Tests/World/Goods/LocatedYieldPhaseTests.cs,gk-core/tests/FusionRpg.Core.Tests/World/TurnEngineTests.cs,gk-core/scripts/verification-boundaries.v1.json -Session <session-id>` then `python -m pytest gk-forge/tools/seedsmith/tests/test_structure_corpus.py -q`
- **Shared files:** TurnEngine.cs (one stamp-gated call inside `Production`, after `SiegeConstruction.AdvanceDepletion` — a step, not a new phase) · `data/tuning/structure-seed.v{n+1}.json` (the `yieldBand` table, published by `empire-seed`) · `gk-data/packs/fusion/data/seed/structures/**` regenerated
- **Notes:** golden re-bless owned here: this wave's flag-granting fixtures, and the regenerated structure corpus with its `--check` gate (landing order §6) — regenerated by `empire-seed`'s generator in this wave, **never hand-edited**. `gk-data/packs/fusion/data/seed/structures/**` has **no** owner mapping today (verified) — adding it is part of this task (ask X-18). Removing `FlatYieldPerTurn` from the conduit's row would move every legacy world: the field stays and the stamp decides which reward pays.

---

## Row 4 — `sector-yield` W4 (`banking-fact` part 1: the `Logistics` phase slot)

### [ ] 4.1 `banking-fact` (slot half) — create the `Logistics` phase with an empty L3
- **Spec:** docs/architecture/trade-network/sector-yield/spec-banking-fact.md §1, §1a (the **Slot** row of its two-wave table)
- **Wave:** row 4 · flag **`trade.bankingPhase`** (this task registers it) · bump **N+5**
- **Depends on:** 0a.4 (the stamp and the capability registry); nothing from the ledgers — that is the point of the split
- **Acceptance:** on a legacy stamp the `Logistics` phase does not begin, `report.Phases` equals today's ten, and the state hash matches today turn for turn · on a `trade.bankingPhase` stamp the report's phases are the eleven with `Logistics` between `Production` and `Growth` (a new test beside `TurnEngineTests.cs:107`) · `trade.bankingPhase`'s `IntroducedAtRuleset` is the value this change bumps `TurnEngine.RulesetVersion` to, so a world stamped at the previous ruleset is not granted it (both directions, `spec-world-stamp.md` acceptance 11); a world granted `trade.bankingPhase` but not `trade.banking` runs the phase with an empty L3 and banks nothing.
- **Verify:** `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs,docs/architecture/decisions.md,gk-core/tests/FusionRpg.Core.Tests/World/TurnEngineTests.cs -Session <session-id>`
- **Shared files:** TurnEngine.cs (the phase slot is created **once, here** — CM4; `logistics-flow` `logistics-phase` extends it at row 5) · `docs/architecture/decisions.md:7` (the phase-order row is amended in this change to eleven phases with `Logistics` stamp-gated)
- **Notes:** this half is deliberately split from row 8 (round 6 C1 + C3) so that `logistics-flow` rows 5–7 are **not** behind the save-identity re-key; CM4 is unchanged and no other module may create the slot. `decisions.md:7` also cites a stale `TurnEngine.cs:180-195` for the phase list (calls are at `:191-207`) — re-point it in this same change. Owner confirms nothing here; the split is a wave split inside one owner.

---

## CHECKPOINT 1 — The sector economy

**Rows 1–4.**

**Pass condition, from the plan §3:** a held sector accumulates located goods, production halts at warehouse
capacity instead of wasting, structures pay a loam term and yield goods, and the `Logistics` phase exists
with its L3 slot empty. `bank-points` answers which sectors are bank points, so *build a Counting House* is a
buildable answer. Four flags, four bumps, in order.

---

## PHASE 2 — The lane layer

Landing-order rows **5–7** and **9**. 12 tasks.

**Row 9 is presented before row 8**, which §2's numeric order does not do. That is not a re-ordering: §7's
interim behaviour already requires it — rows 1–7 and 9 land normally while row 8 waits on the save-identity
re-key, and the plan's §3 puts row 9 in this phase and row 8 in the next.

---

## Row 5 — `logistics-flow` W1 (the phase steps)

### [ ] 5.1 `logistics-phase` — the step order and the `trade.logistics` gate
- **Spec:** docs/architecture/trade-network/logistics-flow/spec-logistics-phase.md
- **Wave:** row 5 · flag `trade.logistics` (registered here) · bump N+6 (shared with 5.2)
- **Depends on:** row 4 (`banking-fact`, slot half — it creates the `Logistics` phase), row 0a (`world-stamp`, `stock-deltas`)
- **Acceptance:** a world without the flag hashes identically turn for turn, L3 behaving as `banking-fact` alone (1) · with the flag, L0–L8 run in the stated order and the order itself is asserted (2) · legacy-, sector-yield- and logistics-stamped worlds coexist in one store and replay independent of creation order (5)
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Logistics/LogisticsSteps.cs,src/FusionRpg.Core/World/Logistics/LogisticsRuntime.cs,gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs,tests/FusionRpg.Core.Tests/World/Logistics/LogisticsPhaseTests.cs,gk-core/scripts/verification-boundaries.v1.json -Session <session-id>`
- **Shared files:** `TurnEngine.cs` — takes row 5's single bump and adds the flow-step calls inside the phase method row 4 created (§4: one wave at a time, rebase onto the latest constant); `RpgStore.WorldTurns.cs` — the commit path passes the per-world runtime, after 0a/0f's ledger tables
- **Notes:** owns row 5's re-bless of fixtures built at the live ruleset and then granted a flag (§6); new logistics-stamped fixtures are new files. `src/FusionRpg.Core/World/Logistics/**` resolves only to `core-fallback` (module level, no `verificationId`) — this task adds a `core-world-logistics` owner boundary, the sibling of the Fleet one `carried-goods` adds (ask X-18).

### [ ] 5.2 `logistics-canonical` — hashed, sparse state for the flow layer
- **Spec:** docs/architecture/trade-network/logistics-flow/spec-logistics-canonical.md
- **Wave:** row 5 · flag `trade.logistics` (registers no row of its own) · bump N+6 (shared with 5.1)
- **Depends on:** 5.1, row 1 (`located-stock` — it holds the canonical append slot before this one)
- **Acceptance:** a world with no packets and no policies writes byte-identical canonical text to today's, and canonical length is invariant under goods that are zero everywhere (1, 2) · save → load → hash round-trips byte-identically with packets and policies present (3) · a turn that changes one route writes exactly that route's packed row and no other (4)
- **Verify:** `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/World/WorldState.cs,gk-core/src/FusionRpg.Core/World/WorldCanonical.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldGraphDiff.cs,tests/FusionRpg.Core.Tests/World/Logistics/LogisticsCanonicalTests.cs -Session <session-id>`
- **Shared files:** `WorldCanonical.cs` — **slot 3** after the `sector-ironwork` loop (§4: `world-stamp`'s stamp row, `located-stock`, this module, then `carried-goods`), stated in the spec as "after the last conditional row present at landing"; `WorldState.cs` — the row 5 field additions (`Transit`, `RoutePolicies`); `RpgStore.World.cs` / `RpgStore.WorldGraphDiff.cs` — two new tables, no migration of an existing one
- **Notes:** owns the `WorldCanonical` append-order golden movement for row 5 (§6); the second module to land at that slot rebases onto this one.

---

## Row 6 — `logistics-flow` W2 (lanes)

### [ ] 6.1 `path-cache` — cached supply-lens paths on an exact topology key
- **Spec:** docs/architecture/trade-network/logistics-flow/spec-path-cache.md
- **Wave:** row 6 · wave flag `trade.logisticsLanes` (this module registers none — it is a memo and changes no output) · bump N+7 (shared across row 6)
- **Depends on:** 5.2, row 1 (`bank-points`, trigger T7); optional and absent-by-default: row 16 (`diplomatic-stance`, T9) and row 18 (`trade-access`, T10)
- **Acceptance:** cached trees equal a fresh computation on every turn of a scripted and a seeded run (1) · every trigger T1–T12 has its own test, and the six key-set triggers assert the new key's answer at the first L0 after the change (2) · a turn with no key change performs zero rebuilds, and each memo edge E1–E4 ends equal to a fresh computation (3, 6)
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Logistics/PathCache.cs,src/FusionRpg.Core/World/Logistics/TopologyKey.cs,gk-core/src/FusionRpg.Core/World/Topology/LaneGraph.cs,tests/FusionRpg.Core.Tests/World/Logistics/PathCacheTests.cs,tests/FusionRpg.Core.Tests/World/Logistics/PathCacheTriggerTests.cs -Session <session-id>`
- **Shared files:** none from §4. `LaneGraph.cs` changes one accessor from private to internal — it is not a §4 shared file, but it is world-map's tree, so keep the edit to that one line.
- **Notes:** exposes `PathCache.Next(faction, destinationKey, sector)`, the single traversal predicate `fleet` `trade-route-order` (13.2) reads for its need rule (ask A9). The spec replaces the map's hashed graph-version counter with an unhashed exact topology key and twelve triggers; `logistics-flow-map.md:128` and its counter/fingerprint paragraph were **corrected** in the reconciliation (R-19.1), so map and spec now agree and this task follows the spec without a deviation to record.

### [ ] 6.2 `lane-flow` — `Width` as throughput, with pro-rata contention
- **Spec:** docs/architecture/trade-network/logistics-flow/spec-lane-flow.md
- **Wave:** row 6 · flag `trade.logisticsLanes` · bump N+7 (shared across row 6)
- **Depends on:** 6.1, row 1 (`located-stock`, `warehouse-axis`, `essence-loop-read` — the PS-5 scale read), row 0a (`synthetic-graph`)
- **Acceptance:** conservation holds per good, per route, per turn, and no lane's committed departures exceed its capacity (1, 2) · contested capacity splits pro rata by demand across commanders within integer rounding, remainders rotated by turn, never by faction id (3) · scaling goods and the scale read together leaves every lane's movable fraction unchanged (4)
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Logistics/LaneFlow.cs,gk-core/src/FusionRpg.Core/World/WorldState.cs,src/FusionRpg.Core/World/Trade/TradeTuning.cs,data/tuning/trade.v2.json,docs/architecture/power/ssot-power-scale.md,tests/FusionRpg.Core.Tests/World/Logistics/LaneFlowTests.cs -Session <session-id>` (the published version number is whatever `publish.py` emits)
- **Shared files:** `WorldState.cs` — a doc-comment change only (`Width` means throughput, map C3); no new hashed field, so no `WorldCanonical` slot
- **Notes:** blocked by ask X-4 — the power-ladder §10 consumer row for lane throughput must exist, because PS-5 requires faucet and sink to read the same scale (§7); the row lands in this change. Publishes `lane.throughputPerWidth` as `trade.v{n+1}` (row 0a `economy-report` created the file, §5). `data/tuning/trade.v*.json` has no owner verification boundary — adding one is part of this task (ask X-18).

### [ ] 6.3 `transit-buffer` — transit time, stranding and delivery overflow
- **Spec:** docs/architecture/trade-network/logistics-flow/spec-transit-buffer.md
- **Wave:** row 6 · flag `trade.logisticsLanes` · bump N+7 (shared across row 6)
- **Depends on:** 6.2, 6.1, row 0a (`ledger-keys`, `stock-deltas`), row 1 (`warehouse-axis` owns `warehouse.deliveryOverflowWasteMilli`)
- **Acceptance:** absent a cut, goods sent on turn *t* with transit *k* are delivered on turn *t + k* exactly, and per-route conservation closes every turn over departed, arrived, lost, returned and wasted (1, 2) · a cut strands, a restore resumes from the slot, a clear returns, and a cut plus a same-turn `route-clear` resolve identically in either filing order (4, 5) · only deliveries waste, and only what is still `AtDoor` after L4 has unloaded into the room L3 freed (6)
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Logistics/TransitBuffer.cs,src/FusionRpg.Core/World/Ledger/LedgerKey.cs,tests/FusionRpg.Core.Tests/World/Logistics/TransitBufferTests.cs -Session <session-id>` (add each `StockDelta*.cs` file the `Route` holder touches)
- **Shared files:** the ledger holder grammar (`LedgerKey.cs`, `StockDelta*.cs`) is row 0a's — extend it with the `r:` route holder and the depart/deliver/waste/return kinds, never fork it
- **Notes:** acceptance 6 is the audit's 2026-09-20 correction; the pre-round-4 wording ("only at a non-bank destination") is void. No criterion asserts a banked total — nothing banks until row 8.

### [ ] 6.4 `lane-loss` — the deterministic bounded-ratio sink (loss layer, v1 stance count)
- **Spec:** docs/architecture/trade-network/logistics-flow/spec-lane-loss.md (§1–§3; §4's switch is task 23.1)
- **Wave:** row 6 · flag `trade.logisticsLanes` · bump N+7 (shared across row 6)
- **Depends on:** 6.2, 6.3
- **Acceptance:** loss ∈ `[0, goods]` for every input over a property sweep, the clamp a commented bounded ratio, and lost goods vanish — no stock anywhere increases because of loss (1, 2) · wards and own escorts never increase loss, hostile forces never decrease it, and the same inputs give the same loss with no RNG consumed (3, 4) · a missing stance or good row is a load rejection naming it, while adding a legion piece to the injected catalog needs no tuning change (5)
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Logistics/LaneLoss.cs,data/tuning/trade.v3.json,tests/FusionRpg.Core.Tests/World/Logistics/LaneLossTests.cs -Session <session-id>`
- **Shared files:** none from §4
- **Notes:** v1 reads no actor number (acceptance 6): escort strength is the tuned count of escort-stance legions, and `world.hazard.resist` defaults to 0 until `world-derived` exists — both switch at row 23, not here. Owns the `lane.stanceEscortMilli.{stance}` key family; the `escort` row publishes in the change that adds the stance to `MovementPolicy.Stances` (`legion-build` `escort-stance`), because the join rejects a stance with no row.

### [ ] 6.5 `logistics-facts` — the closed report vocabulary, from the first turn
- **Spec:** docs/architecture/trade-network/logistics-flow/spec-logistics-facts.md
- **Wave:** row 6 · flag `trade.logisticsLanes` · bump N+7 (shared across row 6)
- **Depends on:** 6.2, 6.3, 6.4
- **Acceptance:** every non-zero loss has exactly one `logistics.loss` entry with one cause, and Σ reported = Σ applied (1) · a cut produces `lane.cut` the turn it strands goods and never on a turn with no new strand (2) · every entry carries its faction as `Audience`, and a faction's projection never contains another faction's logistics entry (3)
- **Verify:** `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs,src/FusionRpg.Core/World/Logistics/LogisticsFacts.cs,tests/FusionRpg.Core.Tests/World/Logistics/LogisticsFactsTests.cs -Session <session-id>`
- **Shared files:** `TurnReport.cs` gains six kind constants — not a §4 file, but the report kinds are a closed vocabulary shared with `sector-yield`'s banking and halt entries; add, never duplicate theirs
- **Notes:** the kinds and each token set are pinned as closed vocabularies with a stated reason; no test counts entries (repo hard rule). No per-lane utilisation entry — the spec's stated deviation from the map.

---

## Row 7 — `logistics-flow` W3 (policy and building)

### [ ] 7.1 `auto-banking` — the default destination and the three policy commands
- **Spec:** docs/architecture/trade-network/logistics-flow/spec-auto-banking.md
- **Wave:** row 7 · flag `trade.logisticsPolicy` (registered here) · bump N+8 (shared with 7.2, 7.3)
- **Depends on:** 6.1, 6.2, 6.3, row 1 (`bank-points`), row 4 (`banking-fact`, slot half), row 0d (`sector-features`, for the `bank-hold` tier read)
- **Acceptance:** with no policy, located goods flow to the nearest reachable own bank point, ties by sector id (1) · `route-set` changes only its `(sector, good)` flow and `route-clear` restores the default exactly, while loam and recruits can never be routed and world stocks route but never bank (3, 4) · a policy whose source sector its commander no longer holds is dormant rather than deleted, in either filing order, and a retake revives it (8)
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Logistics/AutoBanking.cs,gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs,gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs,gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs,gk-core/src/FusionRpg.Contracts/WorldDtos.cs,gk-core/src/FusionRpg.Server/WorldEndpoints.cs,tests/FusionRpg.Core.Tests/World/Logistics/AutoBankingTests.cs -Session <session-id>`
- **Shared files:** `WorldCommand.cs` — the row 7 player-verb slot: `route-set`, `route-clear`, `bank-hold` land here, `WorldCommandAdmission` gaining one arm per kind in the same change (§4); `TurnEngine.cs` — one resolver call in `Snapshot`, under row 7's single bump; `RpgStore.WorldTurns.cs` — additive `CommandPayload` fields
- **Notes:** the row 8 blocker (save-identity re-key, X-1) does **not** reach this task and no criterion asserts a banked total: goods flow to the nearest bank point and wait there, the hold state is stored and the hold-source seam registers, and the first good leaves the map at row 8 (§7 interim behaviour). Acceptance 2 ("delivered on *t* banks on *t*") is only exercisable once row 8 lands: it is a row-8 obligation sitting in a row-7 spec, and this task's own Hard edges already say no criterion here asserts a banked total. Do not tick it in this task's change.

### [ ] 7.2 `construction-chain` — the refine step and world stocks on the lanes
- **Spec:** docs/architecture/trade-network/logistics-flow/spec-construction-chain.md
- **Wave:** row 7 · flag `trade.logisticsPolicy` · bump N+8 (shared with 7.1, 7.3)
- **Depends on:** 6.2, 7.1 (the `route-set` policy), rows 0b/0c (`empire-seed` refinery magnitudes — until then the step is tested on fixture structures)
- **Acceptance:** refining spends rubble and produces exactly `Refine(spent, yieldMilli)` ironwork, both recorded as `refine` stock deltas that reconcile every turn, with a first-construction refinery refining nothing (1) · refine per turn ≤ rate × working refineries, the rate a commented structural limit (2) · no code path turns rubble, ironwork, loam or recruits into a banking fact, material or wallet credit — source scan plus a property test over random routes (3)
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Logistics/ConstructionFlow.cs,gk-core/src/FusionRpg.Core/World/Siege/SiegeConstruction.cs,gk-core/src/FusionRpg.Core/Battle/Board/SiegeTuning.cs,gk-core/data/tuning/siege.v2.json,tests/FusionRpg.Core.Tests/World/Logistics/ConstructionFlowTests.cs,tests/FusionRpg.Guard.Tests/WorldStockNeverBanksGuardTests.cs,gk-core/scripts/verification-boundaries.v1.json -Session <session-id>`
- **Shared files:** none from §4; `SiegeConstruction.cs` gains a caller and a corrected comment, no logic change
- **Notes:** publishes the refine rate into `siege.v{n+1}` (the siege domain's file, read not owned here) and must add the `siege-tuning` owner boundary in the same commit — `data/tuning/siege.v*.json` resolves to no owner today and `verify-change.ps1:118` throws `VERIFICATION BOUNDARY MISSING` (ask X-18). `refineRubblePerIronwork` has no reader anywhere; reported to the siege domain, not read here.

### [ ] 7.3 `lane-verbs` — `widen` and `ward` on a rising, uncapped ladder
- **Spec:** docs/architecture/trade-network/logistics-flow/spec-lane-verbs.md
- **Wave:** row 7 · flag `trade.logisticsPolicy` · bump N+8 (shared with 7.1, 7.2)
- **Depends on:** 6.2, 6.4, 7.2 (the verbs are paid in refined construction stocks)
- **Acceptance:** a short verb is refused with a reason and spends nothing, an accepted one spends exactly the curve's price (1) · each level costs strictly more than the last, no level is refused for being high, and integer arithmetic is `checked` and throws rather than wraps (2) · `WardLevel` stays one field read by the siege approach path and by `lane-loss`, a guard failing on a second field or reader (3)
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Logistics/LaneVerbResolver.cs,gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs,gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs,gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs,gk-core/src/FusionRpg.Contracts/WorldDtos.cs,gk-core/src/FusionRpg.Server/WorldEndpoints.cs,data/tuning/trade.v4.json,docs/architecture/power/ssot-power-scale.md,tests/FusionRpg.Core.Tests/World/Logistics/LaneVerbTests.cs,tests/FusionRpg.Guard.Tests/LaneFieldReadersGuardTests.cs -Session <session-id>`
- **Shared files:** `WorldCommand.cs` — `widen` and `ward` join the same row 7 slot, sequenced after 7.1's three kinds so one wave appends at a time (§4); `TurnEngine.cs` — one resolver call in `Snapshot`, under row 7's bump already taken by 7.1
- **Notes:** the `ssot-power-scale.md` §10 row for the cost ladder lands in this change. `ward` changes siege geometry only on lanes where someone files it; verify the zone geometry at high levels rather than assuming it (acceptance 6 refuses an unrepresentable level instead of throwing at End Turn).

---

## Row 9 — `logistics-flow` W4 (read model and gate)

Whole row: **no flag, no bump** (R3) — *"the forecast writes nothing"* and the bench is a test. That is legal
even though `forecast-facts` runs the whole `Step` including flagged steps, because it writes nothing and the
committed hash is unchanged.

### [ ] 9.1 `forecast-facts` — the side-effect-free dry run and its answer table
- **Spec:** docs/architecture/trade-network/logistics-flow/spec-forecast-facts.md
- **Wave:** row 9 · no flag, no bump (R3: *"the forecast writes nothing"* — it grants no capability)
- **Depends on:** 6.5, 7.1, 7.2, row 1 (`production-halt`), row 0d (`sector-features`, for the `build` answer)
- **Acceptance:** committing the next turn with no new orders produces exactly the halts, strands, losses, shorts and waste the forecast named and nothing it did not, and the committed hash is unchanged by a forecast (1, 2) · the forecast and the phase share every rule, so a tuning change moves both identically (3) · every fact carries answers from the closed table, each a real command kind and, for `build`, a real `SectorFeature` (4)
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Logistics/LogisticsForecast.cs,tests/FusionRpg.Core.Tests/World/Logistics/LogisticsForecastTests.cs -Session <session-id>`
- **Shared files:** none
- **Notes:** the spec runs the whole `Step`, not a partial phase — its stated deviation from the map, and what makes faithfulness hold by construction. Acceptance 5 (a source with no reachable bank point forecasts `no-path` with *build a Counting House* first) is the round 4 Q3 first-throttle answer, and it is answerable in the row-8 interim.

### [ ] 9.2 `logistics-bench` — the performance gate
- **Spec:** docs/architecture/trade-network/logistics-flow/spec-logistics-bench.md
- **Wave:** row 9 · no flag, no bump (R3: test-only — no behaviour, no capability)
- **Depends on:** 5.1, 5.2, 6.1–6.5, 7.1, 7.2, 7.3, 9.1; row 0a (`step-benchmark`, `synthetic-graph`)
- **Acceptance:** after warm-up the Logistics kernel on the giant synthetic graph allocates 0 bytes, asserted in CI (1) · ×1000 volume changes neither allocation nor iteration counts, asserted in CI (2) · a turn with no topology change performs zero path rebuilds, asserted in CI (3)
- **Verify:** `.\scripts\verify-change.ps1 -Paths tests/FusionRpg.Core.Tests/World/Logistics/LogisticsAllocationTests.cs,tests/FusionRpg.Bench/LogisticsBench.cs,gk-core/tests/FusionRpg.Bench/Program.cs,docs/research/perf/03-logistics-flow.md,gk-core/scripts/verification-boundaries.v1.json -Session <session-id>`
- **Shared files:** none
- **Notes:** `gk-core/tests/FusionRpg.Bench/**` resolves to no owner boundary — `verify-change.ps1:118` throws `VERIFICATION BOUNDARY MISSING` for `gk-core/tests/FusionRpg.Bench/AtomFormBench.cs` today (the spec ran it), so this task adds the mapping (ask X-18). Timings live in the bench and are never asserted in CI; never bump a §9.3 target to pass. `logistics-flow` is not done until this gate is green.

---

## CHECKPOINT 2 — The lane layer

**Rows 5–7 and 9.**

**Pass condition, from the plan §3:** goods move along lanes toward the nearest bank point and wait there.
`route-set`, `route-clear` and `bank-hold` work; `widen` and `ward` work. The forecast reads and writes
nothing. The step benchmark is inside budget at the synthetic graph's largest size. **This is the interim
playable state** — a full warehouse economy with no outflow.

---

## PHASE 3 — Outflow

Landing-order row **8**, plus legion wave **L10**, which lands after it. 3 tasks. **This is the phase behind
the family's one gate** (X-1, the save-identity re-key; round 6 C3 = *wait*).

---

## Row 8 — `sector-yield` W5 (`banking-fact` part 2: goods leave the map)

### [ ] 8.1 `banking-fact` (step half) — the L3 banking step, the rate, the hold, the fact, the credit
- **Spec:** docs/architecture/trade-network/sector-yield/spec-banking-fact.md §2–§6 (the **Step** row of its §1a table)
- **Wave:** row 8 · flag **`trade.banking`** (this task registers it) · bump **N+9** — after save identity (§7)
- **Depends on:** 4.1, 1.3, 1.4, 1.2, 0a.3, 0a.7, 0a.9, 0g.1, 0d.1
- **Acceptance:** reconciliation — for every good and turn, Σ warehouse decrements with factKind `bank` = Σ wallet credits + Σ destination credits; committing the same turn twice credits the wallet once (souls and materials); the report replay path leaves every ledger unchanged · no banking fact names `loam`, `rubble`, `ironwork`, `recruit` or a legion piece; a bank point banks at most its tier's scaled rate per turn, raising the tier never lowers what banks, and the split sums to exactly `min(rate, Σ bankable)` with the remainder by ordinal id; at tier ≥ 2 banking never takes a good below its hold, at tier 1 holds do not apply, and a world with no holds hashes as today · **order-independent:** capture in the same turn as banking resolves identically in either filing order, a hold captured in the same turn it was filed is inert either way (with the captor's own `bank-hold` replacing it and the setter's retake reviving it), and registering the destinations in either order lands every fact in the same place while two destinations accepting one faction kind fail at startup.
- **Verify:** `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs,src/FusionRpg.Core/World/Goods/BankingStep.cs,src/FusionRpg.Core/World/Goods/BankingHolds.cs,gk-core/src/FusionRpg.Core/World/WorldState.cs,gk-core/src/FusionRpg.Core/World/WorldCanonical.cs,src/FusionRpg.Core/World/Ledger/FactKinds.cs,gk-core/src/FusionRpg.Core/Creatures/SoulEarnPolicy.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldGraphDiff.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs,data/tuning/trade.v4.json,tests/FusionRpg.Core.Tests/World/Goods/BankingStepTests.cs,tests/FusionRpg.Data.Tests/World/BankingCommitTests.cs -Session <session-id>` then `.\scripts\guard-dal.ps1`
- **Shared files:** WorldState.cs (`WorldSector.BankHolds`) · WorldCanonical.cs (a conditional `sector-bank-hold` row, appended **after the last conditional row present at landing** — now named in §4's sparse-row clause, R-11; sparse, so it moves no existing hash and owes no re-bless) · RpgStore.WorldTurns.cs (commit-time wallet credit, after the diff, before the log insert) · `data/tuning/trade.v{n+1}.json` (`banking.ratePerTurnByTier`) · `SoulEarnPolicy.Reasons` gains `world-bank` (the creature program's closed vocabulary, with its agreement)
- **Notes:** **blocker X-1, round 6 C3 = wait** — it lands after 0g.1, which lands after `save-identity` SE4.12 → SE4.38; option (b) is refused. Interim until then (landing order §7): rows 1–7 and 9 run, goods reach a bank point and **stay there**, nothing leaves the map, no wallet or treasury is credited, and `economy-report` prints a banked total of **zero with that reason** — the family is not shippable before this row lands. Golden re-bless owned here: this wave's flag-granting fixtures; goldens triaged under `decisions.md` *Golden ordering across streams*, never re-blessed to pass. Crosses Core + Data and moves nothing in the phase list (4.1 did) — full suite once at module end, immediately before any live probe.

---

## Wave L10 — `legion-build` W10 (the banked top-up arms)

One capability row, `legion.bankedDraw`, on one bump **`L10`**. Both specs say their top-up arm lands in the
**same** change, so the two tasks below may be one commit; they are listed separately because each is a
different spec's second landing. Neither may land an interim second writer — round 6 C3 is *wait*.

### [ ] L10.1 `legion-equipment` (banked-draw half) — a short warehouse draws banked goods
- **Spec:** docs/architecture/legion-build/spec-legion-equipment.md §7a
- **Wave:** L10 (after family row 8) · flag `legion.bankedDraw` (this task registers it) · bump `L10`, the wave's one
- **Depends on:** L7.1, row 0g (`material-ledger`), row 8 (`banking-fact`, the step half), cross-program blocker **X-1** (the save-identity re-key; round 6 C3 is *"wait"*)
- **Acceptance:** (1) a `produce-gear` or casualty replacement short of a recipe good takes what the warehouse holds, then draws the shortfall from the owner's banked store through `material-ledger` **and nothing else** — no second writer, never `rpg_item_stock`; (2) the behaviour is identical for a player-owned and an AI-owned sector (the same test run twice, only the owner changed); (3) with both short, nothing is written and the order drops `gear.inputs-short`.
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Legion/LegionGearProduction.cs,src/FusionRpg.Core/World/Legion/LegionGear.cs -Session <session-id>`
- **Shared files:** `TurnEngine.cs` — where bump `L10` lands; no ledger table of its own (it writes through `material-ledger`'s `ledger-keys` fact kind).
- **Notes:** round 6 C3 forbids an interim second writer, so nothing of this arm may land early "until the ledger is ready" — that is the defect the single-writer rule exists for. Closes `counterparties` CQ2's scoped assertion.

### [ ] L10.2 `legion-doctrine` (banked-draw half) — the upkeep tops up from banked goods
- **Spec:** docs/architecture/legion-build/spec-legion-doctrine.md §3a
- **Wave:** L10 (after family row 8) · rides `legion.bankedDraw` · rides bump `L10`
- **Depends on:** L6.2, L10.1 (the specs say one change), row 0g (`material-ledger`), row 8, blocker **X-1**
- **Acceptance:** (1) an upkeep shortfall is topped up from the owner's banked store of that good through `material-ledger` only; (2) player-owned and AI-owned legions behave identically, with nothing in the rule reading the owner's faction kind; (3) when neither located stock nor banked goods can pay, the doctrine still **lapses** with its report line — the top-up adds a source to a sink, never a faucet and never a clamp.
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Legion/LegionDoctrine.cs,gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs -Session <session-id>`
- **Shared files:** none beyond L10.1's `TurnEngine.cs` bump.
- **Notes:** `doctrine.bankedDrawPremiumMilli` already exists from L6.2's publish (default 1000‰ = no premium, a bounded ratio divided last), so this arm publishes no new key.

---

## CHECKPOINT 3 — Outflow

**Row 8.**

**Pass condition, from the plan §3:** the first good leaves the map. A banking fact is written, the wallet is
credited at commit time, and the report's banked total is non-zero. `material-ledger` landed first, against
the re-keyed store, and the four writer sites were written **once**.

---

## PHASE 4 — Located income and fleet

Landing-order rows **10–14**, plus legion wave **L7**, which lands after rows 1 and 11. 10 tasks.

---

## Row 10 — `sector-yield` W6 (located income)

### [ ] 10.1 `income-parity` — income earned somewhere on the map stays on the map
- **Spec:** docs/architecture/trade-network/sector-yield/spec-income-parity.md
- **Wave:** row 10 · flag **`trade.incomeParity`** (this task registers it) · bump **N+10** — its `IntroducedAtRuleset` is not below `trade.logistics`' (row 5) and the landing order also puts it after `trade.banking` (row 8), the stronger constraint
- **Depends on:** 1.4, 1.6 (`FullCredit`), 1.5, 1.1, 0a.4, 0a.3, 0a.7, 0a.8, 8.1 (ordering, not code), row 5 (`logistics-flow` `logistics-phase`, ordering only)
- **Acceptance:** on a stamp without the flag every loot credit is byte-identical to today (wallet materials and soul rows unchanged, no `located_income` row written), and an expedition, web-wave or Sanctum-delve manifest credits the wallet as today on **any** stamp · on a flagged map world a located manifest's material and soul grants write `located_income` rows and credit no wallet row while its items mint as today; re-persisting the same manifest writes nothing new, re-committing the same turn credits nothing twice (`UNIQUE` + `applied_turn`), and replay re-derives the same `Step` output from the logged input and writes nothing · a sector at capacity still gains the whole income quantity and its next production halts; Σ `income` stock deltas = Σ applied `located_income` rows per good and turn; every `DropTableValidator.KnownSourceKinds` member is classified in `LocatedIncomeSources` (a join test, not a count), and identical incomes to identical sectors owned by different faction kinds produce identical stock.
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Goods/LocatedIncome.cs,gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs,src/FusionRpg.Core/World/Ledger/FactKinds.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Loot.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs,scripts/ledger-writers.v1.json,gk-core/scripts/enforcement-registry.v1.json,tests/FusionRpg.Core.Tests/World/Goods/LocatedIncomeTests.cs,tests/FusionRpg.Data.Tests/World/LocatedIncomePersistenceTests.cs -Session <session-id>` then `.\scripts\guard-dal.ps1` and `python gk-core/scripts/guard-test-substrate.py`
- **Shared files:** TurnEngine.cs (the optional logged income input + one call in `Production`) · RpgStore.WorldTurns.cs (read, log, stamp applied rows) · `rpg_located_income` is new, born Tier A, with a `ledger-writers.v1.json` row naming its **two** writers and `RpgStore.cs` reset-only
- **Notes:** ask **IP1** to party-dungeon — record the map door's **sector id** beside `DelveStart.ParentWorldId`; until then delve rewards bank as today, a declared gap. Ask **IP2** to `drop-tables`: claim and siege loot are inert (unpassed `PowerTuning`) and flow through this divert unchanged when woken. Still owes a guard or `unguardableReason` row for *"no located reward credits the wallet on a flagged world"* (acceptance 2 is its test). Crosses Core + Data — full suite once at module end.

---

## Row 11 — `sector-yield` W7 (legion equipment as a located good)

### [ ] 11.1 `legion-equipment-stock` — a piece is something a warehouse can hold
- **Spec:** docs/architecture/trade-network/sector-yield/spec-legion-equipment-stock.md
- **Wave:** row 11 · flag **`trade.legionEquipStock`** (this task registers it) · bump **N+11**
- **Depends on:** 1.4, 1.6, 1.5, 0a.4; external `legion-build` (the piece-catalog ids it injects)
- **Acceptance:** a piece id outside `legion-build`'s injected catalog is refused by `LocatedStockOps.Add` and by `LocatedStock.Unpack`, and piece ids are disjoint from material and `souls` ids — an injected collision is a load rejection · pieces count toward `LocatedStock.Total` and `SectorWarehouse.Occupancy`: a warehouse full of pieces halts every yield in that sector and a warehouse full of essence halts piece production (no fourth capacity axis) · `banking-fact` never decrements a piece and a bank point holding pieces keeps them; a piece's stock changes only through `LocatedStockOps.Add`; the `empire-resource-ssot.md` §3 row exists **once**, Class *Located good*, with P4 and P6 stated.
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Goods/LocatedGoodCatalog.cs,gk-core/src/FusionRpg.Server/Program.cs,docs/architecture/empire-resource-ssot.md,tests/FusionRpg.Core.Tests/World/Goods/LegionPieceStockTests.cs -Session <session-id>`
- **Shared files:** none
- **Notes:** tests run against a **synthetic injected** piece catalog — the real one does not exist until `legion-build` ships it, so this task proves the contract, not the corpus. One registry row shared with `legion-build-map.md` §5.14: whichever lands first writes it, the other amends; X4 already ruled the hashed located warehouse over `rpg_item_stock`, and this spec does not edit that map. CQ2's banked-goods shortfall draw is an **ask to `legion-build`** (which fitting, which doctrine upkeep, in what order), not a rule here. Acceptance 7 (the `goods.legion-piece.transitLossMilli` family row) pins a tuning key owned by `logistics-flow/spec-lane-loss.md` — **row 6, task 6.4**. It is verified there, not here, and this task cannot tick it.

---

## Wave L7 — `legion-build` W7 (legion equipment as a located good, the mechanics half)

### [ ] L7.1 `legion-equipment` (located-stock half) — fixed-stat pieces a stack wears
- **Spec:** docs/architecture/legion-build/spec-legion-equipment.md
- **Wave:** L7 (after family rows 1 and 11) · flag `legion.equipment` (this task registers it) · bump `L7`, its own
- **Depends on:** 0e.1, L3.1, row 11 (`legion-equipment-stock`), row 1 (`located-stock`, `production-halt`), row 0d (`sector-features`), row 0c (`trade-structure-rows`, the Workshop chain)
- **Acceptance:** (1) a piece's stats are identical for every player and every read; fitting consumes exactly the fitted count (a short stack is refused, not partly fitted) and casualties consume exactly the dead units' pieces — every read and move of located stock happening **inside `Step`**, with a replay test and a source scan proving no Data-side write; (2) no unique-item rule (sets, affix rolls, sockets, rarity count bands) applies, asserted on the resolver, and the legion slot vocabulary is closed and disjoint from `ItemRole`; (3) every contribution names its slot and piece under `legion-equip:`, and `produce-gear` is legal only where `SectorFeatures.TierOf(sector, legion-equipment)` reaches the requested rung, otherwise dropping `gear.inputs-short` / the named tier reason with nothing written.
- **Verify:** `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/Effects/Atoms/ContainerRow.cs,gk-core/src/FusionRpg.Core/Effects/Atoms/ContainerValidator.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Containers.cs,gk-core/src/FusionRpg.Core/World/WorldState.cs,gk-core/src/FusionRpg.Core/World/WorldCanonical.cs,src/FusionRpg.Core/World/Legion/LegionGear.cs,gk-core/src/FusionRpg.Core/Stats/Derived/ContributionSourceIds.cs,src/FusionRpg.Data/Sqlite/RpgStore.LegionGear.cs,src/FusionRpg.Core/World/Legion/LegionGearProduction.cs,data/tuning/legion.v7.json -Session <session-id>` plus `.\scripts\guard-actor-hub.ps1`
- **Shared files:** `WorldState.cs` — the member `Gear` field; `WorldCanonical.cs` — a `gear` row only for fitted stacks, after row 1's and L6.1's appends. **Tuning:** `legion.v{n+1}` (`equipment.recipeQtyPerTier`, `equipment.batchPerTurnByTier`, `equipment.bankedDrawPremiumMilli`).
- **Notes:** owes the `empire-resource-ssot.md` §3 row (P4 bottleneck, P6 two sinks) in the implementing change; widens `ContainerKind` (+`LegionGear`) and must regenerate `definitions.md` §1's already-stale grammar row in the same change; the banked-draw half is L10.1. The spec's Structure block omitted the `WorldCanonical.cs` edit its default-suppressed `gear` row needs; **the spec was fixed** in the reconciliation (R-19.5), and the file is listed in Shared files above.

---

## Row 12 — `fleet` W1

### [ ] 12.1 `carried-goods` — a hashed, sparse goods pool on a legion
- **Spec:** docs/architecture/trade-network/fleet/spec-carried-goods.md
- **Wave:** row 12 · flag `trade.fleet` (registered here) · bump N+12 (shared with 12.2)
- **Depends on:** 5.1, 5.2, row 1 (`located-stock`, warehouse), row 0e (`member-stack`, for bearer counting)
- **Acceptance:** capacity is a function of bearer count only — fighters never change it — and load/unload conserve per good per call without exceeding any bound (1, 2) · a world with no carried goods hashes, persists and replays byte-identically to today, and a non-empty pool round-trips save → load → hash (3, 5) · no in-`Step` removal of a legion drops carried goods without a recorded fate, asserted by a source scan over the removal sites (4)
- **Verify:** `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/World/WorldState.cs,gk-core/src/FusionRpg.Core/World/WorldCanonical.cs,gk-core/src/FusionRpg.Core/World/WorldValidation.cs,src/FusionRpg.Core/World/Logistics/Fleet/CarriedGoods.cs,src/FusionRpg.Core/World/Logistics/Fleet/FleetFacts.cs,src/FusionRpg.Core/World/Logistics/Fleet/FleetTuning.cs,gk-core/src/FusionRpg.Core/World/Turn/BattleApplication.cs,gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs,data/tuning/trade.v5.json,gk-core/scripts/verification-boundaries.v1.json,tests/FusionRpg.Core.Tests/World/Logistics/Fleet/CarriedGoodsTests.cs -Session <session-id>`
- **Shared files:** `WorldCanonical.cs` — **slot 4**, after 5.2's rows (§4); `WorldState.cs` — the row 12 carried-goods field; `RpgStore.World.cs` — the `carried_goods` column; `WorldValidation.cs` is **world-map's** (ask X-14) — the pool invariants need that owner's change, not a local edit
- **Notes:** owns row 12's `WorldCanonical` append-order re-bless (§6) and adds the `core-world-logistics-fleet` owner boundary every later fleet task uses; publishes `fleet.goodsPerBearer` as `trade.v{n+1}`. The removal-site scan stays red until `world-continuity`'s `AdvanceResolver` takes its call (ask A15) — that is a named wiring gap, not a failure of this task.

### [ ] 12.2 `depot` — the caravan building as load site, allowance and range origin
- **Spec:** docs/architecture/trade-network/fleet/spec-depot.md
- **Wave:** row 12 · flag `trade.fleet` (registered by 12.1) · bump N+12 (shared with 12.1)
- **Depends on:** 12.1, row 0d (`sector-features` — the `caravans` feature and its tier), rows 0b/0c (`empire-seed` `caravan-yard` tier variants and magnitudes), row 1 (warehouse axis), row 2 (`structure-upkeep`)
- **Acceptance:** goods move to or from an own warehouse only at a working own caravan building, and to or from a foreign hub's consignment only where that hub's owner has a working Caravan Yard in the sector, every refusal naming its reason (1) · allowance rises with labour on a diminishing, uncapped curve per tier, never lower at a higher tier, and is shared pro rata (2) · the building's loam upkeep appears exactly once, through the one structure term, asserted by summing upkeep with and without the depot (4)
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Logistics/Fleet/Depot.cs,src/FusionRpg.Core/World/Logistics/Fleet/LabourCurve.cs,src/FusionRpg.Core/World/Logistics/Fleet/DepotRange.cs,gk-core/src/FusionRpg.Core/World/Loam/LegionSupply.cs,src/FusionRpg.Core/World/Logistics/Fleet/FleetFacts.cs,src/FusionRpg.Core/World/Logistics/Fleet/FleetTuning.cs,data/tuning/trade.v6.json,tests/FusionRpg.Core.Tests/World/Logistics/Fleet/DepotTests.cs -Session <session-id>`
- **Shared files:** none from §4; `LegionSupply.cs` is touched a second time after 12.1 — both readers of "full" move together (`ProvisionedCapacity` for the `supply.restored` check and for `RationedDemand`), or a provisioned caravan never reports restored again
- **Notes:** blocked by ask X-11 — multi-slot `BuildResolver` (a slot whose kind is in `RequiredSlotKinds`) and the `build`-on-own-slot upgrade arm are world-map's and land first (§7). Publishes `depot.throughputCurveByTier` and `depot.provisionMilliByTier` as `trade.v{n+1}`; never hand-edit the generated structure row (`caravan-yard`) — that is `empire-seed`'s regeneration.

---

## Row 13 — `fleet` W2

### [ ] 13.1 `crew` — assigned bearers as a building's labour, with the working-site registry
- **Spec:** docs/architecture/trade-network/fleet/spec-crew.md
- **Wave:** row 13 · flag `trade.fleetRoutes` (registered by 13.2) · bump N+13 (shared with 13.2)
- **Depends on:** 12.2, wave **L2** (`legion-build` `standing-orders` — kind-keyed orders with per-kind resolvers, owner decision SO) and row **0e** (`member-stack`). Both are rows in the family order since reconciliation R-13; this task sequences after L2
- **Acceptance:** a building's labour equals the bearer count of own, present, unrouted legions on a crew order naming **its slot**, and no bearer is labour for two buildings (1) · a crew legion's burn and budget equal the same legion's off the order (2) · labour on a site's first working turn is independent of whether the order or the building came first, both orders tested (3)
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Logistics/Fleet/Crew.cs,src/FusionRpg.Core/World/Logistics/Fleet/FleetFacts.cs,tests/FusionRpg.Core.Tests/World/Logistics/Fleet/CrewTests.cs -Session <session-id>` (add `legion-build`'s standing-order kind registry file when that lands)
- **Shared files:** `legion-build`'s standing-order kind registry — one registration line, never a second order store
- **Notes:** **this task ships the `IWorkingSite` predicate registry** (§3 edge 1 of the landing order) with the caravan-building predicate (`LoadSite.Of`) **only**; `exchange-hub` registers its own at row 18 and `crossing-anchor` at row 20, and a feature with no registered predicate is simply *not working*. That inversion is what keeps `crew` at row 13 with no arrow pointing up. Widens three closed vocabularies (order kind, `crew.idle` fact token, `crew.no-bearers` refusal), each pinned with its reason.

### [ ] 13.2 `trade-route-order` — the trade-route standing-order kind
- **Spec:** docs/architecture/trade-network/fleet/spec-trade-route-order.md
- **Wave:** row 13 · flag `trade.fleetRoutes` (registered here) · bump N+13 (shared with 13.1)
- **Depends on:** 12.1, 12.2, 6.1 (`PathCache.Next`, the need rule's one predicate), wave **L2** (`legion-build` `standing-orders`) — a row in the family order since reconciliation R-13
- **Acceptance:** the order re-emits only existing command kinds, so the engine gains no movement path, and every caravan's `Kind` is `WorldEntityKind.Legion` (1, 7) · a world stepped from its command log with standing orders reproduces the state hash byte-identically (3) · a caravan never starts a trip while lane flow has an open path to its destination, while one already under way finishes (5, owner decision Q1)
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Logistics/Fleet/TradeRouteOrder.cs,src/FusionRpg.Core/World/Movement/BelievedPath.cs,gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs,src/FusionRpg.Core/World/Logistics/Fleet/FleetFacts.cs,tests/FusionRpg.Core.Tests/World/Logistics/Fleet/TradeRouteOrderTests.cs -Session <session-id>`
- **Shared files:** `legion-build`'s standing-order kind registry — one registration line; the loop state lives in that module's hashed order record, so its stamp change is `legion-build`'s, not this wave's
- **Notes:** the planner lift out of `FrontierRulesPolicy` must be byte-identical — run the AI goldens once at the lift. Acceptance 4 is the emergent-throughput identity (N loops × min(per-trip quantity, capacity)), never a pinned number. Lane loss applies to lane flow, not to carried goods; a caravan's risk is interception (14.2).

---

## Row 14 — `fleet` W3

### [ ] 14.1 `escort-link` — a caravan's escort holds with it, and answers the forecast
- **Spec:** docs/architecture/trade-network/fleet/spec-escort-link.md
- **Wave:** row 14 · flag `trade.fleetEscort` · bump N+14 (shared across row 14)
- **Depends on:** 13.2, 6.4, 9.1 (the forecast answer it names), wave **L4** (`legion-build` `escort-stance`) and wave **L5** (`field-battle-kinds`, for multi-entity sides — ask A8, which L5.1's criterion 3 closes). Both are rows in the family order since R-13
- **Acceptance:** over a full loop (march, load, march, unload) the escort ends each turn on the caravan's lane or sector, or the report names why (1) · lane loss with the escort posted never exceeds loss without it, through `lane-loss`'s monotonicity (3) · escort assignment order does not change the first escorted turn, both orders tested (4)
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Logistics/Fleet/EscortLink.cs,tests/FusionRpg.Core.Tests/World/Logistics/Fleet/EscortLinkTests.cs -Session <session-id>`
- **Shared files:** none
- **Notes:** owns no tuning key — `lane.stanceEscortMilli.escort` is 6.4's, published with `escort-stance`. Criterion 2 (the escort is in its charge's battle request) is **skipped and visible** until wave L5 (`field-battle-kinds`) widens the request to multi-entity sides — a wiring gap with a named owner **and a place in the family order** (R-13), not a wall. Do not read this task's green suite as proof criterion 2 works. This task never reads an escort strength — row 23 does, in `lane-loss`.

### [ ] 14.2 `interception` — the caravan-side consequence of an ordinary lane/sector battle
- **Spec:** docs/architecture/trade-network/fleet/spec-interception.md
- **Wave:** row 14 · flag `trade.fleetEscort` (row 14's wave flag) · bump N+14 (shared across row 14)
- **Depends on:** 13.2, 12.1, wave **L5** (`legion-build` `field-battle-kinds`, routing `Sector`/`Lane` battles) and row **0e** (`role-aware-placement`) — both rows in the family order since R-13
- **Acceptance:** a caravan's contact produces a `lane` or `sector` request and never a new kind — this module adds nothing to the closed `BattleKinds` set (1) · routed keeps the goods, drops orders for exactly one turn and resumes the route the turn after; destroyed hands the goods to `goods-cargo-fate`'s cache in the same step, per good (2, 3) · while the kinds are still refused, a caravan in contact keeps its goods and the report records the refused battle (5)
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Logistics/Fleet/Interception.cs,gk-core/src/FusionRpg.Core/World/Turn/BattleApplication.cs,src/FusionRpg.Core/World/Logistics/Fleet/FleetFacts.cs,tests/FusionRpg.Core.Tests/World/Logistics/Fleet/InterceptionTests.cs -Session <session-id>`
- **Shared files:** `BattleApplication.cs` — one call per side carrying goods, after 12.1's `OnEntityRemoved` call; every world battle crosses this file, so run the battle and turn goldens once at module end
- **Notes:** criteria 2–4 are inert until wave **L5** routes the non-district battle kinds — criterion 5 asserts today's refusal so the later change is visible. A wiring gap with a named owner and a dated row (R-13), not a wall.

### [ ] 14.3 `goods-cargo-fate` — the hashed goods cache, its claim and its fade
- **Spec:** docs/architecture/trade-network/fleet/spec-goods-cargo-fate.md
- **Wave:** row 14 · flag `trade.fleetEscort` (row 14's wave flag) · bump N+14 (shared across row 14)
- **Depends on:** 14.2, 12.1, row 0a (`ledger-keys`/`stock-deltas` — the `Cache` holder and the `carry`/`fade` kinds, ask A14)
- **Acceptance:** a legion's involuntarily lost goods equal the new or grown cache's goods per good, and a legion carrying nothing creates no cache (1) · claims conserve goods and split pro rata by free capacity, independent of faction ids and entity order, both orders tested (3) · a cache never grows except by creation, shrinks by its clamped fade every turn, and is removed when empty (4)
- **Verify:** `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/World/WorldState.cs,gk-core/src/FusionRpg.Core/World/WorldCanonical.cs,src/FusionRpg.Core/World/Logistics/Fleet/GoodsCache.cs,src/FusionRpg.Core/World/Logistics/Fleet/CarriedGoods.cs,src/FusionRpg.Core/World/Logistics/Fleet/FleetFacts.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldGraphDiff.cs,data/tuning/trade.v7.json,docs/architecture/empire-resource-ssot.md,tests/FusionRpg.Core.Tests/World/Logistics/Fleet/GoodsCacheTests.cs -Session <session-id>`
- **Shared files:** `WorldCanonical.cs` — the next conditional row after 12.1's slot 4, which §4 covers as *"any later conditional row in §2 order"*; `WorldState.cs`, `RpgStore.World.cs` and `WorldGraphDiff.cs` — the new cache table and its packed-row diff
- **Notes:** widens the located-goods row of `empire-resource-ssot.md` §3 with the carried-pool and cache holders and names cache fade as its sink (P1) — that edit belongs to this change. Publishes `cache.fadePerTurnMilli` as `trade.v{n+1}` (bounded ratio, commented). No path from a cache credits a wallet: goods reach the wallet only by being banked.

---

## CHECKPOINT 4 — Located income and fleet

**Rows 10–14.**

**Pass condition, from the plan §3:** a located reward is credited through banking. Legion equipment is a
located good in a sector warehouse. A caravan legion loads, carries, unloads, is escorted, and can be
intercepted — with a stated fate for its cargo.

---

## PHASE 5 — Counterparties

Landing-order rows **15–17**, plus world-continuity waves **WC5–WC8**, which land after row 16. 18 tasks.

---

## Row 15 — `counterparties` W1 (needs, roster, diplomacy facts, treasury, difficulty knobs)

Four capability rows share this wave's **one** bump (R2). The bump lands in 15.1; 15.2–15.4 register their
flag row against that same constant, and 15.5 registers none. **Only `empire-treasury`'s credits wait on the
save-identity re-key** (reconciliation R-8) — the module lands with the wave and reads zero.

### [ ] 15.1 `need-vector` — the real per-good want
- **Spec:** docs/architecture/trade-network/counterparties/spec-need-vector.md
- **Wave:** row 15 · flag `counterparties.needs` (one of four rows sharing this wave's single bump) · bump **N+15**, taken here
- **Depends on:** row 0a (`world-stamp`, `economy-report` creating `trade.v1.json`), row 1 (`sector-yield` located stock — landing-order.md §2 row 15)
- **Acceptance:** same `(world or view, faction, turn)` gives a byte-identical vector, no clock and no `System.Random`; want is monotone in stock and in demand, reads exactly 1000 when `stock == demand`, and is invariant when demand, stock and `k` scale by one factor; a legacy-stamped world keeps `UniformNeeds` and its command log and hash stay byte-identical.
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/World/Ai/INeedVector.cs','gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs','src/FusionRpg.Core/World/Trade/Needs/NeedVector.cs','gk-core/src/FusionRpg.Core/World/Intel/IWorldView.cs','data/tuning/trade.v{n+1}.json','tests/FusionRpg.Core.Tests/World/Trade/Needs/NeedVectorTests.cs') -Session <session-id>`
- **Shared files:** `TurnEngine.cs` — row 15's single `RulesetVersion` bump (§4 "one wave at a time").
- **Notes:** publishes the `needs.*` keys as `trade.v{n+1}` (§5: only row 0a creates the file). `data/tuning/trade.v*.json` has **no owner boundary row today**, so `verify-change.ps1:118` throws `VERIFICATION BOUNDARY MISSING` — adding it is part of this task (ask X-18). `World/Trade/**` resolves only to `core-fallback`; the named `core-world-trade-counterparties` boundary lands here (audit CA9). Owns this wave's flag-granted fixture re-bless (§6 row 1). `planned-sinks` is registered later by 17.2 and shocks by `trade-stories` — an extension seam, not a dependency.

### [ ] 15.2 `empire-roster` — many enemy empires per world
- **Spec:** docs/architecture/trade-network/counterparties/spec-empire-roster.md
- **Wave:** row 15 · flag `counterparties.roster` (shares this wave's single bump) · bump **N+15** (taken by 15.1)
- **Depends on:** row 0a (`world-stamp` carrying the template version, `synthetic-graph`), 15.1 (for the bump already rebased)
- **Acceptance:** a roster-stamped world validates for every N ≥ 0 rivals the synthetic builder produces and rejects zero or two dominant enemy empires naming the rule; an empire holding ground at creation with no seat or no rootbed is rejected while a landless dominant empire (`first-light`) validates; adding a rival leaves every other faction's AI commands for the same turn byte-identical.
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/World/WorldValidation.cs','gk-core/src/FusionRpg.Core/World/Ai/FactionPolicies.cs','gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs','gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.TwoHearths.cs','data/tuning/trade.v{n+1}.json','tests/FusionRpg.Core.Tests/World/RosterValidationTests.cs') -Session <session-id>`
- **Shared files:** none from §4 (no canonical, command or turn-log change of its own).
- **Notes:** owns half of the **shared** template-created-world golden re-bless with rows 0b/0c, `world-continuity` `world-creation` and 16.3 (§6 row 2) — cut `first-light` v2 / `two-hearths` v2 with two free `Wildland` slots per owned empire seat in that one re-bless, never separately. Publishes `personality.*` as `trade.v{n+1}` (X-18 boundary row again). Version-aware `WorldTemplateCatalog.Build` is `trade-foundation`'s ask A4, not this task.

### [ ] 15.3 `diplomacy-facts` — the hashed per-pair fact list
- **Spec:** docs/architecture/trade-network/counterparties/spec-diplomacy-facts.md
- **Wave:** row 15 · flag `counterparties.diplomacy` (shares this wave's single bump; covers the fact list only) · bump **N+15** (taken by 15.1)
- **Depends on:** row 0a (`world-stamp`), 15.1
- **Acceptance:** facts are append-only — `Seq` is gap-free and equals the list index and a source scan finds no `UPDATE`/`DELETE` on `rpg_world_diplomacy_facts`; replaying a world's command log rebuilds `Diplomacy` byte for byte and an empty list writes the same canonical bytes as the same world before the module; a fact appended by a turn-`N` command is visible in `N + 1` and to no hostility read in `N`.
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/World/WorldState.cs','gk-core/src/FusionRpg.Core/World/WorldCanonical.cs','src/FusionRpg.Core/World/Diplomacy/DiplomacyLedger.cs','gk-core/src/FusionRpg.Core/World/Intel/IWorldView.cs','gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs','gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldGraphDiff.cs','data/tuning/diplomacy.v1.json','tests/FusionRpg.Core.Tests/World/Diplomacy/DiplomacyLedgerTests.cs') -Session <session-id>`
- **Shared files:** `WorldCanonical.cs` — appends the **next** conditional row after the last one present at landing (§4 gives slots 1–4 to `world-stamp`, `located-stock`, `logistics-canonical`, `carried-goods`); `WorldState.cs` — the diplomacy field, row 15's slot. Land this before 15.4: only one module at a time appends hashed rows.
- **Notes:** the 12 fact kinds are a **closed vocabulary** the code owns — pin the count with that reason and never a fact-per-scenario count. Round 6 Q-A: `diplomatic-stance` (16.1) becomes a second *writer* of `treaty.broken`; the vocabulary does not widen. **This task is the one creator of `data/tuning/diplomacy.v1.json`, its loader and the `diplomacy` domain in `publish.py`** (`diplomacy.offerTtlTurns`) — settled by reconciliation R-3, which corrected landing order §5: §5's own rule gives `v1` to the **first** module that needs the domain, and that is this one at row 15; `exchange`'s `treaty-vocabulary` and `treaty-lifecycle` are both row 18c and publish `v{n+1}`. The file's verification-boundary owner row lands here too (X-18, R-17). Crosses Core and Data: full suite once at task end.

### [ ] 15.4 `empire-treasury` — the AI's banked goods
- **Spec:** docs/architecture/trade-network/counterparties/spec-empire-treasury.md
- **Wave:** row 15 · flag `counterparties.treasury` (shares this wave's single bump) · bump **N+15** (taken by 15.1)
- **Depends on:** 15.3 (the `WorldCanonical` append slot), row 0a (`ledger-keys` `f:<factionId>` holder, `stock-deltas`), row 8 (`banking-fact` destination seam — **credits only**)
- **Acceptance:** a `TryDebit` beyond balance returns `Ok = false` with the world unchanged and a credit to the player, a clan or the wild throws; capture of any sector including every seat leaves every treasury entry unchanged; `Δbalance = banked − sunk − destroyed` per faction per good per turn equals that turn's treasury `stock-deltas`, and a zero entry writes no canonical and no table row.
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/World/WorldState.cs','gk-core/src/FusionRpg.Core/World/WorldCanonical.cs','src/FusionRpg.Core/World/Trade/Treasury/EmpireTreasury.cs','gk-core/src/FusionRpg.Core/World/Intel/IWorldView.cs','gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldGraphDiff.cs','tests/FusionRpg.Core.Tests/World/Trade/Treasury/EmpireTreasuryTests.cs') -Session <session-id>`
- **Shared files:** `WorldCanonical.cs` — the conditional row after 15.3's, sparse; `WorldState.cs` — the treasury field (§4, row 15).
- **Notes:** **blocked for credits by the save-identity re-key** (X-1 → `material-ledger` row 0g → banking step row 8); round 6 C3 is *wait*. Reconciliation **R-8** narrowed §7's X-1 row to exactly this scope: the blocker is this module's **credits**, not wave 15 — 15.1, 15.2, 15.3 and 15.5 have no X-1 dependency at all. Interim behaviour, stated not discovered: the field, canonical row, seam registration, sink and collapse rules land and **every treasury reads zero**, the economy report prints zero **with that reason**, and acceptance proves the arithmetic on injected facts only — never a campaign's banked total. Round 6 CQ2's recurring drain arrives through 17.2's two `sink` reasons; no new fact kind, no new holder prefix. Crosses Core and Data: full suite once at task end.

### [ ] 15.5 `trade-difficulty-knobs` — the trade rows of the world's difficulty profile
- **Spec:** docs/architecture/trade-network/counterparties/spec-trade-difficulty-knobs.md
- **Wave:** row 15 · **no flag row, no bump of its own** (R3 / CM10: the profile id is stamped at world creation, so the knobs are fixed from creation) — it lands inside row 15's wave and takes none of its bump
- **Depends on:** row 0a (`world-stamp` carrying the profile id), 15.1 (the `trade.v{n+1}` publish chain)
- **Acceptance:** a missing profile row, a missing key, or a row for an unknown profile is a load rejection naming it; with `laneLossMilli = 1000` lane loss equals the un-knobbed result for every input; a knob read in `Step` for a subset of factions writes one `trade.handicap` line per affected faction per turn; `TradeDifficultyHub.For` is pure and never reads a file.
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Core/World/Trade/TradeDifficulty.cs','gk-core/src/FusionRpg.Server/Program.cs','data/tuning/trade.v{n+1}.json','tests/FusionRpg.Core.Tests/World/Trade/TradeDifficultyTests.cs') -Session <session-id>`
- **Shared files:** none from §4.
- **Notes:** `difficulty.<profileId>.*` publishes as `trade.v{n+1}` (§5) and needs its X-18 boundary row. The `laneLossMilli` identity property test can only run once `logistics-flow` `lane-loss` exists (row 6); until then the spec's unit test on the multiplier function is the whole criterion — say so rather than deferring the task. `world-continuity` W7 owns the profile catalog; this task owns three rows and their loader.

---

## Row 16 — `counterparties` W2 (stance, relation facts, clans)

Two capability rows share this wave's **one** bump (R2): `counterparties.stance` (16.1 + 16.2) and
`counterparties.clans` (16.3). The bump lands in 16.1.

### [ ] 16.1 `diplomatic-stance` — war and peace, derived from the facts
- **Spec:** docs/architecture/trade-network/counterparties/spec-diplomatic-stance.md
- **Wave:** row 16 · flag `counterparties.stance` (registered here; gates 16.2 too) · bump **N+16**, taken here
- **Depends on:** 15.3, 15.2, row 0d (`sector-features` for `TierFor`/`FactionTier`), row 0c (`empire-seed` Embassy row)
- **Acceptance:** with the flag absent `IsHostile(world, a, b) == (a != b)` for every pair and the shipped scenarios replay byte-identically; at peace each consumer is tested separately — no contact battle, not held-against (supply and `raise` pass), threat and believed supply ignore peaceful forces, the Finish rule is unblocked, `claim.at-peace`, `assault.at-peace`, `march.border-closed` without a registered passage; **order-independent** — a declaration and a peace acceptance for one pair in one turn give `war.declared` and no `peace.made` in both filing orders, and the source scan for "no owner inequality as hostility" is green.
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/World/Movement/ZoneOfControl.cs','gk-core/src/FusionRpg.Core/World/Movement/ContactResolver.cs','gk-core/src/FusionRpg.Core/World/Movement/ClaimResolver.cs','gk-core/src/FusionRpg.Core/World/Movement/MarchResolver.cs','gk-core/src/FusionRpg.Core/World/Turn/DistrictAssaultPhase.cs','gk-core/src/FusionRpg.Core/World/Growth/RaiseResolver.cs','gk-core/src/FusionRpg.Core/World/Ai/BelievedSupply.cs','gk-core/src/FusionRpg.Core/World/Ai/ThreatMap.cs','gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs','gk-core/src/FusionRpg.Core/World/Ai/MarchGraph.cs','gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs','gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs','tests/FusionRpg.Core.Tests/World/Diplomacy/DiplomaticStanceTests.cs','tests/FusionRpg.Guard.Tests/HostilityRuleGuardTests.cs') -Session <session-id>`
- **Shared files:** `TurnEngine.cs` — row 16's single bump; `WorldCommand.cs` — row 16's player verbs `war-declare`, `peace-offer`, `peace-accept`, with one `WorldCommandAdmission` arm per kind in the same change (§4).
- **Notes:** **owns the passage seam** — `IPassageRule.Grants(world, bands, grantor, requester)`, **default closed**, which `exchange` `trade-access` (row 18) *registers into*; this task names no exchange module (§3 edge 4). Its §8 no-longer-bumps claim is withdrawn by round 6 C1: a wave granting a capability always takes its bump. Owes `path-cache` the graph-version trigger on a stance change (row 6). Owns this wave's flag-granted fixture re-bless (§6 row 1). Touches every hostility consumer in Core: full suite once at task end; the campaign scenarios are run on legacy stamps and **reported** — a movement there is a defect, not a re-bless.

### [ ] 16.2 `relation-facts` — the bridge to the one relation ladder
- **Spec:** docs/architecture/trade-network/counterparties/spec-relation-facts.md
- **Wave:** row 16 · gates on `counterparties.stance` (16.1's row) · registers no capability of its own, no second bump (R2: one bump per wave)
- **Depends on:** 16.1, 15.3, `npc-story-events` `story-ledger` + `relation-ledger` (asks A1, A2, A7, A8 — another program)
- **Acceptance:** deleting every story-ledger row after a turn leaves that turn's replay hash unchanged; re-committing a turn appends no story fact and writes no snapshot row, and at most `cap` `trade.fulfilled` facts are appended per pair per turn whatever the fill count; projecting facts moves no world hash, and `IWorldView.BandWith` during the fill equals `BandSnapshot.For` in that turn's step.
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs','gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs','src/FusionRpg.Core/World/Facts/RelationFactProjector.cs','gk-core/src/FusionRpg.Core/World/Intel/IWorldView.cs','data/tuning/diplomacy.v{n+1}.json','tests/FusionRpg.Core.Tests/World/Facts/RelationFactProjectorTests.cs','gk-core/tests/FusionRpg.Data.Tests/WorldTurnCommitTests.cs') -Session <session-id>`
- **Shared files:** `RpgStore.WorldTurns.cs` — row 16's packed rows, additive through `EnsureColumn`; `TurnEngine.cs` — no bump here (16.1 took it).
- **Notes:** **lands with an EMPTY registration set and names no exchange module** (§3 edge 3): settlement deltas arrive as the `stock-deltas` kinds `settlement-payment` registers at row 18, so this task emits no `trade.fulfilled` until they exist — correct, since nothing has settled. Owns the one step-input record `rpg_world_step_inputs` with registered kinds `band`, `soul-budget`, `goods-cover`; `exchange` and 17.2 register into it, never a second table (C17 / round 5 X14). Crosses Core, Data and a sibling program's store: full suite once at task end.

### [ ] 16.3 `clan-seeding` — clans on the map
- **Spec:** docs/architecture/trade-network/counterparties/spec-clan-seeding.md
- **Wave:** row 16 · flag `counterparties.clans` (shares this wave's single bump; gates clans on the map and nothing else) · bump **N+16** (taken by 16.1)
- **Depends on:** 15.2, 15.1, row 0c (`empire-seed` `trade-structure-rows` — the tier-1 Trading Post and Caravan Yard variants), row 0d (`sector-features` for the seeded tier)
- **Acceptance:** every seeded clan satisfies §1 rules 1–6 and each rule has a negative test rejected with the rule named; two clans with the same climates and species read identical personalities, recomputed from state with no field storing it (source scan); every clan hub `Market` slot carries a constructed tier-1 trade building and the hub sector a constructed tier-1 caravan building, and a clan-stamped world with zero clans validates and plays while a legacy world runs no clan rule.
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/World/WorldValidation.cs','src/FusionRpg.Core/World/Trade/Clans/ClanPersonality.cs','gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs','gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.TwoHearths.cs','tests/FusionRpg.Core.Tests/World/Trade/Clans/ClanSeedingTests.cs') -Session <session-id>`
- **Shared files:** none from §4 (template content and validation only).
- **Notes:** **reads the Trading Post row from `empire-seed` and its tier from `sector-features`, never from an exchange module** (§3 edge 2) — a seeded clan hub is fit for `exchange`'s later gate, and it registers nothing there. Feature rows load as the neutral `StructureKind.Feature` (round 6 C2): a row shipping `structureKind: none` cannot load. Second half of the **shared** template golden re-bless with 15.2, rows 0b/0c and `world-continuity` `world-creation` (§6 row 2). Clans get no A1 start kit — they are not empires.

---

## Wave WC5 — `world-continuity` W5 (production world creation and the advance)

Two tasks, **one flag `continuity.advance` and the wave's one bump, ordinal `C3`**. It lands after family row
16 because the A1 start kit needs `counterparties`' v2 template versions for their free `Wildland` slots, and
because the template-created world goldens are **one shared re-bless** across four modules (§6).

### [ ] WC5.1 `world-creation` — production creation, the template ladder, the stamp and the start kit
- **Spec:** docs/architecture/world-continuity/spec-world-creation.md
- **Wave:** wave WC5 · flag `continuity.advance` (registered here) · the wave's one bump, ordinal **C3** (R-14, §2 row WC5)
- **Depends on:** 0f.1, 0f.2, WC2.1; cross-cluster: row 0a (`world-stamp`), row 0c (0c.1's `banking`/`storage` rows), `sector-features` (the `Feature` member and `StructureDef.FeatureUnlock`), row 15 (`empire-roster`'s v2 templates), row 16 (`clan-seeding`)
- **Acceptance:** `POST /api/world/begin` creates exactly one active map world for a save with none and is `ok.exists` otherwise; **two saves** each get distinct world ids, and a row owned by another save is never reported as `ok.exists` · `NextWorld` is pure and total over the tunable ladder, the intensity transform never leaves `0..MaxIntensityMilli` and is monotone non-decreasing, no creation path writes the literal `1` for the stamp, and the test and production routes produce byte-identical worlds for the same `(template, seed, rung)` · **start kit:** every world created from a current template version holds, in every empire seat sector the empire owns at creation, exactly one active tier-1 `banking` building and one `storage` building (`SectorFeatures.TierOf = 1` each) and none in a clan's sector; a template whose seat lacks a free allowed slot is refused `creation.start-kit-no-slot`; a legacy-stamped world rebuilds with no kit and its old hashes
- **Verify:** `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs,gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs,src/FusionRpg.Core/World/WorldCreation.cs,gk-core/src/FusionRpg.Server/WorldEndpoints.cs,data/tuning/world-continuity.v6.json,tests/FusionRpg.Data.Tests/World/WorldCreationTests.cs,tests/FusionRpg.Server.Tests/WorldBeginEndpointTests.cs -Session <session-id>`
- **Shared files:** `CreateWorld` is touched by `world-stamp` (row 0a), `world-state-vocabulary` (0f.1) and this task **in that order** (`landing-order.md §4`)
- **Notes:** **Golden re-bless this task shares:** the template-created world goldens for the A1 kit — **one shared re-bless** with 0c.1, `counterparties` `empire-roster` (row 15) and `clan-seeding` (row 16); whichever lands last re-blesses (`landing-order.md §6`). S1 is read from `sector-features`, never restated: the kit sets sector and slot owner in the same creation write. `MaxIntensityMilli = 3000` is registered as a bound and the ladder step saturates. Publishes `world-continuity.v{n+1}` for the ladder. The kit cannot be green before row 15, so do not start this task on the current template versions.

### [ ] WC5.2 `advance-carry` — the advance verb, a weight limit, and no goods aboard
- **Spec:** docs/architecture/world-continuity/spec-advance-carry.md
- **Wave:** wave WC5 · rides `continuity.advance` and the wave's one bump (ordinal **C3**)
- **Depends on:** WC5.1, 0f.1, WC2.1, WC3.1
- **Acceptance:** **conservation** — for every item row, stack quantity and unique actor the sum across the two worlds equals the sum before, nothing is copied, the only loss is `CarriedLoam` zeroed with a report line carrying the amount, and a unique actor is a member of at most one world's legion at every committed state · the limit is a **weight**: `load = Σ (Count × world.carry.capacity)` over every departing member with `Count > 0`, refused past with `carry.limit` and **never clamped**, `won` using the larger capacity; the figure equals `LegionWorldChannels.SumPerUnit` over the same legions (one roll-up, not two) and the load is **logged**, so a replay with the Hub delegate absent reproduces the same admissions and hash · both worlds replay to their stored hashes, a failed advance leaves both worlds and every cargo row unchanged, exactly one map world is `active` afterwards, and a departing legion carrying a world stock is refused `carry.goods-aboard` with nothing written
- **Verify:** `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs,gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.LegionCargo.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs,data/tuning/world-continuity.v7.json,tests/FusionRpg.Data.Tests/World/AdvanceCarryTests.cs -Session <session-id>`, plus `python gk-core/scripts/audit-overflow.py`
- **Shared files:** `gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs` — `depart` and `advance` are the **player's own** kinds (X11), added with their `WorldCommandAdmission` arms in the same change; `RpgStore.WorldTurns.cs` — the logged carry load
- **Notes:** reads `world.carry.capacity` behind a **stated default** (`carryWeightPerUnitDefault`) until the named future program `world-derived` ships (round 6 D2); it defines and folds no channel. Round 6 S2: trade goods cross only by `rift-trade` route, so the `world_stock` cargo-kind ask to scoped-inventory is withdrawn. Publishes `world-continuity.v{n+1}` with the three weight keys replacing the two legion counts. Publishes the `AfterCrossWorldMove` hook that `rift-trade` `crossing-anchor` (family row 20) registers into — the hook has no subscriber until then, closing M1 cycle 6. Owes an `enforcement-registry.v1.json` row (no cross-world copy — the conservation test). The manifest is the whole entity with a per-field crossing table and a reflection test that fails on an unlisted field (A-WC4).

---

## Wave WC6 — `world-continuity` W6 (the background economy)

Three tasks, **one flag `continuity.backgroundEconomy` and the wave's one bump, ordinal `C4`**. Lands after
WC5 and after family row 1.

### [ ] WC6.1 `background-yield` — the 500-hour cure, into warehouses, never a wallet
- **Spec:** docs/architecture/world-continuity/spec-background-yield.md
- **Wave:** wave WC6 · flag `continuity.backgroundEconomy` (registered here) · the wave's one bump, ordinal **C4** (R-14, §2 row WC6)
- **Depends on:** WC3.2; cross-cluster: family row 1 (`sector-yield` `located-stock` and `warehouse-axis` — the located registry class the yield lands in)
- **Acceptance:** `yieldMilli(h, mode) < 1000` for every `h ≥ 1`, strictly decreasing in `h` and `> 0` for every tested `h` (a property test over a wide range — a structural bound, not a population) · for the same state, background yield per period is below active yield, adding a hibernating world never raises the per-world multiplier, and idle's base ≤ hibernating's base (load-time validation) · **no** coarse or idle record writes a wallet row, a material-ledger row or a banking fact (source scan plus store test)
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Turn/CoarseStep.cs,src/FusionRpg.Core/World/Turn/BackgroundYield.cs,data/tuning/world-continuity.v8.json,tests/FusionRpg.Core.Tests/World/BackgroundYieldTests.cs -Session <session-id>`
- **Shared files:** `TurnEngine.cs` — the wave's one bump; the located-stock canonical row is `sector-yield`'s (row 1), appended there, not here
- **Notes:** the total is **reported** by the trade-foundation economy report, never pinned by a test (P1 net-flow). Every faucet names its sink in the same change (upkeep). Owes an `enforcement-registry.v1.json` row (no background wallet or banking write). Nothing here banks, so round 6 C3's save-identity wait does not apply. Publishes `world-continuity.v{n+1}` for `hibernatingYieldMilli` and the decay curve — per-mille bounded ratios, commented as exempt from the no-caps rule.

### [ ] WC6.2 `world-event-budget` — one deck, a per-state budget
- **Spec:** docs/architecture/world-continuity/spec-world-event-budget.md
- **Wave:** wave WC6 · rides `continuity.backgroundEconomy` and the wave's one bump (ordinal **C4**)
- **Depends on:** 0f.1, WC3.2
- **Acceptance:** the budget is a pure lookup over `(state, outcome)` and all nine pairs return per §1, tested exhaustively over the closed product · the load-time ordering holds and a tuning file that violates it is rejected · the number of event pulls in a coarse record never exceeds `⌊budget × n / 1000⌋`, the deck id a coarse draw uses equals the active draw's for the same world, and a world's budget changes through its two columns only
- **Verify:** `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs,src/FusionRpg.Core/World/Turn/CoarseStep.cs,src/FusionRpg.Core/World/Turn/WorldEventBudget.cs,data/tuning/world-continuity.v9.json,tests/FusionRpg.Core.Tests/World/Turn/WorldEventBudgetTests.cs -Session <session-id>`
- **Shared files:** `TurnEngine.cs` — the `Events` phase reads the budget; the phase order stays locked (`decisions.md:7`) and the bump is the wave's one
- **Notes:** never a second deck — a hibernating event resolves inside `CoarseStep` from the same deck the active draw uses. `npc-story-events`' map has no per-state budget and no hibernating host; that stays an **ask** on that program, filed, not built here. Publishes `world-continuity.v{n+1}` for the `eventBudget.*` per-mille keys.

### [ ] WC6.3 `world-difficulty-profile` — the catalog and the knobs, in two files
- **Spec:** docs/architecture/world-continuity/spec-world-difficulty-profile.md
- **Wave:** wave WC6 · rides `continuity.backgroundEconomy` and the wave's one bump (ordinal **C4**) (its `default` profile is hash-neutral, so it grants no capability of its own)
- **Depends on:** WC5.1, WC3.2; cross-cluster: row 0a (`trade-foundation` `world-stamp` stores the profile id)
- **Acceptance:** an unknown profile id rejects the load with `difficulty.unknown`, and a profile id in the catalog with no knob block (or the reverse) is a load rejection · a world's profile id is identical at creation and after any number of turns and catch-ups · a world on `default` produces byte-identical step hashes and coarse results to a build without this module, and the knob values a coarse record used are the **logged** ones — a replay with the catalog absent succeeds
- **Verify:** `.\scripts\verify-change.ps1 -Paths data/tuning/world-difficulty-catalog.v1.json,data/tuning/world-continuity.v10.json,src/FusionRpg.Core/World/WorldDifficultyProfile.cs,gk-core/scripts/verification-boundaries.v1.json,tests/FusionRpg.Core.Tests/World/WorldDifficultyProfileTests.cs -Session <session-id>`
- **Shared files:** none from landing-order §4; the profile id rides `trade-foundation`'s stamp record, which this task does not edit
- **Notes:** two files by tunables-ssot T7/T8 — ids and display names in `world-difficulty-catalog.v1.json`, numbers under `difficulty.profiles.{id}` in `world-continuity.v{n+1}` (A-WC9/m12). The catalog is a **new domain**, so `publish.py` needs its first-version path extended here, and both files need verification-boundary rows in this change (program rule R3). The player word is a *difficulty profile*; no IP words and no named actors in a display name.

---

## Wave WC7 — `world-continuity` W7 (the while-you-were-away digest)

### [ ] WC7.1 `away-digest` — derived from the stored record, never recomputed
- **Spec:** docs/architecture/world-continuity/spec-away-digest.md
- **Wave:** WC7 · no flag, no bump (R3: report entries and notification drafts derived from stored coarse and idle records; nothing `Step` or the canonical projection reads)
- **Depends on:** WC3.2, WC3.3, WC4.2
- **Acceptance:** every sector lost, warden fight and storylet resolved in a coarse record appears **exactly once**, deduped on `(save, world, record, fact)` · the digest is derived from the stored record — re-running `AwayDigest.From` on the stored row gives a byte-identical digest with **no** world-graph or Hub read, asserted with the store and Hub seams absent · losses appear in capture order before `world.fallen`, and `away.credited` always appears stating credited and elapsed turns
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Turn/AwayDigest.cs,gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs,gk-core/src/FusionRpg.Server/WorldEndpoints.cs,tests/FusionRpg.Core.Tests/World/Turn/AwayDigestTests.cs,tests/FusionRpg.Server.Tests/AwayDigestEndpointTests.cs -Session <session-id>`
- **Shared files:** none from landing-order §4
- **Notes:** the `rift.*` prefix joins the closed digest prefix list (rift ask A3) — a closed vocabulary pinned with its reason, not a count of facts. Notification delivery is `notification-ssot`'s (`world-notify-source`, `notify-service`); this task writes drafts only. Coarse drafts are catch-up, never live.

---

## Wave WC8 — `world-continuity` W8 (the multiverse surface)

### [ ] WC8.1 `multiverse-surface` — a layer over the World stage, `/idea-ui` first
- **Spec:** docs/architecture/world-continuity/spec-multiverse-surface.md
- **Wave:** WC8 · no flag, no bump (R3: a read-only FE layer; its unlocks are UI milestones, not stamp capabilities)
- **Depends on:** 0f.1, WC5.2, WC7.1, WC4.2
- **Acceptance:** no new top-level route — every surface opens over the World stage (GG-1) — and every disabled verb shows the server's reason verbatim through the authored copy catalog · opening a hibernating world's view triggers exactly one catch-up call, and reopening it with no pending turns makes a call that writes nothing · the advance dialog never lets the picked load pass the carry weight budget, **computing neither** (it reads the budget and the logged load), and says plainly that trade goods do not cross with an advance — they cross by a `rift-trade` route, with `carry.goods-aboard` explained in the player's words
- **Verify:** `npm test`, `npm run build` and `npm run test:e2e` in `gk-web/web/fusion-rpg-web`, then `.\scripts\verify-change.ps1 -Paths web/fusion-rpg-web/src/stages/world/multiverse,gk-web/web/fusion-rpg-web/src/lib/bus/world.ts -Session <session-id>`
- **Shared files:** none from landing-order §4
- **Notes:** `/idea-ui` runs **before** this task; the multiverse map's drawing is undecided and this fragment does not decide it. Buy before build applies to its charts, gauges and motion (the locked set in `docs/design/tech-stack.md`); Phaser-class canvases stay stage-lazy. The list cache must enumerate its full trigger set including `begin`, idle, recall and the End Turn background catch-ups (A-WC17, DESIGN-GATE §2.16), with a test per trigger.

---

## Row 17 — `counterparties` W3 (clan economy, goods sinks, conquest)

Three capability rows share this wave's **one** bump (R2). The bump lands in 17.1.

### [ ] 17.1 `clan-economy` — a clan's production, consumption and upkeep
- **Spec:** docs/architecture/trade-network/counterparties/spec-clan-economy.md
- **Wave:** row 17 · flag `counterparties.clanEconomy` (one of three rows sharing this wave's single bump) · bump **N+17**, taken here
- **Depends on:** 16.3, 15.1, row 1 (`sector-yield` located stock, warehouse axis, production halt), row 5 (`logistics-flow` `logistics-phase` — the pass runs after `exchange` settlement, ask A12)
- **Acceptance:** a clan-owned and a player-owned sector with identical content produce identical located goods in the same turn (no clan branch in production); `Δstock = produced − consumed − sold + bought − lost` per clan per good per turn equals that turn's clan stock deltas, and a clan with no production and no purchases never ends a turn above the turn before; without `counterparties.clanEconomy` the pass does nothing and the hash is unchanged, including on a world that has `counterparties.clans`.
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Core/World/Trade/Clans/ClanConsumption.cs','gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs','data/tuning/trade.v{n+1}.json','tests/FusionRpg.Core.Tests/World/Trade/Clans/ClanEconomyTests.cs') -Session <session-id>`
- **Shared files:** `TurnEngine.cs` — row 17's single bump, plus the consumption pass inside the `Logistics` phase `logistics-flow` owns (§4: the phase slot is created once by `banking-fact` at row 4).
- **Notes:** publishes `clan.consumptionPerTurnMilli` as `trade.v{n+1}` (§5) and needs its X-18 boundary row. The report asserts reconciliation only — never a clan or good count. Owns this wave's flag-granted fixture re-bless (§6 row 1). `Logistics` step order is `logistics-flow`'s and is quoted, not restated (round 5 X5).

### [ ] 17.2 `empire-goods-sinks` — the goods cost every empire pays
- **Spec:** docs/architecture/trade-network/counterparties/spec-empire-goods-sinks.md
- **Wave:** row 17 · flag `counterparties.sinks` (shares this wave's single bump) · bump **N+17** (taken by 17.1)
- **Depends on:** 15.4, 15.1, 16.2 (the `goods-cover` kind in the one step-input record), rows 0b/0c (`empire-seed` cost bands), row 8 (banking, for an AI treasury with a balance to drain)
- **Acceptance:** the same structure in the same sector costs the player and an AI empire the same goods from their respective banked stores; a build short of any one cost term spends nothing and drops with a named reason (`build.goods-short` for goods), and re-committing a turn spends nothing twice; an AI empire's goods-cost build reduces its treasury by exactly the cost with a `sink` stock delta, and without the flag a build costs exactly what it costs today with the hash unchanged.
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs','src/FusionRpg.Core/World/Trade/Sinks/StructureGoodsCost.cs','gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs','data/tuning/trade.v{n+1}.json','tests/FusionRpg.Core.Tests/World/Trade/Sinks/StructureGoodsCostTests.cs','gk-core/tests/FusionRpg.Data.Tests/WorldTurnCommitTests.cs') -Session <session-id>`
- **Shared files:** `RpgStore.WorldTurns.cs` — row 17's packed rows and the pre-step `goods-cover` read, additive through `EnsureColumn`.
- **Notes:** `BuildResolver.cs` is **world-map's file**, not this family's (§4) — its multi-slot and upgrade arms are ask **X-11** and must land before this task touches it; coordinate rather than fork. Round 6 CQ2 adds the two recurring sink reasons `legion-equip` and `doctrine-upkeep`, debiting the treasury only for the **shortfall** after local located stock is spent, the same rule for player and AI, tested against umbrella invariant 11; the `legion-build` half (which fittings and upkeep may fall back, in what order, and what happens when the treasury is empty) is an **ask on `legion-build`**, not decided here. Registers the `planned-sinks` demand term into 15.1's one function and publishes `needs.reserveTurns`. Crosses Core and Data: full suite once at task end.

### [ ] 17.3 `conquest-consequences` — what capture means for counterparties
- **Spec:** docs/architecture/trade-network/counterparties/spec-conquest-consequences.md
- **Wave:** row 17 · flag `counterparties.conquest` (shares this wave's single bump) · bump **N+17** (taken by 17.1)
- **Depends on:** 16.1, 16.2, 17.1, 15.4
- **Acceptance:** capturing a clan sector writes one `clan.conquered` entry naming clan, conqueror and sector, reads the hub closed to every `exchange` query that turn and gives the next `Production` to the conqueror, while a clan sector lost to fade writes none; a surviving AI empire's treasury entries are identical before and after losing any sector including a seat while another remains; a collapsed empire's treasury is empty with `collapse` stock deltas equal to the pre-destruction balance and a sink line in the economy report, and produces no delta on later turns.
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs','src/FusionRpg.Core/World/Trade/ConquestPass.cs','tests/FusionRpg.Core.Tests/World/Trade/ConquestPassTests.cs','gk-core/tests/FusionRpg.Core.Tests/World/ClaimTests.cs','tests/FusionRpg.Guard.Tests/OneCapturePathGuardTests.cs') -Session <session-id>`
- **Shared files:** `TurnEngine.cs` — one pass at the **end of `Snapshot`** over opening-versus-now ownership (no bump here; 17.1 took it), so ground lost to fade is seen as well as claims; `ClaimResolver.cs` is not edited.
- **Notes:** the in-cluster cycle with `relation-facts` is resolved by the wave order (row 16 then row 17), not by a seam — this task reads 16.2's emitter. The one-capture-path source scan concerns the **sector** owner only: it must not flag the slot-owner writes in `BattleApplication.cs:161` or `ClaimResolver.cs:115`. A collapsed empire's destroyed treasury is a named sink, so P1's "every faucet names its sink" holds in this change.

---

## CHECKPOINT 5 — Counterparties

**Rows 15–17.**

**Pass condition, from the plan §3:** empires and clans have needs, a roster, diplomatic facts and a
treasury; relation bands move on real deltas; conquest has consequences. Four flag rows share wave 15's
single bump.

---

## PHASE 6 — Market and AI

Landing-order rows **18** (four sub-waves) and **19** (five sub-waves). 22 tasks.

The sub-wave splits and flag ids below are no longer proposals — reconciliation **R-5** and **R-6** settled
them and §2 now carries the rows.

---

## Row 18a — `exchange` W1 (value, classes, prices, the treaty registry)

**No flag, no bump** (R3: a value table, a class table, a pure Math file, a hand-authored registry and a test
scaffold). Build order from `exchange-map.md:73-75`.

### [ ] 18a.1 `goods-valuation` — one relative value per good, and the soul conversion
- **Spec:** docs/architecture/trade-network/exchange/spec-goods-valuation.md
- **Wave:** row 18a · no flag, no bump (R3: no hashed state — the spec says so itself, §Dependencies)
- **Depends on:** row 0a (`economy-report`, which creates `data/tuning/trade.v1.json` per landing-order §5)
- **Acceptance:** (1) every `tradeable`/`world-barter-only` good has `baseValue ≥ 1`, asserted as a join against `tradeable-goods`, never a count; (3) `ValueForSouls(SoulsBaseFor(v)) ≥ v` and `SoulsBaseFor(ValueForSouls(s)) ≤ s` over a seeded sweep; (4) source scan: no `ContentScale`/`SoulSinkPolicy`/`PowerLadder` under `src/FusionRpg.Core/World/Trade/`.
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Trade/Valuation/GoodsValuation.cs,src/FusionRpg.Core/World/Trade/Valuation/TradeTuningLoader.cs,tests/FusionRpg.Core.Tests/World/Trade/Valuation/GoodsValuationTests.cs,tests/FusionRpg.Guard.Tests/TradeValuationScanTests.cs,gk-core/scripts/verification-boundaries.v1.json,docs/architecture/power/ssot-power-scale.md,docs/architecture/power/inventory.json -Session <session>` plus `python gk-core/scripts/guard-power.py` and `python gk-core/scripts/audit-overflow.py`.
- **Shared files:** none from landing-order §4. It publishes `data/tuning/trade.v{n+1}.json` (§5: `economy-report` is the file's only creator).
- **Notes:** lands **first** in the cluster — it closes the `goods-valuation` ↔ `tradeable-goods` cycle (global audit M1, spec-tradeable-goods §Dependencies). Acceptance 5 owes the `ssot-power-scale.md` §10.2 value-index row **and** its `inventory.json` mirror in the same commit, or the task is not done. `gk-core/data/tuning/**` has **no verification boundary** today (`scripts/verify-change.ps1:118` throws `VERIFICATION BOUNDARY MISSING`; the registry maps only named tuning files) — adding the owner row is part of this task (ask X-18, landing-order §7), and the focused row `core-world-trade-valuation` replaces `core-fallback`.

### [ ] 18a.2 `tradeable-goods` — the closed table of what may trade, and the two credit pools
- **Spec:** docs/architecture/trade-network/exchange/spec-tradeable-goods.md
- **Wave:** row 18a · no flag, no bump (R3: a lookup table plus document amendments)
- **Depends on:** 18a.1, row 0b (`legion-bands`, which produces `LegionPieceDef` — global audit m10), row 1 (`located-goods-registry`, ask E-A4)
- **Acceptance:** (1) every good id resolves to exactly one of the four classes, total over the material, located-goods and world-stock catalogs, and throws on an unknown id; (2) `loam`, `recruit` and every located soul good are `never`, asserted by name; (4) settlement throws on a cross-pool pairing, and a property sweep finds no basket whose pool-A proceeds pay for a pool-B buy.
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Trade/Goods/TradeGoods.cs,tests/FusionRpg.Core.Tests/World/Trade/Goods/TradeGoodsTests.cs,docs/architecture/item/ssot-materials-crafting.md,docs/architecture/empire-resource-ssot.md,gk-core/src/FusionRpg.Core/Items/Materials/SalvagePolicy.cs,gk-core/scripts/verification-boundaries.v1.json -Session <session>`
- **Shared files:** none from §4.
- **Notes:** the four amendments in §Required amendments (materials §7.3, the `SalvagePolicy.cs:46-48` comment, the `catalyst.*` and `souls` registry rows) land **in this commit** (DESIGN-GATE evidence rule 6) and `audit-doc-citations.py --scope` must report no HIGH on both amended documents. Acceptance 3's admission refusals (`order.good-never-trades`, `order.souls-payment-only`) **cannot be tested here**: the `order-set` kind arrives in 18c.1, so this task ships `ClassOf`/`PoolOf` and the reason strings, and 18c.1 wires the admission arm and asserts the refusals. Moving `tradeable-goods` into wave 18c instead would break the global-audit M1 landing note that pairs it with `goods-valuation` in one wave, one flag, one bump.

### [ ] 18a.3 `treaty-vocabulary` — `treaty-kind.v1`, the `Access` levels, the tier and article tables
- **Spec:** docs/architecture/trade-network/exchange/spec-treaty-vocabulary.md
- **Wave:** row 18a · no flag, no bump (R3: a hand-authored registry and its reader)
- **Depends on:** row 15 (`diplomacy-facts`, task 15.3 — **the creator of `data/tuning/diplomacy.v1.json` and its loader**, R-3); none else in-cluster (the disposition band registry is built, `gk-data/packs/fusion/data/seed/dungeon/_registry/disposition.v1.json`); row 0d (`sector-features`) for the `SectorFeature` values §5 names
- **Acceptance:** (1) exactly five treaty kinds and four ordered `Access` levels, each pinned as a closed vocabulary whose message says a sixth/fifth is a reviewed change; (4) with no treaty facts a `Clan` grantor gives `market` at `wary`/`open`/`eager` and `closed` at `hostile`, an empire `closed` at every band, asserted per band from the registry; (6) the 4+2 tier ladders, six deal classes, nine article kinds, two deal shapes and five refusal codes are pinned the same way and every deal class names a tier that exists.
- **Verify:** `.\scripts\verify-change.ps1 -Paths data/seed/diplomacy/_registry/treaty-kind.v1.json,src/FusionRpg.Core/World/Diplomacy/TreatyKindRegistry.cs,data/tuning/diplomacy.v{n+1}.json,tests/FusionRpg.Core.Tests/World/Diplomacy/TreatyVocabularyTests.cs,gk-core/scripts/verification-boundaries.v1.json -Session <session>`
- **Shared files:** none from §4.
- **Notes:** **this task publishes `data/tuning/diplomacy.v{n+1}.json`; it does not create it.** Reconciliation R-3 settled the creator as `counterparties` `diplomacy-facts` (task 15.3, row 15), which needs `diplomacy.offerTtlTurns` a whole row group earlier — this module and `treaty-lifecycle` are both row 18c. Its keys (`treaty.{kind}.lowestBand`, `access.bandGrant.Clan.*`) publish onto the file 15.3 created. The registry path `data/seed/diplomacy/**` is still **unmapped**: add its owner boundary row in this commit (X-18, this family's own work under R-17); the tuning file's row came with 15.3, so do not add a second overlapping one.

### [ ] 18a.4 `price-curve` — the quote, the spreads, the walk
- **Spec:** docs/architecture/trade-network/exchange/spec-price-curve.md
- **Wave:** row 18a · no flag, no bump (R3: a pure Math file, no state, no I/O)
- **Depends on:** 18a.1 (`base = ValueOf(good)`)
- **Acceptance:** (1) `askMilli ≥ priceMilli ≥ bidMilli` and strict `ask > bid` under the load checks, for every generated input; (5) buy `q` then sell `q` loses value in **both** shapes — both legs walked from `s₀` in one pass, and the sell walked from `s₀ − q` — tested with step sizes above and below `q`, including a step that moves price by more than both spreads; (8) every load check in §Design 5 rejects its bad document naming the key.
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Trade/Pricing/PriceCurve.cs,tests/FusionRpg.Core.Tests/World/Trade/Pricing/PriceCurveTests.cs,data/tuning/trade.v1.json,gk-core/scripts/verification-boundaries.v1.json -Session <session>` plus `python gk-core/scripts/audit-overflow.py --targets A3` and `python gk-core/scripts/audit-magic-numbers.py --targets M1` (both must show nothing under `Pricing/`).
- **Shared files:** none from §4. Publishes `trade.v{n+1}` (`price.*`, `spread.*`, `orderStepUnits`).
- **Notes:** property tests **print** the number of generated cases and never assert it (DESIGN-GATE §3 rule 7). `imbalanceMilli`'s clamp is a bounded ratio and its comment must say so (caps rule).

### [ ] 18a.5 `exchange-invariants` — scaffold half (generators, I3 pricing, I5, the guard script)
- **Spec:** docs/architecture/trade-network/exchange/spec-exchange-invariants.md (§5 *Wave 1 (scaffold)* — the spec is three landings, 18a.5 / 18c.4 / 18d.1)
- **Wave:** row 18a · no flag, no bump (R3: tests and a guard script only)
- **Depends on:** 18a.4, row 0a (`synthetic-graph`, the seeded world builder)
- **Acceptance:** (1) I3's pricing half and I5 hold over the generated space at this wave's scope, each failure printing the seed and a minimal counterexample; (2) no assertion names a count of goods, hubs, orders, factions, turns or cases — runs print them; (3) every rule in §4 has a row in `gk-core/scripts/enforcement-registry.v1.json` naming `trade-invariants`, and the registry meta-test passes.
- **Verify:** `.\scripts\verify-change.ps1 -Paths tests/FusionRpg.Core.Tests/World/Trade/Invariants/ExchangeInvariantTests.cs,scripts/guard-trade-invariants.ps1,gk-core/scripts/enforcement-registry.v1.json,scripts/run-guards.ps1,gk-core/scripts/verification-boundaries.v1.json -Session <session>`
- **Shared files:** none from §4.
- **Notes:** `scripts/guard-trade-invariants.ps1` is a **new unmapped path** — add its owner boundary row in this commit or `verify-change.ps1:118` throws. The broken fixtures of acceptance 4 that this half can already prove (a walk priced at the step's starting stock, a `System.Random` under `World/Trade/`) live in the test project, never in `src/`.

---

## Row 18b — `exchange` W2 (the hub on the map, and derived access)

Flag **`trade.exchange`**, registered by `exchange-hub`, granting only what this sub-wave ships — a hub
clears, a consignment is written, tiers read. **One bump: N+18.**

### [ ] 18b.1 `exchange-hub` — the trade hub as a structure, its clearing capacity and consignments
- **Spec:** docs/architecture/trade-network/exchange/spec-exchange-hub.md
- **Wave:** row 18b · flag `trade.exchange` (**this task registers it**) · bump **N+18**
- **Depends on:** 18a.3 (tier tables), row 0a (`world-stamp`, `stock-deltas` owner dimension E-A8), row 0d (`sector-features`), row 0c (`trade-structure-rows` — the `Feature`-kind rows and `requiredSlotKinds`), row 1 (`warehouse-axis`, `essence-loop-read`, `located-stock`), X-11 (multi-slot `BuildResolver`), row 13 (`fleet` `crew` — soft: `staffingMilli` reads 1000 until it lands)
- **Acceptance:** (4) a row with `FeatureUnlock == trade` and `ClearingValuePerTurn ≤ 0`, or any other row with it `≠ 0`, is a load rejection naming the row, and no row carries a `StructureKind.Exchange` (round 6 C2 — the member does not exist); (6) a world without `trade.exchange` never clears, never writes a consignment and replays byte-identically; (13)+(14) at a sector scale from `Θ` = 10,000 with tier 4, the Market bonus and full staffing, `ClearingCapacity` returns the exact `BigInteger`-computed value and throws rather than wraps past `long.MaxValue`, and applying the same consignment deltas in two orders gives byte-identical canonical text and the same `StateHash`.
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Trade/Hub/Hubs.cs,gk-core/src/FusionRpg.Core/World/StructureCatalog.cs,gk-core/src/FusionRpg.Core/World/WorldState.cs,gk-core/src/FusionRpg.Core/World/WorldCanonical.cs,gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs,tests/FusionRpg.Core.Tests/World/Trade/Hub/ExchangeHubTests.cs,gk-core/scripts/verification-boundaries.v1.json -Session <session>`
- **Shared files:** `TurnEngine.cs` — the **one** `RulesetVersion` bump for row 18b, rebased onto the latest constant at landing (§4, R4: never a pre-assigned literal). `WorldState.cs` — `WorldSector.Consignments`, additive. `WorldCanonical.cs` — one conditional row for consignments, appended **after the last conditional row present at landing** (§4 names `carried-goods`, row 12, as the last fixed slot); this task is the family's next appender and takes the slot alone; §4's sparse-row clause names the consignment row (R-11), and because it is sparse it moves no existing hash.
- **Notes:** owns golden re-bless point 1 for this wave (§6: fixtures and Data tests that build a world at the live `RulesetVersion` and then grant `trade.exchange`) — re-blessed **in this commit**, never batched with 18c. `StructureDef.RequiredSlotKinds` and the `BuildResolver`/`WorldValidation` membership arms are **X-11's**, not this task's (landing-order §7 puts them before row 0c); spec §3 still says this module lands them, and the landing order overrides it (§7's X-11 row). `SlotTypeCatalog.cs` is world-map's: the C4 slot rename is ask X-14, not an edit here.

### [ ] 18b.2 `trade-access` — `Access`, the tariff, the passage bit
- **Spec:** docs/architecture/trade-network/exchange/spec-trade-access.md
- **Wave:** row 18b · flag `trade.exchange` (registered by 18b.1; this task ships under it) · bump N+18 (shared, R2)
- **Depends on:** 18a.3, 18b.1, row 15 (`diplomacy-facts`), row 16 (`diplomatic-stance`, `relation-facts` band snapshot), row 17 (`conquest-consequences` — `Collapse.IsCollapsed`)
- **Acceptance:** (3) lowering the band below a treaty's lowest band lowers `Access` the same turn and restoring it restores `Access`, with **no** diplomacy fact written either way, asserted on the fact list; (5) for every grantor and turn, every `preferential` tariff ≤ every tariff that grantor charges any non-bloc requester, over generated fact sequences; (7)+(12) `PassageBit` changes for a pair iff its diplomatic `Level` crosses `passage` — tested for every trigger in §4's table including the band-only change and a faction collapse (the key-set edge) — and building or razing a hub never changes it.
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Diplomacy/Access/TradeAccess.cs,tests/FusionRpg.Core.Tests/World/Diplomacy/Access/TradeAccessTests.cs,data/tuning/diplomacy.v{n+1}.json,gk-core/scripts/verification-boundaries.v1.json -Session <session>`
- **Shared files:** none from §4. Publishes `diplomacy.v{n+1}` (`treaty.{kind}.tariffBandMilli`, `tariff.marketDefaultMilli`) on the file **15.3** created (R-3).
- **Notes:** **registration seam, edge 4** (landing-order §3): this task registers `PassageBit` into `counterparties` `diplomatic-stance`'s `IPassageRule` seam, which already carries the logged band snapshot (round 5 X14) — `counterparties` never depends on `exchange`. Acceptance 8 (no `AccessLevel` field on `WorldState`) owes a source-scan guard row in `gk-core/scripts/enforcement-registry.v1.json`. DESIGN-GATE §2.16 applies through `logistics-flow` `path-cache`'s key, not to a cache here: §4's trigger table is the enumeration, and each trigger has its own test.

---

## Row 18c — `exchange` W3 (orders, settlement, treaties)

**Two capability rows sharing this sub-wave's one bump** (R2; family row 15 is the precedent):
**`trade.exchangeOrders`** (registered by `order-book`, gating `order-set` admission and settlement writes)
and **`trade.diplomacy`** (registered by `treaty-lifecycle`, which implies `counterparties.diplomacy`, global
audit m11). **One bump: N+19.** The new id exists because R1 forbids a flag spanning waves and
`trade.exchange` is registered in 18b (reconciliation **R-5**); 18b and 18c are deliberately not merged.

### [ ] 18c.1 `order-book` — `order-set`, the exchange pass, the aggregate walk, pro rata
- **Spec:** docs/architecture/trade-network/exchange/spec-order-book.md
- **Wave:** row 18c · flag **`trade.exchangeOrders`** (**this task registers it**) — a third exchange flag confirmed by reconciliation R-5, because `trade.exchange` is wave 18b's and a flag never spans waves (R1); 18b and 18c are deliberately **not** merged · bump **N+19**
- **Depends on:** 18a.2, 18a.4, 18b.1, 18b.2, row 5 (`logistics-phase` — the pass runs at row **A1**, after every flow step L0–L8), row 15 (`need-vector` `DemandAt`/`ReserveAt` per sector, ask E-A10), row 8 (`banking-fact` — soft: without the Treasury hold a hub at a bank point sells nothing)
- **Acceptance:** (1) permuting the command list, the `CommandId`s or the filing commanders leaves every fill and value identical (shuffled, seeded); (2) replacing one commander's order with k orders of equal total at the same key gives the same fills and values; (10)+(11) the same world under two `CultureInfo.CurrentCulture` settings gives identical fills and the same `StateHash`, and a pro-rata split and a capacity scaling at a goods magnitude from `Θ` = 10⁶ match an independent `BigInteger` computation without throwing.
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Trade/Orders/ExchangePass.cs,gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs,gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs,gk-core/src/FusionRpg.Core/World/WorldState.cs,gk-core/src/FusionRpg.Core/World/WorldCanonical.cs,gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs,gk-core/src/FusionRpg.Contracts/WorldDtos.cs,gk-core/src/FusionRpg.Server/WorldEndpoints.cs,tests/FusionRpg.Core.Tests/World/Trade/Orders/OrderBookTests.cs,gk-core/scripts/verification-boundaries.v1.json -Session <session>`
- **Shared files:** `WorldCommand.cs` — the `order-set` kind, with its `WorldCommandAdmission` arm in the same change (§4). `WorldState.cs` — `TradeOrders`, additive. `WorldCanonical.cs` — one conditional row for `TradeOrders`, in the slot after 18b.1's consignment row (§4: one module at a time appends). `TurnEngine.cs` — row 18c's one bump, rebased at landing.
- **Notes:** wires the `tradeable-goods` admission refusals 18a.2 could not test (`order.good-never-trades:{id}`, `order.souls-payment-only`) and asserts them here. Crosses Core, Contracts and Server: run the focused boundaries `verify-change.ps1` selects plus `gk-core/tests/FusionRpg.Guard.Tests/WorldDeterminismGuardTests.cs`; the **full** suite runs once at the end of row 18c with 18c.2 (AGENTS.md verification point 2), not per task. `OpenBuyDemandAt` is a pure projection and may land now; the Treasury hold it feeds waits on row 8 (round 6 C3).

### [ ] 18c.2 `settlement-payment` — barter, the soul budget, fees, tariffs, the ledger rows
- **Spec:** docs/architecture/trade-network/exchange/spec-settlement-payment.md
- **Wave:** row 18c · flag `trade.exchangeOrders` (registered by 18c.1) · bump N+19 (shared, R2)
- **Depends on:** 18c.1, 18a.1, 18a.2, 18b.1, 18b.2, row 0a (`ledger-keys`, `world-stock-ledger`, `stock-deltas` owner dimension E-A8), row 16 (`relation-facts` — the one per-turn logged-input record, ask E-A7)
- **Acceptance:** (1) I1 — every trade soul-ledger row has `delta ≤ 0`, Σ souls leaving each player = Σ destroyed, no non-player faction ever has a budget; (2) I2 — a source scan finds no wallet, material or treasury writer under `src/FusionRpg.Core/World/Trade/Settlement/`, no fill pairs pools, and `loam`/`recruit` appear in no record; (9)+(10) each party receives at most `r`‰ of what it was promised where `r` is its own delivered share (no accept-then-default gain), and a turn with several traders plus an order and a deal leg at one hub and good writes exactly **one** row per ledger key holding the sum, with a re-commit writing nothing.
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Trade/Settlement/Settlement.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Souls.cs,gk-core/src/FusionRpg.Core/Creatures/SoulEarnPolicy.cs,tests/FusionRpg.Core.Tests/World/Trade/Settlement/SettlementTests.cs,tests/FusionRpg.Data.Tests/World/SettlementCommitTests.cs,gk-core/scripts/verification-boundaries.v1.json -Session <session>` plus `.\scripts\guard-dal.ps1`; then the **full** suite once, closing row 18c with 18c.1.
- **Shared files:** `RpgStore.WorldTurns.cs` — the commit-side soul spend and the logged soul budget, additive after `Step` and the diff (§4: ledger tables first, then per-wave packed rows in §2 order).
- **Notes:** Data tests run **in memory** (test-substrate hard rule; `guard-test-substrate.py`). `SoulEarnPolicy.Reasons` gains `trade` — a reviewed widening of the creature program's closed list. Round 6 C3: settlement itself does **not** wait on the save-identity re-key (it writes located stock and consignments only); the four waiting paths are named in spec §4 and each states its interim. Round 6 CQ2 adds no settlement path — the banked draw is `legion-build`'s, so invariant I2's source scan is unchanged.

### [ ] 18c.3 `treaty-lifecycle` — the eight diplomacy verbs, terms, blocs, the war-break fact
- **Spec:** docs/architecture/trade-network/exchange/spec-treaty-lifecycle.md
- **Wave:** row 18c · flag **`trade.diplomacy`** (**this task registers it**; `trade.diplomacy` ⇒ `counterparties.diplomacy`, validated by `world-stamp` at registration) · bump N+19 (shared with 18c.1/18c.2, R2)
- **Depends on:** 18a.3, 18b.2, 18c.2 (§7 deal legs settle there), row 15 (`diplomacy-facts` append API and the `TariffMilli?`/`Deal` field, ask E-A13; `counterparties.diplomacy`), row 16 (`diplomatic-stance` — peace, `treaty.imposed`, `IsLockedWar`, `TargetFactionId`)
- **Acceptance:** (2) ending at or after the minimum term writes `treaty.ended` and before it `treaty.broken`, **and** a `war-declare` writes one `treaty.broken` per live treaty still inside its term (breaker = the declarer) — a test asserts an early `treaty-end` and a war declaration at the same turn move the same bands for partner and observers, so war is never the cheaper exit (round 6 Q-A); (5) a `treaty-propose` and a `war-declare` for one pair filed in one turn produce the same facts in **either** filing order; (9) each §3a building gate refuses at admission with its named reason when absent and admits when present, accepting needs no building, and losing an Embassy after signing changes no fact and no `Level`.
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Diplomacy/TreatyLifecycle.cs,gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs,gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs,gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs,gk-core/src/FusionRpg.Contracts/WorldDtos.cs,data/tuning/diplomacy.v{n+1}.json,tests/FusionRpg.Core.Tests/World/Diplomacy/Lifecycle/TreatyLifecycleTests.cs -Session <session>`
- **Shared files:** `WorldCommand.cs` — eight kinds (`treaty-propose`, `treaty-respond`, `treaty-end`, `embargo-set`, `embargo-lift`, `bloc-propose`, `bloc-join`, `bloc-leave`), each with its `WorldCommandAdmission` arm in the same change (§4). `TurnEngine.cs` — resolution in Snapshot; no new phase. Publishes `diplomacy.v{n+1}` (`treaty.minimumTermTurns`, `truceTurns`, `treaty.{kind}.defaultTariffMilli`).
- **Notes:** owns golden re-bless point 1 for row 18c (§6), re-blessed in this change. `spec-ai-commander.md:284`'s *"no diplomacy"* amendment is `counterparties`' ask A5 — this task depends on it, it does not make it. The band check runs at **resolution**, not admission (admission has no band; it arrives as the logged snapshot, CM1).

### [ ] 18c.4 `exchange-invariants` — settlement half (I1, I2, I3 settlement, I4)
- **Spec:** docs/architecture/trade-network/exchange/spec-exchange-invariants.md §5 *Wave 3*
- **Wave:** row 18c · no flag, no bump (R3: the suite asserts, it never grants)
- **Depends on:** 18a.5, 18c.1, 18c.2
- **Acceptance:** (1) I1, I2, I3's settlement half and I4 hold over the generated space, each failure printing the seed and a minimal counterexample; (4) the broken fixtures fail their invariant — a settlement crediting one soul (I1), a fill pairing rubble with essence (I2), a sell of goods bought in the same pass (I4), and a deal whose legs settle independently so a defaulter still receives its counter-leg; (5) I4's closed-cycle check includes deal legs — a cycle mixing an order round trip and a deal leg at one hub still costs the player strictly positive souls or leaves a `(good, location)` balance changed.
- **Verify:** `.\scripts\verify-change.ps1 -Paths tests/FusionRpg.Core.Tests/World/Trade/Invariants/ExchangeInvariantTests.cs,scripts/guard-trade-invariants.ps1,gk-core/scripts/enforcement-registry.v1.json -Session <session>`
- **Shared files:** none from §4.
- **Notes:** the **required amendment** to `trade-network-ideal.md` §7.7 and `trade-network-map.md` §5 invariant 3 — the corrected closed-cycle rule, *"every good returns to every location it started at"* (EC1, F-X1) — lands in this commit, not the 18d one, because this is where I4 first runs.

---

## Row 18d — `exchange` W4 (the invariant suite over treaties and many-empire worlds)

**No flag, no bump** (R3: tests only).

### [ ] 18d.1 `exchange-invariants` — complete (treaties, blocs, many-empire worlds)
- **Spec:** docs/architecture/trade-network/exchange/spec-exchange-invariants.md §5 *Wave 4*
- **Wave:** row 18d · no flag, no bump (R3)
- **Depends on:** 18c.3, 18c.4, row 16 (`clan-seeding` — generated clans), row 17 (`clan-economy`)
- **Acceptance:** (1) I1–I5 hold over the full generated space: worlds with hubs at every Trade tier, factions with and without an Embassy, generated treaty and bloc sequences, and many-empire worlds; (2) no assertion names a count of goods, hubs, orders, factions, turns or cases; (3) every rule in §4 has a registry row naming `trade-invariants` and the meta-test passes.
- **Verify:** `.\scripts\verify-change.ps1 -Paths tests/FusionRpg.Core.Tests/World/Trade/Invariants/ExchangeInvariantTests.cs,gk-core/scripts/enforcement-registry.v1.json -Session <session>`; this is the last task of row 18, so also run the **full** suite (AGENTS.md verification point 1, finishing a large feature).
- **Shared files:** none from §4.
- **Notes:** no golden re-bless is owed here — a golden that moves in this task is a defect to diagnose, not a re-bless (§6's closing sentence).

---

## Row 19a — `trade-ai` W1 (belief, valuation, the two bounds)

Flag **`trade.intel`**, registered by `trade-intel`, with this sub-wave's one bump, **N+20**. `ai-spend-limit`
and `deal-valuation` register nothing and take no bump (R3: policies run outside `Step`; replay never re-runs
one, `gk-core/tests/FusionRpg.Data.Tests/WorldAiCommitTests.cs:136`). The flag and bump exist because `trade-intel`
writes hashed belief inside `Step` and appends conditional canonical rows (reconciliation **R-6**).

**The landing order inside this sub-wave is 19a.1 → 19a.3 → 19a.2**, because reconciliation **R-4** moved the
`gk-core/data/tuning/ai.v3.json` creator to `ai-spend-limit` and `publish.py` can only bump a file that exists. The
task ids are the fragments' and are deliberately **not** renumbered — read the order, not the numbers.

### [ ] 19a.1 `trade-intel` — remembered quotes and flows as faction belief
- **Spec:** docs/architecture/trade-network/trade-ai/spec-trade-intel.md
- **Wave:** row 19a · flag **`trade.intel`** (**this task registers it**) · bump **N+20** — confirmed by reconciliation R-6; `landing-order.md`'s old *"none expected"* for row 19 and `trade-ai-map.md:606`'s *"no `RulesetVersion` bump at all"* are both withdrawn
- **Depends on:** 18a.1 (`ValueOf`), 18a.4 (the pure quote), 18b.2 (`Access` for the `market`-sight rule), row 0a (`world-stamp`), row 0d (`sector-features` for `OwnFeatureTier`), row 6 (`lane-flow`, `logistics-canonical`), row 12 (`fleet` `depot` `ForeignSite.Of` for `BelievedAcceptsCaravans`), ask T-A11 (`RememberedSlot.StructureTier`, world-map `intel`)
- **Acceptance:** (1) a faction never holds a quote for a hub it had neither `Full` sight of nor `market` access to, and no flow row for a lane neither end of which it has seen; (3) after a glimpse of a sector whose quotes were last read on turn *t*, every quote's `SeenTurn` is still *t* (the `Merge` trap, TC8); (5) a world with no hubs and no flows produces byte-identical canonical text to the pre-module engine and a legacy-stamped world records nothing new.
- **Verify:** `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/World/Intel/FactionIntel.cs,gk-core/src/FusionRpg.Core/World/Intel/IntelRecorder.cs,gk-core/src/FusionRpg.Core/World/Intel/IWorldView.cs,gk-core/src/FusionRpg.Core/World/WorldCanonical.cs,gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs,data/tuning/trade.v1.json,tests/FusionRpg.Core.Tests/World/Intel/TradeIntelTests.cs,gk-core/scripts/verification-boundaries.v1.json -Session <session>`
- **Shared files:** `WorldCanonical.cs` — two conditional row kinds (`intel-quote`, `intel-flow`) written after the existing intel rows, in the slot after 18c.1's `TradeOrders` row (§4: one module at a time appends hashed rows). `TurnEngine.cs` — row 19a's one bump, rebased onto the live constant at landing (R4). §4's sparse-row clause names both row kinds (R-11); both are sparse, so a world with no hubs and no flows writes neither. `World/Intel/**` today resolves only to `core-fallback`; the focused boundary row lands here.
- **Notes:** `intel.quoteBandEdgesMilli` / `intel.flowBandEdges` are **step-read**, so they belong in `trade.v{n+1}.json`, not `ai.v3.json` (spec §Hard edges; round 6 M8). The spec's own §Hard edges says *"Whether this rides a `RulesetVersion` bump is `world-stamp`'s rule … not decided here"* — that is the open question the flag above answers. **R-6 closed it:** the flag and the bump are the landing order's now (§2 row 19a), §4's `WorldCanonical` sparse-row clause names the two row kinds, and `trade-ai-map.md:606` was corrected in the same pass.

### [ ] 19a.3 `ai-spend-limit` — the exposure limit and the honest order bound
- **Spec:** docs/architecture/trade-network/trade-ai/spec-ai-spend-limit.md
- **Wave:** row 19a · no flag, no bump (R3: a policy-side limit plus a guard in the commit fill; the fill writes commands, not state)
- **Depends on:** 18c.1 (`order-set` for `AiPolicyOrderKinds`), 18c.3 (the eight treaty kinds), row 7 (`route-set`/`route-clear`/`bank-hold`), row 15 (`trade-difficulty-knobs`, `empire-treasury`), row 16 (`diplomatic-stance` war/peace kinds), row 8 (`banking-fact` — the income read, inert until then)
- **Acceptance:** (2) a policy filing `ownEntities + 1` ordinary orders and `policyBound` policy orders commits, while one more of either, or two policy orders sharing one key, throws inside the commit and leaves the world exactly where it was; (3) adding enemy legions to a world does not change how many orders a faction may file (the TC1 regression); (5) every entity-less command kind is in `AiPolicyOrderKinds` and every member of it exists in `WorldCommandKinds.All`.
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Ai/Trade/AiPolicyOrderKinds.cs,gk-core/data/tuning/ai.v3.json,gk-core/src/FusionRpg.Server/Program.cs,src/FusionRpg.Core/World/Ai/Trade/SpendLimit.cs,gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs,tests/FusionRpg.Core.Tests/World/Ai/Trade/SpendLimitTests.cs,gk-core/tests/FusionRpg.Data.Tests/WorldAiCommitTests.cs,tests/FusionRpg.Guard.Tests/AiPolicyOrderKindsTests.cs,gk-core/scripts/verification-boundaries.v1.json -Session <session>`; crosses Core and Data together, so the **full** suite runs once at the end of this task (AGENTS.md verification point 2).
- **Shared files:** `RpgStore.WorldTurns.cs` — replaces the bound at `:252-255` in place and keeps the two-orders-per-entity check at `:270-272` unchanged.
- **Notes:** both bounds are **structural per-turn rates** and their comments must say so (caps rule); the policy bound is `base + per-own-sector`, never flat (a flat bound facing scaling holdings is a hidden ceiling, PS-8). The limit **binds the AI only and says so** (umbrella invariant 11). Round 6 C3: the income read is *"what its treasury banked last turn"*, so the limit is inert until row 8 — the stated behaviour is *"an AI that banked nothing files no buys; it can still sell"*, not a second income source. **This task creates `gk-core/data/tuning/ai.v3.json`, its loader and the loader switch** (`gk-core/src/FusionRpg.Server/Program.cs:234` names the file literally) — settled by reconciliation R-4, restoring what this module's own spec `:188-191` and `trade-ai-map.md:387-390`/`:614` always claimed. It therefore lands **before** 19a.2 inside wave 19a, and `deal-valuation`, `counter-offer-articles`, `ai-bidding`, `ai-treaty-policy`, `ai-logistics`, `ai-trade-buildings` and `interdiction` all publish `v{n+1}` and claim no switch. Adds the boundary rows `data-world-ai-fill`, `core-world-ai-trade` and, if 18a.1 did not, the `gk-core/data/tuning/**` row (X-18).

### [ ] 19a.2 `deal-valuation` — the one deal function and the one acceptance rule
- **Spec:** docs/architecture/trade-network/trade-ai/spec-deal-valuation.md
- **Wave:** row 19a · no flag, no bump (R3: valuation runs outside `Step`)
- **Depends on:** 19a.1, **19a.3** (the creator of `gk-core/data/tuning/ai.v3.json` and its loader switch — R-4; this task lands **after** it inside wave 19a), 18a.1 (`ValueOf`, `ValueForSouls`), 18a.3 (lowest bands, tier tables, refusal codes), 18b.1 (`TradeTier`), 18b.2 (`LevelAt`, `EffectiveLevel`), row 15 (`need-vector`, `empire-roster` personality), row 16 (`relation-facts` band snapshot), ask T-A10 (`legion-power` through the view — wave **L4** now has a row in the family order, R-13; soft: today's stack count until the view ask lands)
- **Acceptance:** (1) a source scan finds exactly **one** `DealValue` body, and `ai-bidding`, `ai-treaty-policy`, `ai-logistics`, `counter-offer-articles` and `clan-behaviour` contain no valuation arithmetic of their own; (6) for every generated deal, `DealValue(d) + DealValue(mirror(d))` valued from the state after `d` is `≤ 0`, and with every `acceptMilli ≥ 1` a deal and its mirror are never both accepted; (7) a deal whose kind the pair's band does not reach returns `Band` without calling the need vector, asserted with a throwing need-vector fake.
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Ai/Trade/DealValuation.cs,data/tuning/ai.v{n+1}.json,data/tuning/diplomacy.v{n+1}.json,gk-core/src/FusionRpg.Server/Program.cs,tests/FusionRpg.Core.Tests/World/Ai/Trade/DealValuationTests.cs,tests/FusionRpg.Guard.Tests/DealValuationScanTests.cs,gk-core/scripts/verification-boundaries.v1.json -Session <session>`
- **Shared files:** none from §4.
- **Notes:** **this task publishes `data/tuning/ai.v{n+1}.json` and carries no loader switch.** Reconciliation R-4 settled the creator as `ai-spend-limit` (19a.3) — which is what its own spec `:188-191` and `trade-ai-map.md:387-390`/`:614` always said, and which this spec had already conceded; `landing-order.md §5` was the stale line and was fixed there rather than in four other documents. `interdiction` (19e.1) likewise publishes `v{n+1}` (audit M8). `acceptMilli.{eager,open,wary}` is this module's key, published as `diplomacy.v{n+1}` on the file **15.3** created (`hostile` dropped: round 4 blocks every deal there). Adds the focused boundary `core-world-ai-trade`, and the `gk-core/data/tuning/**` owner row (X-18) if 18a.1 did not.

---

## Row 19b — `trade-ai` W2 (the counter walk and the hub plan)

**No flag, no bump** (R3: both modules are policies outside `Step`).

### [ ] 19b.1 `counter-offer-articles` — the fixed walk order and the refusal terms
- **Spec:** docs/architecture/trade-network/trade-ai/spec-counter-offer-articles.md
- **Wave:** row 19b · no flag, no bump (R3)
- **Depends on:** 19a.2, 18a.3 (the nine article kinds and five refusal codes — the vocabulary is `exchange`'s, TC4), 18c.3 (the `treaty-respond` payload that carries `RefusalTerms`, ask T-A5)
- **Acceptance:** (1) a counter differs from its proposal by a sequence of articles from the walk order, of length ≤ `trade.counterStepBound`; (3) every refusal names its code's subject — a band, a building and tier, the vocabulary rule, or a positive shortfall — and a refusal with none fails; (5)+(6) a counter is never produced when the proposer's value of it from the responder's belief is negative, and a counter to a counter is always accept or decline.
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Ai/Trade/CounterOffer.cs,gk-core/data/tuning/ai.v3.json,tests/FusionRpg.Core.Tests/World/Ai/Trade/CounterOfferTests.cs,gk-core/tests/FusionRpg.Data.Tests/WorldAiCommitTests.cs -Session <session>`
- **Shared files:** none from §4. Publishes `ai.v{n+1}` (`trade.counterStepBound`, a structural loop bound, commented).
- **Notes:** owes a registry row for *"no solver"* — a scan under `src/FusionRpg.Core/World/Ai/Trade/` for any search over deals (spec checklist's open box).

### [ ] 19b.2 `ai-bidding` — standing orders per hub, paired so they can settle
- **Spec:** docs/architecture/trade-network/trade-ai/spec-ai-bidding.md
- **Wave:** row 19b · no flag, no bump (R3)
- **Depends on:** 19a.1, 19a.2, 19a.3, 18c.1 (`order-set`, `LimitMilli`, `OwnTradeOrders`), 18c.2 (the barter/pool rule its §2a pairs against), row 15 (`need-vector` want, demand, `needs.reserveTurns`)
- **Acceptance:** (1)+(1a) no sell is filed for a good below its reserve, and every sell is at a hub where the AI files a buy in the same credit pool the same turn for goods in its consignment there or routed there — so a filed pair fills rather than stranding as `order.sell-no-counter-leg`; (3) every buy's limit ≤ the reservation and every sell's limit ≥ it; (7)+(8) given a stale believed quote below the true price the filed order either does not fill or fills at ≤ its limit (integration against `exchange`'s book), and with unchanged needs, quotes and access the AI files zero `order-set` commands on the second turn.
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Ai/Trade/AiBidding.cs,gk-core/data/tuning/ai.v3.json,tests/FusionRpg.Core.Tests/World/Ai/Trade/AiBiddingTests.cs,tests/FusionRpg.Core.Tests/World/Trade/AiBiddingBookIntegrationTests.cs,gk-core/tests/FusionRpg.Data.Tests/WorldAiCommitTests.cs -Session <session>`
- **Shared files:** none from §4. Publishes `ai.v{n+1}` (`trade.orderRefileSteps`).
- **Notes:** `difficulty.<profileId>.aiBidAggressionMilli` is **`counterparties`'** key and is policy-only, so its home is `ai.v3.json` — ask T-A13. Until that move lands this task reads whichever file publishes it and **duplicates no key** (one home, never two). Owes a registry row for criterion 10 (no `WorldFactionKind` branch in this module).

---

## Row 19c — `trade-ai` W3 (diplomacy and logistics decisions)

**No flag, no bump** (R3).

### [ ] 19c.1 `ai-treaty-policy` — one diplomacy move per pair per turn, and the composed policy
- **Spec:** docs/architecture/trade-network/trade-ai/spec-ai-treaty-policy.md
- **Wave:** row 19c · no flag, no bump (R3)
- **Depends on:** 19a.2, 19a.3, 19b.1, 18c.3 (the treaty, embargo and bloc commands; pending offers through `OwnOpenOffers`), row 16 (`diplomatic-stance` — war/peace commands, `IsLockedWar`), row 15 (`empire-roster` personality rows)
- **Acceptance:** (1)+(2) at most one diplomacy command per counterparty (and one bloc command) per faction per turn over a 20-turn run, and the AI never accepts a deal `Accepts` refuses nor declines one it accepts except with code `Band` or an at-war reason; (3) replaying a stored log with a different treaty policy registered leaves every hash unchanged; (11) zero `*.needs-building:*` refusals of AI commands over the run, nothing is ever filed on the `IsLockedWar` pair, and the dominant enemy empire does sign with a rival in a scripted fixture (round 4 Q4).
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Ai/Trade/AiTreatyPolicy.cs,gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs,gk-core/src/FusionRpg.Core/World/Ai/FactionPolicies.cs,gk-core/data/tuning/ai.v3.json,tests/FusionRpg.Core.Tests/World/Ai/Trade/TreatyPolicyTests.cs,gk-core/tests/FusionRpg.Data.Tests/WorldAiCommitTests.cs -Session <session>`; `FrontierRulesPolicy.cs` changes, so the **full** suite runs once at the end of this task, and `TwoHearthsCampaignTests.cs` plus the AI acceptance scenario are run and **reported**.
- **Shared files:** none from §4, but `FrontierRulesPolicy.cs` is shared inside row 19 by 19c.1, 19d.1, 19e.1 and 19e.2 — the task order here is its landing order, and each change must keep a no-trade world's orders byte-identical (criterion 5).
- **Notes:** this task establishes the composed layer order — `ai-trade-buildings` → `ai-logistics` → `ai-bidding` → `ai-treaty-policy` (§1) — so 19d.1 and 19c.2 slot into a list that already exists. Round 6 Q-A: the **War** step subtracts the same `trade.valuation.treatyBrokenWeightMilli` cost the **End** step pays, so no policy scores better by declaring war than by ending a treaty. Personality never moves the acceptance threshold (that would be a second acceptance rule). Publishes `ai.v{n+1}` (`trade.diplomacy.*`).

### [ ] 19c.2 `ai-logistics` — routes, caravans and escorts from idle legions only
- **Spec:** docs/architecture/trade-network/trade-ai/spec-ai-logistics.md
- **Wave:** row 19c · no flag, no bump (R3)
- **Depends on:** 19a.1 (`OwnFlows`), 19a.2, 19a.3, 19b.2 (the sell plan), row 7 (`auto-banking` — `route-set`/`route-clear`), row 12 (`fleet` `depot` `ForeignSite.Of`), row 13 (`fleet` `trade-route-order`), wave **L2** (`legion-build` `standing-orders`) and wave **L4** (`escort-stance`) — both rows in the family order since R-13
- **Acceptance:** (1)+(5) one order per entity over a 20-turn trade run, and a legion on a standing order receives no ladder order; (3) a route whose default path is cut is redirected or cleared within one turn of the cut entering the AI's view; (7)+(9) a source scan under `World/Ai/Trade/` finds no `ReconnectionCost` and no path search, and an escort assigned before or after its caravan's order gives the same first escorted turn (both filing orders tested — the key-set edge is the caravan acquiring its order, DESIGN-GATE §2.16).
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Ai/Trade/AiLogistics.cs,gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs,gk-core/data/tuning/ai.v3.json,tests/FusionRpg.Core.Tests/World/Ai/Trade/AiLogisticsTests.cs,gk-core/tests/FusionRpg.Core.Tests/World/Ai/FrontierRulesTests.cs -Session <session>` plus the widened routing guard (ask T-A4); full suite once at task end; campaign tests run and reported.
- **Shared files:** `FrontierRulesPolicy.cs` (the standing-order skip in the entity walk) — see 19c.1's note.
- **Notes:** **schedulable now.** `legion-build` `standing-orders` lands in wave **L2** and `escort-stance` in wave **L4**, both rows in `landing-order.md` §2 since reconciliation R-13, so this task sits after L4. What remains is ask **T-A2** (`trade-ai` audit A-X2: a legion on a trade standing order must be identifiable from state) — a contract on `standing-orders`, not a scheduling unknown. `trade.caravanShareMilli` is a structural share and its comment must say so.

---

## Row 19d — `trade-ai` W4 (the AI builds what its own plans need)

**No flag, no bump** (R3).

### [ ] 19d.1 `ai-trade-buildings` — `build` and upgrade from blocked plans, one valuation
- **Spec:** docs/architecture/trade-network/trade-ai/spec-ai-trade-buildings.md
- **Wave:** row 19d · no flag, no bump (R3)
- **Depends on:** 19b.2, 19c.1, 19c.2 (all three report the blocked-plan payoffs), 18b.1 (`TradeTier`), 18b.2 (`LevelAt`), row 0d (`sector-features` — `FactionTier` and the upgrade arm of `build`), X-11 (multi-slot `BuildResolver`, for `requiredSlotKinds` candidates), ask T-A10 (`legion-power`, wave **L4** — soft: today's stack count until the view ask lands)
- **Acceptance:** (1) over a 20-turn run every `build` this layer files is admitted and resolves — no `build.elsewhere`, `build.occupied`, `build.wrong-slot-kind` or loam drop; (2)+(3) one order per entity holds, at most `max(1, floor(idle × idleShareMilli / 1000))` builds per faction per turn, doubling a fixture empire's idle legions never lowers that bound, and no building is filed whose payoff is zero; (9) a source scan finds no power-roll-up value used outside a consideration input in `World/Ai/Trade/` — no strength term reaches any resolution.
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Ai/Trade/AiTradeBuildings.cs,gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs,gk-core/data/tuning/ai.v3.json,tests/FusionRpg.Core.Tests/World/Ai/Trade/TradeBuildingsTests.cs,gk-core/tests/FusionRpg.Data.Tests/WorldAiCommitTests.cs -Session <session>`; full suite once at task end.
- **Shared files:** `FrontierRulesPolicy.cs` (the layer list) — see 19c.1's note.
- **Notes:** `trade.build.idleShareMilli` is a **structural pacing share**, commented (the flat `maxPerTurn = 1` it replaces was an unstated AI handicap — umbrella invariant 11). No loam-to-value conversion: loam enters only as affordability and upkeep considerations. Upgrades are candidates only once `sector-features`' upgrade arm exists; until then tier 1 only. `landing-order.md`'s X-2 row no longer lists this module: reconciliation **R-9** narrowed the power-ladder contest blocker to row 23 and `world-warden`'s defence term only, because this spec reads the roll-up **to choose**, never as a contest term, and states a default (today's stack count). X-2 gates a quality improvement here, not the landing.

---

## Row 19e — `trade-ai` W5 (interdiction and the clan brain)

**No flag, no bump** (R3).

### [ ] 19e.1 `interdiction` — a ladder rule that presses believed flows and the leader
- **Spec:** docs/architecture/trade-network/trade-ai/spec-interdiction.md
- **Wave:** row 19e · no flag, no bump (R3)
- **Depends on:** 19a.1 (`BelievedFlows`), 19a.2 (the goods index), row 6 (`lane-loss` — `hostilePresenceMilli`), row 16 (`diplomatic-stance` — stance-aware hostility through `ZoneOfControl.IsHostile`), ask T-A3 (shared anti-Nemesis registry rows with `npc-story-events` `counter-doctrine`)
- **Acceptance:** (1) where `Recover` and `Interdict` would both fire `Recover` wins, and where `Interdict` and `Explore` would both fire `Interdict` wins (owner decision Q1's rule order); (7)+(8) the anti-Nemesis source scan passes — no input keyed by an encounter, battle report, story ledger, character registry or another faction's entity id — and on a world with no flows the policy's orders are byte-identical to the pre-module ladder for the same view; (10) no `move` is filed along a route `SurvivesTheRoute` rejects.
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Ai/Trade/InterdictionTargets.cs,gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs,gk-core/data/tuning/ai.v3.json,tests/FusionRpg.Core.Tests/World/Ai/InterdictionRuleTests.cs,gk-core/tests/FusionRpg.Core.Tests/World/Ai/FrontierRulesTests.cs,gk-core/scripts/enforcement-registry.v1.json -Session <session>`; full suite once at task end; `TwoHearthsCampaignTests.cs` run and reported.
- **Shared files:** `FrontierRulesPolicy.cs` (the `Interdict` rule) — see 19c.1's note.
- **Notes:** the rule-order change is **owner-approved** (trade-ai Q1, 2026-09-19), which is what `spec-ai-commander.md` §Boundaries reserves; that document's own boundary text is amended by ask T-A1, not by this task. Publishes `ai.v{n+1}` (`interdict.shareMilli` — a structural share, commented — `leaderWeightMilli`, `minFlowValue`) and **claims no loader switch** (19a.3 owns it — R-4, audit M8). A campaign golden that moves here is a defect in this change, never a re-bless (criterion 8).

### [ ] 19e.2 `clan-behaviour` — the `clan-keeper` rule subset, and the ladder-list refactor
- **Spec:** docs/architecture/trade-network/trade-ai/spec-clan-behaviour.md
- **Wave:** row 19e · no flag, no bump (R3)
- **Depends on:** 19b.2, 19c.1, 19c.2, row 16 (`clan-seeding` — placement and policy-id assignment), row 17 (`clan-economy` — the income read), row 15 (`need-vector` for computed personality)
- **Acceptance:** (1)+(2)+(9) over a 20-turn run no clan files a `move` leaving its own sectors, no `claim`, no `war-declare` and no `build`; (5) two clans with the same climate, species and state file byte-identical orders up to their own ids, and a source scan finds no clan-id or faction-id literal in the policy; (7) `frontier-rules` produces byte-identical orders before and after the rule-list refactor on every existing AI test scenario.
- **Verify:** `.\scripts\verify-change.ps1 -Paths gk-core/src/FusionRpg.Core/World/Ai/FrontierRulesPolicy.cs,gk-core/src/FusionRpg.Core/World/Ai/FactionPolicies.cs,tests/FusionRpg.Core.Tests/World/Ai/ClanKeeperTests.cs,gk-core/tests/FusionRpg.Core.Tests/World/Ai/FrontierRulesTests.cs,tests/FusionRpg.Core.Tests/World/Ai/WorldAiAcceptanceTests.cs -Session <session>`; this closes row 19, so run the **full** suite (AGENTS.md verification point 1) and report the campaign tests.
- **Shared files:** `FrontierRulesPolicy.cs` — the hard-coded `??` chain becomes a constructed rule list. Spec §Hard edges requires the refactor to land as **its own commit, before** the clan list is added, so a regression bisects to one change: split this task's work into two commits, not two tasks.
- **Notes:** the contract is enforced structurally — by which rules and which diplomacy steps exist in the clan list — never by a zero weight a tuning change could undo. Clans never build, so `ai-trade-buildings` is absent from the clan layer list. Owes a registry row for criterion 5 (no per-clan literal).

---

## CHECKPOINT 6 — Market and AI

**Rows 18 and 19.**

**Pass condition, from the plan §3:** orders clear at a hub, treaties have a lifecycle (war inside a minimum
term writes `treaty.broken`), settlement pays at a bank point, and the AI values deals, spends under a limit
and builds its own trade buildings — drawing banked goods under the same rule the player uses.

---

## PHASE 7 — Cross-world

Landing-order rows **20–23**. 9 tasks.

---

## Row 20 — `rift-trade` W1 (route record, what may cross, the anchor)

One flag, `trade.riftTrade`, registered by 20.1; 20.2 and 20.3 share its bump. The whole row sits **after row
18b** (`exchange`), because the anchor reads the Grand Exchange tier.

### [ ] 20.1 `rift-route` — the save-scoped route record and its per-resolution window
- **Spec:** docs/architecture/trade-network/rift-trade/spec-rift-route.md
- **Wave:** row 20 · flag `trade.riftTrade` (registered here; shared by 20.2 and 20.3) · bump **N+21**, taken here
- **Depends on:** row 0a (`world-stamp`, `ledger-keys`, `system-commands` — the one `FileSystemCommandUnlocked` path), row 0f (`world-continuity` `world-state-vocabulary`, one active world), row 18 (`exchange`)
- **Acceptance:** every admission refusal returns its named reason and writes nothing; an active endpoint's next commit logs exactly one `rift-window` per live route touching it, the other world's log is unchanged, and replaying that world alone reproduces its stored hash with the other absent from the store; a player- or AI-submitted `rift-window` is refused `kind.system-only`, a retried commit logs no second window, and setting two routes from one anchor gives the same windows in either creation order (both tested).
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Data/Sqlite/RpgStore.RiftRoutes.cs','gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs','src/FusionRpg.Core/World/Logistics/Rift/RiftRoute.cs','gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs','gk-core/src/FusionRpg.Server/WorldEndpoints.cs','gk-core/src/FusionRpg.Contracts/WorldDtos.cs','tests/FusionRpg.Data.Tests/RiftRouteStoreTests.cs','tests/FusionRpg.Core.Tests/World/Logistics/Rift/RiftRouteAdmissionTests.cs','tests/FusionRpg.Server.Tests/RiftRouteEndpointTests.cs') -Session <session-id>`
- **Shared files:** `TurnEngine.cs` — row 20's single bump; `WorldCommand.cs` — registers `rift-window` in `system-commands`' closed system-only set (X11), one kind per wave with its admission arm in the same change; `RpgStore.WorldTurns.cs` — one call before the command read, additive.
- **Notes:** `World/Logistics/Rift/**` resolves only to `core-fallback` — the named `core-world-logistics-rift` boundary lands here (audit RA9). Registry rows owed with their tests: `rift-window-system-only`. Owns this wave's flag-granted fixture re-bless (§6 row 1). Store tests run **in memory**. Crosses Core, Data and Server: full suite once at task end.

### [ ] 20.2 `crossing-goods` — the closed table of what may cross
- **Spec:** docs/architecture/trade-network/rift-trade/spec-crossing-goods.md
- **Wave:** row 20 · gates on `trade.riftTrade` (20.1's row) · shares row 20's bump **N+21**, registers no row of its own
- **Depends on:** 20.1, row 1 (`sector-yield` `located-goods-registry`)
- **Acceptance:** `Admit` refuses loam, recruits, wallets, materials, battle budgets and items with their named reasons and admits every located good and both allowed world stocks; an id of a class the table does not list is refused `rift.good-class-unlisted`; the property test finds no path that moves loam or recruits between worlds and none that credits a wallet, material or soul ledger from a rift step, and the source scan fails on any loam or recruit field named under `World/Logistics/Rift/`.
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Core/World/Logistics/Rift/CrossingGoods.cs','tests/FusionRpg.Core.Tests/World/Logistics/Rift/CrossingGoodsTests.cs','tests/FusionRpg.Guard.Tests/RiftCrossingGoodsGuardTests.cs') -Session <session-id>`
- **Shared files:** none from §4.
- **Notes:** round 6 S2/W1 — this table is **the** trade channel between worlds, not one of two: an advance carries no trade goods, and its weight limit (`world.carry.capacity`, units and goods on one limit) is `fleet` `carried-goods`'. Membership is a **closed vocabulary over registry classes** plus the two-member world-stock allow-list, pinned with that reason; no test counts located goods. Registry row owed with its test: `rift-loam-never-crosses`. Round 6 C3: a crossed good banks only through the destination world's own banking step (row 8), so nothing here waits on save identity.

### [ ] 20.3 `crossing-anchor` — a world's end of the crossing
- **Spec:** docs/architecture/trade-network/rift-trade/spec-crossing-anchor.md
- **Wave:** row 20 · gates on `trade.riftTrade` (20.1's row) · shares row 20's bump **N+21**, registers no row of its own
- **Depends on:** 20.1, 20.2, row 13 (`fleet` `crew` `LabourAt`, `depot` `LabourCurve.Eval`), row 18 (`exchange` `Hubs.TradeTier ≥ 4`), row 0d (`sector-features` `TierFor`/`FactionTier`), row 0c (`empire-seed` Rift Anchor row)
- **Acceptance:** `IsWorking` is false with its named reason for a sector not held, no Rift Anchor, an anchor under construction, or a world where the owner holds no working Grand Exchange, and true otherwise; capacity counts only crew bearers on an order naming the anchor's slot, is monotone in them, ignores a caravan building's crew in the same sector, and the site bonus applies exactly when the anchor's sector holds a rift-tear slot; `CrossingWidthLevel` at zero leaves canonical text byte-identical and round-trips non-zero, with one test per far-end-view trigger T1–T5 and T7 against a recomputation from persisted state.
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Core/World/Logistics/Rift/CrossingAnchor.cs','gk-core/src/FusionRpg.Core/World/WorldState.cs','gk-core/src/FusionRpg.Core/World/WorldCanonical.cs','gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs','src/FusionRpg.Data/Sqlite/RpgStore.RiftRoutes.cs','data/tuning/trade.v{n+1}.json','tests/FusionRpg.Core.Tests/World/Logistics/Rift/CrossingAnchorTests.cs','tests/FusionRpg.Data.Tests/RiftAnchorViewTests.cs') -Session <session-id>`
- **Shared files:** `WorldCanonical.cs` — the sparse sector-crossing row, appended after the last conditional row present at landing (§4; after 15.3's and 15.4's); `WorldState.cs` — `WorldSector.CrossingWidthLevel`, additive.
- **Notes:** **registers `IsWorking` into `fleet` `crew`'s `IWorkingSite` predicate registry for `SectorFeature.CrossWorld` in this change** (§3 edge 1 — row 20 registering into row 13, so `crew` never depends upward), and **registers into `world-continuity` `advance-carry`'s post-move hook** rather than being owed a republish call (§3 edge 6, ask A9). Anchor **placement** needs the multi-slot `BuildResolver` arms — ask **X-11**, world-map's (`BuildResolver.cs:84`, `WorldValidation.cs:411`) — for Rift Anchor on `Wildland` (round 5 B2). The row loads as the neutral `StructureKind.Feature` (round 6 C2); `TierFor` carries round 6 S1, so an anchor on a slot a previous owner holds stays closed with `anchor.no-anchor`. Publishes three `crossing.*` keys as `trade.v{n+1}`; registry row `rift-anchor-view-trigger-set` lands with its tests. The far-end view is this family's one **event-refreshed cache**: its full trigger set T1–T7 includes both key-set edges (T4 grow, T7 shrink) and each has a test (DESIGN-GATE §2.16).

---

## Row 21 — `rift-trade` W2 (the crossing leg, the handoff — goods actually move)

One flag, `trade.riftCrossing`, registered by 21.2; 21.1 shares its bump. It is **not** a widening of
`trade.riftTrade`.

### [ ] 21.1 `crossing-leg` — throughput, transit and loss, priced like a lane
- **Spec:** docs/architecture/trade-network/rift-trade/spec-crossing-leg.md
- **Wave:** row 21 · gates on `trade.riftCrossing` (21.2's row) · shares row 21's bump **N+22**, registers no row of its own
- **Depends on:** 20.3, row 6 (`logistics-flow` `lane-flow`, `lane-loss`, `transit-buffer`'s contract), row 7 (`lane-verbs`, ask A8 — `widen` naming an anchor sector)
- **Acceptance:** over a property sweep a crossing and a lane given the same hazard and perishability produce identical `LaneLoss.Milli`, a parcel's load is `lane-flow`'s `loadOf`, the pro-rata split is `lane-flow`'s and the labour part is `crossing-anchor`'s `LabourCurve.Eval(crossing.throughputCurve, labour)` — never a crossing formula; loss is in `[0, departed]` for every input including raw terms below 0 and above 1000, the load departing an anchor never exceeds its end capacity measured at that anchor's own scale, and scaling every scaled yield and the scale read by one factor leaves the movable fraction unchanged; two routes from one anchor against capacity `c < d1 + d2` split proportionally to `d1 : d2` in either creation order (both tested), and `crossing.transitTurns = 0` is a load rejection naming the key.
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Core/World/Logistics/Rift/CrossingLeg.cs','src/FusionRpg.Core/World/Logistics/LaneVerbs.cs','data/tuning/trade.v{n+1}.json','tests/FusionRpg.Core.Tests/World/Logistics/Rift/CrossingLegTests.cs') -Session <session-id>`
- **Shared files:** none from §4.
- **Notes:** `LaneVerbs.cs` is `logistics-flow`'s file and its anchor-target arm is **ask A8 on `lane-verbs`** — one verb, one resolver; do not add a second. Publishes `crossing.transitTurns`, `crossing.hazardMilli`, `crossing.widenCostCurve` as `trade.v{n+1}` (X-18 boundary row again). `widen` stays **uncapped** on a rising price (no progression ceiling); loss is a bounded ratio clamped by `lane-loss` and must say so in a comment. Registry row `rift-one-loss-formula` lands with its test. Row 6's throughput scale needs the consumer-authored power-ladder row **X-4** to be the same scale the sink reads (PS-5).

### [ ] 21.2 `crossing-handoff` — goods leave one world's hash and enter another's
- **Spec:** docs/architecture/trade-network/rift-trade/spec-crossing-handoff.md
- **Wave:** row 21 · flag `trade.riftCrossing` (registered here; gates 21.1 too) · bump **N+22**, taken here
- **Depends on:** 21.1, row 0a (`system-commands`, `stock-deltas`, `ledger-keys` + `rift-depart`/`rift-arrive` kinds, ask A10), row 5 (`logistics-flow` `logistics-phase` — the arrivals step, ask A11), wave **WC2** (`world-continuity` `hibernation-clock`) — a row in the family order since reconciliation R-14
- **Acceptance:** conservation across worlds per good at every counter — `Σ depart = Σ loss + Σ arrive + Σ waste + Σ refuse + Σ strand-lost + in-crossing` — with source stock change equal to `depart` and destination equal to `arrive`; each world replays byte-identically from its own log with the other world's rows absent, a retried commit writes no second consignment, event or command, and a player- or AI-filed `rift-arrive` is refused `kind.system-only`; a world without `trade.riftCrossing` hashes byte-identically to the same world before this module, and a world with `trade.riftTrade` only has routes and anchors and moves no goods.
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Core/World/Logistics/Rift/CrossingHandoff.cs','gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs','gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs','src/FusionRpg.Data/Sqlite/RpgStore.RiftRoutes.cs','gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs','tests/FusionRpg.Core.Tests/World/Logistics/Rift/CrossingHandoffTests.cs','tests/FusionRpg.Data.Tests/RiftCrossingLedgerTests.cs') -Session <session-id>`
- **Shared files:** `TurnEngine.cs` — row 21's single bump, and `TurnResult` carries the typed rift records; `WorldCommand.cs` — `rift-arrive` registered in `system-commands`' closed set with its admission arm in the same change (§4, one kind per wave); `RpgStore.WorldTurns.cs` — two calls in the commit, additive.
- **Notes:** the crossing ledger is save-scoped Data outside every world hash (P14 dedupe on the durable key) — no world ever reads another world's state. Rift arrivals sit inside the arrivals step and departures after banking (round 5 X5 / ask A11), so an anchor sharing a bank-point sector exports only what banking leaves — reported to `sector-yield` as **RX2** and not solved here. Registry rows `rift-arrive-system-only` and `rift-no-post-step-stock-change` land with their tests. Crosses Core and Data: full suite once at task end.

---

## Row 22 — `rift-trade` W3 (sleeping and lost endpoints, facts)

One flag, `trade.riftEndpoints`, and one bump for the wave; the three specs name no flag of their own and
take W3's. Landing-order §2 row 22 names **`sleeping-endpoint`** as the registrar, which no spec did.

### [ ] 22.1 `sleeping-endpoint` — the hibernating and idle sides, in closed form
- **Spec:** docs/architecture/trade-network/rift-trade/spec-sleeping-endpoint.md
- **Wave:** row 22 · flag `trade.riftEndpoints` (registered here for the wave; shared by 22.2 and 22.3) · bump **N+23**, taken here
- **Depends on:** 21.2, wave **WC3** (`coarse-step`, its `inputs` parameter — ask A1), wave **WC4** (`idle-world`, ask A2), wave **WC6** (`background-yield`), wave **WC2** (`hibernation-clock`)
- **Acceptance:** an End Turn in the active world performs **zero** `Step` or `CoarseStep` calls on any other world because a route exists, asserted by counting calls through an injected probe and never by timing; coarse-stepping `a` then `b` turns departs the same total per good as `a + b` at once when landing is linear and no warehouse halt binds, with crossing loss differing by at most one unit per good per extra split and the test stating that bound, and the export function's operation count does not depend on `n`; exports never exceed `stock0 + landingPerTurn × n` nor what the same world would export while active over `n` full steps, imports never credit a wallet or material ledger, and a past-due arrival lands at the next resolution — never earlier, never twice.
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Core/World/Logistics/Rift/SleepingEndpoint.cs','src/FusionRpg.Data/Sqlite/RpgStore.RiftRoutes.cs','tests/FusionRpg.Core.Tests/World/Logistics/Rift/SleepingEndpointTests.cs','tests/FusionRpg.Data.Tests/RiftSleepingEndpointTests.cs') -Session <session-id>`
- **Shared files:** `TurnEngine.cs` — row 22's single bump only (the sleeping path runs inside `CoarseStep`, which `world-continuity` owns).
- **Notes:** "leaving must never pay better than staying" is an **acceptance criterion**, not a claim — the property test sweeps the background multiplier range. Registry row `rift-no-extra-world-step` lands with its probe test. Owns this wave's flag-granted fixture re-bless (§6 row 1). `coarse-step`, `idle-world` and `background-yield` are `world-continuity` modules in waves **WC3**, **WC4** and **WC6**, all rows in `landing-order.md` §2 since reconciliation **R-14** — so this task sits after WC4 and WC6 as well as after 21.2. §2 row 22 also names **this module** as the registrar of `trade.riftEndpoints`, which no spec did. Crosses Core and Data: full suite once at task end.

### [ ] 22.2 `endpoint-loss` — a lost anchor or a fallen world
- **Spec:** docs/architecture/trade-network/rift-trade/spec-endpoint-loss.md
- **Wave:** row 22 · gates on `trade.riftEndpoints` (22.1's row) · shares row 22's bump **N+23**, registers no row of its own
- **Depends on:** 21.2, 20.3 (the far-end view for the far half), wave **WC3** (`world-continuity` `world-fall`), row **0f** (`world-state-vocabulary`)
- **Acceptance:** conservation per consignment pair — refused quantity equals the return consignment's `depart`, and for a route whose destination anchor is lost, returned plus lost at departure equals departed toward it; a return is never delivered to the destination and never takes a second loss, a stranded return lands at the first origin resolution where the origin anchor is working and is lost only by a `clear` while neither end works (one `strand-lost` event, one report entry); **order-independent** — an anchor lost versus its route cleared at the same resolution, and an anchor retaken versus a consignment falling due, give the same final stocks and events in either order (both pairs tested).
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Core/World/Logistics/Rift/EndpointLoss.cs','src/FusionRpg.Data/Sqlite/RpgStore.RiftRoutes.cs','tests/FusionRpg.Core.Tests/World/Logistics/Rift/EndpointLossTests.cs','tests/FusionRpg.Data.Tests/RiftEndpointLossTests.cs') -Session <session-id>`
- **Shared files:** none from §4.
- **Notes:** route validity is **derived each resolution** from world states and anchor ownership, never stored as a flag; the near half comes from the resolving world's own state and the far half from 20.3's far-end view — the correction C6 made, and the reason the view has a full trigger set. The suspension reason set is a **closed vocabulary** pinned with that reason. A captured anchor's warehouse moves only by `sector-yield`'s capture rule; returns re-create nothing.

### [ ] 22.3 `rift-facts` — report and digest entries
- **Spec:** docs/architecture/trade-network/rift-trade/spec-rift-facts.md
- **Wave:** row 22 · gates on `trade.riftEndpoints` (22.1's row) · shares row 22's bump **N+23**, registers no row of its own
- **Depends on:** 21.2, 22.1, 22.2, row 6 (`logistics-flow` `logistics-facts` — the closed kind vocabulary this extends), wave **WC7** (`world-continuity` `away-digest`, ask A3)
- **Acceptance:** every departure, arrival, loss, return, strand and suspension produces exactly one entry in the world or sleeping record where it happened and none elsewhere, and `Σ reported = Σ ledgered` per good and counter over a scripted two-world run; every entry has a non-null `Audience` equal to the world's player faction and a projection for any other faction contains no rift entry, and no entry's detail contains a sector id of the other world; the rift kind list and each token set are pinned as closed vocabularies with a comment saying why, and no test counts entries.
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs','src/FusionRpg.Core/World/Logistics/Rift/RiftFacts.cs','tests/FusionRpg.Core.Tests/World/Turn/RiftFactsTests.cs','tests/FusionRpg.Data.Tests/RiftFactsReconciliationTests.cs','tests/FusionRpg.Server.Tests/AwayDigestRiftTests.cs') -Session <session-id>`
- **Shared files:** none from §4 (`TurnReport.cs` is not in the shared-file table; five additive kinds only).
- **Notes:** the kinds **extend** `logistics-flow`'s closed `logistics-facts` vocabulary rather than opening a second one, so `trade-surface` reads cross-world flow the same way it reads lane flow — one reviewed widening, and `logistics-facts` (row 6) must land first. Digest folding is ask **A3 on `world-continuity` `away-digest`**, whose landing-order row is wave **WC7** since reconciliation R-14. A bump is not taken here; 22.1 took row 22's.

---

## Row 23 — `logistics-flow` W5 (the power switch)

### [ ] 23.1 `lane-loss` — the escort-strength switch (second landing: §4 and §4a only)
- **Spec:** docs/architecture/trade-network/logistics-flow/spec-lane-loss.md §4, §4a
- **Wave:** row 23 · flag `trade.laneLossPower` (its own flag — never a widening of `trade.logisticsLanes`) · bump N+24
- **Depends on:** 6.4 (the v1 loss layer), wave **L4** (`legion-build` `legion-power`, `LegionPower.Of`) — a row in the family order since reconciliation R-13
- **Acceptance:** the escort and hostile terms become one contest between rolled-up powers read from `LegionPower.Of`, summing ActorHub output only and folding no stat in this module · the clamp, the vanish-sink and the monotonicity of §1 all still hold under the new terms · a world stamped before this wave keeps the v1 stance-count rule, so no stamped world changes rules mid-life
- **Verify:** `.\scripts\verify-change.ps1 -Paths src/FusionRpg.Core/World/Logistics/LaneLoss.cs,tests/FusionRpg.Core.Tests/World/Logistics/LaneLossTests.cs -Session <session-id>`
- **Shared files:** `TurnEngine.cs` — row 23's own `RulesetVersion` bump, rebased onto the live constant (§4, R4)
- **Notes:** blocked by ask X-2 — the power-ladder §10 contest row for two rolled-up powers. **Until it lands, escort strength stays the v1 stance count and there is no interim curve** (§7); `world.hazard.resist` joins the same subtraction, defaulting to 0, behind this same flag once `world-derived` exists. Nothing in 6.4 anticipates the switch in code.

---

## CHECKPOINT 7 — Cross-world

**Rows 20–23.**

**Pass condition, from the plan §3:** a rift route carries goods between two worlds under a weight limit;
endpoints sleep and can be lost. Row 23 switches lane-loss escort strength to the power roll-up.

---

## PHASE 8 — Surface and stories

Landing-order rows **24** (five sub-waves) and **25** (four sub-waves). 24 tasks.

Every `trade-surface` sub-wave carries **no stamp capability and no ruleset bump** — its `TradeCapabilities`
are milestone UI unlocks derived from present state (reconciliation **R-16**). `trade-stories` carries
**one** flag, at 25c (**R-7**).

---

## Row 24a — `trade-surface` W1 (vocabulary and the read contract)

### [ ] 24a.1 `trade-lexicon` — the player word for every trade token
- **Spec:** docs/architecture/trade-network/trade-surface/spec-trade-lexicon.md
- **Wave:** row 24a · no flag, no bump (row 24: read-only surface; `TradeCapabilities` are UI milestones, not stamp capabilities). Creates `data/tuning/trade-catalog.v1.json`, a runtime catalog — never the `trade.v1.json` number file
- **Depends on:** row 0d (`sector-features`, for the `featureTiers` readings), row 1 (`located-goods-registry`, goods ids); later families join as their providers land (§2 of the spec: an unlanded family ships **absent**, and each later sub-wave publishes `v{n+1}`)
- **Acceptance:** (1) join closure both ways for every landed family, no orphan row and no uncovered token; (2) `tradeLabel` on an unknown id returns the designed placeholder and no rendered trade surface contains a raw token; (3) the guard fails a fixture row labelled "Trade District", a `displayName` of id shape, and a slot display name that collides with a building's — and passes on the shipped catalogs. No criterion counts goods (a reading, never asserted)
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('data/tuning/trade-catalog.v1.json','gk-core/src/FusionRpg.Server/WorldEndpoints.cs','web/fusion-rpg-web/src/features/trade/tradeLabel.ts','tests/FusionRpg.Guard.Tests/Trade/TradeVocabularyGuardTests.cs','gk-core/scripts/verification-boundaries.v1.json') -Session <session-id>`
- **Shared files:** none from §4. `gk-core/scripts/verification-boundaries.v1.json` is this task's own addition, not a §4 row
- **Notes:** **This task owns the verification-boundary rows for both clusters' FE work** — X-18 is this family's own work, not an ask (reconciliation R-17) — `verify-change.ps1:118` throws `VERIFICATION BOUNDARY MISSING` for any unmapped path, and `web/` has none (count 0). Add a `web-world-trade` row mapping `web/fusion-rpg-web/src/features/trade/**` plus the touched `stages/world/**` files to their vitest files, and a `trade-catalog-tuning` row; until it lands, every later `web/` task in rows 24 and 25 runs its own vitest files by path and reports the gap — never the full suite. `data/tuning/trade-catalog.v1.json` **now has its §5 creator row — this task** (reconciliation R-18); it is a runtime word catalog, never the `trade.v1.json` number file. Web copy: Lingui macros for chrome, catalog rows for content words, `lucide-react` for glyphs, locked libraries for meters — never hand-rolled SVG

### [ ] 24a.2 `trade-wire` — slice W1 (endpoint, own sectors, capabilities)
- **Spec:** docs/architecture/trade-network/trade-surface/spec-trade-wire.md §4 slice W1 (one of three landings; W2+W3 is 24b.2, W4+W5 is 24d.1)
- **Wave:** row 24a · no flag, no bump (read-only projection; acceptance 4 asserts the endpoint moves no world hash)
- **Depends on:** row 1 (`warehouse-axis`, `located-stock`, `production-halt`, `bank-points`), 24a.1 (`trade-lexicon`); lands **before** 24b.1 with `Capabilities` present and every flag false, per the M1 landing note in spec-trade-unlock
- **Acceptance:** (1) fog — a foreign faction's warehouse stock never appears in a viewer's projection; (2) null is not zero — an unowned sector's `Warehouse`/`Halted` serialise null, distinguishable from an owned empty warehouse; (3) read-only — hash before equals hash after; a fixture turn round-trips through `adaptWorldTrade` byte-stable
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Contracts/TradeDtos.cs','src/FusionRpg.Server/TradeEndpoints.cs','gk-web/web/fusion-rpg-web/src/contract/adapt.ts','gk-web/web/fusion-rpg-web/src/lib/bus/world.ts','tests/FusionRpg.Server.Tests/Trade/TradeEndpointTests.cs') -Session <session-id>`
- **Shared files:** none from §4 — the DTOs live in a new `TradeDtos.cs`, and the spec's Hard edges forbid adding trade fields to `WorldSectorDto`
- **Notes:** the `goodsUnits` + value unit widening of the sealed `UnitClass` union is filed here (ask S-X3 on `design/spec-magnitude-and-units.md` / world-stage `world-numbers`); until it is accepted **no goods magnitude ships on the wire**, which holds 24b.3 to its locked-and-absent state. Web paths need 24a.1's boundary row

---

## Row 24b — `trade-surface` W2 (what makes the steady-state turn playable)

### [ ] 24b.1 `trade-unlock` — milestones, building-driven flags, the guaranteed first throttle, teach-once
- **Spec:** docs/architecture/trade-network/trade-surface/spec-trade-unlock.md
- **Wave:** row 24b · **no flag, no bump** — settled by reconciliation **R-16**. `trade-surface` registers no stamp capability anywhere; this module's hashed milestone set is gated by the **producers'** flags, so a world whose stamp grants none of them has an **empty** set, and **an empty milestone set emits no canonical row at all**. That is why an old-stamp world hashes byte-identically: emptiness, not a flag of this module's own. The spec's *"stamp-gated"* wording was corrected in the same pass
- **Depends on:** 24a.2 (`trade-wire` W1 ships the `Capabilities` field this fills), row 0a (`world-stamp`), row 0d (`sector-features` `FactionTier`), row 1 (`production-halt`, `bank-points`), rows 5–7 (`logistics-facts`, `path-cache`), row 9 (`forecast-facts` dry run), rows 15–16 (`empire-roster`, `clan-seeding` — first contact needs a seeded treat-capable faction), npc-story-events `story-ledger` (external, for the save-scoped taught record), world-map-program templates (ask)
- **Acceptance:** (1) reachability — on each first-world template a scripted sequence of **admitted** commands (no debug endpoint) reaches `first-throttle` by `teach.firstThrottleByTurn` and reaches `first-contact`, each false the turn before and true at that turn; (2) monotonic milestones, while building flags follow the buildings (razing the only Trading Post locks clan barter the same turn with its reason, rebuilding unlocks it — both edges); (3) old stamp — a world stamped before this module hashes byte-identically, and replay from the command log yields the same unlock turn and state hash
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Core/World/Trade/TradeMilestones.cs','gk-core/src/FusionRpg.Core/World/WorldState.cs','gk-core/src/FusionRpg.Core/World/WorldCanonical.cs','data/tuning/trade.v1.json','gk-web/web/fusion-rpg-web/src/shell/railState.ts','tests/FusionRpg.Core.Tests/World/Trade/TradeMilestoneTests.cs','tests/FusionRpg.Data.Tests/Narrative/TaughtFactTests.cs') -Session <session-id>`
- **Shared files:** §4 `WorldState.cs` — the milestone set is an additive record field, slot *after the last field present at landing* (§4's named order ends at diplomacy facts + treasury, row 15). §4 `WorldCanonical.cs` — one conditional milestone row, slot *after the last conditional row present at landing*; **§4's sparse-row clause now names this row** (R-11), and because it is sparse it moves no existing hash and owes no re-bless. `data/tuning/trade.v1.json` — publish `v{n+1}` with `teach.firstThrottleByTurn`; creator is row 0a `economy-report`
- **Notes:** the guarantee criterion is the **relaxed** reachability bound (every legion at best speed, every build free and earliest-admissible), not a search over every command sequence. Template edits are world-map-program's; this task files the constraint. Cross-program §7: multi-slot `BuildResolver` (X-11) must already have landed for the `build-feature` answer to be admissible on a Wildland-or-Market slot

### [ ] 24b.2 `trade-wire` — slices W2 and W3 (lanes, status, forecast)
- **Spec:** docs/architecture/trade-network/trade-surface/spec-trade-wire.md §4 slices W2, W3 (second of three landings)
- **Wave:** row 24b · no flag, no bump (read-only)
- **Depends on:** 24a.2 (W1), row 6 (`lane-flow`, `lane-loss`, `logistics-facts`), row 9 (`forecast-facts`), 24b.1 (`Capabilities` filled, so the unlock refetch edge is real)
- **Acceptance:** (1) a lane the viewer cannot see has `Known = false` with null fields, never a zero flow; (2) every magnitude field carries a unit class — a DTO walk fails on a bare number; (3) each of the five invalidation triggers refetches, each with its own test, including the **unlock edge** (capabilities change with no turn advance) — DESIGN-GATE §2.16
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Contracts/TradeDtos.cs','src/FusionRpg.Server/TradeEndpoints.cs','gk-web/web/fusion-rpg-web/src/contract/adapt.ts','gk-web/web/fusion-rpg-web/src/lib/bus/world.ts','tests/FusionRpg.Server.Tests/Trade/TradeEndpointTests.cs') -Session <session-id>`
- **Shared files:** none from §4
- **Notes:** slices add fields and never rename one; a field whose provider has not landed is **absent**, not defaulted

### [ ] 24b.3 `trade-status` — the one-line banked / lost / stuck contract and its HUD strip
- **Spec:** docs/architecture/trade-network/trade-surface/spec-trade-status.md
- **Wave:** row 24b · no flag, no bump (a pure Core fold over the turn's own facts plus a band-1 strip)
- **Depends on:** 24b.2 (W2 slice, `goodsUnits`), 24a.1 (sentences, cause and reason names), 24b.1 (locked state), row 6 (`lane-flow`, `transit-buffer`, `logistics-facts`), row 8 (`banking-fact` step half — for the `Banked` part only), world-stage `world-hud` (ask)
- **Acceptance:** (1) reconciliation — `Lost == Σ LossCauses.Amount` and `Stuck == Σ Bottlenecks.Amount` for any fixture turn; (2) one fold — the strip DTO and the same turn's report entries carry equal totals, built from one fixture; (3) units and quiet — headline totals render in the value unit class and attribution lines in `goodsUnits` (a two-goods fixture shows `Σ qty × ValueOf`, never `Σ qty`), and `Lost = Stuck = 0` renders the quiet sentence
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Core/World/Logistics/TradeStatusFold.cs','src/FusionRpg.Contracts/TradeDtos.cs','web/fusion-rpg-web/src/features/trade/status/TradeStatusStrip.tsx','tests/FusionRpg.Core.Tests/World/Logistics/TradeStatusFoldTests.cs') -Session <session-id>`
- **Shared files:** none from §4
- **Notes:** **round 6 C3 shapes this task.** `Banked` is Σ banking-fact value, so it is 0 and the headline simply **omits the part** until row 8 lands behind the save-identity re-key (§7 X-1) — never a second income read to fill the gap. The strip ships with logistics and gains its first number at row 8. Layout is `/idea-ui`'s, not this task's

### [ ] 24b.4 `throttle-forecast` — next-turn throttles with one-click answers
- **Spec:** docs/architecture/trade-network/trade-surface/spec-throttle-forecast.md
- **Wave:** row 24b · no flag, no bump (a pure forecast; acceptance 6 asserts it leaves the committed state hash unchanged)
- **Depends on:** 24b.2 (W3 slice), row 9 (`forecast-facts` side-effect-free dry run and its answer table), row 7 (`route-set`, `widen` via `auto-banking` / `lane-verbs`), row 0d (`sector-features` for the `build-feature` answer), row 18 (`exchange` `order-book`, `trade-access` — for `trade-away` only), row 11 + `legion-build` `escort-stance` and row 14 (`escort-link`) for the `escort` answer, world-stage `world-turn` (nag ask)
- **Acceptance:** (1) faithful both directions, under the stated condition — no new orders **from any faction** and the same logged step inputs; (2) answers work — committing the top-ranked answer reduces that throttle's `Amount` by at least the reported `UnitsSaved`, and filing two answers in either order yields the same committed state (order-independent, both tested); (3) never blocks — `HARD_BLOCKING_EVENTS` is still empty, at most three admissible answers render, none disabled
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Core/World/Logistics/ThrottleAnswers.cs','data/tuning/trade.v1.json','web/fusion-rpg-web/src/features/trade/forecast/ThrottleChip.tsx','gk-web/web/fusion-rpg-web/src/stages/world/turn/blockingClasses.ts','tests/FusionRpg.Core.Tests/World/Logistics/ThrottleAnswerTests.cs') -Session <session-id>`
- **Shared files:** `data/tuning/trade.v1.json` — publish `v{n+1}` with `forecast.lossAlertMilli`; creator is row 0a `economy-report`. No §4 row
- **Notes:** the fifth answer `build-feature` is the reviewed vocabulary widening (round 4 Q3); the feature comes from `forecast-facts`' answer table, never a second table here. If the nag-list edit is refused, the forecast lives in the trade panel only (map §8 default) and 24e.2's T2/T3 rows shift to the panel path

---

## Row 24c — `trade-surface` W3 (the sector surface, the map lens, the rail rows)

### [ ] 24c.1 `trade-panel` — the `trade` block on the sector inspector
- **Spec:** docs/architecture/trade-network/trade-surface/spec-trade-panel.md
- **Wave:** row 24c · no flag, no bump (renders provider folds; decides no number)
- **Depends on:** 24b.2, 24b.3, 24b.4, 24a.1, 24b.1; world-stage `world-inspector` (ask: insert `trade` into `BLOCK_ORDER` after `vault` and mount the block)
- **Acceptance:** (1) order — the new `BLOCK_ORDER` minus `trade` equals the old order exactly, and `trade` sits immediately after `vault`; (2) absent vs empty vs loading vs error each render their designed piece, and no control is disabled without its reason; (3) gauge honesty — the warehouse gauge fills against `WarehouseCapacity` and no other trade quantity is drawn against a cap; opening the block pushes no band-3 layer
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('web/fusion-rpg-web/src/features/trade/panel/foldTradeBlock.ts','gk-web/web/fusion-rpg-web/src/stages/world/inspector/blockOrder.ts','gk-web/web/fusion-rpg-web/src/stages/world/inspector/SectorInspector.tsx','web/fusion-rpg-web/src/features/trade/panel/foldTradeBlock.test.ts') -Session <session-id>`
- **Shared files:** none from §4 (`blockOrder.ts` and `SectorInspector.tsx` are world-stage's, edited through its ask, not this family's §4 list)
- **Notes:** this task also removes the stale block count from `blockOrder.ts`'s header comment (spec acceptance 8). C2 binds: no tier is read from a `StructureKind` — the hub tier comes from `sector-features`. Layout is `/idea-ui`'s

### [ ] 24c.2 `flow-lens` — a seventh, reviewed lens for lane flow, utilisation and bottleneck
- **Spec:** docs/architecture/trade-network/trade-surface/spec-flow-lens.md
- **Wave:** row 24c · no flag, no bump (a presentation encoding; availability is `trade-unlock`'s pure derivation)
- **Depends on:** 24b.2 (W2 `Lanes`), 24b.1 (`Logistics` flag), 24a.1 (cause and reason names); world-stage `world-lenses` (ask: the closed-set widening plus state-driven availability)
- **Acceptance:** (1) seven lenses, pinned as a declaration with its reason, and key `7` registered only while `flow` is available; (2) locked — before unlock the lens shows its reason, is not selectable, and key `7` does nothing; flipping availability in a mounted stage makes key `7` live with no throw and no duplicate verb (the key-set edge, §2.16); (3) colour-free encoding, an unseen lane encodes `unknown` never zero, and doubling every visible flow leaves every lane's weight unchanged
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('gk-web/web/fusion-rpg-web/src/stages/world/lenses/lensCatalog.ts','gk-web/web/fusion-rpg-web/src/stages/world/lenses/lensState.ts','gk-web/web/fusion-rpg-web/src/stages/world/lenses/useLensHotkeys.ts','gk-web/web/fusion-rpg-web/src/stages/world/render/laneChannels.ts','gk-web/web/fusion-rpg-web/src/stages/world/lenses/lensAutoActivate.test.ts') -Session <session-id>`
- **Shared files:** none from §4
- **Notes:** GG-38 applies — the lane channel draws inside the stage-lazy Phaser `stage-map` chunk, and the encoding, availability and picker code import no Phaser, so `npm run check:bundle` stays green. `registerGlobalVerb` throws on duplicates: unregister before re-registering, never a `try/catch`

### [ ] 24c.3 `trade-notify` — trade's rail rows, their translator and their source
- **Spec:** docs/architecture/trade-network/trade-surface/spec-trade-notify.md
- **Wave:** row 24c · no flag, no bump (a classifier over committed report lines; the catalog is data)
- **Depends on:** 24a.1, 24b.3, 24b.4; notification-ssot `notify-vocabulary`, `notify-format`, `notify-service`, `world-notify-source` (external program, all four required); report producers at rows 1, 5–7 and, as they land, rows 15–18
- **Acceptance:** (1) coverage — every trade `(category, messageKey)` has a translator, and the trade rows in the catalog equal the declared seven (a declaration with its reason; an extra `trade.*` row fails); (2) dedup from the source line's own subject id, so re-running the pump appends nothing and two treaty lines in one turn do not collide; (3) quiet steady state — a turn whose only trade lines are banking and loss produces **zero** drafts, and a turn's several drafts go out in one batch
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Core/World/Logistics/TradeNotifyClassifier.cs','src/FusionRpg.Server/Notifications/TradeNotificationSource.cs','gk-core/data/tuning/notification-catalog.v2.json','web/fusion-rpg-web/src/features/trade/notify/tradeTranslator.ts','tests/FusionRpg.Core.Tests/World/Logistics/TradeNotifyClassifierTests.cs') -Session <session-id>`
- **Shared files:** none from §4. `data/tuning/notification-catalog.v{n}.json` is notification-ssot's file — publish `v{n+1}`; its §5 creator row is that program's, not this family's
- **Notes:** no second report-prefix family — the classifier reads providers' typed `TurnReportKinds` (spec-time correction S1). A promotion to toast or Critical is a reviewed catalog change, never a code default; the rail component itself is world-stage's

---

## Row 24d — `trade-surface` W4 (editors and the power-loop payoff)

### [ ] 24d.1 `trade-wire` — slices W4 and W5 (foreign belief, policy, blocked demand, counterparties)
- **Spec:** docs/architecture/trade-network/trade-surface/spec-trade-wire.md §4 slices W4, W5 (third of three landings; both are unblocked by row 18, so they land in one change)
- **Wave:** row 24d · no flag, no bump (read-only)
- **Depends on:** 24b.2, row 18 (`exchange` `exchange-hub`, `price-curve`, `trade-access`, `treaty-lifecycle`), rows 15–17 (`diplomacy-facts`, `diplomatic-stance`, `relation-facts` band snapshot), row 19 (`trade-ai` `trade-intel`, believed quotes)
- **Acceptance:** (1) a foreign hub appears only with `BelievedQuotes` and an `IntelAgeTurns`, never with stock; (2) the material-shelf refetch trigger fires with no turn advance (a fusion changes what is blocked) — its own test; (3) each added field carries its unit class and the fixture turn still round-trips byte-stable
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Contracts/TradeDtos.cs','src/FusionRpg.Server/TradeEndpoints.cs','gk-web/web/fusion-rpg-web/src/contract/adapt.ts','tests/FusionRpg.Server.Tests/Trade/TradeEndpointTests.cs') -Session <session-id>`
- **Shared files:** none from §4
- **Notes:** the band a turn uses is the **logged step input** snapshot `counterparties` commits, not a live ledger read (counterparties assumption 3 / C4); this slice serves it and derives nothing

### [ ] 24d.2 `trade-policy-editor` — standing hub orders and a caravan's route
- **Spec:** docs/architecture/trade-network/trade-surface/spec-trade-policy-editor.md
- **Wave:** row 24d · no flag, no bump (files existing policy command kinds; adds none)
- **Depends on:** 24c.1, 24d.1 (W4 `Policy`), 24a.1, 24b.1; row 7 (`route-set`, `route-clear`, `bank-hold` — the hold control also needs row 8 for `BankingTier ≥ 2` to mean anything), row 18 (`order-set`, `trade-access`), row 12–13 (`depot` foreign-yard reason, `trade-route-order`), `legion-build` `standing-orders`, empire-inventory-surfaces `legion-sheet` (route-tab reservation ask)
- **Acceptance:** (1) round trip — each bus event files exactly one command of the named kind, the next state read shows the policy the command set, and the turn report states its effect; (2) a new hub with no policy edit banks its goods (auto-banking default), and before the commit the control shows *filed* with no value changed in the view; (3) own only — a foreign hub never opens the editor, every disabled control has a reason, folds are pure and never fetch
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('web/fusion-rpg-web/src/features/trade/policy/foldTradePolicy.ts','gk-web/web/fusion-rpg-web/src/lib/bus/world.ts','gk-web/web/fusion-rpg-web/src/stages/world/legionSheet/LegionSheet.tsx','web/fusion-rpg-web/src/features/trade/policy/foldTradePolicy.test.ts') -Session <session-id>`
- **Shared files:** none from §4 — this task adds **no** `WorldCommand.cs` kind, so §4's one-kind-per-wave rule does not bind it
- **Notes:** the Treasury hold default is round 5 A4 — keep enough to fill other traders' open buy orders at this hub. If the legion-sheet reservation is refused, caravan routes are set from the hub side only (map §8 default)

### [ ] 24d.3 `blocked-demand` — which fusions a good is blocking, and who sells it
- **Spec:** docs/architecture/trade-network/trade-surface/spec-blocked-demand.md
- **Wave:** row 24d · no flag, no bump (a Server projection join)
- **Depends on:** 24d.1 (W4), 24a.1, 24c.1; row 18 (`trade-access`, quotes), row 19 (`trade-intel` believed offers), row 1 (`located-goods-registry`), gui-lego menu-refactor-queue P4 (the Fusion layer's Lego refactor, for the chip only)
- **Acceptance:** (1) no double counting — a fusion short on two goods contributes to neither good's `FusionsBlocked`, and each good's `Shortfall` equals Σ (need − have) over its blocked fusions; (2) access-true — a hub below `market` by `LevelAt` never appears as a seller, and a hub blocked only by the viewer's own missing building appears as a build hint; (3) one projection — the fusion endpoints and this projection call the same cost helper (equal cost lines for a fixture recipe), no material id reaches a player surface, and no chip renders when nothing is blocked
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Server/Trade/BlockedDemandProjection.cs','gk-core/src/FusionRpg.Server/FusionEndpoints.cs','web/fusion-rpg-web/src/features/trade/blockedDemand/BlockedDemandChip.tsx','tests/FusionRpg.Server.Tests/Trade/BlockedDemandProjectionTests.cs') -Session <session-id>`
- **Shared files:** none from §4
- **Notes:** the panel line can ship before the chip (the chip waits on P4). Moving `ProjectCost` touches a Server file the fusion feature owns — behaviour-preserving, proven by equal outputs

---

## Row 24e — `trade-surface` W5 (diplomacy and the counted click budget)

### [ ] 24e.1 `treaty-screen` — the Diplomacy rail layer
- **Spec:** docs/architecture/trade-network/trade-surface/spec-treaty-screen.md
- **Wave:** row 24e · no flag, no bump (renders derived access and the logged band snapshot; files existing diplomacy kinds)
- **Depends on:** 24d.1 (W5), 24a.1, 24b.1 (`Diplomacy` flag and first contact); rows 15–17 (`diplomacy-facts`, `diplomatic-stance`, `relation-facts`), row 18 (`treaty-vocabulary`, `trade-access`, `treaty-lifecycle`), row 19 (`ai-treaty-policy`, `counter-offer-articles`), npc-story-events `relation-ledger` (external)
- **Acceptance:** (1) no FE derivation — access and band shown equal the Core derivation or logged snapshot for every fixture pair; (2) locked, never hidden — a kind above the current band shows its lowest band, a kind blocked by the **viewer's own** missing Embassy, Consulate or Exchange names that building (only the offerer's gates, round 5 C2), a deliberate embargo shows locked without a Consulate while an automatic war embargo is listed in force with no lock; (3) every verb has a surface — an AI offer renders accept, decline and counter, each filing exactly one command, and the bus covers every player-fileable diplomacy kind (a join against `treaty-lifecycle` §1 and `diplomatic-stance`)
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Contracts/TradeDtos.cs','web/fusion-rpg-web/src/features/trade/diplomacy/foldDiplomacyLayer.ts','gk-web/web/fusion-rpg-web/src/shell/railState.ts','gk-web/web/fusion-rpg-web/src/layers/system/keybindings.ts','tests/FusionRpg.Server.Tests/Trade/CounterpartyDtoTests.cs') -Session <session-id>`
- **Shared files:** none from §4
- **Notes:** **blocked on the required amendments**, which are other owners' edits and not made by this task: `design/information-architecture.md` §3/§4/§5/§7 and the Game GUI row at `docs/architecture/decisions.md:110` ("8 layers" → 9) — audit finding S-X2. No specific-actor name and no code identifier reaches the surface; enemy factions are "enemy empires", and the player-facing word for a fighting body is "unit", per `trade-lexicon`'s vocabulary. War is the only diplomacy action that pushes a band-3 confirm

### [ ] 24e.2 `trade-click-budget` — the counted acceptance across every trade surface
- **Spec:** docs/architecture/trade-network/trade-surface/spec-trade-click-budget.md
- **Wave:** row 24e · no flag, no bump (tests only)
- **Depends on:** every task in 24b–24e (24b.3, 24b.4, 24c.1, 24c.2, 24c.3, 24e.1)
- **Acceptance:** (1) each row T1–T6 exists as a test that counts user events and passes against the built surfaces, asserting **equal**, not ≤; (2) a fixture change that adds one required click to any row fails that row; (3) T1 asserts zero trade drafts reach the rail and the strip shows the quiet sentence
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('web/fusion-rpg-web/src/features/trade/clickBudget.test.tsx') -Session <session-id>`
- **Shared files:** none
- **Notes:** lands last by construction. A row whose surface is blocked (T6 if the seventh-lens edit is refused) is marked **pending with its blocker**, never deleted and never quietly relaxed

---

## Row 25a — `trade-stories` W1 (the fact vocabulary)

### [ ] 25a.1 `trade-fact-kinds` — the closed list of trade story facts
- **Spec:** docs/architecture/trade-network/trade-stories/spec-trade-fact-kinds.md
- **Wave:** row 25a · **no flag, no bump** — R3 infrastructure: a vocabulary declaration with no writer yet, which nothing in `Step` and nothing in the canonical projection reads
- **Depends on:** npc-story-events `narrative-vocabulary` (`StoryFactKind`) and `story-ledger` (keys and the `lane`/`legion` subject kinds — external program, blocking); each kind is registered in the **same wave as, or after,** the producer whose record it projects (rows 1, 5–7, 12–14, 15–17, 18)
- **Acceptance:** (1) every kind names exactly one source record kind and one owner, and has a `source_ref` format plus a closed `attrs` set — a writer with an unlisted attribute is refused; (2) the list is pinned at twelve as a declaration with its reason (a closed vocabulary the code owns, not a population); (3) no duplicates — a join against `StoryFactKind` and `relation-facts`' emitted kinds finds no trade kind matching another's (source record kind, subject kind, qualifying condition), with the one declared overlap listed in the test
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Core/World/Trade/Stories/TradeFactKinds.cs','tests/FusionRpg.Core.Tests/World/Trade/Stories/TradeFactKindTests.cs') -Session <session-id>`
- **Shared files:** none from §4 — the story-fact registry and ledger tables are npc-story-events'
- **Notes:** `source_ref`s must be unique per fact **including across years** (the T-A1 lesson). A kind whose producer has not landed is declared with no writer, and 25c.2 marks it **pending, never green**

---

## Row 25b — `trade-stories` W2 (the projector, the hosts, the leaves, the content asks)

### [ ] 25b.1 `trade-fact-source` — commit-time projection of trade records into story facts
- **Spec:** docs/architecture/trade-network/trade-stories/spec-trade-fact-source.md
- **Wave:** row 25b · **no flag, no bump** — R3: acceptance 5 asserts the turn's stored state hash is identical with and without the projection registered, so nothing `Step` or the canonical projection reads changes
- **Depends on:** 25a.1; row 16 (`counterparties` `relation-facts` — this module registers as `ICommitFactProjector` `trade-story` into its existing pass, OD-4), npc-story-events `story-ledger` (external); producers at rows 1, 5–7, 12–14, 18
- **Acceptance:** (1) idempotent — replaying a commit writes nothing new; (2) complete and exact both ways — every source record of a covered kind yields exactly one fact per eligible audience and no fact exists without its record; (3) one writer and order-independent — no path outside `relation-facts`' pass appends a trade kind, and the drafts are the same set whichever order the report's entries are visited
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Core/World/Trade/Stories/TradeStoryProjector.cs','tests/FusionRpg.Core.Tests/World/Trade/Stories/TradeStoryProjectorTests.cs','tests/FusionRpg.Data.Tests/World/TradeStoryCommitTests.cs') -Session <session-id>`
- **Shared files:** none from §4 — the append goes through `story-ledger`'s API, not `RpgStore.WorldTurns.cs`
- **Notes:** the fog rule is reused, never re-implemented (notification-ssot's ask moves it into Core). If `relation-facts` lands its seam with a different signature this module adopts it — it never builds a second commit-time pass

### [ ] 25b.2 `trade-hosts` — the four places a trade storylet may appear
- **Spec:** docs/architecture/trade-network/trade-stories/spec-trade-hosts.md
- **Wave:** row 25b · **no flag, no bump** — the adapters decide only *when* to ask; whether a storylet may fire at all on a world is the storylet engine's own capability, and that is npc-story-events' to register — an **ask** on that program, filed and not built here
- **Depends on:** 25a.1; row 0d (`sector-features` `TierOf`/`FactionTier` — hosts attach by feature tier, never by a `StructureKind` or a row id, C2/S1), row 18 (`exchange-hub`, `trade-access` for `LevelAt` fog), row 12 (`depot`), row 6 (`lane-flow`); narrative-seed `storylet-vocab` (host-kind registry, OD-3) and npc `storylet-reseam`, `world-events-host`, `host-content-theta` (external, blocking)
- **Acceptance:** (1) when, never which — a static guard finds no reference from a trade host adapter to a selection, weight, outcome or reward type; (2) one place, one host — a Market-slot sector with an active hub produces exactly one ask per pulse, both with the hub on the Market slot and with it on a Wildland slot beside an empty Market slot (round 5 B1); (3) fog, streams and joins — a foreign hub never asks for a faction below `market`, every stream root is trade's own and never a combat stream, every adapter's `HostKind` is a registry row and every trade row has an adapter, and every clock is `WorldTurn`
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Core/World/Trade/Stories/TradeStoryletHosts.cs','tests/FusionRpg.Core.Tests/World/Trade/Stories/TradeStoryletHostTests.cs') -Session <session-id>`
- **Shared files:** none from §4 — the `Events`-phase call site is `world-events-host`'s, so this task does not edit `TurnEngine.cs`
- **Notes:** the one-place-one-host rule edits `world-events-host`'s eligibility and is **filed as an ask, never worked around**. No host is keyed on `WorldEntityKind.Caravan` (the umbrella retires it)

### [ ] 25b.3 `trade-predicates` — four state leaves for storylet eligibility
- **Spec:** docs/architecture/trade-network/trade-stories/spec-trade-predicates.md
- **Wave:** row 25b · **no flag, no bump** — the readers read hashed state and write nothing; the leaf enum is a closed vocabulary, not a capability
- **Depends on:** 25a.1; npc-story-events `narrative-predicates` (ordinal order — the trade leaves append after npc's six) and the atom program's predicate grammar (external, blocking); row 1 (warehouse fill), row 18 (`exchange` `EffectiveLevel` for `AccessIs`), rows 15–17 (`diplomacy-facts` for `TreatyIs`)
- **Acceptance:** (1) each leaf compiles through `PredicateCompiler` within depth 4 / 16 nodes, and an out-of-range `Set[0]` is a compile rejection; (2) each reader is deterministic over hashed state and allocation-free, and a guard fails a reader that reads unhashed state inside the step; (3) the four leaves are pinned **by membership** — the enum's total belongs to the atom program's own pin, never to this module
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Effects/Atoms/PredicateNode.cs','src/FusionRpg.Core/World/Trade/Stories/TradeFactReaders.cs','tests/FusionRpg.Core.Tests/World/Trade/Stories/TradeLeafTests.cs') -Session <session-id>`
- **Shared files:** none from this family's §4. `PredicateNode.cs` is the atom program's shared enum — append only, never reorder, and `effect-atom/definitions.md` §3's leaf table moves in the same change or the widening is not done
- **Notes:** event recency is **one generic `StoryFactWithin`** requested on npc, so the enum grows by state leaves only. No leaf reads a `StructureKind` or a building's owner: a tier comes from `sector-features` through the producer (round 6 C2/S1)

### [ ] 25b.4 `trade-storylet-supply` — the registry and coverage asks on narrative-seed
- **Spec:** docs/architecture/trade-network/trade-stories/spec-trade-storylet-supply.md
- **Wave:** row 25b · **no flag, no bump** — asks and a guard; no runtime behaviour
- **Depends on:** 25b.2, 25b.3; narrative-seed `storylet-vocab`, `token-grammar`, `narrative-planner`, `arc-shapes`, `arc-pipeline`, `narrative-metrics` (external program, blocking). Lands **before** 25d.2 with the failure hosts' rows requested and **no rows required to exist** (the M1 landing note in trade-stories-map §14)
- **Acceptance:** (1) every trade host kind has at least one coverage cell in the planner's budget file — a **join, not a count**; (2) no file under `gk-data/packs/fusion/data/seed/narrative/**` is authored or edited by trade-stories (a guard over the specs' touched paths plus a CI diff check); (3) every trade leaf has a condition row, or its absence is listed as pending in 25c.2
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('docs/architecture/trade-network/trade-stories/spec-trade-storylet-supply.md') -Session <session-id>` — boundary `docs-and-assistant-config`; the registry and corpus checks run in narrative-seed's own seedsmith tests
- **Shared files:** none
- **Notes:** `gk-forge/tools/seedsmith/**` has no verification boundary yet — a row this family adds in the first task that touches the path (X-18, R-17), which is 0b.1, not this one; nothing here runs there — the coverage join runs in `narrative-metrics`. **Hard rule:** generated seed data is never hand-edited; a missing trade row is a generator or registry change on narrative-seed, never a JSON edit here

---

## Row 25c — `trade-stories` W3 (pacing, reachability, and the one behaviour change)

**One flag and one bump: `trade.demandShock`, ordinal N+25**, registered by `seasonal-demand-shocks`. Pacing
and reachability register nothing.

### [ ] 25c.1 `trade-story-pacing` — rate limits in data, independent of empire size
- **Spec:** docs/architecture/trade-network/trade-stories/spec-trade-story-pacing.md
- **Wave:** row 25c · **no flag, no bump of its own** — rows in a tuning file plus a selection rule that lives in npc's one engine
- **Depends on:** 25b.2; npc-story-events `storylet-selection` (the per-empire budget rule, OD-5) and `narrative-vocabulary` (the tuning loader and file) — external, blocking
- **Acceptance:** (1) size independence — on seeded fixture worlds identical except that one empire holds twice the hubs, that empire's trade Chosen count per turn never exceeds the budget in either (a structural property; no rate asserted to a number); (2) cooldown on the world-turn clock, and with every trade weight at 0 and no priority storylet, nothing fires; (3) load rejection — a missing trade row or a `budgetGroup` naming no budget rejects the load (T5); a budget-quieted pulse advances pity like a fire miss
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('gk-core/data/tuning/narrative.v2.json','tests/FusionRpg.Core.Tests/Narrative/TradePacingTests.cs') -Session <session-id>`
- **Shared files:** none from §4. `gk-core/data/tuning/narrative.v1.json` is npc-story-events' file and **does not exist yet anywhere in the repo**. `gk-core/tools/tuning/publish.py` can only bump a file that exists, so landing order §7 files an **ask** on that program (reconciliation R-18) with a stated default: if `v1` is not authored by the time this task lands, the trade rate-limit rows stay a proposal in the spec and the size-independence test runs against npc's engine, and the publish follows when the file exists. This family edits nothing under `docs/architecture/npc-story-events/**`
- **Notes:** the budget lives in the one engine — this module ships **no** private limiter and no `const` frequency. The budget is flat per empire by design; anything that scales it is an ask

### [ ] 25c.2 `trade-trigger-reachability` — every fact kind and leaf provably reachable
- **Spec:** docs/architecture/trade-network/trade-stories/spec-trade-trigger-reachability.md
- **Wave:** row 25c · **no flag, no bump** — R3: fixtures, tests and one preflight rule
- **Depends on:** 25a.1, 25b.1, 25b.3; row 0a (`synthetic-graph`, the fixture world builder), npc `storylet-contract` (the preflight rule's code — external); the producer rows behind each kind (1, 5–7, 12–14, 18)
- **Acceptance:** (1) every trade fact kind and every trade leaf value has a passing case or an explicit **pending** entry — closure over the two closed vocabularies, which are declarations; (2) no case uses a debug endpoint or writes state outside admitted commands (a scan of the test sources for debug entry points); (3) the preflight refuses a fixture storylet whose only condition is an unreachable leaf value and accepts one whose condition is reachable
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('tests/FusionRpg.Core.Tests/World/Trade/Stories/TradeTriggerReachabilityTests.cs','tests/FusionRpg.Data.Tests/World/TradeFactReachabilityTests.cs') -Session <session-id>`
- **Shared files:** none
- **Notes:** this is the honest ledger of what row 25 cannot yet prove: **pending entries are expected while producers land and none may be deleted to go green.** No case counts storylets, and no fact is fabricated — the live-probe scope rule applies to fixtures too

### [ ] 25c.3 `seasonal-demand-shocks` — seasons move demand, announced as a fact
- **Spec:** docs/architecture/trade-network/trade-stories/spec-seasonal-demand-shocks.md
- **Wave:** row 25c · flag **`trade.demandShock`** (this task registers it) · bump **N+25** — the one flag and the one bump either surface/stories cluster takes, settled by reconciliation **R-7** and now §2 row 25c. The demand term changes what `Step` computes on a live world, so R1/R2 require its own wave flag; the spec's own Hard edges already say a demand behaviour change "rides the per-world stamp". `trade-stories-map.md:681`'s blanket *"registers no capability flag and takes no `RulesetVersion` bump"* was **corrected** in the same pass; it may not ride row 15's `counterparties.needs` either, because R1 forbids widening an earlier wave's flag
- **Depends on:** 25a.1; row 15 (`counterparties` `need-vector` — the demand contribution seam, plus ask E-A10's per-sector read, without which the shock cannot be climate-correct and **must not ship**, T-X3), row 18 (`exchange` reads demand), row 0a (`world-stamp`)
- **Acceptance:** (1) deterministic — the same world seed and turn produce the same active shocks byte for byte, and over three fixture years the same-named season draws from a different `seasonOrdinal` with a distinct announcement (no yearly repeat, no dedupe collision); (2) one mechanism — a scan finds no price write outside `exchange`, and a shock never changes any stock (stock before equals stock after the phase, per good); (3) bounded ratio and load — `shock.demandMilli ≥ 1000` and any missing `shock.*` key reject the load, and truth-side and belief-side need vectors agree on the term
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Core/World/Trade/Demand/DemandShockSchedule.cs','gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs','data/tuning/trade.v1.json','tests/FusionRpg.Core.Tests/World/Trade/Demand/DemandShockTests.cs') -Session <session-id>`
- **Shared files:** §4 `TurnEngine.cs` — `RulesetVersion` moves once for this wave; **rebase onto the latest constant and take the next integer** (R4), and reference the constant, never a literal. `data/tuning/trade.v1.json` — publish `v{n+1}` with the `shock.*` keys; creator is row 0a `economy-report`
- **Notes:** the shock uses its **own named roll stream**, never the existing special-week or special-month rolls. A shock targets a good class, not a single clan. Old-stamp worlds get no shock and no hash movement, which is what keeps §6's re-bless list short

---

## Row 25d — `trade-stories` W4 (quests and failure branches)

### [ ] 25d.1 `trade-quests` — escort, deliver, recover and ransom as template rows
- **Spec:** docs/architecture/trade-network/trade-stories/spec-trade-quests.md
- **Wave:** row 25d · **no flag, no bump** — template instances in npc's one quest engine plus a pure evaluator over committed facts
- **Depends on:** 25a.1, 25b.1; npc-story-events `quest-sources`, `outcome-routing` (including ask X-T1's one-off deal-offer outcome kind, which blocks `trade-ransom` only), `petition-host` (external); row 8 (`banking-fact`, for `trade-deliver`'s banked count), rows 13–14 (`trade-route-order`, `interception`, `goods-cargo-fate`), row 18 (`settlement-payment`, `goods-valuation`), `legion-build` `escort-stance` (for `trade-escort` only)
- **Acceptance:** (1) no soul faucet — an invariant test over every template's reward path finds no path increasing souls through trade, and a ransom's souls are a sink; (2) ransom never duplicates goods — per good, counterparty stock decreases and the player's **consignment at that hub** increases by the same amount, once, and a short ransom settles at the deal's one fulfilment ratio; (3) mode-agnostic and world-clocked — no template reads a lawn fact, expiry and escort counts are world turns, and `trade-recover` completes on a `goods-cache.claimed` fact naming the faction and on nothing else
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Core/World/Trade/Stories/TradeQuestObjectives.cs','tests/FusionRpg.Core.Tests/World/Trade/Stories/TradeQuestObjectiveTests.cs') -Session <session-id>`
- **Shared files:** none from §4. The quest-objective registry rows are a reviewed change on npc `quest-sources`' vocabulary, not a file in this family's §4 or §5 tables
- **Notes:** `trade-escort` waits on the escort stance and `trade-ransom` on X-T1; **the other two do not wait** (map §8 default), so this task may land three templates and mark one pending with its blocker. The ransom price is `exchange`'s value-index price, settled as a deal leg — never an `order-set` walk and never a quest-local price

### [ ] 25d.2 `trade-failure-branches` — a lost hub, depot or route opens a questline
- **Spec:** docs/architecture/trade-network/trade-stories/spec-trade-failure-branches.md
- **Wave:** row 25d · **no flag, no bump** — failure semantics over facts 25a.1 already declares, routed by npc's one branch engine
- **Depends on:** 25a.1, 25b.1, 25b.3, 25b.4, 25c.1; npc-story-events `failure-branches`, `spine-progress`, `storylet-selection` and narrative-seed `arc-pipeline` (external, blocking); row 18 (`exchange` `trade-access`), row 17 (`conquest-consequences`, for the sector-changing-hands record)
- **Acceptance:** (1) no second penalty — a test compares stocks, roster and souls before and after a branch's first link opens and finds no debit caused by it; (2) loser only — the failure fact is written for the losing faction's save only (fog plus audience), and each trade failure fact has a reachability case in 25c.2; (3) embargo precision — `closesLastAccess` is true only when access to some traded good drops below `market` for every hub the faction could reach, and an eligible branch storylet is chosen over pool storylets on its host within the budget
- **Verify:** `.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Core/World/Trade/Stories/TradeFailureBranches.cs','tests/FusionRpg.Core.Tests/World/Trade/Stories/TradeFailureBranchTests.cs','tests/FusionRpg.Data.Tests/World/TradeFailureFactTests.cs') -Session <session-id>`
- **Shared files:** none from §4
- **Notes:** acceptance asserts the **coverage ask was filed**, never that content exists — a storylet count is a reading, not a contract. Catch-up pressure on the leader's busiest flows is `trade-ai`'s (row 19), deliberately not this task's. No trade-local branch engine

---

## CHECKPOINT 8 — Surface and stories

**Rows 24 and 25.**

**Pass condition, from the plan §3:** the player can see and steer all of it in the repo's locked
presentation libraries, in the `trade-lexicon` vocabulary — "unit", "enemy empires", no IP words, no named
boss. Trade storylets fire from producers' own facts through the `narrative` adapter, with every trigger
tested reachable.

---

## What this todo cannot close, and says so

Six honest gaps the planning fragments found. None is a reason to delay a task; each is a reason not to read
a green suite as proof.

1. **Tasks whose evidence lives in another program's suite.** 25b.4 (`trade-storylet-supply`) touches only
   `docs/**` and asks; its coverage join runs in narrative-seed's `narrative-metrics`. 25c.1
   (`trade-story-pacing`) cannot prove size-independence without npc's budget rule in `storylet-selection`.
   24d.2 and 24e.1 add no command kind and derive nothing — their admission and access tests belong to
   `logistics-flow`, `exchange` and `counterparties`.
2. **Criteria that are inert at their own landing, with a named owner and now a dated row.** 14.1's criterion
   2 and 14.2's criteria 2–4 wait on wave L5 (`field-battle-kinds`); 7.1's acceptance 2 is a row-8
   obligation sitting in a row-7 spec; L4.1's battle-presence clause is inert until L5.1 wires the join.
3. **Criteria that need a corpus or a catalog that does not exist yet.** 1.3 and 11.1 test against fixture
   and injected content (no banking row until 0c, no piece catalog until L7); 1.2's one-factor test only
   closes at 3.1; L3.1's parity half lands with `species-progression`.
4. **25c.2 (`trade-trigger-reachability`) is designed to carry `pending` entries** until producers land. A
   green run is not full coverage, and **no pending entry may be deleted to go green**.
5. **Two publish-only tasks have no focused suite of their own.** L8.1 and L9.1 are tuning publishes; their
   only evidence is the goldens they move plus `publish.py`'s own test, once L4.2 has added the
   `data/tuning/legion.v*.json` boundary row.
6. **Two cross-program asks still have no owner date:** ask X-11's `WorldValidation.cs` extension (R-20,
   default: 0e.1 ships without it) and `gk-core/data/tuning/narrative.v1.json` (R-18, default: 25c.1's rows stay a
   proposal until npc-story-events authors `v1`).

---

## DESIGN-GATE §5 checklist for this file

```
[x] Subsystems: world turn engine, canonical hash, world store and turn log, structures corpus, legion and
    seed corpora, tunables, power scale, verification boundary, FE presentation, narrative adapters.
[x] Read this session: landing-order.md (whole), trade-network-plan.md (whole), decisions-round-4.md Round 6,
    and all seven planning fragments (whole), each of which names the specs and maps it read.
[x] Order and phases cited, never inferred: landing-order.md §2 owns the order, §10 records the twenty
    reconciliation rulings applied here, and trade-network-plan.md §3 owns the phases and the checkpoint
    pass conditions, which are quoted rather than reworded.
[x] audit-doc-citations.py --scope run on this file.
[x] No criterion pins a population count, a corpus size, an item total or generated name/description text.
    Every acceptance bullet is carried from its spec unchanged except where a ruling in §10 changed a flag,
    a bump or a dependency; the only pinned literals are closed vocabularies, each with its stated reason.
[x] No new cap, no private power curve, no second composer, no magic number introduced by this file: it sets
    no number except bump ordinals, which are order, not balance.
[~] Session boundary: this file is docs-only. The implementing session records its own boundary in
    tasks/sessions/<session>.json and fences `paths` to the wave it lands.
[~] Nothing under docs/architecture/npc-story-events/** or docs/architecture/narrative-seed/** was touched;
    the two items that needed it are asks in landing-order.md §7.
```

- [ ] **DOC-NS5.7** (routed by notification-ssot, 2026-09-21) Four citations into the moved/deleted
  world-notify rail files are dead after the owner-accepted ask A1 (notification-ssot NS5.7–NS5.11):
  `docs/architecture/trade-network/trade-surface-map.md:134` and `:458`,
  `docs/architecture/trade-network/trade-surface/spec-trade-click-budget.md:25`,
  `docs/architecture/trade-network/trade-surface/spec-trade-notify.md:39`. The rail store is
  `gk-web/web/fusion-rpg-web/src/shell/notify/rail/railStore.ts` now, `clickBudget.test.tsx` is at
  `shell/notify/rail/clickBudget.test.tsx`, and `flush`/`onCommit` no longer exist anywhere.
- [ ] **DOC-NS5.2** (routed by notification-ssot, 2026-09-21)
  `docs/architecture/legion-build/spec-legion-count-cost.md:26` cites
  `gk-core/src/FusionRpg.Server/WorldEndpoints.cs:1013`; that file is 1003 lines now because notification-ssot's
  NS5.2 moved the report-fog rule out of it into Core `WorldReportVisibility` (ask A2). Re-anchor the
  citation — it points at a region after the moved code. Filed here because `docs/architecture/legion-build/**`
  is outside the notification-ssot lane's fence; route it to that spec's owner if that is not this program.

---

## Finding routed from `test-verification-boundary` (TVB-F15, 2026-09-21)

- [ ] **TVB-F15 (your share) — `doc-citations` is red on this program's docs at the merged head** ·
  `pwsh -NoProfile -File scripts/guard-doc-citations.ps1` exits 1 with HIGH findings in this program's
  documents: citations of `notifyRailStore.ts` / `categories.ts` / `notify/clickBudget.test.tsx` resolve to no
  tracked file at the cited path (D1), and `docs/architecture/legion-build/spec-legion-count-cost.md:26`
  cites `gk-core/src/FusionRpg.Server/WorldEndpoints.cs:1013` in a 1003-line file (D2). The guard is gating in CI, so
  CC8 stays red until the citations are re-anchored to the file's current path or the line says the file
  moved. Full list: `tasks/verification-boundaries-todo.md`'s TVB-F15 row (owning program:
  test-verification-boundary). Owning program here: this one.

- [ ] **TN-cite-1 — dead `doc-citations` cites left by the notification rail move (A1)** · XS ·
  *(filed by the manager 2026-09-21 from `scripts/guard-doc-citations.ps1`, red at the integration head.)*
  - `docs/architecture/trade-network/trade-surface-map.md:134` — D1 `` `notify/notifyRailStore.ts:23` `` — no
    tracked file with this name.
  - `docs/architecture/trade-network/trade-surface-map.md:458` — D3
    `` `notify/clickBudget.test.tsx:50-85` `` — a bare basename shared by more than one file; cite a path.
  - `docs/architecture/trade-network/trade-surface/spec-trade-click-budget.md:25` — D1
    `` `web/fusion-rpg-web/src/stages/world/notify/notifyRailStore.ts:18-23` `` — no tracked file with this name.
  - `docs/architecture/trade-network/trade-surface/spec-trade-notify.md:39` — D1, same retired path.
  - **Cause:** the `notification-ssot` program's owner-accepted **A1** moved the world rail to
    `gk-web/web/fusion-rpg-web/src/shell/notify/rail/` and retired the `stages/world/notify/**` copies, so these
    cites no longer resolve. The filing program owns the citing lines, not the moved file.
  - Fix: re-point each cite at the live path, or state on the citing line that the file is deliberately gone
    (the audit exempts a line that says so).
  - Verify: `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` → 0 HIGH.
