# Spec: Craft risk ladder (`craft-risk-ladder`)

**Initiative:** `species-gear-chain` ([map](../species-gear-chain-map.md)) · **Module:** `craft-risk-ladder`
**Owning programs:** `item` module 15 (`enhance-reroll`) + `deployment-hierarchy` module 7 (`item-durability-repair`)
**Status:** spec, 2026-09-13. Awaiting owner approval. No build authorized. ⚠ *2026-09-18: approved through `tasks/species-gear-chain-plan.md`; build state — Stage 1 SHIPPED (T10 + T11, `f67930ac`); Stages 2–4 unbuilt (T23–T24).*
**Source ideal:** [gear-climb-ideal.md](../gear-climb-ideal.md) § Failure shape

> **Amended 2026-09-18 for owner ruling R-G1 (2026-09-17)** — `gear-climb-ideal.md` § Owner rulings.
> **Build state, verified against git rather than this header:** Stage 1 shipped in `f67930ace`
> (T10 + T11, 2026-09-16) — `CraftRiskPolicy.cs`, `HeadDerivationTables.cs`,
> `DeploymentHierarchyTuning.cs`, `gk-core/data/tuning/deployment-hierarchy.v1.json`. Stages 2–4 (T24, T23)
> are **unbuilt**: `CraftRiskPolicy.CanDecay` is still the `false` stub (`CraftRiskPolicy.cs:25`).
> What R-G1 changes here: **one durability pool, one unit, two formulas** (§ Design 3), the bands
> question is **answered — they stay** (§ Design 5), and R-G1's **consumable layer** is a new module,
> [`craft-assurance`](spec-craft-assurance.md), whose tuning is **one balance problem with this
> module's craft-wear table** (§ Tunables).

⚠ **This module carries SEVEN cross-program asks and must not be built until they are filed and
answered.** Three of them reopen **owner-locked** design. See § Cross-program asks.

---

## Objective

**Answer "can this craft hurt my item?" once, for every craft verb, with one graduated ladder.**

> **Owner, 2026-09-13:** *"make SSOT promote risk… potential is the default assurance for each item,
> but if it exhausted → cause item durability decay and can break and lost."*

| Stage | What the player sees | Mechanism |
|---|---|---|
| **1. Assured** | Crafts simply work | Each item carries **crafting potential**. While it remains, a craft spends materials and **always succeeds** |
| **2. Strained** | "This piece is wearing out" | Potential exhausted. Crafting is still *allowed*, but each attempt now **decays durability** — a visible, accumulating cost, not a hidden dice roll |
| **3. Broken** | The item stops working, but is still yours | Durability at zero ⇒ **unusable until repaired, never destroyed by wear** |
| **4. Lost** | The repair failed | The **repair attempt** carries the tunable destruction chance `spec-item-durability-repair.md` already specifies |

**What this buys over either half alone:**

- **The player always sees it coming.** D4's rejected mechanic was an RNG brick on a finite,
  *invisible* attempt budget applied to a once-in-a-season item. Here the budget is visible, its
  exhaustion is announced by a state change, and the destructive step is a **separate, opt-in action**.
- **Risk becomes a property of the item, not of the verb.** One ladder serves promotion, temper,
  reroll and socket work — so we never answer *"does this verb brick?"* eleven times.
- **It keeps promotion honest.** Promotion stays additive-only; nothing is re-rolled, so nothing is
  ruined by the craft itself. What degrades is the chassis, which is a different axis.

---

## ⛔ The locked anchor this must not break, and the proof that it doesn't

`deployment-hierarchy/spec-item-durability-repair.md` **D1 is a locked anchor**, quoted verbatim:

> *"An item at zero durability is unusable until repaired (**never destroyed by wear alone**), but
> every repair *attempt* — field or workbench — carries a tunable failure chance that destroys the
> item permanently instead of restoring it."*

The owner's chain (exhausted potential → decay → break → loss) is **compatible with D1 without
amending it**, provided the decay never destroys directly. It does not: decay drives the item toward
zero, and the loss — if it happens at all — occurs at the **already-specced repair step**, which
already has its persistence in the closed four-value `rpg_item.Disposition` vocabulary
(`owned | salvaged | transferred | destroyed`, `RpgStore.Items.cs:71-73`).

