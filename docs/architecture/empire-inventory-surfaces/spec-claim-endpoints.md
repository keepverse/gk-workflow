# Spec: `claim-endpoints`

**Status: written against shipped code 2026-09-15** — every `file:line` below was opened this
session in worktree `empire-development-20260915-b7e2`. Module id `claim-endpoints`, row 2 of the
[empire-inventory-surfaces map](../empire-inventory-surfaces-map.md) (wave 1, depends on
`cargo-commands`). Consumes [spec-cargo-commands.md](spec-cargo-commands.md) **in full, exactly as
decided** — six kinds incl. `claim-cache`, the Data-side post-Step pass in `CommitWorldTurn`,
the no-op `DebitActCostUnlocked` seam with debit-after-refill order, and playerId
recorded-not-restored — re-decides none of it. Ideals:
[empire-inventory-surfaces-ideal.md](../empire-inventory-surfaces-ideal.md) §4 (cache rows: listing
+ claim built, no player path reaches them), §6 Diablo precedent (one legion's / one sector's
rows per open, never the empire's), §9 (backend reads as built; pricing/copy owned elsewhere),
Owner resolutions (hidden-until-found pins, header+toast capture messaging). Reachability/replay
shapes: [spec-cache-field-access.md](../deployment-hierarchy/spec-cache-field-access.md) §1a/§2a.
House style: `spec-legion-cargo.md`.

## Objective

The wave-2 surfaces (`legion-sheet` cargo tab, `storage-cache-ui` claim flow) need HTTP they can
bind to, and today zero cargo/cache routes exist on `/api/world`
(`gk-core/src/FusionRpg.Server/WorldEndpoints.cs:28,37,92,148,191,259` — the complete route list). This
module adds exactly four reads-or-filers — list claimable caches per legion, file a claim,
read back one legion's cargo, read back one sector's storage — each scoped to one legion or one
sector, each presence-gated server-side, each carrying the verbs' own refusal vocabulary
verbatim so the wave-2 fold authors against a closed list.

Success looks like: a legion standing on a fallen cache sees it in `GET claimable-caches` and a
legion one sector away does not, with no client-side fog logic anywhere; a filed claim resolves
at the next commit through the `cargo-commands` pass (never inline), keyed idempotently on its
own `CommandId`, and the turn report carries `cache.claimed:<c>+<s>` or the exact verb refusal;
a cargo/storage read returns one legion's / one sector's rows plus used-vs-capacity, never the
empire's inventory.

## Locked anchors

- **`cargo-commands` is consumed, not re-decided.** Six kinds (`load-cargo`, `unload-cargo`,
  `transfer-cargo`, `deposit-cargo`, `withdraw-cargo`, `claim-cache`), `correlationId :=
  CommandId`, claim-before-decay, debit-after-refill, priced-verbs-only
  (claim+deposit/withdraw), playerId recorded-not-restored — all in
  `spec-cargo-commands.md` §§Design/Locked anchors. Where this spec touches the same seam it
  quotes that spec's decision; where it differs it is wrong.
- **Turn-engine purity holds: this module adds no third write kind.**
  `WorldEndpoints.cs:13-17` locks the HTTP surface to two writes — filing orders and ending a
  turn. The claim POST below is a filer, not a mutator: it constructs a `claim-cache`
  `WorldCommand` and delegates to `SubmitWorldCommands`, exactly the way `POST
  /{worldId}/commands` already does (`WorldEndpoints.cs:92-137`). No route calls
  `ClaimCorpseCacheIntoCargo` / `Deposit` / `Withdraw` directly; every mutation still happens
  inside the commit transaction via the §Design 5 pass of `spec-cargo-commands.md`.
- **Presence-gating is server-side, never client-filtered.** `ListClaimableCachesUnlocked`
  reads the legion's live position fresh and returns only non-void, non-empty caches pinned
  exactly where it stands (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CacheFieldAccess.cs:48-93`);
  unknown legions and both-set/neither-set corrupt rows see nothing (`:51-53,69-72`) rather
  than a guess. The GET below projects that result 1:1. An FE that hides, groups, or
  second-guesses the list client-side re-implements fog and is a defect.
- **One legion / one sector per read, never empire-wide.** The Diablo-memory precedent
  (ideal §6: loading everyone's stash caused D4's memory overhead) is binding here: the fold
  requests one legion's or one sector's rows per surface open. No bulk/list-all route ships in
  this module.
- **Weight is never on the wire.** `weightEach`/`weightEachFor` resolve server-side at resolve
  time (spec-cargo-commands §Design 4; `RpgStore.CacheFieldAccess.cs:267-273`,
  `RpgStore.CargoTransfer.cs:121-131` caller-supplied discipline with the resolver as caller).
  Request DTOs carry no weight field; a client that could name its own weight could mint
  capacity.
- **No pricing here; no copy here.** The debit seam (§Design 6 of `spec-cargo-commands.md`)
  and the authored player sentences (ideal §8, GG-62) both belong to other programs. This spec
  reserves the key names and relays the reason strings verbatim, nothing more.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Complete `/api/world` route list: exactly six operations, zero cargo/cache routes | `WorldEndpoints.cs:28` (`GET /{playerId}`), `:37` (`GET /{worldId}/state`), `:92` (`POST /{worldId}/commands`), `:148` (`POST /{worldId}/commit`), `:191` (`GET /{worldId}/turn/{turn}`), `:259` (`GET /catalog`) |
| `/commands` construction mapping (the pattern every new filer follows) | `WorldEndpoints.cs:108-121`; `WorldDtos.cs:450-472` (`WorldCommandRequest`) |
| Viewer discipline: unknown faction refused, never omniscience fallback; commander defaults to player faction | `WorldEndpoints.cs:42-47` (`faction.unknown`), `:99-103` (commander default), `:153-156` (commit default) |
| Batch discipline: bounded input (`MaxCommandsPerSubmit = 200`), per-command partial acceptance | `WorldEndpoints.cs:22,105-106,126-134` |
| Claimable-cache listing: live-position read, non-void + non-empty only, corrupt rows see nothing | `RpgStore.CacheFieldAccess.cs:48-93` (`ListClaimableCachesUnlocked`), public read-only entry `:99-106` |
| Claim-time reachability re-check (caller-supplied id never trusted) | `RpgStore.CacheFieldAccess.cs:163-199` (`IsCargoClaimReachableUnlocked`) |
| Claim into cargo: per-row fit/skip in seq order, `ClaimedSeqs`/`SkippedSeqs` result, replay-safe log | `RpgStore.CacheFieldAccess.cs:31-37` (result record), `:280-366` (verb), replay read `:223-242` + insert `:244-256`, log key the full 6-tuple `(cache_id, delve_id, party_index, world_id, entity_id, correlation_id)` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CacheFieldAccess.cs:152`; delve columns carry sentinels on the world path) |
| Cargo reads: row list, live capacities, used totals, next-seq | `RpgStore.LegionCargo.cs:151-176` (`ListCargo`/`ListCargoUnlocked`), `:101-106` (capacities), `:183-202` (used), `:207-218` (next seq) |
| Sector reads: row list, slot count, owner read, reachability compare | `RpgStore.SectorStorage.cs:98-105` (`ListSectorStorage`), `:107-133` (slot count), `:135-169` (owner + reachability) |
| Sector capacity computed fresh from built vaults | `gk-core/src/FusionRpg.Core/World/SectorItemCapacity.cs:14-27` |
| Payload persist/rehydrate with absent-list → empty precedent | `RpgStore.WorldTurns.cs:462-465` (`CommandPayload`), `:704-728` (`ReadCommandRow`, `:723-726`) |
| Submit idempotent on `(commander, command)` | `RpgStore.WorldTurns.cs:84-137` (`SubmitWorldCommands`), `:139-153` (`CommandExistsUnlocked`) |
| Stored hot-tail report + never-trimmed command log (the replay-fidelity gap this module reads around) | `RpgStore.WorldTurns.cs:549-567` (log insert), `:589` (trim); spec-cargo-commands §Design 5 (post-trim re-derivation replays `Step` only — cargo entries absent) |
| Turn-report fog precedent: static facts (`claim.*`) shown on remembered sight | `WorldEndpoints.cs:344-366` (`VisibleTo`, `StaticFactDetailPrefixes`) |

### Wiring gap (this module closes it)

| Gap | Notes |
|---|---|
| No route serves list-claimable, claim-filing, cargo read-back, or storage read-back | Zero production callers of the Data verbs exist in `src/` (spec-cargo-commands §What already exists, verified by grep that session). Ideal §4 names the missing REST path as the single largest gap. |
| `WorldCommandRequest` + `/commands` mapping lack the cargo/cache fields | `WorldDtos.cs:450-472`; `WorldEndpoints.cs:108-121` — extended by `cargo-commands` §Design 2, consumed here field-for-field. |
| No FE mirror of any cargo/cache DTO | `contractGuard.ts:115` names `WorldCommandRequest` as a guarded shape today; `types.ts`/`adapt.ts` carry no cargo/cache view (verified by grep this session — the only `WorldCommand*` hit under `web/.../contract` is that guard comment). |
| No messaging contract for hidden-until-found pins or header+toast capture notice | Ideal Owner resolutions lock the direction; no DTO carries the states a pin/header/toast binds to. §Design 5 names the fields. |

## Design

### 1. Routes — four, all under the existing `/api/world` group

All routes live in `WorldEndpoints.cs`'s `MapWorld` group (same `g`, same viewer/commander
discipline, same `MaxCommandsPerSubmit` bound where batching applies). No new group, no new
auth shape — the `faction.unknown` / `commander.unknown` refusals are reused verbatim.

