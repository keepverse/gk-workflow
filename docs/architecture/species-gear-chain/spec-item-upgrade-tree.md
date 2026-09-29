# Spec: Item upgrade tree (`item-upgrade-tree`)

**Initiative:** `species-gear-chain` ([map](../species-gear-chain-map.md)) · **Module:** `item-upgrade-tree`
**Owning program:** `item`
**Depends on:** `rarity-promotion`, `craft-risk-ladder`, `requirement-profiles-pullforward`
**✅ BUILT since (2026-09-18 re-verify):** `requirement-profiles-pullforward` shipped as T35 (`ac2dae72`, `gk-core/src/FusionRpg.Core/Items/Requirements/RequirementProfile.cs`, `RequirementProfileResolver.cs`) and T36 (`b158acf1`, tuning + seedsmith validation). The text below is the pre-build record.
**⭐ UN-BLOCKED 2026-09-13 (owner):** `item` module 23 `requirement-profiles` had zero implementation
(`grep -rn "RequirementProfile" src/` → 0 hits) but a **complete, approved spec**
(`docs/architecture/item/spec-requirement-profiles.md`). Rather than wait on the `item` program's own
schedule, a minimal pull-forward of that spec is built inside this initiative — the same shape as
`craft-risk-ladder`'s durability pull-forward. See `requirement-profiles-pullforward`'s tasks.
**Status:** spec, 2026-09-13. Awaiting owner approval. ⚠ *2026-09-18: approved through `tasks/species-gear-chain-plan.md`.* ⭐ **BUILT 2026-09-21 (re-verified against `HEAD`):** T37's executor is shipped — `ItemUpgradePolicy` + `ItemUpgradeEdges`, `RpgStore.TryUpgradeAndApply`, `ItemWorkbench.Upgrade` and `POST /api/items/workbench/upgrade` with its read-only preview, the `materials.v5` / `deployment-hierarchy.v5` publishes, and the web card mark — and T38's authored-edge field is shipped (`gk-data/packs/fusion/data/seed/items/_registry/successor-edges.v1.json` + the basetypegen passthrough and its generator-side closure gate). Evidence: `tasks/evidence-fragments/T37.md`, `T38.md`. **One line is not built:** rule 4's runtime wire, externally blocked on per-atom power (see § Requirement profiles below).
**Source ideal:** [gear-climb-ideal.md](../gear-climb-ideal.md) § The shape 2 (E5)

---

## Objective

**Let an item become a different, better item — consuming the old one, carrying its identity across.**

This is the one place in the whole initiative where the schema **genuinely cannot express the
request.** Promotion is in-place (`outputKind: mutation`, no `outputRef`), so it can never change what
an item *is*. E5 is a different verb: an item-typed cost line, a consume-and-replace `output_kind`,
and a successor edge.

---

## ⛔ The finding that changes this module's design

The ideal proposes the **class ladder** as the successor spine (`cloth→leather→scale→plate`) and notes
it *"already exists as ordering."* **Reading the registry shows the ordering exists for four ladders
and means four different things.** Quoted from `classes.v3.json`'s own `rungCountRationale` fields:

| Ladder | Rungs | What the ordering means | Usable as an upgrade spine? |
|---|---|---|---|
| **armour** | 4 | Weight: `cloth → leather → scale → plate` (tags `light` → `medium-light` → `medium-heavy` → `heavy`); plant frame `fibre → husk → bark → heartwood` | ✅ **Yes.** A genuine progression |
| **weapon** | 3 | ⛔ *"Rungs are ordered by **combat role, not raw damage number**, so the same rung means the same fighting style on both frames."* `blade` (light melee) → `blunt` (medium melee) → `launcher` (heavy **ranged**) | ❌ **No.** A style axis |
| **offhand** | 2 | ⛔ *"The off-hand's entire mechanical question is binary — **does it guard, or does it not**."* `focus` (no-guard) → `bulwark` (guarding) | ❌ **No.** A category switch |
| **jewel** | 3 | *"Ordered by **potency/commitment** (light claim → bold statement → binding pact), not by mass"* | ⚠ **Arguably.** Commitment is not power |
| **standard** | 2 | Commander gear, *"single-band in v1 — it is not item-level tiered"* | ❌ Out of scope |

⭐ **So "upgrade along the class ladder" is correct for armour and wrong for weapons.** Upgrading a
`blade` into a `launcher` would not make a better weapon — it would turn a fast melee weapon into a
heavy ranged one, silently changing what the player's build does. That is **D2's
upgrade-becomes-downgrade failure**, reached by a different route than requirement creep.

### ⚠ Correction, 2026-09-13 — the rationale strings do not prove this, and armour fails the same test

An earlier draft of this spec rested the armour/weapon split on the `rungCountRationale` strings
alone. **That reading is asymmetric and does not survive.** Armour's own rationale asserts *weight
class*, not power: *"Fewer than four collapses two of the nine armour-bearing roles' base types into
indistinguishable **weight classes**"* — and `cloth` and `plate` carry **identical `roles` arrays**.
On the test as stated, armour disqualifies itself exactly as weapon does.

**The evidence that actually vindicates armour is elsewhere, and it is decisive**
(`docs/architecture/item/ssot-item-categories.md`):

- `:493` — *"Bands rise ×2.1, **class rungs rise ×1.4**"*
- `:627-628` — *"band-3 cloth `core-protective` is `280‰ × 780 = 218 hp` (196–240) against plate's
  501. **Plate wins guard by 2.3× and never overlaps.**"*

**A strict, non-overlapping guard-magnitude ladder is a progression spine. The weapon ladder has no
such table, because it is not one.** The conclusion stands; the argument is replaced.

### ⛔ And the constraint that correction exposes — the one this module must actually satisfy

The same section states what makes the armour ladder survivable, and it is not the guard number:

