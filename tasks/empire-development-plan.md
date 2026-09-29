# Implementation Plan: empire-development

**Program:** `empire-development` (umbrella over `scoped-inventory-hierarchy` + `loam-relics-and-wonders`).
**Specs:** all 8 module specs + both sub-maps + the umbrella map are done and strengthened as of
2026-09-13 — see `docs/architecture/empire-development-map.md`, `docs/architecture/scoped-inventory-hierarchy-map.md`,
`docs/architecture/loam-relics-and-wonders-map.md`, and the 8 `docs/architecture/<sub-program>/spec-*.md`
files they index. This plan does not re-derive design; every task below cites the spec section that
already made the call, and points back to it for full reasoning, code snippets, and Design-gate
citations.
**Task list:** `tasks/empire-development-todo.md` (companion file — checkboxes only, this file carries
the reasoning).

## Overview

Two sub-programs, one dependency edge: `scoped-inventory-hierarchy` (five inventory scopes — legion
cargo, sector storage, cross-scope transfer, legion-death cargo fate) is a hard prerequisite for
`loam-relics-and-wonders`' `wonder-build-flow` module (spending a relic requires a real place to spend
it from). The other three `loam-relics-and-wonders` modules (relics as items, Wonders as structures,
the empire-wide production effect) have no dependency on `scoped-inventory-hierarchy` and build in
parallel with it.

One external prerequisite outside this umbrella: `cargo-fate` (scoped-inventory-hierarchy module 4)
needs `deployment-hierarchy`'s `corpse-cache`/`cache-decay-void`/`cache-field-access` trio to actually
exist in code — that program's specs were amended this session (new `place_kind='world_lane'`, reused
`place_kind='world_sector'`, new `source_kind='legion_death'`) to accept exactly the shape `cargo-fate`
needs. ~~Confirmed this session: none of `deployment-hierarchy`'s modules are built yet either (no
`RpgStore.CorpseCache.cs` exists). Phase 0 below builds the minimum slice of that sibling program this
plan actually needs~~ — **stale, corrected 2026-09-20** (`backlog-clean-up` `paperwork-reconcile` P7):
that file, and three of its four siblings (`RpgStore.CacheDecay.cs`, `RpgStore.CacheFieldAccess.cs`,
`RpgStore.CacheRetrieval.cs`), now exist — **this plan built the full trio (modules 3-6), not a
minimum slice**, and never looped back to update `deployment-hierarchy-map.md`/`-todo.md` to say so
(cause C3 in `program-pipeline-audit-2026-09-20.md`). See "Gates vs. checkpoints" note in Phase 0 for
why this was a real dependency, not a manufactured one, and why it was small enough to absorb here
rather than blocking on a separate plan.

## Architecture decisions this plan builds against (inherited, not re-decided here)

