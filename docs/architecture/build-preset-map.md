# Capability map: build-preset

**Status: spec phase, written 2026-09-18. Not yet reviewed by the owner. No build authorized.**
**Built after [`empire-progression`](empire-progression-map.md)**, by owner ruling R5
([spec-rulings-2026-09-18.md](spec-rulings-2026-09-18.md)): *"A new sub-program, specced now, built after
`empire-progression`."* Module specs live in [build-preset/](build-preset/), one per module id.

**Program id: `build-preset`**, a sub-program of `empire-progression`. It is the **"save the whole lean"
layer over layers that already exist**: a named, player-owned bundle of *references* to existing pieces
(patron, gear, aptitude presets, who you field, equipped skills), applied by calling each piece's own
existing write gate at that gate's own price. **It is not a stat layer, it is not a second aptitude
preset library, and it adds no price of its own.**

**Loop (the-loops.md):** Spine C "Item collection and progression", whose Vision line names this exactly:
*"Build presets (Vision): save a synergy loadout — patron, relics, aptitudes, who you field — so a fire lean
is something you keep, not five independent clicks"* (`docs/guide/the-loops.md:55`), hanging on
*"Item collection · level up and power"* (`docs/guide/the-loops.md:164`). No new loop, currency or gate.
The empire-progression ideal records the same gap as R6: *"Nothing combines patron + relics + aptitudes +
field list"* (`docs/architecture/empire-progression-ideal.md:200-202`).

---

## What the gate reading found in code (2026-09-18)

Every row was read in code this session. The pieces exist; the bundle does not.