⭐ **So this module adds no new destruction mechanism. It adds one new decay source beside battle
wear, and routes everything else through paths that already exist.**

### ⛔ And one hard constraint found by reading the enum rather than the design

`MutationOp.cs:50-53`, on `EnhanceOutcome`:

> *"**There is no destroy outcome — not as an enum value, not as a reason code.** A code nothing emits
> is a lie in a table, and reserving one invites a later session to wire it up."*

**This module must not add one.** The craft path's outcomes stay exactly as they are. A craft past
exhaustion emits a *durability decrement*, not a destruction outcome — and the temptation to
"reserve" a destroy code here is precisely what that comment was written against.

---

## What exists today — verified against code and the module-7 spec

### Built

| Fact | Evidence |
|---|---|
| The exact column-migration shape this module copies: idempotent `ALTER TABLE … ADD COLUMN` | `RpgStore.InstanceOps.cs:101-116` (`enhance_level`, `enhance_pity_counter`, `mutation_seq`, `state_hash`, and since T10/T11 the potential and durability pairs); helper `RpgStore.cs:4125` (`EnsureColumn`) |
| The mutation ledger a craft op appends to, **idempotent per `(instance_id, correlation_id)`** | `RpgStore.InstanceOps.cs:121-129`, `UNIQUE INDEX ux_effect_instance_op_correlation` (`:144`) |
| `MutationOpKind` — exactly **ten** members, closed, *"adding a member is ask-first"* | `MutationOp.cs:13-48` |
| `CraftOperation` — a **separate** closed ten-member enum for *priced* operations | `CostClassMatrix.cs:11-44` |
| `EnhanceOutcome` has **no destroy outcome, deliberately** | `MutationOp.cs:50-53` |
| `rpg_item.Disposition` — closed four-value vocabulary a repair-destruction writes into | `RpgStore.Items.cs:71-73` (⚠ an earlier draft cited `RpgStore.ItemUniques.cs:71-73` — right line, **wrong file**; that range is `UniqueCounterPressure`/`UniqueAcquisition` wire mapping) |
| The derivation precedent: a load-time table over closed VALIDATED `class`/`rarity`/`tags`, `checked`, widen-first, divide-last `long`, **refusing at load on an unknown id, never defaulting** | `spec-item-durability-repair.md` §2 (`DurabilityTable.Build`), itself modelled on `PackFootprintTable.Build` |
| At-zero enforcement is a **filter**, not a new Hub gate | `spec-item-durability-repair.md` §6; the seam is `MaterializeRolledEquipRuntime`'s assignments query, `RpgStore.Items.cs:913-916` |
| **Stock-backed assignments never wear** — a fungible counter has no instance row to hold a pair on; only `ref_kind = "rolled"` rows can | `spec-item-durability-repair.md` § Locked anchors |
| The `operations.{verb}` tuning shape, ten rows, legs scaled by a named `variable` class | `gk-core/data/tuning/materials.v1.json` |

### Real gap

| Gap | What must be built |
|---|---|
| Crafting potential storage | Two more nullable columns on `effect_instance`. **This module's own job** |
| Potential derivation + override | A `PotentialTable.Build` mirroring `DurabilityTable.Build` |
| The craft-time decay source | One decrement applied at craft settlement when potential is exhausted |
| Durability itself | ⚠ *2026-09-18:* **storage, derivation and the at-zero filter shipped** as the pulled-forward durability slice a (T11, `f67930ac`; `RpgStore.InstanceOps.cs:37-39` reads the pair). Workbench repair (slice b, T23) is still unbuilt. Original text: **Module 7 is unbuilt** … **hard build dependency on module 7 shipping first** — the ladder's stages 2–4 have nothing to decay |
| `data/tuning/deployment-hierarchy.v{n}.json` | ⚠ *2026-09-18:* **exists** — `v1` (T10/T11) and `v2` (`ecc18cf3`, magic-numbers sweep); `DeploymentHierarchyTuning.cs:6` reads v2. Stages 2–3 publish **v3** through `publish.py` (map § Tuning revisions). Original text: does not exist on disk; whichever lands first creates it |

