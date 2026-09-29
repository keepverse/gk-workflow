# Spec: `storage-cache-ui`

**Status: written against shipped code 2026-09-15** — every `file:line` below was opened this
session in worktree `empire-development-20260915-b7e2`. Module id `storage-cache-ui`, row 5 of the
[empire-inventory-surfaces map](../empire-inventory-surfaces-map.md) (wave 2, depends on
`claim-endpoints` + `storage-content`). Consumes
[spec-claim-endpoints.md](spec-claim-endpoints.md) **in full, exactly as decided** — four routes,
`ClaimableCacheDto` count-only, `SectorStorageDto.OwnerFactionId` header input, the §Design 5
reason/message contract, `correlationId := CommandId`, reserved `*CostMilli` key names — and
[spec-cargo-commands.md](spec-cargo-commands.md) kinds (deposit/withdraw/claim-cache filing shapes)
and [spec-storage-content.md](spec-storage-content.md) (`relic-vault`, bonus 20, `Store ↔ Vault`) —
re-decides none of it. Ideals:
[empire-inventory-surfaces-ideal.md](../empire-inventory-surfaces-ideal.md) §5 rows 4–7
(storage-panel / capture-notice / cache-pin / cache-claim), §7 chosen shape (vault-block recipe,
pin → prompt → fits/left-behind → pick-up), §8 (vault-room content, AP-cost lock), Owner
resolutions (hidden-until-found pins, header+toast capture messaging, AP-cost pick-up). Authoring
order: [idea-ui-phase.md](../idea-ui-phase.md) §1 (recipe → fold + bus → themeRefs → HTML drafts →
owner accept → React mount). House style: `spec-legion-cargo.md` adapted for UI (recipe + fold +
bus + drafts, no production code in this spec).

## Objective

The wave-1 backend is filed and reachable (`claim-endpoints` four routes, `cargo-commands` six
kinds, `storage-content` one vault row) but no player path touches it: the sector inspector has no
vault block (`SectorInspector.tsx:73-126` — nine blocks, no storage member), no cache pin exists
anywhere under `gk-web/web/fusion-rpg-web/src` (grep this session: zero `cache-pin|CachePin` hits;
`claimable` hits only sector-claimability in `worldViewModel.ts:131,310` — a different concept,
so the no-cache-pin conclusion holds), and the refusal vocabulary has no player copy. This module gives the player three things,
all mounted on existing hosts, all bound to the wave-1 contracts: a vault block inside the sector
inspector, a cache-claim flow from map pin to pick-up, and capture-change messaging (header +
toast + report entry).

Success looks like: a held sector with a built `relic-vault` shows a vault block with stored
stacks and a room meter, and put-in / take-out move rows between the standing band and the vault
or the refusal names its gate in plain language; a band standing where a cache lies sees a pin and
a prompt offering pick-up with its AP price, and after the turn the panel shows what fits aboard
and what waits where it lies; the day after a capture the vault header reads "held by X" and the
loser got a toast plus a turn-report entry. No new route, no new stage, no new table.

## Locked anchors

- **Wave-1 contracts are consumed, not re-decided.** Kinds (`deposit-cargo`, `withdraw-cargo`,
  `claim-cache`), admission refusals, `correlationId := CommandId`, claim-before-decay,
  debit-after-refill, per-row fit/skip with `ClaimedSeqs`/`SkippedSeqs`, count-only
  `ClaimableCacheDto`, `SectorStorageDto.OwnerFactionId` — all in `spec-claim-endpoints.md`
  §§Design/Locked anchors and `spec-cargo-commands.md` §§Design/Locked anchors. Where this spec
  touches the same seam it quotes that spec's decision; where it differs it is wrong.
- **Hidden-until-found is server-side, never client fog logic.** The `GET claimable-caches`
  response **is** the fog rule (claim-endpoints §Design 2): a cache appears iff the selected
  legion stands where it lies, non-void, non-empty. This module binds pin presence 1:1 to that
  response. No client-side position compare, no `visible: false` member, no fog-branch in the
  fold — an FE that hides, groups, or second-guesses the list re-implements fog and is a defect.
- **One legion / one sector per open, never empire-wide.** The Diablo-memory precedent (ideal §6)
  is binding: the vault block reads one sector's `SectorStorageDto` per inspector open; the claim
  prompt reads one legion's `ClaimableCacheListDto` per selection. No bulk fetch, no
  event-refreshed cache, no subscription.
