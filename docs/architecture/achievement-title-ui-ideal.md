# Achievement UI (Hall + actor titles) — the ideal

**Status:** idea-ui phase, 2026-09-15. Not a spec. No build authorized.

> **Updated 2026-09-18.** **4 owner rulings landed 2026-09-18**: Hall on the empire rail layer, existing theme packs reused, one worn name with stacking underneath, queued after P4 rail work.

Session: `achievement-title-20260915-7f3a` (worktree). System parent:
`achievement-title-ideal.md` (registry, Cold evaluation, bundles, slots,
lifecycle — all decided). This doc covers **player presentation only**.

Reading gate satisfied this session: `idea-ui-phase.md` (binding procedure),
`gui-lego-ideal.md`, `gui-lego-authoring.md`, `gui-lego-map.md`,
`design/gui-lego/README.md` (piece inventory), `gui-lego/menu-refactor-queue.md`,
`game-gui-principles.md` GG-1/15/23/44/46/54/62, `actor-sheet-ideal.md` (host +
tab kinds), `achievement-title-ideal.md` (system decisions), element/status/
resource catalog shapes + theme-pack shapes, FE factory + route surveys.

## Step 0 — principles, in our own words (binding on every choice below)

1. **Every RPG feature lives in the RPG layer.** Hall and title menus present
   Hub/catalog/RPG state (bindings, unlock ledger, catalogs). They are never
   blocked by Plant/Zombie Unity fields, and they never read live match
   objects — "the lawn can't show titles" is the wrong frame; the fold reads
   the ledger and the Hub snapshot.
2. **A game is a stage with layers, not a document with pages** (GG-1). The
   Hall opens as a layer over the sanctum/empire stage; the actor title menu
   opens as an `ActorPanel` tab layer. No sibling routes (`/achievements`,
   `/titles`, `/hall`); closing returns the exact stage left behind.
3. **Recipe + fold + bus — never a god TSX.** Each surface is a recipe JSON
   (slots + binds) + a pure fold + a closed bus catalog. A 679-line layer
   that owns query, sort, mutations, and paint (the `RelicsLayer` shape) is
   the defect this phase exists to catch.
4. **Theme packs own paint.** Title badges declare element/status/rank slots;
   packs supply `css` + `paint` hex + `vfx`. A hard-coded title color in piece
   markup is a Lego violation, not taste. No new element colors invented —
   `element-*` packs exist.
5. **Buy before build.** `lucide-react` icons, shared kit pieces, existing
   factories — a fat chunk gets code-split, never a reason to hand-roll a
   fourth gauge.
6. **Each bug is one or more modules; shared piece first, surface second.**
   A title badge used by Hall + actor tab + HUD is one piece, not three twins.
7. **No engine vocabulary on the player surface** (GG-23). No
   `typeId`/`ptr`/`Intent`/`UniqueActor`/`Cold`/`mods_json`/`container_kind`,
   no dotted-id title-casing (GG-62) — catalog `displayName` + `reading` only.

## Which loops/places these serve

- **Spine C — item collection** (Hall as collection + loadout: `???` slots do
  the work, Chou CD4) and **Spine A — power** (3-slot doctrine choice).
- **Spine B — summon/fusion** (actor titles on unique specimens).
- **Places 5/7 — world stage + quests/events** (Hall lives on the empire
  stage; hidden/vague teasers and curses live the quest layer).
- Combat depth hangs on places; these surfaces feed it and are not a loop.

## What this is (player language)

The **Hall** is the empire's trophy wall and war table in one: every title
earned, three slots to wear into the world, each choice showing what it does
in words before it is worn. The **actor title menu** is a specimen's honors
sash: titles earned, slots filled, one name worn, the rest working underneath
— plus the marks that can't come off, with what lifts them written plainly.

## What already exists

### Built

