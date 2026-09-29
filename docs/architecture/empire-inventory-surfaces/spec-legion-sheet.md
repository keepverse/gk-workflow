# Spec: `legion-sheet`

**Status: written against shipped code 2026-09-15** — every `file:line` below was opened this
session in worktree `empire-development-20260915-b7e2`. Module id `legion-sheet`, row 4 of the
[empire-inventory-surfaces map](../empire-inventory-surfaces-map.md) (wave 2, depends on
`cargo-commands` + `claim-endpoints`). Consumes
[spec-cargo-commands.md](spec-cargo-commands.md) **and**
[spec-claim-endpoints.md](spec-claim-endpoints.md) **in full, exactly as decided** — six kinds
(`load-cargo`, `unload-cargo`, `transfer-cargo`, `deposit-cargo`, `withdraw-cargo`,
`claim-cache`), Data-side post-Step pass in `CommitWorldTurn`, four REST routes with
read-back DTOs (`LegionCargoDto`, `SectorStorageDto`, `ClaimableCacheListDto`),
`correlationId := CommandId`, claim-before-decay, debit-after-refill, playerId
recorded-not-restored — re-decides none of it. Ideals:
[empire-inventory-surfaces-ideal.md](../empire-inventory-surfaces-ideal.md) §5 (legion-sheet /
cargo-fold / cargo-actions rows, shared reuse map), §7 (chosen sheet-menu direction, rejected
bare-panel shape), Owner resolutions (sheet-menu with sub-tabs, header+toast, hidden-until-found,
AP-cost lock). Procedure: [idea-ui-phase.md](../idea-ui-phase.md) §1 authoring order.
House style: `spec-legion-cargo.md` adapted for UI (Locked anchors → What already exists →
Design → Tunables → Numeric types → Commands → Structure → Code style → Testing strategy →
Boundaries → Success criteria → Interface → Design-gate checklist).

**No React code in this spec.** Authoring stops at owner-accepted drafts + contracts (§Design 9).
JSX/`tsx` implementation is the build phase's job, after this spec's contracts are accepted.

## Objective

The wave-1 backend (six command kinds + four routes + read-back DTOs) has no player path: zero
cargo/cache folds, buses, recipes, or piece bindings exist under `gk-web/web/fusion-rpg-web/src`
(verified by grep this session — the only `WorldCommand*` hit under `web/.../contract` is the
`contractGuard.ts:115` comment). This module specifies the first wave-2 surface that binds to
it: a **sheet-menu host for one selected legion** (the locked Owner direction — actor-sheet-style
menu with sub-tabs, each tab its own role) whose **cargo sub-tab** shows that legion's packs
(contents + slots/weight meters + load/unload/handoff actions) as a recipe of shared pieces
plus a pure fold plus a closed bus. It also **defines the two shared piece contracts this
program owns** (`capacity-meter`, `stock-row` — neither exists yet, verified by grep over
`docs/design/gui-lego/` this session), which the sibling `empire-wonder-surfaces` program and
the `storage-cache-ui` module consume by name.

Success looks like: selecting a war band on the world map opens its sheet over the map (never
a new route); the cargo tab shows that band's rows from `GET .../cargo` plus two honest
meters computed by the fold from the DTO's four numbers; load / unload / hand-to-another-band
file commands through `useSubmitWorldCommands` and answer visibly (band-4 toast) with the
verbs' own refusal vocabulary rendered as authored player sentences; closing the sheet returns
the exact map state (GG-12); and a wonder vault later renders `capacity-meter[room]` without
forking a twin.

## Locked anchors

- **Wave-1 decisions are consumed, not re-decided.** Six kinds, payload fields, admission arms,
  post-Step pass placement (after diff, before log insert, claims before decay),
  `correlationId := CommandId`, debit-after-refill seam, reserved `*CostMilli` key names,
  four routes + five DTOs, count-only `ClaimableCacheDto`, verbatim refusal vocabulary —
  all in `spec-cargo-commands.md` §§Design/Locked anchors and `spec-claim-endpoints.md`
  §§Design 1–5. Where this spec touches the same seam it quotes that decision; where it
  differs it is wrong.
- **Sheet-menu host, cargo as one sub-tab (Owner resolution, locked).** The ideal §7 chosen
  shape supersedes the earlier bare-`cargo-panel`-over-map shape: the legion gets a sheet-like
  menu with sub-tabs (actor-sheet-style, each tab its own role); cargo is one tab. The
  rejected alternative (floating panel) stays rejected — §Design 1 records why, not just what.
- **Shared pieces are owned here, consumed by name elsewhere.** `capacity-meter` +
  `stock-row` + `phase-*` bindings are defined once in this spec (§§Design 3–4); the sibling
  wonder program reuses `capacity-meter`/`stock-row` by name, `storage-cache-ui` reuses both
  plus the fold/bus patterns. One kit, never twins (ideal §5 reuse map; GUI Lego decision
  `decisions.md` — 'GUI Lego — menu composition (2026-09-09)').
- **Recipe + pure fold + closed bus — never a god TSX** (GUI Lego decision, `decisions.md` — 'GUI Lego — menu composition (2026-09-09)';
  idea-ui-phase §0.3). Pieces render payloads only (no fetch, no SignalR); theme packs own
  css + paint; density follows the ERM ladder — amend ERM before inventing a rung.
- **File-vs-resolve separation is visible in the surface** (GG-15, server-authoritative
  outcomes). Filing answers "filed / replayed / refused-at-submit"; resolution answers
  "moved / refused / partially-fit" via the turn report + read-backs. A surface that treats
  the filer's `Ok: true` as "claimed/loaded" confuses filing with resolving and is a defect
  (§Design 6, §Design 7 copy catalog).