- **Outcomes are server-authoritative (GG-15).** The fold shows the last confirmed totals; the
  action's acknowledgment covers the round trip; refusal and partial-success copy comes back from
  the verb/report strings. No client-side capacity prediction ("you can fit 3 more") computed in
  a component — the rejected shape in ideal §7.
- **No engine words on the player surface** (ideal §2.7). The player reads packs, vaults, room,
  fallen caches, and plain reasons ("the packs are full", "what fits is aboard, the rest waits
  where it lies"). Table names, place kinds, disposition flags, correlation ids, and claim-log
  vocabulary live in the evidence table and in specs — never in panel copy. Player sentences are
  authored copy (GG-62), keyed off the closed reason list in claim-endpoints §Design 5.
- **No pricing here; no copy-home here.** The AP price is displayed from the `act-price-table`
  keys once `world-action-economy` creates them (`claimCostMilli`, reserved by
  cargo-commands §Design 6, relayed by claim-endpoints §Tunables); this spec reserves the display
  slot ("pick up (N AP)") and binds the value, never authors the number. Refusal/confirmation
  sentences live in the authored copy catalog whose home file is named at implementation — this
  spec freezes the key list, not the sentences.
- **Shared-piece-first.** `capacity-meter` (room density), `stock-row` (stored + left-behind
  states), `phase-*` lifecycle, `tool-search` are owned by this program and shared by name with
  `legion-sheet` and the sibling wonder program (ideal §5 shared map) — never twinned per
  surface. This spec writes recipes + folds + draft contracts against them; piece factories
  themselves are built/bound elsewhere.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Sector inspector shell: nine ordered blocks + action cluster, pure/presentational | `gk-web/web/fusion-rpg-web/src/stages/world/inspector/SectorInspector.tsx:72-126` (blocks render, `data-block-order`); `BLOCK_ORDER` in `./blockOrder.ts:7-17` (`identity, ground, next-turn, sector-loam, territory, slots, forces, warden, dowsing`); Actions region inline `:120-122` |
| `BLOCK_ORDER` re-exported from the inspector | `SectorInspector.tsx:128` (`export { BLOCK_ORDER }`) |
| World stage renders legions + lanes, mounts the inspector | `WorldStage.tsx:33` (`SectorInspector` mount); `:222` (`adaptWorldLegion`); `worldViewModel.ts:155-196` (`LaneEdge`/`LaneEdgeData`); `render/LegionMarker.tsx:49-99` (force marker); `render/SectorNode.tsx` (sector node) |
| Inspector Actions precedent: exactly one verb today (delve-door row) via the generic cluster | `SectorInspector.tsx:37,120-122` (`delveDoorVerb` + `ActionCluster`); `WorldStage.tsx:171` (verb computed by caller, never in the inspector) |
| Lifecycle pieces: loading / empty / error / pending factories + slot map | `gk-web/web/fusion-rpg-web/src/ui/gui-lego/pieces/lifecycle.tsx:18-55` (`phaseLoadingFactory`, `phaseEmptyFactory`, `phaseErrorFactory`, `phasePendingFactory`, `LIFECYCLE_SLOT_MAP`, `lifecycleFactories`) |
| `tool-search` piece built (filter stacks, GG-50 volume rule) | `gk-web/web/fusion-rpg-web/src/ui/gui-lego/pieces/chrome.tsx:17` (`toolSearchFactory`), `:171,181` (registration); `features/gui-lego/foldDerivedSurfaceVm.ts:307`; `ui/gui-lego/recipes/derived-console.json:23` |
| Notify rail (toast host for capture notice) | `web/fusion-rpg-web/src/stages/world/notify/NotifyRail.tsx` (mounted on the world stage; chrome order Notify → Outliner → Playback per `WorldStage.tsx:65`) |
| Turn-report + stored hot-tail detail (capture/claim lines live here) | `RpgStore.WorldTurns.cs:468,549-567,589` (via claim-endpoints §Design 5); `TurnReportKinds.CommandDropped`/`Event` (via cargo-commands §Design 4) |
| Capture hook no-op-by-construction (reachability derived live) | `RpgStore.SectorStorage.cs:171-196` (via claim-endpoints §Design 5) |
| Vault-room content: `relic-vault`, `ItemStorage`, bonus 20, `Store ↔ Vault` | `spec-storage-content.md` §Design 1–2 (consumed, not re-decided) |
| Four routes + five DTOs + reason/message contract | `spec-claim-endpoints.md` §§Design 1–5 (consumed field-for-field) |

### Wiring gap (this module closes it)

| Gap | Notes |
|---|---|
| Inspector has no vault block; block list has no storage member | `SectorInspector.tsx:73-126` block list; `blockOrder.ts:7-17` nine ids — the vault block slots into this order (recipe §Design 1), extending `BLOCK_ORDER` by one id, never reordering the nine |
| No cache pin on any map/lane layer | Zero `cache-pin`/`CachePin` hits under `web/.../src` (grep this session; `claimable` hits are sector-claimability, unrelated). `LegionMarker`/`LaneEdge`/`SectorNode` render forces and lanes — the pin renders beside them on the same layers, never as a forked overlay |
| No fold, bus binding, recipe, or draft for vault/cache/capture | Zero cargo/cache fold/bus/recipe hits under `features/gui-lego` or `ui/gui-lego` (ideal §4 wiring-gap row, still true — re-verified by the zero-hit grep this session) |
| Refusal vocabulary has no player copy | `cargo.not-present`, `cargo.wrong-faction`, `cargo.sector-full`, `cargo.over-weight`, `cargo.no-slots`, `cache.unreachable`, `cache.claimed:<c>+<s>` — backend strings with no authored sentence (ideal §4; closed key list frozen by claim-endpoints §Design 5) |
| No locked-with-unlock-line lifecycle binding | `lifecycle.tsx` ships loading/empty/error/pending only (no `phase-locked` member — grep this session). "No vault built" binds as locked-with-unlock-line per ideal §7: the binding is new, the factory follows the four existing ones, never a bespoke empty state |

## Design

### 1. Storage-panel vault block — recipe (mounts in inspector block order)

A vault block **inside the sector inspector's existing block order** (`SectorInspector.tsx:73`,
`BLOCK_ORDER` in `blockOrder.ts:7-17`), not a page, not a tab, not a route (GG-1):