- **Shareable pieces with React factories** (`gk-web/web/fusion-rpg-web/src/ui/gui-lego/pieces/`):
  `chip` + rails (`chrome.tsx:88-149`), layout (`surface-shell`,
  `split-inspect`, `scroll-region`, `family-list/block` — `layout.tsx`),
  `channel-row`, `inspect-pane`, `value-hero`, `meta-sentences`, `cap-note`,
  `gauge-donut` (`domain.tsx:232`), `gauge-stack`, `source-list` (GG-49 —
  `domain.tsx:287`), `element-badge`/`phase-badge`/`role-badge`/`shield-status`
  (`badges.tsx`), `pool-meter`, `progression-gauge`, `standing-bars`,
  lifecycle `phase-loading/empty/error/pending` (`lifecycle.tsx:55`).
- **Theme packs (40)** in `docs/design/gui-lego/themes/packs/` (mirrored to
  FE): element×7, status-category×4, resource×6, side×2, posture×3, neutral,
  cook-tab×4, bucket×8, action-category×5 — each `css` + `paint{accent,
  accentMuted, onAccent}` + `vfx{select, idle}` + `glyphDefault` (e.g.
  `docs/design/gui-lego/themes/packs/element-fire.json:5-19`: accent `#e0703c`, `vfx.ember-pulse`).
- **Hosts + tab grammar:** `ActorPanel` canonical band-2 host, never a
  `#/actor/:id` route (`actor-sheet-ideal.md:45-54`); 8 closed tab kinds with
  labels/order from `gk-core/data/tuning/actor-sheet.v1.json:6-60`; a ninth tab kind
  with no renderer is a load reject.
- **Catalog split precedent:** `element/status/resource/derived/aptitude-catalog.v{n}.json`
  (numbers elsewhere); unit cooking rules (per-mille→one-decimal %,
  ms→s — `spec-magnitude-and-units.md:239-250,275-276`); live reads
  `GET /api/actors/{id}/sheet|/derived`, `GET /api/catalogs/actor-surface|derived-surface`.

### Wiring gap

- `element-badge` + theme packs exist but no title surface consumes them —
  the Condition-incident shape (mute chips while packs sit unused). Title
  element paint must fold `themeRef` and render pack `paint`, never a private
  color map.
- `source-list` (FULL attribution) exists; title contributions have no
  surface wiring it yet — sheet agreement test stays red until bound.
- `gauge-donut` exists; Hall family-share display has no wiring to it yet.

### Real gap

- No `hall-console` / `actor-title-tab` recipes (5 recipes ship: derived,
  condition, shield, aptitudes, preset — no achievement/title/hall file in
  either recipes dir); no queue rows (P0–P4 + Later list has no Hall/title
  entry — two rows proposed, one surface per stream, sequenced Hall first);
  no title pieces (`title-card`, `title-slot-row`, `curse-row`,
  `hall-slot-list`; teaser = stub state, worn = variant — see reuse map); no
  `achievement-titles-catalog.v{n}.json`; no Hall/actor-title FE, routes, or
  bus events (grep `achievement` in `web/.../src`: zero). No queue row is
  eligible until fold/bus named + recipe JSON + HTML per queue entry criteria.
- Ninth `ActorPanel` tab ships as a migration, not an assumption: tuning JSON
  9th entry + renderer + grammar version bump (Ask-first: `actor-sheet`
  owns shell/tab grammar, `gui-lego` owns queue/recipe) — until landed, the
  tab load-rejects per the closed-8 rule.
- No title-rarity/variety pack: v1 folds `themeRef` from element/status/
  resource packs only (`rank` slot dropped — no owning pack, private title
  colors reject). A rarity pack needs an acceptance test (which family paint
  beyond element/status a content pass proves) or closes as packs-only.

### Built, defective

- Sibling rail layers (`RelicsLayer.tsx:679` god-TSX) are the anti-pattern on
  record — the Hall must not copy that shape even though it looks like the
  nearest neighbor.

## Owner needs → module breakdown