- **One ownership root, scope = overlay.** `rpg_item`/`rpg_item_stock` never gain a second owner
  column; every new scope (legion cargo, sector storage) is a reachability+capacity overlay table with
  no `player_id`/owner column of its own where the design calls for it (`decisions.md` "Scoped
  inventory hierarchy SSOT").
- **Move, never copy**, single transaction, for every scope-to-scope transfer and every death/capture
  event — proven precedent `corpse-cache` already established, reused verbatim by `cargo-fate`.
- **A Wonder is an orthogonal `StructureDef` facet, not a new `StructureKind` value** (`spec-wonder-structure.md`
  §Design 1) — `StructureKind` stays at 5 members.
- **A relic is a new sibling item kind (`DropEntryKind.Relic`), never a `unique` `KindSpec` variant**
  (`spec-relic-item-kind.md` §The schema decision) — `unique`'s 144-row corpus and validator suite are
  untouched by this whole program.
- **Empire-scope Wonder production is SUM, offset by a real per-turn upkeep proportional to the
  benefit** (`spec-wonder-effect-empire.md` §Design 3, §Design 6 — the upkeep term was added this
  session after an adversarial economy audit found the un-offset design risked recreating the exact
  "decay has no effect" failure mode the owner rejected when withdrawing the Warden mechanic).
- **`TurnEngine.Step` stays pure — every world-turn computation reads only already-loaded `WorldState`,
  never a live DB call mid-step.** Binding across every module that touches the turn engine.

## Task List

Tasks are grouped into phases matching the specs' own approved build waves. Within a phase, tasks with
no dependency on each other are parallelizable across agents/sessions (noted per task).

### Phase 0: External prerequisite — the `corpse-cache` trio (`deployment-hierarchy`)

**Why this is here and not a separate plan.** `cargo-fate` (Phase 2) cannot compile or be tested
without `rpg_corpse_cache`/`rpg_corpse_cache_item` existing, and this session amended that sibling
program's specs specifically to accept `cargo-fate`'s shape. This is a genuine code dependency, not an
approval gate (per the planning skill's "Gates vs. checkpoints" — check: is it irreversible? No, but it
is a real compile/runtime dependency, which behaves the same way a gate would if skipped: **it must be
built before Phase 2's `cargo-fate` task starts.** Named resolver: whoever picks up Phase 2. Stated
default: if `deployment-hierarchy`'s own plan has already built this trio by the time Phase 2 starts,
skip Phase 0 entirely and verify with `grep -rn "rpg_corpse_cache" gk-core/src/FusionRpg.Data` before starting
`cargo-fate`; if not, build it here — it is small, already fully spec'd, and this program is the one
that currently needs it. **Note on Task 0.3b specifically:** it was added late (this session, to close
a real spec gap — see Task 0.3b's own description), so a `deployment-hierarchy` plan written before this
gap was found will not include it even if it already built the rest of the trio — verify
`ClaimCorpseCacheIntoCargoUnlocked` separately with `grep -rn "ClaimCorpseCacheIntoCargoUnlocked" gk-core/src/FusionRpg.Data`
rather than assuming the trio-skip check above also covers it.

#### Task 0.1: `corpse-cache` — schema + death/wipe move (deployment-hierarchy module 3)

**Description:** Build `rpg_corpse_cache`/`rpg_corpse_cache_item` (two tables, header+contents shape)
and the move-on-`Retired`/move-on-wipe functions, per `docs/architecture/deployment-hierarchy/spec-corpse-cache.md`
§Design 1-3 — including this session's amendment: `place_kind` accepts `'lawn' | 'delve_room' | 'siege'
| 'world_sector' | 'world_lane'`, `source_kind` accepts `'death' | 'wipe' | 'legion_death'`.

**Acceptance criteria:**
- [ ] `rpg_corpse_cache`/`rpg_corpse_cache_item` exist with the exact column shape in §Design 1.
- [ ] `RetireUniqueActorUnlocked`'s both existing callers move the specimen's `rpg_item_assignment` rows
  into a cache in the same transaction; `rpg_player_item_assignment` is never read.
- [ ] `CloseDelve`'s wipe branch moves every party member's assignment + carry-in + haul into a cache,
  gated on the `loot-pack` §7 ask being accepted (spec §3 — verify this ask's status before starting;
  if still open, this sub-task is blocked and must be flagged, not silently skipped).
- [ ] **Core move mechanism vs. anti-fraud guarantee, distinguished explicitly** (`spec-corpse-cache.md`
  §Locked anchors, Structure table): the move-on-`Retired`/move-on-wipe mechanism itself (the two AC
  bullets above) is buildable now and has no external blocker. The **anti-fraud property** — that gear
  moved is provably the gear a specimen had at *deploy time*, never gear stripped mid-deployment to
  dodge the stake — is a second, separate guarantee that is **BLOCKED** on `SaveAssignment`/
  `RemoveAssignment` gaining a `Phase == Roster`-required gate (mirroring the expedition precedent at
  `RpgStore.Expeditions.cs:61-62`), an ask filed on the item program, not yet accepted. Ship the core
  mechanism; flag the anti-fraud guarantee as blocked-and-tracked, matching the same non-blocking
  treatment already given the `loot-pack` §7 ask (see Risks table).

**Verification:**
- [ ] Tests pass: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~CorpseCache"`
- [ ] Tests pass: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~Delve.CloseDelve"`
- [ ] `.\scripts\guard-dal.ps1` and `.\scripts\guard-actor-hub.ps1` green.

**Dependencies:** None.

**Files likely touched:** `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CorpseCache.cs` (new),
`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs`,
`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Items.cs` (where the blocked anti-fraud phase-gate lands, once the
item-program ask is accepted — `SaveAssignment`/`RemoveAssignment`, per `spec-corpse-cache.md`
§Locked anchors).

**Estimated scope:** M (3 files).

#### Task 0.2: `cache-decay-void` — the clock, amended for durable world-map places

**Description:** Build the decay clock and void transition per `docs/architecture/deployment-hierarchy/spec-cache-decay-void.md`,
including this session's V5 amendment: `world_sector`/`world_lane` caches start their decay clock
immediately but **never** flip `in_void` — unlike a lawn match or a closed delve room, a sector/lane is
a durable, revisitable place, so a cache there stays perpetually field-reachable rather than expiring.

**Acceptance criteria:**
- [ ] `TryStartDecayClockUnlocked` branches correctly on `place_kind` per the amended spec.
- [ ] A `world_sector`/`world_lane` cache never reaches `in_void=1` under any test scenario, including
  one that runs the decay clock far past the timeout that would void a `lawn`/`delve_room` cache.

**Verification:**
- [ ] Tests pass: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~CacheDecay"`
- [ ] `.\scripts\guard-dal.ps1` green.

**Dependencies:** Task 0.1.

**Files likely touched:** `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CacheDecay.cs` (new — schema,
`TryStartDecayClockUnlocked`, `TickCorpseCacheDecayForPlayerUnlocked`); `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CorpseCache.cs`
(module 3's file — one new line calling `TryStartDecayClockUnlocked`); **`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs`**
(one new line inside `CommitWorldTurn` calling `TickCorpseCacheDecayForPlayerUnlocked`, right before
its own `tx.Commit()` — the decay-clock's per-turn tick hook, per `spec-cache-decay-void.md` §Design 3/
§Structure).

**Estimated scope:** S-M.

#### Task 0.3: `cache-field-access` — reachability, amended for `world_sector`/`world_lane`

**Description:** Build field-access reachability per `docs/architecture/deployment-hierarchy/spec-cache-field-access.md`
§1a: a querying legion's live `WorldEntity.AtSectorId` (for `world_sector`) or `.OnLaneId` (for
`world_lane`) must match the cache's `place_ref` for it to be reachable.

**Acceptance criteria:**
- [ ] A legion standing at a sector can list/claim a `world_sector` cache pinned there; one standing
  elsewhere cannot.
- [ ] A legion on a lane can list/claim a `world_lane` cache pinned there; one on a different lane or at
  a sector cannot.
- [ ] The reachability read (§1/§1a) is correct standalone — the actual write into a legion's cargo
  overlay is a separate, sequenced-after task (0.3b, below): a genuine SPEC gap this session's audit
  found (`cache-field-access.md` §1a originally named `cargo-fate` as the write's owner, but
  `spec-cargo-fate.md`'s own Interface table shows nothing depends on it — it was never going to build
  the verb). The spec itself is now fixed (`spec-cache-field-access.md` §2a, amended 2026-09-13, later
  session) to own the write directly; this task builds only the reachability half.

**Verification:**
- [ ] Tests pass: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~CacheFieldAccess"`
- [ ] `.\scripts\guard-dal.ps1` green.

**Dependencies:** Task 0.1.

**Estimated scope:** S-M.

**Files likely touched:** `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CacheFieldAccess.cs` (new — schema,
`ListClaimableCachesUnlocked`, `ClaimCorpseCacheUnlocked`; per `spec-cache-field-access.md` §Structure).

#### Task 0.3b: `cache-field-access` — claim into legion cargo (world-map claim write, fixes a real spec gap)

**Description:** Build `ClaimCorpseCacheIntoCargoUnlocked`, per `docs/architecture/deployment-hierarchy/spec-cache-field-access.md`
§2a (added this session to close a real gap this plan's own adversarial audit found: §1a originally
named `scoped-inventory-hierarchy/cargo-fate` as the owner of this write, but `spec-cargo-fate.md`'s own
"Interface exposed to dependents" table states plainly that nothing in either program depends on
`cargo-fate` — it was never actually going to build this verb). The function reads a `world_sector`/
`world_lane` corpse-cache row the caller is proven reachable to (reusing §1a's own reachability query),
inserts each claimed row into the claiming legion's `rpg_world_entity_cargo` subject to `legion-cargo`'s
own weight/slot capacity gates (reusing `WeightCapacityUnlocked`/`SlotCapacityUnlocked`, refusing a
single over-capacity row rather than the whole claim), and deletes the claimed rows from the cache in
the same transaction (move-never-copy).

**Acceptance criteria:**
- [ ] A legion with headroom for every row in a reachable `world_sector`/`world_lane` cache claims all
  of them; the cache empties and `rpg_world_entity_cargo` gains an equal number of rows, in one
  transaction.
- [ ] A legion with room for only some rows claims exactly those, in `seq` order; the rest stay in
  `rpg_corpse_cache_item`, unclaimed — never a whole-claim refusal, never a partial-row insert.
- [ ] The reachability check re-runs at claim time, not just at the earlier list time — a stale/forged
  `cacheId` from a legion no longer at the matching sector/lane refuses `cache.unreachable`.
- [ ] Replaying an identical `(cacheId, worldId, entityId, correlationId)` claim is a no-op the second
  time (same replay-safety table shape as the delve claim).
- [ ] `legion-cargo`'s own `rpg_world_entity_cargo` schema and capacity functions are reused, never
  redefined — this task adds no second capacity formula.

**Verification:**
- [ ] Tests pass: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~CacheFieldAccess"`
- [ ] `.\scripts\guard-dal.ps1` green.

**Dependencies:** Task 0.3 (extends the same module's reachability read), Task 1.1 (`legion-cargo` —
`rpg_world_entity_cargo`'s schema and `WeightCapacityUnlocked`/`SlotCapacityUnlocked`, a genuine new
cross-program dependency this task introduces, named plainly in the spec's own header/checklist).

**Files likely touched:** `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CacheFieldAccess.cs` (same file as Task
0.3 — `ClaimCorpseCacheIntoCargoUnlocked`, per spec §2a), reading (never modifying)
`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.LegionCargo.cs`.

**Estimated scope:** S-M.

### Checkpoint: Phase 0 complete

- [ ] All of Phase 0's tests pass in one combined run.
- [ ] `guard-dal.ps1`/`guard-actor-hub.ps1` green.
- [ ] `grep -rn "rpg_corpse_cache" gk-core/src/FusionRpg.Data` shows the trio wired end-to-end.
- [ ] Review with human before Phase 2's `cargo-fate` task starts (Phase 1 does not depend on this and
  may proceed in parallel with Phase 0).

---

### Phase 1: Wave 1 — four independent modules, fully parallelizable

None of the four tasks below depend on each other or on Phase 0. Assign to separate
agents/sessions freely.

#### Task 1.1: `legion-cargo` — slot+weight cargo overlay

**Description:** Build `rpg_world_entity_cargo` and `LoadCargoUnlocked`/`UnloadCargoUnlocked`/
`TransferCargoUnlocked`, per `docs/architecture/scoped-inventory-hierarchy/spec-legion-cargo.md`.
Capacity = **every** member regardless of role (`memberCount × tuning.CargoWeightPerUnit`/
`CargoSlotsPerUnit`) — a deliberate divergence from `LegionSupply`'s Bearer-only precedent, confirmed
by the owner during `/spec`.

**Acceptance criteria:**
- [ ] `rpg_world_entity_cargo` exists with the exact column shape (`world_id, entity_id, seq, kind,
  instance_id, container_id, qty, weight_each`).
- [ ] `LoadCargoUnlocked` refuses `cargo.not-owned`/`cargo.over-weight`/`cargo.no-slots` correctly,
  before any write.
- [ ] `weight_each` is captured once at load time from the item's derived weight field, never
  re-resolved on read (§Design 4).
- [ ] Capacity uses **all** members, not Bearer-filtered — a regression test proves this explicitly.
- [ ] **`TransferCargoUnlocked` (legion-to-legion), covered explicitly — this is half the module's own
  stated objective, not an afterthought** (`spec-legion-cargo.md` §Design 5, §Testing strategy, §Success
  criteria #2): a transfer either fully succeeds (source loses the row, destination gains it) or fully
  fails (both unchanged) under a forced-failure test — no interrupted-transaction state ever
  observable; a transfer where the two legions' `OwnerFactionId`s resolve to different `player_id`s
  refuses `cargo.cross-empire`; the destination's own capacity gate (`cargo.over-weight`/
  `cargo.no-slots`) is checked before any write, same as `LoadCargoUnlocked`.

**Verification:**
- [ ] Tests pass: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~LegionCargo"`
- [ ] Tests pass: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~LegionCargo"`
- [ ] `.\scripts\guard-dal.ps1` green.

**Dependencies:** None.

**Files likely touched:** `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.LegionCargo.cs` (new), tests.

**Estimated scope:** M (2-3 files).

#### Task 1.2a: `sector-storage` — `StructureKind.ItemStorage` + capacity axis

**Description:** Add the 6th `StructureKind` value (`ItemStorage`) and `SectorItemCapacity.EffectiveCapacity`,
mirroring `LoamPhases.EffectiveCapacity`'s exact shape, per `docs/architecture/scoped-inventory-hierarchy/spec-sector-storage.md`
§Design 1-3.

**Acceptance criteria:**
- [ ] `StructureKind` has exactly 6 members, `ItemStorage` doc-commented like its siblings.
- [ ] `StructureDef.ItemStorageCapacityBonus: long` exists, optional at parse time (25 existing rows
  load byte-identical).
- [ ] `SectorItemCapacity.EffectiveCapacity` sums correctly across N active `ItemStorage` structures,
  provably independent of `LoamPhases.EffectiveCapacity` (a shared regression test proves both can move
  independently without affecting the other).

**Verification:**
- [ ] Tests pass: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~StructureCatalog|SectorItemCapacity"`
- [ ] All 25 existing structure seed rows unchanged (`StructureCatalogImportTests` — see Risks table for
  its own pre-existing pinned-count debt).

**Dependencies:** None.

**Estimated scope:** M (2-3 files).

#### Task 1.2b: `sector-storage` — table + capture hook

**Description:** Build `rpg_world_sector_storage` (no `weight_each`, no owner column) and the
sector-capture hook inside `DiffSectors`'s existing per-sector loop, per §Design 4-5. Confirms the
capture-transfer no-op: because the table has no owner column, reachability flips automatically the
instant `ClaimResolver` reassigns `sector.OwnerFactionId` — no migration code needed.

**Acceptance criteria:**
- [ ] `rpg_world_sector_storage` exists with the exact column shape (no `weight_each`, no owner column).
- [ ] A sector capture test: items already in storage at a captured sector are reachable by the new
  owner and unreachable by the old owner, with **zero** rows touched by the capture itself.
- [ ] **The capture hook fires inside the turn-commit transaction, not after it** (`spec-sector-storage.md`
  §Testing strategy): a forced-failure test, mirroring `legion-cargo`'s own atomicity test, proves a
  crash immediately after `DiffSectors`'s sector-owner write but before `tx.Commit()` leaves the
  sector's `OwnerFactionId` and its storage rows' observable reachability in the **same** pre-capture
  state — never one flipped and the other not.

**Verification:**
- [ ] Tests pass: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~SectorStorage"`
- [ ] `.\scripts\guard-dal.ps1` green.

**Dependencies:** Task 1.2a (needs `ItemStorage` kind to exist first).

**Estimated scope:** M (2-3 files).

#### Task 1.3a: `relic-item-kind` — KindSpec + enum + mint arm

**Description:** Register the new `relic` `KindSpec` (seedsmith + C# mirror), `DropEntryKind.Relic`
(10th member), `ContainerKind.Relic` (12th member), and the `MintRelic` arm that persists to `rpg_item`
only, never `item_generation` — per `docs/architecture/loam-relics-and-wonders/spec-relic-item-kind.md`
§Design 1-3.

**Acceptance criteria:**
- [ ] A relic anchor authors and loads without `frame`/`baseType`/`counterPressure`/`powerAxis`; the
  existing `unique` validator suite runs unmodified and green.
- [ ] **`a_relic_kindspec_has_no_reference_fields`** (`spec-relic-item-kind.md` §Testing strategy): the
  `relic` `KindSpec`'s own `refs` set is `{}` — a relic never points at a base type or role.
- [ ] A relic mints to a durable `rpg_item` row with a real `instance_id`; `item_generation` gains zero
  rows from that mint.
- [ ] **`mint_relic_produces_no_base_type_role_or_frame`** (`spec-relic-item-kind.md` §Testing
  strategy): the **persisted `rpg_item` row itself** carries none of the three — not merely that
  `item_generation` gains no row (the bullet above), but that there is nowhere on the `rpg_item` row to
  put them either.
- [ ] `DropTableDraw.UnavailableKinds` carries `Relic` until this task ships, mirroring `Unique`'s own
  pre-`MintUnique` history.

**Verification:**
- [ ] Tests pass: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Relic"`
- [ ] Tests pass: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~Relic"`
- [ ] `python -m seedsmith check gk-data/packs/fusion/data/seed/items --adapter items` (once relic anchors exist, Task 1.3c).
- [ ] `.\scripts\guard-dal.ps1` green; existing 144-row unique corpus tests green with zero edits to
  unique's own files.

**Dependencies:** None.

**Files likely touched:** `gk-forge/tools/seedsmith/seedsmith/adapters/items/kinds.py`,
`gk-forge/tools/ItemSeedValidator/Registries/KindCatalog.cs`, `gk-core/src/FusionRpg.Core/Items/Drops/DropTableModel.cs`,
`gk-core/src/FusionRpg.Core/Effects/Atoms/ContainerRow.cs`, `gk-core/src/FusionRpg.Core/Items/Drops/LootPipeline.cs`,
`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Loot.cs`.

**Estimated scope:** L (6 files) — **at the edge of this skill's size guideline; if it proves
unwieldy in one session, split along the Core/Data boundary** (enum+KindSpec+mint-signature in one
task, the actual `RpgStore.Loot.cs` host implementation in a second).

#### Task 1.3b: `relic-item-kind` — seedsmith `droptablegen` gains a `relic` `entryKind`

**Description:** The real, scoped generator sub-task this session's strengthen pass found: no existing
seedsmith command can append a new entry to an already-shipped `drop-table` row. Per §Design 4a: a 10th
`EntryKinds` member in `gk-forge/tools/ItemSeedValidator/Checks/DropTableCheck.cs`, a new `_relic_row` emit
function in `droptablegen/emit.py`, a `relic_refs`/`RELIC_SLOT_COUNT` slot in `brief.py`, a
`load_relic_ids()` reader in `tuning.py`, and a genuinely new **targeted append operation** that adds
one new `Relic`-kind group to an existing on-disk row through the same validate-then-`--write` path
every other kind uses.

**Acceptance criteria:**
- [ ] `DropTableCheck.cs`'s `EntryKinds` accepts `"relic"` and requires a resolvable `ref`.
- [ ] `_relic_row` raises `IllegalChoiceError` for a `ref` absent from the real relic corpus, mirroring
  `_insert_row`/`_consumable_row`.
- [ ] The append operation adds exactly one `Relic`-kind group to a named existing table id and leaves
  every other row/group in that file byte-identical.

**Verification:**
- [ ] Tests pass: `python -m pytest gk-forge/tools/seedsmith/tests/test_drop_tables_gen.py -q`

**Dependencies:** Task 1.3a (needs `DropEntryKind.Relic` to exist for cross-checking).

**Estimated scope:** M (4 files, Python-only).

#### Task 1.3c: `relic-item-kind` — content authoring (regeneration, never hand-edit)

**Description:** Author relic anchors and, via the Task 1.3b append operation, add one `Relic`-kind
entry to each of the seven real, wired `SourceKind` drop tables (`web-wave`/`expedition-tier`/
`world-sector`/`dungeon-room`/`dungeon-clear`/`dungeon-quest`/`siege-assault`). **Never a direct JSON
edit of an existing `_meta.model`-stamped file** — this is the exact hard-rule violation this session's
strengthen pass caught and fixed at the spec level; do not reintroduce it at build time.

**Acceptance criteria:**
- [ ] Every one of the seven `SourceKind`s resolves a drop table containing a `Relic` entry.
- [ ] `pvz-run` still refuses by name, unchanged, proving the refusal isn't accidentally bypassed by the
  new kind.
- [ ] Every touched `gk-data/packs/fusion/data/seed/items/drop-tables/*.json` file's diff is the output of the regeneration
  command, never a hand-typed edit — confirm via `git diff` that only the append operation's own
  machine-formatted output changed.

**Verification:**
- [ ] `python -m seedsmith items fill --kind drop-table --entry-kind relic --ref relic.<id> --drop-band
  <band> --write` (one per `SourceKind` table).
- [ ] Tests pass: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Relic"` (the
  per-`SourceKind` resolvability tests from Task 1.3a's own suite, now exercised against real content).

**Dependencies:** Tasks 1.3a, 1.3b. **Open content call, not architecture:** the exact drop
weight/rate per table is a genuine balance decision, not pre-decided by any spec — pick a low default
matching `unique`'s own low-weight precedent (per `spec-relic-item-kind.md` §Tunables) and flag it for
a balance pass, don't block on it.

**Estimated scope:** S (content only, no code).

#### Task 1.4: `wonder-structure` — vocabulary + `StructureDef` facet + `Validate`

**Description:** Ship `WonderScope`/`WonderRarity`/`WonderEffectKind`/`WonderEffectDef` and the
`StructureDef.WonderScope?`/`.WonderRarity?`/`.WonderEffects` orthogonal facet fields, plus the
`Validate` refusals that keep `World`/`Multiverse` and `DefensePower`/`AuraGrant`/`EmpireBuff`
unreachable, per `docs/architecture/loam-relics-and-wonders/spec-wonder-structure.md` §Design 1-6.
**Note the `Validate` snippet in the spec was corrected this session** (originally cited invalid C#,
`World.Sector` instead of `WonderScope.Sector`) — implement against the corrected version.

**Acceptance criteria:**
- [ ] `StructureKind` unchanged at 5 members.
- [ ] A `Sector`-scope Wonder row loads through the existing `StructureCatalog.All` pipeline and is read
  by the existing, unmodified `LoamProduction.For` — zero engine change needed for this case.
- [ ] `Validate` refuses `World`/`Multiverse` and each of `DefensePower`/`AuraGrant`/`EmpireBuff`
  individually, each with a message naming the reserved member.
- [ ] `Validate` refuses a `WonderScope`/`WonderRarity` pairing mismatch (one set, the other null).
- [ ] `Validate` refuses a `WonderEffectDef.Scope` that disagrees with its own row's `WonderScope`.
- [ ] `Validate` refuses a duplicate `(Kind, Scope)` pair within one row's `WonderEffects`.
- [ ] `WonderPolicy.ExistenceCapFor(scope, Common)` returns `long.MaxValue` for both live scopes, never
  a finite number.
- [ ] `WonderPolicy.ExistenceCapFor(scope, Unique)` reads the tunable file's own number — changing the
  tuning file's value changes the returned cap with no code change, proving it is data, not a constant.
- [ ] `WonderPolicy.ExistenceCapFor` throws before `Configure` runs, matching `LoamPolicy`'s own "no
  built-in default" discipline.
- [ ] All 25 existing structure seed rows remain byte-identical.

**Verification:**
- [ ] Tests pass: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~WonderCatalog|StructureCatalogImportTests"`
- [ ] `.\scripts\guard-dal.ps1` green (no SQL touched by this task at all).

**Dependencies:** None.

**Files likely touched:** `gk-core/src/FusionRpg.Core/World/StructureCatalog.cs`,
`gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs`, `gk-core/src/FusionRpg.Core/World/WonderCatalog.cs`
(new), `gk-core/src/FusionRpg.Core/World/Loam/WonderTuning.cs` (new), `gk-core/data/tuning/loam-relics-wonders.v1.json`
(new).

**Estimated scope:** L (5 files) — **candidate for splitting** (vocabulary+fields in one task,
`WonderPolicy`+tuning file+tests in a second) if it doesn't fit one session.

### Checkpoint: Phase 1 complete

- [ ] All four modules' test suites pass independently.
- [ ] `.\scripts\guard-dal.ps1`, `.\scripts\guard-actor-hub.ps1`, `.\scripts\guard-single-writer.ps1`
  all green.
- [ ] `python gk-core/scripts/audit-overflow.py` and `python gk-core/scripts/audit-magic-numbers.py` show no new
  critical findings introduced by this phase.
- [ ] Review with human before Phase 2. Phase 0 (if not already done in parallel) must also be complete
  before Phase 2's `cargo-fate` task specifically — the other three Phase 2 tasks do not wait on it.

---

### Phase 2: Wave 2 — four modules, each depends on one or two Phase 1 modules

#### Task 2.1: `cargo-transfer` — deposit/withdraw/legion-to-legion

**Description:** Connect `legion-cargo` and `sector-storage` via `DepositUnlocked`/`WithdrawUnlocked`
and a `SameFaction` helper (plain `FactionId` string equality, deliberately not resolving to
`player_id`), per `docs/architecture/scoped-inventory-hierarchy/spec-cargo-transfer.md`. **Note this
session's correction:** `WithdrawUnlocked`'s weight resolution was fixed — `rpg_world_sector_storage`
has no `weight_each` column (Task 1.2b's own design), so weight must be read fresh from the item's
derived weight field, the same mechanism `LoadCargoUnlocked` already uses, not a column read.

**Acceptance criteria:**
- [ ] `DepositUnlocked`/`WithdrawUnlocked` both refuse `cargo.cross-empire` correctly using
  `SameFaction`'s plain string-equality check.
- [ ] `WithdrawUnlocked` resolves weight fresh from the item's own derived field (regression test
  against the corrected design — reading a nonexistent `weight_each` column must fail loudly if
  reintroduced, not silently return zero).
- [ ] Never touches `rpg_item.player_id`/`disposition`.
- [ ] **Presence gate refuses:** a legion not at the sector refuses `cargo.not-present`, no write on
  either table (`spec-cargo-transfer.md` §Testing strategy).
- [ ] **Faction gate refuses against a same-turn ownership change:** a legion at the sector but
  belonging to a different faction than the sector's *current* owner refuses `cargo.wrong-faction`,
  tested against a sector whose owner just changed this same turn — proving the check reads live
  state, never a stale value.
- [ ] **Both capacity gates refuse independently:** a deposit into a full sector refuses
  `cargo.sector-full` without touching the legion's own cargo; a withdraw that would overweight the
  legion refuses `cargo.over-weight` without touching the sector's storage.
- [ ] **Atomicity under forced failure:** a crash between the delete and the insert (either direction)
  leaves the pre-transfer state fully intact on replay, mirroring both dependency modules' own
  atomicity tests; deposit is separately proven to move (never copy) by row count, not just absence of
  an error.

**Verification:**
- [ ] Tests pass: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~CargoTransfer"`
- [ ] `.\scripts\guard-dal.ps1` green.

**Dependencies:** Tasks 1.1, 1.2a, 1.2b.

**Estimated scope:** M (1-2 files).

#### Task 2.2: `cargo-fate` — legion-death cargo cache

**Description:** Hook `DiffEntities` (before its existing `DeleteMissing` call) to move a destroyed
legion's cargo into a `corpse-cache` row, per `docs/architecture/scoped-inventory-hierarchy/spec-cargo-fate.md`
§Design 1-2 (fully resolved this session — sector death uses `place_kind='world_sector'`, lane death
uses the new `place_kind='world_lane'`, both tagged `source_kind='legion_death'`).

**Acceptance criteria:**
- [ ] A destroyed legion's cargo is provably moved into a `corpse-cache` row **before** the entity row
  itself is deleted — the exact `ON DELETE CASCADE` race this session's audit found and ordered around.
- [ ] Sector-death and lane-death both produce a correctly-keyed cache row; a legion with no cargo
  produces no empty cache row.
- [ ] A legion with neither `AtSectorId` nor `OnLaneId` set is unreachable per `WorldState.cs`'s own
  invariant — no destroyed-outright fallback path exists or is needed.

**Verification:**
- [ ] Tests pass: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~CargoFate"`
- [ ] `.\scripts\guard-dal.ps1` green.

**Dependencies:** Task 1.1 (`legion-cargo` — the `rpg_world_entity_cargo` schema this module moves rows
out of), **Phase 0 complete** (external — `corpse-cache`'s `ResolveOrCreateCacheUnlocked` must exist).
**Corrected from the map's own wave-2-depends-on-wave-1 framing:** the capability map places this task
after `cargo-transfer` (Task 2.1), but `spec-cargo-fate.md`'s own design (§Design 1-2) never calls any
`cargo-transfer` function — its real code dependency is `legion-cargo`'s schema plus Phase 0, both
Wave-1/Phase-0 items. The wave-based map framing is coarser than the actual code dependency; noted here
so a reader does not wonder why the listed dependency changed from the map's own row.

**Estimated scope:** S-M (1-2 files).

#### Task 2.3a: `wonder-effect-empire` — faction-input plumbing + the SUM

**Description:** Add the `int scopeModifierMilli` parameter to `LoamProduction.For`, restructure
`LoamPhases.Production` into decrement-all → compute-per-faction-sum → compute-yield, and build
`WonderEmpireEffects.ComputeScopeModifierMilli`, per `docs/architecture/loam-relics-and-wonders/spec-wonder-effect-empire.md`
§Design 1-3.

**Acceptance criteria:**
- [ ] Zero-Wonder byte-identity: every existing Loam golden that authors no Empire-scope Wonder is
  unchanged.
- [ ] SUM, not max or replace: two built Empire-scope Wonders, 200 and 300 milli, produce exactly 1500.
- [ ] Same-pass activation: a Wonder finishing construction this exact Production phase already
  contributes to this same phase's sum.
- [ ] Lost-sector drop-out: losing the sector holding a faction's only Empire Wonder returns
  `ScopeModifierMilli` to 1000 the very next Production phase, no residue.
- [ ] **`checked`-overflow regression test, named explicitly** (`spec-wonder-effect-empire.md` §Testing
  strategy) — a synthetic scenario with a sum large enough to overflow the inherited `int`
  `ScopeModifierMilli` field throws `OverflowException` at the narrowing cast (`checked((int)(1000 +
  sum))`), never wraps to a negative or wrapped-around modifier.

**Verification:**
- [ ] Tests pass: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~WonderEmpireEffects|LoamPhasesTests|LoamProductionTests"`

**Dependencies:** Task 1.4.

**Estimated scope:** M (3 files: `LoamProduction.cs`, `LoamPhases.cs`, `WonderEffectEmpire.cs` new).

#### Task 2.3b: `wonder-effect-empire` — SQL persistence + three secondary call sites

**Description:** Close the `ScopeModifierMilli` persistence gap (new `scope_modifier_milli` column via
`EnsureColumn`, wired into `WriteWorldGraphUnlocked`/`LoadWorldGraphUnlocked`/`DiffFactions`) and update
`LoamForecast.ProjectedStock`/`LoamBalance.PerSector`/`WorldEndpoints.cs`'s debug view to resolve and
pass the stored modifier rather than silently under-reporting, per §Design 4-5.

**Acceptance criteria:**
- [ ] A world saved with a faction at `ScopeModifierMilli == 1500`, reloaded, reads back 1500 — not the
  record default 1000.
- [ ] The value survives a turn-commit `DiffFactions` pass unchanged when nothing about that faction's
  Wonders changed.
- [ ] All three secondary call sites report the same yield for a sector as `LoamPhases.Production` would
  compute for it, given the same `WorldState`.

**Verification:**
- [ ] Tests pass: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~WorldGraph"`
- [ ] `.\scripts\guard-dal.ps1` green.

**Dependencies:** Task 2.3a.

**Estimated scope:** M (4 files: `RpgStore.World.cs`, `RpgStore.WorldGraphDiff.cs`, `LoamForecast.cs`,
`LoamBalance.cs`, `WorldEndpoints.cs` — **at the edge of size guideline**, split by Data/Core boundary
if needed).

#### Task 2.3c: `wonder-effect-empire` — the upkeep term (owner-requested addition)

**Description:** Add the fifth `LoamUpkeepBreakdown` term (`WonderUpkeep`), charged to the Wonder's own
hosting sector, proportional to `ValueMilli × EmpireWonderUpkeepRateMilli / 1000`, per §Design 6 (added
this session after the owner explicitly chose to offset the economy risk now rather than defer). This
is the mechanism that makes losing a Wonder's sector a real, felt loss, not just a benefit that vanishes
— it reuses `LoamPhases.Pressure`'s existing per-sector-drawn/per-component-faded mechanism verbatim.

**Acceptance criteria:**
- [ ] `LoamUpkeepBreakdown` gains `WonderUpkeep` as a fifth additive field; `Sum`/`Total` include it.
- [ ] `Breakdown(...)`'s new trailing parameter is defaulted (`= 0`) so every existing call site
  (including the belief-side overload, deliberately left at 0) compiles unchanged.
- [ ] `EmpireWonderUpkeepRateMilli` lives in `LoamPolicy`/`data/tuning/loam.v{n}.json`'s existing
  `upkeep` block — **not** `WonderPolicy`/`loam-relics-wonders.v1.json`.
- [ ] A faction that lets a Wonder's hosting sector/component starve loses the Wonder outright (the
  existing lost-sector branch already clears the slot); `ScopeModifierMilli` recomputes down the very
  next Production phase with no new bookkeeping.
- [ ] **Sum-then-divide, not divide-then-sum** (`spec-wonder-effect-empire.md` §Design 6's own dedicated
  reasoning paragraph and §Testing strategy) — two Empire-scope `LoamGenerationRate` effects on the same
  sector produce the same `WonderUpkeep` as one effect authoring their combined `ValueMilli`, proving
  `Σ(ValueMilli) × rate / 1000`, never `Σ(ValueMilli × rate / 1000)`; use a deliberately non-round
  `ValueMilli`/rate pair so the two orderings would disagree if the wrong one were implemented (mirrors
  `LoamUpkeepTests.The_formula_divides_only_once_not_once_per_multiplier`'s own proof shape).
- [ ] **`checked`-overflow proof for the new multiply:** a synthetic `ValueMilli`/`EmpireWonderUpkeepRateMilli`
  pair large enough to overflow `long` throws `OverflowException` at the multiply, never wraps.
- [ ] **Same-pass activation parity:** a Wonder whose `ConstructionTurnsRemaining` reaches zero this
  exact Production pass already contributes both its `ScopeModifierMilli` share and its `WonderUpkeep`
  charge this same Pressure phase — not the phase after, for either side.
- [ ] **Belief-overload-unaffected regression:** `LoamUpkeep.For(int, int, int, int, int, int)` (and its
  only real caller, `FrontierRulesPolicy.cs:192`) returns the identical value before and after this
  addition, proving the new defaulted trailing parameter changed no existing behaviour.

**Verification:**
- [ ] Tests pass: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~LoamUpkeep"`

**Dependencies:** Task 2.3a (reads `WonderEmpireEffects.EmpireLoamGenerationValueMilliFor`).

**Estimated scope:** S-M (2 files: `LoamUpkeep.cs`, `LoamPolicy.cs`). **Open, non-blocking:** the
provisional rate (`50`) named in the spec is a real balance number with no playtest data behind it yet
— ship with it, flag for a balance pass, do not block this task on getting it "right" first.

#### Task 2.4: `wonder-build-flow` — Core-side (buildable now, no external dependency)

**Description:** Per `docs/architecture/loam-relics-and-wonders/spec-wonder-build-flow.md`'s own
"External dependency status" table — everything that touches only `WorldState`/`StructureDef` and needs
neither a relic instance's real ownership nor `scoped-inventory-hierarchy`'s tables: `WorldCommand
.RelicInstanceIds`, `StructureDef.RelicCost` + `Validate` pairing rule, the admission-time count/dup
check, `WonderExistenceScan.CountExisting`, and the `BuildResolver.Run` extension (cap check +
**the pre-existing rubble/ironwork wiring-gap fix**, independent of Wonders entirely).

**Acceptance criteria:**
- [ ] An ordinary, non-Wonder `build` order is unaffected — zero behavior change for the 25 shipped
  structure rows.
- [ ] **The rubble/ironwork fix**: any structure (Wonder or not) with a nonzero `ConstructRubbleCost`/
  `ConstructIronworkCost` now correctly refuses/debits via `BuildResolver`, which never read those
  fields before this task — test this independently of any Wonder content.
- [ ] `WonderExistenceScan.CountExisting` counts a Wonder **the moment its build order is accepted**,
  not at completion — the session's own found-and-fixed existence-cap bypass (a regression test proves
  two `Unique`-rarity Wonders of the same scope cannot both be under construction at once).
- [ ] Admission refuses `relic.count-mismatch`/`relic.duplicate` correctly.

**Verification:**
- [ ] Tests pass: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~WonderBuild|BuildResolver"`

**Dependencies:** Task 1.4 (`WonderPolicy.ExistenceCapFor`, `StructureDef.WonderScope`/`.WonderRarity`).

**Files likely touched (corrected — the plan's own list omitted the wire-format parse site):**
`WorldCommand.cs`, `WorldCommandAdmission.cs`, `StructureCatalog.cs` [shared edit with Task 1.4 —
sequence after it], `gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs` (the `RelicCost`
optional wire-field parse site, per `spec-wonder-build-flow.md` §Design 2/§Structure — missing from
this task's original file list), `BuildResolver.cs`, `WonderExistenceScan.cs` (new).

**Estimated scope:** L (6 files, not 5 — crosses from the plan's own M/edge-of-guideline framing into
L territory once `StructureCorpus.cs` is counted correctly). **Split recommended**: the materials-fix +
cap-check + `StructureCorpus.cs` wire parsing in one task, the admission-time relic count/dup check
(`WorldCommand.cs`/`WorldCommandAdmission.cs`) in a second — do not silently absorb the extra file into
a single session without flagging it, per this plan's own size guideline.

### Checkpoint: Phase 2 complete

- [ ] All Phase 2 tasks' test suites pass.
- [ ] `.\scripts\guard-dal.ps1`, `.\scripts\guard-actor-hub.ps1` green.
- [ ] Within `scoped-inventory-hierarchy`: a legion can load cargo, transfer it to another legion or a
  sector, and — if destroyed — its cargo lands in a real corpse-cache row. End-to-end manual/integration
  check, not just per-module unit tests.
- [ ] Within `loam-relics-and-wonders`: a Sector-scope Wonder row (hand-authored test fixture) correctly
  boosts its own sector's loam yield with zero engine change; an Empire-scope one correctly sums into
  `ScopeModifierMilli`, persists across a save/load, and now correctly costs upkeep.
- [ ] Review with human before Phase 3.

---

### Phase 3: `wonder-build-flow` — Data-side (the final integration)

#### Task 3.1: relic reachability pre-check + spend, inside the real turn-commit transaction

**Description:** Per §Design 4, 6-7 — `ValidateWonderRelicCommandsUnlocked` (runs immediately before
`TurnEngine.Step` inside `CommitWorldTurn`, verifying every named relic instance is owned, unassigned,
reachable via `legion-cargo`/`sector-storage`, and not already claimed by an earlier command in the same
batch) and `SpendWonderRelicsUnlocked` (runs immediately after `DiffWorldGraphUnlocked`, deleting the
relic from wherever it sat and marking `rpg_item.disposition = 'consumed'`) — both inside the **same**
transaction `CommitWorldTurn` already opens.

**Acceptance criteria:**
- [ ] A Wonder-shaped `build` order with the correct relic count, affordable materials, an empty
  compatible slot, and headroom under the existence cap succeeds end-to-end, in one turn commit.
- [ ] **Move, never copy, stated explicitly** (`relic_spend_moves_never_copies`,
  `spec-wonder-build-flow.md` §Testing strategy): after a successful Wonder build, the relic's source
  cargo/storage row is gone **and** `rpg_item.disposition = 'consumed'`, asserted as mutually exclusive
  outcomes — never both still present, never neither changed.
- [ ] A relic named by an earlier command in the same batch cannot fund a second Wonder the same turn.
- [ ] A command dropped for any reason (cap, materials, wrong slot, unreachable relic) leaves every
  named relic's row and disposition completely untouched — the relic spend only fires for an accepted
  `"build.started:"` report line.
- [ ] A relic moved out of reach between order-filing and commit (by an unrelated command in the same
  batch) correctly refuses at commit time, not at admission.

**Verification:**
- [ ] Tests pass: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~WonderBuild"`
- [ ] `.\scripts\guard-dal.ps1` green.

**Dependencies:** Task 2.4 (this program's own Core-side work), Task 2.1 (`cargo-transfer`, completing
`scoped-inventory-hierarchy`'s own build — the actual hard external block this task has waited on since
the very first `/spec` session), Task 1.3a-c (a real relic instance to spend). **Distinguished
explicitly, same map-coarser-than-code pattern as Task 2.2's own correction (#8 above), but resolved
differently here:** `spec-wonder-build-flow.md` §Design 4/7 reads/deletes `rpg_world_entity_cargo`/
`rpg_world_sector_storage` rows directly and never calls `cargo-transfer`'s own functions, so the
literal compile/schema dependency is only Task 1.1 (`legion-cargo`) + Task 1.2b (`sector-storage`'s
table). Keeping Task 2.1 as a listed dependency here is a **deliberate choice, not an error**: this
task is the final integration of the whole `scoped-inventory-hierarchy` sub-program (per the map's own
sequencing and the spec's own "the actual hard external block" framing), so waiting for `cargo-transfer`
to ship — even though this task's own code never calls it — is "wait for the sibling program to be
done," not a code dependency. Stated so a reader does not mistake this for the same map-vs-code drift
Task 2.2 needed corrected.

**Estimated scope:** M (2 files: new `RpgStore.WonderBuild.cs`, `RpgStore.WorldTurns.cs` edit).

### Checkpoint: Phase 3 complete — full program integration

- [ ] End-to-end: mint a relic via a real drop table (Task 1.3c's content), carry it in a legion's cargo
  or deposit it into a sector's storage, spend it to build a Sector- or Empire-scope Wonder, observe the
  loam-production effect (and, for Empire scope, the upkeep cost) on the very next Production phase.
- [ ] Full test suite green: `dotnet test tests\FusionRpg.Core.Tests`, `tests\FusionRpg.Data.Tests`,
  `tests\FusionRpg.Guard.Tests`.
- [ ] All 5 boundary guards green (`guard-single-writer`, `guard-secondary-no-unity`, `guard-funnel-delta`,
  `guard-dal`, `guard-actor-hub`, `guard-test-substrate`).
- [ ] `python gk-core/scripts/audit-overflow.py` and `python gk-core/scripts/audit-magic-numbers.py` clean of new
  findings from this program.
- [ ] Ready for owner review / live deploy-play smoke test.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| `loot-pack` §7's own ask (Task 0.1's wipe-path sub-item) may still be unaccepted when Phase 0 starts | Med — blocks only the wipe-path half of `corpse-cache`, not the death path `cargo-fate` alone needs | Verify status before starting; if still open, ship the death path and flag the wipe path as a named, tracked follow-up rather than blocking Phase 0 entirely |
| `SaveAssignment`/`RemoveAssignment`'s Roster-phase gate (Task 0.1's own anti-fraud guarantee) is an unaccepted ask on the item program, not this program's to grant | Low — the core move-on-death/move-on-wipe mechanism works without it; only the "gear is provably deploy-time, not death-time" guarantee is unproven until it lands | Ship the core mechanism now; track the phase-gate ask against the item program, matching the `loot-pack` §7 row's own treatment above |
| `StructureCatalogImportTests` pins literal population counts (pre-existing debt, not introduced by this program) | Low — the numbers are correct today; the first real Wonder/`ItemStorage` seed row that ships will need a one-line bump | Not this program's to fix; note it in the PR that adds the first real row so the bump isn't mistaken for a test failure |
| Relic mint volume has no named sink beyond Wonder-spend (ideal doc Open question #9) | Low, deferred | Not blocking; a future balance pass watches relic-pile growth once content ships |
| `EmpireWonderUpkeepRateMilli`'s provisional value (`50`) has no playtest data | Med — could be too cheap (risk not actually offset) or too harsh (Wonders feel punishing) | Ship provisional, tunable (data file, not code), revisit after first real playtest |
| Tasks 1.3a and 1.4 both touch `StructureCatalog.cs`/related files independently (relic vs. Wonder additions are in different files, but both are Wave 1 parallel work) | Low — different files per spec's own Structure tables, but worth a merge-conflict check | Confirm at task-assignment time that 1.3a and 1.4 touch disjoint files before parallelizing; they do per each spec's own file list |
| Phase 0 duplicates work if a separate `deployment-hierarchy-plan.md` also builds the same trio | Low — wasted effort, not a correctness risk | Check for an existing `tasks/deployment-hierarchy-plan.md`/`-todo.md` before starting Phase 0; if one exists and already covers this, skip Phase 0 and link to it instead |

## Deferred, named future work

Three sibling specs each carry a "Notification hook — named, not built (strengthen pass, 2026-09-13)"
section — a real, player-relevant, currently-silent event this program creates with no in-band signal.
None of the three modules that carry these sections builds the hook; each names it so a future
notification-consumer session does not have to rediscover the event independently by re-reading three
specs:

- `spec-sector-storage.md` — a sector's storage becoming reachable/unreachable to a different owner the
  instant `ClaimResolver` reassigns `OwnerFactionId` (§5's own "no migration needed" mechanism); the
  affected player has no signal their stored items silently changed hands.
- `spec-cargo-fate.md` — a legion's cargo silently becoming a decaying-but-never-voiding, revisit-lootable
  cache on death; the player who lost the legion has no in-band signal their haul is sitting recoverable
  at a specific sector or lane.
- `spec-wonder-build-flow.md` — a Wonder finishing construction (a `TurnReportEntry` already fires,
  `"build.started:{structureId}"`, but nothing reads it as a player-facing signal) and a `build` order
  refusing on `wonder.cap-reached` (the player spent a turn filing an order that resolved to nothing,
  with no in-band explanation beyond the turn report).

All three name `docs/architecture/notification-ssot-ideal.md` as the eventual consumer and each states
it would reuse an already-written event (a table write, a `TurnReportEntry`) rather than needing a new
emission path. Not a task in this plan — carried here so a future session picks up all three at once
instead of finding them one spec at a time.

## Deferred, named future gap — world↔battle inventory bridge (owner-confirmed 2026-09-16)

No module in any map designs the transfer between world-map scopes (legion cargo, sector vaults) and
battle scopes (unique-actor loadout, delve PackGrid): legion cargo into a lawn battle as loadout, or
battle loot out into cargo/storage. Death is covered on both sides (corpse-cache, cargo-fate,
PackSettlement); the *living* transfer is not. Never promised by either ideal — not a dropped
requirement, the next visible hole. Options: a small cross-program idea under move-never-copy, or an
explicit loadouts-stay-personal decision. Canonical record:
`docs/architecture/empire-development-map.md` Open items (2026-09-16 bullet) — point future sessions
there, not here.

## Open Questions

None blocking — the `/spec` strengthen pass (2026-09-13) already resolved every architectural fork this
plan depends on. Two genuinely open **content/balance** decisions remain, both explicitly non-blocking
per their own specs:

- Exact relic drop weight/rate per `SourceKind` table (Task 1.3c) — pick a reasonable low default, flag
  for balance pass.
- `EmpireWonderUpkeepRateMilli`'s real value (Task 2.3c) — ship the spec's provisional `50`, flag for
  balance pass after playtest.

## Cross-program asks filed by this program (tracked, not blocking the build)

**Note (2026-09-20, `backlog-clean-up` `paperwork-reconcile` P7, rule 3):** this ask is the same one
tracked as this file's own **4B.3** (line 1204) and `empire-development-todo.md`'s **4B.3** (line
152) — three records of one ask. This prose paragraph is kept as the fuller writeup; 4B.3 in both
task files is the single checkbox to close when it lands.

- **Item program (`drop-volume` owner): runtime-corpus relic rows** (`spec-relic-item-kind.md` §Design
  4b, filed at build time 2026-09-13). This program ships everything technically required
  (`DropEntryKind.Relic`, `ContainerKind.Relic`, `MintRelic`, validator acceptance, 3 relic anchors,
  authored-corpus rows) — but `gk-data/packs/fusion/data/seed/loot/*.json` (the only corpus the game reads) has zero relic
  rows, so no live drop mints a relic until the item program adds one real-weight `Relic`-kind entry
  per runtime table backing the seven `SourceKind`s. No engine work needed on either side.
  Live-probe addition 2026-09-16 (4B.4): no producer imports `gk-data/packs/fusion/data/seed/items/relics/*.json` into
  `effect_container` either (`RelicEndpoints` serves definitions only) — same owner, same ask;
  and cargo-via-HTTP needs a real mass source at `TryResolveCargoWeight` (4A.1 named it).
- **Item program: `SaveAssignment`/`RemoveAssignment` Roster-phase gate** (anti-fraud guarantee, Task
  0.1) and **`loot-pack` §7 carry-in ask** (wipe path, Task 0.1) — both pre-existing, tracked in Risks.
- **Notification consumer (future session):** the three named-not-built hooks in "Deferred, named
  future work" above.

---

## Phase 4: Live-wire — the player-triggerable surface (added 2026-09-15, owner-directed)

**Why this phase exists.** A 9-agent playability audit (one per built feature, verdicts against the
ORIGINAL ideal docs, 2026-09-15) found: **2 DEAD-CODE** (`legion-cargo`, `cargo-transfer` — tested
store verbs, zero live callers), **7 WIRED-BUT-UNTRIGGERABLE** (everything else — real machinery on
real paths, no player trigger), **0 PLAYABLE**. The engine/store layer is proven; nothing a player can
click, file, or observe exists yet. Owner direction: extend this plan (not a new sub-program), full
scope including web UI, idea-ui phase staffed first under its own standard, deployment-hierarchy gaps
included.

**Audit evidence base (in-session reports, 2026-09-15):** `legion-cargo` DEAD-CODE (no command kind,
no endpoint, no UI, no read-back, no live weight source; spec-§reuse drift); `cargo-transfer`
DEAD-CODE (same; plus dropped-`playerId` and caller-supplied-`weightEach` drifts);
`sector-storage` (zero `ItemStorage` seed rows; Deposit triggerless); `cargo-fate` (death live on
real commit path; recovery zero callers); `relic-item-kind` (live corpus zero relic rows; authored
appends runtime-unreadable); `wonder-structure` (zero Wonder rows; zero UI); `wonder-effect-empire`
(SUM/persistence/upkeep proven on real paths; observes 1000/0 vacuously); `wonder-build-flow`
(REST DTO drops `RelicInstanceIds` — live entry severed at the API boundary); corpse-cache trio
(lawn death recovers, never retires — headline death→cache never fires; delve claim §2 unbuilt;
nothing consumes voided caches).

### Wave 4A — triggers (no UI; makes every verb HTTP-reachable)

#### Task 4A.1: cargo WorldCommands + admission + resolver

**Spec:** `docs/architecture/empire-inventory-surfaces/spec-cargo-commands.md` (six kinds, post-Step
pass, `DebitActCostUnlocked` seam, 3 drift repairs decided).

**Description:** New `WorldCommandKind`s (`load-cargo`, `unload-cargo`, `transfer-cargo`, `deposit-cargo`,
`withdraw-cargo`, `claim-cache`) + payload fields (`Seq`/`TargetEntityId`/`CacheId`/`CargoKind`/
`InstanceId`/`ContainerId`/`Qty` — never `weightEach` on the wire) + `WorldCommandAdmission`
arms + turn-phase resolver calling the `*Unlocked` verbs. **Spec-drift repairs included, decided:**
D1 HELPERS locked — deposit/withdraw/claim already consume the shared capacity helpers, no code
change required (spec-cargo-commands D1); D2 `playerId` RECORD — load/unload/transfer keep
derived-`playerId`, deposit/withdraw keep their absence as intentional, claim's accepted-but-ignored
`playerId` stays byte-identical (spec-cargo-commands D2); D3 server-side `weightEach`/`weightEachFor`
resolution from the derived weight field with loud `cargo.weight-unknown` refusal (keep the
loud-on-missing regression). **Implementation's first task:** name the server-side weight-lookup
function (none exists in code today — spec-cargo-commands §Design 4 honest gap). **Merge order
(shared record with wonder-rest):** this task and 4A.2 extend the same DTO + mapping for different
fields (cargo fields here, `RelicInstanceIds` there) — both land additively, neither reorders
existing lines, merge in either order, no dependency either way.

**Acceptance criteria:**
- [ ] Each verb files via `POST /api/world/{id}/commands` and resolves on commit; errors are the
  spec's named refusals verbatim (`cargo.not-present`/`wrong-faction`/`over-weight`/`no-slots`/
  `unreachable`/`cross-empire`/`not-found`/`not-owned`), zero writes on refusal
  (spec-cargo-commands §Testing strategy bullets 1–2).
- [ ] Per-kind resolve moves, never copies: each of the six kinds leaves source-minus-one /
  destination-plus-one by row count (spec §Testing strategy bullet 1).
- [ ] Claim skip-not-refuse + idempotency: mixed-fit claim reports `cache.claimed:<c>+<s>` with
  skipped rows still in the cache; re-committing the same `CommandId` returns the byte-identical
  recorded result (spec §Testing strategy bullet 3).
- [ ] Claim-before-decay: a claimed row is absent when the decay tick runs the same commit; a
  skipped row remains subject to it (spec §Testing strategy bullet 4).
- [ ] No-bump proof (scoped pre-pricing): existing golden suite green **plus** one new test
  asserting an old-log replay `StateHash` is unchanged with the pass present; `RulesetVersion`
  stays 10 (spec-cargo-commands §Design 5).
- [ ] Weight-probe extension + helper-reuse guard: resolver issues no `weight_each` read against
  sector/cache tables; no cargo `SUM`/`COUNT(*)` outside `RpgStore.LegionCargo.cs` /
  `RpgStore.SectorStorage.cs` (spec D1/D3 + §Testing strategy bullet 6).
- [ ] Admission matrix: each §Design 3 arm's malformed shape refuses with its named reason at
  submit (`entity.missing`/`cargo.kind-unknown`/`cargo.ref-missing`/`cargo.seq-missing`/
  `cargo.target-missing`/`sector.missing`/`cache.missing`) — spec §Testing strategy bullet 7.
- [ ] No verb is test-only: every `*Unlocked` function has a command-path caller, proven by grep.
- [ ] The three spec drifts are closed as decided above (D1 helpers locked, D2 recorded, D3
  server-side + regression extended).
- [ ] Action-economy seam only: the pass exposes the `DebitActCostUnlocked` seam with
  debit-after-refill order selected (spec-cargo-commands §Design 6) — numbers, allowance, and
  the debit body belong to 4A.6/4A.7/4A.8, not here.

**Verification:** `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~CargoCommand"` (new);
`dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~WorldCommandAdmission"`;
`guard-dal` green.

**Dependencies:** None.

**Files likely touched (spec-cargo-commands §Structure, 7 surfaces):**
`gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs` (6 kinds + 7 payload fields), `WorldCommandAdmission.cs`
(5 arms), `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs` (`CommandPayload`/`ReadCommandRow`/
hook site), `RpgStore.CargoCommands.cs` NEW (`CargoResolveUnlocked` + `DebitActCostUnlocked` stub),
`gk-core/src/FusionRpg.Contracts/WorldDtos.cs` (`WorldCommandRequest` fields), `gk-core/src/FusionRpg.Server/WorldEndpoints.cs`
(`/commands` mapping), `gk-core/tests/FusionRpg.Data.Tests/CargoCommands/` NEW.

**Estimated scope:** M (7 surfaces, all in one seam — at the edge; split resolver-vs-tests if unwieldy).

#### Task 4A.2: Wonder REST entry

**Spec:** `docs/architecture/empire-wonder-surfaces/spec-wonder-rest.md` (one-line mapping, no early
pass — admission owns refusals; merge-additive with 4A.1's DTO extension).

**Description:** `WorldCommandRequest.RelicInstanceIds` + `WorldEndpoints` mapping (the audit's
1-line-class fix) + FE mirror (`bus/world.ts` + `worldSelection.ts` `PendingOrder`/`toRequests`).
**No early pass — admission owns refusals** (`relic.count-mismatch`/`relic.duplicate` at
`WorldCommandAdmission.cs:116-118`; a third endpoint check is a SOLID fork — spec-wonder-rest
§Design 2). **Unknown `structureId` never reaches a `Get`** — the mapping copies the list
opaquely; admission owns `structure.unknown`. Merge-additive with 4A.1's DTO extension (neither
reorders existing lines, merge in either order).

**Acceptance criteria:**
- [ ] Mapping round-trip order-preserved: a `build` request with N ids reaches
  `WorldCommand.RelicInstanceIds` unchanged; absent/null reads as empty (spec-wonder-rest
  §Testing strategy).
- [ ] Admission over HTTP per-command: wrong count → `relic.count-mismatch`; repeated id →
  `relic.duplicate`; rest of batch unaffected (submit-time admission, never an endpoint pass).
- [ ] FE null-vs-`[]`: a relic order survives `PendingOrder` → `toRequests`; a no-relic order
  emits `null`, not `[]`-vs-`null` drift (existing `worldSelection.test.ts:163-173` stays green).
- [ ] No silent cleaning: blank/whitespace ids refuse at admission, never trimmed away.
- [ ] **Live proof owed (RPG-server-debug scope, real record, normal-path readback):** player files
  order over HTTP → commit advances → `build.started:{id}` + every named relic
  `disposition='consumed'` + both overlay rows gone + slot carries the Wonder with
  `constructionTurnsRemaining == BuildTurns` → after `BuildTurns` commits the structure stands
  (spec-wonder-rest §Design 4, 5 steps).

**Verification:** `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~WorldCommandAdmission"`;
`dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~WorldCommands"`;
`npm test -- worldSelection`; `npm run build`; `guard-dal` green (no new SQL).

**Dependencies:** None (merge-additive with 4A.1, no dependency either way).

**Files likely touched (spec-wonder-rest §Structure, 6 files):** `gk-core/src/FusionRpg.Contracts/WorldDtos.cs`
(`RelicInstanceIds`), `gk-core/src/FusionRpg.Server/WorldEndpoints.cs` (mapping line only),
`gk-web/web/fusion-rpg-web/src/lib/bus/world.ts` (TS mirror), `gk-web/web/fusion-rpg-web/src/stages/world/worldSelection.ts`
(`PendingOrder` + `toRequests`), `tests/FusionRpg.Server.Tests/World/` (mapping tests),
`worldSelection.test.ts` (round-trip test).

**Estimated scope:** M (6 files, Core/Server/FE slice).

#### Task 4A.3: cache discovery + claim endpoints + read-back DTOs

**Spec:** `docs/architecture/empire-inventory-surfaces/spec-claim-endpoints.md` (four routes,
presence-gated listing, `correlationId := CommandId`, production `weightEachFor` resolver,
one-scope read-backs).

**Description:** `GET` claimable-caches (per legion), `POST` claim filer (delegates to
`SubmitWorldCommands`, never a direct verb call), cargo contents/capacities + sector storage
read-back DTOs. **Passes no weight and resolves none** — request DTOs carry no weight field; the
production `weightEachFor` lookup is 4A.1's named first task (spec-claim-endpoints §Design 3).
Covers world-map claim (`ListClaimableCaches`/`ClaimCorpseCacheIntoCargo`) and the legion-cargo
read-back gap. No bulk route, no direct-mutation POST, no client fog logic.

**Acceptance criteria (spec-claim-endpoints §Testing strategy, all 10):**
- [ ] Presence-gated listing: legion on the cache's sector/lane lists it; one sector away lists
  nothing (`200` empty); both-set/neither-set legion lists nothing.
- [ ] Hidden-until-found body assert: a no-reachable-cache response contains zero cache ids; no
  `visible: false` member exists on the DTO (schema assertion).
- [ ] Unknown-vs-empty: unknown `entityId` → `entity.unknown`; known legion, no cache → `200`
  empty — asserted separately.
- [ ] Foreign-legion `entity.not-yours`: a legion owned by another faction refuses even when a
  cache is reachable at its position.
- [ ] Filer idempotency: same `CommandId` posted twice → second returns `Replayed: true`, one
  stored command row; missing `CommandId`/`CacheId` refuse at submit with zero writes.
- [ ] Filer-never-resolves: after POST, cache rows and cargo are untouched — the claim moves
  only at commit through the 4A.1 pass (file-vs-resolve, GG-15).
- [ ] One-scope reads: cargo read returns exactly the legion's rows, storage exactly the
  sector's; a probe asserts no cross-legion/cross-sector route exists.
- [ ] Refusals verbatim: every §Design 5 string byte-matches the verb's own string;
  `correlation.missing` asserts unreachable-on-this-path (named, never produced by the filer).
- [ ] No-weight-on-wire schema: no `weightEach`-shaped member on any of the four request DTOs.
- [ ] Stored-detail-not-replay: the committed `cache.claimed:<c>+<s>` line is read from the
  stored hot-tail report (post-trim re-derivation omits it — documented, not re-proven).

**Verification:** `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~CacheFieldAccess"`;
`dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~World"`;
`guard-dal` green (projection only, no new SQL).

**Dependencies:** 4A.1 (kinds + pass + `correlationId := CommandId` contract).

**Files likely touched (spec-claim-endpoints §Structure, 5 surfaces):**
`gk-core/src/FusionRpg.Contracts/WorldDtos.cs` (5 DTOs, additive), `gk-core/src/FusionRpg.Server/WorldEndpoints.cs`
(4 routes + filer), `gk-web/web/fusion-rpg-web/src/contract/types.ts` (`CargoView`/`VaultView`/`CachePinView`),
`gk-web/web/fusion-rpg-web/src/contract/adapt.ts` (3 folds), `gk-core/tests/FusionRpg.Server.Tests/WorldClaimEndpoints/`
NEW.

**Estimated scope:** L (5 surfaces across Server + FE contract + new suite — split Server-routes
vs FE-mirror if unwieldy).

#### Task 4A.4: Wonder catalog/slot wire (added 2026-09-15 strengthen pass — was an unowned orphan)

**Description:** Per `docs/architecture/empire-wonder-surfaces/spec-wonder-wire.md`: catalog DTO
extensions + slot facet + upkeep/production attribution + reachability read. The reads
composer/display require; without them owner-locked live counts are unrenderable.

**Acceptance criteria (spec-wonder-wire §Testing strategy):**
- [ ] Catalog identity round-trips: `standing-stones` → `Sector`/`Common`/`RelicCost=1`/
  `ExistenceCap=long.MaxValue`; `sunspire-throne` → `Empire`/`Unique`/`3`/tuning number;
  non-Wonder rows → `null`/`null`/`0`/`long.MaxValue`. Changing the tuning file moves the cap
  with no code change (tunable-read proof).
- [ ] Reserved tiers never reach the wire: a `wonderScope: "World"` row still fails `Validate`
  at startup, loud, never a wire value.
- [ ] Slot facet without a second fetch: slot with `standing-stones` projects scope/rarity inline;
  empty/unknown/non-Wonder → `null`/`null`; fog parity — facet visible exactly when
  `StructureId` is visible.
- [ ] Live counts count acceptance, not completion: two `Unique` of one scope with one still
  under construction count `2`; `Common` reads `0` (never scanned); Empire count identical
  across one faction's sectors, `0` for unowned/unseen.
- [ ] Upkeep operand reconciles: `Base+Garrison+Development+Danger+WonderUpkeep` through the
  four-factor `Total` reproduces `LoamUpkeep.For` exactly (ledger test extended to five terms —
  wire and ledger agree or the test fails).
- [ ] Production attribution reconciles: `WonderProductionContribution == For(stored) − For(1000)`;
  Wonder-free faction reads `0`.
- [ ] Reachability matches the gate: every id the `GET` returns passes
  `IsRelicSpendableUnlocked`; unknown/unpositioned legion reads `[]`; the read performs no write.

**Field inventory (exact names are the contract — spec-wonder-wire §Design 1–6):** catalog
`WonderScope`/`WonderRarity`/`RelicCost`/`ExistenceCap` (producer `StructureCatalog`/`WonderPolicy`,
route `GET /api/world/catalog`); slot `WonderScope`/`WonderRarity` (catalog join at slot projection,
fog-parity with `StructureId`); sector `WonderLiveCountSector`/`WonderLiveCountEmpire` (producer
`WonderExistenceScan.CountExisting`, owner-only; `Common` deliberately absent — reads `0`/uncapped
per GG-64) + `WonderUpkeep` (inside `upkeepBreakdown`, from the already-computed map, never a
second formula) + `WonderProductionContribution` (`For(stored) − For(1000)`); NEW
`WorldRelicReachabilityDto` + `GET /api/world/{worldId}/relic-reachability?entityId=&sectorId=&asFaction=`
(producer NEW `ListReachableRelicsUnlocked` — gate predicate minus batch `claimed` set); TS mirrors
in `bus/world.ts` + `SlotView`/`UpkeepBreakdownView`/sector extensions in `types.ts` + adapter lines
in `adapt.ts` land in the SAME diff (no-drift rule); `reproducedTotal` + `Sum` docs updated to five
terms (the fifth ledger ROW stays 4D.4's module).

**Verification:** `WorldCatalog`/`WorldState` route tests (new) + `ReachableRelic` Data tests +
`adaptWorldSlot`/`adaptWorldSector` FE tests + `npm run build` + `guard-dal` green.

**Dependencies:** 4B.1 (rows the wire describes).

**Files likely touched (spec-wonder-wire §Structure, 6 files):** `gk-core/src/FusionRpg.Contracts/WorldDtos.cs`
(+4/+2/+1/+3 DTO fields + NEW reachability DTO), `gk-core/src/FusionRpg.Server/WorldEndpoints.cs`
(catalog/slot/sector projections + NEW GET), `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WonderReach.cs` NEW,
`gk-web/web/fusion-rpg-web/src/lib/bus/world.ts` (TS mirrors), `gk-web/web/fusion-rpg-web/src/contract/types.ts`
(`SlotView`/`UpkeepBreakdownView`/sector), `gk-web/web/fusion-rpg-web/src/contract/adapt.ts` (adapter lines).

**Estimated scope:** L (6 files across Data/Server/FE — split wire-vs-mirror if unwieldy).

#### Task 4A.5: act-price-table (world-action-economy module 1)

**Description:** Per `docs/architecture/world-action-economy/spec-act-price-table.md`: six tuning
rows (`claimCostMilli` 250 / `depositCostMilli` 100 / `withdrawCostMilli` 100 / `loadCostMilli` 50 /
`unloadCostMilli` 50 / `holdAllowanceMilli` 250 — provisional content, balance-owned) + hold-allowance
number in `world.v{n}.json` movement + loader arms (incl. the three test bootstrap constructor updates).
Loader-only; goldens byte-identical. camelCase spellings exactly as keyed (`claimCostMilli`,
`depositCostMilli`, `withdrawCostMilli`, `loadCostMilli`, `unloadCostMilli`, `holdAllowanceMilli` —
prose or rows carrying another spelling is a defect). Reserved `clearCostMilli`/`sustainCostMilli`
are NOT accepted by the loader (half-present key worse than absent); no `buildCostMilli` reserved.

**Acceptance criteria (spec-act-price-table §Testing strategy):**
- [ ] Missing-key-per-key rejection: deleting each new key in turn rejects naming
  `movement.<key>` (T5, mirrors the dowse rejection).
- [ ] Non-integer rejects: string/float/negative for any new key rejects at load, not at debit.
- [ ] Round-trip: shipped `world.v{n+1}.json` parses to the §Design 1 values via
  `WorldTuningHub.Tuning.Movement.*`.
- [ ] No-golden-moves: full world-map golden set byte-identical (nothing reads the keys yet; any
  move is this module's defect, not "also a rebalance").
- [ ] Publish-via-tool + `_meta` note + old version stays (T4; revert = restore a file).
- [ ] Three bootstrap updates land in the same change (`ContractTuningTestBootstrap` Core + E2E,
  `WorldPolicyTestBootstrap` Server).

**Verification:** `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~WorldTuning"`;
`guard-single-writer` green.

**Dependencies:** None.

**Files likely touched (spec §Structure):** `data/tuning/world.v{n+1}.json` NEW VERSION,
`gk-core/src/FusionRpg.Core/World/WorldTuning.cs` (record + parse arms), `WorldTuning` tests,
3 test bootstraps.

**Estimated scope:** M (tuning + loader + tests).

#### Task 4A.6: budget-debit (world-action-economy module 2)

**Description:** Per `docs/architecture/world-action-economy/spec-budget-debit.md`: debit-after-refill
implementation (refill-minus-spent rejected with evidence), flat per-act lookup
(`claimCostMilli`/`depositCostMilli`/`withdrawCostMilli`/`loadCostMilli`/`unloadCostMilli` camelCase;
`transfer-cargo` enters the seam charged-0), `entity.spent` refusal, attempt-pays/refusal-free
precedence, replay-once-per-`CommandId`, re-hash after debit (corrected — `MovementRemaining` IS
hashed), `RulesetVersion` 10→11 + golden re-bless.
**Sequence note:** lands AFTER 4A.1 (inventory no-bump proof is scoped pre-pricing). AS BUILT
2026-09-15: 4A.7 landed first and carries 10→11, so 4A.6 rides 11 and bumps 11→12 on landing
(same earned-by-moved-golden rule); 4A.1's no-bump test pins the live `RulesetVersion`
dynamically (never a literal), so no test update is owed by the bump; 4A.8 rides 12 unless it
moves a golden itself.

**Acceptance criteria (spec-budget-debit §Testing strategy, 7 bullets):**
- [ ] Debit-after-refill: refill to 1000, one `deposit-cargo` (100) post-Step → DB reads 900; a
  marched-1000-to-0 legion still pays from the refill, never the exhausted leftover.
- [ ] Flat per-act: two identical `claim-cache` cost 250 + 250 regardless of member count/level/
  faction; transfer costs 0.
- [ ] Short budget refuses `entity.spent` with zero writes on cargo tables and zero budget change.
- [ ] Attempt-pays / refusal-free: `cache.unreachable` → no debit (free retry);
  `cache.claimed:0+N` all-skipped → full 250 debited; skipped rows still decay same commit.
- [ ] Replay debits once: re-commit of a recorded `CommandId` returns byte-identical detail with
  no second subtract; post-trim re-derivation replays Step + post-Step pass from the untrimmed
  command log and converges.
- [ ] Old-log hash: zero-priced-kind logs replay `StateHash`-identical on 11 (re-hash is a fixed
  point); a priced-kind log diverges by exactly debit + re-hash (bump justification).
- [ ] Hold-zero interim: before 4A.7 lands, a 0-budget garrison refuses `entity.spent` (no hole).

**Verification:** `WorldTurn` Core tests + `CargoCommands` Data tests + `guard-dal` +
`guard-single-writer` green.

**Dependencies:** 4A.5 (keys + loader), 4A.1 (seam site + pass order).

**Files likely touched (spec §Structure):** `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CargoCommands.cs`
(seam body + debit-once key), `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs` (`RulesetVersion`
10→11 ONLY), `gk-core/tests/FusionRpg.Data.Tests/CargoCommands/` (extended).

**Estimated scope:** M (seam + bump + tests).

#### Task 4A.7: hold-allowance (world-action-economy module 3)

**Description:** Per `docs/architecture/world-action-economy/spec-hold-allowance.md`: allowance rule
(`BudgetFor(Hold) => holdAllowanceMilli`, act money never march money) + `ReachMap` stance-gated
emptiness + held-gate `Move`-only lock (priced acts pass; short budget refuses `entity.spent` at
the debit site, never `entity.held`) + AI single-slot handling (Recover keeps the slot while
healing; holder acts flow through the existing ladder, no new rule) + `Hold => 0` comment rewrite
+ ash-waste fixture update. Rides the 4A.6 bump unless it moves a golden itself.

**Acceptance criteria (spec-hold-allowance §Testing strategy, 7 bullets):**
- [ ] Holder refills to the allowance (re-blessed dig-in test).
- [ ] Holder still cannot march: hold then `Move` drops `entity.held`, legion unmoved.
- [ ] Holder reach stays empty even with nonzero refill (existing test unchanged — the regression
  this exists to prevent).
- [ ] Holder priced act admitted, not held-dropped: a holder's non-`Move` command passes Reveal
  without `entity.held`; its budget refusal arrives from the debit site only.
- [ ] Healing holder spends its slot healing: holding legion with wounds files `StandFast`, no
  second order in the same `Decide` output.
- [ ] Upkeep ignores stance: holder and marcher with identical garrisons produce identical
  `LoamUpkeep` totals.
- [ ] Golden re-bless table: `StanceTests` dig-in + `MovementTurnTests` wild-pack move to the
  allowance (named, with reason); `ReachMapTests` hold-empty + held-march-drop +
  `FrontierRulesTests` Recover stay green; template goldens snapshotting `e-wild-pack-1`/
  `ash-waste` re-blessed naming this spec; any other move is this module's defect.

**Verification:** `ReachMap` + `Stance` + `FrontierRules` Core tests green.

**Dependencies:** 4A.5 (allowance key; rides 4A.6's version 11).

**Files likely touched (spec §Structure):** `LaneCost.cs` (refill arm + doc),
`ReachMap.cs` (stance gate), `TurnEngine.cs` (COMMENT only — gate carve-out),
`WorldTemplateCatalog.cs` (fixture), `StanceTests` + `MovementTurnTests` (re-bless).

**Estimated scope:** M (Core + fixture + re-bless).

#### Task 4A.8: claim-pricing (world-action-economy module 4)

**Description:** Per `docs/architecture/world-action-economy/spec-claim-pricing.md`: price wiring
for all five verbs (`claim-cache`→`claimCostMilli` 250 before the per-row loop after the
reachability re-check; `deposit-cargo`→100 / `withdraw-cargo`→100 / `load-cargo`→50 /
`unload-cargo`→50 after gates before the move; `transfer-cargo` enters the seam charged-0),
claim-vs-decay precedence, replay mapping, deposit-pipe proof, per-verb golden deltas. **Note:**
the `§Named` gap (cargo-commands load/unload paragraph) is ALREADY FIXED directly in the spec —
no plan action; the table-wins override (load/unload priced at 50) stands, and implementation
updates that one `cargo-commands` paragraph when the seam lands.

**Acceptance criteria (spec-claim-pricing §Testing strategy, 8 bullets + pipe + deltas):**
- [ ] Per-verb wiring: one claim (250), one deposit (100), one withdraw (100), one load (50), one
  unload (50) each leave the post-refill budget exactly `cost` lower; one transfer leaves it
  unchanged.
- [ ] Flat per-act: two identical claims cost 250 + 250 regardless of member count/level/faction.
- [ ] Attempt-pays: `cache.claimed:0+N` still debits 250; skipped rows decay same commit.
- [ ] Refusal-free: `cache.unreachable` / `entity.gone` / `entity.routed` → zero budget change.
- [ ] Short budget refuses `entity.spent` with zero writes.
- [ ] Replay debits once: re-commit returns byte-identical `cache.claimed:<c>+<s>` with no second
  subtract; double-POST returns `Replayed: true` with one stored row.
- [ ] Per-verb golden deltas: zero-kind logs hash-identical on 11; transfer-only identical; each
  priced kind diverges by exactly its debit (re-blessed in the same change).
- [ ] Deposit-pipe proof (§Design 3): each of the five verbs is a filed→admitted→committed→
  reported round trip asserting the exact detail string plus the exact post-refill budget.

**Verification:** `WorldTurn` Core + `CargoCommands` Data + `WorldClaimEndpoints` Server tests +
`guard-dal` + `guard-single-writer` green.

**Dependencies:** 4A.6 (seam body + order + refusal; rides 11).

**Files likely touched (spec §Structure):** `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CargoCommands.cs`
(per-verb seam calls), `gk-core/tests/FusionRpg.Data.Tests/CargoCommands/` (per-verb wiring + pipe proof).
`TurnEngine.cs` UNTOUCHED (11 already landed); tuning files UNTOUCHED.

**Estimated scope:** M (wiring + proof tests).

### Wave 4B — content (makes the machinery encounterable)

- [ ] **4B.1 Wonder seed rows** — `standing-stones` (Sector/Common, `relicCost: 1`) +
  `sunspire-throne` (Empire/Unique, `relicCost: 3`) per `spec-wonder-content.md` §Design 1–2.
  Authoring path RESOLVED: hand-author under `gk-data/packs/fusion/data/seed/structures/wonder/` (`AUTHORED`
  provenance; loader walks `*.json` recursively, no loader/plan edit). Validate acceptance
  (spec §Design 4): pairing holds (scope+rarity together, one `LoamGenerationRate` effect with
  `Scope == WonderScope`, `RelicCost >= 1`); reserved probes still refused loud (a `World`-scope
  probe fails naming the scope; `DefensePower`/`AuraGrant`/`EmpireBuff` probes fail naming the
  kind); exact-case spellings (`Sector`/`Empire`/`Common`/`Unique`/`LoamGenerationRate` —
  `Enum.Parse` without `ignoreCase` rejects any other casing). `relicCost` 1-vs-3 marks the
  Empire work dearer; effect `valueMilli: 0` is a balance-owned placeholder (Sector scope reads
  the row's own yield fields, Empire scope sums it). Cap-literal ban: rows and prose carry no
  cap number — `ExistenceCapFor(Empire, Unique)` returns the tuning file's number (prove by
  changing the file with no code change), `ExistenceCapFor(any, Common)` returns
  `long.MaxValue`. Verification: `StructureCatalogImportTests` byte-identical +
  `WonderCatalog` tests + `guard-dal` green.
- [ ] **4B.2 ItemStorage seed row** — `relic-vault` (bonus 20) per `spec-storage-content.md`
  §Design 1, at `gk-data/packs/fusion/data/seed/structures/store/relic-vault.json` (role dir `store/`, `Store` role +
  `Vault` slot). Same resolved authored path (§Design 2 ruling — hand-authored `AUTHORED`, NO
  generator fix owed): prove `write_corpus` survival (file byte-identical after regen, tree
  otherwise identical) + `test_structure_corpus.py` assert
  (`by_id["relic-vault"]["structureKind"] == "ItemStorage"`). Tests: catalog loads
  (`IsKnown`, `Kind == ItemStorage`, bonus 20); `EffectiveCapacity == 20` with one built vault,
  under-construction → 0, wrong-slot (`Wildland`) → `build.wrong-slot-kind`; granary `Storage`
  contributes 0 to the item axis (axes never bleed).
- [ ] **4B.3 Runtime-corpus relic rows** — item-program ask (§Design 4b); unblocks live drops.
- [ ] **4B.4 Live probe:** Wonder built → commit → boosted yield + upkeep + reload persistence,
  observed through the normal path (not test fixtures).

### Wave 4C — deployment-hierarchy gaps (owner: include all)

- [ ] **4C.1 Lawn-death producer** — needs design first (injury-tiers build vs explicit lawn→Retire
  trigger); investigate, propose, then build. Until then the headline death→cache never fires.
- [ ] **4C.2 Wipe path** — gated on `loot-pack` §7 (tracked); build on acceptance.
- [ ] **4C.3 Anti-fraud Roster gate** — item-program ask (tracked).
- [ ] **4C.4 Delve claim verb §2** (PackGrid + floor spill) **+ retrieval-mission module 6** (consumer
  for `in_void=1` caches) — module 6 is a full module build; spec pointer is
  `spec-cache-retrieval-mission.md`.

### Wave 4D — UI builds (ideals LANDED + answers recorded 2026-09-15 — the old pre-work gate's
premise is satisfied, so this wave is sequenced on owner-accept drafts per spec, not gated)

Locked UI directions (strengthen-pass reconciled): legion sheet-menu with sub-tabs (cargo one tab
— supersedes bare panel); fog pins hidden until found; header + toast on capture; panel composer
with reachable-first picking spanning sheet tab + sector store; live cap counts shown; reserved
tiers as locked teasers; `stock-row`/`capacity-meter`/shelf owned by the inventory program
(recommended, owner confirms at `/spec`).

#### Task 4D.1: legion-sheet build (spec `empire-inventory-surfaces/spec-legion-sheet.md`)

**Description:** Owner-accept HTML drafts first (review checkpoint inside the task — drafts are the
spec's §Design output, not a phase gate), then mount: sheet host + cargo-tab recipe, owned
`capacity-meter`/`stock-row` piece contracts, `cargo-fold`, closed `cargo-actions` bus, verbatim
refusal catalog, header/toast inputs.

**Acceptance criteria:**
- [ ] Drafts accepted by owner before mount (checkpoint, recorded).
- [ ] Overview tab + per-legion reset: sheet opens from legion select with `overview` default
  (cargo is NOT the default); switching legions resets to the default tab (spec-legion-sheet
  §Design 1 — tab ids a closed vocabulary with a stated reason).
- [ ] Sheet opens over the map (no new route); cargo sub-tab shows rows from `GET .../cargo` +
  two honest meters from the fold's four numbers; load/unload/hand-to-band file through 4A.1
  kinds; refusals render verbatim copy; close returns the exact map state (GG-12) and never
  clears the pending queue.
- [ ] Unknown-vs-empty: unknown legion → error-with-retry; known legion, empty packs →
  empty-with-next-action — asserted separately.
- [ ] One-scope probe: the tab issues exactly one legion's `GET .../cargo` per open/selection/
  commit-advance; no empire-wide fetch.
- [ ] File-vs-resolve: after filing, rows are untouched until commit (GG-15); the toast answers
  filing, the report + read-back answer resolution.
- [ ] No-`weightEach` bus schema: no `weightEach`-shaped member on any bus event or request.
- [ ] Closed-vocab fold: reason→copy-key mapping covers every §Design 7 wire string (including
  `correlation.missing` → no-copy and reserved `act.spent` key without a finalized sentence);
  the fold never recomputes capacity, never compares positions, never predicts fit, never
  prettifies an id (GG-15).
- [ ] GG-55: a known-unfilable action stays enabled and answers with the refusal sentence, never
  silent-disable.
- [ ] Shared pieces consumed by name downstream (wonder build references, never forks).

**Verification:** `npm test` (fold/bus unit + landmark tests); `npm run build`; `npm run check:bundle`
(route-split, never entry chunk); `guard-dal` green (no SQL).
**Dependencies:** 4A.1, 4A.3 (routes/DTOs to bind).
**Files likely touched:** `docs/design/gui-lego/pieces/capacity-meter.html`, `pieces/stock-row.html`,
`recipes/legion-sheet-cargo.html`, `web/.../contract/types.ts`, `contract/adapt.ts`,
`web/.../stages/world/legionSheet/` (new dir).
**Estimated scope:** M (6 files).

#### Task 4D.2a: storage-panel build (spec `empire-inventory-surfaces/spec-storage-cache-ui.md` §Design 1)

**Description:** Vault block inside the inspector block order (+1 `BLOCK_ORDER` id `vault`
appended after forces/facts and before warden/dowsing — NEVER reorder the nine existing ids),
`capacity-meter[room]`, put-in/take-out via 4A.1 kinds through the generic ActionCluster.
**Acceptance:** vault block renders room + rows for a sector with `relic-vault` (4B.2); deposit/
withdraw round-trips through real kinds; `data-block-order` reads `...,forces,vault,warden,...`;
`SlotCapacity == 0` binds locked-with-unlock-line naming `relic-vault` (GG-17 — the one new
lifecycle binding; empty vault with capacity binds `phase-empty`, the two never confused); room
meter binds `SlotsUsed`/`SlotCapacity` and never computes (probe asserts no capacity read, no
position compare); fog prohibition — zero position compares, zero void/empty filtering, zero
`visible: false` handling in the fold; winner-no-toast (header already says "held by" them —
toast is loser-directed only); one-scope probe (one sector's rows per open, no cross-sector
fetch); fits/left-behind fold — committed `cache.claimed:<c>+<s>` + stored skip lists paint
per-row states, every string byte-matching the verb; header always shows "held by X" from live
`OwnerFactionId`. **Never list:** `StoragePage.tsx` (developer archive console) and the Relics
"storage" tab (empire scope) are never the vault host.
**Verification:** `npm test`, `npm run build`, `guard-dal` green.
**Dependencies:** 4A.1, 4A.3, 4B.2.
**Files likely touched:** `docs/design/gui-lego/storage-panel.html`, `recipes/` (storage-panel),
`stages/world/inspector/` (vault section), `contract/` (VaultView folds).
**Estimated scope:** M (4-5 files).

#### Task 4D.2b: cache-claim + notify build (same spec, §§Design 2–4)

**Description:** Map `cache-pin` beside LegionMarker/LaneEdge (hidden-until-found — server gates, no
client fog logic), pin → prompt → fits/left-behind → pick-up filing `claim-cache` with "(N AP)"
slot bound to `claimCostMilli` (display slot only — the number is 4A.5's, bound once it lands,
never a local constant), capture header + loser toast/report entry off the event feed.
**Acceptance:** pin renders iff the selected legion's `ClaimableCacheListDto` lists the cache
(pin presence == response presence; structural assertion: no `visible: false` on the pin view,
no position-compare helper in the fold); claim flow files a real order (double-submit replays
on `CommandId`); capture shows header + exactly one loser toast via `NotifyRail`, winner gets
no toast; `BLOCK_ORDER` +1 discipline shared with 4D.2a (never reorder); one-scope probe (one
legion's list per selection); fog prohibition as in 4D.2a; fits/left-behind fold as in 4D.2a;
Never list as in 4D.2a.
**Verification:** `npm test`, `npm run build`, `guard-dal` green.
**Dependencies:** 4A.1, 4A.3 (claim routes), 4A.6 (AP cost to display).
**Files likely touched:** `docs/design/gui-lego/cache-claim.html`, `recipes/` (cache-claim),
`stages/world/render/` (pin), `stages/world/notify/` (toast), `contract/` (CachePinView folds).
**Estimated scope:** L (5 files across render + notify + contract + drafts — split pin-vs-toast
if unwieldy).

### Checkpoint: inventory UI
- [x] Sheet + vault + claim flows mountable against 4A routes with zero test-constructed commands.
- [ ] `npm run build` + landmark tests green; bundle budget held.
- [ ] Re-hash proof: post-debit hash stored and describes the committed state (4A.6 correction).
- [ ] AP display bound: pick-up "(N AP)" reads `claimCostMilli` (4A.5's key, 4A.6's spend) — no
  local constant.
- [ ] Capture header + loser toast proven off the report entry (winner gets no toast).
- [ ] Review with human before wonder UI (shared pieces freeze here — wonder consumes).

#### Task 4D.3: wonder-composer build (spec `empire-wonder-surfaces/spec-wonder-composer.md`)

**Description:** Owner-accept drafts first (checkpoint), then panel composer: reachable-first picking
(sheet tab + sector store — where-it-sits truth stays the sibling overlay's; this fold only
joins it), live cap counts (requires 4A.4 fields — no placeholders; pre-wire the fold shows the
designed pending state, never a guessed number), locked teasers, cost-plate, four-reason refusal
fold, closed `wonder-composer.*` bus. Packs are NOT built here (4D.4 owns them — coordination
note, no twin files).
**Acceptance:** composer files a real Wonder order over 4A.2 wire against 4B.1 rows; slot tree
per §Design 1 (tool-search + split-inspect catalog/relic-shelf + slot-pick + cost-plate + band-3
confirm + lifecycle overlays); fold renders the 6 readings (catalog rows, reachable-first
candidates, live cap counts, slot compatibility, affordability, locked teasers) with the
prohibitions held (no bare per-mille, no id-words, no second palette/shell/density); bus carries
the 6 closed events (`search.set`/`wonder.select`/`relic.toggle`/`slot.select`/`confirm`/`retry`,
GG-15 pending on file); cost-plate shows the 5 lines (relic foundation k-of-N, stone+ironwork
vs stores, nights, blessing reading, upkeep note); refusals map the 4 rows (`wonder.cap-reached`/
`relic.count-mismatch`/`relic.not-reachable`/`build.cannot-afford-materials`) with next actions
and nothing consumed; themeRefs/catalog rows owed per §Design 6 (scope/rarity packs, display
catalog incl. locked-teaser reasons + unknown-id placeholder); 6 draft states owner-accepted
(catalog + reachable shelf + cost-plate + confirm + refusal toasts + lifecycle) before any TSX —
the owner-accept gate.
**Verification:** `npm test -- wonderComposer`, `npm run build`, `guard-dal` green.
**Dependencies:** 4A.2, 4A.4, 4B.1, 4D.1 (shelf/tab to pick from).
**Files likely touched:** `recipes/wonder-composer.json`, `pieces/wonder-*.html` (drafts),
`features/gui-lego/foldWonderComposerVm.*`, `features/gui-lego/wonderComposerBus.*`.
**Estimated scope:** L (recipe + fold + bus + 6 drafts + catalog rows — split composer-vs-refusal-fold
if unwieldy; drafts-accept is a checkpoint inside the task, not a phase gate).

#### Task 4D.4: wonder-display build (spec `empire-wonder-surfaces/spec-wonder-display.md`)

**Description:** Sector-card recipe, `wonder-scope-*`/`wonder-rarity-*` theme packs (BUILT ONCE HERE —
4D.3 references by contract), GG-62 display catalog (`gk-data/packs/fusion/data/seed/display/wonder-display.v1.json`,
path to confirm), construction-progress sentence, shelf-consume by name. Runs ∥ with 4D.3 (packs
contract-first; composer never creates pack files).
**Acceptance:** sector card renders identity/effect/progress for both 4B.1 rows (authored names +
themed badges + effect sentences — zero raw ids); reserved tiers render locked teasers with
reasons (never buildable); all four refusal reasons map to copy + next action with nothing
consumed; unknown ids hit the placeholder rule (designed placeholder + `card.expand`, never the
id); under-construction renders name + "rising — N nights left" + shared meter, built renders
no progress slot; fifth ledger ROW lands here (operand + test-doc update rode 4A.4 — the W62/W63
drift class); pending-state rule — pre-wire cap lines render the designed pending state, never a
guessed number and never a hidden row.
**Verification:** `npm test -- SlotRow`, `npm test -- ModifierLedger`, `npm run build`, `guard-dal` green.
**Dependencies:** 4B.1, 4A.4 (wire fields), 4D.1 (meter/row twins risk — shared `capacity-meter`/
`stock-row` consumed by name, never forked; freeze from the inventory-UI checkpoint applies).
**Files likely touched:** `recipes/wonder-sector-card.json`, `themes/packs/wonder-scope-*.json`,
`themes/packs/wonder-rarity-*.json`, `gk-data/packs/fusion/data/seed/display/wonder-display.v1.json`, sector-card mount.
**Estimated scope:** M (5 files).

### Checkpoint: wonder UI
- [x] Composer + display bind live 4A.4 fields with zero placeholders.
- [x] Live N-of-cap proven: `Unique` cards render "N of cap raised" from `WonderPolicy` numbers
  (tuning change moves the line, no code change); `Common` renders buildable-on-cap-grounds.
- [ ] `npm run build` green; packs consumed (never forked) by both surfaces.
- [ ] Review with human before 4B.4 probe + 4C builds.

### Checkpoint: Phase 4 complete — the game is playable like the idea

- [x] Every Phase 0-3 verb has an HTTP-reachable trigger or a named, tracked reason it doesn't.
  (verified 2026-09-16: six kinds + filer + 6 read routes; tracked: 4B.3, 4C.2, 4C.3)
- [x] `RulesetVersion` 12 with per-verb golden deltas (4A.7 took 10→11, 4A.6 rode to 12; 4A.8 delta
  table); zero-kind and transfer-only logs hash-identical.
- [x] Live probe: earn relic → carry → build Wonder → observe yield + upkeep (4B.4 real server :5099,
  GET readback; yield correctly 0 on placeholder rows; owner live deploy-play smoke still required).
- [x] Full suite + all guards green modulo confirmed-foreign (Core 13762 + dungeon CRLF; Data 1503 +
  creature drift; Guard 314/314; 6/6 guards; web build green, 10 foreign guard fails); audits: overflow
  0 empire deltas; magic-numbers 5 CacheDecay + 1 retrieval documented starting-shape (no re-litigation).
- [x] Scope-creep check clean: no World/Multiverse buildable tier, no cross-faction spend, no
  second pool — verified by grep over the Phase 4 diff before sign-off.