⚠ **This reorders the map's Layer 0 placement, honestly.** The map lists `craft-risk-ladder` with no
dependencies. That is true of its *design*, not its *build*: stages 2–4 require durability to exist.
**Stage 1 (potential + assured crafts) is genuinely independent and can ship alone**; stages 2–4 wait
on module 7. Recommend splitting on that line — see Open question 4.

---

## Design

### 1. Storage — two more columns on `effect_instance`

Exact `enhance_level` / durability precedent, nullable at the column level:

```
EnsureColumn(db, "effect_instance", "craft_potential_max",     "INTEGER");   -- NULL until derived
EnsureColumn(db, "effect_instance", "craft_potential_current", "INTEGER");   -- NULL until derived
```

NULL is the correct *"not yet derived"* state for an instance imported before this ships — **never a
fabricated `0`** (which would read as exhausted) and never a fabricated full value. Derive and backfill
lazily on first read, mirroring `origin_values_json`'s lazy-write contract
(`origin_values_json` column `RpgStore.InstanceOps.cs:107`, its `COALESCE` write `:298`). Non-equipment instances never populate these columns.

### 2. Derivation — DERIVED, with an authored per-base-type override

> **Owner, 2026-09-13:** potential is **derived, with an authored override.**

`PotentialTable.Build(baseTypeEntries, tuning)` over the closed VALIDATED registry fields
`class`/`rarity`/`tags`, `checked`, widen-first, divide-last `long`, **refusing at load on an unknown
id rather than defaulting** — the `DurabilityTable.Build` shape, value for value.

⛔ **Two sources of truth is the known hazard here, so the rule is stated rather than assumed:**

- **The override is explicit or absent — never a sentinel.**
- **An absent override means *derive*.**
- **A present override must be a real authored value.**
- **A missing-but-expected override is a load rejection naming the base type** (`tunables-ssot.md`
  T5), never a silent fallback.

The derivation stays the default path; the override is the exception that has to justify itself.

### 3. Exhaustion — the decay source, in durability's own unit

```
craftWear = ceil(durability_max × craftWearPerAttemptMilli / 1000)
durability_current = max(0, durability_current - craftWear)
```

⭐ **The unit deliberately matches battle wear's** (`spec-item-durability-repair.md` §3:
`wear = ceil(durability_max × wearPerBattleMilli / 1000)`), so the two decay sources are **comparable**.
A balance pass can ask *"is one craft worth three battles?"* and read the answer off two numbers in
the same unit — which is the whole reason to match it.

⭐ **R-G1 (owner, 2026-09-17): one pool, one unit, TWO formulas.** *"You cannot calculate damage on
the item same at a attack hit and a craft time."* Sharing a **unit** is not sharing a **formula**:

| | Ruled |
|---|---|
| Pool | **One** — combat and crafting draw the same `durability_current` |
| Unit | **One** — per-mille of `durability_max` |
| Formula | **Two** — battle wear (module 7 §3, `wearPerBattleMilli`) and craft wear (this section) are separate mechanisms with separate inputs, each with **its own tuning table** |