| # | Player need | Module(s) | Bucket | Notes |
|---|---|---|---|---|
| 1 | See 3 Hall slots, equip/unequip | `hall-slot-list`, `title-card`, closed Hall bus | Real gap | Atomic apply; skipped slots reported, never silent (loadout pitfall) |
| 2 | Compare a title before wearing it | `inspect-pane` (reuse) + FULL `source-list` | Wiring gap | No-compare = wiki-tab-out (Solana); side-by-side equipped vs candidate |
| 3 | Names/readings that read like fiction | catalog-driven copy | Real gap | GG-62: `displayName`/`reading`/`hudToken` rows; dotted ids forbidden |
| 4 | Element paint on badges | `element-badge` reuse + packs | Wiring gap | `themeRef` folded, `paint` hex rendered; private color map forbidden |
| 5 | Expiry honesty ("12 world turns left, from worn turn", never silent snap) | lifecycle slice + `cap-note`/`meta-sentences` with destination copy | Real gap | GG-54: withdraw + visible restore naming destination (back-to-Hall/re-equippable, Hall-full path, dead-actor path) |
| 6 | Hidden/vague teaser (`???` slots that say what unlocks them) | `title-card` stub state + `phase-empty` with catalog teaser + lock reason | Real gap | GG-44/GG-17: slots shown, tier placement hidden, unlock reason authored |
| 7 | Curses visible, unwearable, liftable | `curse-row` + ritual CTA (disabled-with-reason) | Real gap | Price from `titleRitualPrice.*` numbers + catalog copy; insufficient = disabled naming need + source, no escrow; failed ritual paints player-words reversal |
| 8 | Empty Hall / empty slots honest | `phase-empty` (reuse) | Built | Ledger-empty Hall renders lifecycle piece, never omits |
| 9 | Find a title in a large collection | `tool-search` (reuse) | Built | Keyword + family filter (Diablo stash lesson) |
| 10 | Every tap acknowledged, truth from authority | per-mutation GG-15 contracts (equip / unequip-all / ritual) | Real gap | Ack in one frame, paint on confirm only; preview never mutates (see shape) |
| 11 | Actor tab: slots + one worn name | `title-slot-row`, `title-card` worn-variant, actor title recipe | Real gap | Highest-tier-wins + tiebreak; sheet/HUD/telemetry share one selector |
| 12 | Numbers as effects, never raw ints | GG-46 cook slice with per-quantity table | Wiring gap | Shares/weights `perMilleRatio` + op (`Increased +15%` vs `More ×1.15`, R1 divide-by-10/one-decimal, R2 away-from-zero); `validTurns` integer turns (Count-like, never ms); prices in stock units; renderer rejects bare numbers |

**Shared reuse map:** `chip`, `element-badge`, `gauge-donut` (family shares —
only with soft-cap marker rule below, else chip + number), `source-list`,
`inspect-pane`, `tool-search`, `phase-empty/loading/error`,
`meta-sentences`, `cap-note`, `value-hero`, `family-list/block`,
`split-inspect`, `scroll-region` — one `title-card` (Card-rung specialization;
`ActorCard`/relic-card composition insufficient because neither carries
slot/equip/teaser/curse semantics) serves Hall + actor tab + (future) HUD
tooltip. New pieces (4): `title-card`, `title-slot-row` (Row rung —
`channel-row` variant insufficient: slot equip + requirement-failure states),
`curse-row` (Row rung — ritual CTA + tombstone states), `hall-slot-list`
(layout list of 3 fixed slots — `family-block`+rows cannot carry atomic-apply
slot semantics). NOT pieces: teaser = `title-card` in `stub` payload state +
`phase-empty` (six-state SSOT); worn mark = `title-card` worn-variant (never
a sixth piece).

## Prior art (numbers, failure modes, sources)