| Method + path | Purpose | Success | Refusals (verbatim strings) |
|---|---|---|---|
| `GET /{worldId}/legions/{entityId}/claimable-caches?asFaction=` | Presence-gated listing for the wave-2 cache-claim flow | `200` + `ClaimableCacheListDto` | `world.unknown`; `faction.unknown` (unknown `asFaction`, `:42-47` precedent); `entity.not-yours` (legion not this viewer's — admission's ownership root, spec-cargo-commands §Design 3); unknown legion → `entity.unknown` (caller error, distinct from "known legion, nothing reachable" which is `200` empty) |
| `POST /{worldId}/legions/{entityId}/claims` | File a `claim-cache` order for the turn (a filer — §Locked anchors) | `200` + `WorldCommandResultDto` (`Ok`/`Replayed`, `WorldDtos.cs:484-490`) | Submit-time admission reasons verbatim (`entity.missing`, `cache.missing`, `command.id-missing`, `kind.unknown` — spec-cargo-commands §Design 3); never a resolve-time string |
| `GET /{worldId}/legions/{entityId}/cargo?asFaction=` | One legion's contents + capacities for the `legion-sheet` cargo tab | `200` + `LegionCargoDto` | `world.unknown`; `faction.unknown`; `entity.not-yours`; `entity.unknown` |
| `GET /{worldId}/sectors/{sectorId}/storage?asFaction=` | One sector's vault contents + room for the storage panel block | `200` + `SectorStorageDto` | `world.unknown`; `faction.unknown`; `sector.unknown` |

