# Empire Wonder surfaces — the ideal

> ### ⚠️ Status line vs. what shipped (checked 2026-09-20)
>
> **This document's status line is not current.** It says *"idea-UI phase ... Not a spec. Not a
> plan. Not code."* Measured today: [empire-wonder-surfaces-map.md](empire-wonder-surfaces-map.md)
> reads **"APPROVED 2026-09-15 (owner: 'Approve all')"**, with a same-day strengthen-pass amendment
> adding module 5 (`wonder-wire`). **5** module specs are written at
> `docs/architecture/empire-wonder-surfaces/spec-<module-id>.md`. This program has no
> `tasks/empire-wonder-surfaces-todo.md` of its own — the map states it extends
> `tasks/empire-development-plan.md` Phase 4B.1/4B.4/4D.
>
> Read this document for its reasoning and its decisions, never for its status. Verify anything
> load-bearing against the capability map, the module specs, and the code.

**Status:** idea-UI phase, 2026-09-15. **Not a spec. Not a plan. Not code.** Stop at this doc +
owner answers; next step after answers is `/spec` → per-module specs under
`docs/architecture/empire-wonder-surfaces/` (proposed), plan in `tasks/empire-wonder-surfaces-plan.md`.

**Program:** `empire-development` (map: `docs/architecture/empire-development-map.md`).
**System idea:** `docs/architecture/loam-relics-and-wonders-ideal.md` (relic earning, Wonder race
feeling, scope/rarity ladder). **Backend specs (all four read in full this session):**
`docs/architecture/loam-relics-and-wonders/spec-relic-item-kind.md`,
`spec-wonder-structure.md`, `spec-wonder-effect-empire.md`, `spec-wonder-build-flow.md`.
**Sibling ideal (do not write):** `docs/architecture/empire-inventory-surfaces-ideal.md` — a
concurrent agent owns it; shared pieces are cross-referenced by name in §5 below.

**Grounding read this session (DESIGN-GATE §1 + idea-ui §0 table):** `idea-ui-phase.md` §§0–5
(full); `loam-relics-and-wonders-ideal.md` (full, lines 1–412+); the four module specs above;
`game-gui-principles.md` (GG-1–GG-64, tiers); `gui-lego-ideal.md`, `gui-lego-map.md`,
`docs/design/gui-lego/README.md` (piece inventory, reuse matrix), `menu-refactor-queue.md`;
`decisions.md` GUI Lego row + Loam relics and wonders SSOT row; `the-game.md` + `the-loops.md`
(full). Surveyed: `docs/design/gui-lego/themes/packs/` (element/side/resource/action-category/
neutral packs), FE `features/gui-lego` (folds, buses, registries) + `ui/gui-lego` (RecipeMount,
pieces, recipes), world-stage inspector blocks.

**Verified against code this session:** refusal strings + Wonder fields exist server-side
(`BuildResolver.cs:104-130`, `WorldCommandAdmission.cs:114-116`,
`StructureCatalog.cs:211-226,393-426`, `WonderCatalog.cs`, `WonderExistenceScan.cs`,
`RpgStore.WonderBuild.cs`, `RpgStore.WorldTurns.cs:535-547`); FE slot/sector display
(`SlotRow.tsx`, `SectorLoamBlock.tsx`, `ReleaseGroundDialog.tsx:89-91`,
`adapt.ts:413-518`, `worldSelection.ts`); relic layer shape (`RelicsLayer.tsx:1-120`);
**zero** FE references to wonder/refusal vocabulary (grep over `web/` for
`wonder|RelicCost|RelicInstanceIds|cap-reached|count-mismatch|not-reachable` returns one false
positive — a comment containing "wondering" in `ChannelControl.tsx:8`). **Honest gaps:** no live
game probe ran (static + adapter evidence only); backend structure-field citations lean partly on
the four specs' own this-session-verified `file:line` readings, re-confirmed by grep here rather
than full re-reads.

---

## 0. Principles this doc stands on (in our own words, first)

1. **The empire screen shows empire facts, never engine facts.** Everything a Wonder surface
   displays — what a Wonder does, what it costs, why a build was refused — comes from world/Game
   state and catalogs. Nothing about these surfaces depends on, or mentions, the lawn, Unity, or
   any injector field. "The lawn can't show X" is the wrong frame; these surfaces never ask the
   lawn anything.
2. **A Wonder composer opens over the world, it never replaces it.** The player is standing on the
   world stage looking at a sector; raising a Wonder is a layer pushed on top of that stage
   (GG-1/GG-5). Closing it returns them to the exact sector, selection, and scroll they left
   (GG-12). There is no "Wonder page" you navigate to while the world unmounts behind you.