- **Inventory/equipment/preset split** (solana.garden loadout guide): inventory
  owns instances; equipment owns worn-slot references; presets are named
  snapshots (slot→instance map). Failures: partial preset apply leaving limbo
  items (always report skipped slots — "Fire Staff not found, 7/9 applied");
  stat order ambiguity (document + unit-test aggregation); mid-combat swaps
  (enforce in API, not buttons); duplicate uniques via race (lock instance
  across slots); no-compare UI (players leave for wikis); paper-doll without
  list fallback (controller/mobile); preset bloat (cap 3–10). Harbor
  Chronicles: 5 presets + resistance tags + armory screen cut raid prep
  11.8→~5 min (~67%). Hall adopts: 3 fixed slots (no presets v1), atomic
  apply with skipped-slot report, comparison pane mandatory, equip rule in
  API.
- **Preview-without-commit + destructive confirm** (TLOU loadout case,
  lilyxia.com): equipped vs viewed states distinct; reset requires
  confirmation; "not enough points" flyout names the reason + points at the
  info. Hall adopts: candidate preview never mutates bindings; unequip-all
  confirms; Hall-full/requirement failures name cause + destination.
- **Armory blueprint space** (Diablo IV inventory case): configure builds in a
  space separate from equipped attributes; quick-save current as preset;
  keyword + attribute stash filters. Hall adopts: inspect/compare sandbox
  before apply; `tool-search` keyword + family filters from day one.
- **In-stage loadout check** (Deathloop loadout study): players asked to see
  loadout mid-stage; read-only check costs nothing and aids strategy. Hall
  adopts: read-only Hall layer openable from any stage (GG-1), apply gated
  out of combat.
- **Achievement plumbing failures** (bugnet.io): SDK-not-ready (queue +
  flush), offline unlocks (persist pending in save, flush on reconnect),
  ID mismatch (code vs registered pack fails silently), progress reset on
  reload (persist counters in save, not locals), cert-unreachable
  achievements. Hall adopts: pending-grant queue flushed on load; id grammar
  validated at load; progress counters ledger-backed; every achievement
  reachable in normal play (no debug-gated titles).

## The shape (chosen vs rejected)

**Chosen:** two recipes — `hall-console` (PanelShell rail layer over the
empire/sanctum stage) + actor title tab (ninth `ActorPanel` tab migration,
same host, same tab grammar) — sequenced one surface per stream, Hall first,
each with its own queue row. Composed of shared pieces plus 4 new pieces,
one fold + closed bus catalog per surface, `themeRef`s from existing packs,
HTML drafts before React, owner gate before mount. Per-mutation GG-15
contracts: equip/unequip-all/ritual acknowledge in one frame (press/`sending…`,
candidate preview never mutates) and mutate paint only on authoritative
confirm, with forced-500/toast path. Reach: Hall reads from empire/sanctum
stages; from lawn/battle it is travel-or-forbidden with reason (per-stage
reach matrix at spec time — GG-1 grants layers, not universal reach);
read-only Hall check allowed wherever reach permits, apply gated out of
combat.
**Rejected:** a god-TSX Hall layer (copies the `RelicsLayer` defect);
"one CSS PR" over chronicle/almanac wrappers (wrong surface, zero modules);
sibling `/hall` or `/titles` routes (GG-1 violation — layers, not pages);
inventing title colors (packs exist); a second badge/palette kit (ERM/pack
extension or nothing); presets v1 (3 fixed slots already decided — presets
are a later queue item, not this surface).

## Tunables (presentation only — no balance numbers in FE)

Catalog: `achievement-titles-catalog.v{n}.json` (`displayName`, `reading`,
`icon`/`hudToken`, flavor; hidden-teaser copy lives here too). ThemeRefs:
element/status/resource pack ids per title row (+ title-rarity pack only if
gui-lego accepts it). Structural CSS: 3-slot grid, card density, fixed gauge
boxes. Cook: GG-46 unit rules (per-mille→%, ms→s). Nothing else tunable here —
shares, caps, windows, prices stay in the numbers file owned by the system
specs.

## What this deliberately does not decide

- Registry/evaluator/bundle/lifecycle behavior (system ideal + 6 specs own it).
- Exact titles/copy (Seedsmith content passes + catalog authors).
- Queue priority or host choice (gui-lego-owned; proposed: Hall as empire
  rail layer, actor tab as ninth `ActorPanel` tab).