```
recipe storage-panel:
  host: SectorInspector block region (one new section, data-testid inspector-block-vault)
  order: appended AFTER the slots/forces facts and BEFORE warden/dowsing —
         the plate's own logic ("what is on the ground, then what you can do about it"):
         identity → ground → next-turn → sector-loam → territory → slots → forces
           → VAULT (new) → warden → dowsing → actions
         BLOCK_ORDER gains one id ("vault"); the nine existing ids keep their relative order.
  slots:
    - vault-header: "held by X" (binds SectorStorageDto.OwnerFactionId, live per open — §Design 4)
    - capacity-meter[room]: binds SlotsUsed/SlotCapacity (row-count unit — storage-content §Design 3,
      never summed qty); paint from packs (full/left-behind), never hard-coded
    - tool-search: filter stored stacks (reuse chrome.tsx toolSearchFactory, GG-50)
    - stock-row*: one per SectorStorageRowDto in seq order (shared piece; stored state)
    - action-row: put-in (deposit-cargo) / take-out (withdraw-cargo) for the band standing there
      → cargo-commands admission shapes (§Design 3 below); no confirm for put-in/take-out
      (same-faction, reversible, GG-22 prefers undo over confirm — ideal Q2 recommendation)
    - phase-bindings: loading → phase-loading; fetch failure → phase-error with retry;
      empty vault → phase-empty with next action ("send a band with goods");
      NO vault built (SlotCapacity == 0) → locked-with-unlock-line naming relic-vault
      (GG-17; the one new lifecycle binding, following the four factories in lifecycle.tsx:18-55)
  fold: vault-fold — SectorStorageDto → header text + room fraction + row display + refusal-copy keys.
        Computes meter fractions from the DTO's four numbers; never recomputes capacity,
        never compares positions, never prettifies an id (claim-endpoints §Design 4 fold rule).
  bus: cargo-actions bus (closed: deposit/withdraw file via POST /{worldId}/commands shapes from
       cargo-commands §Design 2–3; claim-endpoints filer discipline for the dedicated claim route).
```

Put-in / take-out file `deposit-cargo` / `withdraw-cargo` orders (`EntityId` + `SectorId` + `Seq`;
admission: `entity.missing` / `sector.missing` / `cargo.seq-missing` — cargo-commands §Design 3)
and resolve at commit through the Data-side pass (never inline). The outcome returns via the turn
report (`cargo.deposited:<newSeq>` / `cargo.withdrawn:<newSeq>` or the verb refusal verbatim) plus
the `GET storage` read-back — never via the file response (file-vs-resolve separation, GG-15).

