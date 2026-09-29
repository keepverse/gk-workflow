# Spec: `wonder-rest`

**Status: written against shipped code 2026-09-15** — every `file:line` below was opened this
session in worktree `empire-development-20260915-b7e2`; main checkout untouched. Module id
`wonder-rest`, row 1 of the [empire-wonder-surfaces map](../empire-wonder-surfaces-map.md)
(wave 1, no dependency — builds in parallel with `wonder-content`). Ideal:
[empire-wonder-surfaces-ideal.md](../empire-wonder-surfaces-ideal.md) (§4 order-shape rows, §9.7,
§10 Q1–Q4 answered). Backend contract:
[loam-relics-and-wonders/spec-wonder-build-flow.md](../loam-relics-and-wonders/spec-wonder-build-flow.md)
(§Design 1/3/4/6–7). Decisions: [decisions.md](../decisions.md) "Loam relics and wonders SSOT
(2026-09-13)" and "Scoped inventory hierarchy SSOT (2026-09-13)".

## Objective

Close the one wire gap between the shipped Wonder build engine and every caller above it: a
`build` order naming a Wonder-shaped `StructureId` (`RelicCost > 0`) must be able to carry its
`RelicInstanceIds` from the FE pending-order queue, over HTTP, through the endpoint mapping,
into the store payload, and to `TurnEngine.Step` — where the already-shipped admission gate,
Data-side reachability gate, and spend already handle it. Then pay the owed live proof: one real
Wonder build filed over HTTP, committed, started, spent, and completed, read back through the
normal paths.

Success looks like: the composer (module `wonder-composer`, wave 2) can file
`{ structureId, slotIndex, relicInstanceIds }` and have the exact list the player picked reach
`WorldCommand.RelicInstanceIds` unchanged; a malformed list is refused at submit-time
admission with the same
`relic.count-mismatch` / `relic.duplicate` strings admission already owns; and one live
RPG-server-debug probe proves the whole path file → commit → `build.started` → `disposition =
'consumed'` → slot completed after `BuildTurns`.

## Locked anchors

- **The engine half is built and untouched.** `WorldCommand.RelicInstanceIds`
  (`WorldCommand.cs:139-145`), the admission count/dup check
  (`WorldCommandAdmission.cs:112-119`), the store payload round-trip
  (`RpgStore.WorldTurns.cs:186-189,462-465,723-726`), the Data-side gate + spend
  (`RpgStore.WonderBuild.cs:53-227`), the commit wiring (`RpgStore.WorldTurns.cs:531-547`),
  and the resolver refusals (`BuildResolver.cs:102-110`) all ship. This module adds no new
  engine behavior and changes none of it.
