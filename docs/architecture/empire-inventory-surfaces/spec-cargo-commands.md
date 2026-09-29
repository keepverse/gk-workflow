# Spec: `cargo-commands`

**Status: written against shipped code 2026-09-15** — every `file:line` below was opened this
session in worktree `empire-development-20260915-b7e2`. Module id `cargo-commands`, row 1 of the
[empire-inventory-surfaces map](../empire-inventory-surfaces-map.md) (wave 1, no dependency).
Ideals: [empire-inventory-surfaces-ideal.md](../empire-inventory-surfaces-ideal.md) §§4–5 (verbs are
built, no player path reaches them), §7 (closed `cargo-actions` bus direction), §8 + Owner
resolutions (legion sheet-menu direction, AP-cost lock); [world-action-economy-ideal.md](../world-action-economy-ideal.md)
Locked constraints (debit order, deposit pipe). Backend SSOTs:
[scoped-inventory-hierarchy/spec-cargo-transfer.md](../scoped-inventory-hierarchy/spec-cargo-transfer.md),
[spec-legion-cargo.md](../scoped-inventory-hierarchy/spec-legion-cargo.md),
[spec-cargo-fate.md](../scoped-inventory-hierarchy/spec-cargo-fate.md) (verb semantics).
House style: `spec-legion-cargo.md`.

## Objective

The six scoped-inventory verbs — load, unload, legion-to-legion transfer, deposit, withdraw,
claim-into-cargo — are built in `FusionRpg.Data` and callable only in-process/tests today: no
`WorldCommandKind` names them, no admission arm admits them, no resolver resolves them, and the
`/api/world` route list contains zero cargo/cache routes
(`gk-core/src/FusionRpg.Server/WorldEndpoints.cs:28,37,92,148,191,259`). This module promotes all six to
first-class turn orders so the wave-2 surfaces (`legion-sheet` cargo tab, `storage-cache-ui`
claim flow) and the `world-action-economy` pricing program have a command path to bind to. It
also closes the three audit-found spec drifts (§Drift repairs) with evidence, not preference.

Success looks like: a filed `deposit-cargo` order resolves in the turn it was filed — the cargo
row leaves the legion and one sector-storage row appears, or the turn report carries the exact
verb refusal (`cargo.not-present`, `cargo.sector-full`, …); a filed `claim-cache` order moves
what fits and skips what does not, keyed idempotently on its own `CommandId`; and an old command
log with none of the new kinds replays byte-identically (no `RulesetVersion` bump).

## Locked anchors

- **TurnEngine purity is held mechanically: `TurnEngine.cs` is untouched.** Cargo state lives in
  side tables (`rpg_world_entity_cargo`, `rpg_world_sector_storage`, `rpg_corpse_cache*`), never
  in `WorldState`, so no Core resolver can see it — and the replay path re-derives reports by
  calling `TurnEngine.Step` DB-free (`RpgStore.WorldTurns.cs:659`). Resolution therefore runs as a
  Data-side post-Step pass inside the commit transaction (§Design 5), the same split the
  wonder-build-flow already established: a pre-Step command rewrite
  (`ValidateWonderRelicCommandsUnlocked`, `RpgStore.WorldTurns.cs:532-536`) plus a post-Step spend
  keyed off resolution outcome (`SpendWonderRelicsUnlocked`, `:545-547`). Core gains kinds,
  payload fields, and admission arms only — never a DB read.
- **One ownership root, unchanged.** `rpg_item.player_id`/`disposition` are never read or written
  by deposit/withdraw/claim (spec-cargo-transfer §Locked anchors); load/unload keep their existing
  `player_id` checks (`RpgStore.LegionCargo.cs:284,413`). On the command path the ownership root
  is `CommanderId` + admission's `entity.not-yours` gate (§Design 3) — see Drift repair D2.