### 2. Cache-claim flow — pin → prompt → fits/left-behind → pick-up

```
flow cache-claim:
  1. pin: cache-pin marking (§Design 3) renders where GET claimable-caches lists a cache
     for the SELECTED legion. One legion's list per selection; re-read per selection
     (AsOfTurn is a staleness marker — claim-endpoints §Design 2). Movement next turn can
     strand a pin; the pin never subscribes, never caches across turns.
  2. prompt: legion-context prompt (band-2 layer over the stage, GG-1/GG-5; closes back to the
     exact map state, GG-12) reusing capacity-meter[fits?] per row (fits / doesn't-fit preview
     is fold-computed from the legion's last confirmed cargo totals — a reading, never a
     prediction promise) + stock-row* for the cache's rows + tool-search.
  3. pick-up: ONE action filing claim-cache (EntityId from path, CacheId from body, CommandId
     caller-supplied; POST .../claims filer, claim-endpoints §Design 1/3). Button copy reserves
      the AP slot: "pick up (N AP)" — N binds the claimCostMilli key once act-price-table
     creates it (world-action-economy owns the number; this flow shows nothing until it lands,
     never a local constant).
  4. answer: at commit the claim resolves per-row fit/skip in seq order; the panel folds
     cache.claimed:<c>+<s> + stored ClaimedSeqs/SkippedSeqs into per-row fits / left-behind
     states on stock-row (ideal §3 one-sentence rule: what fits is aboard, what stays waits
     where it lies) + capacity-meter refresh from the GET cargo read-back.
     Stale pin (marched away / forged id) folds cache.unreachable into the stale-pin copy.
     Double-submit replays on CommandId (Replayed: true, zero new rows — the pick-up button's
     safety).
```

What is deliberately absent: a claim-detail read serving full cache contents pre-claim
(hidden-until-found — claim-endpoints §Boundaries Ask-first; product call, not a fix); a
co-location gate display for transfer (cargo-commands §Boundaries Ask-first); any price beyond
relaying the reserved key.

### 3. Cache-pin marking contract (hidden-until-found — NO client fog logic)

- The pin binds **presence + count only** (`CachePinView`: `CacheId`, `PlaceKind ∈
  {world_sector, world_lane}`, `PlaceRef`, `ItemCount`, `AsOfTurn` — claim-endpoints
  `ClaimableCacheDto`, count-only by lock). Never contents: serving manifests on the list would
  hand every cache's contents to any viewer that asks — the fog leak hidden-until-found exists to
  prevent (claim-endpoints §Design 4).
- Render site: beside `LegionMarker` (`render/LegionMarker.tsx:49-99`) on sector nodes and beside
  `LaneEdge` (`worldViewModel.ts:155-196`) on lanes — one pin kind meaning "fallen cache", glyph
  + faction-neutral paint from packs (themeRefs, never hard-coded). No forked overlay, no second
  marker pipeline (SOLID: one marker layer family, extended by one kind).
- Fog rule, stated as a prohibition: the FE performs **zero** position compares, **zero**
  void/empty filtering, **zero** `visible: false` handling. Absent from the response = absent from
  the map. A pin that appears without a same-response listing entry is a defect; a cache hidden
  client-side that the server listed is a defect.
- Lifecycle: re-read per legion selection; `AsOfTurn` displayed nowhere (staleness marker for the
  layer, not player data). Emptied caches vanish by the server's `EXISTS` clause, never by an
  FE-side delete.

### 4. Capture-notice — held-by-X header + loser toast + report entry (event-feed dependency named)

Backend transfer is silent by construction (reachability derived live,
`RpgStore.SectorStorage.cs:171-196` — consumed). The notice is this module's real-gap build:

| Part | Contract |
|---|---|
| Vault header | Always shows "held by X" from `SectorStorageDto.OwnerFactionId` (live read per open — claim-endpoints §Design 4–5). No "previous owner" state, no history line — the header is the current fact |
| Loser toast | Band-4 toast (GG-16: silence is not an outcome) on capture, fired off the turn-report entry below — hosted in `NotifyRail` (`notify/NotifyRail.tsx`; world chrome order Notify → Outliner → Playback). Copy authored in the GG-62 catalog against the report-entry key |
| Report entry | **Event-feed dependency, named:** the commit path appends a capture entry (`TurnReportKinds.Event`, cargo-commands §Design 4 discipline — the same `report.Add(phase, Event, …)` shape the cargo pass uses) carrying the sector id + new `OwnerFactionId`. The toast and any future feed bind to this stored entry while it lives in the hot tail (`RpgStore.WorldTurns.cs:468,549-567,589`); post-trim re-derivation omits it (the replay-fidelity gap, consumed from cargo-commands §Design 5 — surfaces read stored detail while it lives, read-back DTOs after) |
| Winner view | No toast for the new holder — their vault header already says "held by" them. Toast is loser-directed only (Owner resolution: header + toast, ideal §10 Q4) |