3. **A Wonder surface is a recipe of small pieces plus a pure data fold plus a closed list of
   player actions — never one big component that owns layout, paint, data-joining, and copy.**
   A "BuildWonderPanel.tsx" that fetches relics, joins slots, paints rarity, and writes its own
   refusal sentences is the defect this phase exists to catch (decisions.md GUI Lego row).
4. **Paint belongs to theme packs, not to Wonder code.** Whether a far-reaching Wonder reads as
   gold and a local one as stone, and what its half-built state looks like, is decided in a
   `wonder-scope` / `wonder-rarity` pack (`css` + `paint` hex + optional `vfx`). A hard-coded
   colour map for scope or rarity inside a piece is a Lego violation, not taste — the same rule
   that already forbids hard-coded element chips.
5. **Buy presentation, don't hand-roll it.** Icons (`lucide-react`), progress display, motion, and
   any chart of "what this Wonder earns" come from the locked stack or kit pieces already in the
   queue. A heavy first paint is fixed by splitting the chunk (GG-38), never by banning the
   library or drawing four bespoke SVGs.
6. **Every player complaint about these surfaces becomes one or more named modules, not one
   restyle.** Scope is deliberately large: a shared piece first (reused with the sibling inventory
   surfaces and the existing sector inspector), the Wonder recipe second, polish third.
7. **No engine words where the player can see them.** Scope tiers, rarity, costs, refusals, and
   construction state are all said in fiction words with authored names (GG-23, GG-62). No
   `RelicCost`, `WonderScope`, `ExistenceCapFor`, `wonder.cap-reached`, `relic.count-mismatch`,
   dotted ids, or "see definitions" anywhere on the surface.

---

## 1. Which loop this extends