- **Move, never copy, one transaction.** Every kind resolves through the existing `*Unlocked`
  verbs (§Design 4 table), which already delete+insert atomically; the pass itself runs inside the
  commit `tx` (`RpgStore.WorldTurns.cs:510-591), so a mid-pass crash rolls back the whole turn.
- **`claim-cache` is the converged kind name.** `world-action-economy-ideal.md` (Locked
  constraints §3, Owner resolutions Q4) converges on promoting claim to a command kind via plan
  Task 4A.1 — this spec defines that kind once, and the economy program consumes it without
  renaming. The existing sector-claim keeps `Claim = "claim"`
  (`gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:19`); the cache claim is `"claim-cache"`,
  never a second `"claim"`.
- **No pricing here.** The resolver exposes one named debit seam (§Design 6) and reserves cost-key
  names (§Tunables); numbers, allowance, and the debit implementation belong to
  `world-action-economy`'s `act-price-table` + `budget-debit` modules. Filing and resolving a
  priced act today costs nothing and changes no budget.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Closed 12-kind vocabulary, admission gate, Reveal discipline | `gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:7-88` (`All`, `IsKnown`); `WorldCommandAdmission.cs:17-134`; `TurnEngine.cs:188-233` |
| Optional typed payload fields (not a JSON blob) + persist/rehydrate round trip with drift-in-one-place discipline | `WorldCommand.cs:98-146`; `RpgStore.WorldTurns.cs:155-197` (`InsertCommandUnlocked`, `CommandPayload` `:462-465`); `ReadCommandRow` `:704-728` (absent-list → empty precedent `:723-726`) |
| Submit path: admission per command, idempotent on `(commander, command)` | `RpgStore.WorldTurns.cs:84-137` (`SubmitWorldCommands`), `:139-153` (`CommandExistsUnlocked`) |
| Commit path with pre-Step rewrite + Step + diff + post-Step spend + stored report, all in one `tx` | `RpgStore.WorldTurns.cs:485-591` (`CommitWorldTurn`); diff `:543`; log insert `:549-567`; decay tick `:586` |
| Resolver drop-pattern precedent (`entity.gone`/`entity.routed`, re-validated ownership, `Drop` helper) | `ClaimResolver.cs:45-70,159-160`; `SustainResolver.cs:29-45,87-88`; `BuildResolver.cs:32-60,198-199` |
| All six verbs built with refusal vocabularies | `RpgStore.LegionCargo.cs:253-266` (load), `:395-402` (unload), `:457-468` (transfer); `RpgStore.CargoTransfer.cs:62-73` (deposit), `:136-147` (withdraw); `RpgStore.CacheFieldAccess.cs:372-387` (claim) |
| Shared capacity helpers (the D1 evidence — reused, never redefined) | `WeightCapacityUnlocked`/`SlotCapacityUnlocked` (`RpgStore.LegionCargo.cs:100-106`); `WeightUsedUnlocked`/`SlotsUsedUnlocked` (`:183-202`); consumed by deposit/withdraw (`RpgStore.CargoTransfer.cs:93-95,170-175`) and claim (`RpgStore.CacheFieldAccess.cs:26-29,326-330`) |
| Sector capacity read + reachability read | `SectorStorageSlotCountUnlocked` + `ReadSectorOwnerUnlocked` (`RpgStore.SectorStorage.cs:107-147`); `SectorItemCapacity.EffectiveCapacity` (`gk-core/src/FusionRpg.Core/World/SectorItemCapacity.cs:14-27`) |
| Claim replay safety + per-row skip + reachability re-check | `RpgStore.CacheFieldAccess.cs:296-300` (log), `:302-304` (re-check), `:314-361` (per-row gates, skip-not-refuse) |
| Loud-on-missing weight regression (the D3 evidence) | `gk-core/tests/FusionRpg.Data.Tests/CargoTransfer/CargoTransferTests.cs:321-341` (7-column shape pinned, `weight_each` read throws `no such column`) |
| Wire mapping for existing payload fields | `WorldEndpoints.cs:108-121` (command construction); `WorldDtos.cs:450-472` (`WorldCommandRequest`) |

### Wiring gap (this module closes it)

| Gap | Notes |
|---|---|
| No kind, payload, admission, or resolver for any of the six verbs | Zero production callers of any verb exist in `src/` (verified by grep this session — definitions + tests only). The ideal §4 names this as the single largest gap. |
| `CommandPayload`, `ReadCommandRow`, `WorldCommandRequest`, and the `/commands` mapping lack every cargo/cache field | `RpgStore.WorldTurns.cs:462-465,704-728`; `WorldDtos.cs:450-472`; `WorldEndpoints.cs:108-121` |
| No Data-side post-Step cargo pass in `CommitWorldTurn` | Slots exist before (`:536` rewrite) and after (`:547` spend, `:586` decay) where §Design 5 inserts exactly one new step |

## Design

### 1. New kinds (`WorldCommandKinds`, `WorldCommand.cs:7-88` family)

```csharp
public const string LoadCargo = "load-cargo";         // armoury/stock → legion
public const string UnloadCargo = "unload-cargo";     // legion → armoury/stock
public const string TransferCargo = "transfer-cargo"; // legion → legion, same empire
public const string DepositCargo = "deposit-cargo";   // legion → sector vault
public const string WithdrawCargo = "withdraw-cargo"; // sector vault → legion
public const string ClaimCache = "claim-cache";       // fallen cache → legion (converged name, Locked anchors)
```

All six join `All` (closed vocabulary — a guard pins membership the same way atom-kind counts
are pinned). Kebab-case matches the existing twelve. `ClaimCache` is distinct from
`Claim = "claim"` (sector-claim) by construction.

### 2. Payload fields (`WorldCommand`, same optional-typed discipline as `:98-146`)

| Field | Type | Used by | Notes |
|---|---|---|---|
| `Seq` | `int?` | unload / transfer / deposit / withdraw | Cargo-row selector. NOT `SlotIndex` (that names a sector slot — `WorldCommand.cs:114`; conflating the two id-spaces repeats the `ward`/`bind-warden` collision the kind comment at `:43-50` records as repaired-once). |
| `TargetEntityId` | `string?` | transfer | Destination legion. `EntityId` is the source. |
| `CacheId` | `string?` | claim | Target cache. Never trusted without the reachability re-check (verb already re-checks, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CacheFieldAccess.cs:302-304`). |
| `CargoKind` | `string?` | load | `'instance'` \| `'stack'` — the same two-kind split every overlay table uses. |
| `InstanceId` | `string?` | load | `kind='instance'` only. |
| `ContainerId` | `string?` | load | `kind='stack'` only. |
| `Qty` | `long?` | load | `kind='stack'` only. `long`, matching `LegionCargoRow.Qty` (`RpgStore.LegionCargo.cs:18`). |

