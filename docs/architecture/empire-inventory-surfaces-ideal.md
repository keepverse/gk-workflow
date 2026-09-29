# Empire inventory surfaces — the ideal

> ### ⚠️ Status line vs. what shipped (checked 2026-09-18)
>
> **This document's status line is not current, and it is the kind of wrong that costs a whole
> session.** Measured today: **map APPROVED 2026-09-15 (owner: "Approve all")**, **5 module specs** under `docs/architecture/empire-inventory-surfaces/`, and a task list at **all 5 module specs written against the approved map**.
>
> A status line reading *"no build authorized"* over a program that has already shipped invites
> the next session to re-derive work that exists — and its inventory of gaps is stale in the same
> direction, because a gap named before the build is usually closed by it. **Read this document
> for its reasoning and its decisions; never for its status, its gap list, or its counts.**
> Verify anything load-bearing against the capability map, the task list, and the code.

**Status:** idea-UI phase, 2026-09-15. Not a spec. No build authorized. No React, no plan, no code.

**Program id:** `empire-inventory-surfaces` (player surfaces only). The system underneath is
`scoped-inventory`, whose idea is locked in
[scoped-inventory-hierarchy-ideal.md](scoped-inventory-hierarchy-ideal.md) and whose backend verbs
are spec'd in `scoped-inventory-hierarchy/spec-legion-cargo.md`,
`spec-sector-storage.md`, `spec-cargo-transfer.md`, `spec-cargo-fate.md`.
This doc designs **what the player sees and touches** for three surfaces and nothing else:

1. **Legion cargo panel** — what a marching war band carries, with its slot and weight meters.
2. **Sector storage panel** — what a held settlement keeps in its vault, with capacity, contents,
   and capture-change messaging.
3. **Cache discovery + recovery flow** — fallen caches on sectors and lanes, the claim action, and
   failure/refusal messaging.

**Sibling:** a concurrent agent is writing `empire-wonder-surfaces-ideal.md` — not touched here.
Shared pieces are cross-referenced **by name** (`capacity-meter`, `stock-row`, `phase-*`) so both
surfaces converge on one kit instead of growing twins.

**DESIGN-GATE §1 rows read this session:** Product vision (`guide/the-game.md`,
`guide/the-loops.md`); Anything-a-player-sees (`game-gui-principles.md`,
`design/information-architecture.md`, `design/README.md` §2 ERM, `fe-game-foundation.md`);
Player menus (`gui-lego-ideal.md`, `gui-lego-map.md`, `design/gui-lego/README.md`,
`gui-lego/menu-refactor-queue.md`, `decisions.md` GUI Lego row). `actor-sheet-ideal.md` was
**not** re-opened in full: these surfaces live on the world stage and its inspector layers, not on
the ActorSheet, and nothing here composes actor derived channels — that boundary is stated, not
assumed. `decisions.md` was grepped for an existing "empire inventory surfaces" lock: **none** —
greenfield at the doc level.

---

## 1. Which loop this extends

**Place 4 (World map — adventure: legions)** and **Place 5 (World stage — empire building)**,
feeding **spine C (Item collection and progression)** — `the-loops.md:48-58, 105-121`.

- The **legion cargo panel** hangs on Place 4: a legion is committed, marches, and stands somewhere.
  Its packs are inspected and loaded where the legion is — on the world stage, over the map, never
  on a separate screen.
- The **sector storage panel** hangs on Place 5: inside a held sector, beside slots, buildings, and
  recruitment (`the-loops.md:117-119`). It is part of "inside a held sector," not a new place.
- The **cache recovery flow** hangs on Place 4's march-and-claim verbs (`farm / hunt / defend`,
  `the-loops.md:83-99`): a fallen cache is ground the player holds or reaches, and picking it up is
  hunting's aftermath, not a new loop.
- All three serve spine C's verbs — find, vault, equip, compare — at empire scale: cargo and vaults
  are where relics **rest between** the finding and the equipping, which still happens in the
  Relics layer.

The world map is a **stage** (IA §2.2, GG-4: a place the player acts in). All three surfaces are
**band-2 layers over that stage** (GG-1/GG-5): the legion panel opens from a selected legion, the
vault panel lives inside the sector inspector, the cache prompt opens from a legion standing where
a cache lies. Closing any of them returns the player to the exact map state they left (GG-12).
No new route, no new stage, no sibling screen — inventing one to "fix" glanceability would be the
GG-1 violation this phase exists to catch.

---

## 2. Load-bearing principles, restated inline (not links-only)

In this doc's own words — read first, per idea-ui §0, and applied below, not merely cited:

1. **The game numbers live in the game layer, never in the lawn.** Cargo totals, vault capacity,
   and cache contents are world-map state. Nothing on these surfaces waits on the PvZ board, the
   injector, or a live match. "The lawn can't show the packs" is the wrong frame — the lawn is
   never asked.