**Place 5 — World stage, empire building** (`the-loops.md:113-121`): the Wonder composer and the
Wonder map/sector display are things the player does *where they stand when they run the empire* —
one camera, inspector over the map, slots and upkeep inside a held sector — on the **virtual-turn**
clock (End Turn commits orders; construction takes nights). **Place 3 — Farming, hunting, and
defending the empire** (`the-loops.md:83-99`): a Wonder is the farm verb at its most committed —
*hold this ground so hard it earns faster* — and its upkeep is a defend-verb cost (a starving
sector can lose the Wonder outright, per `wonder-effect-empire` §Design 6). It does not touch the
lawn loop, expeditions, delves, or quests; relics *arrive* from those loops (delve, expedition,
world-map assault, quest per the system ideal) but are *spent* here. `the-game.md:44` ("You keep
who you are. You lose where you were") is the stakes: a Wonder lives and dies with its ground.

---

## 2. Load-bearing principles restated inline (not links-only)

- **Stage with layers (GG-1, GG-5, GG-11).** The world map / sector inspector is the stage. The
  composer (pick Wonder + relics + slot) is a band-2 panel; the confirm that spends relics is a
  band-3 dialog (GG-22, destructive-by-consumption); refusal and result notices are band-4 toasts
  (GG-16). No new top-level route; the URL encodes stage + open layers (GG-8).
- **Player vocabulary only (GG-23) + authored names (GG-62).** Wonder names, scope/rarity
  readings, effect sentences, and refusal reasons are authored catalog copy. Refusal reason strings
  (`wonder.cap-reached`, `relic.count-mismatch`, `relic.not-reachable`,
  `build.cannot-afford-materials`) are wire tokens the fold translates — they never render raw.
- **Acknowledge instantly, paint authority on confirmation (GG-15, GG-54).** Filing a build order
  acknowledges within a frame ("order filed — resolves at End Turn"); the slot, stocks, and relics
  change only when the turn commit confirms. A reversal (order filed, then refused at commit)
  is shown and explained in player words, never silently snapped back.
- **Numbers state meaning (GG-46) + change is attributable (GG-49).** A Wonder's effect renders
  as *"this ground earns +X loam a night"* / *"every holding earns …"*, never a bare per-mille.
  Sector loam already opens the `ModifierLedger` for its upkeep rows (`SectorLoamBlock.tsx:22-26`);
  the Wonder's contribution and its upkeep must be attributable rows in the same ledger, not a
  mystery delta.
- **Choosable is comparable (GG-47).** Picking between Wonder rows, and between candidate relic
  instances, defaults to a side-by-side against the current state (this slot now vs with the
  Wonder; relics needed vs relics reachable here).
- **Disabled says why (GG-55) + four designed states (GG-17).** An unbuildable Wonder names its
  blocker (cap full, relics short, materials short, slot wrong) on the control; empty relic shelf,
  locked Wonder tier, and failed sector reads are authored states, not blank panels.
- **One home per concept (GG-9) + depth capped (GG-10).** The relic's authoritative card lives in
  exactly one place (shared with the sibling inventory ideal); the composer links into it, never
  re-implements it. Stage → sector → composer → confirm is the full depth; no fourth push for
  "what does this do" (GG-63 — readings open in-pane, not in a nested dialog).

---

## 3. What this is (player language)

**The player sentence:** *I saved up treasure from my adventures. In a sector I hold, I choose a
great work, lay the treasure I actually carry into its foundation along with stone and ironwork
from that ground's own stores, and over several nights it rises. A finished great work makes its
ground — or, for the rarest ones, my whole empire — prosper. If the work can't begin, the game
tells me plainly why: this land already holds all it can, my treasure isn't here, or the stores
are short — and nothing I own is taken when I'm refused.*

Four surfaces, all on the world stage:

1. **The great-work composer** — choose which great work, lay down the exact pieces of treasure
   it asks for, choose the open plot, see the stone-and-ironwork price beside it, confirm.
2. **The great-work display** — on the map and in the sector reading: what it is, how far its
   blessing reaches, how rare it is, what it does, and whether it is still rising (nights left)
   or complete.
3. **Plain refusals** — cap reached, treasure count wrong, treasure out of reach, stores short —
   each naming the blocker and the next action, with nothing consumed on refusal.
4. **The treasure shelf** — the treasure I own that can found a great work, and *where each piece
   sits* (with my travelling band or already stored in a sector) — shared with the sibling
   inventory surfaces, linked from the composer rather than duplicated.

No engine words appear above on purpose; §4–§5 use the precise backend names so builders can
trace every claim.

---

## 4. What already exists

### Built (works end to end — cite + proof)

| Finding | Evidence |
|---|---|
| Wonder vocabulary + catalog fields exist server-side: `WonderScope` (Sector/Empire live, World/Multiverse reserved), `WonderRarity`, `WonderEffectKind`/`WonderEffectDef`, `StructureDef.WonderScope?/WonderRarity?/WonderEffects/RelicCost`, `StructureCatalog.Validate` refusals, `WonderPolicy.ExistenceCapFor` | `gk-core/src/FusionRpg.Core/World/WonderCatalog.cs:8-123`; `gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:211-226` (fields), `:393-426` (Validate incl. `RelicCost` pairing at `:421-426`); corpus parse at `gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:42-48,154-165` |
| Build-time refusals exist with stable reason strings: `relic.count-mismatch` (admission), `relic.not-reachable` + `wonder.cap-reached` + `build.cannot-afford-materials` (resolution) | `gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs:114-116`; `gk-core/src/FusionRpg.Core/World/Movement/BuildResolver.cs:104-130` |
| Existence-cap scan exists (counts built **and under-construction**, per scope-unit) | `gk-core/src/FusionRpg.Core/World/WonderExistenceScan.cs:14-49` |
| Relic reachability gate + atomic spend exist (same turn-commit transaction as the world diff) | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WonderBuild.cs:53-117` (gate), `:119-122` (helper), `:202-227` (spend); call sites `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:535-547` |
| Sector slot display with seven player-worded row states incl. built vs under-construction with nights-to-build | `gk-web/web/fusion-rpg-web/src/stages/world/inspector/SlotRow.tsx:4-84` (states at `:4-11`, construction read at `:28-34`, sentence at `:55-59`) |
| Slot wire carries `structureId` + `constructionTurnsRemaining` as known readings, not permanent Pending | `gk-web/web/fusion-rpg-web/src/contract/adapt.ts:506-518` (+ W62 note at `:499-505`); `contract/types.ts:871-872` |
| Sector loam block with attributable upkeep ledger (the pattern Wonder rows must join) | `gk-web/web/fusion-rpg-web/src/stages/world/inspector/SectorLoamBlock.tsx:1-38`; upkeep breakdown adapter at `contract/adapt.ts:447-454` |
| Construction cost shown in player words on release-ground confirm ("N nights of building lost") | `gk-web/web/fusion-rpg-web/src/stages/world/confirms/ReleaseGroundDialog.tsx:89-91` |
| Sector inspector host exists over the world stage (the stage the composer must layer over) | `gk-web/web/fusion-rpg-web/src/stages/world/WorldStage.tsx:33,488` (`SectorInspector`); inspector blocks in `stages/world/inspector/` (`SectorInspector.tsx`, `GroundBlock.tsx`, `ActionCluster.tsx`, `NextTurnBlock.tsx`, …) |
| Relic collection layer exists with row/card/compare/paperdoll and four tabs | `gk-web/web/fusion-rpg-web/src/layers/relics/RelicsLayer.tsx:1-120` (tabs at `:39`, no-route discipline at `:89-115`) |
| gui-lego kit exists: three registries, recipe mount, folds/buses, theme packs (element/side/resource/action-category/neutral), ERM rungs, queue discipline | `docs/design/gui-lego/README.md` (piece inventory + reuse matrix); `web/.../features/gui-lego/` (folds, `pieceRegistry.ts`, `recipeRegistry.ts`, `themeRegistry.ts`, buses); `web/.../ui/gui-lego/` (`RecipeMount.tsx`, pieces, recipes); queue `docs/architecture/gui-lego/menu-refactor-queue.md` |

### Wiring gap (machinery exists but the Wonder path doesn't use it)

| Gap | The inert/underused line |
|---|---|
| Slot rows print the raw `structureId` (`SlotRow.tsx:54,58` — `"${slot.slotTypeId} — ${slot.structureId}"`) with no Wonder identity: no scope/rarity/effect reading, no themed badge, no link to what the Wonder does | `SlotRow.tsx:49-78` renders sentences from `SlotView` only; `SlotView` (`contract/types.ts:871-872`) carries no Wonder facet |
| Sector loam upkeep ledger has exactly four rows (base/garrison/development/danger); the Empire-scope Wonder upkeep term has no row and no wire field reaching the adapter | `SectorLoamBlock.tsx:22-26` + `adapt.ts:447-454` (four rows); backend term is `wonder-effect-empire` §Design 6 |
| Sector production figure carries no attributable Wonder contribution — an Empire-blessed sector's "Earns" cannot be expanded into its Wonder source | `SectorLoamBlock.tsx:17-20` reads `sector.loam.production` alone |
| Relics layer is equip-framed (equip flow, paperdoll, sockets, craft benches); nothing presents a relic as *build-founding treasure*: no instance-pick-for-a-recipe, no where-it-sits (band vs sector store) | `RelicsLayer.tsx:96-120` (Held=equip, Armoury=instances, Equipped=paperdoll, Storage="not split yet") |
| World build-order drafting carries `structureId`/`slotIndex` but no relic instance list | `stages/world/worldSelection.ts:28-46,106-118` (build order shape; `structureId` round-trips at `worldSelection.test.ts:163-173`) |
| Theme packs cover element/status-catalog/resource/side/action-category/neutral — no `wonder-scope` / `wonder-rarity` pack exists | `docs/design/gui-lego/themes/packs/` listing (this session): element-*, status-category-*, resource-*, side-*, action-category-*, bucket-*, cook-tab-*, neutral — no wonder-* |
| Closed surface buses exist per surface (derived/shield/condition/aptitudes) — no wonder-composer bus exists | `features/gui-lego/*SurfaceBus.ts` (+ `createSurfaceBus.ts`); nothing wonder-scoped |

### Real gap (no shareable piece/pack/recipe path exists yet)

| Gap | What would have to be built |
|---|---|
| No `wonder-composer` recipe (Wonder row + N relic instances + slot + material price + confirm) | New recipe + fold slice + closed bus (§5, module `wonder-composer`) |
| No Wonder identity piece (scope/rarity/effect presentation) and no scope/rarity theme packs | New piece(s) + two new theme-pack kinds (§5, module `wonder-sector-card` + packs) |
| No refusal-message catalog mapping the four wire reasons to authored player copy with next actions | New fold mapping + toast/dialog copy (§5, module `wonder-refusal`) |
| No relic-as-treasure shelf (owned instances + where each sits) shared with the sibling inventory ideal | New shared piece, co-owned with `empire-inventory-surfaces-ideal.md` (§5, module `wonder-relic-shelf`) |
| No Wonder display-name/reading catalog rows (GG-62: names and one-line effect readings must be authored, never generated from ids) | New runtime display catalog (or extension of an existing one), names TBD at spec time |
| Reserved tiers (`World`/`Multiverse` scope, `DefensePower`/`AuraGrant`/`EmpireBuff` kinds) have no presentation contract — not even a "not yet" state | Deliberately unbuilt; §9 names the non-decision |

### Built, defective (present but wrong — still a module fix, not a vibe pass)

| Finding | Why defective |
|---|---|
| `SlotRow` built-state sentence prints the raw structure id (`SlotRow.tsx:54` — `"${slot.slotTypeId} — ${slot.structureId}."`) | GG-23/GG-62 defect: an id where an authored name belongs; a Wonder row would render as its seed id. Fix inside the Wonder identity piece, not a CSS nudge. |
| `RelicsLayer` Storage tab "says so rather than faking a split" (`RelicsLayer.tsx:102`) | Honest today, but it is exactly the seam the treasure shelf must eventually replace with real where-it-sits; leaving it means the composer cannot show reachability. Module fix shared with the sibling ideal. |
| `adapt.ts` upkeep breakdown is a four-row shape (`adapt.ts:447-454`) | Any fifth (Wonder upkeep) row needs an adapter + type + ledger change together; adding the backend term without the row re-creates the W62/W63 drift class (`lib/bus/world.ts:80,112,165-166` documents the pattern). |

---

## 5. Owner bugs → module breakdown (+ shared reuse map)

**No owner bug list was filed for these surfaces** — the scope arrived as a feature brief (composer,
map/sector display, refusal messaging, relic inventory display), not as reported defects. The table
below derives one module per scoped surface instead; each row is still a module with a bucket, per
§3's required shape. If the owner later files concrete bugs, they fold into these four rows.

| # | Player surface (scope wording) | Module(s) | Bucket | Notes / file:line |
|---|---|---|---|---|
| 1 | Build-Wonder composer (pick Wonder row + N owned relic instances + sector slot, material cost display) | `wonder-composer` (recipe + fold + closed bus) + `wonder-cost-plate` (material price piece) | Real gap | Backend contract ready: `WorldCommand.RelicInstanceIds` (`WorldCommand.cs:140`), `StructureDef.RelicCost` (`StructureCatalog.cs:220-226`), admission `relic.count-mismatch` (`WorldCommandAdmission.cs:114-116`); FE order shape has no relic list (`worldSelection.ts:28-46,106-118`) |
| 2a | Wonder map/sector display — slot state machine | `wonder-sector-card` (identity + effect piece) | Wiring gap | Slot state machine exists (`SlotRow.tsx:4-37`); wire readings need Wonder facet (`SlotView`, `gk-web/web/fusion-rpg-web/src/contract/types.ts:886-895`) |
| 2b | Wonder map/sector display — scope/rarity paint | `wonder-scope-pack` / `wonder-rarity-pack` (theme packs) | Real gap | Packs don't exist (packs dir survey) |
| 3 | Existence-cap/refusal messaging (`wonder.cap-reached`, `relic.count-mismatch`, material shortfall) | `wonder-refusal` (reason→copy fold + toast/dialog recipe) | Wiring gap | All four reasons exist server-side (`BuildResolver.cs:104-130`); **zero** FE handlers (web-wide grep: no hits) |
| 4 | Relic inventory display (owned relics, where they sit) | `wonder-relic-shelf` (shared piece, owned by sibling inventory ideal — recommended, owner confirms at `/spec`) | Built, defective (equip-framed host exists; treasure framing missing) | Host: `RelicsLayer.tsx:1-120`; ownership root `rpg_item` (`RpgStore.Items.cs` per specs); reachability overlay blocked on `scoped-inventory-hierarchy` (spec'd, unbuilt — `spec-wonder-build-flow.md` §External dependency status) |

**Shared reuse map (who reuses what — prefer one piece everywhere):**

| Piece | `wonder-composer` | Wonder sector display | Sibling inventory ideal | Existing consumer |
|---|---|---|---|---|
| `tool-search` | relic picking, Wonder row picking | — | yes (shelf filter) | Derived, Creatures (queue P2) |
| `chip` (+ new wonder packs) | scope/rarity filter chips | scope/rarity badges (themed, never mute text) | relic filter chips | Derived rails; Condition `element-badge` precedent (paint SSOT, mute twin forbidden) |
| `split-inspect` | list left / reading right (GG-63) | sector reading in-pane | shelf list / card reading | Derived console |
| `scroll-region` | long relic shelf, Wonder catalog | — | dense shelf (GG-61 bounded shell) | Derived, Creatures |
| `phase-*` (loading/empty/error/pending) | empty shelf, locked tier, failed sector | locked/reserved states (GG-17) | same | All surfaces (empty **not** for zero-status precedent noted) |
| `SlotRow` (+ Wonder facet) | slot picking state | construction-progress sentence | — | World inspector (already mounted) |
| `ModifierLedger` (+ Wonder rows) | material affordability | attributable effect + upkeep rows (GG-49) | — | `SectorLoamBlock.tsx:22-26` |
| `RelicRow`/`ItemCard`/`CompareView` (relic layer) | linked candidate card (GG-9: link, don't re-implement) | — | authoritative home (GG-9) | `layers/relics/` |
| `capacity-meter` | effect magnitude hero support (density reuse) | progress meter | owned by sibling inventory ideal (recommended; owner confirms at `/spec`) | — |
| `stock-row` | relic candidate rows (density reuse) | — | owned by sibling inventory ideal (recommended; owner confirms at `/spec`) | — |
| `value-hero` / `gauge-*` | effect magnitude hero ("earns +X a night", GG-46/GG-64) | progress + effect display | — | Derived inspect |
| `surface-shell` / `PanelShell` | composer host (band-2) | inspector host (already) | shelf host | Shell standard; never fork (queue "Explicitly out") |

---

## 6. Prior art (outside repo, with sources)

| Source | What transfers | Failure mode to avoid |
|---|---|---|
| **Civilization VI — wonder race + "production salvaged" notification** ([Arqade: "Is production completely lost when losing a wonder race?"](https://gaming.stackexchange.com/questions/291148/is-production-completely-lost-when-losing-a-wonder-race)) | The loser gets a **named notification stating exactly how much production was salvaged** ("You were not able to complete the world wonder … in time. However 918 Production has been salvaged … awarded to the city of …"), and the city's production list then shows follow-on items at reduced cost. I.e. refusal/loss is a **first-class authored message with an amount and a next action**, not a silent revert. | Silent or amount-less refusal trains players to never attempt the mechanic (the same race-skip dynamic the system ideal records from CivFanatics/Humankind forums, `loam-relics-and-wonders-ideal.md` §Prior art). Our `wonder-refusal` module must name what was *not* taken (relics untouched, stores untouched) and the next action — the Civ6 salvaged-amount line is the direct precedent. |
| **Civilization VI — wonders built on tiles in gradual construction states + completion movie** ([Civilization Wiki: Wonder (Civ6)](https://civilization.fandom.com/wiki/Wonder_(Civ6)); [Civ6 Wiki: Wonder](https://civ6.fandom.com/wiki/Wonder)) | "Wonders will be **shown in gradual states of being construction** as work on it progresses. Once it is finished the construction will be **repeated with a cinematic**." Placement requirements (terrain/tech) are shown **before** construction begins; only one instance of each Wonder per game. | Two failures: (a) a construction state the map doesn't show — our under-construction slot sentence (`SlotRow.tsx:55-59`) is the seed of the gradual-state display and must grow Wonder identity rather than stay an id + count; (b) a completion that arrives as a silently changed number — a finished Wonder deserves the reward-moment treatment (GG-52: sequenced, skippable), not just a flipped row state. |
| **Civilization VI — rival wonder starts visible via visibility/diplomacy + placement blocking mod demand** ([same Wiki](https://civilization.fandom.com/wiki/Wonder_(Civ6)); [Steam Workshop: Uninterrupted Wonder Construction](https://steamcommunity.com/sharedfiles/filedetails?id=2413049462)) | "You can see wonders being built in other nations if you look around at their tiles… with high enough diplomatic visibility you will be **notified when they begin**." The mod's popularity ("Tired of constantly losing Wonders…?") proves the race notice is load-bearing UI, not chrome. | Our reserved `World`-scope tier explicitly contemplates Zomboss contesting the same Wonder (decisions SSOT). If that ever ships, the *contest notice* is a required surface from day one — never a silent cap-race the player discovers via `wonder.cap-reached` after the fact. Named here; not designed (§9). |
| **Civilization VI — wonder list with requirements + costs** ([IGN: Wonders — Civilization 6 Guide](https://www.ign.com/wikis/civilization-6/Wonders)) | Every Wonder row shows **requirement (tech/civic + tile placement) + production cost + effect** in one comparable list — the exact shape our composer catalog needs (requirement + relic count + stone/ironwork price + effect reading, GG-47 comparable by default). | A picker showing only names/flavor with costs hidden behind a second click — the composer must lead with price and requirement (GG-26 progressive disclosure inverted correctly: the three things needed to decide, details behind the select). |
| **Civilization V — National vs World Wonder split** (recorded in-repo, `loam-relics-and-wonders-ideal.md` §Prior art: [StrategyWiki](https://strategywiki.org/wiki/Sid_Meier's_Civilization_V/Wonders), CivFanatics National-Wonder + "biggest trap" threads) | The closest system match to our tier→scope gate: per-civilization empire-wide Wonders vs globally-unique ones, with the empire tier explicitly **more expensive as the empire grows** (125 + 30 × city count). | (a) **Prerequisite-lockout trap** — gating the empire tier on per-sector prerequisites instead of flat relic/material cost (system ideal's own recommendation; presentation corollary: never render a blocker the player can't act on without shrinking their empire). (b) **Production-sink trap** — the composer must keep showing the opportunity cost (nights + upkeep), not just the prize. Cited via the system ideal's own surveyed sources; not re-fetched this session. |

---

## 7. The shape — chosen vs rejected

**Chosen:** four modules (§5) composed as **recipe + pure fold + closed bus**, mounted in existing
hosts — composer as a band-2 panel over the world stage (PanelShell/`surface-shell` grammar),
sector display as facet extensions of the mounted inspector blocks (`SlotRow`, `SectorLoamBlock`/
`ModifierLedger`), refusals as band-4 toasts (+ band-3 confirm for the spend), treasure shelf as a
shared piece owned by the sibling inventory ideal (CONFIRMED by owner 2026-09-16). The composer (LOCKED: band-2 panel) reads relic candidates from the legion sheet-menu cargo sub-tab and the sector store. New theme-pack kinds (`wonder-scope`,
`wonder-rarity`) own all paint; a new display-copy catalog owns all names/readings (GG-62); a new
closed bus (e.g. `wonder-composer.*`: `search.set`, `wonder.select`, `relic.toggle`,
`slot.select`, `confirm`, `retry`) owns all actions. Authoring order per idea-ui §1: queue row →
piece index → recipe → fold + bus → themeRefs → HTML drafts → owner accept → React mount +
landmark tests. New surfaces enter `menu-refactor-queue.md` as their own rows (one surface per
stream — composer first, sector display second; never both in one stream).

**Rejected:**

| Rejected shape | Why |
|---|---|
| **One CSS PR on the inspector** ("style the slot rows, ship it") | Fails the whole inventory: no composer, no refusal copy, no shelf, no packs. The Condition-glance incident (idea-ui §8) is the precedent — a tab treated as a CSS pass while theme packs sat unused and modules stayed missing. |
| **A god `BuildWonderPanel.tsx`** (hypothetical — rejected, never built) owning layout + fetch + joins + paint + copy | The exact defect the GUI Lego decision bans (`decisions.md` GUI Lego row). It would duplicate the relic card (GG-9), hard-code scope paint (Lego violation), and bypass the queue. |
| **A new top-level "Wonders" route / sidebar entry** | GG-1/GG-7 violation: replaces the stage instead of layering over it; unreachable mid-flow without losing the sector. The relic layer already documents the correct discipline ("No route, no stage, no sibling screen", `RelicsLayer.tsx:89`). |
| **Raw reason strings / ids rendered to the player** (`wonder.cap-reached` as toast text, structure ids as names) | GG-23/GG-62 violation; `SlotRow.tsx:54` already exhibits the mild form. The fold translates every token. |
| **A second palette / second shell / second density ladder** | GG-29 + queue "Explicitly out": no forked PanelShell, no parallel kit beside ERM/pieces, no hard-coded hex in feature code. |
| **Banning lucide/recharts/motion for entry-chunk anxiety** | GG-38 (amended): split the chunk; buy the library. The effect hero and progress display use the locked stack. |

---

## 8. Tunables — catalog / theme pack / structural CSS called out

| Tunable | Home | Notes |
|---|---|---|
| Wonder display names, one-line effect readings, scope/rarity readings, refusal copy + next actions | **New runtime display catalog** (GG-62 authored lexicon; T7/T8 sibling of number files — never mixed into balance numbers) | Every Wonder row, both scopes, all four refusal reasons need authored rows before React mounts; unknown ids fall to a designed placeholder, never id-words. Spec-time decision: new file vs extending an existing display catalog. |
| Scope paint (`wonder-scope`: Sector vs Empire + reserved), rarity paint (`wonder-rarity`: Common vs Unique), construction-state `vfx` | **New theme packs** `wonder-scope-*` / `wonder-rarity-*` (`css` + `paint` hex + optional `vfx`; GG-32 reduced-motion) | Pieces declare slots only. Reserved tiers get a "not yet" treatment in the pack contract, not an invented look per surface. Design SSOT; re-copy to `features/gui-lego/themes/` per README §FE sync. |
| Refusal thresholds text (cap counts: "2 of 3 standing stones raised") | Display catalog (above) + fold reading `WonderPolicy` numbers | LOCKED by owner: show live counts — the fold MUST render them, not either-way |
| Recipe slot trees (composer layout, sector card slots, toast placement) | **Recipe JSON** (`docs/design/gui-lego/recipes/wonder-*.json`) | Changing IA = editing the recipe, not the TSX (composition grammar). Structural CSS (grid/flex areas, 720px-floor bounds per GG-36/GG-61, internal scroll) is called out per recipe, not per piece. |
| Backend numbers (RelicCost, existence caps, upkeep rate, ValueMilli) | Owned by the four backend specs (`gk-core/data/tuning/loam-relics-wonders.v1.json`, seed corpus) | **Not this doc's to tune.** The fold formats them (GG-46 unit families); it never invents them. |

No progression ceiling is introduced by any surface choice: caps render as data (`ExistenceCapFor`
readings), never as painted-full gauges on uncapped magnitudes (GG-64).

---

## 9. What this deliberately does not decide

1. **Backend behavior or numbers** — recipe shape details (`RelicCost` semantics, SUM rule,
   upkeep rate, cap values) are locked in the four module specs + decisions SSOT; this doc only
   presents them.
2. **Relic identity/tag matching** — v1 recipe is generic-by-count (`spec-wonder-build-flow.md`
   §recipe-shape decision); any "this work needs treasure of theme X" picker is a future wave.
3. **Sector/legion reachability presentation source** — the where-it-sits truth depends on
   `scoped-inventory-hierarchy` (spec'd, unbuilt); this doc assumes the overlay API the sibling
   ideal will specify and designs the shelf's reading contract, not its backend join.
4. **Reserved tiers' presentation** (`World`/`Multiverse`, `DefensePower`/`AuraGrant`/`EmpireBuff`)
    — LOCKED by owner: locked-with-reason teasers (GG-17/GG-44); the packs carry the "not yet"
    slot per §8.
5. **Contest/race surfaces** (Zomboss competing for the same Wonder) — named as prior-art debt
   (§6), never designed.
6. **Queue placement and build order** — which module specs first, and whether composer or sector
   display enters the queue first, is for `/spec` + owner accept, not this phase.
7. **Backend reads these surfaces need but don't have yet** — reachable-first picking needs a
    REST reachability read (only `ListClaimableCachesUnlocked` in-process exists); live cap counts
    need `WonderScope`/`WonderRarity`/`RelicCost`/cap fields on the catalog/slot wire
    (`WorldStructureDto`/`SlotView` carry none today); locked teasers need scope metadata the
    catalog exposes. These are plan Tasks 4A.3/4B dependencies, not this doc's design.
8. **React implementation, file layout, or component APIs** — no specs, plans, or code from this
    phase (§6 hand-off rules).

---

## 10. Open questions (owner decisions only — Q1-Q4 ANSWERED, see Owner resolutions; Q5-Q7 still open)

1. **Composer host:** ~~band-2 panel vs take-over?~~ ANSWERED: panel — locked (§7 updated).
2. **Relic picking:** ~~reachable-here vs full shelf?~~ ANSWERED: reachable-first (full shelf one
    disclosure away) — locked; "reachable here" spans the legion sheet cargo tab + sector store
    per the locked sibling direction.
3. **Cap visibility:** ~~live counts vs refusal-only?~~ ANSWERED: show counts — locked (§8 updated).
4. **Reserved tiers:** ~~hide vs locked-with-reason?~~ ANSWERED: locked teasers — locked
    (§8 packs carry the "not yet" slot; §9.4 updated).
5. **Effect readings for reserved kinds:** the three named-but-unregistered effect kinds get
   display-catalog rows now (so the vocabulary reads complete) or only when their wave ships?
   Recommendation: now for scope/rarity, later for effect kinds — effects imply promises.
6. **Completion moment:** finished Wonder gets a sequenced reward beat (GG-52, Civ6 movie
   precedent) or a toast + updated row? Recommendation: toast + ledger update for Sector scope;
   authored beat for the first Empire-scope completion (once, skippable).
7. **Sibling split:** does `wonder-relic-shelf` live in this program's spec set with the inventory
    ideal as consumer, or vice versa? RECOMMENDED: the sibling inventory ideal owns `stock-row` +
    `capacity-meter` + the relic shelf (it defined them first); this program consumes by name
    (GG-9). CONFIRMED by owner 2026-09-16 — both docs name the inventory program as owner.

---

## 11. The real question

**Shape, not feasibility.** The backend contract is built and the kit (recipes, folds, buses,
packs, hosts) is proven — nothing here asks "can we show this." The question is **which modules
exist and who owns the shared ones**: is the four-module split above (§5: composer, sector card +
packs, refusal, shared shelf) the right cut, does the shelf belong to this program or the sibling
inventory program, and do two new theme-pack kinds plus one display-copy catalog cover every
painted and spoken word these surfaces will ever need? Answer that, and `/spec` can proceed
surface by surface through the queue.

## Owner resolutions (2026-09-15 — owner's selected labels, quoted verbatim)

- Composer host: "Panel (Recommended)".
- Relic picking: "Reachable-first (Recommended)".
- Cap counts: "Show counts (Recommended)".
- Reserved tiers: "Locked teasers".

## Hand-off checklist (this document)

```
[x] Subsystems: world-stage sector/legion presentation (FE Lego), Wonder backend contract (read-only refs). No Status/ActorHub/Combat touched.
[x] Session boundary: worktree empire-development-20260915-b7e2 only; main checkout untouched.
[x] Checked decisions.md: GUI Lego row; no "wonder surfaces" lock — greenfield confirmed.
[x] Every factual claim cites file:line (§4 tables); verified against code in-session.
[x] Nothing contradicts a §2 invariant (no second shell/kit/palette; no painted-full gauges on uncapped magnitudes).
[x] No population-count or generated-text pins; no seed edits proposed (display catalog + packs are authored content).
[x] Idea phase runs no suite — no test movement claimed.
```

Queue: `menu-refactor-queue.md` gains rows for composer first, sector display second (one surface per stream) when the program starts. Plans (at `/spec`): `tasks/empire-wonder-surfaces-plan.md` / `tasks/empire-wonder-surfaces-todo.md`.

## Hand-off

- Stop at this ideal. **No specs, plans, or code from this phase.**
- Next step after owner answers §10: `/spec` → capability map + per-module specs under
  `docs/architecture/empire-wonder-surfaces/`, plans in
  `tasks/empire-wonder-surfaces-plan.md` / `tasks/empire-wonder-surfaces-todo.md`.
- Queue: `menu-refactor-queue.md` gains rows for composer first, sector display second (one surface
  per stream) when the program starts.