So `craftWear` above is the **first** formula of the craft-wear table, not a copy of battle wear's.
The flat per-attempt shape is the starting point; whether craft wear **escalates** (each attempt past
exhaustion costing more than the last) is a property that table may gain in its balance pass. It is
**not** a structural choice this spec makes. Shipped today, the craft-wear table is one flat key —
`craftWearPerAttemptMilli` in `gk-core/data/tuning/deployment-hierarchy.v1.json`, read at
`DeploymentHierarchyTuning.cs:82` — and battle wear's `wearPerBattleMilli` is a separate key reserved
for module 7 in the same file's `sourceRef`. Keep them separate: if the craft-wear formula grows a
second input it becomes its own `craftWear` object in the next `deployment-hierarchy.v{n+1}.json`
publish (⚠ *2026-09-18:* the file on disk and in `DeploymentHierarchyTuning.cs:6` is now **v2** — T24's
revision is **v3** via `publish.py`), never a shared wear block with battle's keys. ⛔ *Corrected 2026-09-18 (strengthen pass — [map § Tuning revisions](../species-gear-chain-map.md), which reverses the map's § Corrections #11):* a revision publishes a **new** `<domain>.v{n+1}.json` through `gk-core/tools/tuning/publish.py` (tunables-ssot **T4**; the tool refuses to overwrite, `publish.py:556`), with the host's reader switched in the same commit — **never** an in-place `version` bump. The internal `version` field is not a revision identity (`sockets.v1.json` already reads `3` from in-place history). The number is not reserved here: it is whatever `publish.py` derives at build time, in the land order the map's table gives (for `sockets`, after strain-splice-host's `circuit-topology` v2 and `combo-budget`, per [strain-splice-host-map.md](../strain-splice-host-map.md) *Revision sequencing*).

⚠ An earlier version of this section said the two sources are *"comparable rather than separately
tuned."* **Struck by R-G1** — they are comparable **and** separately tuned.

**Idempotency key: `(instanceId, correlationId)`** — the unique index already exists, so a replayed
craft re-derives the identical decrement and never double-decays.

### 4. At-zero — a filter, never a new composer

A broken item stops granting stats by being **excluded from the assignments query** that already
withdraws no-longer-present sources (`RpgStore.Items.cs:913-916`, withdraw machinery at `ApplyEquipProjection` `:857-870`).
Module 7 owns that gate; this module adds no second one.

### 5. Enhancement's risk bands — ANSWERED: they stay (one vocabulary per question)

⛔ **The original design here — the bands fold into the ladder — was filed and answered "no" on
2026-09-15**, before R-G1 was written. `item-map.md` § *"Filed decision 2026-09-15 — ask #4"*:
**"The Safe/Risk bands stay."** The two own exhaustively different questions:

| Question | Owner |
|---|---|
| *Did this attempt succeed?* | `spec-enhance-reroll.md` §4's bands (`EnhancePolicy.SuccessMilli`) |
| *May this craft proceed, and at what cost to the item?* | This ladder |

That is also the split R-G1's consumable layer needs: an **assure** consumable acts on the first row,
a **protect** consumable on the second (`spec-craft-assurance.md`). Success criterion 7's *"or an
explicit, filed decision records why they stay"* branch is the one that was taken.

---

## Cross-program asks — file before building

| # | Ask | Against | Note |
|---|---|---|---|
| 1 | A new per-instance **crafting potential** pair beside durability's `(max, current)` | `deployment-hierarchy` module 7 | Module 7 is **owner-locked D1–D6** and written against shipped code, not idea-phase |
| 2 | Potential exhaustion as a **new decay source** | `deployment-hierarchy` module 7 | D1 holds unamended — decay drives to zero, only **repair** may destroy |
| 3 | Superseding `spec-enhance-reroll.md` §4's Safe/Risk bands | `item` module 15 | Reopens written design |
| 4 | Whether potential's derivation shares durability's `class`/`rarity`/`tags` table or a subset | `deployment-hierarchy` module 7 | Open question 1 |
| 5 | ⭐ A **`ssot-power-scale.md` §11 caps-register row** for `craft_potential` as a soft cap | `power` | § Caps above |
| 6 | ⛔ **An amendment to module 7's own Never list.** `spec-item-durability-repair.md:408` forbids *"per-item authored durability (max is DERIVED, **never authored, matching every sibling DERIVED field**)."* This module's design §2 is *derived **with an authored per-base-type override*** on a sibling per-instance head field of the same table. The owner decided the override (`gear-climb-ideal.md:350-352`), but **the decision has never been reconciled with `:408`**, and `gear-climb-ideal.md:273` contradicts itself by also calling it open. **File it; do not build through it** | `deployment-hierarchy` module 7 | § Design 2 |
| 7 | ✅ *Overtaken 2026-09-18: the file exists (v1, v2) with one parser, `DeploymentHierarchyTuning`.* **Schema ownership of `gk-core/data/tuning/deployment-hierarchy.v1.json`.** The file does not exist; this module is Layer 0 so it always creates it, yet module 7 owns most of its keys (`wearPerBattleMilli`, `repairDestroyChanceMilli`). Two independently written parsers over one file with a **throw-on-missing-section** posture (T5) is a build-order hazard. Agree the section layout before Stage 1 builds | `deployment-hierarchy` module 7 | § Project structure |