> `ssot-item-categories.md:629-631` — *"Cloth's entire compensation therefore has to come from its
> **class-tagged affix pool** and its **implicit slate**. If I8 does not differentiate
> `armour-cloth` from `armour-plate`, cloth is strictly worse and the ladder collapses into 'wear the
> heaviest thing you can.'"*
>
> `:746-747` — *"I8 — the affix pool must be filtered by `affix_pool_tag`, and **cloth must not be
> strictly worse than plate**."*

⛔ **So "carry every affix across untouched" — this spec's own §2 rule and success criterion 2 —
launders `armour-cloth`-pool affixes onto a plate chassis**, producing a combination the drop path
can never roll. And because the successor is a different base type it carries a different
`implicitFamily` (`classes.v3.json` `implicitSlates`), so **the piece's implicit silently changes**.

That is D2's upgrade-becomes-downgrade by a third route — on the one ladder this spec certified as
safe. **Two rules are therefore mandatory, and they are Design §2a below.**

### And a correction to the ideal's cost estimate

The ideal states the class ladder *"is currently read by no C# code, so adopting it is itself work."*
**That is not accurate.** It is read by:

- `gk-forge/tools/ItemSeedValidator/Registries/RegistrySet.cs:371` — iterates `classLadders`
- `gk-forge/tools/ItemSeedValidator/Checks/ReferenceCheck.cs:130` — validates `class` references against it
- `seedsmith/adapters/items/basetypegen/tuning.py:96` and `gk-forge/tools/seedsmith/seedsmith/adapters/items/registries.py:79`

**The precise statement is: it is read by the validator and the generators, not by the runtime
(`FusionRpg.Core`).** Every entry already carries an explicit `rung` integer, so a successor edge is
**expressible today** — `rung n → rung n+1` within `(ladder, frame)`. That is *less* work than the
ideal estimated, on the armour ladder where it is meaningful.

⚠ **But the registries are `frozen: true` with `minCompatibleVersion`**, and there are three files
(`classes.v1/v2/v3.json`, at `registryVersion` 3/4/5). Adding successor edges is a **reviewed registry
change**. ⚠ **Corrected:** an earlier draft cited `v4Note` as the additivity precedent. It is not — `v4Note` records *"re-derive the 32-family global exclusion list against `AtomKindRegistry.cs` instead of the frozen v1 designNotes snapshot"*, a **replacement** of a frozen snapshot. The additivity constraint is real but rests on `minCompatibleVersion` and `stage1aFrozen` (*"a change to this registry invalidates authored content unless minCompatibleVersion says otherwise"*), which is what this spec must argue from.

---

## What exists today — verified

### Built

- **`CreatureRecipeDef`** (`Creatures/Fusion/CreatureRecipeCatalog.cs:11-13`) — full signature
  `(string RecipeId, string OutputSpeciesId, string InputSpeciesIdA, string InputSpeciesIdB, bool CrossRungGapFill = false)`. The creature side already ships a
  consume-two-produce-one shape. It is the structural precedent, on the other side of the house.
- Every class ladder entry carries `id`, `frame`, **`rung`**, `nameKey`, `identity`, `roles`, `tags`.
- `ItemWorkbench`'s six-verb pattern, the mutation ledger, and the recipe corpus (67 recipes,
  `outputKind` / `outputQty` / `costLines` / `soulsCostBand`).
- ~~`requirement-profiles` (item module 23) exists~~ ⛔ **STRUCK — it did not.** `grep -rn "RequirementProfile" src/` returned **zero hits** as of the /spec audit. What existed was a **complete, approved spec** (`docs/architecture/item/spec-requirement-profiles.md`, Design-gate record already ticked) with no code. **A doc saying "approved" is not evidence something is built.** ⭐ **Resolved 2026-09-13:** rather than wait, the owner approved pulling that already-designed module forward — see `requirement-profiles-pullforward`'s own tasks, built exactly to that spec. This module's dependency on it is now a normal task dependency, not an external blocker.

### Real gap — ⚠ the table below is the PRE-BUILD record (2026-09-13); every row is now built, and the entries are kept as written so the gap they named stays readable

| Gap | What must be built | Built by |
|---|---|---|
| Item-typed cost line | `costLines` today names `material` ids; consuming an **item instance** is a new line kind | ⭐ **Not needed, and the design says why:** an item is not a `MaterialClass`, so the consumed instance rides the mutation and the only cost line is `MaterialCostLine.Souls` built in the verb (`ItemWorkbench.Upgrade`). No new line kind exists, deliberately |
| Consume-and-replace `output_kind` | Every shipped recipe is `mutation` (in-place) or a mint. Neither consumes an instance and produces a different one | `RpgStore.TryUpgradeAndApply` — one transaction: op for the consumed instance, salvage-shaped disposition, `SaveInstanceUnlocked` for the successor, the successor's `item_generation` row |
| Successor edge | Expressible via `rung`, but not declared — and only meaningful on one ladder | T38: the authored per-base-type `successorOf` (`_registry/successor-edges.v1.json`), never a ladder derivation (owner ruling 2026-09-21) |
| An `op_kind` member | `MutationOpKind` is closed and ask-first. ⚠ This is the **third** queued ask on module 15, behind `Repair` and `Elevate` | `MutationOpKind.Upgrade` (the thirteenth) + `CraftOperation.Upgrade` (the twelfth), under the owner ruling; the §5.3 row and the §10 cost row landed with them |

---

## Design

### 1. One successor source — the authored per-base-type edge (owner ruling 2026-09-21)

⭐ **RULED 2026-09-21 (owner, `d12dcb90`): every base type upgrades through an explicit authored
`successorOf` edge on its own row; the successor is NEVER derived from a class ladder.** This retires
the "two sources" shape this section previously described (armour reading the class ladder's `rung`,
everything else reading `successorOf`) — there is one source and one executor.