The event feed itself (a queryable capture-event stream beyond the hot-tail report) is NOT built
here — this module supplies the header input + the report-entry vocabulary + the toast binding,
never a second feed table or a parallel notification pipeline.

### 5. Authoring order — to owner-accept drafts, NO React code

Per idea-ui-phase §1 (queue row → reuse index → recipe → fold + bus → themeRefs → HTML drafts →
owner accept → React mount + landmark tests), this module stops at **owner accept**. No `.tsx`,
no factory code, no test code ships from this spec:

1. Queue row: `menu-refactor-queue.md` gains one row per surface (storage-panel, cache-claim,
   capture-notice) — one surface per stream, per queue discipline (ideal §Hand-off).
2. Reuse index: confirm `capacity-meter[room]` density, `stock-row` left-behind state, `phase-*`
   locked binding, `tool-search` slot against the ERM/piece index — amend ERM before inventing a
   density (idea-ui §1 table).
3. Recipes: §§Design 1–2 slot trees above (vault block; claim prompt).
4. Fold + bus: vault-fold / claim-fold (fractions + reason→copy-key mapping, never capacity or
   position recomputation) + `cargo-actions` closed bus (deposit/withdraw/claim file shapes).
5. ThemeRefs: room-meter paint, stored/left-behind row paint, pin glyph, header faction tint —
   pack names only (`rarity` pack is these rows' first consumer — ideal §4; `side` pack exists).
6. HTML drafts: `docs/design/gui-lego/` drafts per recipe (landmarks match the slot trees;
   structural CSS tokens GG-29; bounded shell GG-61) — the artifact the owner accepts.
7. Owner accept, then React mount + landmark tests (implementation's job, not this spec's).

Drafts carry fiction labels only until the GG-62 copy catalog names the home file; stub draft copy
never ships as product (idea-ui §1 table).

## Tunables

**None created here.** Named so implementation knows where each lands:

| Tunable | Home | Owner |
|---|---|---|
| `CargoWeightPerUnit` (`long`), `CargoSlotsPerUnit` (`int`) | `gk-core/data/tuning/scoped-inventory.v1.json` (exist) | scoped-inventory (reused via capacities) |
| `ItemStorageCapacityBonus` = 20 for `relic-vault` | Seed corpus row (content, regenerated via generator) | `storage-content` (consumed — the room number the panel paints) |
| `claimCostMilli`, `depositCostMilli`, `withdrawCostMilli`, `loadCostMilli`, `unloadCostMilli` (per-mille) | `data/tuning/world.v{n+1}.json` `movement` — RESERVED by `cargo-commands` §Design 6, CREATED by `world-action-economy` `act-price-table` (key owner) | world-action-economy (this flow binds the display slot only) |
| Player refusal/confirmation sentences (`cargo.*`, `cache.unreachable`, per-row skip, capture transfer, "pick up (N AP)") | Authored copy catalog (GG-62); home file named at implementation | this program wave 2 (key list frozen by claim-endpoints §Design 5; sentences authored, never prettified ids) |
| Meter geometry, rarity/faction paint, shell bounds | `capacity-meter` piece contract (GG-29 tokens, GG-61 shell) + theme packs | this program (shared pieces) |

## Numeric types

Inherited from claim-endpoints §Numeric types: `Qty`, `WeightEach`, `RowWeight`, `WeightUsed`,
`WeightCapacity` are `long`, `checked`; `Seq`, slot counts, `ItemCount`, `AsOfTurn` are `int`
(structural bounds, commented as such). The folds in §§Design 1–2 compute meter fractions from
the DTO numbers — fractions are display math on confirmed totals, never a second capacity or a
level-derived magnitude (no `f(Θ)` anywhere; no power-ladder read). FE `long` figures beside
their exact decimal strings past 2^53 (`Magnitude.exact` precedent, claim-endpoints §Numeric
types). Integer overflow throws, never wraps (DESIGN-GATE §2.13).

## Commands

```powershell
npm test                # vitest — fold unit tests + recipe landmark tests once mounted
npm run build           # tsc --noEmit + vite build — type errors fail the build
python gk-core/scripts/guard-dal.py # trivially green — this module adds no SQL, no Server route, no DTO
```

## Structure

```
docs/design/gui-lego/storage-panel.html        NEW — vault-block draft (§Design 1 slot tree, landmarks)
docs/design/gui-lego/cache-claim.html          NEW — claim-prompt draft (§Design 2 slot tree, landmarks)
gk-web/web/fusion-rpg-web/src/ui/gui-lego/recipes/    EXTENDED — storage-panel + cache-claim recipes (post-accept mount)
gk-web/web/fusion-rpg-web/src/stages/world/inspector/ MODIFIED — vault section + BLOCK_ORDER + "vault" id (§Design 1);
                                                        Actions region gains deposit/withdraw verbs via the
                                                        SAME generic ActionCluster (delveDoorVerb precedent,
                                                        SectorInspector.tsx:120-122)
gk-web/web/fusion-rpg-web/src/stages/world/render/    MODIFIED — cache-pin kind beside LegionMarker/LaneEdge (§Design 3)
gk-web/web/fusion-rpg-web/src/stages/world/notify/    MODIFIED — capture toast binding off the report entry (§Design 4)
gk-web/web/fusion-rpg-web/src/contract/               EXTENDED — VaultView / CachePinView folds (fractions + copy-key
                                                        mapping; claim-endpoints FE-mirror discipline)
UNTOUCHED: WorldEndpoints.cs (no new route — four suffice); WorldCommand.cs kinds/payload
           (cargo-commands' surface — consumed field-for-field); RpgStore.* verb bodies;
           TurnEngine.cs (purity); StateHasher (overlays unhashed); SectorItemCapacity.cs;
           StructureCatalog.cs + gk-data/packs/fusion/data/seed/structures/** (storage-content owns the row);
           gk-core/data/tuning/** (no number authored here); StoragePage.tsx (developer archive console —
           ideal Built-defective row: never the vault host); RelicsLayer "storage" tab
           (empire scope — never the sector vault host); ActorSheet/ActorHub/Combat/Injector.
```

## Code style

No production code in this spec (authoring order stops at owner-accept drafts — §Design 5). The
style lock for implementation, stated now so drafts already obey it:

```
// A recipe, not a god TSX: slots bind shared pieces, the fold turns rows into display text,
// the bus files closed kinds — the recipe owns none of the three.
recipe(storage-panel) = vault-header(held-by-X) + capacity-meter[room] + tool-search
                      + stock-row* + action-row(deposit/withdraw) + phase-bindings
fold(vault-fold): SectorStorageDto → { header, roomFraction, rows[], copyKeys[] }
                  // fractions + reason→copy-key mapping; never capacity/position recomputation
bus(cargo-actions): file(deposit-cargo | withdraw-cargo | claim-cache) → report + read-back
```

## Testing strategy

- **Vault block mounts in order:** inspector renders the vault section between forces and warden
  (`data-block-order` contains `...,forces,vault,warden,...`); the nine existing ids keep relative
  order (landmark test, post-accept).
- **Room meter binds, never computes:** `SlotsUsed`/`SlotCapacity` from one `SectorStorageDto`
  paint the meter; a probe asserts the fold issues no capacity read and no position compare.
- **No-vault-built locked line:** `SlotCapacity == 0` binds locked-with-unlock-line naming
  `relic-vault`; empty vault (`SlotsUsed == 0`, capacity > 0) binds `phase-empty` with next
  action — the two never confused.
- **Pin presence == response presence:** pin renders iff the selected legion's
  `ClaimableCacheListDto` lists the cache; structural assertion that no `visible: false` member
  exists on the pin view and no position-compare helper exists in the fold.
- **Fits/left-behind fold:** a committed `cache.claimed:<c>+<s>` + stored skip lists paint per-row
  states on `stock-row`; `cache.unreachable` paints the stale-pin copy; every §Design 5 string
  byte-matches the verb's own string (refusals verbatim, authored sentences keyed, never
  prettified ids).