2. **The map is a stage with layers, not a document with pages.** A war band's packs, a
   settlement's vault, and a fallen cache all open **over** the world map. A "cargo page" or a
   "vault tab" that navigates away from the map is the defect, not a design.
3. **A surface is a recipe of shared pieces plus a pure data fold plus a closed list of actions —
   never one big component that owns everything.** A "CargoPanel.tsx" that fetches, lays out,
   paints meters, joins item names, and writes its own copy is the god-TSX defect. The pieces
   (`capacity-meter`, `stock-row`, lifecycle pieces) are shared; the recipe is per surface; the
   fold turns backend rows into display text; the action list (load, unload, deposit, withdraw,
   claim) is closed and reviewed.
4. **Paint belongs to theme packs, not to the panel.** Rarity colors, faction tints, full/empty
   meter paint, and any claim-success flourish come from packs as resolved paint values. A
   hard-coded gold-for-legendary or red-for-full inside a cargo component is a Lego violation,
   not taste.
5. **Buy presentation, don't hand-build it.** Meters, icons, and motion come from the locked set
   (`lucide-react`, `recharts`, `motion`) or from kit pieces already in the queue. A heavy first
   load is fixed by splitting the chunk, never by banning the library or drawing four bespoke
   SVGs.
6. **Every player-visible gap becomes one or more named modules, not one styling pass.** "The
   vault looks empty" is a module question (which piece owns empty? which fold supplies the
   locked/unbuilt states?) answered at module scope: shared piece first, surface recipe second,
   polish third.
7. **No engine words on the player surface.** The player reads packs, vaults, weight, slots,
   fallen caches, and plain reasons ("the packs are full"). They never read table names,
   place kinds, disposition flags, correlation ids, or claim-log vocabulary. Those live in §4's
   evidence table and in specs — never in panel copy.

---

## 3. What this is (player language)

**The player sentence:** *Every war band I send out carries its own packs — I can see what's in
them and how heavy and full they are. Every settlement I hold can keep a vault, once I've built
one there — I can see what it holds and how much room is left. If a war band falls on the march,
its packs don't vanish: they lie where it fell, marked on the map, and another band that reaches
that ground can pick them up. If I lose a settlement, what's in its vault goes to whoever holds
it now — and the game tells me so, plainly, instead of letting me discover it.*

Three surfaces, one mental model: **things are where they are, and the panel shows where.**