**Why no ladder, on any ladder.** Armour's own rationale names *weight classes*, not power, and
`cloth`/`plate` carry identical `roles` arrays; weapon's rationales say *"ordered by combat role, not
raw damage number"* (`blade` light melee → `blunt` medium melee → `launcher` heavy **ranged**);
offhand's whole question is binary ("does it guard, or does it not"); jewel's is commitment. A
successor read off any of them would silently produce a different *kind* of item — the
upgrade-becomes-downgrade failure by a third route, on the one ladder that has a non-overlapping guard
ladder. The corpus analysis above is the cause this ruling rests on.

**Consequences, in one place:**
- `successorOf` is an **additive, optional** field on the base-type corpus
  (`gk-data/packs/fusion/data/seed/items/base-types/**`), authored through the generator's own input table and regenerated —
  never a hand edit, and **no `classes.v*.json` change at all**.
- **Zero values are authored by T38.** A base type without an edge refuses by name
  (`upgrade.no-successor`), which is the correct state today for every non-armour base type and for any
  armour chassis whose edge nobody has authored yet. That content pass is owed separately and named in
  the todo.
- The executor keeps one lookup: `ItemUpgradePolicy.Decide` reads the edge and applies the same
  affix-legality, implicit-change and requirement rules on every ladder, armour included.

**Content scope.** The edges are authored per chassis, so a ladder's coverage is whatever its authors
have written; nothing in the mechanism privileges armour. Armour's own ladder (both frames:
`cloth→leather→scale→plate`, `fibre→husk→bark→heartwood`) is where a first edge set is most obviously
meaningful — but that is an authoring choice, not a mechanism constraint, and the mechanism is proved
by test against synthetic edges on all four ladders today.

~~**DECIDED 2026-09-13 (owner):** weapons, offhands and jewels get a **new authored `successorOf`
field per base type** …~~ ⛔ struck 2026-09-21: the ruling extends that field to **every** ladder, so
there is no armour/rest split left to describe.

~~**The executor reads whichever source the base type declares — armour reads the class ladder's
`rung`, everything else reads `successorOf` — one lookup function, two inputs, never two executors.**~~
⛔ struck 2026-09-21 — the class-ladder input does not exist. What survives is the shape the sentence
got right: **one lookup function, never two executors.**

### 2. ⛔ Do not reroll on upgrade

PoE's Blessing orbs reroll everything and **that is the documented complaint.** Affixes carry across
unrerolled, exactly as promotion does — **subject to §2a, which is not optional.**

### 2a. ⛔ Affix-pool legality and the implicit swap — the two rules the guard ladder demands

**Rule 1 — the successor's affix set must be legal on the successor's own `affix_pool_tag`.**
Carrying an `armour-cloth`-pool affix onto a plate chassis creates an item the drop path cannot roll
and removes cloth's only compensation (`ssot-item-categories.md:629-631`, `:746-747`). An upgrade
whose affix set is not legal on the successor **refuses**; it does not silently relabel.

⚠ **This makes the upgrade lossy or refusing, and that is a real design choice, not a detail.** Three
shapes exist and only the first is safe by default:

| Shape | Verdict |
|---|---|
| **Refuse** when any affix is illegal on the successor's pool | ✅ **v1.** Consumes nothing, explains itself, and cannot produce an unrollable item |
| Drop the illegal affixes | ❌ Silent value loss on a consumed input |
| Re-tier them into the successor's pool | ❌ That is a reroll, banned by §2 |

⛔ **ERRATUM 2026-09-21 (found while building T37's production caller — Rule 1 cannot be implemented from today's corpus as written).** Rule 1 names `affix_pool_tag`, and that name is real: `ssot-item-categories.md:295` declares it a `TEXT NOT NULL` column (*"the key I8's pool generator filters on — `armour-plate`, `weapon-nozzle`"*), with worked values at `:532`, `:572` and `:599`. But **no shipped base-type row carries it** (`gk-data/packs/fusion/data/seed/items/base-types/**` carries `class`, `band`, `role`, `implicit`, `socketMax`, `tags`, `enhanceTrack`), and **no affix-family row carries it either** (`gk-data/packs/fusion/data/seed/items/affix-families/**` carries `roles` — a per-role allow-list — plus `powerBand`, `frames`, `side`). The only corpus files that mention a pool tag at all are `uniques/*` and `_exemplars/*.json`. A runtime executor therefore has nothing to compare: it can read neither the successor's pool tag nor an affix's.

**Two ways out, and the choice is a design decision, not an implementer's call:**
1. **Emit the column** — author `affix_pool_tag` onto base types (and the matching pool key onto affix families) in the generator, regenerate, and Rule 1 reads exactly what this spec says; or
2. **Re-express Rule 1 over the data that exists** — the successor's own `role`/`class` against each affix family's `roles` allow-list (and its `powerBand`/`frames`), which is the corpus's real legality shape today.

⛔ **Until one of those lands, T37's affix-legality rule is proven only against caller-supplied data** (the pure policy's own tests) and **must not be claimed as production-enforced**. Same class of defect this module's history keeps catching: a rule that reads correct and has no field behind it.

⭐ **RESOLVED 2026-09-21 (the executor's own call, recorded here because the row's spec owns the decision).** Rule 1 reads **option 2**: the successor's own `role` and `frame` against each carried affix family's `roles` allow-list (plus its `powerBand`/`frames`/`side`, which the same corpus rows already carry). Reasons, in order of weight: (a) the data exists today, so the rule becomes production-enforced in this commit instead of waiting on a generator pass; (b) it is the *same* filter the drop path already applies when it rolls an item's affixes — "what this chassis can roll" is what `roles` means — so the upgrade agrees with the drop corpus by construction rather than by a second vocabulary; (c) the `affix_pool_tag` column stays the eventual home for an authored pool key, and the executor takes its legality through **one injected predicate**, so switching the source later is a wiring change in one place, not a rewrite of the rule. ⛔ The generator pass that would emit `affix_pool_tag` is **not** required for v1 and is not silently assumed: nothing in this module reads that column today.