- **Capture header + toast:** header shows "held by X" from live `OwnerFactionId`; a capture
  report entry fires exactly one loser toast via `NotifyRail`; winner gets no toast.
- **One-scope reads:** vault opens one sector's rows, claim prompt one legion's list; a probe
  asserts no cross-legion/cross-sector fetch (Diablo-memory precedent).
- **Guardrail discipline:** no assert on vault row counts, item totals, generated
  names/descriptions, or per-cycle outcomes — assert envelope, closed-enum membership
  (`PlaceKind ∈ {world_sector, world_lane}`, six kinds, refusal vocabulary), uniqueness,
  join/closure, and structural bounds (validation-ssot).

## Boundaries

- **Always:** gates before writes (admission at file, reachability at resolve); verb reasons
  verbatim into folds; one legion / one sector per open; list = position-proven presence, never
  contents; claim result via report + read-backs, never the file response; "held by X" header on
  every vault paint.
- **Ask first:** exposing cache row contents pre-claim (weakens hidden-until-found — product
  call); a co-location gate display for transfer; any price/allowance/budget surface beyond
  binding the reserved `*CostMilli` display slot; a second `ItemStorage` row or rebalanced bonus
  (content call, `storage-content` §Boundaries); a queryable capture-event stream beyond the
  hot-tail report entry.