Why a `POST .../claims` filer instead of telling the FE to use `POST /{worldId}/commands`
directly: the wave-2 flow files exactly one kind with exactly two ids (`EntityId`, `CacheId`)
and one idempotency key. A dedicated filer binds that shape (missing-`CacheId` becomes
`cache.missing` at submit, not a malformed generic command), delegates to the same
`SubmitWorldCommands` store call (`WorldEndpoints.cs:126`), and returns the same
`WorldCommandResultDto` — one construction site, the `/commands` mapping discipline
(`:108-121`) reused, never forked. The generic route keeps working unchanged.

What is deliberately absent: **no bulk route** (`GET .../caches` empire-wide, `GET
.../cargos`), **no direct-mutation POST** (a route that calls the claim/deposit verb inline
would bypass admission, the debit seam, claim-before-decay, and the turn report — the exact
second write kind `WorldEndpoints.cs:13-17` forbids), and **no `weightEach` on any request**
(§Locked anchors).

### 2. `GET claimable-caches` — hidden-until-found, enforced here

```
handler(worldId, entityId, asFaction):
  world = LoadWorldState; viewer = asFaction-or-player-faction (:37-47 discipline)
  refuse faction.unknown on unknown viewer
  refuse entity.not-yours unless the legion's OwnerFactionId == viewer
      (read via ReadEntityOwnerUnlocked, RpgStore.LegionCargo.cs:220-232)
  refuse entity.unknown for an unknown legion
  rows = ListClaimableCaches(worldId, entityId)   // RpgStore.CacheFieldAccess.cs:99-106 — no other query
  return ClaimableCacheListDto { EntityId, AsOfTurn, Caches: rows → ClaimableCacheDto }
```

Semantics, each inherited from the verb and stated so the FE never re-derives it:

- The response **is** the fog rule. A cache appears iff the legion stands where it lies
  (`world_sector`: `AtSectorId == place_ref`; `world_lane`: `OnLaneId == place_ref`,
  `RpgStore.CacheFieldAccess.cs:12-20`), it is `in_void = 0`, and it still holds rows
  (`EXISTS`, `:76-82`). Hidden-until-found (Owner resolution) falls out with no extra flag:
  unreachable caches are absent, not masked — there is no `visible: false` member for a client
  to misread, and no client-side position compare anywhere in the contract.
- Empty is `200` with zero entries, never `404`: "no cache here" is a normal reading (an
  emptied cache is excluded by the same `EXISTS` clause, never an error).