**Rule 2 — the implicit change is presented before the input is consumed.** The successor's
`implicitFamily` comes from its own row in `classes.v3.json` `implicitSlates` and will usually differ.
The card must show the outgoing and incoming implicit, under the **same refuse-never-warn posture**
this spec already applies to requirements — the input is consumed and there is no undo.

### 3. ⛔ Do not claim to be the named successor

D2 had to put a wiki warning on this. An upgraded `cloth` piece becomes a **`leather` chassis carrying
its own identity** — it is not "a Leather Vest." **The card must say so**, and this is a requirement,
not a nicety.

### 4. ⛔ Requirement creep is the live risk

~~⛔ `requirement-profiles` is **unbuilt** (above), so this rule is specced and **cannot be built until module 23 ships**.~~ ✅ *Shipped as T35–T36 (2026-09-18 re-verify) — the rule is buildable against `RequirementProfileResolver`; the snippet below names the intent, not the shipped method names, which T37 must read first.* **An upgrade that raises a requirement past what the owner can meet is
a downgrade wearing a better name.** The executor must check the resulting requirement against the
owner **before** consuming the input, and refuse with a message naming the unmet requirement.

⭐ **Refuse, never warn-and-proceed.** The input is consumed; there is no undo.

### 5. Risk comes from the ladder

⛔ **Upgrade has no failure chance of its own.** Risk is a property of the item, in
`craft-risk-ladder`. The input is consumed on success; a refusal consumes nothing.

---

## The executor's consume-and-replace seam (designed 2026-09-21, T37 slice 3)

This is the part the corpus, the tuning and the store shapes had to settle, so it is written down before it is built. It mirrors an existing verb exactly — `RpgStore.TrySpendSocketInsertAndApply` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Workbench.cs:192`) already does "debit + write the op + save a freshly minted instance, in one transaction" — so this adds a *sibling* of that method, never a second transaction model.

**The cost is the input instance itself, plus souls.** Souls are priced per class rung by the
`operations.upgrade` souls leg in the shipped materials tuning — `coefficient × (rung + 1)`, the leg's own
`rung` variable, with **no recipe `soulsCostBand` and therefore no band multiplier and no species
multiplier**. That is the one way this verb's price differs from every recipe-priced verb, it is deliberate
(there is no recipe — the consumed item IS the material cost), and it is pinned by
`gk-core/tests/FusionRpg.Core.Items.Tests/Items/ItemUpgradeCostContractTests.cs` rather than left to inference. The price
is built in the executor as `MaterialCostLine.Souls(qty)` (`MaterialRecipeCatalog.cs:72`), and the preview
and the commit build it from the SAME helper — `ItemUpgradeEndpointTests.ThePreviewQuotesExactlyWhatTheCommitSpends`
pins that the quoted price equals the spent one, because a preview that misquotes is a player-facing defect.
An *item* is not a `MaterialClass`, so the consumed instance is expressed on the mutation rather than as a
cost line, and no recipe row is generated.

**The Data seam.** A new store method, sibling to the socket-insert one:

```csharp
// RpgStore.Workbench.cs — one transaction via TrySpendRecipe, like every sibling verb
public WorkbenchApplyResult TryUpgradeAndApply(
    long playerId, string recipeId, IReadOnlyList<MaterialCostLine> lines, string correlationId,
    WorkbenchMutation consumedMutation,   // Kind = Upgrade; InstanceId = the CONSUMED instance
    InstanceRow successorInstance, string successorInstanceId,
    ItemGenerationStamp successorGeneration, string? playerKey = null);
```

Inside `perform`, in this order, all on the same connection and transaction:
1. `AppendMutationOpUnlocked` for the **consumed** instance with `MutationOpKind.Upgrade` — the op ledger's `instance_id` stays the input's, so the upgrade reads as that item's own history, and it is the same append every other verb's mutation half uses (a refusal throws `WorkbenchApplyRefused` and rolls the debit back — D2 clause 11, both directions);
2. `MarkItemDestroyedUnlocked(db, owner, consumedInstanceId)` — the salvage-shaped disposition T23 established (⛔ never `DeleteInstance`: the op ledger must keep a readable item);
3. `SaveInstanceUnlocked(db, tx, successorInstance, successorInstanceId)` — the successor's `effect_instance` + atoms under its own new id, the same call the socket-insert verb uses;
4. the successor's `item_generation` row (`base_type_id` = the successor; `drop_log_id` = the consumed row's own value so provenance keeps pointing at the original acquisition; plus the successor's `frame`/`role`) — the INSERT shape at `RpgStore.Loot.cs:650`;
5. the returned `OutcomeRef` is the **successor's** instance id, so the caller and the card read the new item, never the consumed one.

**Replay and idempotence are inherited, not re-invented:** `TrySpendRecipe` short-circuits a replayed `(playerId, correlationId)` before `perform` runs, and `SaveInstanceUnlocked`'s `ON CONFLICT UPDATE` makes a repeated perform converge rather than collide — the two properties the socket-insert verb already proves.

⭐ **WEAR AND POTENTIAL CROSS BY USED FRACTION — audit 2026-09-21 (lane sgc-1): the design the code owes.**
The successor is a NEW instance, and `SaveInstanceUnlocked` writes neither `durability_current` nor
`craft_potential_current/max`, so both pairs are **derived fresh** on first read (`RpgStore.InstanceOps.cs:35,83`)
while the consumed item's used fractions are disposed with it. Two consequences: `Upgrade` is a strictly better
repair than `Repair` (a 1%-durability piece yields a pristine successor), and the potential-reset loop Open
question 3 warns about — *"with the used fraction carried across — otherwise upgrading becomes a
potential-reset loop, which is the exact escape hatch the risk ladder exists to close"* — is open in the shipped
write. **Rule (both pairs, one transaction):** carry the input's USED FRACTION onto the successor —
`SetDurabilityCurrentUnlocked` for durability and the head-pair writer (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.InstanceOps.cs:42`) for potential, on the
successor's id, inside `TryUpgradeAndApply`. ⛔ The alternative (refusing to upgrade a worn or
potential-exhausted item) is a product decision nobody has ruled on and is NOT taken. Filed as **T60**.