- **Never:** client-side fog/position/capacity logic; a weight field on any request; a bulk route;
  a direct-mutation POST; a second claim-log/cargo/vault table or a second feed table; a renamed
  refusal string; a tuning-file edit; a generated-data edit; routing players to `StoragePage` or
  the Relics "storage" tab as the vault; React code before owner-accept of drafts.

## Non-touch list

`gk-core/src/FusionRpg.Server/WorldEndpoints.cs` (four routes suffice), `gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs`
+ `WorldCommandAdmission.cs` (consumed field-for-field), `RpgStore.LegionCargo.cs`,
`RpgStore.SectorStorage.cs`, `RpgStore.CargoTransfer.cs`, `RpgStore.CacheFieldAccess.cs`,
`RpgStore.CargoFate.cs`, `RpgStore.WorldTurns.cs`, `TurnEngine.cs`, `SectorItemCapacity.cs`,
`StructureCatalog.cs`, all 25 existing `gk-data/packs/fusion/data/seed/structures/**/*.json` bytes + the `relic-vault`
generator path, `gk-core/data/tuning/**`, `web/.../features/storage/StoragePage.tsx`,
`web/.../layers/relics/RelicsLayer.tsx`, `BLOCK_ORDER`'s nine existing ids' relative order,
`lifecycle.tsx`'s four factories (extended by one binding, never edited), ActorHub/combat/Injector.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| Vault-block recipe + vault-fold + deposit/withdraw bus bindings (§Design 1) | `empire-wonder-surfaces` — reuses `capacity-meter[room]` + `stock-row` + `phase-*` by name where a wonder vault needs them; never forks them |
| Claim-fold + `CachePinView` (presence + count) + pick-up filing shape (§§Design 2–3) | `world-action-economy` — prices the filed `claim-cache` via `claimCostMilli` without touching this flow; the "(N AP)" slot is its display surface |
| Capture report-entry vocabulary + header input + toast binding (§Design 4) | Any future capture-event feed — binds the stored entry, never re-derives it post-trim |

## Success criteria

1. Vault block paints one sector's rows + room + "held by X", put-in/take-out file and answer per §§Design 1–2, each refusal byte-matching the verb's string.
2. Hidden-until-found holds on the pin: no listed position, no pin — zero client fog logic (probe-green).
3. Pick-up files once, replays on `CommandId`, answers fits/left-behind per row from the report + read-backs.
4. Capture paints header + loser toast + report entry; winner gets no toast.
5. Drafts owner-accepted before any `.tsx`; zero edits to every path in the Non-touch list (verified by diff).

## Design-gate checklist