⚠ Module 15 is already carrying two other queued asks — `Repair`'s `op_kind`, and `Elevate`'s.
**`Repair` filed first** (`deployment-hierarchy-map.md:89`), so it takes the eleventh slot.

---

## Tech stack

C# .NET 8 (`FusionRpg.Core` policy, `FusionRpg.Data` storage), xUnit. No new dependency.
**SQL only inside `FusionRpg.Data`** — `guard-dal.py` enforces it.

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~InstanceOp"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Potential"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Durability"
python gk-core/scripts/guard-dal.py
python gk-core/scripts/guard-actor-hub.py
python gk-core/scripts/guard-test-substrate.py
python gk-core/scripts/audit-overflow.py
```

## Seedsmith / generator

**No generator involved.** Potential and durability derive at load from the base-type registry's
existing `class` field and the rung (`HeadDerivationTables.cs`); every number, including R-G1's
craft-wear table and the (still empty) `potential.overrides`, is authored runtime tuning in
`gk-core/data/tuning/deployment-hierarchy.v1.json`. The base-type corpus (`basetypegen`) is read, never
extended — this module adds no seed field.

## Project structure

| Path | Role |
|---|---|
| `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.InstanceOps.cs` | The two columns, beside the durability pair |
| `gk-core/src/FusionRpg.Core/Items/…/PotentialTable.cs` | Load-time derivation + override resolution |
| `gk-core/src/FusionRpg.Core/Items/…/CraftRiskPolicy.cs` | Stage resolution; pure, no I/O |
| `gk-core/data/tuning/deployment-hierarchy.v1.json` | Shared with module 7 — **one file, never two** |
| `gk-core/tests/FusionRpg.Data.Tests/Items/` | Migration + idempotency |

## Code style

The override rule is the thing most likely to be softened later, so it is enforced in code and said in
the message:

```csharp
// EXPLICIT OR ABSENT, never a sentinel (tunables-ssot.md T5). Absent means DERIVE. A base type
// listed in `potentialOverrideExpected` but carrying no value is a LOAD REJECTION naming the base
// type — a silent fallback here would make the derived and the authored path indistinguishable,
// which is exactly the two-sources-of-truth hazard this rule exists for.
if (expectsOverride && !overrides.TryGetValue(baseTypeId, out var authored))
    throw new PotentialTuningRejection(
        $"craft potential: base type '{baseTypeId}' is declared to carry an authored override but " +
        "none is present — an expected-but-missing override is a rejection, never a derive");