⭐ **BOTH PAIRS NOW CROSS — T60 (durability half landed 2026-09-21; potential half 2026-09-22).**
`RpgStore.TryUpgradeAndApply` takes `successorDurabilityCurrent` and `successorPotentialCurrent` and writes each
on the successor's own id inside its transaction; `ItemWorkbench.Upgrade` computes each from the input's RAW
`current` against the two DERIVED maxes (the input's own chassis + rung, then the successor's) — `checked`,
multiply-first, divide-last, and only the `current` ever crosses. A caller with no wear source carries nothing,
so the successor's pair stays underived and derives its own full max on first read rather than a value being
invented from a missing input. ⚠ **The potential carry IS the upgrade's potential consumption:** the
successor's own max already absorbs the input's spend, so a `potentialCostPerVerb[upgrade]` decrement beside it
would charge the same craft twice.

**Hub bindings are withdrawn by absence — and that required clearing the LOADOUT, found by the Data probe (2026-09-21).** Step 2 disposes the consumed instance, so the withdraw-on-absence machinery (`RpgStore.Items.cs` `ApplyEquipProjection`'s reaper, reached through `MaterializeRolledEquipRuntime`) drops its bindings on the next reconcile — ⛔ use it; a second withdrawal path is the defect that machinery exists to prevent. But the probe proved the first implementation was WRONG: an assignment row that still names the consumed instance keeps it in the projection's own `desired` set, so the reaper kept its binding — a live binding on a **destroyed** item, which would go on composing its atoms. `TryUpgradeAndApply` therefore clears the consumed instance's rows from `rpg_item_assignment` and `rpg_player_item_assignment` inside the same transaction, and the EXISTING reconcile then withdraws by absence. ⚠ Re-pointing the loadout at the SUCCESSOR instead is a UX decision nobody has ruled on, so it is deliberately not invented: today the piece leaves the loadout and the successor is equipped like any other item.

**The successor's container comes from the one container builder, and the carried affixes are the consumed instance's own atoms.** `EquipmentContainerBuild.From(grant, lookups)` (`gk-core/src/FusionRpg.Core/Items/EquipmentContainerBuild.cs:47`) is the single place a container is built, and it needs a `LootGrant` carrying the successor's `BaseTypeId`/`Frame`/`Role` (`gk-core/src/FusionRpg.Core/Items/Drops/LootPipeline.cs:40`) — so the executor synthesizes that grant for the successor chassis rather than assembling a container by hand. ⚠ **What `From` returns is the chassis and its POOL, not an item's rolled affixes:** its `Affixes` map is the pool's backing and its tier range comes from the grant's `MinTier`/`MaxTier`, which is exactly what a *drop* needs and exactly what an *upgrade* must not re-roll. Therefore the successor's `InstanceRow.Atoms` is the **consumed instance's own atom list, unchanged** (identity, tier, value — the `InstanceAtomRow` shape at `gk-core/src/FusionRpg.Core/Effects/Atoms/Instantiator.cs:26`), and the container is what changes. ⛔ A caller that let `From`'s pool resolution decide the successor's affixes would be performing the reroll §2 forbids, and a caller that re-rolled to "fill the successor's slots" would be doing it one step later — the carried atom list *is* the affix set.

**Where the plan comes from.** The executor resolves the successor from the authored edges, read at boot
into a hub beside the other tunings, and builds `ItemUpgradeNode`s from the base-type corpus before
calling `ItemUpgradePolicy.Decide` for the refusals — absent edge, top rung, standard gear, illegal
affix, unmet requirement — *before* anything is spent. Only an `Ok` decision reaches
`TryUpgradeAndApply`.

⛔ **Which FILE the runtime reads — corrected 2026-09-21.** The runtime reads the EMITTED CORPUS field
(`successorOf` on `gk-data/packs/fusion/data/seed/items/base-types/**` rows, via `ItemUpgradeEdgeCorpusReader`), not the
authoring registry. The registry (`_registry/successor-edges.v1.json`) keeps its own two jobs — it is the
generator's INPUT and the closure gate's subject — and the earlier text here ("read at boot from
`_registry/successor-edges.v1.json`") was wrong in a way worth naming: the generator wrote `successorOf`
onto the corpus and **nothing in `src/` read it** (a grep found only refusal-message strings), so the same
fact lived in two places while the emitted field had no reader. One fact, one runtime source: the corpus
the host actually ships beside the base types.

**The preview surface (2026-09-21).** `ItemWorkbench.UpgradePreview` + `POST /api/items/workbench/upgrade-preview`
run the SAME decision through the same private `DecideUpgrade` path and write nothing at all — no spend,
no op row, no instance write — returning the successor chassis, the outgoing and incoming implicit, the
carried affix count and the souls price. That is what Rule 2 and Success criterion 5 need before the
input is consumed, and it needs the base type's own `implicit.family`, which no store table carries:
the host reads it off the base-type seed corpus at boot (`BaseTypeSocketMaxCorpus.LoadImplicitFamilyById`,
the third lookup beside `socketMax` and `class`). ⛔ With no implicit lookup wired the preview shows no
implicit rather than inventing one. The Workbench's Craft bench renders that preview (`UpgradeSwapLine`) and keeps its
commit disabled until a preview succeeded, so the swap is on screen **before** the piece is consumed,
and the line says in words that the result is a chassis carrying its own identity rather than the named
successor (Success criterion 5).

⛔ **What the runtime can and cannot see — found while implementing (2026-09-21), and it changes two
of the shapes above.** `RpgStore.GetBaseType(baseTypeId)` returns **`(Frame, Role)` and nothing else**
(`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.BaseTypes.cs:77`): the class, the band and the implicit family are
*seed-file* facts, never persisted, so the executor cannot read a base type's `class`/`band`/`implicit`
from the store. Two consequences:

1. **The rung/ladder shape check is not a production input.** With the 2026-09-21 ruling the authored
   edge IS the authority on which chassis follows which, and the corpus exposes no class or band at
   runtime, so `ItemUpgradePolicy`'s `Successor.Rung == Input.Rung + 1` / same-ladder check is a
   *content-time* invariant (checked by T38's closure check and by `ItemSeedValidator`), not a
   runtime one. The runtime's own checks are: an edge exists, the successor resolves, it is the **same
   frame**, its affixes are legal, and the requirement is met. The implementation therefore passes nodes
   with no rung data and the policy must not invent one — ⛔ never default a rung to 0 and compare, and
   never re-derive a ladder from `frame`/`role`.
2. **The implicit change is presented from the container, not from a column.** The card's outgoing /
   incoming implicit comes from the built container (`EquipmentContainerBuild`), which is where the
   implicit slate lives, not from `item_generation` (which carries no implicit column — see step 4 of
   the seam above). So "the implicit change is shown before the input is consumed" is satisfied by the
   **preview** half of the verb ([`ItemUpgradePolicy`'s plan, both implicits named] + a read-only
   endpoint), not by a stored field.

### Requirement profiles — why the upgrade passes `null`, designed 2026-09-21

§ 4 says an upgrade that raises a requirement past what the owner can meet is a downgrade wearing a
better name, and that the executor checks the RESULTING requirement before consuming. The executor seam
is built and tested (`ItemUpgradeRequest.SuccessorRequirement` + `RequirementTrialEvaluator`), and the
verb passes `null`. That is a recorded dependency, not an oversight, and this is the reading it rests on
(checkable, all four by grep over `src/`):

| Fact | Command | Reading |
|---|---|---|
| Requirement profiles are not persisted anywhere | `grep -rn "requirement_profile" gk-core/src/FusionRpg.Data/Sqlite/*.cs` | no hits — no column, no row, no reader |
| Their tuning is never boot-loaded | `grep -rn "RequirementTuningHub\|RequirementProfileTuningHub" --include=*.cs src/` | no hits — nothing configures it outside tests |
| Nothing outside the module reads a profile | `grep -rln "RequirementProfile" --include=*.cs src/` | only `Items/Requirements/**` and this policy |
| The trial runs in exactly one place, and it is this module's | `grep -rn "RequirementTrialEvaluator\|RequirementProfileResolver" --include=*.cs src/ \| grep -v "Items/Requirements"` | one hit: `ItemUpgradePolicy.cs:175` |

**So a runtime profile does not exist yet — not for drops, not for equipment, not for a card.** Wiring the
upgrade to resolve one would make this verb the ONLY place in the game where a trial is evaluated: a
dropped item of the same chassis would demand nothing while an upgraded one could demand a trial and
refuse, which is precisely the kind of second, inconsistent rule this module's own erratum history keeps
catching (the two-source successor, the armour-only scope, the pool tag with no field behind it).

**Decision (this module's, recorded here as the design the code follows).** The upgrade keeps passing
`null` until requirement profiles are wired at runtime as a whole:

1. **persist a profile per item at generation** — the resolver exists (`RequirementProfileResolver.Resolve`,
   seeded, replay-identical) and needs a column beside `item_generation` plus a boot-loaded tuning;
2. **enforce it once, in the shared equip/admission path**, so every item of that chassis is judged the
   same way rather than only upgraded ones;
3. **then the upgrade passes the successor's own profile**, and the carry-vs-redraw question answers
   itself: a profile is a property of the item's own generation, so what crosses is the profile the
   successor would have been generated with — never a fresh draw the player could not have predicted
   from the item they are holding. Re-drawing at upgrade time is the variant that would make an expected
   purchase fail for a reason the player cannot see, and it is rejected here.

⛔ **Until step 1 lands the executor must not claim rule 4 as production-enforced.** The policy-level
rule is real and tested; the wire is owed, and the owning surface is requirement-profiles' runtime half
(the module whose resolver T35–T36 pulled forward), not this one. The verb's refusal code
`upgrade.requirement-unmet` exists and is unreachable in production today — deliberately, and said here
rather than left to be discovered.

⚠ **And step 1 is itself gated on another lane's deliverable, found 2026-09-21 while mapping it.** The
resolver needs `contentTheta`, `pTheta` and a `PowerVector` (`RequirementProfileResolver.cs:28-30`), and
an instance carries only `ThetaContent`/`ContentScaleMilli` (`Instantiator.cs:55-56`) — its per-atom
power is **null on every row by design**: *“`PowerJson` stays null on every row: power is backfilled
later (E9), never computed on [the fly]”* (`InstanceProducer.cs:51`). So a profile cannot be resolved at
generation today, because the two magnitude inputs do not exist yet, and the ordering is: **per-atom
power (E9) → a profile can be resolved and persisted → the shared equip-time enforcement → this verb
passes the successor's profile.**

⛔ **No fallback P(Θ) is invented here to paper over that.** The resolver's own band lookup refuses an
unreachable magnitude (`power-out-of-band`, `RequirementProfileResolver.cs:52-54`), so a made-up number
would not merely be imprecise — it would mint a trial the item never earned and demand it of the player.
Rule 4 therefore waits for the power backfill, and this module's contribution is the seam, the rule and
this dependency statement.

⚠ **And the backfill is a subsystem wiring job, not a side quest — checked 2026-09-21.** A pricer DOES
exist (`PredicatePricer.PriceTree(PredicateNode?, PowerTables, int floorMilli)`) but **nothing in `src/`
calls it** — a grep for `PredicatePricer.` outside its own directory returns nothing — and it prices a
predicate TREE against `PowerTables`, so using it means building each atom's predicate tree, supplying
the tables and choosing the floor. That is E9's own semantics (how power is measured), and reproducing
them inside an upgrade verb would be a second, divergent source for the same number — the defect class
this module has already caught three times. So the dependency is recorded as a subsystem dependency,
not as "a helper we could call": E9 wires the pricer, the per-atom power lands, and then the profile
can be resolved.

## Tech stack

C# .NET 8 (`FusionRpg.Core/Items`, `FusionRpg.Server`, `FusionRpg.Data`), xUnit. No new dependency.

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Upgrade"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Recipe"
dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~InstanceOp"
dotnet run --project gk-forge/tools/ItemSeedValidator
dotnet test gk-core/tests/FusionRpg.Server.Tests
python gk-core/scripts/guard-dal.py
python gk-core/scripts/audit-overflow.py
```

## Project structure — ⚠ as PLANNED 2026-09-13, with what shipped beside each row

| Path | Role | Shipped as |
|---|---|---|
| ~~`gk-data/packs/fusion/data/seed/items/_registry/classes.v3.json`~~ | ~~Successor edges — a reviewed, additive registry change~~ | ⛔ **Struck by the 2026-09-21 ruling:** the edges are authored per base type in the NEW `gk-data/packs/fusion/data/seed/items/_registry/successor-edges.v1.json`, and `classes.v3.json` is untouched (it is `frozen: true`, and per its own `rungCountRationale` it orders weight, not power) |
| `gk-core/src/FusionRpg.Core/Items/Mutation/MutationOp.cs` | The new `op_kind` member | `MutationOpKind.Upgrade` + its `MutationOpKinds.Id` case (the thirteenth member) |
| `gk-core/src/FusionRpg.Core/Items/…/UpgradePolicy.cs` | Pure resolve, requirement check | `gk-core/src/FusionRpg.Core/Items/Mutation/ItemUpgradePolicy.cs` (+ `ItemUpgradeEdges.cs` for the authored edge table and its boot hub) |
| `gk-core/src/FusionRpg.Server/ItemWorkbench.cs` | The **eighth** verb (six ship today: `Salvage` :164, `Upcycle` :194, `Enhance` :240, `SocketAdd` :293, `SocketInsert` :338, `SocketImbue` :378; `rarity-promotion` adds the seventh) | `ItemWorkbench.Upgrade` + `UpgradePreview`, sharing one private `DecideUpgrade`, with `POST /api/items/workbench/upgrade` and `…/upgrade-preview` |
| `gk-core/src/FusionRpg.Core/Items/Materials/CostClassMatrix.cs` | ⛔ The **eleventh `CraftOperation`** member — closed, ask-first | `CraftOperation.Upgrade` (the twelfth, after T23's `Repair`) + its `Id` case and its empty `CatalystFor` cell |
| ~~`gk-data/packs/fusion/data/seed/items/recipes/recipes.json`~~ | ~~**Generated** — regenerated via its generator~~ | ⭐ **Not needed:** the upgrade has no recipe row — its price is the `operations.upgrade` souls leg and the consumed item itself, so no generator run is involved |

## Code style

```csharp
// Check the RESULTING requirement against the owner BEFORE consuming the input — D2's documented
// failure is an upgrade that raises a requirement past what the owner can meet, a downgrade wearing a
// better name. REFUSE, never warn-and-proceed: the input is consumed and there is no undo.
//
// ⚠ As SHIPPED, the call is the trial evaluator's, not a `RequirementProfile.Met` (no such method
// exists) — and it runs only when the caller supplies a profile, which today is nobody in production
// (see § Requirement profiles: no runtime profile exists until E9's per-atom power lands):
var trial = RequirementTrialEvaluator.Evaluate(requirement, ownerLevel, allocation);   // ItemUpgradePolicy.cs
if (!trial.Ready) return Refuse("upgrade.requirement-unmet", $"the successor requires {trial.Unmet}");
```

---

## Tunables

| Number | Meaning | Owner |
|---|---|---|
| `upgradeCostSoulsMilli` per class rung | the souls `coefficient` on `operations.upgrade`'s leg, `variable: "rung"` — the price is that coefficient above the rung floor and takes no band or species multiplier (the verb has no recipe) | the shipped materials tuning's `operations.upgrade`, published through `gk-core/tools/tuning/publish.py` (currently `materials.v5.json`); the row is on the power-scale §10 ledger |
| `successorOf` per base type (every ladder) | Which specific chassis a given one upgrades into — **authored content, never a formula and never a ladder derivation** | ⭐ **Built (T38, 2026-09-21):** `gk-data/packs/fusion/data/seed/items/_registry/successor-edges.v1.json` `edges` (source base-type id → successor id) read by `seedsmith/adapters/items/basetypegen/successor_edges.py` and injected by `basetypegen/emit.py::assemble_entry`. An entry with no edge carries **no key at all**, so the table shipped empty changes nothing in the corpus. ⛔ **No `classes.v*.json` change at all** under the ruling ★ |

⚠ **`upgradeCostSoulsMilli` prices on a rung, so it is a cost ladder and owes a
`ssot-power-scale.md` §10 row** — the same ask `rarity-promotion` files.

⛔ **No hard progression ceiling.** A configurable soft cap, never a hard stop.

**Structural (stays `const`, with a comment saying why):** the **no-reroll** rule and the
**consume-exactly-one-input** rule. They are the contract, not balance.

## Numeric types

- Costs are **`long`** and price on a rung, so they scale with the ladder.
- **Widen before multiplying; divide by 1000 last, exactly once; overflow throws, never wraps.**
- **Floating-point is allowed** (owner ruling 2026-09-15) — a `float` not being integer-exact past 2^24 is precision, not overflow.
- Class `rung` is a small identity `int` — an ordering position, **never a magnitude and never a
  multiplier.** An upgraded item is not a scaled item; its magnitudes come from its new base type
  through the paths that already exist.

## ActorHub gate

**Contributes nothing; consumes nothing.** An upgraded item grants stats through the existing
equipment path into `ActorHub` — it is a different base type wearing carried-over affixes, and both
halves already compose today.

⛔ **No `*Composer*`, no private fold.** `guard-actor-hub.py` stays green.

⚠ **One real consequence:** the upgraded instance is a **different instance**, so any Hub binding held
against the old one must be **withdrawn**. The withdraw-on-absence machinery already exists
(`RpgStore.Items.cs:846-859`) — use it; do not write a second one.

## Testing strategy

**Store tests run in memory**; a failed temp-delete is a **failure**, never `catch { }`.

| Level | What it asserts |
|---|---|
| Unit | ⭐ **Affixes carry across identically** — identity, tier and value, for every affix |
| Unit | The input instance is **consumed**; exactly one output exists |
| Unit | ⭐ **A refusal consumes nothing** — the input survives an unmet requirement, byte-identical |
| Unit | An upgrade raising a requirement past the owner's **refuses**, naming the unmet requirement |
| Unit | The successor is `rung n+1` within the **same (ladder, frame)** — never across frames |
| Unit | Top-rung upgrade refuses cleanly |
| Unit | ⭐ **A base type with no authored edge refuses by name** — never derived from its class ladder; armour included |
| Unit | Hub bindings against the consumed instance are **withdrawn** |
| Unit | Upgrade has no private failure chance |
| Unit | `checked` throws rather than wrapping |
| Integration | Full round trip: upgrade, re-equip, verify stats compose from the new base type |
| Contract | `ItemSeedValidator` green; every successor edge resolves; the registry change is **purely additive** (every id legal before is legal after) |

⛔ **No test asserts a recipe or item count.** Readings.

## Boundaries

**Always**
- Check requirements **before** consuming.
- Carry affixes across untouched.
- Make the card say the item is a *chassis carrying its own identity*, not the named successor.
- Withdraw Hub bindings against the consumed instance using the existing machinery.
- Keep registry changes purely additive, argued from `minCompatibleVersion` / `stage1aFrozen` (**not** from `v4Note`).
- Commit with plain `git` (explicit paths).

**Ask first**
- ⛔ **The `MutationOpKind` member** — closed, ask-first, and **third in the queue** behind `Repair`
  and `Elevate`.
- ⛔ **Any change to `classes.v*.json`.** They are `frozen: true` with `minCompatibleVersion`, and
  `stage1aFrozen` records that *"a change to this registry invalidates authored content unless
  minCompatibleVersion says otherwise."*
- ~~Extending beyond the armour ladder (Open question 1).~~ ⛔ struck 2026-09-21: the ruling makes
every ladder's successors authored edges, so there is no armour-only scope to extend beyond; what
stays ask-first is **authoring edges** (content) and the §10 cost row.
- The §10 row for the cost ladder.

**Never**
- ⛔ **Reroll on upgrade.** PoE's documented complaint.
- ⛔ **Deriving a successor from the weapon or offhand ladder.** Those orderings are style and
  category axes. ⚠ **An earlier draft said "This is not a scope cut - it is a correctness requirement"
  and then argued armour-only from the guard ladder's x1.4 / 2.3x evidence.** Both halves are
  superseded by the 2026-09-21 ruling: the correctness requirement is that **no** successor is derived
  from **any** ladder (armour included), and whether a base type upgrades at all is now a matter of
  whether an edge has been authored for it — content, not a per-ladder scope cut.
- ⛔ Consume the input before the requirement check passes.
- Claim the upgraded item is the named successor item.
- Give upgrade a private failure chance.
- Make class rung a magnitude multiplier.
- Add a hard ceiling to the cost curve.
- Assert a population count.

## Success criteria

1. An armour piece upgrades to the next rung within its own `(ladder, frame)`, consuming the input.
2. Every affix carries across identically.
3. A requirement the owner cannot meet **refuses, and consumes nothing** — proven byte-identically.
4. The card presents the result as a chassis carrying its own identity, not as the named successor.
5. ⭐ A weapon/offhand/jewel base type upgrades if it carries an authored `successorOf`, and
   **refuses by name** if it does not — never derived from the class ladder. Standard (commander gear)
   stays explicitly refused; it is not a progression ladder at all.
6. Hub bindings against the consumed instance are withdrawn via the existing machinery.
7. The registry change is purely additive; `minCompatibleVersion` semantics hold; `ItemSeedValidator`
   green.
8. No reroll, no private failure chance, no hard ceiling.
9. `guard-dal.py`, `guard-actor-hub.py` green; Core, Data and Server suites green.

## Open questions

1. *(Not a question — moved to Design §1.)* **DECIDED 2026-09-13 (owner): a separate, explicit
   `successorOf` field on the base type**, authored per chassis, never derived from any ladder.
   Authoring actual `successorOf` values for the ~800 non-armour base types is its own content pass
   and does not block armour or the executor mechanism itself.
2. **Does the upgraded item keep its `promoted_from_ordinal`?** It is a different base type but the
   same player's item. **Recommendation: keep it** — the mark answers *"was this natural?"* about the
   rarity, which the upgrade does not change.
3. **Does upgrade consume crafting potential, and does the successor inherit the remainder?**
   ⭐ **DECIDED and shipped (T60, 2026-09-22): consume, and derive the successor's afresh from its own base
   type with the *used fraction* carried across** — otherwise upgrading becomes a potential-reset loop, which
   is the exact escape hatch the risk ladder exists to close. The carry *is* the consumption (see § 3's "BOTH
   PAIRS NOW CROSS" note); no separate `potentialCostPerVerb` decrement is owed by this verb.
4. **Does the species binding survive an upgrade?** A set piece's `speciesId` is on the set entry, not
   the instance — so a chassis change may leave the set. **Recommendation: refuse to upgrade a set
   piece in v1**, and record it, rather than silently breaking a set bonus.