```
[x] Subsystems: world-map sector/legion state (Core/Data verbs, consumed), Server HTTP surface
    (consumed, not extended), player-menu presentation (FE Lego). No Status/ActorHub/Combat/
    Injector subsystem touched.
[x] Read this session: spec-claim-endpoints.md (IN FULL — four routes, count-only pin DTO,
    filer idempotency, §Design 5 messaging contract, reserved *CostMilli names); spec-cargo-
    commands.md (kinds — deposit/withdraw/claim-cache filing shapes, admission, debit seam);
    spec-storage-content.md (relic-vault row, bonus 20, Store↔Vault, content-not-tuning);
    empire-inventory-surfaces-map.md (module 5 row, wave-2 deps); empire-inventory-surfaces-
    ideal.md (§5 rows 4-7, §7 vault-block + pin designs, §8 tunables, Owner resolutions:
    hidden-until-found, header+toast, AP cost); idea-ui-phase.md (authoring order, queue →
    recipe → fold+bus → themeRefs → drafts → accept → mount); DESIGN-GATE.md §1 topic index
    (world-map + player-menu rows) + §2 invariants (applied below).
[x] Code cited by file:line, opened this session in the worktree: SectorInspector.tsx (:72-126
    blocks, :37,120-122 delveDoorVerb/ActionCluster, :128 BLOCK_ORDER export);
    blockOrder.ts (:7-17 nine ids); WorldStage.tsx (:33 inspector mount, :65 chrome order,
    :171 delveDoorVerb, :222 adaptWorldLegion); worldViewModel.ts (:155-196 LaneEdge);
    render/LegionMarker.tsx (:49-99); render/SectorNode.tsx; notify/NotifyRail.tsx;
    ui/gui-lego/pieces/lifecycle.tsx (:18-55 four factories + slot map);
    ui/gui-lego/pieces/chrome.tsx (:17 toolSearchFactory, :171,181 registration);
    foldDerivedSurfaceVm.ts (:307); recipes/derived-console.json (:23).
[x] Checked decisions.md for a covering lock: scoped-inventory SSOT (one ownership root,
    move-never-copy) reused via cargo-commands/claim-endpoints; GUI Lego row (recipe + fold +
    bus, never a god TSX) followed; no "storage-cache-ui" lock exists — greenfield at the
    recipe level, constrained surface otherwise.
[x] Verified claims against CODE, not comments (all citations opened in-session in the worktree;
    zero-pin gap proven by grep over web/.../src; zero-fold gap per ideal §4 re-verified by the
    same grep; no-phase-locked proven by grep over ui/gui-lego — the locked binding is new,
    stated as such).
[x] Read the surrounding section of every rule quoted (inspector doc comment :40-58 with its
    nine-block + reserved-Actions context; GG-1/GG-5 stage-vs-page with band context; GG-15
    server-authoritative outcomes; GG-22 undo-over-confirm; GG-40 developer-tree separation for
    StoragePage; claim-endpoints §Design 2 fog rule with its absent-not-masked context).
[x] Tested (not assumed) constraints: no suite run — spec phase, no code; the no-bump and
    replay claims are staked on wave-1's named tests, cited not re-asserted.
[x] Nothing contradicts a §2 invariant: SQL only in FusionRpg.Data (no SQL here at all);
    no magnitude cap (room/slots/weight are structural, fixture-bound, refuse-with-reason);
    no f(Θ) (flat per-act costs reserved, never level-scaled); no second ownership root
    (CommanderId + entity gates, playerId recorded-not-restored per cargo-commands D2);
    no second composer; SOLID: one fold family, one closed bus, one marker layer extended
    by one kind, no forked shell/overlay/feed.
[x] No assertion pins a derived-population count, item total, generated name/description, or
    per-cycle outcome. (Counts named: 4 routes + 5 DTOs + 6 kinds + 9 inspector blocks —
    closed code-owned vocabularies with stated reasons; bonus 20 — closed content for the
    relic-vault row with a stated reason; ItemCount — a per-cache reading, never a pinned
    literal.)
[x] No event-refreshed cache introduced. (AsOfTurn is a staleness marker; pin re-reads per
    selection, never subscribes — stated in §§Design 2–3.)
[x] No acceptance criterion fixes an ordering that can vary in real play. (Vault-after-forces
    is a fixed recipe order, asserted; file→commit→report→read-back is the fixed pipeline
    sequence.)
[x] No actor combat/derived magnitude produced or consumed — actor-sheet boundary not crossed.
[x] No SOLID-violating parallel path: no second submit path, no parallel price engine, no forked
    capacity/reachability math, no second claim log/feed table, no twinned meter/row pieces;
    the economy's debit stays a stub in the one seam.
[ ] The full world-map program docs (world-map-program.md, world-map-runtime-ideal.md, the
    runtime specs) were not re-opened this session — the host facts used here (inspector order,
    marker/lane layers, stage chrome) were verified against the TSX directly. (Honest gap.)
[ ] The exact planner-source edit for the Store↔Vault pair is storage-content §Design 2's own
    open box, inherited — this spec only names the relic-vault its panel paints. (Honest gap,
    inherited.)
```