| Fact | Evidence |
|---|---|
| An **aptitude** preset library ships end to end: 3 tables, CRUD, active binding, transactional activate | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AptitudePresets.cs:55-88,184-256,341-430`; routes `gk-core/src/FusionRpg.Server/AptitudePresetEndpoints.cs:24-240` |
| Activating an aptitude preset **prices only the species scope** today, through the species respec path; commander and unique scopes write the allocation free. **Ruling R18 prices both** (`empire-progression` [`specimen-respec-price`](empire-progression/spec-specimen-respec-price.md)) | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AptitudePresets.cs:374-391` (free today) and `:392-423` (calls `TryRespecSpeciesUnlocked` at `:410-411`) |
| By-hand commander and unique allocation are also free today; R18 prices them the same way | `gk-core/src/FusionRpg.Server/AptitudeEndpoints.cs:29-55,64-94` |
| The one respec price function | `gk-core/src/FusionRpg.Core/Stats/Aptitudes/RespecPolicy.cs:36-48`. `empire-progression` `specimen-respec-price` re-types it to take its parameter set and adds the one `RespecPolicy.Quote`; `respec-free-counter` feeds that quote the empire's earned free respec stock ([spec](empire-progression/spec-respec-free-counter.md)) |
| An **item** loadout library exists as a store and a pure conflict report, with **zero production callers** and no HTTP route | store `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Items.cs:131-147,431,459,489,576`; report `gk-core/src/FusionRpg.Core/Items/LoadoutReport.cs:40-101`; claimed by `docs/architecture/item/spec-armoury.md:103-121`, whose route row says *"apply lands with module 4"* (`:220`) |
| Two equip flows write one assignment table: rolled copies through `ItemEquipService`, catalog relics (`stock`) through the relic wire | `gk-core/src/FusionRpg.Server/ItemEquipEndpoints.cs:28-62,110,209`; relic wire `gk-core/src/FusionRpg.Server/UniqueActorService.cs:54,82` |
| **Patron** designation: first free, each switch costs `switchCostSouls`; the patron must be bound and deployable | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Patron.cs:17-73` (`:38-40`, `:49-56`); `gk-core/src/FusionRpg.Core/Creatures/Patron/PatronPolicy.cs:35` |
| The patron route does its runtime refresh, broadcasts and injector push **inline in the endpoint lambda** | `gk-core/src/FusionRpg.Server/PatronEndpoints.cs:26-62` |
| **Who you field** = the contract-bound set: bind costs one day of upkeep and respects capacity; release is free and refuses a deployed, expedition, patron or warden creature | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Contracts.cs:232-273,333-366`; `gk-core/src/FusionRpg.Core/Creatures/Contracts/ContractPolicy.cs:171` |
| **Equipped skills**: a 5-slot action loadout, player scope only on HTTP | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Loadouts.cs:41,87,116`; `gk-core/src/FusionRpg.Server/LoadoutEndpoints.cs:43-70`; `gk-core/src/FusionRpg.Core/Actions/Loadout/LoadoutSet.cs:43` |
| The player-facing label **"Build presets" is already taken** by the aptitude preset console | `gk-web/web/fusion-rpg-web/src/features/aptitudes/AptitudePresetConsoleHost.tsx:384`; `gk-web/web/fusion-rpg-web/src/features/gui-lego/foldAptitudesSurfaceVm.ts:205,262` |
| The guide page still says Vision | `docs/guide/mechanisms/build-presets.md:3` |

---

## Modules

Stable kebab-case ids, chosen once.

| # | Module id | Responsibility | Depends on | Wave |
|---|---|---|---|---|
| 1 | `gate-services` | Lift the four write gates whose logic lives in endpoint lambdas into named services, behaviour byte-identical: `PatronService.Set`, `AptitudePresetActivation.Activate` (+ a read-only `Preview`), `ContractService.Bind/Release`, `ActionLoadoutService.Set`. The endpoints become thin callers. Without this an applier would either skip the runtime refresh and injector push (a weaker second path) or copy them | external `specimen-respec-price`, `respec-free-counter` (for `Preview` and the payment choice) | **A** |
| 2 | `item-loadout-apply` | The armoury loadout library's HTTP surface and its **apply**, exactly as `spec-armoury.md` claimed it: refuse on `LoadoutConflict` by default, `force` reports what it stripped, each entry routed to the flow that owns its ref kind | — (fills the item program's claimed, unbuilt surface) | **A** |
| 3 | `preset-store` | `rpg_build_preset` + `rpg_build_preset_piece` (new): a player-owned library of references, a closed piece vocabulary, validate-on-read with `Missing` markers, soft max from `build-preset.v1.json` | — | **A** |
| 4 | `piece-appliers` | One applier per piece kind behind one interface: `Preview` (read-only: refusal or price quote) and `Apply` (delegates to the gate from module 1 or 2, or to the existing store gate). Prices come from the gate's own policy: `RespecPolicy.Quote` (every aptitude scope), `PatronPolicy.SwitchCostSouls`, `ContractPolicy.UpkeepPerDay` | `gate-services`, `item-loadout-apply`, `preset-store`; external `specimen-respec-price`, `respec-free-counter` | **B** |
| 5 | `apply-orchestrator` | `POST …/preview` and `POST …/apply`: the structural piece order, whole-plan refusal before any write, summed price per resource (souls and free empire respecs), the player's spend-or-pay choice per species target carried from preview to apply, derived correlation ids so a retried apply converges without double-charging, one per-piece outcome report | `piece-appliers` | **B** |
| 6 | `capture-current` | "Save what I have now": snapshot the current patron, bound set, skill loadout, gear and aptitude allocations into a new build preset, writing the aptitude and gear parts into their **own** libraries and referencing them | `preset-store`, `item-loadout-apply` | **B** |
| 7 | `preset-surface` | The FE contract only: recipe + pure fold + closed bus + host-to-API commands. Layout waits on an `/idea-ui` pass | `apply-orchestrator`, `capture-current`; `/idea-ui` pass | **C** |

**Not a module here, by ownership:**

- **The aptitude preset library, its activate transaction, and the assign ladder.** `aptitude-sheet` owns
  the library; `empire-progression` `assign-ladder` owns which rule fills a draft. A build preset only
  points at an aptitude preset id.
- **Respec pricing.** `empire-progression` owns it: `specimen-respec-price` owns `RespecPolicy.PriceOf`,
  `Quote` and the unique/commander gate; `respec-free-counter` owns the earned free empire respec stock and
  the species spend-or-pay choice. Applying a preset reaches them only through the activate gate, where a
  by-hand change reaches them.
- **The commander seat** (which creature leads). Not in the Vision line's four pieces, and
  `empire-progression` `commander-roster` is still changing its shape. Adding it later is a reviewed
  change to the closed piece vocabulary (D2).
- **A delve party or a legion lineup.** Both are chosen when that mode starts; neither is a persistent
  set to restore. See D3.

## Dependencies on `empire-progression`

| `empire-progression` module | What build-preset needs from it | Hard or order |
|---|---|---|
| `specimen-respec-price` | `RespecPolicy.Quote(tuning, effectiveCount, freeStock)` (new there) and the priced commander/unique gate `TryReallocateUnlocked` (new there), so a preview shows what a commander or specimen re-allocation charges by hand | **Hard.** `piece-appliers` preview and the activate gate call it |
| `respec-free-counter` (after `empire-level`) | The species spend-or-pay choice (`payWith`) and the empire's free respec stock, read by `QuoteSpeciesRespecUnlocked` (new there), so a preview shows both options for a species target | **Hard.** `piece-appliers` and `apply-orchestrator` carry the choice |
| `assign-ladder` | The `active-preset` rung reads the binding that activation writes (`RpgStore.AptitudePresets.cs:370`). The FE's duplicate auto-assign is retired there, so the preset surface never inherits it | Order |
| `default-build` | `systemCopy` presets get a producer; a build preset may reference one like any other aptitude preset | Order |
| `commander-roster` (and `solid-enforcement` `commander-identity`, `save-identity` per R3) | The actor-reference grammar a preset stores for "commander" targets. Today a commander target is `CommanderIds`' stable id for Dave (`gk-core/src/FusionRpg.Server/ItemEquipEndpoints.cs:304-320`) and the allocation key `player:{id}` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AptitudePresets.cs:432`). Building before those land would bake the shape R3 is retiring | **Hard** for `preset-store`'s target column |