- **The request shape locked here is `wonder-composer`'s contract.** Wave-2 composer work
  consumes `relicInstanceIds?: string[]` on `PendingOrder`, `WorldCommandRequest` (TS), and
  `WorldCommandRequest` (C#) by name (GG-9: link, don't re-implement). Composer may add picking
  UI; it may not rename, re-shape, or fork this field.
- **Refusal strings are owned by admission, never mirrored.**
  `relic.count-mismatch` and `relic.duplicate` already exist at
  `WorldCommandAdmission.cs:116-118`, enforced at submit and at Reveal. This module adds no
  endpoint-level check (deleted 2026-09-15, SOLID — a third site with zero new information);
  the identical strings for the identical symptoms arrive via admission, never a second spelling.
- **No new numbers.** There is no tunable in this module — no cost, no cap, no threshold, no
  timeout. `RelicCost` stays owned by the seed corpus (`spec-wonder-build-flow.md` §Tunables);
  caps stay owned by `WonderPolicy.ExistenceCapFor`. A balance-shaped literal appearing in this
  diff is a review failure.
- **Ideal §10 Q1–Q4 answers are consumed, not re-decided.** Composer host is a band-2 panel,
  relic picking is reachable-first (legion cargo tab + sector store), caps show live counts,
  reserved tiers render as locked teasers (`empire-wonder-surfaces-ideal.md` Owner resolutions).
  This module's only obligation to them is to not foreclose them: the wire carries the full
  picked list (reachable-first needs it) and drops nothing the count display needs.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| `WorldCommand.RelicInstanceIds` — opaque-to-Core list of `rpg_item.instance_id` strings, empty for every non-Wonder order | `gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:139-145`, read in full this session |
| Admission structural check — right count, no duplicates, never an ownership check | `gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs:112-119` (`relic.count-mismatch` at `:116`, `relic.duplicate` at `:117-118`) |
| Store payload round-trip — `CommandPayload` carries `RelicInstanceIds`, serialize at insert, null-tolerant read-back (pre-field rows read as empty) | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:186-189` (serialize), `:462-465` (record), `:723-726` (read-back) |
| Data-side reachability gate — owned/live/unassigned/Relic-container + reachable-right-now + per-batch `claimed` set; failures rewritten to empty | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WonderBuild.cs:53-117` (gate), `:128-182` (per-id check) |
| Commit wiring — gate before `TurnEngine.Step`, spend after `DiffWorldGraphUnlocked`, same `tx` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:531-547` |
| Resolver re-check (`relic.not-reachable`) + cap (`wonder.cap-reached`) + materials (`build.cannot-afford-materials`) | `gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:102-132` |
| Relic spend — fires only on an accepted `build.started:` line, deletes both overlays best-effort, marks `disposition = 'consumed'` exactly once (loud on 0/2 rows) | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WonderBuild.cs:202-253`; `RelicConsumedDisposition = "consumed"` at `:27` |

### Wiring gap

| Gap | The inert/underused line |
|---|---|
| `WorldCommandRequest` (C#) carries `structureId`/`slotIndex` but no relic list — a Wonder order filed over HTTP cannot name its relics | `gk-core/src/FusionRpg.Contracts/WorldDtos.cs:449-472` (full record; no `RelicInstanceIds` field anywhere in it) |
| `POST /{worldId}/commands` maps every `build` field except the relic list — even a correct FE payload would be dropped at the boundary | `gk-core/src/FusionRpg.Server/WorldEndpoints.cs:108-121` (projection; no `RelicInstanceIds` line) |
| FE `WorldCommandRequest` mirror has `stance`/`amount`/`structureId` but no relic list | `gk-web/web/fusion-rpg-web/src/lib/bus/world.ts:277-295` |
| FE order queue carries `structureId`/`slotIndex` but no relic list, and `toRequests` maps everything the wire accepts except relics | `gk-web/web/fusion-rpg-web/src/stages/world/worldSelection.ts:28-46` (`PendingOrder`), `:106-118` (`toRequests`) |
| Zero FE references to the whole Wonder refusal vocabulary — nothing could file, and nothing could explain a refusal, even if the engine refused correctly | `worldSelection.ts` + `bus/world.ts` carry no `relicInstanceIds`; ideal §4 confirms the web-wide grep (`wonder\|RelicCost\|RelicInstanceIds\|cap-reached\|count-mismatch\|not-reachable`) returns only a "wondering" comment false positive |

### Real gap

| Gap | What this module builds |
|---|---|
| No end-to-end proof that a Wonder build filed over HTTP resolves, spends, and completes against live tables | The owed live proof (§Design 4) — RPG-server-debug scope, real relic rows, normal-path read-back. Static + adapter evidence only exists today (ideal §0 honest gaps: no live game probe ran). |

## Design

### 1. `WorldCommandRequest.RelicInstanceIds` — the C# DTO field

```csharp
// WorldDtos.cs — new optional field on WorldCommandRequest, following StructureId's own
// nullable-optional convention. List<string>?, null = "spends no relic", matching every other
// optional payload field on the same record.
public List<string>? RelicInstanceIds { get; set; }
```

Null-tolerant by construction: absent (every non-Wonder order, every old client) reads as "spends
no relic" — the same posture `CommandPayload.RelicInstanceIds` already takes on read-back
(`RpgStore.WorldTurns.cs:723-726`). Element type is `string` (opaque `instance_id`s); no magnitude,
no enum, no closed vocabulary to extend.

### 2. Endpoint mapping — `WorldEndpoints.cs:108-121` (no early pass)

The existing projection gains exactly one line:

```csharp
RelicInstanceIds = c.RelicInstanceIds,
```

**No endpoint-level count/dup pre-check** (DELETED 2026-09-15 strengthen pass, lens B2 SOLID:
the draft's early structural pass duplicated `WorldCommandAdmission`'s `relic.count-mismatch` /
`relic.duplicate` rule at a third site with zero new information). Submit-time admission
(`RpgStore.WorldTurns.cs:114-119`, per-command reasons) already teaches the filer at file time;
Reveal re-admits (`TurnEngine.cs:199-206`). One rule, two existing sites, no third.

Rules for the mapping line:

- **Unknown `structureId` never reaches a `Get`.** The mapping copies the list opaquely; admission
  owns `structure.unknown` for forged/typo ids (no `IsKnown` call here — Core has no DB access
  and the endpoint must not throw where admission refuses).
- **Non-Wonder orders ignore the field.** `RelicCost == 0` with a non-empty list is inert data
  the resolver never reads (spend skips `RelicCost <= 0` rows,
  `RpgStore.WonderBuild.cs:211-213`) — the endpoint does not invent a refusal for it.
- **Merge order (shared record with cargo-commands).** This spec and `spec-cargo-commands.md`
  extend the same `WorldCommandRequest` + mapping function for different fields; both land
  additively, neither reorders existing lines — merge in either order, no dependency.
- **Known pre-existing wire loss (not this module's).** The same DTO/mapping already drops
  `WardenId` (Core/payload/rehydrate carry it — `bind-warden` unfilable over HTTP) and the TS
  mirror lacks `projectId` (`develop` unfilable from FE). Named so a reader doesn't mistake the
  mapping's field-for-field discipline for a claim the wire is complete.

### 3. FE mirror — `bus/world.ts` + `worldSelection.ts`

```ts
// bus/world.ts — WorldCommandRequest gains:
relicInstanceIds?: string[] | null;

// worldSelection.ts — PendingOrder gains:
relicInstanceIds?: string[];
// toRequests maps it:
relicInstanceIds: order.relicInstanceIds ?? null,
```

`null`/absent = "spends no relic", matching the C# DTO. No validation logic in the reducer
beyond faithful round-trip (the `stance`-was-dropped precedent, `worldSelection.ts:96-104`, is
exactly what this closes for relics): every field the queue carries the wire must carry. Picking
order is preserved (list order is what the `claimed` set and the spend iterate). Reachable-first
filtering, shelf UI, and refusal copy are `wonder-composer` / `wonder-refusal` work — this module
only guarantees the picked list survives to the wire.

### 4. The owed live proof — acceptance, RPG-server-debug scope

**Scope label: RPG Server Debug** ([live-probe-standard.md](../../contributing/live-probe-standard.md);
DESIGN-GATE §1 "Proving a feature works live" row). This probe runs the real
application/domain/persistence path (`POST /commands` → `CommitWorldTurn` → `TurnEngine.Step` →
`DiffWorldGraphUnlocked` → `SpendWonderRelicsUnlocked`) against real rows — never a fabricated
relic id, never an injector-fabricated assertion.

Steps, each read back through the normal path (a response body alone is never proof):

1. **Setup (real rows only):** a real world with a held sector, an empty compatible slot, a
   Wonder-shaped `StructureDef` with known `RelicCost = N`, and N real `rpg_item` rows
   (`disposition` live, `origin_kind = 'drop'`, Relic-container `origin_ref`) reachable via the
   issuing legion's cargo or the target sector's storage. Record every id.
2. **File over HTTP:** `POST /api/world/{worldId}/commands` with one `build` order naming the
   Wonder `structureId`, `slotIndex`, and the N `relicInstanceIds`. Expect per-command `ok:true`
   (submit-time admission passes).
3. **Commit:** `POST` the turn commit (all commanders). Expect the turn report to contain
   `build.started:<structureId>` for the filed `CommandId`.
4. **Read back the spend through the normal path:** query the `rpg_item` rows — every named relic
   reads `disposition = 'consumed'`; both overlay rows (cargo / sector-storage) for those ids are
   gone. Query the sector/slot — the slot carries the Wonder `structureId` with
   `constructionTurnsRemaining == BuildTurns`.
5. **Advance `BuildTurns` turns** (End Turn commits) and read the slot again: construction completes
   (remaining reaches zero, structure stands). Refusal-path probes (wrong count → `relic.count-
   mismatch`; unreachable id → `relic.not-reachable`; over cap → `wonder.cap-reached`) are
   `wonder-composer`/`wonder-refusal` acceptance, not this module's — named here so the proof is
   not mistaken for covering them.

Failure semantics: any step failing fails the module — the wire is not done when it compiles.

## Tunables

None. This module introduces zero tunable numbers — no cost, no cap, no rate, no threshold.

| Number a reader might expect here | Actual home (not this module) |
|---|---|
| `RelicCost` per Wonder row | Seed corpus (`gk-data/packs/fusion/data/seed/structures/**`), per `spec-wonder-build-flow.md` §Tunables |
| `UniqueExistenceCap.Sector` / `.Empire` | `gk-core/data/tuning/loam-relics-wonders.v1.json`, owned by `wonder-structure`, read via `WonderPolicy.ExistenceCapFor` |
| Material costs (`Cost`, `ConstructRubbleCost`/`ConstructIronworkCost`) | Existing structure rows; resolution already spends them (`BuildResolver.cs:125-132`) |

## Numeric types

`RelicInstanceIds` carries opaque strings — no magnitude, no width question. The only numeric
comparison this module's validation performs is `ids.Count (int) != needed (long RelicCost)` —
an `int`-vs-`long` comparison that needs no widening cast and cannot overflow (a list Count is
structurally bounded by the request body; `MaxCommandsPerSubmit` already bounds the batch above
it). No `contentScale`, no per-mille math, no narrowing.

## Commands

```powershell
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~WorldCommandAdmission"
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~WorldCommands"
python gk-core/scripts/guard-dal.py        # no new SQL in this module — must stay green
```

```powershell
# web (gk-web/web/fusion-rpg-web):
npm test -- worldSelection   # PendingOrder -> toRequests round-trip incl. relicInstanceIds
npm run build                # tsc --noEmit + vite build — type errors fail the build
```

## Structure

```
gk-core/src/FusionRpg.Contracts/WorldDtos.cs            MODIFIED — WorldCommandRequest + RelicInstanceIds (§Design 1)
gk-core/src/FusionRpg.Server/WorldEndpoints.cs          MODIFIED — mapping line only (§Design 2; no early pass — admission owns refusals)
gk-web/web/fusion-rpg-web/src/lib/bus/world.ts         MODIFIED — WorldCommandRequest + relicInstanceIds (§Design 3)
gk-web/web/fusion-rpg-web/src/stages/world/worldSelection.ts   MODIFIED — PendingOrder + toRequests (§Design 3)
tests/FusionRpg.Server.Tests/World/             EXTENDED — mapping tests (§Testing strategy)
gk-web/web/fusion-rpg-web/src/stages/world/worldSelection.test.ts  EXTENDED — round-trip test (§Testing strategy)
UNTOUCHED: WorldCommand.cs, WorldCommandAdmission.cs, BuildResolver.cs, RpgStore.WonderBuild.cs,
           RpgStore.WorldTurns.cs, StructureCatalog.cs, relic minting/drop tables, cargo/storage schemas
```

## Code style

```csharp
// Endpoint projection — one line, same flat style as every sibling field.
RelicInstanceIds = c.RelicInstanceIds,
```

```ts
// toRequests — the same ?? null discipline every optional field already uses.
relicInstanceIds: order.relicInstanceIds ?? null,
```

## Testing strategy

- **Mapping round-trips:** a `build` request with N ids reaches `WorldCommand.RelicInstanceIds`
  unchanged (order preserved); absent/null reaches the store as empty (pre-field posture).
- **Admission refusal over HTTP:** wrong count → `relic.count-mismatch`; repeated id →
  `relic.duplicate`; per-command `Ok:false`, rest of batch unaffected (submit-time admission,
  never an endpoint pass).
- **FE round-trip:** `PendingOrder` with `relicInstanceIds` survives `toRequests` (and a
  no-relic order emits `null`, not `[]`-vs-`null` drift); existing
  `worldSelection.test.ts:163-173` structure-id coverage stays green alongside.
- **No silent cleaning:** blank/whitespace ids refuse at admission (`count-mismatch`), never trimmed away.
- **Live proof (§Design 4) is the acceptance gate** — unit tests prove the wire; only the probe
  proves the build. No population-count or generated-text pins (validation-ssot): assert refusal
  strings (closed vocabulary, owned by admission — state the reason), `consumed` disposition
  (closed value owned by this program), `build.started:` report prefix, and slot remaining-turn
  transitions — never corpus sizes, item totals, or authored names.
- **Not covered here:** reachability/cap/material refusals over HTTP, composer picking,
  refusal copy, cap-count display — each belongs to its wave-2 module.

## Boundaries

- **Always:** pass the picked list through untouched at every layer (queue → TS wire → C# DTO →
  endpoint → store); admission's own strings surface at submit; prove live over HTTP with normal-
  path read-back. Merge order with cargo-commands' DTO/mapping extension: additive both sides,
  either order — no dependency either way.
- **Ask first:** any change to the refusal strings (owned by `WorldCommandAdmission`); any second
  wire shape for relics (a parallel field is a SOLID fork — extend this one).
- **Never:** engine changes (resolver/admission/spend/store wiring are built — §Locked anchors);
  relic minting/ownership logic (read rows, never author them); cargo/storage schema or verb
  changes (consumed, never re-implemented); catalog/slot wire additions for cap counts,
  scope/rarity, or `RelicCost` display (ideal §9.7 backend-reads note — plan Tasks 4A.3/4B
  dependencies, `wonder-display`'s problem, not this module's); composer/refusal/shelf UI (wave-2
  modules); a second debug surface re-implementing these endpoints (adapter-wrap, scope-label —
  debug-mcp-ideal assessed shape).

## Success criteria

1. A Wonder `build` order's picked relic list survives queue → HTTP → endpoint → store → engine
   unchanged, proved by round-trip tests at each layer.
2. Malformed lists refuse with `relic.count-mismatch` / `relic.duplicate` at submit-time
   admission, per-command, batch intact.
3. The owed live probe passes: file over HTTP → commit → `build.started:` + every named relic
   `disposition = 'consumed'` + slot completes after `BuildTurns` (RPG-server-debug scope,
   normal-path read-back).
4. `guard-dal.py` green (no new SQL). 5. Zero changes to engine, relic, cargo/storage, or
   catalog code. 6. `wonder-composer` can consume the locked shape by name with no further wire
   work.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `WorldCommandRequest.RelicInstanceIds` (C#) + endpoint mapping | `wonder-composer` (module 3) — files the picked list; never re-maps it |
| `WorldCommandRequest.relicInstanceIds` (TS) + `PendingOrder.relicInstanceIds` + `toRequests` | `wonder-composer` — the picking UI's only file path |
| Live-proof procedure (§Design 4) | `wonder-composer` / `wonder-refusal` — reuse the probe harness for their own refusal/display acceptance |

## Design-gate checklist

```
[x] Subsystems: world command wire (Contracts/Server/FE queue) + Wonder build contract (read-only
    refs). No Status/ActorHub/Combat, no engine behavior change.
[x] Session boundary: worktree empire-development-20260915-b7e2 only; main checkout untouched.
[x] Read this session: empire-wonder-surfaces-map.md row 1; empire-wonder-surfaces-ideal.md (§4
    order-shape rows, §9.7 backend-reads note, §10 Q1-Q4 answered + Owner resolutions, §0 honest
    gaps); loam-relics-and-wonders/spec-wonder-build-flow.md (§Design 1/3/4/6-7, recipe-shape
    decision, Tunables); DESIGN-GATE.md (§1 proving-live row, §2 invariants, §5 checklist).
[x] Checked decisions.md: Loam relics and wonders SSOT + Scoped inventory hierarchy SSOT rows —
    no "wonder REST" lock; greenfield wire confirmed.
[x] Every factual claim cites file:line, verified against CODE this session: WorldCommand.cs
    (:139-145), WorldCommandAdmission.cs (:112-119), WorldDtos.cs (:449-472),
    WorldEndpoints.cs (:108-121), RpgStore.WorldTurns.cs (:186-189, :462-465, :531-547,
    :723-726), RpgStore.WonderBuild.cs (:53-117, :202-253), BuildResolver.cs (:102-132),
    bus/world.ts (:277-295), worldSelection.ts (:28-46, :106-118).
[x] Read the surrounding section of every rule quoted (admission doctrine, endpoint partial-
    acceptance comment, store null-tolerance comment, live-probe RPG-server-debug scope).
[x] Tested constraints: none claimed — no "moves goldens" / "needs sign-off" asserted. Suite
    selection stated in Commands; live proof is the acceptance that has not run yet (said so).
[x] No §2 invariant contradicted: SQL only in FusionRpg.Data (no new SQL); no cap on a magnitude
    (ids are opaque strings); no f(Θ); no second ActorHub composer; no parallel relic path
    (extends the one command kind); no second debug surface.
[x] Corrections propagated: prose + Structure + Testing + Boundaries + Interface agree on the
    four-file change set and the non-touch list.
[x] No assertion pins a derived-population count, item total, generated name/description, or
    per-cycle outcome. Refusal strings and 'consumed' are closed vocabularies owned by
    admission/this program, with reasons stated (validation-ssot).
[x] No event-refreshed cache introduced or touched.
[x] No acceptance criterion fixes a silently-ordered execution: live proof asserts set/state
    transitions (started + consumed + completed), not an order.
[x] No actor combat/derived magnitude produced or consumed.
[x] No SOLID-violating parallel path: reuses the one build kind, one DTO, one mapping, one
    admission vocabulary.
```

(End of file)