- **Weight is never on the wire, capacity is never recomputed client-side.**
  `weightEach` resolves server-side at resolve time (cargo-commands §Design 4); the fold
  renders the DTO's `WeightUsed`/`WeightCapacity`/`SlotsUsed`/`SlotCapacity` as fractions
  and never re-derives them from row weights, never compares positions, never prettifies an
  id (ideal §2.7; claim-endpoints §Design 4 FE-mirror rule).
- **No pricing here; no copy invention here.** The debit seam's future spent-shape refusal is
  relayed as a reserved copy key (§Design 7); numbers belong to `world-action-economy`
  `act-price-table` + `budget-debit`. Player sentences are authored copy (GG-62) against the
  closed verbatim list — the fold maps reason strings to copy keys, never invents a new
  reason string.
- **No engine words on the player surface** (ideal §2.7). Table names, place kinds,
  disposition flags, correlation ids, claim-log vocabulary live in specs — never in tab copy.

## What already exists

### Built

| Finding | Evidence |
|---|---|
| Actor-sheet precedent: shell + vertical tab rail + per-tab roles + summarize + Esc close + collapse | `gk-web/web/fusion-rpg-web/src/ui/actor/ActorPanel.tsx:43-46,101-123` (shell, rail, fallback); `ActorSheetTabRail.tsx:29-124` (rail contract: `tabs/value/onChange/collapsed/summarize`, `role="tablist"`, `aria-orientation="vertical"`, `data-testid="actor-sheet-rail"`) |
| Legion selection state: pure reducer, `select-entity` + queue + `toRequests` wire mapping | `gk-web/web/fusion-rpg-web/src/stages/world/worldSelection.ts:48-59` (state), `:67-94` (reducer), `:106-118` (`toRequests` — the exact payload `POST /commands` expects) |
| World-stage legion select: force payload toggles `select-entity`, clears sector; outliner + UnresolvedCount reuse the same selection | `gk-web/web/fusion-rpg-web/src/stages/world/WorldStage.tsx:295-321` (`handleWorldSelect` force branch `:304-310`, outliner `:313-321`); `:235-238` (`selectedLegion` memo); `:249,252` (selection-driven effects) |
| Submit path: `useSubmitWorldCommands(worldId)` mutation over `POST /{worldId}/commands` | `gk-web/web/fusion-rpg-web/src/lib/bus/world.ts:549-554` |
| Turn-commit path + report read (resolution evidence, not filer evidence) | `world.ts:560-572` (`useCommitWorldTurn`, invalidates `["world"]` on advance); `:541-547` (`useWorldTurnReport`) |
| Sector inspector shell (the vault's future host — cited so this sheet never claims it) | `gk-web/web/fusion-rpg-web/src/stages/world/inspector/SectorInspector.tsx:60-73` (`DockShell`, `data-block-order`); `:120-122` (Actions region, one delve-door verb today) |
| `tool-search` draft (filter stacks; GG-50 volume rule) + `channel-row` nearest row precedent + `phase-*` lifecycle pieces + `scroll-region` + `surface-shell` | `docs/design/gui-lego/pieces/tool-search.html`; `channel-row.html` (identity + columns + selectable + state class); `phase-empty.html` / `phase-loading.html` / `phase-error.html` / `phase-pending.html`; `scroll-region.html`; `surface-shell.html` |
| Wave-1 wire this surface binds: four routes + five DTOs + messaging contract | spec-claim-endpoints §§Design 1–5 (routes table, `LegionCargoDto`/`CargoRowDto` counts-vs-contents discipline, `OwnerFactionId` header input, report-detail vocabulary) |
| Six kinds + admission + post-Step pass + debit seam (the fold/bus author against these, never around them) | spec-cargo-commands §§Design 1–6 |

### Wiring gap (this module closes it)

| Gap | Notes |
|---|---|
| No legion sheet-menu exists; no cargo sub-tab recipe, fold, or bus exists | Zero `cargo\|sector.?storage\|corpse.?cache\|ClaimCorpseCache` hits under `gk-web/web/fusion-rpg-web/src` (verified by grep this session, per claim-endpoints §What already exists). The kit to reuse is there (rail, reducer, mutation, drafts) — it is simply not wired to these verbs. |
| No FE mirror of any cargo/cache DTO | `contractGuard.ts:115` names `WorldCommandRequest` as a guarded shape today; `types.ts`/`adapt.ts` carry no cargo/cache view (claim-endpoints §What already exists). |
| Refusal vocabulary has no player copy anywhere in FE | Searched FE strings — none (ideal §4 wiring-gap row). Authoring is content work inside this program (GG-62), not a backend change. |
| `PendingOrder` kind union covers eight march-era kinds only | `worldSelection.ts:28-46` (`move/clear/claim/stand-fast/stance/sustain/build/ward`) — the six cargo kinds are absent. The bus (§Design 6) extends the queue shape or carries its own cargo-order shape; it never smuggles a cargo kind onto a march field. |

### Real gap (no shareable piece path exists yet — this spec defines it)

| Gap | Proof it does not exist |
|---|---|
| `capacity-meter` shared piece (slots+weight dual-gate + room density) | Zero `capacity-meter` hits under `docs/design/gui-lego/` (grep this session). `gauge-donut`/`gauge-stack` prove share/proportion, `pool-meter` proves a resource track — none renders two simultaneous gates where either can refuse. |
| `stock-row` shared piece (one carried/stored/cache stack + per-row claim states) | Zero `stock-row` hits under `docs/design/gui-lego/` (grep this session). `channel-row` is the shape precedent (not code reuse); Relics `RelicRow` is layer-local, reuse shape not code (ideal §4). |

## Design

### 1. Sheet-menu host (mirrors actor-sheet, does not fork it)

The legion sheet is a band-2 layer over the world stage (GG-1/GG-5): it opens from legion
select, over the map, and closing returns the exact map state (GG-12). No new route, no new
stage, no sibling screen.

| Contract point | Decision |
|---|---|
| Open trigger | `selectedEntityId != null` (the `worldSelection.ts:48-59` state this sheet reads; set by `WorldStage.tsx:304-310` force branch and `:313-321` outliner). The sheet never owns selection — it renders it. |
| Host shape | Mirror `ActorPanel.tsx:43-46,101-123` + `ActorSheetTabRail.tsx:29-124`: near-fullscreen shell, left vertical rail (`role="tablist"`, vertical orientation, expand/collapse, Esc close so the shell can drop its header row), per-tab bodies each with its own role. Do not fork `PanelShell`/`DockShell`; mount inside the existing shell discipline (GUI Lego decision). |
| Tabs | Closed initial set: `overview` (identity — name, faction tint, position, member count; read-only) + `cargo` (this spec's recipe, §Design 2) + future tabs by reservation only (orders, caches-nearby belong to later modules, never snuck into this recipe). Tab ids are a closed vocabulary with a stated reason (validation-ssot: pin a literal only for a closed code-owned vocabulary). |
| Tab state | Per-legion: switching legions resets to the default tab (cargo is NOT the default — `overview` is; the player asked to see the band, not its packs). Rail collapsed preference persists the same way the actor rail does (`ActorPanel.tsx:25-41` localStorage pattern, same key family, new key name). |
| Close | Esc / ✕ / selecting empty map deselects (`select-entity: null`, `WorldStage.tsx:320` precedent). Close never clears the pending queue (`worldSelection.ts:57-59` queue is turn-scoped, sheet-scoped close must not drop filed-but-uncommitted orders). |
| Lifecycle | `phase-*` bindings, not new components: sheet loading = `phase-loading`; unknown legion = `phase-error` with retry (distinct from "known legion, empty packs" which is `phase-empty` with next action — claim-endpoints §Testing strategy unknown-vs-empty rule, applied to the surface). |

### 2. Cargo sub-tab recipe

```
legion-sheet / cargo-tab =
  identity-strip
  + capacity-meter[slots+weight]          (§Design 3 — owned here)
  + tool-search                           (reuse draft, GG-50 volume rule)
  + scroll-region > stock-row*            (§Design 4 — owned here)
  + action-row (load / unload / hand-to-band)
  → cargo-fold (pure)                     (§Design 5)
  → events → cargo-actions bus (closed)   (§Design 6)
```

| Slot | Binds | Notes |
|---|---|---|
| `identity-strip` | `WorldEntityDto` (`entityId`, `displayName`, `ownerFactionId`, position, member count) | Read-only. Faction tint via `side` pack (already built); never a hard-coded color. Member count is a reading (population), never asserted as a literal. |
| `capacity-meter[slots+weight]` | `LegionCargoDto` four numbers via fold (§Design 5) | Two thin meters (ideal Q5 recommendation (a) — still OPEN, owner-decided at build; the tighter-gate-big variant stays polish-later). Refusal names the gate (§Design 7). |
| `tool-search` | Client-side filter over folded rows only | Filters displayed stacks by name; never filters by position/capacity, never hides a refused row (a refused row stays visible with its reason — XCOM lesson, ideal §6). |
| `stock-row*` | Folded `CargoRowDto` list, seq order | One row per stack aboard; one row one slot. Empty packs = `phase-empty` with next action ("load from the stash" / "march to a cache"), never a blank tab. |
| `action-row` | `cargo-actions` bus events (§Design 6) | Closed set: `load` (stash → band), `unload` (band → stash), `hand-to-band` (transfer; target picker = second band of the same empire — co-location gate is Ask-first, cargo-commands §Boundaries). Deposit/withdraw/claim do NOT live on this tab (deposit/withdraw belong to the vault block / `storage-cache-ui`; claim belongs to the cache flow) — the bus carries the kinds, the recipe exposes only this tab's three. Buttons never disable silently (GG-55): a known-unfilable action stays enabled and answers with the refusal sentence on filing, or carries its reason inline where the fold already knows it (full packs). |
| Data source | `GET /{worldId}/legions/{entityId}/cargo?asFaction=` per sheet open + per selection change + per commit advance | One legion per open (Diablo-memory precedent, ideal §6 — never the empire's inventory). `AsOfTurn` is a staleness marker: after any commit, re-read before acting (no event-refreshed cache — checklist). |

### 3. `capacity-meter` piece CONTRACT (owned here, wonder consumes by name)

New shared piece. Three densities, one contract — cargo uses `[slots+weight]`, the vault
uses `[room]`, the cache flow uses `[fits?]` (per-row fits / doesn't-fit against the same
gates). The sibling wonder program consumes this contract by name; it never forks a twin.

**Slots (structure — ERM gauge rung, GG-29 tokens only, GG-61 bounded shell):**

| Slot | Content | Notes |
|---|---|---|
| `track` | One bar per gate (`slots`, `weight`, or `room`) in a fixed box the recipe gives it | Geometry (bar vs. donut) is structural CSS in this contract; meter never sizes itself off content (idea-ui-phase §4: gauge owns a fixed box). |
| `fraction` | `used / capacity` per gate, supplied by the fold | The piece divides and paints; it never sums rows, never reads tuning, never derives capacity. |
| `gate-flag` | Which gate refuses first (`slots` \| `weight` \| `none`), supplied by the fold | Dual-gate honesty (ideal §5 bug #2): either gate can refuse; the piece shows both, flags the tighter. |
| `label` | Short numeric label per track (`3/10 slots`, `41/120 wt`) | Numbers from the fold; units abbreviated per `spec-magnitude-and-units.md` discipline. |

**Paint (theme packs own it — no hard-coded colors):** full/near-full track paint, faction
tint for headers, rarity paint for rows arrive as resolved paint values from packs (`side`
pack already built; `rarity` pack's first consumer is these rows — ideal §4 real-gap row).
A hard-coded gold-for-legendary or red-for-full inside the piece is a Lego violation, not
taste (ideal §2.4). SVG (if any) uses paint hex, never `fill="var(--token)"` alone
(idea-ui-phase §4).

**Copy (fold-supplied, never piece-authored):** the piece renders the sentence the fold
gives it for the flagged gate ("the packs are full" / "too heavy for the band to carry");
it never prettifies a reason id (ideal §2.7, GG-62).

**Densities:**

| Density | Used by | Shows |
|---|---|---|
| `[slots+weight]` | cargo tab (this spec) | Two tracks; either gate refuses. |
| `[room]` | vault block (`storage-cache-ui`) | One track: rows used vs. `SlotCapacity` from `SectorStorageDto`. |
| `[fits?]` | cache-claim flow (`storage-cache-ui`) | Per-candidate fits / doesn't-fit against the standing band's live gates; left-behind rows keep their reason. |

### 4. `stock-row` piece CONTRACT (owned here, wonder consumes by name)

New shared piece. One carried / stored / cache stack: icon, name, count, weight, per-row
state. Shape-reference (not code reuse) is Relics `RelicRow` (`RelicsLayer.tsx:51-70`);
structural precedent is `channel-row` (identity + columns + selectable + state class).

**Slots:**

| Slot | Content | Notes |
|---|---|---|
| `icon` | Item icon via catalog `hudToken`/icon, never id-slice | Locked set first (`lucide-react`); bespoke SVGs only through the kit queue (ideal §2.5). |
| `name` | Display name from the catalog join the fold performs | Never a prettified id (GG-62: authored catalog rows). Missing-name rows render `#<seq>` fallback + `phase-badge` "unknown", never a blank row. |
| `count` | `Qty` for stacks (`long`); `1` implicit for instances | Bars stay the precision path for absolute ints (idea-ui-phase §4). |
| `weight` | `RowWeight` (`long`, `checked(qty × weightEach)` or `weightEach` — claim-endpoints §Design 4) | Snapshot display; the piece never re-derives it. |
| `state` | `carried` \| `stored` \| `fits` \| `left-behind:<gate>` \| `refused:<key>` | Claim states are first-class (ideal §5 bug #7): a skipped cache row stays visible as `left-behind` with its gate; a refused action row carries its copy key. |

**Paint:** rarity paint + faction tint from packs (same packs as §Design 3). **Copy:** the
fold supplies the per-row sentence; the piece renders it verbatim.

Wonder consumes `stock-row` by name wherever a wonder vault or relic-carry display needs a
stack row — one `stock-row`, never a wonder-flavored twin.

### 5. `cargo-fold` (pure — rows → display + fractions + copy keys)

Pure function over wave-1 DTOs + stored report entries. Mirrors the `CargoView` fold named
in claim-endpoints §Design 4 (rows + used/capacity fractions; reason→copy-key mapping).

Inputs: `LegionCargoDto` (rows + four numbers) + the legion's latest stored turn-report
entries touching its `CommandId`s + `WorldEntityDto` identity fields. Outputs: meter
fractions + gate flag; folded row view-models in seq order; copy keys per refusal/skip;
action-row enablement hints (hints only — GG-55: never silent-disable).

The fold MUST NOT: recompute capacity from rows or tuning; compare positions; predict
"you can fit N more" client-side (GG-15 — outcomes are server-authoritative; the fold
shows last confirmed totals, the action's acknowledgment covers the round trip); prettify
an id; invent a reason string (closed list only, §Design 7). `long` figures cross beside
their exact decimal strings where they can exceed 2^53 (`gk-web/web/fusion-rpg-web/src/contract/types.ts:108-119`
`Magnitude.exact` precedent — claim-endpoints §Numeric types).

### 6. `cargo-actions` bus (closed — six kinds carried, three exposed here)

Closed event list. The bus carries all six cargo kinds (so `storage-cache-ui` reuses the
same bus for deposit/withdraw/claim) but this tab's recipe exposes only three actions
(§Design 2 action-row). Every event files through the existing submit path
(`useSubmitWorldCommands`, `world.ts:549-554`) or the claims filer
(`POST .../claims`, claim-endpoints §Design 1) — never a direct verb call, never inline
mutation (the two-write lock, `WorldEndpoints.cs:13-17` via claim-endpoints Locked
anchors).

| Bus event | Filed kind | Fields | Idempotency |
|---|---|---|---|
| `cargo.load` | `load-cargo` | `EntityId` + `CargoKind`/`InstanceId`/`ContainerId`/`Qty` (cargo-commands §Design 2) | `CommandId` via `orderId(turn, kind, entityId)` (`worldSelection.ts:200-202` pattern, extended — never a second key) |
| `cargo.unload` | `unload-cargo` | `EntityId` + `Seq` | same |
| `cargo.hand-to-band` | `transfer-cargo` | `EntityId` + `TargetEntityId` + `Seq` (destination ownership-checked at filing AND resolve — cargo-commands §Design 3) | same |
| `cargo.deposit` / `cargo.withdraw` | `deposit-cargo` / `withdraw-cargo` | carried for `storage-cache-ui`; not bound on this tab | same |
| `cache.pick-up` | `claim-cache` | carried for `storage-cache-ui` via the claims filer (`EntityId` path + `CacheId` body + `CommandId`); `correlationId := CommandId` end to end (claim-endpoints §Design 3) | double-POST replays at submit (`Replayed: true`), re-commit replays at resolve |

`PendingOrder`'s eight-kind union (`worldSelection.ts:28-46`) is extended (or the bus
carries its own cargo-order shape that `toRequests` maps field-for-field, `:106-118`
discipline — a field the queue carries and the wire drops is lost silently). `ward`-style
unreachable kinds are never drawn (the `worldSelection.ts:10-27` rule). No weight field on
any event (Locked anchors).

### 7. Refusal copy catalog (verbatim wire strings → copy keys → draft sentences)

The wire carries backend reason strings verbatim; player sentences are authored copy
(GG-62), owned here, keyed off this closed list. The fold maps reason → copy key; the
authored catalog (home file named at implementation — the GG-62 catalog, sibling of the
tuning files, never inside a balance-number file) carries the sentence. Draft sentences
below are **owner-accept drafts** (idea-ui-phase §1: fiction labels only until amended) —
no engine words (`typeId`, `Seq`, `correlationId`, table names) appear in any of them.

| Wire string | Producer | Copy key | Draft player sentence |
|---|---|---|---|
| `cargo.loaded:<newSeq>` / `cargo.unloaded:<seq>` / `cargo.transferred:<newSeq>` / `cargo.deposited:<newSeq>` / `cargo.withdrawn:<newSeq>` | resolve pass (cargo-commands §Design 4 detail column) | `cargo.done.*` | "Stowed." / "Unloaded." / "Handed over." / "Vaulted." / "Taken out." + header+toast capture where applicable (§Design 8) |
| `cache.claimed:<c>+<s>` + `ClaimedSeqs`/`SkippedSeqs` | claim pass (`CorpseCacheCargoClaimResult`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CacheFieldAccess.cs:31-37` via claim-endpoints §Design 5) | `cache.claimed.partial` / `cache.claimed.all` | "Picked up what fits — the rest waits where it lies." Per-row `fits` / `left-behind:<gate>` states on `stock-row` (ideal §3 one-sentence rule). |
| `cargo.over-weight` / `cargo.no-slots` | load/transfer/withdraw gates; per-row claim skips (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CacheFieldAccess.cs:326-337`) | `cargo.full.weight` / `cargo.full.slots` | "Too heavy for the band to carry." / "The packs are full." Names the gate that fired (ideal §5 bug #2; Total War lesson, ideal §6). |
| `cargo.not-owned` | load gate (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.LegionCargo.cs:282-298`) | `cargo.not-yours` | "That belongs to another band's stores." |
| `cargo.not-found` | unload/transfer/deposit/withdraw (stale `Seq`) | `cargo.gone` | "That is no longer where the band left it." |
| `cargo.not-present` | deposit/withdraw (marched-away legion) | `cargo.not-here` | "The band is no longer at that ground." |
| `cargo.wrong-faction` | deposit/withdraw (holder changed — capture) | `vault.held-by-other` | "That vault is held by <holder> now." Holder name from `SectorStorageDto.OwnerFactionId` (§Design 8). |
| `cargo.sector-full` | deposit gate (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CargoTransfer.cs:95-96`) | `vault.full` | "The vault has no room." |
| `cargo.cross-empire` | transfer gate (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.LegionCargo.cs:491,493`) | `cargo.other-empire` | "Bands of another empire cannot take this." |
| `cache.unreachable` | claim re-check (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CacheFieldAccess.cs:302-304`) | `cache.gone` | "Nothing lies within reach any more — the band has moved on, or the cache is spent." (Stale-pin copy.) |
| `entity.not-yours` / `entity.unknown` / `entity.missing` / `entity.gone` / `entity.routed` | admission / resolver drop pattern (cargo-commands §§Design 3–4) | `band.*` | "That is not your band." / "No such band." — caller-error family, distinct from empty. |
| `cache.missing` / `sector.missing` / `cargo.kind-unknown` / `cargo.ref-missing` / `cargo.seq-missing` / `cargo.target-missing` / `command.id-missing` / `kind.unknown` | submit-time admission (cargo-commands §Design 3) | `order.malformed` | Never shown as player prose — these are authoring-time errors surfaced in dev tooling; the recipe never files a shape that triggers them (bus construction guarantees fields). Listed so the fold never authors copy for them. |
| `correlation.missing` | claim verb (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CacheFieldAccess.cs:289-292`) | — | Unreachable on the command path (named, not re-checked — cargo-commands §Design 3). Listed so the fold never authors copy for it. |
| *(future)* spent-shape refusal | `DebitActCostUnlocked` seam (cargo-commands §Design 6), implemented by `world-action-economy` | `act.spent` (reserved) | Reserved key + recommended `entity.spent`-shaped vocabulary so this fold has one family to author against. No sentence finalized here; the economy program owns it. |

### 8. Capture header + toast inputs (consumed, not owned)

Capture messaging is owned by `capture-notice` (ideal §5 bug #5; the event feed is that
module's real cost). This sheet consumes exactly two inputs from claim-endpoints §Design 5
and owns neither:

1. **Header input:** `SectorStorageDto.OwnerFactionId` (live read,
   `RpgStore.SectorStorage.cs:135-147` via claim-endpoints §Design 4). Any deposit/withdraw
   refusal naming the holder (`vault.held-by-other` above) reads this field — never a cached
   faction, never a client guess.
2. **Toast/report input:** the turn-report entry vocabulary (`cache.claimed:<c>+<s>`,
   per-row skip lists, capture entry for the loser). The cargo tab surfaces claim/load
   outcomes as band-4 toasts fed by the stored hot-tail report while it lives and by the
   read-back DTOs after (claim-endpoints §Design 5 stored-vs-replay rule — never assume
   replay reproduces a claim line).

The legion sheet never renders a vault "held by X" header itself (that header lives on the
vault block in `storage-cache-ui`); it only names the holder inside a refusal sentence
where the verb already refused on faction grounds.

### 9. Authoring order to owner-accept drafts (idea-ui-phase §1, no React code)

Follow the binding order — queue row → reuse ERM/piece index → recipe → fold + bus →
themeRefs → HTML drafts → owner accept → React mount + landmark tests
(idea-ui-phase §1, lines 69–70):

1. **Queue row:** `menu-refactor-queue.md` gains one row for this surface (one surface per
   stream, per queue discipline — ideal §Hand-off). Not in this spec; named so the plan does it.
2. **Reuse ERM/piece index:** done in §What already exists (rail, reducer, mutation, drafts,
   `channel-row` shape precedent; `capacity-meter`/`stock-row` proven absent). ERM rung:
   gauge rung for `capacity-meter`, row rung for `stock-row` — amend ERM first if neither
   rung fits, never invent a private density (GUI Lego decision).
3. **Recipe:** §Design 2 slot tree (above).
4. **Fold + bus:** §§Design 5–6 contracts (above).
5. **ThemeRefs:** §§Design 3–4 paint rows (`side` pack now; `rarity` pack as first consumer).
6. **HTML drafts:** `docs/design/gui-lego/pieces/capacity-meter.html` +
   `stock-row.html` (new, owned here) + `docs/design/gui-lego/recipes/legion-sheet-cargo.html`
   (new, this tab's slot tree with landmark `data-testid`s). Drafts carry fiction-label
   discipline (idea-ui-phase §1: stub copy never ships as product).
7. **Owner accept:** drafts + this spec's contracts accepted before any `tsx`.
8. **React mount + landmark tests:** build phase (§Testing strategy), not this spec.

## Tunables

**None created, none retuned, no tuning file touched.** Names reserved-but-not-created
(owners named), inherited from the wave-1 specs:

| Tunable | Home | Owner |
|---|---|---|
| `CargoWeightPerUnit` (`long`), `CargoSlotsPerUnit` (`int`) | `gk-core/data/tuning/scoped-inventory.v1.json` (exist) | scoped-inventory (reused via `ScopedInventoryPolicy`) |
| `ItemStorageCapacityBonus` per structure row | Seed-authored structure rows | `storage-content` (module 3) |
| `claimCostMilli`, `depositCostMilli`, `withdrawCostMilli`, `loadCostMilli`, `unloadCostMilli` (per-mille) | `data/tuning/world.v{n+1}.json` `movement` — RESERVED by `cargo-commands` §Design 6, CREATED by `world-action-economy` `act-price-table` (key owner) | world-action-economy |
| Meter geometry (bar vs. donut, fixed box, breakpoints) | Structural CSS in the `capacity-meter` piece contract (§Design 3; GG-29 tokens only; GG-61 bounded shell) | this program (piece contract, not a number file) |
| Rarity paint / faction tint / full/left-behind meter paint | Theme packs (`rarity` first-consumed here; `side` already built) | this program (pack refs, §Design 3) |
| Player refusal/confirmation sentences (§Design 7) | Authored copy catalog (GG-62); home file named at implementation | this module (drafts above; owner accepts) |

## Numeric types

Inherited from cargo-commands §Numeric types via claim-endpoints §Numeric types, extended
to the fold: `Qty`, `WeightEach`, `RowWeight`, `WeightUsed`, `WeightCapacity` are `long`,
`checked` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.LegionCargo.cs:183-189,204-205`; `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CacheFieldAccess.cs:322-324`;
`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CargoTransfer.cs:170-171`). `Seq`, slot counts, `ItemCount`, `AsOfTurn` are `int` —
structural bounds, commented as such. On the FE, `long` figures cross beside their exact
decimal strings where they can exceed 2^53 (`gk-web/web/fusion-rpg-web/src/contract/types.ts:108-119` `Magnitude.exact`
precedent) — never a `number`-into-`long` parse-back. Integer overflow throws, never wraps
(DESIGN-GATE §2.13). Member counts and row counts are readings (populations), never pinned
literals.

## Commands

```powershell
cd gk-web/web/fusion-rpg-web
npm test                # vitest — fold/bus unit + landmark tests (§Testing strategy)
npm run build           # tsc --noEmit + vite build — type errors fail the build
npm run check:bundle    # entry-chunk budget; cargo tab ships route-split, never on the entry chunk
```

No C# suite is owned here (no `src/` change — Non-touch list). `guard-dal.py` is
trivially green (no SQL added); `guard-actor-hub.py` is unaffected (no actor magnitude
produced or consumed — checklist).

## Structure

```
docs/design/gui-lego/pieces/capacity-meter.html      NEW — §Design 3 draft (owned here)
docs/design/gui-lego/pieces/stock-row.html           NEW — §Design 4 draft (owned here)
docs/design/gui-lego/recipes/legion-sheet-cargo.html NEW — §Design 2 slot tree with landmarks
gk-web/web/fusion-rpg-web/src/contract/types.ts             PLANNED (build) — CargoView / VaultView /
                                                      CachePinView, additive (types.ts:11-19
                                                      extension rule — no CONTRACT_VERSION bump)
gk-web/web/fusion-rpg-web/src/contract/adapt.ts             PLANNED (build) — cargo-fold (§Design 5:
                                                      fractions + reason→copy-key, never capacity/
                                                      position recomputation)
gk-web/web/fusion-rpg-web/src/stages/world/legionSheet/     PLANNED (build) — sheet host (§Design 1) +
                                                      cargo-tab recipe (§Design 2) + cargo-actions
                                                      bus (§Design 6); landmark data-testids
gk-web/web/fusion-rpg-web/src/stages/world/legionSheet/*.test.*  PLANNED (build) — §Testing strategy
UNTOUCHED (this spec adds docs only; the build's non-touch list): TurnEngine.cs;
  RpgStore.WorldTurns.cs / LegionCargo.cs / SectorStorage.cs / CargoTransfer.cs /
  CacheFieldAccess.cs / CargoFate.cs verb bodies; WorldCommand.cs kinds/payload;
  WorldState schema/StateHasher; Intel/belief projection; decay tick;
  DiffEntities/DiffSectors; AI policies; every tuning file; gk-data/packs/fusion/data/seed/** and
  gk-data/packs/fusion/data/generated/**; ActorPanel.tsx / ActorSheetTabRail.tsx (mirrored, never modified);
  worldSelection.ts reducer shape (extended only by additive cargo-order fields);
  SectorInspector.tsx (the vault's host — storage-cache-ui's surface, never this tab's);
  RelicsLayer.tsx / StoragePage.tsx (wrong scope/tree — ideal §4 built-defective rows).
```

## Code style

No JSX in this spec by lock (§Design 9). Contracts are sketched as data shapes only:

```typescript
// cargo-fold (§Design 5): pure, closed reason vocabulary in, display model out.
// Fractions arrive as numbers; the piece divides and paints — the fold never draws.
type CargoFoldInput = {
  cargo: LegionCargoDto;            // one legion, AsOfTurn staleness marker included
  report: TurnReportEntry[];        // stored hot-tail entries touching this legion's CommandIds
  identity: { entityId: string; displayName: string; ownerFactionId: string; memberCount: number };
};
type CargoFoldOutput = {
  slots: { used: number; capacity: number };      // int, structural
  weight: { used: string; capacity: string };     // exact decimal strings beside longs
  gateFlag: "slots" | "weight" | "none";
  rows: FoldedStockRow[];                         // seq order, state includes left-behind/refused
  copyKeys: Record<string, CopyKey>;              // §Design 7 keys only — never a new string
  headerInputs: { ownerFactionId: string | null }; // §Design 8 passthrough, never cached
};

// cargo-actions (§Design 6): closed event list. Filing only — resolution is read back.
type CargoAction =
  | { type: "cargo.load"; entityId: string; cargoKind: "instance" | "stack"; instanceId?: string; containerId?: string; qty?: string }
  | { type: "cargo.unload"; entityId: string; seq: number }
  | { type: "cargo.hand-to-band"; entityId: string; targetEntityId: string; seq: number };
  // deposit / withdraw / pick-up ride the same bus shape for storage-cache-ui; not bound here.
```

## Testing strategy

- **Fold purity + closed vocabulary:** fold unit tests assert meter fractions from the four
  DTO numbers, gate-flag selection, seq-order rows, and reason→copy-key mapping over every
  §Design 7 wire string — including `correlation.missing` mapping to no-copy (named,
  never produced) and the reserved `act.spent` key existing without a finalized sentence.
- **Piece contracts by landmark:** draft-HTML landmark tests (`data-testid` per recipe slot)
  assert slot presence, fixed-box geometry, paint-hex (never bare token var), and per-row
  states (`fits` / `left-behind:<gate>` / `refused:<key>`) — structural, never pixel prose.
- **Bus files, never resolves:** bus tests assert the constructed `WorldCommandRequest`
  field-for-field (the `stance`-loss precedent, `CommandPayload` doc comment) with no
  `weightEach`-shaped member on any event (schema assertion, claim-endpoints §Testing
  strategy rule applied to the bus).
- **Unknown-vs-empty:** unknown legion → error-with-retry; known legion, empty packs →
  empty-with-next-action. Asserted separately so a test never confuses caller error with
  "nothing aboard".
- **One-scope reads:** the tab issues exactly one legion's `GET .../cargo` per open /
  selection / commit-advance; a probe asserts no empire-wide fetch (Diablo-memory
  precedent, ideal §6).
- **File-vs-resolve:** after filing, cargo rows are untouched until commit (GG-15); the
  toast answers filing, the report + read-back answer resolution.
- **No population pins:** no test asserts a member count, row count, `ItemCount`, or
  generated name/description literal — readings, not constants (validation-ssot).
- **No ordering pins beyond the fixed pipeline:** seq order (the verbs' deterministic
  tie-break) and file→commit→report→read-back are asserted; no test fixes an ordering
  that can vary in real play (checklist).

## Boundaries

- **Always:** gates before writes (admission at submit, reachability + capacity at
  resolve); verb reasons verbatim onto the wire, copy keys in the fold; one legion per
  open; list = position-proven presence via the DTO, never client fog; close returns the
  exact map state (GG-12); every outcome answers visibly (GG-16).
- **Ask first:** exposing transfer inline vs. via select-another-band (ideal §9 deferred
  handoff presentation); a co-location/adjacency gate for `transfer-cargo` display
  (cargo-commands §Boundaries); any price/allowance/budget surface beyond relaying the
  reserved `act.spent` key (world-action-economy's program); widening the tab set beyond
  `overview` + `cargo`.
- **Never:** a weight field on any bus event or request; a bulk/list-all read; a
  direct-mutation call from the surface; SQL outside `FusionRpg.Data`; client-side
  fog/position/capacity recomputation; capacity prediction ("you can fit N more");
  a renamed refusal string or a newly invented one; a second `capacity-meter`/`stock-row`
  twin in wonder or vault code; a god TSX owning fetch+layout+paint+joins+copy; engine
  vocabulary on the surface; a tuning-file or generated-data edit; React code before
  owner-accepted drafts (§Design 9).

## Success criteria

1. Sheet-menu host + cargo sub-tab recipe per §§Design 1–2, mirroring the actor-sheet
   rail discipline without forking it; close returns the exact map state.
2. `capacity-meter` + `stock-row` contracts per §§Design 3–4 defined once here and
   consumable by name (wonder + `storage-cache-ui` bind without twins).
3. Fold + bus per §§Design 5–6: fractions from the four DTO numbers, closed six-kind bus,
   three actions exposed, every refusal byte-matching the named verb string.
4. Copy catalog per §Design 7 authored against the closed verbatim list; header/toast
   inputs consumed per §Design 8 without owning the event feed.
5. Authoring order per §Design 9 followed to owner-accept drafts; zero `tsx` in this phase.
6. `npm test` + `npm run build` green for the build phase; no `src/` diff (docs + drafts
   only in this spec — verified by diff).

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `capacity-meter` contract (§Design 3: slots/paint/copy + three densities) | `empire-wonder-surfaces` (wonder vault by name) + `storage-cache-ui` (`[room]`, `[fits?]`) — reuse, never twin |
| `stock-row` contract (§Design 4: slots + claim states) | `empire-wonder-surfaces` (relic-carry display) + `storage-cache-ui` (stored / fits / left-behind rows) |
| `cargo-fold` output shape (§Design 5) + copy-key catalog (§Design 7) | `storage-cache-ui` — same fold discipline for vault/cache rows; same closed reason list for its flow's copy |
| `cargo-actions` bus (§Design 6: six kinds carried) | `storage-cache-ui` — binds `cargo.deposit` / `cargo.withdraw` / `cache.pick-up` on the same bus |
| `correlationId := CommandId` + debit-after-refill + reserved `*CostMilli` names + `act.spent` key (relayed, not re-decided) | `world-action-economy` — prices the filed kinds without touching this surface |

## Design-gate checklist

```
[x] Subsystems: world-map legion state + turn/ordering (Core/Data, consumed via wave-1 specs),
    Server HTTP surface (consumed — four routes + DTOs), player-menu presentation (FE Lego).
    No Status/ActorHub/Combat/Injector subsystem touched.
[x] Read this session: spec-cargo-commands.md (IN FULL — six kinds, post-Step pass, debit seam +
    debit-after-refill order, playerId recorded-not-restored, consumed exactly);
    spec-claim-endpoints.md (IN FULL — four routes, read-back DTOs, correlationId := CommandId,
    count-only pins, §5 messaging contract, consumed exactly);
    empire-inventory-surfaces-map.md (module 4 row); empire-inventory-surfaces-ideal.md (§5
    legion-sheet/cargo-fold/cargo-actions/shared rows, §7 sheet direction, Owner resolutions:
    sheet-menu with sub-tabs, header+toast, hidden-until-found, AP-cost lock);
    idea-ui-phase.md (authoring order §1, module unit §1, hand-off §6);
    DESIGN-GATE.md §1 UI + Player-menus rows + §2 invariants + §5 checklist;
    gui-lego-ideal.md (binding standard through §60: DPLP/stage/ERM/registries/MVVM);
    decisions.md GUI Lego row (:125) + Scoped-inventory SSOT row (:47, one ownership root).
[x] Code cited by file:line, opened this session in the worktree: ActorPanel.tsx (:43-46 shell,
    :25-41 rail-persist, :101-123 fallback/tabs); ActorSheetTabRail.tsx (:29-124 rail contract);
    worldSelection.ts (:28-59 kinds+state, :67-94 reducer, :106-118 toRequests, :200-202 orderId);
    WorldStage.tsx (:235-238 selectedLegion, :249-252 selection effects, :295-321 select branches);
    lib/bus/world.ts (:541-554 report+submit, :560-572 commit); SectorInspector.tsx (:60-73 shell,
    :120-122 Actions region); contractGuard.ts (:115); RelicsLayer.tsx (:51-70 RelicRow shape);
    tool-search.html / channel-row.html / phase-*.html / scroll-region.html / surface-shell.html
    (reuse index); WorldEndpoints.cs two-write lock + routes (via claim-endpoints citations,
    re-verified through that spec, not re-opened).
[x] Checked decisions.md for a covering lock: GUI Lego composition (recipe+fold+bus, reused);
    Scoped-inventory SSOT (one ownership root, move-never-copy, reused via wave-1 specs);
    no "legion-sheet" lock exists — greenfield at the surface level, constrained wire otherwise.
[x] Verified claims against CODE, not comments (all FE citations opened in-session in the worktree;
    capacity-meter/stock-row absence proven by grep over docs/design/gui-lego/ returning zero hits;
    FE gap proven by the zero cargo/cache-hit grep under web/src per claim-endpoints).
[x] Read the surrounding section of every rule quoted (rail contract with its Esc-close comment;
    reducer with its one-order-per-legion comment; toRequests with its stance-loss comment;
    orderId with its per-commander-per-turn comment; Actions region with its pending-roster
    context; GG rules with their band context via the ideal).
[x] Tested (not assumed) constraints: no suite run — spec phase, no code (no tsx, no C#);
    absence claims staked on named greps restated above, not asserted as measured suite runs.
[x] Nothing contradicts a §2 invariant: SQL only in FusionRpg.Data (surface adds none);
    no magnitude cap (slots/weight/room are structural, fixture-bound, refuse-with-reason);
    no f(Θ) (no level-derived number anywhere); no second ownership root (CommanderId +
    entity gates, playerId recorded-not-restored per cargo-commands D2); no second composer
    (fold consumes Hub/API output only where identity overlaps — no actor magnitude produced);
    SOLID: one recipe + one fold + one closed bus, shared pieces defined once and reused by name.
[x] No assertion pins a derived-population count, item total, generated name/description, or
    per-cycle outcome. (Counts named: 6 kinds + 4 routes + 5 DTOs + 3 exposed actions —
    closed code-owned vocabularies with stated reasons; member/row/ItemCount — readings, never
    literals; tab ids — a closed vocabulary with a stated reason.)
[x] No event-refreshed cache introduced. (AsOfTurn is a staleness marker; the tab re-reads per
    open/selection/commit-advance — stated in §Design 2.)
[x] No acceptance criterion fixes an ordering that can vary in real play. (Seq order is the verbs'
    own deterministic tie-break; file→commit→report→read-back is the fixed pipeline sequence.)
[x] No actor combat/derived magnitude produced or consumed — actor-sheet files mirrored, never
    modified; Hub-adjacent subsystems untouched.
[x] No SOLID-violating parallel path: no second sheet shell, no forked rail, no twin meter/row,
    no parallel submit path, no forked capacity/reachability math, no second claim log; the
    economy's debit stays a stub in the one seam.
[ ] gui-lego-ideal.md read only through §60 in-session (binding-standard head + principles);
    deeper sections (queue mechanics, Derived vertical slice) not needed for this surface and not
    claimed. (Honest gap.)
```

(End of file)