- Recipe JSON, fold contracts, bus event names, HTML drafts (`/spec` phase).
- Title presets, sharing, transmog-style display overrides (later).

## Owner rulings — 2026-09-18

All four confirmed at the recommendation.

| # | Ruled |
|---|---|
| 1 | **Queue placement:** Hall **and** the actor-title tab land **next after the P4 rail work** |
| 2 | **Hall host: the empire rail layer** |
| 3 | **Title rarity extends the existing element/status packs** — no new title-rarity pack |
| 4 | **Worn display: one worn name, stacking benefits underneath.** No "show all equipped" variant |

### Why the rail, and what stays off it

Titles have two scopes, and ruling 2 puts each where its subject already lives: the **empire** half owns
Hall slots and sits on the rail beside Creatures, Commanders, Relics and Fusion; the **actor** half stays
a tab on the actor sheet. That split is not cosmetic — it is what stops the Hall becoming a second place
to manage actors.

**This is now load-bearing in a way it was not when this document was written.**
`species-progression-ideal.md` R-S1 (2026-09-17) ruled that a general creature and a unique creature are
the same thing apart from **equipment, then title, then later layers** — *"if unique unit have no
equipment, is literally a general unit with same level and same stats/passive skill distribution."*
**Title is differentiator #2.** The actor-title tab is therefore not decoration on the sheet; it is one of
the two surfaces that explain why a unique creature is different from a general one at all.

### Ruling 3 keeps one theming vocabulary

Extending the element/status packs rather than adding a title-rarity pack is the same discipline this
repo applies to weight tables and action vocabularies: **a fourth of anything has to justify itself.**
The cost is accepted and worth naming so it is not a surprise later — title rarity is a ten-rung ladder
being expressed in tokens designed for elements and statuses, so a rung may end up borrowing a colour
whose fiction is elemental. If that becomes a real conflict (a rarity that cannot be read without
stealing an element's meaning), the split happens then, with evidence, rather than pre-emptively.

### Ruling 4 is the same separation `achievement-title` decision 3 already made

One worn name is the **fiction**; stacking benefits are the **mechanics**. Decision 3 in
`achievement-title-ideal.md` already drew that line with highest-tier-wins so *"sheet, HUD, and telemetry
agree"* — a "show all equipped" variant would re-merge them and force three surfaces to invent a rule for
which name is *the* name anyway.

**One honest risk this leaves**, worth a spec's attention rather than a re-decision: stacking
contributions the player cannot see are the thing most often mistaken for a bug. The ruling does not
require a contributor list, and nothing here adds one — but if players report titles "not working", that
invisibility is the first place to look, not the stacking rule itself.

### A sequencing note on ruling 1, recorded not overridden

The ruling puts both surfaces after P4. Worth noting for whoever schedules it: **the actor-title tab has
no rail dependency** — the actor sheet already exists — so it *could* ship earlier, and it is the half
R-S1 made load-bearing. The owner chose to keep them together, which keeps one review surface and one
catalog landing instead of two. Recorded so a later session does not mistake the pairing for an
unexamined default.

---

<details><summary>Original open questions, for the trail</summary>

## Open questions (owner decisions only)

1. **Queue placement:** Hall + actor-title-tab as which queue rows (proposed:
   next after P4 rail work — gui-lego to confirm)?
2. **Hall host:** empire rail layer vs sanctum layer — which stage owns it?
3. **Title-rarity pack:** extend element/status packs only, or add a small
   title-rarity pack (Ask-first with gui-lego)?
4. **Worn display:** single worn name + stacking underneath (system-locked) —
   confirm no "show all equipped" variant wanted?

## The real question

**Shape** (module set + recipe split + reuse map), not feasibility — every
piece, pack, host, and catalog shape needed already exists except 5 small
pieces, 2 recipes, and the catalog file. The risk is composing a sixth god
layer, not inventing a system.

</details>