What is deliberately absent: **`weightEach` is never on the wire.** Weight is resolved
server-side at resolve time and snapshotted (§Design 4, Drift repair D3). A client that could
name its own weight could mint capacity.

`CommandPayload` (`RpgStore.WorldTurns.cs:462-465`) gains the same fields in the same order;
`ReadCommandRow` (`:704-728`) maps them with the `RelicInstanceIds` absent→empty discipline;
`WorldCommandRequest` (`WorldDtos.cs:450-472`) and the `WorldEndpoints.cs:108-121` construction
gain them field-for-field. Forgetting a field here loses it in the round trip — the `stance`
precedent the `CommandPayload` doc comment (`:457-461`) already records.
**Merge order (shared record with wonder-rest):** this spec and `spec-wonder-rest.md` extend the
same DTO + mapping for different fields (cargo fields here, `RelicInstanceIds` there) — both land
additively, neither reorders existing lines, merge in either order, no dependency either way.
**Known pre-existing wire loss (not this module's):** the same DTO/mapping already drops
`WardenId` (`bind-warden` unfilable over HTTP) and the TS mirror lacks `projectId` (`develop`
unfilable from FE) — named so field-for-field discipline isn't mistaken for wire completeness.

### 3. Admission arms (`WorldCommandAdmission.cs:17-134` family)

The generic EntityId ownership check (`:32-40`, `entity.not-yours`) already covers every kind's
acting legion. Each arm adds only its own shape checks — legality-at-reveal (has the world moved
since filing) stays in the resolver, per the file's own contract (`:3-11`):

| Kind | Arm (refusal on malformed) |
|---|---|
| `load-cargo` | `entity.missing` if no `EntityId`; `cargo.kind-unknown` unless `CargoKind ∈ {instance, stack}`; `cargo.ref-missing` if instance-without-`InstanceId` or stack-without-`ContainerId`/`Qty ≤ 0` (mirrors the verb's own throws, `RpgStore.LegionCargo.cs:273-280`, as refusals, not exceptions) |
| `unload-cargo` | `entity.missing` if no `EntityId`; `cargo.seq-missing` if no `Seq` |
| `transfer-cargo` | `entity.missing` if no `EntityId`; `cargo.target-missing` if no `TargetEntityId` or target unknown/unowned (`entity.not-yours` — the destination is ownership-checked here, not only at resolve, because both legions must be the commander's at filing just as at resolution) |
| `deposit-cargo` / `withdraw-cargo` | `entity.missing` if no `EntityId`; `sector.missing` if no `SectorId` (the `Claim`/`Clear` arm precedent, `:54-58,122-132`); `cargo.seq-missing` if no `Seq` |
| `claim-cache` | `entity.missing` if no `EntityId`; `cache.missing` if no `CacheId`. `correlationId` is `CommandId` by lock (§Design 4) — `command.id-missing` (`:22-23`) already guarantees it non-empty, so `correlation.missing` is unreachable on this path (named, not re-checked). |

`Reveal` needs no edits: routed entities drop with `entity.routed` (`TurnEngine.cs:211-215`,
free for every kind); the `entity.held` march-only gate (`:219-226`) does not touch cargo —
a garrison may act (no prices exist yet, so the hold-allowance fan-out in
`world-action-economy-ideal.md` Locked constraint 2 is cited, not solved).

### 4. Verb mapping (the resolver calls `*Unlocked`, never reimplements)

One row per kind. `playerId` is derived server-side from `rpg_worlds`
(`ReadWorldPlayerUnlocked` precedent, `RpgStore.LegionCargo.cs:234-242`), never from the wire:

| Kind | Verb | Gates (verb order, refused verbatim) | Success report detail |
|---|---|---|---|
| `load-cargo` | `LoadCargoUnlocked(db, tx, worldId, entityId, playerId←derived, CargoKind, InstanceId, ContainerId, Qty, weightEach←server-resolved)` | `cargo.not-owned` → `cargo.over-weight` / `cargo.no-slots` (`RpgStore.LegionCargo.cs:282-304`) | `cargo.loaded:<newSeq>` |
| `unload-cargo` | `UnloadCargoUnlocked(…, seq, playerId←derived)` | `cargo.not-found` → `cargo.not-owned` (`:407-414`) | `cargo.unloaded:<seq>` |
| `transfer-cargo` | `TransferCargoUnlocked(…, from=EntityId, to=TargetEntityId, seq, playerId←derived)` | `cargo.not-found` → `cargo.cross-empire` → `cargo.over-weight` / `cargo.no-slots` (`:470-500`); same-legion no-op success (`:474-480`) preserved | `cargo.transferred:<newSeq>` |
| `deposit-cargo` | `DepositUnlocked(…, entityId, sectorId, seq)` — no `playerId` (D2 records the absence) | `cargo.not-found` → `cargo.not-present` → `cargo.wrong-faction` → `cargo.sector-full` (`RpgStore.CargoTransfer.cs:79-96`) | `cargo.deposited:<newSeq>` |
| `withdraw-cargo` | `WithdrawUnlocked(…, sectorId, entityId, seq, weightEach←server-resolved)` | `cargo.not-found` → `cargo.not-present` → `cargo.wrong-faction` → `cargo.over-weight` / `cargo.no-slots` (`:149-175`) | `cargo.withdrawn:<newSeq>` |
| `claim-cache` | `ClaimCorpseCacheIntoCargoUnlocked(…, entityId, playerId←parity, cacheId, correlationId:=CommandId, nowUtc, weightEachFor←server resolver)` | `cache.unreachable` → per-row fit/skip (`RpgStore.CacheFieldAccess.cs:302-337`); result's `ClaimedSeqs`/`SkippedSeqs` reported | `cache.claimed:<claimed-count>+<skipped-count>` |

`weightEach` / `weightEachFor` are resolved server-side from the item record at resolve time —
the caller-supplied-weight discipline (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CacheFieldAccess.cs:267-273`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CargoTransfer.cs:121-131`)
with the caller now being the resolver, not the client. The exact lookup has no named function
in code today (the shipped comment records "no per-item weight column exists anywhere,"
`RpgStore.LegionCargo.cs:30-35`); naming that lookup is implementation's first task, not assumed
solved here. Lookup failure refuses loudly (`cargo.weight-unknown`), never zero-fills (D3).

Stale-legion drops follow the resolver precedent: entity gone → `entity.gone`; entity routed →
`entity.routed` (Claim/Sustain/Build `Drop` pattern). All outcomes append
`TurnReportKinds.CommandDropped` or `TurnReportKinds.Event` entries — the refusal vocabulary is
the verbs' own strings verbatim, so the wave-2 fold authors copy against a closed list.

### 5. The pass — one new step in `CommitWorldTurn`, `TurnEngine.cs` untouched

```
CommitWorldTurn tx (RpgStore.WorldTurns.cs:510-591), inserted between SpendWonderRelics (:547)
and the turn-log insert (:549-567):

  CargoResolveUnlocked(db, tx, worldId, commands, result):
    for each command in stable (commander, command) order (Reveal's own order, TurnEngine.cs:194-197)
    where kind ∈ the six §Design 1 kinds:
      route per §Design 4 table; on ok append Event entry (§Design 4 detail column);
      on refusal append CommandDropped entry with the verb's reason verbatim;
      run the §Design 6 debit seam (no-op today) inside the same per-command scope.
    claim commands resolve BEFORE the decay tick (:586): claim-then-decay is locked —
    a claimed row is gone before decay sees it; skipped (left-behind) rows remain and decay
    normally. (Answers world-action-economy Locked constraint 4's precedence half; the
    idempotency-mapping half is answered by correlationId := CommandId, §Design 4.)
```

Placement rationale (read → verify → propose): the pass must run **after**
`DiffWorldGraphUnlocked` (`:543`) because every verb reads live post-turn positions/owners
(`ReadTransferEntityUnlocked`, `ReadLegionPositionUnlocked`), and **before** the log insert
(`:549`) so its entries are stored in the hot-tail report. What it must NOT do: run inside
`TurnEngine.Step` (purity — Locked anchors), or after the decay tick (would price already-decayed
rows). Replay fidelity gap, stated honestly: post-trim re-derivation (`:644-660`) replays `Step`
only, so cargo entries are absent from re-derived reports — the stored hot-tail report plus the
never-trimmed command log remain the audit trail, and `StateHash` is unaffected (cargo tables are
not hashed). `claim-endpoints` list/detail reads must therefore serve stored-report detail, never
assume replay reproduces it.

`RulesetVersion` stays 10: no existing log can contain the new kinds (submit previously refused
`kind.unknown`, `WorldCommandAdmission.cs:19-20`), Core resolvers filter by kind so `Step` is
byte-identical for old logs — the `Assaults`-phase precedent (`TurnEngine.cs:101-109`: a new
kind is provably a no-op for predating worlds). Proof obligation: the existing golden suite green
plus one new test asserting an old-log replay hash is unchanged with the pass present.

### 6. Debit-site exposure for `world-action-economy` (no pricing here)

Inside the per-command scope (§Design 5), after gates pass and before the move, the pass calls:

```
DebitActCostUnlocked(db, tx, worldId, entityId, kind) → (bool Ok, string Reason)
```

Ships as accept-always (no cost table exists yet). The economy program's `budget-debit` module
owns its body; this spec locks only the seam contract:

- **Order: debit-after-refill.** The pass runs post-Step post-Diff, so `MovementRemaining` in the
  DB is the refilled next-turn budget (`TurnEngine.cs:413-423`) — an act spends next turn's march,
  never this turn's already-spent leftover. This is Locked-constraint-1's `debit-after-refill`
  option, selected here; `march-then-act, no reservation` (Owner resolutions Q6) is preserved
  because marching never sees the debit.
- **Priced verbs (Q3 + price table wins).** REVISED 2026-09-15 (reconciliation with
  `spec-act-price-table.md` + `spec-claim-pricing.md`, which own keys and implementation):
  claim/deposit/withdraw/load/unload are all priced per `act-price-table` keys
  (`claimCostMilli`, `depositCostMilli`, `withdrawCostMilli`, `loadCostMilli`,
  `unloadCostMilli`); transfer unpriced entirely. This spec's earlier claim-only reading and
  `ClaimCacheCostMilli`-shaped key names are superseded — the price table is the key owner.
- Short-budget refusal shape is the economy's content call; the reason vocabulary prefix
  (`entity.spent`-shaped, cf. `entity.held`/`entity.routed`) is recommended so the wave-2 fold
  has one family to author against.

### Drift repairs (audit-found, decided with evidence)

**D1 — Shared capacity helpers vs raw-SQL: HELPERS (locked).** Both transfer directions and the
claim already consume `WeightCapacityUnlocked`/`SlotCapacityUnlocked`/`WeightUsedUnlocked`/
`SlotsUsedUnlocked`/`SectorStorageSlotCountUnlocked`/`SectorItemCapacity.EffectiveCapacity`
(Built table) with zero raw-SQL capacity re-derivation in either file. This spec locks
"reuse, never redefine": the pass and any future verb call the helpers; a `SUM(weight_each)` /
cargo `COUNT(*)` outside `RpgStore.LegionCargo.cs` / `RpgStore.SectorStorage.cs` fails a new
guard test. No code change required — the drift was spec-side (spec-cargo-transfer §Design 1-2
spells raw `SELECT COUNT(*)`/`SUM` where the shipped code calls helpers).

**D2 — `playerId` restore-or-record: RECORD (locked).** Restore is refused on evidence:
submit-time ownership is already gated by admission (`entity.not-yours`,
`WorldCommandAdmission.cs:32-40`) with `CommanderId` as the root, and the shipped
deposit/withdraw carry no `playerId` (`RpgStore.CargoTransfer.cs:62,136`) with complete gates
(presence + faction + capacity). So: load/unload/transfer keep their `playerId` parameters
(derived server-side, §Design 4 — they predate commands and stay immediately callable);
deposit/withdraw keep their absence (recorded here as intentional, not as a hole); claim's
accepted-but-ignored `playerId` (`_ = playerId`, `RpgStore.CacheFieldAccess.cs:287`) is recorded
as delve-parity shape whose gate is reachability alone — signatures stay byte-identical this
module (see Non-touch list), the command path never reads ownership off it.

**D3 — Server-side `weightEach` with loud-on-missing regression: LOCKED as §Design 4.**
Sector storage has no `weight_each` by design (`RpgStore.SectorStorage.cs:12-15`); the 7-column
shape plus the throwing probe are pinned (`CargoTransferTests.cs:321-341`); withdraw/claim take
caller-supplied weight and snapshot it (`RpgStore.CargoTransfer.cs:121-131`,
`RpgStore.CacheFieldAccess.cs:258-273`). The command path extends the discipline: no weight on
the wire, server-side resolution, loud `cargo.weight-unknown` refusal on lookup failure. The
regression test is extended, not edited: one new case asserting the resolver never issues a
`weight_each` read against sector/cache tables.

## Tunables

Named, never valued — no literals in this spec, no tuning file touched:

| Tunable | Home | Owner |
|---|---|---|
| `CargoWeightPerUnit` (`long`), `CargoSlotsPerUnit` (`int`) | `gk-core/data/tuning/scoped-inventory.v1.json` (exist — `scoped-inventory.v1.json:10-11`) | scoped-inventory (reused via `ScopedInventoryPolicy`, `:25-47`) |
| `ItemStorageCapacityBonus` per structure row | Seed-authored structure rows (spec-storage-content) | empire-inventory-surfaces module 3 |
| `claimCostMilli`, `depositCostMilli`, `withdrawCostMilli`, `loadCostMilli`, `unloadCostMilli` (per-mille; transfer unpriced) | `data/tuning/world.v{n+1}.json` `movement` — RESERVED here, CREATED by `world-action-economy` `act-price-table` (key owner; §Design 6 revision) | world-action-economy |
| Refill frame (`PointsPerTurn` march / scout-half / hold-zero, `LaneCost.cs:32,35,47-57`) | NOT retuned — the fixed frame costs measure against (economy-ideal §Tunables T7) | world-action-economy (read-only) |
| Player refusal/confirmation sentences (`cargo.*`, `cache.unreachable`, per-row skip, spent-shape) | Authored copy catalog (GG-62); home file named at claim-endpoints/legion-sheet spec time | empire-inventory-surfaces wave 2 |

## Numeric types

Inherited from spec-legion-cargo §Numeric types, extended to the wire: `Qty`, `weightEach`,
added weights, used/capacity totals are `long`, `checked` (widen-before-multiply —
`ScopedInventoryPolicy.cs:39-47`; `checked` sums — `RpgStore.LegionCargo.cs:183-189`;
`checked` row weight — `RpgStore.CargoTransfer.cs:170-171`, `RpgStore.CacheFieldAccess.cs:322-324`).
`Seq`, slot counts, member counts are `int` — structural bounds, commented as such. New payload
`Qty` is `long?`; new `Seq` is `int?`. Integer overflow throws, never wraps; narrowing is checked
or reported (DESIGN-GATE §2.13).

## Commands

```powershell
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~Cargo"
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~WorldCommandAdmission"
python gk-core/scripts/guard-dal.py        # every new SQL string lives in FusionRpg.Data
```

## Structure

```
gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs            MODIFIED — six kind constants (§Design 1) + seven
                                                          payload fields (§Design 2), All extended (closed vocab)
gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs   MODIFIED — five admission arms (§Design 3)
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs         MODIFIED — CommandPayload + InsertCommandUnlocked +
                                                          ReadCommandRow (§Design 2); CargoResolveUnlocked hook
                                                          site in CommitWorldTurn (§Design 5)
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CargoCommands.cs      NEW — CargoResolveUnlocked + DebitActCostUnlocked stub
                                                          (§Design 5-6); SQL lives here, only here (guard-dal)
gk-core/src/FusionRpg.Contracts/WorldDtos.cs                     MODIFIED — WorldCommandRequest fields (§Design 2)
gk-core/src/FusionRpg.Server/WorldEndpoints.cs                   MODIFIED — /commands construction mapping (§Design 2)
gk-core/tests/FusionRpg.Data.Tests/CargoCommands/                NEW — per-kind resolve, refusal-verbatim, idempotent
                                                          reclaim, old-log replay-hash-unchanged, weight-probe
                                                          extension, helper-reuse guard
UNTOUCHED: TurnEngine.cs (purity); MarchResolver/MovementPhase; RpgStore.LegionCargo.cs,
           RpgStore.SectorStorage.cs, RpgStore.CargoTransfer.cs, RpgStore.CacheFieldAccess.cs,
           RpgStore.CargoFate.cs verb bodies (called, never modified); WorldState schema/StateHasher
           (cargo unhashed); Intel/belief projection; decay tick; DiffEntities/DiffSectors; AI policies;
           every tuning file; web/.
```

## Code style

```csharp
// Data-side post-Step, same-tx, wonder-spend-shaped: positions are post-turn (post-diff),
// entries land before the log insert, refusals reuse the verb's own strings verbatim.
foreach (var command in CargoKinds(commands))   // stable (commander, command) order, Day-1 discipline
{
    var result = ResolveCargoUnlocked(db, tx, worldId, command, result.World /* post-Step */, nowUtc);
    if (result.Ok) report.Add(phase, TurnReportKinds.Event, command.CommandId, result.Detail, result.SectorId);
    else report.Add(phase, TurnReportKinds.CommandDropped, command.CommandId, result.Reason);
}
```

## Testing strategy

- **Per-kind resolve moves, never copies:** each of the six kinds, filed via `SubmitWorldCommands`
  and resolved by `CommitWorldTurn`, leaves source-minus-one / destination-plus-one — asserted by
  row counts, mirroring each verb's own atomicity tests.
- **Refusals verbatim, nothing written:** `cargo.not-present` (marched-away legion), `cargo.wrong-faction`,
  `cargo.sector-full`, `cargo.over-weight`/`cargo.no-slots`, `cache.unreachable` (stale/forged cache id),
  `cargo.cross-empire` — each asserts the exact string plus zero writes on either table.
- **Claim skip-not-refuse + idempotency:** a mixed-fit claim reports `cache.claimed:<c>+<s>` with skipped
  rows still in the cache; re-committing the same `CommandId` returns the byte-identical recorded result
  (claim-log replay, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CacheFieldAccess.cs:296-300`, keyed on `CommandId` as correlation).
- **Claim-before-decay:** a claimed row is absent when the decay tick runs the same commit; a skipped row
  remains subject to it.
- **Old-log replay hash unchanged:** a golden asserting `StateHash` for a log with zero new kinds is
  identical with the pass present (the no-bump proof).
- **Weight probe extension + helper-reuse guard:** D3's new case (resolver issues no `weight_each` read
  against sector/cache tables) and D1's guard (no cargo `SUM`/`COUNT(*)` outside the two owner files).
- **Admission matrix:** each §Design 3 arm's malformed shape refuses with its named reason at submit.

## Boundaries

- **Always:** gates before writes; verb reasons verbatim into the report; one transaction (the commit's);
  resolve after diff, before log insert, claims before decay; `correlationId := CommandId`.
- **Ask first:** a co-location/adjacency gate for `transfer-cargo` (the verb has none —
  `RpgStore.LegionCargo.cs:470-493` checks owner + capacity only; adding one is a product call, not a fix);
  any price, allowance, or budget read beyond the §Design 6 stub (economy's program); widening
  `WorldCommand` with further fields.
- **Never:** a weight field on the wire; a second cargo table or cache table; Core-side DB access;
  resolving cargo inside `TurnEngine.Step`; touching `rpg_item.player_id`/`disposition` from
  deposit/withdraw/claim; inventing refusal strings when the verb already names one.

## Success criteria

1. All six kinds file, resolve, and report per §Design 4–5, each refusal byte-matching the verb's own string.
2. D1–D3 locked as decided, each with its guard/regression test green.
3. `guard-dal.py` green; no SQL outside `FusionRpg.Data`.
4. Old-log replay hash unchanged (`RulesetVersion` stays 10).
5. Zero edits to every path in the Non-touch list (verified by diff).

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| Six kinds + payload fields + admission reasons (§Design 1–3) | `claim-endpoints` (wave 1) — REST binds load/unload/deposit/withdraw/list/claim onto these; `correlationId := CommandId` is the idempotency contract it relays to clients |
| `ClaimCorpseCacheIntoCargoUnlocked` result shape (`ClaimedSeqs`/`SkippedSeqs`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CacheFieldAccess.cs:31-37`) + `ListClaimableCaches` (`:99-106`) | `claim-endpoints` — contents/capacities read-back DTOs and the claim POST response; per-row skip copy is authored against these two lists |
| `DebitActCostUnlocked` seam + debit-after-refill order + reserved `*CostMilli` key names (§Design 6) | `world-action-economy` (`budget-debit`, `act-price-table`) — implements the stub, creates the keys, owns the spent-shape refusal; hold-allowance fan-out stays its problem |
| Report detail strings (§Design 4 detail column) + verb refusal vocabulary | `legion-sheet` / `storage-cache-ui` (wave 2) — the closed lists the fold and player copy author against |

## Design-gate checklist

```
[x] Subsystems: world-map turn engine + command vocabulary (Core), cargo/cache Data verbs,
    world tuning names. No Status/ActorHub/Combat/Injector subsystem touched.
[x] Read this session: empire-inventory-surfaces-map.md (module 1 row);
    empire-inventory-surfaces-ideal.md §§4-5, §7-8 + Owner resolutions (legion sheet direction,
    AP-cost lock); spec-cargo-transfer.md + spec-legion-cargo.md + spec-cargo-fate.md (full);
    world-action-economy-ideal.md (Locked constraints, Owner resolutions Q1-Q6);
    DESIGN-GATE.md §1 topic rows + §2 invariants + §5 checklist.
[x] Code cited by file:line, opened this session: WorldCommand.cs (:7-88 kinds, :98-146 payload);
    WorldCommandAdmission.cs (:17-134 arms); TurnEngine.cs (:94-120 phases/order, :188-233 Reveal,
    :405-423 refill, :101-109 new-kind-no-bump precedent); MarchResolver.cs/MovementPhase.cs
    (resolver pattern); RpgStore.CargoTransfer.cs (:62-196 verbs); RpgStore.LegionCargo.cs
    (:100-106 capacities, :183-202 usage, :253-521 verbs); RpgStore.CargoFate.cs (move discipline);
    RpgStore.CacheFieldAccess.cs (:48-106 list, :280-387 claim); RpgStore.SectorStorage.cs
    (:107-147 reads); SectorItemCapacity.cs (:14-27); ScopedInventoryPolicy.cs (:39-47 checked);
    RpgStore.WorldTurns.cs (:84-197 submit, :462-465 payload, :485-591 commit, :704-728 rehydrate);
    WorldEndpoints.cs (:28-139 routes+mapping); WorldDtos.cs (:450-472 request DTO);
    LaneCost.cs (:32-57 budget frame); world.v5.json (:83-85 movement); scoped-inventory.v1.json
    (:10-11); CargoTransferTests.cs (:321-341 loud regression).
[x] Checked decisions.md for a covering lock: scoped-inventory SSOT (one ownership root, move-never-copy)
    reused in Locked anchors; RulesetVersion-history precedent reused for the no-bump call.
[x] Verified claims against CODE, not comments (all citations opened in-session in the worktree;
    zero-caller wiring gap proven by grep over src/; no-weight-column proven by the throwing test).
[x] Read the surrounding section of every rule quoted (admission contract :3-11; refill comment
    :405-407; payload-drift comment :457-461; rehydrate fallback :723-726; purity doc :10-17).
[x] Tested (not assumed) constraints: no suite run — spec phase, no code; the no-bump claim is
    staked on a named new test (old-log replay hash), not asserted as measured.
[x] Nothing contradicts a §2 invariant: SQL only in FusionRpg.Data (guard-dal); no magnitude cap
    (capacities are structural, fixture-bound, refuse-with-reason); no f(Θ) (flat per-act costs
    reserved, never level-scaled); no second ownership root; no second ActorHub/composer;
    SOLID: one resolver seam, one payload record, helpers reused never forked.
[x] No assertion pins a derived-population count, item total, generated name/description, or
    per-cycle outcome. (Counts named: 12 existing kinds + 6 new — closed code-owned vocabularies
    with stated reasons, not populations; 7-column shape — a schema contract with a stated reason.)
[x] No event-refreshed cache introduced. (Claim-log replay cited as built behavior; replay-fidelity
    gap for post-trim re-derivation stated in §Design 5, not hidden.)
[x] No acceptance criterion fixes an ordering that can vary in real play. (Commit-internal ordering
    — diff→cargo→log→decay — is a fixed pipeline sequence, asserted; stable (commander, command)
    order reused from Reveal, never reinvented.)
[x] No actor combat/derived magnitude produced or consumed — no Hub-adjacent subsystem touched.
[x] No SOLID-violating parallel path: no second admit path, no parallel price engine, no forked
    capacity math; the economy's debit is a stub in the one seam, not a second pool.
[ ] The exact server-side weightEach lookup has no named function in code today — named as
    implementation's first task (§Design 4), not assumed solved. (Honest gap, cf. spec-legion-cargo
    §Design-gate checklist's own open box.)
```
