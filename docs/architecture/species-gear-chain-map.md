# Species-gear chain — capability map

**Status:** capability map, 2026-09-13. **19 modules specced; audited and corrected 2026-09-13.**
Awaiting owner approval. No build authorized. ⚠ *2026-09-18: superseded — 20 modules; the plan was
approved and 13 modules have shipped in part or whole (§ Strengthen pass, item 1).*

⚠ **Read § Corrections before the module table.** A five-agent audit found ~35 defects across the
map and the specs; the module rows, build order and exclusion lists below are the **post-audit**
versions.

> **Amended 2026-09-18 — six owner rulings reconciled** (§ Owner rulings 2026-09-17/18, below):
> R-SS1–R-SS3 (`species-selection-ideal.md`), R-SC1–R-SC2 (`species-craft-ideal.md`), R-G1
> (`gear-climb-ideal.md`). One ruling needed a module no row covered — **`craft-assurance`**, R-G1's
> boss-farmed consumable layer — so the initiative is now **20 modules**. The rest amend existing specs.
> **Build state is not this header's to state:** T1–T21, T18b, T35, T36 have shipped (`git log --grep
> species-gear-chain`); the plan's todo checkboxes have not been ticked to match.

> **Amended 2026-09-18 — rulings R9 and R10** ([spec-rulings-2026-09-18.md](spec-rulings-2026-09-18.md)):
> **R9** removes the general trophy layer (species 2, family 8, general 0) — `species-materials`,
> `creature-drop-tables`; **R10** decides that *protect* does not cover a repair's destroy chance —
> `craft-assurance`. Both close the OWNER questions those specs carried. § Owner rulings below.

> **Strengthen pass 2026-09-18** (adversarial audit, § Strengthen pass at the end): **build state stated
> per module** (13 of 20 modules fully or partly shipped, so their specs' *"What exists today"* sections
> are the **pre-build record** and each built spec now opens with a build-state banner and its drifted
> citations corrected); **§ Corrections #11 reversed** — a tuning revision is a new `v{n+1}` file
> published through `gk-core/tools/tuning/publish.py` (tunables-ssot T4), never an in-place `version` bump, with
> the cross-program publish order in § Tuning revisions; two new dependency edges; one OWNER question.

> **Amended 2026-09-18 — ruling R22** (session `rulings-r20-r24-20260918`): a multi-family species
> drops **one family trophy per kill, equal odds**, on a named seeded stream, and counts as a member of
> **every** listed family for recipes — closes OWNER question O1. R20 is cross-referenced in
> `spec-gem-tier.md` and § Tuning revisions (`forge-gem` repriced only by strain-splice-host's report).

**Initiative id:** `species-gear-chain`
**Module spec path:** `docs/architecture/species-gear-chain/spec-<module-id>.md`
**Plan / tasks:** `tasks/species-gear-chain-plan.md` / `tasks/species-gear-chain-todo.md`

---

## Why this initiative exists, and why it is not called `tier-system`

[tier-system-ideal.md](tier-system-ideal.md) § DISPOSITION **withdrew `tier-system` as a program**:
`gameplay-tiers-ideal.md:156` already closed the graduation list — *"never by reopening sealed
ideals"* — and the surviving work belongs to programs that already exist. That withdrawal stands.

What the audit found instead (§ AUDIT A10, the reframe) is a **single dependency spine** that four
separate ideal docs each describe one segment of:

> **A player must be able to reach a species → the species must yield something → that something must
> feed a craft that climbs.**

Today the spine is severed at the first link: **a player meets 10 of 904 creatures.** Everything
species-keyed downstream — 844 species-themed set entries, species materials, species-shaped craft
costs — is decoration until that is fixed.

This map is therefore **an index over four approved ideals, not a new program**. Every module below
names the **existing program that owns it**; the module id is the stable handle downstream plans and
`/build` select by. If the owner prefers these specs filed directly under the owning programs'
directories instead of a shared one, that is a one-line change to this map and to no module content.

**Source ideals, all four owner-reviewed 2026-09-13:**

| Ideal | Covers |
|---|---|
| [tier-system-ideal.md](tier-system-ideal.md) | The propagation contract (T-1…T-5), the six edges E1–E6, the consistency pass, D1–D8 |
| [species-selection-ideal.md](species-selection-ideal.md) | The three moves that make species reachable |
| [species-craft-ideal.md](species-craft-ideal.md) | The species binding at the bench, species materials, socket caps by item kind |
| [gear-climb-ideal.md](gear-climb-ideal.md) | Promotion (E6), the risk ladder, item→item upgrade (E5), R-G1's boss-farmed consumable layer (`craft-assurance`) |

---

## Modules

| Module id | Responsibility | Depends on | Owning program | From |
|---|---|---|---|---|
| `tier-propagation-contract` | T-1…T-5: a ladder is declared once in `gk-core/data/tuning/`; no code restates its ids; derived counts are derived (`CreatureRarityLadder.RungCount`); coverage is guarded per ladder; a tier reaches a magnitude only as an additive `thetaOffset` owing a `ssot-power-scale.md` §10 row | — | `power` + `creature-seed` | tier §The shape 1 |
| `ladder-consistency-repair` | The four measured defects: 84 retired rarity ids in `themes.v1.json`; the FE roster sort dead at 4+ sites; the two duplicate Python `RARITY` tuples; `EncounterTuning.cs:42` | `tier-propagation-contract` | `seedsmith` (`theme-refresh`) + `fe-essentials` | tier §The shape 3, DO #4 |
| `threat-band-fill` | D8: write back the `threatBand` the existing module already scores for all 719 unresolved anchors; ship the `SpeciesExpander.cs:31-33` refusal in the same commit | — | `creature-seed` module 4 | tier DO #2 |
| `species-magnitude-synth` | A7: synthesize `trait.species-magnitude-*` containers in `ImportCreatureSpecies` from values already in SQLite — turns a 904-row content program into an importer change | `threat-band-fill` (it rewrites every magnitude) | `creature-seed` | tier DO #3, §The shape 3 |
| `wave-species-roll` | Replace `pool[i % pool.Count]` with a seeded weighted slot table; widen `Band` past four rungs; add the missing acquisition filter | — | `creature-lawn-deploy` | selection move 1 |
| `wild-species-spawn` | Replace the `"normalzombie"` literal in `SpawnTheUnmade` with a sector/climate-weighted roll; per-flag wild admission (`Summonable` admit, `CaptureOnly` **admit**, `EventOnly` refuse) | — | `loam` / `world-map-runtime` | selection move 3 |
| `delve-species-wiring` | Give `Encounter`/`SlotFill` a production caller; fix `SlotFilter.cs:49`'s missing `+50,000` plant offset in the same change | `threat-band-fill` (its null-`ThreatBand` refusal is correct) | `party-dungeon` | selection move 2 |
| `creature-drop-tables` | E1 a ninth `source_kind` + authored tables; E2 one arm in `LootMintAt.Mint` + one credit call; E3a read the species' own rung instead of the hardcoded `shard.chaff`/`shard.cultivated` | `species-magnitude-synth`, and at least one of `wave-species-roll` / `wild-species-spawn` / `delve-species-wiring` | `drop-tables` | tier §The shape 2, E1–E3a |
| `set-species-binding` | A real `speciesId` + `setClass` field on the set entry; `set-charm-gen` emits it forward; a **deterministic** repair pass extracts it backward from `themeKey`; refuse-and-report the ~40 non-`creature.*` keys rather than guessing | — | `item` module 13 | craft slice 1 |
| `species-cost-shaping` | `speciesCostMultiplierMilli` keyed on the declared species' rarity rung, **gated above a tunable threshold rung — one default plus an explicit per-verb override (R-SC2)**; upgrade level and set membership stay orthogonal | `set-species-binding` | `item` | craft slice 2 |
| `socket-allowance-by-kind` | `socketAllowanceByKind` table beneath the existing 15-row per-role ceiling: ordinary = base max, set piece **reduced**, unique/boss **increased** — bounded above by `structuralCeiling: 4` until the eight-socket topology lands | — | `item` (sockets) | craft §Socket caps |
| `species-materials` | D2: **two trophy layers — 2 per species, 8 per consolidated family, no general layer (R-SC1 as revised by R9)** — minted by a **deterministic seedsmith planner** from two generation parameters (`gk-core/data/tuning/species-material-run.v1.json`), never authored rows; general creatures are not zeroed; a species with no family yields its species leg only; a sixth `MaterialClass` (`Trophy`) as a reviewed change; `CostClassMatrix.Allows` admits it; per-leg drop chances are draw-group weights in the `gk-data/packs/fusion/data/seed/loot/**` creature tables (the spec's § Tunables — not `creature-yield.v1.json`) | `species-cost-shaping`, `creature-drop-tables`, ⭐ **`creature-seed` ask 4** (the C# `speciesKind` mirror in `CreatureAdmission` — strengthen pass 2026-09-18) | `item` + `creature-seed` + `item-seedgen` module 3 (the planner) | craft slice 3, tier E3b, **R-SC1**, **R9** |
| `craft-risk-ladder` | Crafting potential as a new per-instance column, **derived with an explicit authored override** (never a sentinel); exhaustion becomes a new durability decay source — **one pool, one unit, its own craft-wear formula and table beside battle wear's (R-G1)**; enhancement's Safe/Risk bands **stay** (filed decision 2026-09-15, `item-map.md`) — one risk vocabulary **per question** | — (but carries two **cross-program asks**, below) | `item` module 15 + `deployment-hierarchy` module 7 | gear §Failure shape, **R-G1** |
| ⭐ `craft-assurance` | **(new, 2026-09-18 — R-G1)** Boss-farmed consumables that make a craft certain: *assure* (raise enhance success up to 1000‰), *protect* (suppress the attempt's downgrade or craft wear — **never a repair's destroy chance, R10**), *repair* (extra repair coverage); a closed three-id `MaterialClass.Assurance` spent in the **one** `TrySpendAndApply` transaction; boss-channel-only sourcing; a gamble-vs-assurance report. **Fixes a found defect: `wardLoaded` is a free client-asserted flag today** (`WorkbenchEndpoints.cs:37,191`) | `craft-risk-ladder` Stage 2 (T24) for protect-vs-wear; `durability-slice` b (T23) for repair — the *assure* half and the ward fix need neither | `item` modules 14 + 15, `deployment-hierarchy` module 7, `drop-tables` | gear **R-G1** |
| `rarity-promotion` | E6: one reviewed `op_kind` amendment, one `MutationOpKind` member, one executor + POST on the five-verb `ItemWorkbench` pattern, and the `promoted_from_ordinal` mark on the card | `craft-risk-ladder`, `tier-propagation-contract` | `item` | gear §The shape 1 |
| `item-upgrade-tree` | E5: an item-typed cost line, a consume-and-replace `output_kind`, a successor edge on the **armour** class ladder plus an authored `successorOf` field for weapon/offhand/jewel (content not authored here); no reroll; affix-pool legality + the implicit swap presented before consuming | `rarity-promotion`, `craft-risk-ladder`, ⭐ `requirement-profiles-pullforward` | `item` | gear §The shape 2 |
| ⭐ `requirement-profiles-pullforward` | ⛔ **Un-blocks `item-upgrade-tree`, owner-approved 2026-09-13** — the same pull-forward shape as `durability-slice`. `item` module 23 (`requirement-profiles`) already has a **complete, approved spec** (`docs/architecture/item/spec-requirement-profiles.md`) — a pure deterministic resolver + trial evaluator + one tuning file, no schema/persistence change in v1. Built here exactly to that spec, filed back into `item-map.md` | — | `item` module 23 | (new, not from an ideal) |
| ⭐ `gem-tier` | ⛔ **A WIRING gap, not a content gap — the ideal's own fix was illegal.** A gem's tier is already derived in production (`GemContainerBuild.cs:49` → `UniqueBudget.TierOfPowerBand`); the socket path just **hardcodes `1`** at three sites. Authoring a tier on a gem entry is an explicit **OwnershipViolation** (`entry-shapes.md:81`), so the ideal's *"gem tier ids in tuning"* row cannot ship. Also wires the unread `upcycleInputPerOutput` ladder | — | `item` module 16 | tier §Wiring gap |
| ⭐ `socket-combat-wiring` | Make a socketed insert actually reach combat. **Today sockets reach no combat at all** — every production reader is card/surface/workbench; nothing in `Battle/`, equip runtime or the injector reads a socket. Must contribute via **ActorHub**, never a second composer | `gem-tier` | `item` module 16 | tier §Wiring gap · ⛔ **Arm 2 (combination-grant binding) is owned by strain-splice-host `combo-bind`** — this module ships arm 1 (inserts) only (2026-09-18, strain-splice-host map §6 C15) |
| ⭐ `enhance-track-wiring` | Make the authored per-item `enhanceTrack` milestone atoms append at the right enhance levels. **All 1,178 base types carry one; `grep enhanceTrack src/` returns zero hits**, and `ItemWorkbench` passes `Array.Empty<AtomAppend>()` | — | `item` module 15 | tier §Wiring gap |
| ⭐ `craft-executor-completion` | Executors for the remaining priced-but-inert craft verbs (`Forge`, `ForgeGem`, `RerollOne`, `RerollAll` — **`Elevate` is `rarity-promotion`'s**), plus the inverse defect: verbs that are routeable with **zero authored recipes** and so always refuse `material.recipe-unknown` | ⚠ **Corrected — nothing.** The module's own spec header overrides this row: *"Depends on: nothing that blocks it. **Runs beside `rarity-promotion`, not after it**"* — it needs zero enum members and can land in Phase 1, while `rarity-promotion` sits behind an external, two-deep closed-enum queue. **Expect this module to land first** | `item` module 14 + 16 | tier §Wiring gap |

**No cycles**, verified by building the declared graph and the specs' own implied graph and diffing
them. The two shared-tuning-file cases are ordering constraints, not cycles.

---

## Build order

⚠ **Corrected after the dependency audit.** Three edges were wrong or missing; the changes are
marked. The old order had `set-species-binding` in Layer 0, a layer **ahead of** the module that
rewrites the registry it reads.

```
Layer 0 (no dependencies — all EIGHT can run in parallel)
  tier-propagation-contract · threat-band-fill · wave-species-roll · wild-species-spawn¹
  socket-allowance-by-kind  · craft-risk-ladder (STAGE 1 ONLY²)
  gem-tier                  · enhance-track-wiring

Layer 1
  ladder-consistency-repair   ← tier-propagation-contract      [⛔ gated on the themes.v2 decision]
  species-magnitude-synth     ← threat-band-fill
  delve-species-wiring        ← threat-band-fill
  socket-combat-wiring        ← gem-tier

Layer 2
  set-species-binding         ← ladder-consistency-repair       [⭐ NEW EDGE — see Corrections #13]
  creature-drop-tables        ← species-magnitude-synth + any one selection module

Layer 3
  species-cost-shaping        ← set-species-binding

Layer 4
  species-materials           ← species-cost-shaping, creature-drop-tables,
                                creature-seed ask 4 (C# speciesKind mirror in CreatureAdmission)  [⭐ NEW EDGE 2026-09-18]

craft-assurance (⭐ new, R-G1) — split on the same line craft-risk-ladder was:
  assure + the ward defect fix ← nothing unbuilt (EnhancePolicy + TrySpendAndApply both ship);
                                  the shipped FE ward checkbox is deleted in the SAME change
  ⚠ no task in tasks/species-gear-chain-todo.md yet — owed before /build can select it
  protect-vs-craft-wear        ← craft-risk-ladder Stage 2 (T24)
  repair leg                   ← durability-slice b (T23)
  Tuned in ONE pass with craft-risk-ladder's craft-wear table (R-G1), never after it.

OUTSIDE the layered graph, previously — now RESOLVED:
  craft-risk-ladder 2–4       ← deployment-hierarchy module 7 (durability)      pulled forward, DONE
  item-upgrade-tree           ← item module 23 requirement-profiles            pulled forward, DONE

  rarity-promotion            ← craft-risk-ladder + item-side rung arithmetic   (its own deliverable)
  item-upgrade-tree           ← rarity-promotion, craft-risk-ladder, requirement-profiles-pullforward
  requirement-profiles-pullforward  ← nothing — Layer 0, parallel-safe like durability-slice

  craft-executor-completion  ⚠ NOT dependent on rarity-promotion — moved into Layer 0 by the
                              module's own spec correction (needs zero enum members; expect it to
                              land first). See the module table row above.

**⭐ Owner-approved 2026-09-13: `item-upgrade-tree` is no longer deferred.** Both of this initiative's
external blockers were resolved the same way — pulling a small, already-designed slice of the
blocking program forward rather than waiting on its own schedule. **The deferred list is now empty.**
```

¹ moves to Layer 2 behind `species-magnitude-synth` if its Open question 2 resolves to species
magnitudes rather than the flat `UnmadeMemberHp`.
² the split `craft-risk-ladder`'s own Open question 4 recommends — **and which its § Caps section now
forbids shipping alone**, because Stage 1 without Stage 2 is a hard stop on a `long` magnitude.

**Recommended first three, and why** — the ideals argue this order and the evidence supports it:

1. **`threat-band-fill`** — 730 of 904 species sit on one default rung, so the ladder carrying the
   most weight carries the least content. It is free (the scoring already ran) and it gates two
   other modules.
2. **`wave-species-roll` + `wild-species-spawn`** — selection open question 1 recommends these first:
   neither needs `threatBand`, both are cheap, and they prove the slot-table shape before the Delve
   inherits it. ⚠ *2026-09-18:* **R-SS3 ruled "together, in one pass"** — after all three had already
   shipped as separate commits (T3 `0faad36e9`, T6 `63b9e8eb9`, T7 `d2361c761`). The attribution risk
   R-SS3 accepted therefore never arose: the commit boundary exists, and the wave roll never reads
   `threatBand` (`WaveCatalog.cs:170-171` keys on `BaseRarity`). Recorded in both selection specs.
3. **`species-magnitude-synth`** — until it lands, the `threatBand → Θ → P(Θ)` bake reaches no
   gameplay and nothing downstream is observable.

`species-materials` is last on purpose. Its deferral was **sequencing only**: MH's documented fix for
species-bound gear whose species is unreachable was to *make the species farmable*, never to invent a
substitute.

---

## Cross-program asks this map owes (filed nowhere today)

These are not module work; they are amendments against programs that own locked design. They must be
**filed in the owning program's map**, the way `deployment-hierarchy-map.md:89` filed its own.

| Ask | Against | Note |
|---|---|---|
| `Elevate` `op_kind` row in `ssot-enhancement.md` §5.3's reserved table | `item` module 15 | `Repair` is already queued ahead of it for the same closed enum |
| A new per-instance `crafting potential` column beside durability's `(max, current)` | `deployment-hierarchy` module 7 | Module 7 is **owner-locked D1–D6** and written against shipped code, not idea-phase |
| Potential exhaustion as a **new decay source** | `deployment-hierarchy` module 7 | D1 (*"never destroyed by wear alone"*) holds unamended — decay drives to zero, only **repair** may destroy |
| ~~Superseding `spec-enhance-reroll.md` §4's Safe/Risk bands~~ | `item` module 15 | ✅ **Filed and answered 2026-09-15 — the bands stay** (`item-map.md`, *"Filed decision 2026-09-15 — ask #4"*): the bands own *did it succeed*, the ladder owns *may it proceed and at what cost* |
| ⭐ **`MaterialClass.Assurance`** — a closed three-id spend class (`assurance.assure` / `.protect` / `.repair`) | `item` (`ssot-materials-crafting.md` §3.1) | `craft-assurance`, R-G1. Answers *"how much variance do I accept?"* — none of the five classes asks it. Independent of `species-materials`' `Trophy` ask |
| ⭐ **Amend `ssot-enhancement.md` §7.6** (`:548-551`) — protection that **raises** success odds, and `ward.enhance` → `assurance.protect` | `item` module 15 | `craft-assurance`, R-G1. The section calls odds-raising protection *"a paywall"*; R-G1's consumable is boss-farmed, not bought |
| ~~The deterministic trophy planner~~ (mints trophy ids from `perSpecies`/`perFamily`; R9 removed `perGeneral` and the general branch) | `item-seedgen` module 3 (`materials-gen`) | ✅ **Built 2026-09-19 (T34)** — `gk-forge/tools/seedsmith/seedsmith/adapters/items/trophyplan/`, `gk-core/data/tuning/species-material-run.v1.json`, the generated `gk-data/packs/fusion/data/seed/items/materials/trophy-registry.json`, `item-seedgen-map.md` ask #3. `materialgen` stays name/flavor/tags only, extended to fold the registry's ids into `ISSUABLE` — its own scope still says *"never a new material id"* |
| ⭐ **A scope-parametric trophy drop entry** (`trophyScope` ∈ {`species`, `family`} + `slot`, resolved against the killed species at mint time) | `drop-tables` + `item` module 11 (`gk-data/packs/fusion/data/seed/loot/**`) | `creature-drop-tables` Open question 3, R-SC1 — the alternative is 904 per-species tables |
| ⭐ **A C# mirror of `speciesKind: "excluded"`**, consumed in `CreatureAdmission` | `creature-seed` | R-SS2's 2026-09-18 correction: 12 excluded rows still ship as `Summonable` and `CreatureAdmission.cs:14-24` admits them. One declaring site, not a per-roller filter. ✅ **Filed 2026-09-18** as ask 4 in [creature-seed-map.md](creature-seed-map.md) § *Filed by the `species-gear-chain` initiative*. ⛔ Now a **build edge**: `species-materials`' trophy entries wait on it (a kill of an excluded species would otherwise hit the by-name refusal for an absent trophy id) |
| Widening the closed 27-id material vocabulary + a sixth `CostClassMatrix` class | `item` (`ssot-materials-crafting.md` §3.1/§3.4) | A reviewed change, explicitly not a tunable |
| A ninth `source_kind` on `LootSourceRow` | `drop-tables` | Vocabulary + content, not architecture |
| A `ssot-power-scale.md` §10 row per new cost ladder (`promoteCostSoulsMilli`, `upgradeCostSoulsMilli`, any `thetaOffset` table) | `power` | Rows 6/26/27/31/33 are precedent; row 18 shows an authored per-rung table still earns one |
| A `ContributionSourceIds` (GG-49) id for the species-magnitude corpus | `actor-hub` | It reaches the Hub via `AtomDerivedSubsystem` as a registered atom reader — it contributes, it does not fold privately |
| A third creature category (**neutral, never a legion troop**) in `creature-system-map.md`'s Vocabulary | `creature-system` | Today a creature is general **or** unique; a permanently non-recruitable neutral is neither |
| ~~A second contested slot: the sixth `MaterialClass`~~ | — | ⛔ **Struck — a misreading, found during the `/plan` audit 2026-09-13.** `deployment-hierarchy-map.md:89` says *"shard-leg material class **at high rungs**"* — reusing the existing `Shard` class as a repair-recipe cost leg, exactly as `elevate` already does. It proposes no new class. **There is no collision**; `species-materials`' sixth class (`Trophy`) is an ordinary single-owner ask-first change against `ssot-materials-crafting.md` §3.1. Left here as the record of the error — this is the same "cited without opening" pattern the round-2 audit named but did not itself catch |
| ⭐ **`themes.v2.json` + migration** — the append-only rule and the registry `set-charm-gen` consumes | `seedsmith` (`spec-creature-themes.md` §2.4a) + `item` module 13 | `--rebuild`'s sanction expired once 844 set entries bound to `creature.*` keys |
| ⭐ **An eleventh `CraftOperation` member** for `item-upgrade-tree` | `item` | A **separate** closed enum from `op_kind`; *"adding a verb here is code"* |
| ⭐ **A `ssot-power-scale.md` §11 caps-register row** for `craft_potential` as a soft cap | `power` | PS-8: a cap on a magnitude is a progression ceiling until a verdict says otherwise |
| ⭐ **An amendment to `deployment-hierarchy` module 7's own Never list** (`spec-item-durability-repair.md:408` forbids per-item authored derived fields) | `deployment-hierarchy` module 7 | The owner decided the authored potential override; it has never been reconciled with `:408` |
| ⭐ **Schema ownership of `data/tuning/deployment-hierarchy.v{n}.json`** | `deployment-hierarchy` module 7 | ⚠ *2026-09-18:* **overtaken** — `deployment-hierarchy.v1.json` shipped with T10+T11 (`f67930ace`) and `v2` with the magic-numbers sweep (`ecc18cf3`); `DeploymentHierarchyTuning.cs:6` reads v2. T24's craft-wear revision is therefore `v3` via `publish.py`. Original text: The file does not exist and `craft-risk-ladder` is Layer 0, so a module that does not own it creates it — with a throw-on-missing-section parser |
| ⭐ **Replace three `27` pins with a reconciliation canary** (`materialgen/vocab.py:120`, `:124` — module-level `assert`s — and `test_recipes_gen.py:200`) | `item-seedgen` module 3 (`materials-gen` owns `materialgen`, **not** seedsmith) | Two of the three **hard-crash on import**, so widening the vocabulary breaks the build, not a test |
| ⭐ **`species-rank`** — an unlisted 19th `creature-seed` module already claiming a `threatBand × rarity` grid | `creature-seed` | Live overlap with `threat-band-fill` and `wave-species-roll`; reconcile before either builds |

⚠ **Filing is not optional and not this map's job alone.** Per the owner's 2026-09-13 decision, each
ask above is **written into the owning program's own map as a row**, the way
`deployment-hierarchy-map.md:89` filed its own. A cross-program ask that lives only here is an ask the
owning program never sees.

---

## Explicitly out of scope — and which state each is in

**Withdrawn** (gone; reasoning kept only as a trail in the ideals):

- **D7 — lineage as the family key.** Disproven by measurement: median group size **2**, 49
  singletons, 272–333 species with no lineage, cyclic DAG, 80% multi-root.
- ~~**The family layer.**~~ ⭐ **Reinstated by R-SC1 (2026-09-17) — on a different key.** The
  withdrawal was of a family keyed on **lineage** (D7, above), and that stays withdrawn. R-SC1's family
  is the consolidated family map the action corpus already plans against
  (`gk-data/packs/fusion/data/seed/actions/_generated/family-map.json` — 227 families, a reading), and it now carries **8**
  trophy ids each (R9; R-SC1 had 4 — `spec-species-materials.md` § Design 1).
- **`tier-system` as a program.**

**Deferred, with the trigger named:**

| Item | Trigger |
|---|---|
| **D1 — invented species** | Freeze each species' currently-computed `CreatureTypeId` as its permanent allocated id and allocate new ones above the max. ✅ The `SlotFilter` plant-offset divergence this row warned of is fixed (T19): every site now calls `CreatureSpeciesCatalog.CreatureTypeIdFor` |
| **D5 — deterministic exchange** | Rides with `species-materials` |
| **E4 — material grade → socket** | An owner decision, not a bug: `decisions.md` — 'Eight-socket topology (2026-09-10)' deliberately keeps them separate today |
| **The hunt interaction** | The world-stage extension. This initiative stops at *creatures are there and are varied* |
| **The eight-socket topology** | `decisions.md` — 'Eight-socket topology (2026-09-10)' is decided but unapplied; `strain-splice-host` owns the migration order |

**Reserved — named so the socket table leaves room, nothing designed:** **unique item** (world event —
⚠ reconcile against item module 17 `uniques`, which already exists, before either is specced),
**boss item** (4-party raid), **void item** (dropped by a **void beast** via a **void raid** — the void
sieging a player-held sector; the only reserved kind whose source is *defensive*). Also named only:
**demon** (a new empire, *"serious huge program"*) and **void beast** (non-empire).

**Never in this initiative:** any FE surface (a tier bench, compendium, material shelf, hunt board or
bestiary belongs to `item-surfaces` module 20 / `gui-lego`, and a player menu goes through `/idea-ui`);
the `pvz-run` loot source; changing what PvZ itself spawns.

---

## The guard this initiative must ship with, not after

⛔ **No single species' rewards may strictly dominate.** The Wilds/Arkveld case shows monoculture
follows **reward dominance, not the UI** — a map full of creatures whose drops are strictly ordered
will be farmed at exactly one sector. This is `roster-metrics` (creature-seed module 14) pointed at
encounters instead of anchors, and it lands **with** the hunt interaction, not after it.

It is a **report**, never a test assertion: roster coverage is a reading, and
`validation-ssot.md` bans pinning readings.

---

## Open questions the module specs must resolve (all balance data)

None of these blocks the map; each is named here so no module spec silently invents a `const`.

| # | Question | Module |
|---|---|---|
| 1 | ✅ Answered by the build — a **subset**: `class` + rung (`HeadDerivationTables.cs:40-45`); `tags` unread | `craft-risk-ladder` |
| 2 | ✅ **R-G1** — one pool, one unit, **two formulas**; the number is balance data, tuned with `craft-assurance` | `craft-risk-ladder` |
| 3 | Is the class ladder E5's successor spine, or a new field? (It is read by **no C# item code** today, so "reuse" is not free) | `item-upgrade-tree` |
| 4 | ✅ **R-SC2** — one value plus an explicit per-verb override; the rung itself is balance data (T32) | `species-cost-shaping` |
| 5 | ✅ **R-SC1**, revised by **R9** — 2 per species, 8 per family, **no general layer**; generals not zeroed. The former interpretation question (`spec-species-materials.md` Open question 5) is moot | `species-materials` |
| 6 | ✅ **R-SS3** — together; overtaken by the build (separate commits), risk never arose | `wave-species-roll`, `wild-species-spawn` |
| 7 | ✅ **R-SS1** — its own table; built that way (`world-spawn.v1.json`) | `wild-species-spawn` |
| 8 | ✅ **R-SS2** — not this program's question; coverage belongs to future spawn-surface programs, measured by a distribution statistic engine of its own | — |

---

## ⛔ Corrections the module specs found — the map's own rows are amended by these

Each was measured against code or the shipped corpus while speccing, and each contradicts something
this map or a source ideal carried. **The spec is the authority; these are recorded so the map is not
read against them.**

| # | Where | The correction |
|---|---|---|
| 1 | `craft-risk-ladder`'s dependencies | The map lists **none**. True of its *design*, not its *build*: stages 2–4 need durability, and `deployment-hierarchy` module 7 is **unbuilt** (*"Nothing tests durability, because nothing implements it"*). **Stage 1 is independent; stages 2–4 are not.** The spec recommends splitting on that line |
| 2 | `delve-species-wiring` | ✅ *Fixed by T19 (`937390c3`): `SlotFilter.cs:53` now calls `CreatureSpeciesCatalog.CreatureTypeIdFor(Side, GameTypeId)`.* Original finding: `SlotFilter.cs:49` is not merely *"a latent divergence"* — it omits the plant offset the other two sites apply, and **102 `gameTypeId` values appear on both sides**, so it maps 102 plant/zombie pairs onto the **same** `CreatureTypeId`. A silent collision in an identity field |
| 3 | `set-species-binding` | The ideal expected a refusal backlog (*"844 of 884 resolve"*). **All 844 `creature.*` themeKeys resolve — 844 of 844** — but **only case-insensitively** (`creature.abyssswordstar` vs `AbyssSwordStar`). An exact-match repair resolves **zero** and looks like a content gap |
| 4 | `set-species-binding` | ⭐ `gk-data/packs/fusion/data/seed/creatures/_registry/themes.v1.json` carries **`speciesId` as a field** on all 904 rows — a real `themeKey → speciesId` index, a better join than parsing the key's suffix |
| 5 | `creature-drop-tables` | E3a is **not "one read."** The shard mints at `ExpeditionResolver.cs:94-98` from an `isBoss` ternary over two consts, **at plan time, with no species in scope** — and the comment records that plan-time is load-bearing for manifest determinism |
| 6 | `item-upgrade-tree` | ⭐ **The class ladder is only an upgrade spine for armour.** The registry's own rationale says the weapon ladder is ordered *"by combat role, not raw damage number"* (`blade → blunt → launcher`, melee → **ranged**) and the offhand's question is *"does it guard, or does it not."* Upgrading along those is D2's upgrade-becomes-downgrade |
| 7 | `item-upgrade-tree` | The ideal says the class ladder *"is read by no C# item code today."* It **is** read — `gk-forge/tools/ItemSeedValidator/Registries/RegistrySet.cs:371`, `ReferenceCheck.cs:130`, and two seedsmith modules. Precisely: **read by the validator and generators, not by the runtime**, and every entry already carries a `rung` |
| 8 | `threat-band-fill` | The ideal's *"ship the `SpeciesExpander.cs:31-33` refusal in the same commit"* would **refuse 719 species**. The exclusion is deliberate and documented (a sanctioned fallback exists). The defect is that the fallback **leaves no trace** — so the fix is provenance + a report |
| 9 | `ladder-consistency-repair` | The 84 retired rarity ids are in **`gk-data/packs/fusion/data/seed/creatures/_registry/themes.v1.json`** (the items one is frozen and carries none) — and the repo's several *"themes.v1.json (84 rows)"* comments are a **stale reference to the old catalog size**, an unrelated coincidence |
| 10 | `tier-propagation-contract` | A **fourth** restated ladder, not in the ideal's three: `Items/RarityLadder.cs` `RungIds` restates the ten item rarity ids while its own class comment says the seed file is the authority |
| 11 | Every tunables row | ~~The ideals write *"a new `<file>.v{n}.json` revision."* The shipped pattern is **one file carrying `schemaVersion` + `version`** (`sockets.v1.json` is at `version: 2`). The `v{n}` phrasing would have created second files~~ ⛔ **REVERSED by the strengthen pass, 2026-09-18.** This correction read one file's history as the rule and overrode the standard: `tunables-ssot.md` **T4** — *"A tool republishes `v{n+1}`; the old version stays on disk"* — and `gk-core/tools/tuning/publish.py` writes exactly that. The repo has since followed T4 (`deployment-hierarchy.v2.json`, `creature-threat.v2.json`), and `strain-splice-host` plans `sockets.v2`/`v3`. T-tasks built under the reversed rule edited files in place (T4: `sockets.v1.json` `version` 2→3; T6: `waves.v1.json`) — **grandfathered history, not a template**. The ideals' `v{n}` phrasing was right. See § Tuning revisions |
| 12 | `species-materials` | The sixth `MaterialClass` has an **exact stated test** to pass — *"which of these five questions is unanswerable for my spend?"* The spec argues it against `Substrate` (the near miss) rather than asserting it |

## ⛔ Corrections — round 2, the five-agent audit (2026-09-13)

Five parallel audits — coverage, evidence, compliance, dependencies, adversarial — found **~35
defects**, the large majority in the specs rather than the ideals. All are fixed in the files; the
load-bearing ones are recorded here because **the pattern matters more than the individual errors**.

### Three failure patterns, named

1. **Cited without opening.** `ItemWorkbench`'s "five verbs" (`Temper`/`Bore`/`Socket`/`Imbue` are
   **not method names** — they are `CraftOperation` arguments *inside* `Enhance`/`SocketAdd`);
   `CreatureRarityLadder.IsTopRung` called on an **item** rarity (wrong type, would not compile);
   `Disposition` cited to `RpgStore.ItemUniques.cs` instead of `RpgStore.Items.cs`;
   `SocketCircuitSize`, which is a proposed snippet in a spec doc and **not shipped code**.
2. **Trusted a doc's status over the code.** `item-map.md` says module 23 `requirement-profiles` is
   *"approved 2026-09-09"*; a spec wrote *"exists"*. `grep -rn "RequirementProfile" src/` → **zero
   hits**. **Approved is not built.**
3. ⭐ **Read a struck claim and rebuilt on it anyway.** Five specs used figures the tier ideal's own
   § AUDIT had already corrected — the overstated kill attribution in `decisions.md` — 'Battle death attribution (2026-09-08)', E2's "one arm"
   (really 2–3 Data files plus a `string`/`long` player-id mismatch), the propagation refactor's
   6–8 sites (really ~30 across ~24 files), and `RarityTuningCoverageTests`' real coverage
   (5 tuning files with two **seven-rung** exceptions, not a blanket guard). This is the exact
   propose→get-corrected→read sequence DESIGN-GATE exists to stop.

### The findings with the highest rework cost

| # | Finding |
|---|---|
| 13 | ⭐ **`set-species-binding` was a layer ahead of the module that rewrites the registry it reads.** The spec contained the warning (*"sequence them"*) and the map ignored it. New edge; module moved to Layer 2 |
| 14 | ⛔ **`ladder-consistency-repair`'s root cause was wrong, and its fix path has an expired sanction.** The generator's no-op defect is described in the **past tense**; the inputs are already clean. The 84 survive because the registry is **deliberately append-only**, and `--rebuild`'s permission was conditional on *"nothing is bound to these keys yet"* — **844 set entries are now bound.** Owner decision: **`themes.v2.json` + migration** |
| 15 | ⛔ **T-5 as written was false of shipped code and made three sibling modules illegal.** `materials.v1.json` prices six verbs on `rung` as a **coefficient**. Split into T-5a (actor magnitude — additive `thetaOffset` only) and T-5b (economy cost — a rung coefficient owing its own §10 row). Success criterion 6 would otherwise have written the false rule into the power SSOT |
| 16 | ⛔ **`item-upgrade-tree`'s armour-only scope was argued from the wrong evidence, and armour fails that argument too.** The real vindication is `ssot-item-categories.md:493` (class rungs ×1.4) and `:627-628` (plate wins guard 2.3×, **never overlaps**). **And the constraint that exposes:** `:629-631` says cloth's entire compensation is its **class-tagged affix pool and implicit slate**, so "carry affixes untouched" **launders cloth-pool affixes onto a plate chassis** and silently swaps the implicit. Two new mandatory rules (Design §2a) |
| 17 | ⛔ **`socketAllowanceByKind` was declared a tunable on an append-only, `catalog_revision`-derived surface** — a post-ship edit silently re-sockets every item ever dropped at that rung, and **no build-time test catches it.** Rows are now append-only and revision-pinned. The derived window also bypassed **OD4 overlap, monotonicity and non-negativity**; all three are now load rejections |
| 18 | ⛔ **Three live `27` pins, two of them module-level `assert`s that hard-crash seedsmith on import.** Widening the material vocabulary breaks the build, not a test. Replaced with a reconciliation canary |
| 19 | **`rarity-promotion`'s declared dependency was satisfied by nothing.** `Items/RarityLadder` has no `IsTopRung`/`OneRungAbove`/`RungCount`, and `tier-propagation-contract` will not add them. Item-side rung arithmetic is now that module's own deliverable |
| 20 | **Two drop-table corpora, and the spec named the wrong one.** `gk-data/packs/fusion/data/seed/loot/README.md` has a section titled *"Why this is not `gk-data/packs/fusion/data/seed/items/drop-tables/`"*. `droptablegen` writes the latter; E1's runtime tables belong in the former. ⚠ The ideal's claim that `gk-data/packs/fusion/data/seed/loot/**` *"does not exist"* is also **false** |
| 21 | **A settled decision was reversed without saying so.** D5 (*"ships **with** the first tier content, undisputed"*) was re-opened as an open question recommending the opposite. Restored |
| 22 | **Measurements corrected:** 910 set entries, not 911 (the 911th was a generator ledger); `theme.*` 30, not 31; **seven** ladder restatements, not four; `waves.v1.json` has **no `version` field**, so a revision is an add, not a bump; `CreatureSpeciesCatalog` **already enforces** `creatureTypeId` uniqueness at load (the narrower real gap is that `SlotFilter`'s computed property bypasses that guard) |
| 23 | **Three fake open questions** (each answered in its own sentence) and **one manufactured certainty** (*"not a scope cut — it is a correctness requirement"*, which no owner decided) removed |
| 24 | **Unverifiable claims struck rather than repeated** — the "6 sites vs ≥22 files" measurement had no ladder, file list or command behind it |
| 25 | ⛔ **SOLID:** two specs proposed the same admission rule as **prose duplicated across two files**. Replaced with one `CreatureAdmission` declaring site in Core, a named member per context |

### What survived the audit

Every load-bearing **measurement** taken while writing the specs reproduced exactly on an independent
re-derivation: 904 species / 185 stored `threatBand` / 719 absent; the 730-on-one-rung reconciliation;
**102 colliding `gameTypeId`s**; 844-of-844 case-insensitive themeKey resolution with **0** exact
matches; `MaterialCatalog.All == 27 == 10+8+6+3`; 67 recipes with 10 `elevate`; exactly **10 distinct
species** reachable across the four shipped waves. Every long verbatim code-comment quote matched word
for word, with the behaviour verified in code rather than inferred from the comment.

**Tunables (T1–T8), validation-ssot, numeric overflow and the ActorHub gate came back clean across all
fifteen specs.** The failures were in claims *reasoned to*, not claims *measured*.

---

## Owner rulings 2026-09-17/18 — where each landed

| Ruling | Source | Landed in |
|---|---|---|
| **R-SS1** — the map spawn table is its own | `species-selection-ideal.md` | Already built so (T7); `spec-wild-species-spawn.md` Open question 1 marked ruled |
| **R-SS2** — roster coverage is not this program's question | same | `spec-wild-species-spawn.md` Open question 1 note; open question 8 above; the `speciesKind` ask above |
| **R-SS3** — roll restoration and `threatBand` fill together | same | `spec-wave-species-roll.md` Open question 1 — overtaken by the build; no task owed |
| **R-SC1** — 2 / 4 / 4 trophies as seedsmith parameters (**counts superseded by R9: 2 / 8 / 0**) | `species-craft-ideal.md` | `spec-species-materials.md` (rewritten design §1, §2, §4, §5, Seedsmith section); `spec-creature-drop-tables.md` Open question 3 + Seedsmith section |
| **R-SC2** — one threshold plus an explicit per-verb override | same | `spec-species-cost-shaping.md` § Design 1, Tunables, Testing |
| **R-G1** — one pool, one unit, two formulas; boss-farmed consumables | `gear-climb-ideal.md` | `spec-craft-risk-ladder.md` § Design 3, 5, Tunables; ⭐ new module `spec-craft-assurance.md` |
| **R9** (2026-09-18) — craft materials: species 2, family 8, **general 0** (layer removed) | [spec-rulings-2026-09-18.md](spec-rulings-2026-09-18.md); recorded beside R-SC1 in `species-craft-ideal.md` | `spec-species-materials.md` (header, § Design 1–5, Seedsmith, Tunables, Testing, Boundaries, Success criteria, Open questions 1 and 5); `spec-creature-drop-tables.md` (header, E3b note, Seedsmith section, Open question 3) |
| **R10** (2026-09-18) — *protect* does not cover repair destruction; the repair destroy chance stands as the durability sink | [spec-rulings-2026-09-18.md](spec-rulings-2026-09-18.md) | `spec-craft-assurance.md` (header, § Design 2, Testing, Boundaries, Success criteria, Open question 1) |
| **R20** (2026-09-18) — the `forge-gem` souls leg may be repriced by strain-splice-host's `combo-budget` report | [spec-rulings-2026-09-18.md](spec-rulings-2026-09-18.md) | `spec-gem-tier.md` (Project structure, Tunables, Boundaries); § Tuning revisions `materials` row |
| **R22** (2026-09-18) — multi-family species: one family per kill, equal odds; counts toward every listed family for recipes | [spec-rulings-2026-09-18.md](spec-rulings-2026-09-18.md) | `spec-species-materials.md` (R22 note, § Design 5.2, Testing, Strengthen pass item 4, Open question 6); `spec-creature-drop-tables.md` (R22 note, Testing, Strengthen pass item 3, Open question 3); O1 below |

Every amended or new spec carries a **Seedsmith / generator** section — naming the adapter, the
parameter file, new seed fields and regeneration commands where a generator is involved, and saying so
in one line where none is.

## Gate status

**DESIGN-GATE §5, honestly:** the four source ideals each carry their own reading-gate section
recording the documents read and the code verified at `file:line`. This map introduces no new claim
that is not carried by one of them. ~~**The §5 boundary box remains untickable**~~ — *2026-09-18: the
strengthen pass ran under `tasks/sessions/strengthen-sgc-20260918.json`, so the boundary box is
tickable for this map's latest edits; the earlier sessions' gap stays recorded as history.*

**Next step:** ~~owner approves module boundaries … then each module gets its own spec~~ *(overtaken —
all 20 specs exist and 13 modules have shipped in part or whole).* Remaining build: T22–T34 and T37–T38
in the plan, plus `craft-assurance`, which **has no task in `tasks/species-gear-chain-todo.md` yet** (the
module was added 2026-09-18, after the plan) — its tasks are owed before `/build` can select it.

---

## Tuning revisions — one rule, one publish order (strengthen pass 2026-09-18)

**The rule (tunables-ssot T4, restored):** a balance change to `gk-core/data/tuning/<domain>.v{n}.json` publishes
a **new** `<domain>.v{n+1}.json` through `gk-core/tools/tuning/publish.py`; `v{n}` stays on disk for revert. The
publish takes `n` from disk at build time (`publish.py` `latest_version`), so **no spec here reserves a
number**. `publish.py` refuses to invent a key, so a module adding a *new* key extends the tool first
(`tunables-ssot.md` §7.1). The host's reader switch — the filename at `gk-core/src/FusionRpg.Server/Program.cs` / `:308` / `:316`
for materials / enhancement / sockets, or the domain's own loader (`DeploymentHierarchyTuning.cs:6`) —
lands **in the same commit** as the publish, or the new file is dead config.

**Shared domains and the order their publishes land in.** Two programs writing one domain never branch
from the same `v{n}` in parallel: the later build rebases onto the earlier publish.

| Domain | Latest on disk | Pending publishes, in land order | Owner of each |
|---|---|---|---|
| `sockets` | `v1` (`version` 3, in-place history) | `circuit-topology` (strain-splice-host; names it `sockets.v2`) → `combo-budget` (`v3`) → any species-gear-chain socket change (`gem-tier` only if `upcycleInputPerOutput` moves; `socket-combat-wiring` only if its Tunables row 1 is adopted) takes the **next** number after them | strain-splice-host first; this map only if it must |
| `materials` | `v3` (T23 published `v2` first — the repair op's own row — then `species-cost-shaping` T32 published `v3`, 2026-09-19: `speciesCostMultiplierMilli`/`speciesCostThresholdRung`/`speciesCostThresholdRungByVerb`, `Program.cs` switched in the same commit) | `species-materials` (T34, **one** publish: trophy `operations` rows + D5 exchange) → `rarity-promotion` / `item-upgrade-tree` if either adds a cost row. `strain-splice-host` `socket-pricing` names a conditional `materials.v{n+1}` — ⚠ takes whatever number is next after T34's publish. **R20 (2026-09-18):** that conditional publish may now also carry `operations.forge-gem.souls.coefficient` at `combo-budget`'s derived value — `gem-tier`'s *"confirm, do not re-author"* leg is repriced only through it, on top of whatever this map's rows have already published | this map + strain-splice-host (flagged in this pass's report, not edited here) |
| `deployment-hierarchy` | `v2` | `craft-risk-ladder` Stages 2–3 (T24) → `v3` | this map |
| `enhancement` | `v1` | none from this map — `craft-assurance` publishes its own new `craft-assurance.v1.json` | — |
| `creature-yield` | none | `creature-drop-tables` creates `v1` — **sole owner** (it was "shared with `species-materials`, whoever first": two owners for one file) | this map |
| `species-material-run` | none | `species-materials` creates `v1` (read by seedsmith only) | this map |

## Strengthen pass 2026-09-18 — findings that changed the map

1. **Build state.** Shipped per `git log --grep species-gear-chain`: T1–T2 `tier-propagation-contract`,
   T3 `threat-band-fill`, T4 `socket-allowance-by-kind`, T5 `CreatureAdmission`, T6 `wave-species-roll`,
   T7 + T18b `wild-species-spawn`, T8–T9 `gem-tier`, T10 `craft-risk-ladder` Stage 1, T11 durability
   slice a, T12–T13 `enhance-track-wiring`, T14–T15 (+ T9) `craft-executor-completion`, T35–T36
   `requirement-profiles-pullforward`, T16–T17 `ladder-consistency-repair`, T18
   `species-magnitude-synth`, T19–T20 `delve-species-wiring`, T21 `socket-combat-wiring` a. The module
   table's *"today"* phrasing (*"sockets reach no combat at all"*, *"hardcodes `1` at three sites"*,
   *"`grep enhanceTrack src/` returns zero hits"*, *"a player meets 10 of 904 creatures"*) is the
   **pre-build** state those tasks closed. Each built spec now opens with a build-state banner.
   **Unbuilt:** `set-species-binding`, `species-cost-shaping`, `creature-drop-tables`,
   `species-materials`, `rarity-promotion`, `item-upgrade-tree`, `craft-assurance`, `craft-risk-ladder`
   Stages 2–4, `socket-combat-wiring` b (T22), durability slice b (T23).
2. **§ Corrections #11 reversed** — § Tuning revisions.
3. **New edge:** `species-materials` (and `creature-drop-tables`' parametric trophy entry) ← `creature-seed`
   ask 4. Without it the 12 excluded species, still admitted in every context, would refuse their loot on
   every kill.
4. **`creature-yield.v1.json` had two owners** — now `creature-drop-tables` alone.
5. **`craft-assurance`:** its overload refusal used an unregistered namespace (`assure.*` — would throw,
   not refuse); refusing any request "carrying `wardLoaded`" would have refused every enhance the shipped
   web client sends (it always sends the key), and the shipped ward checkbox must be deleted in the same
   change; the policy's load count and the debited lines are now one input; the boss-only rule is closed
   through `Table` recursion and otherwise stated as visibility, not proof.
6. **`creature-drop-tables`:** E2's credit site was named as `LootMintAt.Mint`, which `Material` grants
   never reach — it is `PersistLootUnlocked`, after the correlation-id early return (retry-safe);
   `DropEntryKind` has ten members, not nine; the parametric trophy entry now has a persisted shape;
   its own Boundaries called `gk-data/packs/fusion/data/seed/loot/**` generator output, contradicting its § What exists.
7. **`species-materials`:** the family-map reader it said to reuse returns only family ids, returns empty
   on a missing file and unions a legacy registry — a dedicated loader refuses both edges; the trophy
   registry gets a CI `--check`; recipe trophy legs resolve in the one `MaterialRecipeCatalog.Resolve` site.
8. **The error-code count is not a conflict.** `DropTableValidator.cs:28`'s "34th" and the specs'
   "closed 33-code list" describe one enum: 33 specific codes, `ContentRuleViolated` the 34th and last,
   plus `None` — 35 members, pinned as a closed vocabulary (`SocketOperationsTests.cs:61`).

## OWNER questions (strengthen pass 2026-09-18)

Kept to what no ruling covers and code cannot decide.

| # | Question | Default if unanswered | Blocks |
|---|---|---|---|
| ~~O1~~ **Ruled R22** | A species in two families (278 on 2026-09-18, a reading): which family's trophy does a **recipe** demand? | ~~The first family on both sides~~ **Ruled R22 (2026-09-18):** the drop rolls one family per kill with equal odds on the named stream `item.trophy-family.{tableId}.{groupKey}` (deterministic, replay-safe); the species counts as a member of **every** listed family, so any listed family's trophy pays its family-scope cost leg (`spec-species-materials.md` § Design 5.2, Strengthen pass item 4) | Nothing — T34's multi-family cost legs proceed |