## Build order

```
(empire-progression complete through wave D's empire-level and respec-free-counter: assign-ladder,
 default-build, specimen-respec-price, commander-roster, empire-level, respec-free-counter;
 solid-enforcement commander-identity and save-identity)

Wave A  gate-services          (independent; pure refactor)
        item-loadout-apply     (independent; item program's claimed surface)
        preset-store           (independent)

Wave B  piece-appliers ─► apply-orchestrator
        capture-current        (after preset-store + item-loadout-apply)

Wave C  preset-surface         (after its /idea-ui pass)
```

**Why this order.** The appliers cannot exist before the gates they call are callable without their
endpoints (module 1) and before gear has an apply (module 2); otherwise the applier becomes the second
implementation. The orchestrator is only order and bookkeeping over appliers. Capture needs the store and
the item library's write surface. The surface is last because its layout is an `/idea-ui` output.

## Checkpoints

| Checkpoint | Proves | After |
|---|---|---|
| **CP0 — review** | Owner reviews this map and D1–D6. Its one OWNER question was closed by ruling R18 | before any build |
| **CP1 — the gates are callable** | Patron set, aptitude activate and contract bind/release behave byte-identically through their services (existing endpoint tests unchanged and green); an item loadout can be saved, listed and applied over HTTP with a named conflict refusal | modules 1–2 |
| **CP2 — a preset applies** | A build preset naming a patron, a field, an aptitude preset, gear and skills previews with the exact price the by-hand clicks would cost (a species target shows both "spend a free respec" and the soul price, and applies the player's pick; a commander or specimen target that takes points back shows its soul price), applies, and a retry with the same correlation id charges nothing more; each layer is read back through its own normal read path, never the preset's response | modules 3–5 |
| **CP3 — keep what you have** | Capture then apply on a changed build restores the captured build; the aptitude and gear parts are rows in their own libraries | module 6 |
| **CP4 — the player can reach it** | Playwright: create, capture, preview (prices and refusals visible by name), apply | module 7 |

## Decisions this map records

**D1. A build preset is a composite of references, never a copy.** Its aptitude piece stores an
`rpg_aptitude_preset.preset_id`, its gear piece an `rpg_item_loadout.loadout_id`. Copying their rows
would make a second aptitude library and a second gear library, each with its own validation, soft max
and drift (S in SOLID). Validate-on-read reports a deleted reference as `Missing`, the armoury's own rule
(`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Items.cs:474-488`).

**D2. The piece vocabulary is closed: `Patron`, `Field`, `Aptitudes`, `Gear`, `Skills`.** Four are the
Vision line's; `Skills` is the equipped action loadout, which is how an aura or a fire skill is part of a
"fire lean" (`gk-core/src/FusionRpg.Server/LoadoutEndpoints.cs:60-63`). A sixth kind is a reviewed change with a
pinned-membership test, like any closed enum here.

**D3. "Who you field" is the contract-bound set.** It is the only persistent, player-chosen "who serves"
set: binding decides who is deployable (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Patron.cs:38-40` reads it for
the patron), and it carries a real price and capacity (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Contracts.cs:257-268`).
A delve party and a legion are chosen at mode start from that set. A field piece is an **exact** set:
apply binds the missing members and releases the extra ones. Release is free and keeps loyalty
(`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Contracts.cs:329-330`), so an exact set costs nothing a by-hand
release would not.

**D4. The preset adds no price, and removes none.** The apply price is the sum of what the same changes
cost by hand, computed by the same functions. That is the guardrail, stated as a contract test in
`piece-appliers`. Under ruling R18 it reads, per aptitude target:

| Target scope | By hand (R18) | By preset |
|---|---|---|
| **Species** (the empire respec) | Priced, but the player chooses per respec: spend one earned free empire respec, or pay `RespecPolicy.PriceOf` in souls (`respec-free-counter`) | Preview shows **both** options for every species target that would be a respec, with the stock. Apply takes the player's choice per target; a target left unchosen while a free respec exists refuses by name. The preset never picks for the player |
| **Commander** pool | Taking points back is priced in souls; adding unspent points is free (`specimen-respec-price`) | Same function, same price. Never draws on free empire respecs |
| **Unique creature** (specimen) | Same as commander, on its own counter | Same function, same price |

All three reach `RespecPolicy.Quote` through `TryActivateAptitudePreset`, the one place a by-hand
preset activation reaches it.

**D5. Apply is convergent, not one transaction.** The gates own separate transactions and two of them
live in Server services with runtime side effects (`gk-core/src/FusionRpg.Server/ItemEquipEndpoints.cs:460-485`,
`gk-core/src/FusionRpg.Server/PatronEndpoints.cs:43-58`). Folding them into one SQL transaction would mean moving
equip and patron logic into a new composite writer, which is the parallel path this program exists not
to build. Instead: a read-only preview refuses the whole apply if any piece would refuse or the summed
price exceeds the balance; apply re-checks, runs the pieces in a structural order, and passes each gate
a correlation id derived from the apply's own, so a retry after an interrupted apply converges and
never charges twice. A partly applied build is reported piece by piece, never hidden.

**D6. Not a stat layer.** Answered in full below. A preset writes rows that existing layers already
read; it contributes no `DerivedModifier`, owns no SourceId, and never reads Hub output to decide
anything.

## The actor-layer five questions (`actor-layer-compose-ideal.md` §"What a new feature owes this stack")

A preset changes actor numbers, but only by changing what existing layers hold. So it is **not a layer**,
and the five answers are about the layers it writes to.

| Question | Answer |
|---|---|
| 1. Which layer? | **None new.** It writes the inputs of: commander allocation (Commander scope, applied side-wide by ruling R4, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:573-590`; resolved on its own points by ruling R16; priced on a take-back, R18); **2a** specimen allocation (UniqueCreature scope; priced on a take-back, R18); **2b** empire species allocation (species scope, priced, with the earned free respec as the player's alternative, R18); **3** item equipment (`rpg_item_assignment`); **6** patron aura (`rpg_patron`); and the action loadout, which is how an equipped aura action reaches `AuraRuntime` |
| 2. Scope? | The library is **per player**. Each write keeps its target layer's own scope; a preset never widens one (a specimen's gear stays that specimen's) |
| 3. Lifetime? | The library is persistent and player-mutable. An apply is a one-shot write into each layer's own table; the preset holds nothing live |
| 4. Carrier? | **None of its own.** Each layer's existing carrier (allocation seams into Hub, `EquippedBoundAtoms`, `patron.aura`) is unchanged |
| 5. Provenance? | Contributions keep their layer's own SourceIds. A sheet explains a number by its layer, never by "preset". A guard test asserts the build-preset assemblies reference no `DerivedModifier`, `ActorHub` or `ContributionSourceIds` type |

## Seedsmith and generator coverage

| Module | Generator involved | Why none |
|---|---|---|
| all seven | **None** | A build preset is player-authored runtime state over player-owned rows. There is no seed shape, no corpus and no population to generate. A "suggested build preset" would compose `default-build`'s `systemCopy` producer, not a new generator |

## Open questions (OWNER)

None open. The one question (should commander and specimen re-allocation be priced?) was answered by
ruling R18 on 2026-09-18; see "Rulings applied".

## Rulings applied 2026-09-18

Source: [spec-rulings-2026-09-18.md](spec-rulings-2026-09-18.md) (binding, not reopened here).

| Was | Ruling | What changed in this program |
|---|---|---|
| **Q1** — price commander and specimen re-allocation? | **R18, with the owner's correction: yes.** A unique creature always pays to respec, and *"commander is unique creature, it pays for respec"*. The empire (species) respec is priced, its free respecs are earned one grant per empire level, and at each empire respec the player chooses to spend a free respec or pay. Presets charge exactly the by-hand price | D4 rewritten per scope. `piece-appliers` prices commander and unique targets through `specimen-respec-price`'s gate and quote, and carries the species spend-or-pay choice. `apply-orchestrator` sums free empire respecs as their own resource and takes the choice on apply. `gate-services` passes the choice through activation. `preset-surface` shows both options and never picks |
| *(none here)* — which level earns free respecs? | **R19: a new empire-level track** (`empire-progression` `empire-level`) | Nothing built here; the stock the preview reads is filled by it |

## Contradictions found while specifying

| # | Between | Finding | Resolution |
|---|---|---|---|
| X1 | the-loops ↔ FE | "Build presets" names the synergy loadout in the product-vision SSOT (`docs/guide/the-loops.md:55`), but the shipped aptitude preset console is titled "Build presets" (`gk-web/web/fusion-rpg-web/src/features/aptitudes/AptitudePresetConsoleHost.tsx:384`) | The guide wins (DESIGN-GATE product-vision row). `preset-surface` renames the aptitude console's label to "Aptitude presets" in its `/idea-ui` pass |
| X2 | guide ↔ code | `build-presets.md` says *"Can I save presets now? No — Vision"* while aptitude presets ship (already noted as the ideal's R6) | Rewritten when CP4 passes, not before (a guide describes what ships) |
| X3 | `spec-armoury.md` ↔ code | The armoury spec plans `GET · PUT · DELETE /api/items/loadouts…` and an apply "with module 4" (`docs/architecture/item/spec-armoury.md:220`). Module 4's equip executor shipped (`gk-core/src/FusionRpg.Server/ItemEquipEndpoints.cs:63`), yet no loadout route or apply exists | `item-loadout-apply` builds exactly the armoury's contract. If the item program lands it first, the module closes as consumed |
| X4 | loadout table ↔ assignment table | A loadout entry pins a copy as `ref_kind = "item"`; an assignment pins the same copy as `"rolled"` (`gk-core/src/FusionRpg.Core/Items/EquipProjector.cs:16-27`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Items.cs:533-539`) | `item-loadout-apply` maps them in one named function; never a second spelling |
| X6 | `spec-armoury.md` ↔ code | G-C, *"loadout membership implies lock"* (`docs/architecture/item/spec-armoury.md:129`), is claimed as shipping with the library, but no salvage path reads `rpg_item_loadout_entry` (the table is read only inside `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Items.cs`) | Not built here: it is a salvage guard, the item program's. Recorded because `capture-current` creates item loadouts, and once G-C lands every captured piece becomes salvage-locked, which is the armoury's intent |
| X5 | activate gate ↔ its callers | Activate's budget resolve, materialize and check live in the endpoint lambda (`gk-core/src/FusionRpg.Server/AptitudePresetEndpoints.cs:172-240,295-331`), so the only way to activate is an HTTP call | `gate-services` lifts it into `AptitudePresetActivation`, one implementation for both callers |

## Module specs

| Module | Spec |
|---|---|
| `gate-services` | [spec-gate-services.md](build-preset/spec-gate-services.md) |
| `item-loadout-apply` | [spec-item-loadout-apply.md](build-preset/spec-item-loadout-apply.md) |
| `preset-store` | [spec-preset-store.md](build-preset/spec-preset-store.md) |
| `piece-appliers` | [spec-piece-appliers.md](build-preset/spec-piece-appliers.md) |
| `apply-orchestrator` | [spec-apply-orchestrator.md](build-preset/spec-apply-orchestrator.md) |
| `capture-current` | [spec-capture-current.md](build-preset/spec-capture-current.md) |
| `preset-surface` | [spec-preset-surface.md](build-preset/spec-preset-surface.md) |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: aptitude presets and allocation, respec pricing, item loadouts and equip, patron,
    contracts (binding), action loadout, player menus (GUI Lego), tunables, data/SQL.
[x] Session boundary recorded: tasks/sessions/build-preset-spec-20260918.json (docs only). R18/R19
    applied by tasks/sessions/respec-rulings-20260918.json.
    session-boundary-check reports one crossing on this map's paths: progression-rulings-20260918
    (active) also claims empire-progression-map.md. This session's only edit there is one appended
    reconciliation line; named in the hand-off.
[x] Read this session: DESIGN-GATE §1 rows (anything, product vision, stats, actor layer, tunables,
    data/SQL, creature vocabulary, UI, player menus) and §5; the-loops; guide build-presets page;
    empire-progression-map and its respec-free-counter, assign-ladder and default-build specs;
    empire-progression-ideal R6 and §6; actor-layer-compose-ideal layer stack and "What a new feature
    owes"; decisions.md Actor layer stack and GUI Lego rows; creature-system-map vocabulary;
    gui-lego-ideal principles and bans; idea-ui-phase §0; tunables-ssot T4-T6 and §7.1;
    spec-armoury loadout section; software-architecture §6.
[x] decisions.md checked: no row covers a composite preset. No row owed: this program adds no layer,
    no new vocabulary outside its own closed piece enum, and no architecture lock.
[x] Every factual claim cites file:line; unbuilt files carry "(new)".
[x] audit-doc-citations run on every file written (result in the hand-off).
[x] Claims verified against code, not comments (X3-X5 are where the docs and code disagreed).
[x] Surrounding sections read for every rule quoted.
[ ] Tested constraints: none run. Docs-only session. "Byte-identical" for gate-services is a
    prediction that its first task proves with the existing endpoint tests.
[x] No §2 invariant contradicted.
[x] Corrections propagated to the map, specs, testing and boundaries sections.
[x] No population pin: tests assert the piece enum (closed, 5, reason stated), price equality and
    round-trips, never counts of presets, items or creatures.
[x] Edge-refreshed caches: none introduced. Validate-on-read recomputes every read.
[x] Order-independence: the piece order is structural and justified (patron needs its creature
    bound; the old patron cannot be released while it is patron); save order of pieces is irrelevant
    and tested.
[x] ActorHub: no contribution, no read of Hub to decide a number (D6).
[x] No SOLID-violating parallel path: D1, D5, X3, X5 are the places one was avoided.
```
