# Capability map: `trade-surface`

**Status: APPROVED 2026-09-19.** Owner decisions recorded in §0. **Reconciled with the round-4 owner
decisions ([decisions-round-4.md](decisions-round-4.md)) on 2026-09-19** — see §12; where older text here
disagrees with §12, §12 and the register win. Module specs are written at
`docs/architecture/trade-network/trade-surface/spec-<module-id>.md` (all twelve, 2026-09-19); plan and task list at
`tasks/trade-surface-plan.md` (new) · `tasks/trade-surface-todo.md` (new), the prefixed pair. The bare
`tasks/plan.md` / `tasks/todo.md` pair belongs to another stream and is never a fallback.

**Umbrella:** [trade-network-ideal.md](../trade-network-ideal.md) sub-program 8, `trade-surface`
(§11 row 8: *"Trade panel, policy editor, flow lens, turn-report and notification entries, unlock and
teaching ladder, a click-budget acceptance criterion"*), plus the player-experience gaps closed in
§14b and the visibility row of §8.5.
**Session record:** `tasks/sessions/trade-network-idea-20260919.json` (its `paths` include
`docs/architecture/trade-network/**`).
**DESIGN-GATE rows read this session:** Anything a player sees (UI), Player menus, World map, Economy;
§2 invariants; §3 evidence rules; §5 checklist. Honest gaps are in the checklist at the end.

---

## 0. Owner decisions (2026-09-19, with approval)

Recorded identically in [trade-stories-map.md](trade-stories-map.md) §0. OD-1, OD-2 and OD-6 bind this
map; OD-3 to OD-5 bind trade-stories and are listed for completeness.

| # | Decision | Where it lands |
|---|---|---|
| OD-1 | **Treaties get a new "Diplomacy" rail layer, unlocked at first contact.** This needs an IA amendment (`design/information-architecture.md` §3, §4, §5 key `D`, §7) and a `decisions.md` amendment (Game GUI row, `docs/architecture/decisions.md:110`, "8 layers" → 9). **Listed as a requirement; neither edit is made by this program's specs.** Closes Q1 with option (a) | [spec-treaty-screen.md](trade-surface/spec-treaty-screen.md) *Required amendments*; [spec-trade-unlock.md](trade-surface/spec-trade-unlock.md) (first-contact fact, `Diplomacy` flag) |
| OD-2 | **A seventh "flow" lens**, as a reviewed widening of the closed lens set (`lensCatalog.ts:3-8`). Closes Q2 | [spec-flow-lens.md](trade-surface/spec-flow-lens.md) |
| OD-3 | **narrative-seed owns the list of storylet host kinds** | trade-stories `trade-hosts`, `trade-storylet-supply` |
| OD-4 | **`trade-fact-source` registers into `counterparties`' `relation-facts` projection** | trade-stories `trade-fact-source` |
| OD-5 | **Event frequency gets a per-empire budget in the one selection engine** — a request to npc-story-events `storylet-selection`, recorded as decided | trade-stories `trade-story-pacing` |
| OD-6 | **The "lanes never bind on a first world" vs "guaranteed first throttle" contradiction is resolved by naming the throttle's source in the spec** | [spec-trade-unlock.md](trade-surface/spec-trade-unlock.md) §Design 3: a production halt with bottleneck reason `no-path`, produced by first-world template placement, never by lane capacity. **Round 4 Q3 adds its answer:** a one-click "build a Counting House" |

## 1. What this sub-program is

Every surface a player uses to see and steer trade and logistics, and nothing that decides a number.
Goods flow home on their own each End Turn (Shape B, ideal §8.6); this sub-program makes that flow
**legible in one sentence**, makes the one decision a turn usually holds (**a throttle is coming —
what do you do?**) answerable in one or two clicks, and gives treaties and standing orders a place to
be set. It sits on the world stage and on two existing layers. It **reads** what `logistics-flow`,
`exchange`, `counterparties` and `fleet` compute; it never computes a flow, a price or an access level
itself.

## 2. Which loop it extends

From [the-loops.md](../../guide/the-loops.md): **Place 5 — World stage, empire building** (primary —
the sector inspector, turn cluster, lenses and HUD are that stage's surfaces), **Place 4 — World map,
adventure** (the flow lens reads lanes and routes), and **Loop B — creature summon and fusion** through
the blocked-demand read (trade's payoff to the power loop, ideal §14b). World clock only: virtual turns
and End Turn. No fourth clock.

## 3. Principles restated (binding on every module)

A module spec reads this map, not its links.

1. **RPG layer only.** Nothing here touches PvZ, the injector or the lawn. Every surface works with
   the game closed (standalone-first, DESIGN-GATE §2 invariant 9).
2. **A game is a stage with layers** (GG-1). The world map is a stage; everything trade adds is a
   block inside the existing band-2 sector inspector, a HUD element, a lens, a toast/rail entry, or a
   band-2 layer. No new route, no page to navigate to (GG-1 forbids "navigating to look at
   something").
3. **Menus are recipe + pure fold + closed bus, never a god TSX** (`decisions.md` GUI Lego row,
   `docs/architecture/decisions.md` — 'GUI Lego — menu composition (2026-09-09)'). Pieces never fetch. Theme packs own paint. **Every menu,
   band-2 body, filter/inspect panel, HUD chip, gauge, badge or glance strip in this map goes through
   `/idea-ui` before its `/spec`** ([idea-ui-phase.md](../idea-ui-phase.md) §0, §6). Those modules are
   marked **UI-gate** below.
4. **Player vocabulary only** (GG-23, GG-62). Display names are authored catalog rows under
   `gk-core/data/tuning/`, never title-cased ids. Generic strategy-genre words (owner, ideal §14b): *trade hub,
   warehouse, depot, trade route, caravan, supply line, treaty, tariff, embargo*; the shipped *legion,
   sector, clan* stay. **No franchise-specific words; "district" is never a building-slot term.**
5. **A number states its meaning** (GG-46). Every quantity renders through the one magnitude renderer
   with an explicit unit family; no renderer guesses. **A change is attributable** (GG-49): "why did I
   lose 30 ice essence?" is answerable from the surface.
6. **Complexity unlocks; teach once, in place** (GG-44, GG-45). Nothing trade adds is present on a
   player's first turn; each surface appears when its mechanic first matters, says what unlocks it
   while locked (GG-17), and explains itself the first time it is met, on the surface where it is met.
7. **Interruption is a budget** (GG-53) and **the hard-block list stays empty unless argued**
   (`world-stage-ideal.md` §4.6; `gk-web/web/fusion-rpg-web/src/stages/world/turn/blockingClasses.ts:8`).
   Trade never takes band 3 unprompted and never hard-blocks End Turn.
8. **Acknowledge instantly, never paint authority early** (GG-15). A one-click answer files a command;
   the resolved result arrives with the turn report.
9. **The surface reads, the domain decides.** Flow, loss, price, access and forecast math live in Core
   (their owning sub-programs, or a pure Core fold in this sub-program where named). The web renders
   folds. SQL only in `FusionRpg.Data`; new reads are Server projections (DESIGN-GATE §2 invariant 6).
10. **Balance numbers are data; no hard ceilings.** Any number a balance pass would tune (forecast
    horizon, teaching turn target) lives in `data/tuning/trade.v1.json` (new). Legibility thresholds
    of a pure UI visual are structural and say so in a comment, per the precedent at
    `gk-web/web/fusion-rpg-web/src/stages/world/lenses/lensCatalog.ts:92-94`. A gauge never paints a false
    `CAP` on an uncapped magnitude (GG-64).
11. **A guardrail validates the contract**, never a population count or generated text
    ([validation-ssot.md](../validation-ssot.md)). Closed vocabularies (lens ids, answer kinds, cause
    kinds) are pinned as declarations with a reason.
12. **No actor numbers.** Nothing here produces or consumes an actor combat or derived magnitude, so
    the ActorHub gate does not apply.
13. **FE stack and i18n (added by the 2026-09-20 audit — no spec here named Lingui or a locked
    library).** Chrome copy (labels, verbs, sentence frames, locked-reason frames) goes through Lingui
    macros and `npm run extract` ([tech-stack.md](../../design/tech-stack.md) §4; the web already depends
    on `@lingui/core`, `gk-web/web/fusion-rpg-web/package.json:24`). Content words — goods, causes, reasons,
    treaty kinds, building names — are catalog rows (`trade-lexicon`, structure rows) served by the host,
    never a Lingui key per id and never an id (tech-stack §4.1's two text systems). Glyphs map a catalog
    `icon` key to `lucide-react` with the GG-58 fallback; meters, gauges and sparklines are kit pieces or
    the locked libraries (`recharts`, `react-tiny-sparkline`), never hand-rolled; motion uses `motion` and
    honours reduced motion (GG-32). The flow lens draws inside the Phaser world stage (`stage-map` chunk,
    stage-lazy); no trade module imports Phaser outside it. Pieces never fetch, folds are pure, buses are
    closed. Every FE spec carries this line in its Hard edges.

## 4. Locked assumptions (correct before approving)

1. **Shape B and auto-banking by default** (ideal D2, §8.5): the steady-state turn needs no trade input.
2. **The trade center is a structure row on a buildable slot** (ideal §7.1), so the sector inspector —
   not a new screen — is its home.
3. **The six lenses are a closed set; a seventh is a reviewed change** (`lensCatalog.ts:3-8`) — decided
   by the owner (OD-2) and recorded in `flow-lens`.
4. **Notification categories are an open catalog** (notification-ssot ruling R-N2,
   [notification-ssot-map.md](../notification-ssot-map.md) §Rulings). "A closed trade entry set" in
   this map means **trade declares its own rows as a fixed, reviewed list** and guards that list; it
   does not close the catalog.
5. **World-stage owns the stage chrome** ([world-stage-map.md](../world-stage-map.md) modules
   `world-inspector`, `world-turn`, `world-notify`, `world-lenses`, `world-playback`,
   `world-numbers`). Every change to those modules is filed as an ask on world-stage, never edited
   around it.

## 5. What exists (verified against code, 2026-09-19)

### Built

| What | Evidence |
|---|---|
| Sector inspector with an ordered, append-by-order block list | `gk-web/web/fusion-rpg-web/src/stages/world/inspector/blockOrder.ts:7-22` — ten ids; the `vault` block was inserted after `forces` "never reordering the nine existing ids" (`:15-18`). Rendered in that order at `inspector/SectorInspector.tsx:108-183` |
| A per-sector forecast with one-click answers | `inspector/NextTurnBlock.tsx:24-45` — the will-release sentence plus "Keep this ground" / release-first pins that file real `stand-fast` / `cede` orders |
| Turn cluster with a nag class and an empty hard-block class | `turn/blockingClasses.ts:8` (`HARD_BLOCKING_EVENTS = []`), `:11` (`NAGGING_EVENTS`); nag state rendered at `turn/TurnCluster.tsx:86` |
| Six exclusive lenses, number-row hotkeys, colour-free encodings | `lenses/lensCatalog.ts:9-16` (closed set), `:37-108` (encodings); lens 4 is the server-cost lifelines lens (`gk-core/src/FusionRpg.Server/WorldEndpoints.cs:52`) |
| Notify rail with flush-on-End-Turn and a counted click budget | `gk-web/web/fusion-rpg-web/src/shell/notify/rail/railStore.ts:23` (`onCommit`); `gk-web/web/fusion-rpg-web/src/shell/notify/rail/clickBudget.test.tsx:50,59,75,85` (0 clicks routine, 1 click to act, 0 per-item to clear, 1 to re-route a category) |
| A legion sheet built as recipe + fold + closed bus | `legionSheet/CargoTab.tsx:13-28` (recipe comment: capacity meter, search, rows, closed `cargo-actions` bus); tabs closed to `overview` + `cargo`, "future tabs by reservation only" (`legionSheet/LegionSheet.tsx:34-35`) |
| Rail renders from state with locked reasons | `gk-web/web/fusion-rpg-web/src/shell/railState.ts:1-6`, `:38` (`lockedReason` required when locked), `:65-74` (unlock ladder) |
| Fusion cost have/need fold | `gk-web/web/fusion-rpg-web/src/features/fusion/fusionView.ts:55-76` (`haveNeed` — per-recipe shortfall per material) |
| Lane throughput and ward fields on the wire | `gk-core/src/FusionRpg.Contracts/WorldDtos.cs:292-301` (`WorldLaneDto.Width`, `HazardMilli`, `WardLevel`) |

### Wiring gap (exists, inert — not a wall)

| What | Where | Closed by |
|---|---|---|
| The lens picker iterates a compile-time constant, so a lens cannot be locked or unlocked (GG-44 forbids a navigation surface whose entries are a constant) | `lenses/LensPicker.tsx:33` maps `LENSES`; `lenses/useLensHotkeys.ts:20` registers every entry | `flow-lens` (availability from state) |
| The notify rail's items are local component state, not fed from the server | `gk-web/web/fusion-rpg-web/src/stages/world/WorldStage.tsx:142` | notification-ssot `world-notify-source` (external); `trade-notify` rides it |
| The legion sheet reserves future tabs but has none for a standing route | `legionSheet/LegionSheet.tsx:34-35` | `trade-policy-editor` (reservation filed on the owning program) |
| Fusion cost lines label materials by raw id (`essence.fire`) — **built, defective** (GG-23/GG-62) | `features/fusion/fusionView.ts:63,69` (`label: cost.shardMaterialId` / `cost.essenceMaterialId`; corrected from `:64` at spec time) | `blocked-demand` consumes a catalog display name; the fix itself is the Fusion layer's (menu-refactor-queue P4) |
| `blockOrder.ts`'s header comment says "nine blocks" while the array holds ten — **built, defective** (stale comment) | `inspector/blockOrder.ts:2` vs `:7-22` | Fixed in `trade-panel`'s change |

### Real gap

| What | Why it matters |
|---|---|
| **No trade code, DTO or endpoint anywhere** — a repo grep for `trade` in `gk-core/src/FusionRpg.Core/World` finds only prose comments; `WorldDtos.cs` has no trade field | Every module here waits on a provider sub-program's read model |
| **No logistics numbers to show** — lane flow, warehouse stock, loss causes and bottleneck reasons do not exist until `sector-yield` and `logistics-flow` land (ideal §5 Real gap) | The status line and flow lens have nothing to read |
| **No escort stance** — stances are `March`, `Scout`, `Hold`, `Dowse` only (`gk-core/src/FusionRpg.Core/World/Movement/LaneCost.cs:22`) | The "escort" throttle answer needs `fleet` first |
| **No treaty command kinds** — `WorldCommandKinds` ends at the cargo verbs (`gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:7-119`), and ideal §8.7's new-kind list has none for treaties either | The treaty screen needs `counterparties` to name them (see §10 contradiction 3) |
| **No teach-once record** — no generic "the player has been taught X" store exists (only domain ledgers such as `gk-core/src/FusionRpg.Core/Items/Surfaces/CompendiumReveal.cs:16`) | GG-45 needs a once-only fact |
| **Web paths have no verification boundary** — `gk-core/scripts/verification-boundaries.v1.json` contains no `web/` path (grep count 0), so `verify-change.py` cannot select vitest for any FE module here | An unmapped production path is a verification-boundary defect (AGENTS.md); every FE module below must add its mapping or report it |

## 6. Modules

Stable kebab-case ids, chosen once. **UI-gate** = `/idea-ui` before `/spec`.

| # | Module id | Responsibility (one line) | Depends on | UI-gate | Wave |
|---|---|---|---|---|---|
| 1 | `trade-lexicon` | Player vocabulary for trade: the runtime display catalog, the banned-term list, the playback translation rows for trade report lines | `logistics-flow`, `exchange`, `counterparties` (their closed token sets) | no | 1 |
| 2 | `trade-wire` | Server projections and FE view contract for every trade read on the world stage, fog-correct | `sector-yield`, `logistics-flow` (then `exchange`, `counterparties`, `fleet` as they land) | no | 1 |
| 3 | `trade-status` | The one-line status contract *banked N · lost M (main cause) · stuck K (worst bottleneck)*: pure Core fold + HUD strip | `trade-wire`, `trade-lexicon` | yes (HUD strip) | 2 |
| 4 | `throttle-forecast` | Next-turn throttle forecast with two or three one-click answers, in the turn cluster (nag class) and the trade panel | `trade-wire`, `logistics-flow` | yes (forecast chip) | 2 |
| 5 | `trade-panel` | The `trade` block on the sector inspector: hub (its round-4 tier), warehouse, clearing, flows out, forecast | `trade-wire`, `trade-status`, `throttle-forecast` | **yes** | 3 |
| 6 | `trade-policy-editor` | Standing trade orders: hub order policy and a caravan's route, filed as policy commands | `trade-panel`; `exchange`, `fleet`, `legion-build` command kinds | **yes** | 4 |
| 7 | `flow-lens` | A seventh, reviewed lens for per-lane flow, utilisation and bottleneck; lens availability from state | `trade-wire`, `trade-unlock` | **yes** | 3 |
| 8 | `blocked-demand` | Roster/fusion-side read: which fusions a good is blocking and whether an open hub sells it | `trade-wire`, `exchange` | **yes** | 4 |
| 9 | `trade-notify` | Trade notification rows (a fixed, reviewed set), their translator and source on the world-turn pump; trade turn-report entries | `trade-lexicon`; notification-ssot `notify-vocabulary`, `notify-format`, `notify-service` | no (rows); rail is world-stage's | 3 |
| 10 | `trade-unlock` | Unlock milestones as world-state facts, capability flags (**building-driven since round 4**: a feature unlocks when its building exists), the guaranteed first throttle, teach-once facts, and their reachability tests | `trade-wire`; `sector-yield`, `counterparties`; shared building-tier read (exchange E-A14) | yes (teaching copy placement) | 2 |
| 11 | `treaty-screen` | The Diplomacy rail layer (OD-1): access, relation band, treaties, proposals with terms, embargoes; **round 4:** proposals to empires need an Embassy, blocs and embargoes a Consulate | `trade-wire`, `trade-lexicon`, `trade-unlock`; `counterparties`, `exchange` | **yes** | 5 |
| 12 | `trade-click-budget` | Counted click-budget acceptance across the trade surfaces | every FE module above | no | 5 |

### 6.1 `trade-lexicon`

**Capability.** One authored runtime catalog, `data/tuning/trade-catalog.v1.json` (new), holding the
player display name and one-line reading for every trade token a surface shows: goods, trade structure
roles, loss causes, bottleneck reasons, throttle answers, treaty kinds and access levels. It is a
runtime catalog (tunables-ssot "Runtime catalog" class), never mixed into the `trade.v1.json` (new) number
file. It also owns the vocabulary guard for trade copy — the generic-strategy word list from ideal
§14b, a ban on "district" as a slot/building term, and a ban on franchise-specific words, with
`ip-censor` as the release gate for names (no second name filter) — and the playback translation rows
for trade report lines, filed on world-stage `world-playback`.

**Bucket.** Real gap: no trade tokens exist. The pattern is built: `lensCatalog.ts:9-16` carries
authored labels, and GG-62's catalog home is `gk-core/data/tuning/<domain>-catalog.v{n}.json`
(`game-gui-principles.md` §14, GG-62 "Home").

**Depends on.** The closed token sets published by `logistics-flow` (loss causes, bottleneck reasons),
`exchange` (goods ids, order states), `counterparties` (treaty kinds, access levels). Reads, never
defines them.
**Touches.** `data/tuning/trade-catalog.v1.json` (new) and its host loader; a web catalog reader;
`gk-web/web/fusion-rpg-web/src/stages/world/playbackTable.ts` (rows, via world-stage ask).
**Acceptance.** Every token in each provider's closed set has exactly one catalog row with a non-empty
display name (join closure, both directions: no orphan row, no uncovered token). No player-facing
trade string is derived from an id (GG-62 guard). The banned-term guard fails on "district" used as a
building-slot label and on any listed franchise term in trade copy. Every trade report line prefix has
a playback row.
**Verification boundary.** `gk-core/data/tuning/**` has no mapped boundary today (only single files such as
`materials-tuning` are mapped) — the spec adds `trade-catalog` to
`gk-core/scripts/verification-boundaries.v1.json`; web tests need the web mapping (§5 Real gap).

### 6.2 `trade-wire`

**Capability.** The Server-layer projections and the sealed FE view contract for trade on the world
stage, following world-stage's `world-contract` / `world-wire` split: `TradeSectorView` (hub level,
warehouse stock per good, fill against its own capacity axis, halt state, clearing capacity),
`LaneFlowView` (flow this turn, utilisation, bottleneck reason, loss with cause), `TradeStatusView`,
`ThrottleForecastView`, and `CounterpartyView` (access level, relation band, active treaties). Owner-only
fields follow the existing fog rule: your own warehouses are truth; foreign hubs are believed state
(ideal §8.5 "Information — plan on believed prices and lane states; settle on the truth"), rendered with
their intel age.

**Bucket.** Real gap (no DTO). Precedent built: owner-only fields such as `loamNet`
(`lenses/lensCatalog.ts:48-55` explains the owner-only zero) and the fog filter
(`gk-core/src/FusionRpg.Server/WorldEndpoints.cs:565-587`).

**Depends on.** `sector-yield` (warehouse, halt), `logistics-flow` (lane flow, loss, bottleneck,
transit), then `exchange` (quotes), `counterparties` (access, treaties), `fleet` (caravan state).
**Touches.** `gk-core/src/FusionRpg.Contracts/WorldDtos.cs`; `gk-core/src/FusionRpg.Server/WorldEndpoints.cs` (or a
sibling endpoint file); `gk-web/web/fusion-rpg-web/src/lib/bus/world.ts`; `gk-web/web/fusion-rpg-web/src/contract/adapt.ts`.
**Acceptance.** A foreign faction's warehouse stock never appears in a viewer's projection except as
believed state with an intel age; an unowned sector's trade fields serialise as "not yours" (null),
never as a zero indistinguishable from a real zero (the lens-2 lesson, `lensCatalog.ts:48-55`). Every
magnitude field declares its unit family in the contract. A fixture turn round-trips through the
adapters byte-stable.
**Verification boundary.** `server-fallback` / `contracts-fallback` (module level) plus the web mapping.

### 6.3 `trade-status` — UI-gate (HUD strip)

**Capability.** The one-sentence surface contract from ideal §14b: **banked N · lost M (main cause) ·
stuck K (worst bottleneck)**, detail one step away. A pure Core fold over the turn's logistics facts
produces `{banked, lost, lossCauses[], stuck, bottlenecks[]}` for one faction; *main cause* is the
cause with the largest share of `lost`, and *worst bottleneck* the lane or hub holding the largest
share of `stuck`, each named from the lexicon. One step away (a select on the strip) opens the
attribution (GG-49): per-cause and per-bottleneck contributions. The quiet state reads as one phrase
("all goods banked") when `lost = stuck = 0`.

**Bucket.** Real gap. The placement precedent is built: the loam summary strip in the world HUD
(`world-stage-ideal.md` §8b decision 5, `gk-web/web/fusion-rpg-web/src/stages/world/hud/TopStrip.tsx`).

**Depends on.** `trade-wire`, `trade-lexicon`.
**Touches.** A Core fold (new, under the trade namespace `logistics-flow` creates); `hud/` (world-stage
`world-hud` ask); `gk-web/web/fusion-rpg-web/src/i18n/magnitude.ts` through world-stage's `world-numbers`.
**Acceptance.** **Reconciliation:** `lost` equals the sum of its causes and `stuck` equals the sum of its
bottlenecks, for any fixture turn. **One fold:** the status line and the turn-report trade entries of
the same turn are computed from the same facts, and a test asserts their totals agree. **Determinism:**
ties for main cause and worst bottleneck break by stable id. **Units:** banked, lost and stuck render in
one declared goods unit family. If goods are value-normalised (ideal §14b, PS-5), that family is a new
member of the sealed `UnitClass` union and goes through `design/spec-magnitude-and-units.md` as a
reviewed change, never a local formatter. **Band:** the strip is band 1 and never opens band 3.
**Verification boundary.** `core-fallback` for the fold; web mapping for the strip.

### 6.4 `throttle-forecast` — UI-gate (forecast chip)

**Capability.** Answers *"most End Turns held no decision"* (ideal §14b). A pure Core forecast, the
logistics analogue of `LoamForecast` (`gk-core/src/FusionRpg.Core/World/Loam/LoamForecast.cs:9,25`), runs the
next Logistics step under the player's current orders and reports each **throttle**: a sector that
will halt at a full warehouse, a delivery that will overflow and waste, goods that a known cut will
strand, a route whose forecast loss crosses the player's alert level. Each throttle carries two or
three **answers** from a closed vocabulary (ideal §14b): `reprioritise` (route priority), `escort`
(assign an escort), `widen` (widen the bottleneck lane), `trade-away` (a sell order at the nearest hub
the player can reach), and — round 4 Q3 — `build-feature` ("build a Counting House" for a `no-path` halt;
the next Storage tier for a full warehouse; the fact → feature table is `logistics-flow` `forecast-facts`'). Answers are offered only when their command exists and is admissible, ranked
deterministically by forecast units saved. One click files the command; the forecast re-runs on the
next state read.

It surfaces in two places: the **turn cluster** as a nag-class entry (`trade.will-halt` added to
`NAGGING_EVENTS`, `turn/blockingClasses.ts:11`, a reviewed list change under `spec-world-turn.md` §2 —
never the hard-block list), and the trade panel's forecast row (the `NextTurnBlock` pattern,
`inspector/NextTurnBlock.tsx:24-45`).

**Bucket.** Real gap (no logistics step to forecast). Both placements are built patterns.
**Depends on.** `trade-wire`; `logistics-flow` (a side-effect-free way to run the Logistics step on a
copy); answer commands from `logistics-flow` (`route-set`, `widen`), `fleet` (escort), `exchange`
(`order-set`).
**Touches.** A Core forecast (trade namespace); `turn/blockingClasses.ts` and `turn/TurnCluster.tsx`
(world-stage `world-turn` ask); the trade panel.
**Acceptance.** **Faithful:** for any fixture world, every throttle the forecast names occurs when the
turn is committed with no new orders, and every halt/waste/strand that occurs was forecast (a
property test over seeded fixture worlds). **Answers work:** filing the top-ranked answer and
committing removes or reduces that throttle in the same fixture. **Never blocks:** `HARD_BLOCKING_EVENTS`
stays empty; the nag clears on a fresh turn (`TurnCluster.tsx:41-42` precedent). **At most three
answers** per throttle (a structural presentation limit, commented). **Pure:** the forecast mutates no
state and moves no hash.
**Verification boundary.** `core-fallback` + web mapping.

### 6.5 `trade-panel` — UI-gate

**Capability.** A new `trade` block on the sector inspector for a sector with a trade hub or depot:
the hub and its level, the warehouse (fill against its own capacity axis — a real cap, so the gauge may
fill against it), clearing capacity, the flows leaving this sector with their lane and bottleneck, the
sector's line of the status fold, and its forecast row with answers. A foreign hub shows believed
prices and the viewer's access level instead of stock. **Append-only discipline:** the id `trade` is
inserted into `BLOCK_ORDER` immediately after `vault` ("what is on the ground", before "what you can do
about it", the logic `blockOrder.ts:15-18` states), and no existing id moves. Composed as recipe + fold
+ closed bus; the dense entity scrolls inside the dock (GG-61).

**Bucket.** Real gap; host built (`inspector/SectorInspector.tsx:108-183`).
**Depends on.** `trade-wire`, `trade-status`, `throttle-forecast`, `trade-lexicon`.
**Touches.** `inspector/blockOrder.ts`, `inspector/SectorInspector.tsx` (world-stage `world-inspector`
ask); new piece, recipe and fold files under the GUI Lego layout; fixes the stale "nine blocks" comment
(`blockOrder.ts:2`).
**Acceptance.** The ten existing ids keep their relative order (the new order minus `trade` equals the
old order). The block renders nothing for a sector with no trade structure and the designed empty
piece while its data loads, errors or is empty (GG-17). No verb in the block is disabled without its
reason (GG-55). Opening the block never pushes band 3 (GG-63).
**Verification boundary.** Web mapping (vitest landmark tests).

### 6.6 `trade-policy-editor` — UI-gate

**Capability.** Where standing trade orders are set: automation policy, never per-turn micromanagement
(ideal §6 lesson 8). Two homes, one fold: (a) at a hub, the order policy — what this hub buys and sells,
limits, and route priority — as a sibling inspector opened from the trade block (GG-63: inspect
in-pane, no dialog for reading); (b) on a legion, the caravan's standing route — a `route` tab on the
legion sheet, which reserves future tabs (`legionSheet/LegionSheet.tsx:34-35`). Every edit files a
policy command; policy commands set policy and move nothing themselves (ideal §8.7).

**Bucket.** Real gap (no commands). Host patterns built (`legionSheet/CargoTab.tsx:13-28`).
**Depends on.** `trade-panel`; command kinds `route-set`, `route-clear` (`logistics-flow`), `order-set`
(`exchange`), `caravan-send` and the per-legion standing order (`fleet`, `legion-build`).
**Touches.** Legion sheet tab rail (reservation ask on the owning program); trade block sibling
inspector; `gk-web/web/fusion-rpg-web/src/lib/bus/world.ts` (command filers).
**Acceptance.** A filed policy round-trips: the next state read shows the policy the command set, and
the turn report states its effect (GG-15, filing ≠ resolving, the `CargoTab.tsx` note-split precedent).
Auto-banking is on by default and a new hub needs no edit to bank. No control is disabled without its
reason.
**Verification boundary.** Web mapping; command admission tests are the owning sub-program's.

### 6.7 `flow-lens` — UI-gate

**Capability.** Per-lane flow, utilisation and bottleneck reason every turn (ideal §8.5 Visibility),
as a map lens: line weight for flow, a pattern for the bottleneck reason, a glyph for loss — colour-free
by the lens encoding rule (`lensCatalog.ts:27-35`). **This is a seventh lens and therefore a reviewed
change to a closed set** (`lensCatalog.ts:3-8`: "Adding a seventh is a spec decision, not a
convenience"). The same module makes lens availability come from state, so the lens is absent from the
picker and hotkeys until trade unlocks and says what unlocks it (GG-44/GG-17) — today every lens is
unconditional (`LensPicker.tsx:33`). Auto-activates when the player selects a trade hub or a caravan
(the genre's lens auto-activation rule, `world-stage-ideal.md` §4.8).

**Bucket.** Real gap (lens); wiring gap (picker availability).
**Depends on.** `trade-wire`, `trade-unlock`.
**Touches.** `lenses/lensCatalog.ts`, `lenses/LensPicker.tsx`, `lenses/useLensHotkeys.ts`,
`lenses/lensAutoActivate.test.ts` (world-stage `world-lenses` ask); a lane channel function beside
`render/laneChannels.ts`.
**Acceptance.** The lens set is exactly seven, pinned as a declaration with its reason. Key `7` is free
(IA reserves `1`–`9` for the stage hotbar, `design/information-architecture.md` §5). A locked lens
neither renders in the picker as active nor answers its hotkey, and shows its unlock reason. The
encoding carries no colour field. A lane you cannot see renders "unknown", never zero flow.
**Verification boundary.** Web mapping.

### 6.8 `blocked-demand` — UI-gate

**Capability.** Trade's payoff to the power loop, stated where the player feels it (ideal §14b):
*"3 fusions need ice essence — an open hub sells it."* A Server projection joins the fusions the player
could otherwise perform with their material shelf (the `haveNeed` fold, `fusionView.ts:55-76`, applied
across recipes) and the hubs the player can trade at with their believed offers. The FE shows it as a
chip on the Fusion layer and as a line in the trade panel of any hub that sells a blocking good. The
economy-report reading "share of banked essence that came through trade" belongs to `trade-foundation`'s
report, not here.

**Bucket.** Wiring gap: the per-recipe shortfall exists (`fusionView.ts:55-76`) but only for the
selected recipe, labelled by raw id (`:63,69`); no cross-recipe aggregate or hub join exists.
**Depends on.** `trade-wire`, `exchange` (believed offers, access through `counterparties`).
**Touches.** A Server projection; the Fusion layer (`gk-web/web/fusion-rpg-web/src/layers/fusion/FusionLayer.tsx:11-16`
mounts the legacy `FusionPage`; menu-refactor-queue P4 is its Lego refactor, so the chip is a Lego piece
mounted by recipe, not another edit to the god page).
**Acceptance.** A fusion counts as blocked on a good only if every other cost line is met (no double
counting a fusion blocked twice). "Sells it" is true only for a hub the viewer has `market` access to
this turn. Goods are named from the lexicon, never by material id. The chip is absent, not "0", when
nothing is blocked.
**Verification boundary.** `server-fallback` + web mapping.

### 6.9 `trade-notify`

**Capability.** Trade's rows in the notification catalog and in the turn report. Trade declares a
fixed, reviewed set of categories — `trade.halt`, `trade.waste`, `trade.stranded`, `trade.caravan`,
`trade.price`, `trade.treaty`, `trade.embargo` — each defaulting to the rail; a promotion to toast or
Critical is a reviewed change in the catalog's `promotions` block (R-N2, R-N4). A web translator on
notification-ssot's `notify-format` primitives turns message keys into sentences. The source rides the
world-turn pump beside `world-notify-source` and `cache-notify-source`, reading committed trade report
lines. Trade report lines use the world's existing report shape (sector id and audience for fog,
`gk-core/src/FusionRpg.Core/World/Turn/TurnReport.cs:24-31`) with a closed `trade.` detail-prefix family, each
with a playback row (`trade-lexicon`); if npc-story-events' typed-kind row NS8 lands first, trade adopts
typed kinds instead.

**Bucket.** Real gap (no trade events). Infrastructure is external and mapped
([notification-ssot-map.md](../notification-ssot-map.md), modules `notify-vocabulary` … `notify-client`).
**Depends on.** `trade-lexicon`; notification-ssot `notify-vocabulary`, `notify-format`, `notify-service`;
report producers in `logistics-flow`, `exchange`, `counterparties`, `fleet`.
**Touches.** `data/tuning/notification-catalog.v{n}.json` (rows); a trade translator; a trade source.
**Acceptance.** Every trade category has a translator for every message key (notify-format's coverage
guard). Every draft carries a dedup key from the durable fact id (R-N5). A trade line is visible only to
its audience (the fog rule, `WorldEndpoints.cs:565-587`). Steady state — goods banked, nothing lost or
stuck — produces **no** notification. The same-turn burst goes out as one batch (R-N6).
**Verification boundary.** Per the notification-ssot modules' boundaries; `core-fallback` for the
classifier.

### 6.10 `trade-unlock` — UI-gate (teaching copy placement)

**Capability.** The unlock and teaching ladder, with every step provable. (a) **Milestones are
world-state facts:** each unlock is a pure, monotonic function of hashed world state (never of
unhashed presentation state), so a replay reaches the same unlock on the same turn. The ideal's two
milestones (§8.6): **logistics surfaces unlock at the first throttle**; **route orders and clans unlock
at first clan contact** — derivable from the faction's intel memory reaching a `Clan` sector
(`gk-core/src/FusionRpg.Core/World/Intel/FactionIntel.cs:169` sets `Watched`). The empire-development
milestone the ideal also names is undefined in specifics (`docs/architecture/empire-development-map.md:78-83`),
so it joins as an OR term when it exists. (b) **Capability flags** derived from those facts gate the
trade panel sections, the flow lens, the policy editor and the treaty screen; each locked surface says
what unlocks it (GG-17). (c) **The first throttle is guaranteed** on a first world within
`teach.firstThrottleByTurn` (a tunable in `trade.v1.json` (new)), which is a constraint filed on the world
templates and the world generator. (d) **Teach once, in place** (GG-45): the first throttle's forecast
row carries the one explanation, recorded as a save-scoped "taught" fact so it never repeats.

**Bucket.** Real gap (no milestone, no teach-once record). The rail's state-derived unlock is the built
precedent (`shell/railState.ts:65-94`).
**Depends on.** `trade-wire`; `sector-yield` (a first world can produce a throttle), `counterparties`
(clans are seeded), world-map-program (templates: `gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:15`
`first-light`).
**Touches.** A Core capability derivation; the templates (ask on world-map-program); a save-scoped
taught record (location decided at spec — the recommendation is a fact kind in npc-story-events'
`story-ledger` save scope rather than a third store).
**Acceptance.** **Reachability:** on the shipped first-world template, a scripted sequence of real
commands (no debug fabrication — live-probe standard's scope rule) reaches the first throttle by
`teach.firstThrottleByTurn` and reaches first clan contact; each unlock fact is asserted true at that
point and false before it. **Monotonic:** once true, an unlock never reverts for that faction in that
world, across any later state. **Replay:** recomputing from the command log yields the same unlock turn.
**Teach once:** the explanation renders on the first throttle and never on a later one.
**Verification boundary.** `core-fallback` + web mapping.

### 6.11 `treaty-screen` — UI-gate

**Capability.** The diplomacy surface for ideal §7.7: every known faction with its relation band (the
one four-band ladder), the derived access level `Access(grantor, requester, turn)` ∈ {closed, passage,
market, preferential} both ways, active treaties with their minimum terms and truce state, embargoes,
and **proposals**: pick a treaty kind the band allows, see its terms and tariff, file it; see an AI
answer with the refusal's terms shown and counter-offers from the fixed article list. It never computes
access or valuation; it renders `counterparties`' derived values and files its commands.

**Bucket.** Real gap. Relation data is external: npc-story-events `relation-ledger`.
**Depends on.** `trade-wire`, `trade-lexicon`; `counterparties` (treaty registry `treaty-kind.v1`,
access derivation, treaty command kinds — see contradiction 3), npc-story-events `relation-ledger`.
**Touches.** A band-2 surface and its home (owner question Q1).
**Acceptance.** Access shown equals the Core derivation for every fixture pair (no FE derivation). A
treaty kind whose lowest band is above the current band is shown locked with that reason, never hidden.
Every refusal shows its terms. Proposing is one command; the answer arrives with the turn (GG-15).
**Verification boundary.** Web mapping; derivation tests are `counterparties`'.

### 6.12 `trade-click-budget`

**Capability.** The counted acceptance the ideal asks for (§11 row 8), in the form world-notify already
proved (`gk-web/web/fusion-rpg-web/src/shell/notify/rail/clickBudget.test.tsx:50-85`). **Budget, stated:** a steady-state trade turn costs **0
clicks** beyond End Turn (auto-banking, rail flush, no promotion); **answering a forecast throttle costs
at most 2 clicks** from the stage (open the forecast chip, pick an answer), and **1** when the forecast
row is already open in the trade block; re-routing a trade notification category costs 1 (inherited).
**Bucket.** Built pattern, real gap for trade.
**Depends on.** Every FE module above.
**Touches.** Tests only.
**Acceptance.** Each budget row is a test that counts user events. A new trade surface that raises a
row's count fails the suite.
**Verification boundary.** Web mapping.

## 7. Dependency direction and build order

One way, no cycles. Provider sub-programs sit upstream; world-stage modules are edited only through
asks.

```text
logistics-flow · sector-yield · exchange · counterparties · fleet · legion-build   (external providers)
        │
   trade-lexicon ── trade-wire
        │              ├── trade-status ─┐
        │              ├── throttle-forecast ─┤
        │              ├── trade-unlock ──────┼── flow-lens
        │              │                      └── trade-panel ── trade-policy-editor
        │              ├── blocked-demand
        ├── trade-notify
        └── treaty-screen
                                   trade-click-budget (last)
```

```text
Wave 1  trade-lexicon ∥ trade-wire                  (after logistics-flow's read model exists — ideal §11: "starts after 3")
Wave 2  trade-status ∥ throttle-forecast ∥ trade-unlock
Wave 3  trade-panel ∥ flow-lens ∥ trade-notify
Wave 4  trade-policy-editor ∥ blocked-demand         (after exchange / fleet command kinds)
Wave 5  treaty-screen ∥ trade-click-budget           (after counterparties' treaty commands)
```

**Why this order.** The umbrella says trade-surface "starts after 3, grows with 4–7" (ideal §11). The
contract and vocabulary come first so every later module renders words and units it was told. The
status line, forecast and unlock are the three things that make Shape B playable, so they come before
any panel that shows detail. Editors and the treaty screen wait for the commands they file.

## 8. Cross-program asks

| Ask | Owning program / module | Blocks | Default if unanswered |
|---|---|---|---|
| Insert `trade` into `BLOCK_ORDER` after `vault`; mount the block | world-stage `world-inspector` | `trade-panel` | None — edits another program's shipped module |
| Add `trade.will-halt` to `NAGGING_EVENTS` (never hard-block) | world-stage `world-turn` (`spec-world-turn.md` §2) | `throttle-forecast` (turn-cluster placement only; the panel row ships regardless) | Forecast lives in the trade panel only |
| A seventh lens and state-driven lens availability | world-stage `world-lenses` | `flow-lens` | None — a closed-set widening is a reviewed change |
| Playback rows for the `trade.` prefix family | world-stage `world-playback` | `trade-lexicon`, `trade-notify` | None |
| Trade status strip in the HUD | world-stage `world-hud` | `trade-status` | Strip lives in the trade panel only |
| A goods unit family in `UnitClass` if goods are value-normalised | world-stage `world-numbers`, `design/spec-magnitude-and-units.md` | `trade-status` | None |
| A `route` tab reservation on the legion sheet | empire-inventory-surfaces `legion-sheet` | `trade-policy-editor` (b) | Caravan routes set from the hub side only |
| Templates guarantee a first throttle on a first world | world-map-program (templates), world generator | `trade-unlock` (c) | None — the guarantee is the acceptance |
| Read-only projections: flow, loss causes, bottleneck reasons, a side-effect-free Logistics run | `logistics-flow` | `trade-wire`, `throttle-forecast` | None |
| Treaty command kinds and the access derivation (corrected: `exchange` `treaty-lifecycle` / `trade-access`; war and peace from `counterparties` `diplomatic-stance`) | `exchange`, `counterparties` | `treaty-screen` | None |
| IA §3/§4/§5/§7 and `decisions.md:110` amendments for the Diplomacy layer (OD-1) | IA owner (`design/information-architecture.md`), `decisions.md` | `treaty-screen` | None — the layer is not built until both are amended |
| A web verification boundary in `gk-core/scripts/verification-boundaries.v1.json` | verification boundary owners (`guard-verification-boundary-tests`) | every FE module's `verify-change` run | Report the gap per AGENTS.md; never run the full suite instead |

## 9. Owner questions

**None open.** Both questions this map raised were decided with its approval (§0):

- **Q1 — Where does the treaty screen live?** Decided **OD-1**: a Diplomacy rail layer behind the
  first-contact unlock (the option (a) recommendation). The IA and `decisions.md` amendments it needs are
  requirements listed in `spec-treaty-screen.md`, not edits made by this program.
- **Q2 — Seventh lens or a widened lens 4?** Decided **OD-2**: a seventh `flow` lens, key `7`.

The question text as asked is kept below for the record.

<details><summary>Q1/Q2 as asked (2026-09-19, before approval)</summary>

**Q1 — Where does the treaty screen live?** The IA fixes nine player layers and eight rail layers
(`design/information-architecture.md` §3; `gk-web/web/fusion-rpg-web/src/shell/railState.ts:8-16`; the Game GUI
row in `docs/architecture/decisions.md:110` says "8 layers"). A treaty screen must be reachable from
every stage (GG-7). Options: **(a)** a tenth rail layer "Diplomacy" behind the first-contact unlock —
an IA and `decisions.md` amendment plus a key (`D` is unused in the verb table); **(b)** a sibling
inspector opened from any faction crest (sector inspector, turn report, notices), with no rail entry —
the notification-ssot R14 precedent, which added a Chronicle tab instead of a layer.
**Recommendation: (a).** Treaties are a standing decision the player returns to, like Pacts, and
option (b) leaves no route to the screen from a stage where no faction crest is on screen, which fails
GG-7. The amendment is small and the unlock keeps the first session clean.

**Q2 — Seventh lens or a widened lens 4?** Trade flow could fold into lens 4 ("Supply & lifelines").
**Recommendation: a seventh lens.** Lens 4 already means legion supply and lifeline hinges and carries a
server-cost gate (`WorldEndpoints.cs:52`); overloading it repeats the ES2 failure the world-stage ideal
cites (two scans converging, `world-stage-ideal.md` §4.8). The cost is one reviewed widening.

No other question here is for the owner: numbers are tunables decided by principle, and placements are
`/idea-ui` work.


</details>

## 10. Contradictions and tensions found

1. **"Closed trade entry set" vs an open catalog.** The request says trade notification entries are a
   closed set via notification-ssot; that program's ruling R-N2 makes the category catalog **open**. This
   map reconciles by declaring trade's rows a fixed, reviewed list inside the open catalog (§4 item 4,
   §6.9). No conflict remains if the owner accepts that reading.
2. **"Lanes never bind on a first world" vs "a first throttle is guaranteed on a first world."**
   **Resolved (OD-6).** The throttle's source is named in [spec-trade-unlock.md](trade-surface/spec-trade-unlock.md)
   §Design 3: a production halt with bottleneck reason `no-path`, produced by first-world template
   placement (the starting yield sector has no Supply-lens path to a bank point, closed by a `deep` lane,
   a keyed gate or ground held against the player), with a checkable template constraint that no legal
   command sequence opens the path before the forecast names the halt. Lanes stay wide enough never to
   bind in the teaching window. Filed on world-map-program templates and the generator.
3. **Treaties have no command kinds.** Ideal §7.7 describes proposals, acceptance, breaking and
   embargoes, but §8.7's new-kind list has no treaty kind. **Corrected at spec time:** the approved
   [exchange-map.md](exchange-map.md) owns treaty, embargo and bloc commands (`treaty-vocabulary`,
   `treaty-lifecycle`); `counterparties` owns only war and peace (`diplomatic-stance`). This map's original
   text said `counterparties` must add them. `treaty-screen` files against both.
4. **Relation band read inside the step.** Ideal §14b requires disposition facts that trade reads inside
   `step` to be world-hashed or logged inputs; npc-story-events' `relation-ledger` derives the band from a
   Data-side story ledger ([npc-story-events-map.md](../npc-story-events-map.md) modules 4–5). The treaty
   screen only renders the band, but `counterparties` reads it in `step`; the two programs must agree
   how the band enters the hashed step before either is specced.
   **Resolved by [counterparties-map.md](counterparties-map.md) assumption 3 / C4:** the band a turn uses is a
   logged step input (a per-pair snapshot taken at commit, replayed from the log); `treaty-screen` renders
   that snapshot.
5. **Stale comment:** `inspector/blockOrder.ts:2` says "nine blocks"; the array holds ten
   (`:7-22`). Fixed in `trade-panel`'s change.
6. **No web verification boundary** (§5 Real gap). Every FE module in this map inherits it; the fix is
   a mapping, not a broader test run.

## 10a. Spec-time corrections (2026-09-19)

Found while writing the module specs; each is carried in the named spec and summarised here so the map
stays the index.

| # | Map text | Correction | Spec |
|---|---|---|---|
| S1 | §6.9: trade report lines use a closed `trade.` detail-prefix family | No second prefix family: `logistics-flow` chose typed `TurnReportKinds` members (`lane.cut`, `logistics.loss`, …); `trade-notify` reads providers' kinds | [spec-trade-notify.md](trade-surface/spec-trade-notify.md) |
| S2 | §6.4: the `escort` answer's command is `fleet`'s | The `escort` stance is `legion-build` `escort-stance` (filed as the existing `stance` command); `fleet` `escort-link` consumes it | [spec-throttle-forecast.md](trade-surface/spec-throttle-forecast.md) |
| S3 | §6.3: the goods unit family is `trade-status`'s acceptance | The contract owner decides it: `trade-wire` files `goodsUnits` on `UnitClass`; `trade-status` consumes it | [spec-trade-wire.md](trade-surface/spec-trade-wire.md) §3 |
| S4 | §6.10: first clan contact | "First contact" (OD-1) reads contact with a treat-capable faction (`Clan` or `Rival`); the dominant enemy empire is excluded because it never treats with the player | [spec-trade-unlock.md](trade-surface/spec-trade-unlock.md) §1 |
| S5 | §6.12: answering a throttle costs ≤ 2 clicks | Applies to throttles with an admissible answer; the teaching throttle (`no-path`) carries a "show me" focus action instead | [spec-trade-click-budget.md](trade-surface/spec-trade-click-budget.md) |
| S6 | §6.2 cache | `trade-wire`'s refetch triggers include the material-shelf edge that `blocked-demand` adds | [spec-trade-wire.md](trade-surface/spec-trade-wire.md) §5 |
| S7 | §6.10: `Routes` and `Diplomacy` flags from first contact; unlocks monotonic | **Round 4:** building-driven flags (Trading Post, Market, Exchange, Caravan Yard, Treasury, Embassy, Consulate); `Routes` retired; building flags follow the buildings (not monotonic); milestones stay for teaching and the Diplomacy layer's first appearance | [spec-trade-unlock.md](trade-surface/spec-trade-unlock.md) §2 |
| S8 | S5 / §6.12: the teaching throttle has only a "show me" action | **Round 4 Q3:** it has the `build-feature` answer (Counting House); T2/T3 cover it | [spec-throttle-forecast.md](trade-surface/spec-throttle-forecast.md), [spec-trade-click-budget.md](trade-surface/spec-trade-click-budget.md) |
| S9 | §6.4: four answers | Five: `build-feature` added (reviewed widening; the id `logistics-flow` `forecast-facts` asked for), the feature taken from forecast-facts' answer table — no second table here | [spec-throttle-forecast.md](trade-surface/spec-throttle-forecast.md) §2 |
| S10 | §6.11: proposals gated by band only | Also by Embassy / Consulate / Exchange, each shown locked with its building | [spec-treaty-screen.md](trade-surface/spec-treaty-screen.md) |
| S11 | §6.2 `TradeSectorDto.HubLevel` | `HubTier` — a structure has no level; the tier is `trade-foundation` `sector-features`' slot tier | [spec-trade-wire.md](trade-surface/spec-trade-wire.md) |
| S12 | `trade-policy-editor` bus: `order.cancel` with an `orderId` to "the order-book's cancel kind" | `order-book` has neither; cancel is `order-set` at 0 keyed by hub, good and side. Round 4 adds the Treasury hold control | [spec-trade-policy-editor.md](trade-surface/spec-trade-policy-editor.md) |
| S13 | `blocked-demand` / `trade-away`: "a hub with `market` access" | `LevelAt ≥ market` at that hub (tier and the viewer's own Trading Post count); a hub blocked only by the viewer's building shows as a build hint | [spec-blocked-demand.md](trade-surface/spec-blocked-demand.md) |

**Spec index:** [trade-lexicon](trade-surface/spec-trade-lexicon.md) · [trade-wire](trade-surface/spec-trade-wire.md) ·
[trade-status](trade-surface/spec-trade-status.md) · [throttle-forecast](trade-surface/spec-throttle-forecast.md) ·
[trade-panel](trade-surface/spec-trade-panel.md) · [trade-policy-editor](trade-surface/spec-trade-policy-editor.md) ·
[flow-lens](trade-surface/spec-flow-lens.md) · [blocked-demand](trade-surface/spec-blocked-demand.md) ·
[trade-notify](trade-surface/spec-trade-notify.md) · [trade-unlock](trade-surface/spec-trade-unlock.md) ·
[treaty-screen](trade-surface/spec-treaty-screen.md) · [trade-click-budget](trade-surface/spec-trade-click-budget.md).
UI-gate specs carry a *Layout pending `/idea-ui`* section; their layout is not decided.

## 11. DESIGN-GATE §5 checklist

```
[x] Subsystems identified: world stage (inspector, turn cluster, lenses, HUD, playback), notification
    SSOT, GUI Lego menus, fusion layer, IA/rail, world turn engine (read only), economy (read only).
[x] Session boundary: tasks/sessions/trade-network-idea-20260919.json lists docs/architecture/
    trade-network/** in its paths. I did not run session-boundary-check.py in this sub-task (docs
    only, a new file); the record's own notes carry the last run's crossings.
[~] §1 rows read this session: UI row — game-gui-principles.md (GG-1…GG-10, GG-23…GG-30, GG-43…GG-53,
    GG-61…GG-64), design/information-architecture.md §1, §3–§7; Player menus row — gui-lego-ideal.md,
    idea-ui-phase.md, gui-lego/menu-refactor-queue.md; World map row via world-stage-ideal.md §0,
    §4.4–§4.11, §8 and world-stage-map.md modules; Economy row via trade-network-ideal.md in full.
    NOT read this session: design/README.md, fe-game-foundation.md, gui-lego-authoring.md,
    gui-lego-map.md, design/gui-lego/README.md, the world-map runtime specs, empire-resource-ssot.md,
    empire-economy-ssot.md, economy-principles.md. Each module spec reads its row in full first.
[x] decisions.md checked: Game GUI (:110, "8 layers" — Q1), GUI Lego (:132), Empire resource
    registry (:108). This map locks nothing; Q1 would amend :110.
[x] Every factual claim cites file:line (verified by reading the lines this session).
[x] audit-doc-citations.py --scope run on this file; HIGH findings fixed (see the run with this change).
[x] Claims verified against code, not comments (BLOCK_ORDER contents vs its comment; LENSES vs picker;
    stances; command kinds; web boundary absence by grep).
[x] Surrounding sections read for quoted rules (lens closed-set comment, blocking classes, block-order
    append note, notification R-N2).
[x] No constraint reported as "moves goldens" or "needs sign-off" without a test; the forecast is
    specified as pure so it moves no hash — a property the spec tests, not a claim.
[x] No §2 invariant contradicted.
[x] Corrections propagated: none made to other files (outside this sub-task's fence); each is listed
    in §10 with its owner.
[x] No assertion pins a population. Pinned literals are declarations: seven lenses, the answer
    vocabulary, at most three answers per throttle, trade's category rows — each with its reason.
[x] Event-refreshed cache: the forecast and status are recomputed per state read, not cached. If a
    spec adds a client cache, it lists every trigger, including the unlock edge (key set changes when
    trade unlocks) and the turn-advance edge.
[x] Ordering: the forecast-faithfulness criterion is order-independent (any order of filed answers);
    unlock reachability is asserted at a turn bound, not a sequence.
[x] Actor numbers: none produced or consumed.
[x] No SOLID-violating parallel path: one inspector, one lens system, one notification pipeline,
    one magnitude renderer, one relation ladder; the surface reads provider folds and never recomputes.
[ ] New rule registry rows: the trade vocabulary guard, the no-hard-block rule for trade and the
    append-only BLOCK_ORDER rule need rows in gk-core/scripts/enforcement-registry.v1.json at spec time.
```


---

## 12. Reconciliation 2026-09-19 (round 4)

Applies [decisions-round-4.md](decisions-round-4.md) (binding). Verified against code this session: a
`build` needs a legion standing in the sector and pays from its carried loam
(`gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs:110`,
`gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:47`, `:134`), so a one-click "build a Counting House"
is real only when a legion is there (otherwise one click sends it); the `build` kind exists
(`gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:34`); the `Market` slot's display name is "Market"
(`gk-core/src/FusionRpg.Core/World/SlotTypeCatalog.cs:74`).

### 12.1 What round 4 changed here

| Decision | Where it landed |
|---|---|
| Q3 — the first-throttle answer is "build a Counting House" | `throttle-forecast` (fifth answer `build-feature`, fed by `forecast-facts`' answer table); `trade-unlock` §3 (answer + two template clauses); `trade-click-budget` (teaching throttle joins T2/T3) |
| B — the unlock ladder is building-driven | `trade-unlock` §2 (tier flags from `sector-features` `FactionTier`; `Routes` retired; building flags follow the buildings); `trade-wire` (tiers in `Capabilities`, `HubTier`, `MissingBuildingId`); `trade-panel` (tier and next-tier line); `trade-policy-editor` (building reasons; hold control) |
| B — the treaty screen needs an Embassy (Consulate for blocs and embargo) | `treaty-screen` (locks with the building named; the layer itself still appears at first contact, OD-1) |
| B — access = building tier AND treaty/band | `blocked-demand`, `throttle-forecast` `trade-away` (read `LevelAt`) |
| Q2 — Treasury per-good hold | `trade-policy-editor` `hold.set`; `trade-unlock` `BankingTier ≥ 2` |
| Q4 — never-peace is player-only | `treaty-screen` (no proposable treaty toward the player only) |

### 12.2 Asks aimed at this map

| Ask | From | Status |
|---|---|---|
| A7 (the escort answer depends on `legion-build`'s stance and `fleet`'s `escort-link`) | `fleet-map.md` | Already answered (S2) |
| `build-feature` answer in the closed answer vocabulary | `logistics-flow` `forecast-facts` §2 | Answered: `throttle-forecast` §2 (S9) |
| A6 (consume `logistics-facts`' token sets and `forecast-facts`' dry run) | `logistics-flow-map.md` | Already answered (`trade-lexicon`, `throttle-forecast` anchors) |
| E-A9's replacement (reachability of the first clan market) | `exchange-map.md` | Answered: `trade-unlock` Acceptance 1 (build a Trading Post, fill a clan order) |

### 12.3 Cross-cluster conflicts (outside this fence — not edited)

| # | Conflict | Recommended resolution |
|---|---|---|
| X-S1 | World templates must satisfy two new first-throttle clauses: a free slot a Counting House row allows in the throttle sector, and a starting legion able to reach it with the loam | Filed on world-map-program templates and the generator's first-world constraint table, beside OD-6's constraint |
| X-S2 | The Counting House row's slot kind and loam cost are `empire-seed` / `sector-yield` content; the one-click answer is only admissible if the row can be built on a slot the template gives | `sector-yield` `bank-points` names the row's required slot kind; the template check reads it |
| X-S3 | The IA and `decisions.md:110` amendments for the Diplomacy layer (OD-1) are unchanged, but the layer's §7 unlock ladder row should now say "first contact; treaties with empires need an Embassy" | IA owner, with OD-1's amendment |
| X-S4 | The shared building-tier read had no owner (`exchange-map.md` X-1) | **Resolved during this reconciliation:** `trade-foundation` `sector-features` ([spec](trade-foundation/spec-sector-features.md)); every building flag here reads `FactionTier` |

### 12.4 Closed-vocabulary widenings

Throttle answers 4 → 5 (`build-feature`); capability flags: `Routes` retired, five tier fields added (a reviewed
change to the `TradeCapabilities` record); lexicon families 9 → 10 (`buildingTiers`), then 10 → 9 when the 2026-09-20 audit withdrew `reportPrefixes` (sentence frames are Lingui chrome); policy-editor bus
6 → 7 (`hold.set`). No lens, nag or block-order change.

### 12.5 Gap check

- Every module has a spec (12 of 12).
- Dependencies resolve (the building-tier read is `trade-foundation` `sector-features`).
- Tuning keys: no new key; `teach.firstThrottleByTurn` and `forecast.lossAlertMilli` stay single-owner.

### 12.6 Owner questions

None new for this map. ~~The word collisions the building ladders create on player surfaces ("Market",
"Exchange", "Vault") are asked once, as `exchange-map.md` OQ-2, because the names are the buildings'.~~
(Superseded: decided by round 5 C4 — see §13.)

### 12.7 Citation audit

`python scripts/audit-doc-citations.py --scope` was run on this map and every edited spec under
`trade-surface/` after these edits: no HIGH finding.

## 13. Round 5 (2026-09-20)

Applies [decisions-round-4.md](decisions-round-4.md) *Round 5* (R5-A, R5-X; binding). Re-verified this
session: the `market` and `vault` slot types are displayed "Market" and "Vault"
(`gk-core/src/FusionRpg.Core/World/SlotTypeCatalog.cs:74`, `:72`); a row names one required slot kind
(`gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:54`).

| Ruling | Where it landed |
|---|---|
| **A1** — every seat starts with a tier-1 Counting House and Storehouse | `trade-unlock` §2 (Banking/Storage tier 1 from turn 0), §3 (the throttle sector is never the seat) |
| **A4** — hold default = other traders' open buy orders at the hub | `trade-policy-editor` `hold.set` default copy |
| **B1** — Trading Post on Wildland or Market | `trade-unlock` `TradeTier ≥ 1` row |
| **B3** — caravans unload at a foreign hub only with the hub owner's yard | `trade-policy-editor` §2 reason (reads `fleet` `depot` `ForeignSite.Of`, `depot.no-foreign-yard`) |
| **B4** — the trader's best Trade tier anywhere counts at a clan hub | `trade-unlock` `TradeTier ≥ 1` row |
| **C2** — only the offering side needs an Embassy | `treaty-screen` (lock is the viewer's own building only) |
| **C3** — a deliberate embargo needs a Consulate; war embargoes automatic | `treaty-screen` (acceptance 2) |
| **C4** — slot display names renamed, building names and ids stay | `trade-lexicon` §4a ("Market Square", "Vault Site"), guard acceptance 3a |
| **X1** — gates read `sector-features` | Already true (`trade-unlock` §2 reads `FactionTier`) |

**Asks filed by round 5:**

| # | To | Ask |
|---|---|---|
| S-R5-1 | world-map program (`SlotTypeCatalog`) | Change the `Name` of slot types `market` → "Market Square" and `vault` → "Vault Site" (`SlotTypeCatalog.cs:74`, `:72`); ids and `SlotKind` members unchanged; `Name` is not hashed |
| S-R5-2 | `empire-seed` `world-exemplars` | The tone brief carries the rule "a building never takes a slot's display name" (done in that spec's round-5 edit) |

**Not applicable here:** A2, A3, B2, C1, D1, X2–X16 except as noted (no trade-surface interface changes).
No new contradiction; no owner question.

Citation audit: `python scripts/audit-doc-citations.py --scope` run on this map and every edited
`trade-surface/` spec after these edits.

## Audit 2026-09-20

Independent audit of this map and its twelve specs against DESIGN-GATE §2/§3/§5 and the UI / Player
menus rows, PRINCIPLES §9, game-gui-principles (GG-1, GG-17, GG-23, GG-38, GG-44–GG-46, GG-53, GG-55,
GG-62, GG-64), gui-lego-ideal, tech-stack (buy before build, §4 i18n, §6 chunks), validation-ssot and
testing-standard. Re-verified this session: `gk-core/scripts/verification-boundaries.v1.json` still has no
`web/` path (grep count 0); the Game GUI row still says 8 layers (`docs/architecture/decisions.md:110`)
and `design/information-architecture.md` has no Diplomacy layer, while `decisions.md` — 'Treaties, Diplomacy rail layer, flow lens (2026-09-19)' records the
Diplomacy layer and flow-lens decisions. Baseline `audit-doc-citations.py --scope` on this map and
`trade-surface/`: 0 HIGH before the edits.

### Findings

| # | Sev | Finding (evidence) | Status |
|---|---|---|---|
| S-A1 | HIGH | **`trade-away` could not relieve a throttle.** It filed a lone sell order, but exchange payment is barter at one hub (a sell with no buy there delivers nothing, `exchange/spec-settlement-payment.md` §2), a sell is capped by pass-start consignment at that hub (`exchange/spec-order-book.md` §Design 6), and no order may sit at one's own hub (`order.own-hub`). Its own "answers work" criterion would fail | **Fixed:** `throttle-forecast` §2 — `trade-away` is a command list (route the good into a foreign hub's consignment + a paired sell and buy); `ThrottleAnswer.Commands` |
| S-A2 | HIGH | **The treaty screen could not answer an AI offer or run a bloc.** Its closed bus had propose / accept-counter / end / embargo / war / peace only, while `ai-treaty-policy` proposes to the player and `treaty-lifecycle` defines bloc verbs — a dead end the player cannot act on | **Fixed:** `diplomacy.respond` and the three bloc events; criterion 8 joins the bus to the command lists |
| S-A3 | MED | **Headline totals summed unlike goods.** `trade-status` added essence units to substrate units as one "banked N" | **Fixed:** headline totals in value-index units through `goods-valuation`; lines keep `goodsUnits` |
| S-A4 | MED | **No FE spec named Lingui, lucide or the locked chart libraries**, and `trade-lexicon` stored Lingui message ids inside a data catalog, mixing tech-stack §4.1's two text systems | **Fixed:** principle 13 above, one line in every FE spec's Hard edges; `reportPrefixes` withdrawn; flow lens states it stays in the stage-lazy Phaser chunk |
| S-A5 | MED | **Forecast faithfulness asserted an impossibility.** "Every throttle that occurs was shown" ignores AI orders and the new band snapshot committed in the same turn | **Fixed:** stated under "no new orders from any faction and the same logged inputs" |
| S-A6 | MED | **Dedup key collisions in `trade-notify`.** `sectorOrLaneId` is empty for treaty, embargo and caravan lines, so two in one turn shared a key and the second was dropped (R-N5) | **Fixed:** key carries the line's subject id |
| S-A7 | MED | **A hashed milestone read a post-commit computation.** `trade-unlock`'s `first-throttle` could flip from a "post-commit forecast" — unhashed input to hashed state (P13) | **Fixed:** the dry run is taken inside the step |
| S-A8 | LOW | `trade-unlock` criterion 2 required a search over *every* legal command sequence (exponential) | **Fixed:** a sound relaxed reachability bound |
| S-A9 | LOW | Stale "counterparties Q1 recommendation" (decided by round 4 Q4) in `treaty-screen` and `trade-unlock`; a contradictory "(either side's)" lock rule in `treaty-screen`; a franchise game name in §6.7 | **Fixed** |

**Checked and sound (no change):** menus are recipe + pure fold + closed bus in every FE spec; pieces never
fetch; GG-1 (every surface is a block, lens, rail entry or band-2 layer — no route); GG-23/GG-62 (authored
catalog rows, a designed unknown placeholder, a vocabulary guard); UI-gate modules defer layout to
`/idea-ui` with a *Layout pending* section; GG-64 gauge honesty; null-is-not-zero fog rules; the
`trade-wire` refetch trigger set enumerates the key-set edges (unlock, shelf) with one test each
(DESIGN-GATE §2.16); closed vocabularies pinned with reasons; no population pinned.

### Violations this map cannot fix (other owners)

| # | Owner | Violation | Fix |
|---|---|---|---|
| S-X1 | verification-boundary owners (`guard-verification-boundary-tests`) | No `web/` path in `gk-core/scripts/verification-boundaries.v1.json`, so `verify-change.py` cannot select vitest for any module here (an unmapped production path is a boundary defect, AGENTS.md) | Add a `web-world-trade` boundary row mapping `web/fusion-rpg-web/src/features/trade/**` and the touched `stages/world/**` files to their vitest files; until then each FE task reports the gap and runs its own vitest files by path, never the full suite |
| S-X2 | IA owner and `decisions.md` (Game GUI row) | OD-1's Diplomacy layer is recorded (`decisions.md` — 'Treaties, Diplomacy rail layer, flow lens (2026-09-19)') but the Game GUI row (`:110`, "8 layers") and `design/information-architecture.md` §3/§4/§5/§7 are unamended | Amend both before `treaty-screen` is built (already its listed requirement) |
| S-X3 | `design/spec-magnitude-and-units.md` / world-stage `world-numbers` | Two unit classes are now needed: `goodsUnits` (per-good quantities) and a value unit for the headline totals | One reviewed widening covering both (`trade-wire` §3 files it) |

### Owner questions

None. S-A3 applies the one-valuation rule; the rest are corrections.

---

## 14. Round 6 (2026-09-20)

Applies [decisions-round-4.md](decisions-round-4.md) *Round 6* (binding) and the global-audit items this
cluster owed. Where this section disagrees with anything above, it wins; each change is in the named spec.

| Ruling / finding | Change in this cluster | Where |
|---|---|---|
| **C1** — one capability flag and one ruleset bump **per wave** | The word *capability flag* means two different things and this cluster now says so: the **stamp's** rows (`trade.logistics`, `trade.exchange`, …) are what a world's *rules* grant — one row and one `RulesetVersion` bump per landing wave, owned by the module that lands the wave — while `trade-unlock`'s flags are a **pure derivation over present state** for the surface. This cluster registers **no** stamp row and takes **no** bump. Where they meet: `For()` reads the stamp first and returns every building tier as 0 on a world whose stamp lacks the feature's wave, so the rail never offers a control admission must refuse (the TC6 shape) | [trade-surface/spec-trade-unlock.md](trade-surface/spec-trade-unlock.md) §2; [landing-order.md](landing-order.md) |
| **C2** — one neutral `StructureKind.Feature`; `StructureKind.Exchange` withdrawn | Every building flag in `trade-unlock` §2 would have read **0 for ever** before C2: the feature rows were emitted `structureKind: none`, which never loads (global audit C2). C2 makes the whole building-driven flag section real, and this cluster's landing follows the wave that lands `sector-features` and the member. `trade-lexicon`'s "Exchange" collision note is also settled at the source — no code name shares the building's word any more | spec-trade-unlock §2; [spec-trade-lexicon.md](trade-surface/spec-trade-lexicon.md) §4a |
| **S1** — a feature building counts for nobody until one faction owns both its sector and its slot | Read from `sector-features`' `FactionTier`, never re-derived and never softened to "nearly unlocked": a split-owned building leaves the flag locked with its own reason copy. That is the only correct surface behaviour — a player who owns the sector but not the slot is told to finish owning it, not shown a half-enabled control | spec-trade-unlock §2 |
| **C3** — banking waits on the save-identity re-key | `trade-status`'s `Banked` part is Σ banking-fact value, so it is **0** until banking lands (`banking-fact` → `material-ledger` → `solid-enforcement` SE4.12–SE4.38) and the headline simply omits the part (a zero part is already omitted). The strip ships with logistics and gains its first number when banking lands — never a second income read to fill the gap. The Treasury hold control (`BankingTier ≥ 2`) unlocks on the same schedule | [spec-trade-status.md](trade-surface/spec-trade-status.md) §3; spec-trade-unlock §2 |
| **L6** — the Standard Hall is an eighth building kind | Deliberately **not** a rail flag: forging standards is `legion-build`'s surface, and this cluster's flag list stays the five trade/logistics ladders plus the two milestones. A legion surface that wants it reads the same `FactionTier(standard)`, never a copy of `TradeCapabilities` | spec-trade-unlock §2 |
| **S2 / W1 / W2** — goods cross only by rift route; an advance is a weight-limited transit | Nothing in this cluster claims otherwise, and one player-facing consequence is owed: the advance dialog is `world-continuity` `multiverse-surface`'s, and it now says plainly that goods do not cross with an advance and shows the carry **weight** budget. `trade-lexicon` owes no new word yet — `world-transit` will bring the import/export vocabulary when it exists | `world-continuity/spec-multiverse-surface.md` (no change owed here) |
| **CQ2** — legion equipment and doctrine upkeep may draw banked goods | No surface change owed: the draw is `legion-build`'s and symmetric, so no handicap line appears in the turn report (principle 11 would require one only for an AI-only lever) | — (stated) |
| **m15** (global audit, owed) — the C4 slot rename had two routes into one world-map file | **One ask** (global audit X-14) covering both display names (`market` → "Market Square", `vault` → "Vault Site"), filed by `trade-lexicon` and referenced by `exchange` `exchange-hub`, which no longer edits `SlotTypeCatalog.cs`. Ids and `SlotKind` unchanged | spec-trade-lexicon §4a; `exchange/spec-exchange-hub.md` §3 |
| **M1** (global audit, owed) — the `trade-wire` ↔ `trade-unlock` cycle needed a landing note | One line: `trade-wire` lands **first** with `WorldTradeDto.Capabilities` present and every flag false (an additive wire contract change with no FE consumer yet); `trade-unlock` lands next and fills it, asserting it fills the field the wire already ships. The intermediate state is a rail with everything locked — correct, not broken | spec-trade-unlock (before Boundaries) |

### DESIGN-GATE §5 (this round)

`[x]` Read this session: the register's Round 6 (whole), the global audit (C1–C3, M1–M8, minor table), this
map and every spec edited · `[x]` Verified against code: `SlotTypeCatalog.cs:72`, `:74` (the two slot display
names) · `[x]` citation audit run on every edited file · `[ ]` no suite run (documents only) · `[~]` session
boundary: the caller's fence (this map, `trade-surface/**` and the other named trees) · `[x]` corrections
propagated (§12.4's flag wording is unchanged: the five tier fields stay, and the stamp-vs-surface distinction
is stated in the spec) · `[x]` no population pinned · `[x]` no cap added · `[x]` fog rules untouched (null is
not zero; a locked flag shows its reason, never a fabricated tier).