```

---

## Tunables

| Number | Meaning | Owner |
|---|---|---|
| `potentialBaseByClass` + `potentialRarityMultiplierMilli` | The derivation table | `gk-core/data/tuning/deployment-hierarchy.v1.json` |
| `potentialOverride` per base type | The authored exception | Same file |
| `craftWearPerAttemptMilli` | ⭐ Stage 2's whole tension. **Flat per-mille of durability `max`, the same unit as `wearPerBattleMilli`** — but **its own formula and table** (R-G1), never battle wear's. ⛔ **Tuned together with `craft-assurance`'s consumable magnitudes and boss drop rates, not before them** (R-G1: *"one balance problem, tuned together"*) — T24 ships the mechanism with the shipped starting value (`50`), and the measured pass that sets the real number covers both tables at once | Same file |
| Whether a given verb consumes potential at all, and how much | Some verbs may cost more potential than others | Same file, per `CraftOperation` id |
| `repairDestroyChanceMilli` | Stage 4 — **already module 7's**, not authored here | Module 7's keys |

### ⛔ Caps — PS-8, and why the recommended split must not ship alone

This spec types `craft_potential_max` as a **`long` magnitude on an endless-progression axis**, and
then caps it per item. `ssot-power-scale.md` PS-8: *"A cap on a magnitude is a progression ceiling
until proven otherwise… Everything else is a wall on the grind and needs a verdict in this table."*

**The full four-stage ladder makes it a SOFT cap, and that is the verdict:** at exhaustion crafting
**continues** (stage 2, at durability cost), the item is repairable, and D1 guarantees wear alone
never destroys. There is no point at which progression stops.

⛔ **But Open question 4's recommended Stage-1-only split removes exactly that continuation.**
*"Crafts are assured until potential runs out, **then they stop**"* is a **hard stop on a `long`
magnitude with no decay path and no restore verb** — which `AGENTS.md` forbids outright. So:

- **Stage 1 may not ship alone** without either (a) stage 2's decay, or (b) a restore verb that
  replenishes potential, or (c) an explicit owner verdict accepting a temporary hard stop.
- This module owes a **`ssot-power-scale.md` §11 row** registering `craft_potential` as a soft cap
  with stage 2 named as its continuation path. **Filed as cross-program ask 5 below.**

**Structural (stays `const`, with a comment saying why):** the ladder's four stages and their order.
That is the contract; a tunable that could reorder them would be a different feature.

## Numeric types

- `craft_potential_max` / `craft_potential_current`: **`long`**. They are per-instance magnitudes on
  an endless-progression axis, and `long` is the default for every magnitude.
- The decay computation is `checked`, **widens before multiplying** (`(long)max * milli`, never
  `(long)(max * milli)` — the cast binds to the *result*, so the multiply has already overflowed), and
  **divides by 1000 last, exactly once**.
- **Overflow throws, never wraps.** No silent `unchecked` on this path.
- `P(Θ)` is quadratic; a per-mille `int` exceeds its range at `Θ` = 3,213 (`CLAUDE.md` "Numeric types").
  Floating-point is allowed (owner ruling 2026-09-15 — precision is not overflow).
- `craftWearPerAttemptMilli` is a **bounded ratio** in `[0, 1000]`, bounds-checked at load — exempt
  from the magnitude rules and required to say so in a comment.

## ActorHub gate

**Neither contributes nor consumes.** A broken item is filtered out of the assignments query
*before* compose — the module never reads a Hub snapshot.

⚠ An earlier draft said *"Consumes Hub output only."* That is the wrong label: the mechanism below is
a `FusionRpg.Data` query filter, not a Hub read, and a later session could otherwise cite the line as
precedent for one.

A broken item stops granting stats by being **filtered out of the assignments query**
(`RpgStore.Items.cs:913-916`), which is module 7's specced gate — *"a filter, not a new Hub gate."*
The withdraw-on-absence machinery already runs at `:857-870` and needs no new logic.

⛔ **No `*Composer*` is introduced, and no private ChannelMods combat writer.** `guard-actor-hub.py`
must stay green. `BattleStatComposer` is grandfathered **debt until fused** and is **not** a pattern
this module may copy.

## Testing strategy

**Test substrate is a hard rule:** a store test runs **in memory**; disk only when the disk is the
thing under test; a failed temp-delete is a **failure**, never `catch { }`. An empty catch around
`Directory.Delete` plus SQLite connection pooling is what leaked 65.5 GB in one local run.
`guard-test-substrate.py` enforces it.

| Level | What it asserts |
|---|---|
| Migration | The two columns are added idempotently; running the migration twice is a no-op |
| Unit | NULL columns derive-and-backfill on first read; a pre-existing instance is **not** treated as exhausted |
| Unit | An absent override **derives**; a present one **wins**; an expected-but-missing one **throws naming the base type** |
| Unit | Unknown `class`/`rarity` id at load **refuses**, never defaults |
| Unit | While potential remains, a craft **always succeeds** and durability is untouched |
| Unit | Past exhaustion, a craft succeeds **and** decrements durability by the per-mille formula |
| Unit | ⭐ **Decay never destroys.** Durability floors at 0 and `Disposition` stays `owned` — the D1 assertion |
| Unit | ⭐ **No destroy outcome is emitted on a craft path**, and `EnhanceOutcome` gains no member |
| Unit | Idempotency: replaying `(instanceId, correlationId)` re-derives the identical decrement |
| Unit | Stock-backed (`ref_kind != "rolled"`) assignments never gain potential or wear |
| Unit | The decay computation `checked`-throws rather than wrapping at the boundary |
| Unit | `craftWearPerAttemptMilli` outside `[0, 1000]` is a load rejection |
| Guard | `guard-actor-hub.py`, `guard-dal.py`, `guard-test-substrate.py` green |

⛔ No population count asserted anywhere.

## Boundaries

**Always**
- Keep decay and destruction on **separate** paths. Decay drives to zero; only repair may destroy.
- Match battle wear's unit exactly, so the two decay sources stay comparable.
- Use `checked`, widen first, divide last.
- Write SQL only inside `FusionRpg.Data`.
- Run store tests in memory.
- Commit with plain `git` (explicit paths).

**Ask first**
- ⛔ **All four cross-program asks**, before any code. Two of them reopen owner-locked design.
- Adding any `MutationOpKind` or `CraftOperation` member — both are closed and ask-first, and
  `Repair` is already queued ahead.
- Creating `gk-core/data/tuning/deployment-hierarchy.v1.json` if module 7 has not — coordinate so there is
  **one file**, not two.

**Never**
- ⛔ Add a destroy outcome to `EnhanceOutcome` — *"a code nothing emits is a lie in a table."*
- ⛔ Destroy an item by wear. That is D1, and it is locked.
- Give any craft verb its own private failure chance. Risk is a property of the **item**, in one
  ladder — eleven verbs answering separately is eleven balance surfaces and eleven explanations.
- Use a sentinel for the override.
- Add a second ActorHub composer or a private fold.
- Let potential raise or lower durability `max`. They are independent head fields, exactly as
  durability and `enhance_level` are.
- Build stages 2–4 before module 7 ships.

## Success criteria

1. Every rolled equipment instance carries a derived `craft_potential` pair; pre-existing instances
   backfill lazily and are never mistaken for exhausted.
2. The override is explicit-or-absent, and an expected-but-missing one throws naming the base type.
3. While potential remains, **every** craft verb succeeds — proven across the priced operations.
4. Past exhaustion a craft succeeds and decays durability, in battle wear's unit.
5. ⭐ **No craft path can destroy an item.** Proven by driving durability to zero through crafting and
   asserting `Disposition == "owned"`.
6. `EnhanceOutcome` gains no member; no destroy reason code exists.
7. Enhancement's Safe/Risk bands are removed **or** an explicit, filed decision records why they stay.
8. One shared `deployment-hierarchy.v1.json`; no second tuning file.
9. `guard-actor-hub.py`, `guard-dal.py`, `guard-test-substrate.py` green; `audit-overflow.py` shows
   no new critical.

## Open questions

1. ✅ **Answered by the build.** Recommendation was *the same three* (`class`/`rarity`/`tags`); what
   shipped reads **two** — `entry.Class` and the rung id (`HeadDerivationTables.cs:40-45` for
   potential, `:68-73` for durability); `tags` is read by neither. Both head numbers still share one
   table shape, which was the point of the recommendation, so the subset is the truth and no rework is
   owed. `gear-climb-ideal.md` records the same correction.
2. ✅ **RULED 2026-09-17 (R-G1) — structure; the number is still balance data.** One pool, one unit,
   two formulas (§ Design 3). The number is owed to a measured pass that tunes the craft-wear table
   **together with** `craft-assurance`'s consumables.
3. **Does every verb consume potential equally?** **Recommendation: start equal, keyed per
   `CraftOperation` id so a balance pass can differentiate without a code change.**
4. ⭐ **Do stages 1 and 2–4 ship as one module or two?** Stage 1 is genuinely independent; stages 2–4
   need module 7's durability, which is **unbuilt**. **Recommendation: split.** Shipping "crafts are
   assured until potential runs out, then they stop" is a complete, safe, playable state — it is plain
   Last Epoch — and it lets the consequence land when durability exists rather than blocking the
   whole ladder on another program.