- `AsOfTurn` is the world's `CurrentTurn` at read time — a staleness marker for the pin
  layer, not a cache. Movement next turn can strand a pin; the pin re-reads per selection,
  never subscribes (no event-refreshed cache is introduced by this module — checklist).

### 3. `POST claim` — replay ↔ `CommandId` mapping (decided with evidence)

**Decision: `correlationId := CommandId`, end to end, no second key.** This is not a new
decision — it is `spec-cargo-commands.md` §Design 4's lock, relayed to the wire:

1. The filer takes `{ CacheId, CommandId }`, constructs a `WorldCommand` with
   `Kind = "claim-cache"`, `EntityId` from the path, `CacheId` from the body, and the
   caller-supplied `CommandId`, and calls `SubmitWorldCommands`. Submit is idempotent on
   `(commander, command)` (`RpgStore.WorldTurns.cs:84-153`): a retried POST with the same
   `CommandId` returns `Replayed: true` with zero new rows — the double-submit safety the
   claim flow needs for its pick-up button.
2. Admission checks `entity.missing` / `cache.missing` only (spec-cargo-commands §Design 3);
   `correlation.missing` is unreachable on this path because `command.id-missing`
   (`WorldCommandAdmission.cs:22-23` via that spec's citation) already guarantees non-empty.
3. At commit, the post-Step pass calls
   `ClaimCorpseCacheIntoCargoUnlocked(…, correlationId := command.CommandId, …)`. The
   verb's replay read is keyed `(cache_id, world_id, entity_id, correlation_id)` with delve
   sentinels (`RpgStore.CacheFieldAccess.cs:223-242`); a re-commit of the same command
   returns the byte-identical recorded result and performs no `DELETE`/no `INSERT`
   (`:296-300,363-365`).
4. The outcome reaches the player exclusively through the turn report
   (`cache.claimed:<claimed>+<skipped>` detail, per-row skip lists in the stored entry) plus
   the §4 read-backs — never through the POST response, which answers only "filed / replayed /
   refused-at-submit". A client that treats `Ok: true` from the filer as "claimed" confuses
   filing with resolving (the GG-15 violation the ideal §7 already rejects for capacity
   prediction).

Why not a distinctive `claim-<uuid>` correlation separate from `CommandId`: the claim log's
key already contains `(cache_id, world_id, entity_id)` — the only remaining disambiguator a
retry needs is "which filing", and `CommandId` already is that, guaranteed unique per
commander per turn (`WorldCommand.cs:103-104`). A second key would need its own uniqueness
proof and its own absent→empty discipline (`RpgStore.WorldTurns.cs:723-726` precedent) for
zero gain. The `production weightEachFor resolver` the brief names is likewise not decided
here — spec-cargo-commands §Design 4 records that no named lookup function exists in code
today (`RpgStore.LegionCargo.cs:30-35`) and makes naming it implementation's first task; this
spec's POST passes no weight and resolves none, so it cannot fork that decision.

### 4. Read-back DTOs — one scope each, capacities computed fresh

```csharp
// Contracts (gk-core/src/FusionRpg.Contracts/WorldDtos.cs, additive — mirror discipline of WorldCommandRequest)
public sealed record CargoRowDto {
    public int Seq { get; init; }                    // LegionCargoRow.Seq (RpgStore.LegionCargo.cs:11-19)
    public string Kind { get; init; } = "";          // 'instance' | 'stack' — the closed two-kind split
    public string? InstanceId { get; init; }
    public string? ContainerId { get; init; }
    public long? Qty { get; init; }                  // long, LegionCargoRow.Qty
    public long WeightEach { get; init; }            // snapshot, never re-derived
    public long RowWeight { get; init; }             // stack: checked(qty * weightEach), else weightEach (:204-205)
}
public sealed record LegionCargoDto {
    public string WorldId { get; init; } = "";
    public string EntityId { get; init; } = "";
    public int AsOfTurn { get; init; }
    public IReadOnlyList<CargoRowDto> Rows { get; init; } = Array.Empty<CargoRowDto>();  // seq order (:161-176)
    public long WeightUsed { get; init; }            // checked C# sum (:183-189)
    public long WeightCapacity { get; init; }        // memberCount × tuning, live (:101-102)
    public int SlotsUsed { get; init; }              // COUNT(*), one row one slot (:192-202)
    public int SlotCapacity { get; init; }           // (:104-106)
}
public sealed record SectorStorageRowDto { /* same row shape minus WeightEach/RowWeight — storage has no weight_each by design (RpgStore.SectorStorage.cs:12-15 via spec-cargo-commands D3) */ }
public sealed record SectorStorageDto {
    public string WorldId { get; init; } = "";
    public string SectorId { get; init; } = "";
    public string? OwnerFactionId { get; init; }     // live read (:135-147) — the capture-header input, §Design 5
    public int AsOfTurn { get; init; }
    public IReadOnlyList<SectorStorageRowDto> Rows { get; init; } = Array.Empty<SectorStorageRowDto>();
    public int SlotsUsed { get; init; }              // row count, never summed qty (:120-125)
    public int SlotCapacity { get; init; }           // SectorItemCapacity.EffectiveCapacity (:14-27)
}
public sealed record ClaimableCacheDto {
    public string CacheId { get; init; } = "";
    public string PlaceKind { get; init; } = "";     // 'world_sector' | 'world_lane' — closed, the only two this verb serves (:184-187)
    public string PlaceRef { get; init; } = "";
    public string SourceKind { get; init; } = "";
    public int ItemCount { get; init; }              // row count only — never contents (hidden-until-found: the pin shows presence, the claim flow shows contents after reachability is proven again at claim time)
    public string CreatedUtc { get; init; } = "";
}
public sealed record ClaimableCacheListDto {
    public string WorldId { get; init; } = "";
    public string EntityId { get; init; } = "";
    public int AsOfTurn { get; init; }
    public IReadOnlyList<ClaimableCacheDto> Caches { get; init; } = Array.Empty<ClaimableCacheDto>();
    public int ClaimCostMilli { get; init; }   // live claimCostMilli from tuning — the AP slot binds this (added 2026-09-16, cost follow-up closed)
}
```

`ItemCount` is a count, not contents, deliberately: the list answers "something lies here"
for the pin; the per-row contents arrive only through the claim result / a future
claim-detail read after the reachability re-check (`IsCargoClaimReachableUnlocked`,
`RpgStore.CacheFieldAccess.cs:163-199`) has run. Serving full contents on the list would
hand every cache's manifest to any viewer that asks — the fog leak hidden-until-found exists
to prevent.

FE mirrors (`types.ts` additive views + `adapt.ts` folds, same extension rule as
`gk-web/web/fusion-rpg-web/src/contract/types.ts:1449-1462`): `CargoView` (rows + used/capacity fractions), `VaultView` (rows + room),
`CachePinView` (presence + count). The fold computes meter fractions from the four numbers
and maps reason strings to authored copy — it never recomputes capacity, never compares
positions, never prettifies an id (ideal §2.7).

### 5. Messaging contracts for `legion-sheet` / `storage-cache-ui`

The wire carries backend reason strings verbatim; player sentences are authored copy
(GG-62), owned by wave 2, keyed off this closed list. This spec freezes the list — the fold
authors copy against it, never against a new string invented at implementation:

| Wire string | Producer | Player-visible contract (wave 2 authors the sentence) |
|---|---|---|
| `cache.claimed:<c>+<s>` + stored `ClaimedSeqs`/`SkippedSeqs` | claim pass (§Design 3; `CorpseCacheCargoClaimResult`, `RpgStore.CacheFieldAccess.cs:31-37`) | Partial-success copy: what fits is aboard, what stays waits where it lies (ideal §3 one-sentence rule) — per-row fits/left-behind states on `stock-row` |
| `cache.unreachable` | reachability re-check (`:302-304`) | Stale-pin copy: the cache is no longer where the band stands (marched away / forged id) |
| `cargo.over-weight` / `cargo.no-slots` (as skips, not errors) | per-row gates (`:326-337`) | Left-behind copy naming the gate that fired |
| `cargo.not-present` / `cargo.wrong-faction` / `cargo.sector-full` / `cargo.not-found` / `cargo.cross-empire` / `cargo.not-owned` | deposit/withdraw/transfer/load verbs (`RpgStore.CargoTransfer.cs:55-60,133-134`; `RpgStore.LegionCargo.cs:282-304,407-414,470-500`) | Refusal copy on the deposit/withdraw/handoff actions |
| `correlation.missing` | claim verb (`:289-292`) | Unreachable on the command path (named, not re-checked — spec-cargo-commands §Design 3); listed so the fold never authors copy for it |
| Capture header: `OwnerFactionId` (live, `SectorStorageDto`) + turn-report entry for the loser | capture hook no-op-by-construction (`RpgStore.SectorStorage.cs:171-196`: reachability is derived live, so reassignment takes effect in the same tx) + ideal Owner resolution | Vault header always shows "held by X"; band-4 toast + turn-report entry on capture (ideal §10 Q4 resolution). The event feed itself is `capture-notice`'s module, not this one's — this spec supplies the header input + the report-entry vocabulary, never the toast component |
| Stored-report detail (hot tail, 50 turns) | `RpgStore.WorldTurns.cs:468,549-567,589` | Claim/capture lines older than the hot tail are re-derived without cargo entries (spec-cargo-commands §Design 5 gap, consumed here): surfaces read stored detail while it lives and read-back DTOs after — never assume replay reproduces a claim line |

## Tunables

**None.** This module creates no tunable, retunes none, and touches no tuning file. Names it
reserves-but-does-not-create (owners named):

| Tunable | Home | Owner |
|---|---|---|
| `CargoWeightPerUnit` (`long`), `CargoSlotsPerUnit` (`int`) | `gk-core/data/tuning/scoped-inventory.v1.json` (exist) | scoped-inventory (reused via `ScopedInventoryPolicy`) |
| `ItemStorageCapacityBonus` per structure row | Seed-authored structure rows | `storage-content` (module 3) |
| `claimCostMilli`, `depositCostMilli`, `withdrawCostMilli`, `loadCostMilli`, `unloadCostMilli` (per-mille) | `data/tuning/world.v{n+1}.json` `movement` — RESERVED by `cargo-commands` §Design 6, CREATED by `world-action-economy` `act-price-table` (key owner) | world-action-economy |
| Player refusal/confirmation sentences | Authored copy catalog (GG-62); home file named at wave-2 spec time | `legion-sheet` / `storage-cache-ui` (wave 2) |

## Numeric types

Inherited from spec-cargo-commands §Numeric types, extended to the DTOs: `Qty`,
`WeightEach`, `RowWeight`, `WeightUsed`, `WeightCapacity` are `long`, `checked`
(`RpgStore.LegionCargo.cs:183-189,204-205`; `RpgStore.CacheFieldAccess.cs:322-324`;
`RpgStore.CargoTransfer.cs:170-171`). `Seq`, slot counts, `ItemCount`, `AsOfTurn` are `int`
— structural bounds, commented as such. On the FE, `long` figures cross the wire beside
their exact decimal strings where they can exceed 2^53 (`gk-web/web/fusion-rpg-web/src/contract/types.ts:108-119` `Magnitude.exact`
precedent) — the DTOs above carry the numeric field; the exact-string beside-field is added
at implementation if any figure can reach past `Number.MAX_SAFE_INTEGER`, never a
`number`-into-`long` parse-back. Integer overflow throws, never wraps (DESIGN-GATE §2.13).

## Commands

```powershell
dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~CacheFieldAccess"
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~World"
python gk-core/scripts/guard-dal.py        # every new SQL string lives in FusionRpg.Data (these routes add none — projection only)
```

## Structure

```
gk-core/src/FusionRpg.Contracts/WorldDtos.cs          MODIFIED — five DTOs (§Design 4), additive; ClaimableCacheDto
                                                       carries count-only, never contents
gk-core/src/FusionRpg.Server/WorldEndpoints.cs        MODIFIED — four routes (§Design 1) + claims filer construction;
                                                       delegation to SubmitWorldCommands / ListClaimableCaches /
                                                       ListCargo / ListSectorStorage + capacity reads; no verb called
                                                       directly, no SQL in Server (guard-dal)
gk-web/web/fusion-rpg-web/src/contract/types.ts      MODIFIED — CargoView / VaultView / CachePinView, additive
                                                       (types.ts:11-19 extension rule — no CONTRACT_VERSION bump)
gk-web/web/fusion-rpg-web/src/contract/adapt.ts      MODIFIED — three folds (fractions + reason→copy-key mapping, never
                                                       capacity/position recomputation)
gk-core/tests/FusionRpg.Server.Tests/WorldClaimEndpoints/  NEW — presence-gating, hidden-until-found, filer idempotency,
                                                       one-scope reads, refusal-verbatim, no-weight-on-wire
UNTOUCHED: TurnEngine.cs (purity); RpgStore.WorldTurns.cs (submit/commit/rehydrate — called, never
           modified); RpgStore.CacheFieldAccess.cs, RpgStore.LegionCargo.cs, RpgStore.SectorStorage.cs,
           RpgStore.CargoTransfer.cs verb bodies (called, never modified); WorldCommand.cs kinds/payload
           (cargo-commands' surface — consumed field-for-field); WorldState schema/StateHasher (unhashed
           overlays); Intel/belief projection; decay tick; DiffEntities/DiffSectors; AI policies; every
           tuning file; gk-data/packs/fusion/data/seed/** and gk-data/packs/fusion/data/generated/** (no content touched).
```

## Code style

```csharp
// A filer, not a mutator: construct the command, file it, report filing — resolution
// happens at commit through the cargo-commands pass, never here.
var command = new WorldCommand
{
    CommanderId = commanderId,
    CommandId = body.CommandId?.Trim() ?? "",
    Kind = WorldCommandKinds.ClaimCache,   // the converged kind (spec-cargo-commands Locked anchors)
    EntityId = entityId,
    CacheId = body.CacheId?.Trim(),        // weightEachFor resolves server-side at commit — never on this wire
};
var outcome = store.SubmitWorldCommands(worldId, new[] { command }).Single();
return Results.Ok(new WorldCommandResultDto { CommandId = outcome.CommandId, Ok = outcome.Ok, Reason = outcome.Reason, Replayed = outcome.Replayed });
```

## Testing strategy

- **Presence-gated listing:** a legion on a cache's sector/lane lists it; a legion one
  sector away lists nothing (`200` empty); a both-set/neither-set legion lists nothing
  (corrupt-sees-nothing precedent, `RpgStore.CacheFieldAccess.cs:69-72`).
- **Hidden-until-found server-side:** the response for a legion with no reachable cache
  contains zero cache ids — asserted on the body, not on FE behavior; no `visible: false`
  member exists on the DTO (structural, via schema assertion).
- **Unknown legion vs empty:** unknown `entityId` → `entity.unknown`; known legion, no
  cache → `200` empty. The two are asserted separately so a test never confuses "caller
  error" with "nothing here".
- **Foreign legion refused:** a legion owned by another faction → `entity.not-yours` even
  when a cache is reachable at its position (ownership root precedes reachability).
- **Filer idempotency:** same `CommandId` posted twice → second returns `Replayed: true`,
  one stored command row; missing `CommandId`/`CacheId` refuse `command.id-missing` /
  `cache.missing` at submit with zero writes.
- **Filer never resolves:** after POST, the cache rows are untouched and cargo unchanged —
  the claim moves only at commit through the `cargo-commands` pass (file-vs-resolve
  separation, GG-15).
- **One-scope reads:** cargo read returns exactly the legion's rows; storage read exactly
  the sector's; neither accepts a wildcard, and a probe asserts no route lists across
  legions/sectors (Diablo-memory precedent, ideal §6).
- **Refusals verbatim:** every §Design 5 string byte-matches the verb's own string; the
  `correlation.missing` row asserts unreachable-on-this-path (named in the contract, never
  produced by the filer).
- **No weight on the wire:** schema assertion over all four request DTOs — no
  `weightEach`-shaped member exists.
- **Stored detail, not replay:** a committed claim's `cache.claimed:<c>+<s>` line is read
  from the stored hot-tail report; the test documents (not re-proves) that post-trim
  re-derivation omits it (spec-cargo-commands §Design 5 gap).

## Boundaries

- **Always:** gates before writes (admission at submit, reachability at resolve); verb
  reasons verbatim onto the wire; one legion / one sector per read; list = position-proven
  presence, never contents; claim result via report + read-backs, never the filer response.
- **Ask first:** exposing cache row contents pre-claim (a claim-detail read would weaken
  hidden-until-found — product call, not a fix); a co-location gate for transfer display;
  any price/allowance/budget surface beyond relaying the debit seam's future spent-shape
  refusal (world-action-economy's program).
- **Never:** a weight field on any request; a bulk/list-all route; a direct-mutation POST;
  SQL in Server; client-side fog/position/capacity logic; a second claim-log or cargo
  table; a renamed refusal string; a tuning-file edit; a generated-data edit.

## Success criteria

1. Four routes file/list/read-back per §§Design 1–4, each refusal byte-matching the named verb or gate string.
2. Hidden-until-found holds on the body: no reachable position, no cache ids — zero client logic.
3. `correlationId := CommandId` end to end: double-POST replays at submit, re-commit replays at resolve, both byte-identical.
4. `guard-dal.py` green; no SQL outside `FusionRpg.Data`.
5. Zero edits to every path in the Non-touch list (verified by diff).

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| Four routes + five DTOs + §Design 5 reason/message contract (§§Design 1–5) | `legion-sheet` (wave 2) — cargo sub-tab binds `LegionCargoDto` + `cargo-fold`; refusal copy authored against the closed list |
| `ClaimableCacheListDto` (count-only) + filer idempotency + report-detail vocabulary | `storage-cache-ui` (wave 2) — `cache-pin` binds presence/count; claim flow files + folds `cache.claimed:<c>+<s>` / skip lists; capture header binds `SectorStorageDto.OwnerFactionId` + toast/report entry |
| `correlationId := CommandId` + debit-after-refill + reserved `*CostMilli` names (relayed, not re-decided) | `world-action-economy` — prices the filed kinds without touching these routes |

## Design-gate checklist

```
[x] Subsystems: world-map turn/ordering (Core), cargo/cache Data verbs, Server HTTP surface, FE
    contract mirrors. No Status/ActorHub/Combat/Injector subsystem touched.
[x] Read this session: spec-cargo-commands.md (IN FULL — six kinds, post-Step pass, debit seam +
    debit-after-refill order, playerId recorded-not-restored, consumed exactly); empire-inventory-
    surfaces-map.md (module 2 row); empire-inventory-surfaces-ideal.md (§4 cache rows, §6 Diablo
    one-scope precedent, §9 backend-reads note, Owner resolutions: hidden-until-found pins,
    header+toast); spec-cache-field-access.md §1a/§2a (ListClaimableCaches/ClaimCorpseCacheIntoCargo
    shapes, reachability, replay key); DESIGN-GATE.md §1 rows + §2 invariants + §5 checklist.
[x] Code cited by file:line, opened this session in the worktree: WorldEndpoints.cs (:13-17 two-write
    lock, :22 bound, :28,37,92,148,191,259 route list, :42-47 viewer, :99-103/:153-156 commander
    default, :108-121 mapping, :126 submit, :344-366 fog precedent); WorldCommand.cs (:103-104
    idempotency key); WorldDtos.cs (:450-472 request, :484-490 result, :542-551 log DTO);
    RpgStore.WorldTurns.cs (:84-153 submit, :462-465 payload, :510-591 commit, :589 trim, :704-728
    rehydrate); RpgStore.CacheFieldAccess.cs (:31-37 result, :48-106 list, :163-199 re-check,
    :223-256 replay log, :267-273 weight discipline, :280-366 verb); RpgStore.LegionCargo.cs (:11-19
    row, :30-35 no-weight-column, :101-106 capacities, :151-218 reads, :220-242 ownership);
    RpgStore.CargoTransfer.cs (:55-60,:133-134 refusals, :121-131 weight discipline);
    RpgStore.SectorStorage.cs (:98-169 reads, :171-196 capture hook); SectorItemCapacity.cs (:14-27);
    types.ts (:11-19 extension rule, :108-119 exact-string precedent); contractGuard.ts (:115).
[x] Checked decisions.md for a covering lock: scoped-inventory SSOT (one ownership root,
    move-never-copy) reused via cargo-commands; no "claim-endpoints" lock exists — greenfield at
    the route level, constrained surface otherwise.
[x] Verified claims against CODE, not comments (all citations opened in-session in the worktree;
    zero-route gap proven by enumerating the six mapped routes; FE gap proven by grep over
    web/.../contract).
[x] Read the surrounding section of every rule quoted (two-write lock :13-17 with its reads-are-
    projections context; viewer comment :34-37; commit-turn-required :158-162; fog rules :313-342
    with the sectorless-entry scoping; claim-log key with its delve-sentinel columns).
[x] Tested (not assumed) constraints: no suite run — spec phase, no code; the no-bump and
    replay claims are staked on named new tests, not asserted as measured.
[x] Nothing contradicts a §2 invariant: SQL only in FusionRpg.Data (projection-only routes);
    no magnitude cap (capacities/room are structural, fixture-bound, refuse-with-reason); no
    f(Θ) (no level-derived number anywhere); no second ownership root (CommanderId + entity
    gates, playerId recorded-not-restored per cargo-commands D2); no second composer; SOLID:
    one filer into one submit path, one list read reused never forked, helpers reused never
    redefined.
[x] No assertion pins a derived-population count, item total, generated name/description, or
    per-cycle outcome. (Counts named: 4 routes + 5 DTOs + 6 commands — closed code-owned
    vocabularies with stated reasons; hot-tail 50 — an existing stored constant cited, not
    asserted; ItemCount — a per-cache reading, never a pinned literal.)
[x] No event-refreshed cache introduced. (AsOfTurn is a staleness marker; pins re-read per
    selection — stated in §Design 2.)
[x] No acceptance criterion fixes an ordering that can vary in real play. (Per-row seq order is
    the verb's own deterministic tie-break, asserted; file→commit→report→read-back is the fixed
    pipeline sequence.)
[x] No actor combat/derived magnitude produced or consumed — actor-sheet boundary not crossed.
[x] No SOLID-violating parallel path: no second submit path, no parallel price engine, no forked
    capacity/reachability math, no second claim log; the economy's debit stays a stub in the one
    seam.
[ ] The production weightEachFor lookup has no named function in code today — consumed as
    cargo-commands §Design 4's named-first-task, not assumed solved. (Honest gap, inherited.)
```