- **War-band packs (legion cargo panel).** Select a war band on the map → a panel shows its
  contents as a list of stacks, plus two meters: **slots** (how many different stacks) and
  **weight** (how heavy, against what the band's troops can carry). Loading from the home stash
  and unloading back are actions on this panel. The totals are the band's — troops are a headcount,
  never individuals with their own packs, so no per-fighter breakdown is ever shown.
- **Settlement vault (sector storage panel).** Select a held settlement → inside its inspector, a
  vault block shows stored stacks and one meter: **room** (rows used against what the built
  vaults grant). No vault building → no vault block, only a short line saying what would unlock
  it. Moving things between a band standing in the settlement and its vault (put in / take out)
  happens here. If the settlement changes hands, the panel says so: the stored goods now belong
  to whoever holds the ground.
- **Fallen caches (discovery + recovery).** A war band that falls leaves its packs where it fell —
  on a settlement's ground or on a road between settlements — marked on the map. A band standing
  on that ground sees the cache and can **pick it up**; what fits goes into its packs, what
  doesn't stays for a later trip, and the panel says which is which. A cache nobody can reach, or
  one that's already been emptied, never pretends otherwise.

What all three share: **every action answers visibly.** Success, refusal, and partial success all
produce a plain-language message on the spot (band-4 toast). Silence is not an outcome (GG-16).

---

## 4. What already exists — built / wiring gap / real gap / built-defective, with file:line

Backend first: the four scoped-inventory verbs are **built in `FusionRpg.Data` (+ one Core
capacity function)**. Every citation below was opened this session in the worktree.

### Built (backend — the surfaces' data and verbs exist, proven by code)

| Finding | Evidence |
|---|---|
| Legion cargo table exists: one row per stack aboard a legion, keyed by legion, with snapshotted per-unit weight | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.LegionCargo.cs:64-77` (`CREATE TABLE rpg_world_entity_cargo`, incl. `weight_each`) |
| Load / unload verbs exist, single-transaction, with refusal vocabulary `cargo.not-owned` / `cargo.over-weight` / `cargo.no-slots` | `RpgStore.LegionCargo.cs:253-266` (public `LoadCargo`), `:268-304` (`LoadCargoUnlocked` — ownership check `:282-298`, capacity gates `:300-304`), `:395-402` (public `UnloadCargo`) |
| Legion-to-legion transfer exists, same-empire only, refuses `cargo.cross-empire` | `RpgStore.LegionCargo.cs:457-493` (`TransferCargo` / `TransferCargoUnlocked`, cross-empire refusals `:491,493`) |
| Sector vault table exists: one row per stored stack, keyed by sector, deliberately **no** owner column (reachability is derived live from whoever holds the sector) | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.SectorStorage.cs:55-70` (schema), `:113` (row-count read) |
| Sector vault capacity is computed fresh from built vault structures, additive, never cached | `gk-core/src/FusionRpg.Core/World/SectorItemCapacity.cs:14-27` (`SectorItemCapacity.EffectiveCapacity`; :3-12 doc comment states the loam-mirror shape); catalog field `gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:75` |
| Deposit / withdraw verbs exist (band ↔ vault), gated on presence + same faction + destination capacity; refusals `cargo.not-present` / `cargo.wrong-faction` / `cargo.sector-full` / `cargo.over-weight` / `cargo.no-slots` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CargoTransfer.cs:62-73` (public `DepositCargo`), `:75-96` (gates + `cargo.sector-full` at `:95-96`), `:136-147` (public `WithdrawCargo`), `:149-175` (withdraw gates) |
| Destroyed-legion cargo becomes a revisit-lootable cache at its last sector or lane (move, never copy, before the cascade delete) | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CargoFate.cs:23` + move at `:69,92` (`DELETE FROM rpg_world_entity_cargo` ordered before entity delete) |
| Claimable-cache listing exists: non-empty, non-voided caches pinned exactly where a legion stands; corrupt both-set/neither-set positions see nothing rather than a guess | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CacheFieldAccess.cs:48-93` (`ListClaimableCachesUnlocked`), public read-only entry `:99-106` |
| Claim-into-cargo exists: per-row fit against the band's weight+slot gates, one transaction; a row that doesn't fit **stays** for later (skip, not whole-claim refusal); replay-safe via claim log; refusals `correlation.missing` / `cache.unreachable` | `RpgStore.CacheFieldAccess.cs:280-366` (`ClaimCorpseCacheIntoCargoUnlocked` — reachability re-check `:302-304`, per-row gates `:327-337`, move `:342-360`), public entry `:372-387` |
| Empire stash surface exists (the load/unload source): held/armoury/equipped/storage tabs, real catalog rows, in-situ comparison | `gk-web/web/fusion-rpg-web/src/layers/relics/RelicsLayer.tsx:1-70` (tabs `"held" \| "armoury" \| "equipped" \| "storage"`, adapter joins) |
| Sector inspector shell exists (the vault's future host): nine ordered blocks + action cluster, pure/presentational | `gk-web/web/fusion-rpg-web/src/stages/world/inspector/SectorInspector.tsx:72-126` (blocks render, `data-block-order`; `BLOCK_ORDER` imported from `./blockOrder`, re-exported :128; Actions region inline ~:120-122) |
| World stage renders legions and opens the inspector; legion/sector view adapters exist | `gk-web/web/fusion-rpg-web/src/stages/world/WorldStage.tsx:222` (`adaptWorldLegion`), `:33` (`SectorInspector` mount) |

### Wiring gap (machinery exists but no player path reaches it)

| Finding | Evidence / notes |
|---|---|
| **No REST route serves any cargo/vault/cache verb.** `/api/world` exposes exactly six operations — state reads, command submit, turn commit, turn read, catalog — and none of Load/Unload/Deposit/Withdraw/ListClaimableCaches/Claim is among them | `gk-core/src/FusionRpg.Server/WorldEndpoints.cs:28,37,92,148,191,259` (the complete route list; zero cargo/cache routes). The Data verbs are callable only in-process/tests today — **not a wall**, the standard endpoint+fold+binding path, but the single largest gap in this doc |
| No fold, no bus, no recipe, no piece binding exists for cargo/vault/cache anywhere in `features/gui-lego` or `ui/gui-lego` | Verified by grep: zero `cargo\|sector.?storage\|corpse.?cache\|ClaimCorpseCache` hits under `gk-web/web/fusion-rpg-web/src` (this session). The kit to reuse is there (`pieces/chrome|layout|domain|badges|lifecycle`, `foldDerivedSurfaceVm`/`foldConditionSurfaceVm` as fold precedent, `createSurfaceBus` as bus precedent) — it is simply not wired to these verbs |
| Sector inspector has no vault block and no cache row; its Actions region holds exactly one verb (the delve-door row) ahead of the full roster | `SectorInspector.tsx:120-122` (Actions region inline, reserved, pending full roster); block list (`:73-126`) has no storage/cache member |
| Refusal vocabulary exists but has **no player copy**: `cargo.not-present`, `cargo.wrong-faction`, `cargo.sector-full`, `cargo.over-weight`, `cargo.no-slots`, `cache.unreachable` are backend reason strings with no authored player sentence anywhere | Searched FE strings this session — none. Authoring them is content work inside this program (GG-62: authored catalog rows, never prettified ids), not a backend change |

### Real gap (no shareable piece/pack/recipe path exists yet)

| Gap | Notes |
|---|---|
| `capacity-meter` shared piece (slot meter + weight meter + room meter as one piece with three densities) | `gauge-donut`/`gauge-stack` (`docs/design/gui-lego/pieces/gauge-donut.html`, `gauge-stack.html`) prove share/proportion; `pool-meter` proves a resource track — but no piece renders **two simultaneous gates** (slots AND weight, where either can refuse) or a vault's single room count. New piece, shared by all three surfaces by design |
| `stock-row` shared piece (one cached/carried/vaulted stack: icon, name, count, weight, per-row state) | `channel-row` is the nearest precedent (identity + columns + selectable + state class) but it renders derived channels, not item stacks with claim states (fits / doesn't-fit / left-behind). New piece; the Relics `RelicRow` (`RelicsLayer.tsx:51-70`) is a layer-local row, not a Lego piece — reuse its **shape**, not its code |
| Cache map marking (fallen-cache pin on sectors/lanes, incl. fog behavior) | `LegionMarker`/`LaneEdge` (world stage) render forces and lanes; plate 11 (`11-world-stage.html`) catalogs pins — but no pin kind means "fallen cache," and fog interaction (does a cache show under fog? whose fog?) is undecided (open question Q3) |
| Capture-change messaging content + event source | The backend transfer is reachability-only (no event fires — `spec-sector-storage.md` §Design 5 names this as a future notification consumer). No turn-report event, no toast copy, no vault "now held by" state exists |
| Rarity/theme pack coverage for item stacks on world surfaces | Packs exist for elements, resources, status-categories, sides, neutral (`docs/design/gui-lego/themes/packs/` — 30+ files). No `rarity` pack is wired to world-surface rows yet (gui-lego-ideal's theme taxonomy lists `rarity` as "future Relics") — cargo/vault/cache rows are that future's first consumer |

### Built, defective (present but wrong — still a module fix, not a vibe pass)

| Finding | Evidence |
|---|---|
| `features/storage/StoragePage.tsx` is a **developer archive console**, not a player vault: summary + archives + run-purge + trim-tails behind `testId="page-storage"`, `storage-*` test ids throughout | `gk-web/web/fusion-rpg-web/src/features/storage/StoragePage.tsx:37,216-352`. Under GG-40 this is correctly a developer-tree surface — the defect would be **mistaking it for the sector-vault surface** or routing players to it. Named here so no spec reuses it as the vault host |
| `RelicsLayer` "storage" tab is empire-scope storage, not sector storage | `RelicsLayer.tsx:39` (`type Tab = "held" \| "armoury" \| "equipped" \| "storage"`). Same word, different scope — the vault panel must never be a fourth tab here; it lives in the sector inspector (Place 5), beside buildings, not beside the armoury |

---

## 5. Owner bugs → module breakdown (+ shared reuse map)

No owner bug list was filed for these surfaces (greenfield — the backend shipped ahead of any
player surface). The table below converts the **scope brief** (cargo panel / storage panel /
cache+claim flow, each with contents, meters, and messaging) into modules, so a future bug list
has rows to land on.

| # | Player need (bug-shaped) | Module(s) | Bucket | Notes / file:line |
|---|---|---|---|---|
| 1 | "I can't see what my war band carries" | `cargo-panel` (recipe) + `stock-row` (shared) + `cargo-fold` | Wiring gap | Verbs built (`RpgStore.LegionCargo.cs:168` list read); no REST, no fold, no recipe |
| 2 | "I can't tell how full the packs are (slots? weight? which refuses first?)" | `capacity-meter` (shared) + `cargo-fold` | Real gap | Dual-gate meter piece doesn't exist; gates proven in code (`RpgStore.LegionCargo.cs:300-304`) |
| 3 | "Loading/unloading says nothing when it refuses" | `cargo-actions` (closed bus) + player refusal copy | Wiring gap | Reasons exist (`cargo.not-owned/over-weight/no-slots`); zero player sentences exist |
| 4 | "My settlement has no vault / I can't see what's stored" | `storage-panel` (recipe) + `stock-row` + `capacity-meter` (room density) | Wiring gap | Table + capacity built (`RpgStore.SectorStorage.cs:55`, `SectorItemCapacity.cs:14`); host built (`SectorInspector.tsx:60-72`); nothing connects them |
| 5 | "Nobody told me the vault changed hands when the settlement fell" | `capture-notice` (event + copy) | Real gap | Backend transfer is silent by construction (`spec-sector-storage.md` §Design 5); needs a turn-report event + toast + vault header state |
| 6 | "I can't see fallen caches on the map" | `cache-pin` (map marking) | Real gap | Listing built (`RpgStore.CacheFieldAccess.cs:48-93`); no pin, no fog rule |
| 7 | "I can't pick up a fallen cache / it says nothing when part doesn't fit" | `cache-claim` (recipe + actions) + `stock-row` (left-behind state) + `capacity-meter` | Wiring gap | Claim verb built with per-row skip (`RpgStore.CacheFieldAccess.cs:314-361`); no surface, no copy |
| 8 | Empty/unbuilt states read as broken ("empty vault", "no vault built", "no caches near", "band with no packs") | `phase-*` lifecycle reuse (loading/empty/error/locked) | Wiring gap | Pieces built (`docs/design/gui-lego/pieces/phase-empty.html` etc.; factories `ui/gui-lego/pieces/lifecycle.tsx`); never bound to these verbs |

**Module list (7 + shared):** `legion-sheet` (host menu with sub-tabs — locked Owner
resolution: legion gets a sheet-like menu, actor-sheet-style, each tab its own role; cargo is one
tab — supersedes the earlier bare-`cargo-panel`-over-map shape below, which is kept as the
rejected alternative), `storage-panel`, `cache-claim` (recipes);
`cargo-actions` (closed bus: load/unload/deposit/withdraw/transfer/claim); `cargo-fold`
(pure fold: rows → display + meter fractions + refusal sentences); `capacity-meter`,
`stock-row` (shared pieces, OWNED BY THIS PROGRAM — recommended; sibling wonder program reuses by
name; CONFIRMED owner 2026-09-16); `capture-notice`, `cache-pin` (event + marking).
Sibling `empire-wonder-surfaces` reuses `capacity-meter` + `stock-row` + `phase-*` by name where
a wonder vault or relic-carry display needs them — one kit, never twins.

**Shared reuse map (who reuses what):**

```text
capacity-meter  ← cargo-panel (slots+weight) · storage-panel (room) · cache-claim (fits?/left?)
                  · wonder-vault (sibling, by name)
stock-row       ← cargo-panel (carried) · storage-panel (stored) · cache-claim (fits/left-behind)
                  · RelicsLayer shape-reference only (not code reuse — layer-local row)
phase-*         ← all three surfaces (loading/empty/error/locked) · already built, bind only
tool-search     ← cargo-panel + storage-panel + cache-claim (filter stacks; GG-50 volume rule)
chip/badge      ← stack identity + faction tint via packs (no new badge piece)
surface-shell   ← all three recipes (host discipline; no forked shell)
SectorInspector ← storage-panel mounts as a vault block (host, not owner)
WorldStage      ← cargo-panel opens from legion select; cache-pin renders on map/lane layer
```

---

## 6. Prior art (outside repo)

| Source | What transfers | Failure mode to avoid |
|---|---|---|
| **Total War — baggage train vs. settlement supply warehouse** ([Supply Warehouse wiki](https://totalwar.fandom.com/wiki/Supply_Warehouse); Divide et Impera [baggage train](https://www.honga.net/totalwar/rome2/unit.php?l=en&v=dei&f=rom_rome&u=Supply_Roman)) | Two structurally distinct scopes ship side by side: a baggage unit **attached to an army** (carries on the march, reduces logistics costs) vs. a **settlement building** competing for a building slot (boosts replenishment for forces at home; "best built in areas near fighting"). Neither substitutes for the other. Direct precedent for packs-vs-vault being two mechanisms, and for the vault competing for a limited structure slot. | Armies show a single **supply bar with hover detail** (Thrones of Britannia community: "see your supplies when you click your general… supply bar bottom-left, hover for consumption/replenishment") — one glanceable meter, detail on demand. Our failure mode: showing two raw numbers (slots, weight) with no glanceable meter and no per-refusal reason (GG-55: never disable without saying why). |
| **Diablo (series) — carried grid vs. town stash** ([Inventory wiki](https://diablo.fandom.com/wiki/Inventory); [Diablo 4 stash performance](https://diablo4.gg/diablo-4-stash-tabs-a-performance-concern-diablo-4-devs/)) | The carried inventory is **bounded and spatial** (tiles per item; D4: fixed 33 slots), the stash is **larger, town-bound, and tabbed by item type** — the exact packs-vs-vault split, including "must return to town to put away finds." D4 tabs separate quests/consumables/equipment; console D4 drops tile management for a **sorted list by type** when space is tight. | Two documented failures: (a) **stash pressure with no search/filter** — D4's armory/loadout case study notes inventory management "difficult to sort, filter, and search"; fixed with keyword search + attribute filters + lock-to-protect. Our surfaces need `tool-search` + filters from day one (GG-50/51), not as polish. (b) **Loading everyone's stash always** caused D4's memory overhead — our fold must request **one legion's / one sector's** rows, never the empire's whole inventory, per surface open. |
| **XCOM 2 — timed loot + carry-or-lose recovery** ([Loot wiki](https://xcom.fandom.com/wiki/Loot_(XCOM_2)); community [corpse/evac rules](https://steamcommunity.com/app/268500/discussions/0/412448792359959003/)) | Drops appear **on the map with a radius marker and a turn timer**; any unit in radius collects; unexpired loot at mission end **auto-recovers**; on evac missions **only what carriers hold** comes home; explosives can **destroy** the loot ("Loot Destroyed!"); a carrier who dies **drops** what they held. | Three failures with direct cache-claim lessons: (a) **silent loss** — corpses/loot lost on evac with no signal read as a bug ("can't recover corpses" threads). Our claim flow must always say what stayed and why (per-row skip copy), and capture-notice must never let a vault silently change hands. (b) **destroyed-by-explosives with one red line** — the *only* acknowledgment is a floating message; our overweight/left-behind rows need the same in-place, at-the-moment signal, not a log entry. (c) **auto-collect vs. carry-home ambiguity** — two recovery rules by mission end state confused players for years. Our rule must be one sentence: *standing bands pick up what fits; the rest waits where it lies.* |

In-repo precedent (not external, listed because it already settled the pattern): `loot-pack`
(`party-dungeon/spec-loot-pack.md`) — capacity as a structural bound, move-never-copy, refusal
before write. The surfaces above present that discipline; they don't re-decide it.

---

## 7. The shape — chosen vs rejected

**Chosen: three recipes over two shared pieces, one fold, one closed bus, mounted on existing
hosts — with the locked legion-sheet direction.**

- `cargo-panel` = a **sub-tab of the new legion sheet-menu** (locked Owner resolution — actor-sheet
  with multiple tabs, each tab its own role) containing legion identity + `capacity-meter[slots+weight]` +
  `tool-search` + `stock-row*` in a `scroll-region` + action row (load / unload / hand to another
  band) → `cargo-fold`, events → `cargo-actions` bus. The earlier bare-panel-over-map shape is
  rejected below in favor of this.
- `storage-panel` = a vault block **inside the sector inspector's existing block order**
  (`SectorInspector.tsx:73`, `BLOCK_ORDER`) + `capacity-meter[room]` + `stock-row*` +
  put-in/take-out actions for the band standing there → same fold, same bus.
- `cache-claim` = map `cache-pin` → legion-context prompt reusing `capacity-meter[fits?]`
  (per-row fits / doesn't-fit) + `stock-row[left-behind]` + pick-up action → same fold, same bus.
- Empty/unbuilt/locked states are `phase-*` bindings, not new components: no vault built =
  locked-with-unlock-line (GG-17); empty packs/vault/cache = empty-with-next-action; load failure
  = error-with-retry.

**Rejected:**

| Rejected | Why |
|---|---|
| A bare `cargo-panel` over the map (the pre-resolution shape) | Superseded by the locked legion sheet-menu direction — cargo lives as a sub-tab, not a floating panel |
| One styling pass over the inspector + a new route ("cargo page") | Burns GG-1 (navigates away from the map) and GG-10 (adds depth); fixes no module — the verbs have no REST/fold at all, so there is nothing for CSS to style |
| One god `CargoPanel.tsx` (hypothetical — rejected, never built) owning fetch, layout, meters, joins, and copy | The exact defect this phase exists to catch (idea-ui §0.3, decisions.md GUI Lego row). Three surfaces would then triple it |
| Three twin meters / three twin rows (cargo-flavored, vault-flavored, cache-flavored) | Violates shared-piece-first (idea-ui §0.6) and GG-9 (one canonical rendering per concept). One `capacity-meter` with three densities; one `stock-row` with claim states |
| Reusing `StoragePage` (dev archive console) or the Relics "storage" tab as the vault host | Wrong tree (GG-40: developer surfaces stay developer) and wrong scope (empire vs. sector). The vault lives in the sector inspector on the world stage |
| Inventing a weight system or rarity colors in the pieces | Weight arrives snapshotted from the backend (`weight_each`); paint arrives from packs. Pieces render payloads (gui-lego-ideal §Theme taxonomy); they never author numbers or colors |
| Client-side capacity prediction ("you can fit 3 more") computed in the component | GG-15: outcomes are server-authoritative. The fold shows the last confirmed totals; the action's acknowledgment animation covers the round trip; refusal copy comes back from the verb |

---

## 8. Tunables — catalog / theme pack / structural CSS called out

None decided here — named so a future spec knows where each lands:

| Tunable | Home |
|---|---|
| Per-fighter carry weight + pack slots (flat defaults today; per-species table later) | `data/tuning/scoped-inventory.v{n}.json` (`CargoWeightPerUnit`, `CargoSlotsPerUnit` — spec-legion-cargo §Tunables); shape resolved, numbers open |
| Vault room per structure row | Seed-authored per structure row (`ItemStorageCapacityBonus` — spec-sector-storage §Tunables corrects the map: content, not a bare tunable entry); exact numbers open |
| Fallen-cache decay clock | `cache-decay-void`'s existing turn-counted clock (≈112 turns — spec-cargo-fate §Tunables); no second rate for band-death caches |
| Deposit/withdraw/claim cost | LOCKED by owner (action points extending `MovementRemaining`, HOMM3-inspired — see Owner resolutions + `world-action-economy` program): homes in `data/tuning/world.v{n}.json` `movement` block (dowse precedent); exact per-act numbers are spec-time content |
| Rarity paint for stack rows; faction tint for vault/cache headers; full/left-behind meter paint | Theme packs (`rarity` pack = cargo/vault/cache rows are its first consumer; `side` pack already built — `side-plant.json`, `side-zombie.json`) |
| Meter geometry (bar vs. donut, fixed box, breakpoints) | Structural CSS in the `capacity-meter` piece contract (GG-29 tokens only; GG-61 bounded shell — body scrolls, shell never swallows the viewport) |
| Player refusal/confirmation sentences (`cargo.sector-full`, `cache.unreachable`, per-row skip, capture transfer, …) | Authored copy catalog (GG-62 — authored rows, never prettified reason strings); home file named at spec time |

---

## 9. What this deliberately does not decide

- Deposit/withdraw/claim **pricing shape** (action points extending `MovementRemaining` —
  locked by owner, `world-action-economy` program owns the design); exact per-act numbers and the
  hold-garrison allowance stay spec-time content calls.
- Legion-to-legion handoff presentation (the `TransferCargo` verb is built;
  whether the panel exposes it inline, via select-another-band, or not at all).
- Cross-faction trade presentation — a real backend gap (no second item-owning identity exists);
  nothing here designs for it.
- Sector-to-sector trade routes — explicitly deferred to a future trading program (the hierarchy
  ideal's own deferral, with the Stellaris warning attached).
- Exact numbers: pack slots/weight defaults, vault room per structure, cache decay — shapes are
  locked upstream, numbers are tuning.
- Backend schema or verb changes — the Data layer is taken as built and correct; if a surface
  needs a verb that doesn't exist (e.g. a capture event feed), the spec names it as a dependency,
  this doc doesn't design it.
- Wonder/relic specifics — the sibling `empire-wonder-surfaces-ideal.md` owns them; this doc only
  reserves shared-piece names.
- Whether vault/cache surfaces wait on the item-collection chapter gate (Dave-level chapter,
  `the-loops.md:49-53`) or exist from first sector contact — the hierarchy ideal's Q4, still open
  upstream; this doc's surfaces inherit whichever answer lands.

---

## 10. Open questions — owner decisions only (Q1/Q3/Q4/Q6 ANSWERED — see Owner resolutions; Q2/Q5 still open)

1. **Where does the packs panel open from?** ~~Legion select on the map (preferred), or a rail layer?~~
   ANSWERED: legion sheet-menu with sub-tabs (cargo one tab) — locked direction, §5/§7 updated.
2. **Does withdrawing need a confirm?** Take-out moves goods into a band that may march away.
    Recommendation: no confirm for put-in/take-out between a band and a vault it stands in
    (same-faction, reversible, GG-22 prefers undo over confirm); confirm only for destructive or
    cross-faction-adjacent acts if any ever ship.
3. **Do fallen caches show under fog / to which eyes?** ~~Options (a)/(b)/(c), recommendation (c).~~
   ANSWERED: hidden until found — locked. (The earlier recommendation (c) is superseded; §4 fog
   references should be read as hidden-until-found.)
4. **What does the vault header say the day after a capture — and who gets told?**
    ANSWERED: "held by X" header always + band-4 toast and turn-report entry for the loser —
    locked (event feed is the real cost in `capture-notice`).
5. **Slots, weight, or both on first paint?** The backend refuses on either gate. Options: (a)
   both meters always (honest, denser); (b) the tighter gate big, the other small (glanceable,
   needs fold logic). Recommendation: (a) now — two thin meters, refusal names the gate; (b) is
   polish after the verbs are reachable.
6. **Does picking up a cache need a turn action, or is it free on stand?**
    ANSWERED: costs action points (HOMM3-inspired) — locked; designed in `world-action-economy`,
    surfaced here as "pick up (N AP)" copy once numbers land.

---

## 11. The real question

**Shape, not feasibility.** Every verb these surfaces need is built, tested, and refusal-typed
in `FusionRpg.Data` — load, unload, transfer, deposit, withdraw, list-claimable, claim-into-cargo,
destroyed-band-to-cache. Nothing here asks "can we build it." The question this doc puts to the
owner is the module set in §5: **two shared pieces + one fold + one closed bus + three recipes
on existing hosts** — and the six open questions above, which are all presentation and copy
calls, not architecture. Answer those, and `/spec` writes per-module specs (`spec-cargo-panel`,
`spec-capacity-meter`, …) under `docs/architecture/empire-inventory-surfaces/`, plans in
`tasks/empire-inventory-surfaces-plan.md` / `tasks/empire-inventory-surfaces-todo.md`, without
revisiting any backend.

---

## Hand-off

- Stop at this ideal. **No specs, plans, or code from this phase.**
- Next step after owner answers §10: `/spec` → capability map + per-module specs as above.
- Queue: `menu-refactor-queue.md` gains a row for these surfaces when the program starts
  (world-stage/empire entries — one surface per stream, per queue discipline).
- Sibling cross-ref: `empire-wonder-surfaces-ideal.md` (concurrent) — shared names reserved:
  `capacity-meter`, `stock-row`, `phase-*`.

## DESIGN-GATE §5 checklist (this document)

```
[x] Subsystems identified: world-map legion/sector state (Core/Data), player-menu presentation
    (FE Lego). No Status/ActorHub/Combat subsystem touched.
[x] Session boundary: worktree empire-development-20260915-b7e2 only; main checkout untouched.
    (No edits made outside the one ideal path below.)
[x] Read every doc in the §1 rows for those subsystems, this session (see header list).
[x] Checked decisions.md for a lock covering this: GUI Lego row (composition discipline, reused);
    no "empire inventory surfaces" lock exists — greenfield confirmed by grep.
[x] Every factual claim cites file:line (see §4 tables).
[x] Verified claims against CODE, not comments (all Data/FE citations opened in-session in the
    worktree; refusal strings read from implementation, not spec prose).
[x] Read the surrounding section of every rule quoted (GG band/time/authority rules cited with
    their band context, not as slogans).
[x] Tested (not assumed) constraints: REST gap proven by enumerating WorldEndpoints.cs routes;
    FE gap proven by repo-wide grep (zero cargo/cache hits under web/src); no golden/test
    movement claimed — idea phase runs no suite.
[x] Nothing contradicts a §2 invariant (SQL stays in FusionRpg.Data; no magnitude cap presented
    as progression ceiling — pack/vault limits are structural, fixture-bound, and throw/refuse
    rather than clamp; no f(Θ); no second ownership root).
[x] No assertion pins a derived-population count, item total, generated name/description text,
    or per-cycle outcome. (Counts named: 6 WorldEndpoints routes — a closed code-owned route
    list with a stated reason, not a population; 30+ theme packs — a reading, not a guardrail.)
[x] No event-refreshed cache introduced. (The claim-log replay-safety and reachability re-checks
    are cited as built backend behavior, not proposed.)
[x] No acceptance criterion fixes an ordering. (N/A — idea phase; stated where live reads are
    required: presence/faction/capacity checked fresh per verb.)
[x] No actor combat/derived magnitude produced or consumed — actor-sheet boundary explicitly
    declined, not silently crossed.
[x] No SOLID-violating parallel path: no second cache table, no second vault host (inspector
    block, not a page), no forked shell, no duplicated meter/row pieces — shared-piece-first
    throughout.
```

## Owner resolutions (2026-09-15, verbatim)

- Panel host: 'sub tabs in legion menu, legion need it own menu, maybe it is legion select, like actor sheet with multiple tabs, each tab have it own role' — NEW DIRECTION: legion gets a sheet-like menu with sub-tabs (cargo one tab), not a bare panel.
- Fog pins: 'Hidden until found'.
- Capture messaging: header + toast (recommended option).
- Pickup cost: 'cost action point, need new idea for this, inspire of heroes of might and magic 3, but you need audit current system already have this feature or not to avoid overlap' — action-point cost + new HOMM3-inspired idea; prerequisite: audit existing action/turn-cost systems for overlap (staffed separately).

### Action-point overlap audit (2026-09-15, code-verified) — verdict: GREENFIELD with boundary.
Movement budget EXISTS (WorldEntity.MovementRemaining, BudgetFor march-1000/scout-500/hold-0/dowse-tunable, Snapshot refill); march pricing EXISTS (LaneCost); stamina/action-points on world map NOT-FOUND (AP only battle-side); per-legion limits are one-move-last-wins + routed-drops + held-blocks. New per-action AP idea must EXTEND MovementRemaining/BudgetFor/Snapshot-refill, never mint a second pool, and must not re-mint LaneCost pricing or Admit-Reveal-report discipline. Claim-cost seam options: promote claim to command kind, or debit in-verb/resolver, or Pressure-side drain. Engine change bumps RulesetVersion + re-blesses goldens.
