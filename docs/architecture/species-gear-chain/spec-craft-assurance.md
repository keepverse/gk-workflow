# Spec: Craft assurance consumables (`craft-assurance`)

**Initiative:** `species-gear-chain` ([map](../species-gear-chain-map.md)) · **Module:** `craft-assurance`
**Owning programs:** `item` module 15 (`enhance-reroll` — the success roll and the ward) + module 14
(`salvage-craft` — the spend class) + `deployment-hierarchy` module 7 (repair) + `drop-tables` (boss sources)
**Depends on:** `craft-risk-ladder` Stage 2 (T24) for the craft-wear half of *protect*;
`durability-slice` b (T23) for *repair*. The *assure* half and the ward defect fix depend on nothing
unbuilt.
**Status:** spec, 2026-09-18. Awaiting owner approval. No build authorized. Everything below marked
**(new)** does not exist in code.
**Source:** [gear-climb-ideal.md](../gear-climb-ideal.md) § Owner rulings — **R-G1** (2026-09-17),
§ *The consumable layer — gamble or grind, and the player picks*

> **Amended 2026-09-18 for owner ruling R10** ([spec-rulings-2026-09-18.md](../spec-rulings-2026-09-18.md)):
> *protect* does **not** cover a repair destroying the item — *"the repair destroy chance stands as the
> durability sink."* This was the spec's default and its only OWNER question; it is now decided, and
> § Design 2, Testing, Boundaries and Open questions record it as such.

---

## Objective

**Give every risky craft a second, honest route: farm boss-dropped consumables and remove the
variance.**

> **Owner, 2026-09-17 (R-G1):** *"user can use special consumable item that can farm on boss to
> repair, protect damage or increase success chance. so basically user can 100% success rate if they
> have enough item. they have choice gamble with risk and assurance (damage/durability system) and
> 100% success with more time effort to farming."*

| Route | The player pays | The player gets |
|---|---|---|
| **Gamble** | Materials only | A cheaper attempt in expectation, sometimes ruinous |
| **Assurance** | Materials **plus** boss-farmed consumables (time) | A certain outcome |

**Variance is a discount.** Neither route is the correct play, and the whole design is keeping it
that way — see § The two failure modes. R-G1 is binding; this spec supplies the shape it left to a
spec, not a re-opening.

### Where this sits in the risk vocabulary

`craft-risk-ladder` § Design 5 records the filed 2026-09-15 answer (`item-map.md`, *"Filed decision
2026-09-15 — ask #4"*): **one risk vocabulary per question.** The consumable layer maps onto it
exactly, one effect per question:

| Effect **(new)** | Question it insures | Mechanism it acts on (shipped or specced) |
|---|---|---|
| **assure** | *Did this attempt succeed?* | `EnhancePolicy.SuccessMilli` (`EnhancePolicy.cs:69-77`) — the bands, which stay |
| **protect** | *What did this attempt cost the item?* | Enhance downgrade (`EnhancePolicy.cs:169`, today's `WardLoaded`) **and** craft wear past exhaustion (`craft-risk-ladder` § Design 3, T24) |
| **repair** | *How is a worn item restored?* | Workbench repair (`spec-item-durability-repair.md` §5, T23) |

The effect vocabulary is **closed at three** — a fourth is a reviewed change, and the tests pin it
(§ Testing strategy).

---

## What exists today — verified against code, not comments

### Built

| Fact | Evidence |
|---|---|
| The enhance success roll — a per-mille chance per target level, from open-topped bands that never reach 0 | `EnhancePolicy.cs:69-77` (`SuccessMilli`), `:142-176` (`Resolve`); `gk-core/data/tuning/enhancement.v1.json` |
| ⭐ **A protect concept already exists — `ward.enhance`.** A loaded ward suppresses the downgrade half of a peril failure | `EnhancePolicy.cs:16-19` (`EnhanceContext.WardLoaded`), `:169`; designed in `item/ssot-enhancement.md:548-551` |
| The workbench's one spend gate: recipe cost lines debited and the mutation applied in **one** transaction, idempotent per `correlation_id` | `RpgStore.Workbench.cs:84` (`TrySpendAndApply`); called by `ItemWorkbench.Enhance` |
| A boss channel on drop-table **entries**, declared as an authoring fact | `DropTableModel.cs:46-50` (`AffixChannels.Boss`: *"a content-authoring fact, not a detected one"*) |
| `DropEntryKind.Material` already mints material stock from a drop | `DropTableModel.cs:20-32` |
| A report that prices crafting against the power ladder, computed from shipped tuning, never authored | `Items/Mutation/CraftingHorizonReport.cs` |

### ⛔ A defect found while verifying — the ward is free today

`WorkbenchEndpoints.cs:37` declares `EnhanceRequest(... bool? WardLoaded)`, `:191` passes
`body.WardLoaded ?? false` straight into `ItemWorkbench.Enhance` (`ItemWorkbench.cs:494`), which
forwards it into `EnhanceContext` (`:506`) — and **nothing is spent**. `TrySpendAndApply` receives only
the recipe's lines. Any caller that sends `"wardLoaded": true` gets downgrade protection for free.

It is latent rather than live-harmful only because level loss starts at `+17`, which
`decision-d4-content-budget.md:157` records shipped item levels cannot reach (`ilvl_cap(11) = +6`). **It is still the exact shape R-G1 forbids** — an
assurance that costs no farming — and it is the first thing this module fixes (§ Design 3).

### Also found — a written design the code does not implement

`ssot-enhancement.md:542-545` specifies an enhancement pity (*"every failure at a level adds +80‰ to
that level's chance"*). `EnhanceContext`'s own doc comment says the counter *"gates the reroll tier
guarantee, **never the enhancement odds**"* (`EnhancePolicy.cs:14-15`), and `SuccessMilli` reads only
the target level. This is module 15's divergence, **named here and not fixed here** — but it matters to
R-G1's first failure mode (a guarantee "technically reachable and practically not" is exactly what a
pity meter answers), so the balance pass in § Tunables must know it is absent.

### Real gap

| Gap | **(new)** |
|---|---|
| A spend class for the three consumables | ⛔ Ask-first against `ssot-materials-crafting.md` §3.1 (§ The ask-first boundary) |
| *assure* — a success bonus applied inside `EnhancePolicy.Resolve` | Context field + one addition, clamped at certainty |
| *protect* — spent, not asserted; extended from downgrade to craft wear | The ward defect fix + T24's decay path reading it |
| *repair* — a consumable cost leg on the workbench repair | T23's `RepairPolicy` coverage input |
| Boss-only sourcing | A drop-table validator rule |
| The gamble-vs-assurance expected-cost report | Beside `CraftingHorizonReport` |

---

## ⛔ The ask-first boundary

`MaterialCatalog.cs:7-9`: a new spend class must answer *"which of these five questions is
unanswerable for my spend?"* (Souls — may I act; Shard — how good; Substrate — what is it made of;
Essence — what flavour; Catalyst — what am I doing to it).

**The assurance consumables answer "how much variance do I accept on this attempt?" — none of the
five asks it.** The near miss is `Catalyst` (*"what am I doing to it?"*): a catalyst names the verb
(`forge`/`temper`/`flux`) and is spent whether or not the player wants insurance; an assurance item is
optional and changes the attempt's **risk**, never its verb. Folding them into `catalyst.*` would make
the verb vocabulary carry a second meaning.

So: **(new) `MaterialClass.Assurance`**, ids `assurance.assure`, `assurance.protect`,
`assurance.repair` — a closed three-id vocabulary generated from a shape table like the five shipped
classes (`MaterialCatalog.cs:50-57`), pinned in tests. ⚠ Independent of `species-materials`'
`Trophy` ask: each is its own filing, and neither presumes the other's enum ordinal.

**Why a material and not a `ConsumableClass`.** `ConsumableClass.Ward` already exists and means a
**battle** absorption layer (`ConsumableDef.cs:21-23`), and `UseContext` has no workbench context. A
craft consumable spent through the consumable belt would be a second spend path beside
`TrySpendAndApply` for the same workbench transaction — the dual-gate shape SOLID (S) forbids. The
material shelf is the one gate the workbench already debits through.

**`ward.enhance` is renamed, not duplicated.** `ssot-enhancement.md` names the one insurance item
`ward.enhance`; no data row carries that id today (it appears only in `enhancement.v1.json`'s
`downgradeNote` prose). The amendment files `assurance.protect` as its successor so the repo never
holds two ids for one effect.

---

## Design

### 1. assure — raise the success chance, up to certainty

```
effectiveSuccess = min(1000, SuccessMilli(target) + loadedAssure × assureBonusMilli)
```

- **(new)** `EnhanceContext` gains `AssureLoaded` (a count, `int`, ≥ 0). `Resolve` applies the sum
  **before** the roll and reports `effectiveSuccess` in `EnhanceAttempt.SuccessMilli`, so the odds a
  player sees are the odds rolled.
- The `min(1000, …)` is a **bounded ratio** — a probability cannot exceed certainty — exempt from the
  no-hard-ceiling rule **and saying so in a comment**. It is not a cap on progression: loading more
  than enough is refused (next bullet), never silently wasted.
- **Loading past certainty is refused by name** — `MutationRules.Violated("enhance.assure-overloaded", …)`
  via the existing `ContentRuleViolated` code, never a new code. ⚠ *Corrected 2026-09-18: this said
  `assure.overloaded`; `assure` is not a registered namespace (`MutationOp.cs:308-322` registers only
  `enhance`/`reroll`/`mutation`), and `AtomRejection.ContentRule` **throws** on an unregistered prefix —
  so the refusal would have crashed rather than refused. The rule lives under `enhance.*`, the verb it
  guards* — so a player never pays for a consumable
  that bought nothing.
- Applies only to verbs whose policy rolls a success die. **Today that is `Enhance` alone** (grep
  `SuccessMilli` across `Items/` finds only `EnhancePolicy`). A verb that does not roll refuses an
  `assure` line by name rather than accepting it as a no-op.

⚠ **This amends written design.** `ssot-enhancement.md:548-551`: *"It does **not** raise the success
chance. Protection that improves odds is a paywall on the core mechanic."* R-G1 rules the opposite,
and the rationale that section gave does not hold here: there is no shop — the item is **boss-farmed**,
earned in play, which is a grind, not a paywall. **Filed as a cross-program ask against module 15**
(§ Boundaries), not assumed.

### 2. protect — spend it, and let it cover every cost the attempt can inflict on the item

| Attempt cost | Without protect | With one `assurance.protect` loaded |
|---|---|---|
| Enhance peril failure (from `downgradeFromLevel`) | Drop one level (`EnhancePolicy.cs:169`) | Fail-nothing — today's `WardLoaded` behaviour, unchanged |
| Craft past potential exhaustion (T24) | `durability_current -= craftWear` | **No decrement** for this attempt |

- One effect, one id, two call sites — never a second "craft ward".
- **Not covered: repair destruction — DECIDED 2026-09-18 (R10).** `spec-item-durability-repair.md` D1
  (owner-locked): *"every repair attempt … carries a tunable failure chance that destroys the item"*.
  R10: *"the repair destroy chance stands as the durability sink."* The 100% route R-G1 describes does
  **not** need to reach it: with protect covering craft wear, crafting never wears the item toward the
  repair step. Battle wear still sends items to repair, and that step keeps its risk — deliberately:
  it is the one sink that removes items from the economy. D1 is unamended; `assurance.protect` is
  **refused by name** on a repair attempt (an effect on a verb that cannot use it, § Boundaries).

### 3. The ward defect fix — protection is spent, never asserted

**(new)** `EnhanceRequest.WardLoaded` is replaced by explicit consumable lines. The workbench appends
the loaded assurance ids to the recipe's `MaterialCostLine` list and passes the union to the **one**
`TrySpendAndApply` call — so insurance is debited in the same transaction as the craft, replays
idempotently on the same `correlation_id`, and an insufficient stack refuses the whole attempt through
the shipped shortfall path. **No second debit, no second transaction.**

A request carrying `wardLoaded: true` is refused by name (`enhance.ward-flag-retired`) rather than
honoured, so a stale client cannot keep the free ward alive. ⚠ *Sharpened 2026-09-18:* the shipped web
client sends the key on **every** enhance (`gk-web/web/fusion-rpg-web/src/layers/relics/Workbench.tsx:324`,
`:393`; typed at `src/lib/bus/items.ts:463`), usually as `false` — so refusing the key's mere presence
would refuse every FE enhance. `false`/absent is accepted and ignored; only `true` is refused.

**The ward checkbox is removed in the same change** (`Workbench.tsx:324-393`, its test at
`workbench.test.tsx:204-213`, and the `wardLoaded` field in `items.ts`). This is not a new FE surface —
the odds panel that loads assurance lines stays `item-surfaces`' (module 20) — it is deleting a control
that would otherwise be a lie the moment the server stops honouring it. Leaving it in place makes the
FE's one ward path a guaranteed 4xx.

**One source for what was loaded.** `EnhanceContext.WardLoaded` / `AssureLoaded` are **derived from the
same assurance line list that is appended to `lines`** and passed to `TrySpendAndApply` — never from a
separate request count. Two inputs (a count for the policy, a line list for the debit) is the exact
shape of today's defect: the policy would believe one thing and the ledger record another. The debit's
`cost_json` is already built from the same `lines` (`RpgStore.Workbench.cs:96-98`), so the recorded op
shows the insurance that was actually taken. Assurance ids are coalesced to **one line per id** before
the union, so a duplicated id cannot double-count in the policy while debiting once.

### 4. When is it spent — the two questions R-G1 left to the spec

R-G1: *"whether consumables are consumed on failure or only on use, and whether a protected craft
that still fails consumes the protection"*. **Answered: spent on load, whatever the outcome.**

- **Technical reason (decisive):** § Design 3's single transaction debits cost lines *before* the
  outcome is persisted. An outcome-dependent spend would need a second, conditional debit — the
  dual-path shape this module exists to remove.
- **Design reason:** the odds panel (`ssot-enhancement.md` §7.7 item 6) shows *"whether a ward is
  loaded and exactly what it changes"* before commit. A price known before the roll is what makes the
  assurance route honest; a price that depends on the roll is a second gamble.
- Consequence, stated: a protect loaded on an attempt that then succeeds is still spent. That is the
  insurance premium, and the expected-cost report prices it.

### 5. repair — a cost leg, not a second repair verb

`assurance.repair` is an optional leg on T23's workbench repair recipe: each loaded unit adds
`repairCoverageBonusMilli` to `RepairPolicy.Resolve`'s material coverage, so a repair restores more of
`missingFraction`. The destruction chance is **unchanged** (D1). No new verb, no new `CraftOperation`,
no new `MutationOpKind`.

### 6. Boss-farmed — a validator rule, not a convention

**(new)** `DropTableValidator` refuses an `assurance.*` material entry that is not authored on the
boss channel (`AffixChannels.Boss`, `DropTableModel.cs:46-50`), via the existing
`ContentRuleViolated{drop.*}` namespace (`drop.assurance-non-boss`) — **never a new error code**. The
boss fact stays an authoring fact, as that file says; this rule only stops an author putting insurance
on trash.

**What the rule can and cannot enforce — stated so it is not over-trusted (strengthen pass
2026-09-18).** The channel is a per-entry label (`DropTableEntryRow.AffixChannel`,
`DropTableModel.cs:93-107`) and `LootSourceRow` carries no boss fact, so the validator cannot prove a
*table* is only reached from a boss. Two closures make the rule as strong as the data allows:

- **Through `Table` recursion.** An `assurance.*` entry inside a sub-table is legal only if **every**
  `Table`-kind entry that reaches that sub-table is itself on the boss channel — otherwise a boss-labelled
  entry in a shared sub-table leaks onto trash through a `drop`-channel pointer. Refused as
  `drop.assurance-non-boss`, naming the referencing table.
- **Visibility, not proof, for the rest.** A mislabelled trash table (an author marking a trash entry
  `boss`) is not detectable — the file says so on purpose. § Design 7's report therefore prints assurance
  yield **per `LootSourceRow`** (`source_kind:source_id`), so a boss-only consumable dropping from a
  `web-wave` source is visible in review. It is a report, never an assertion.

### 7. The two failure modes — a report, never an assertion

R-G1 names both, from Lost Ark's honing:

1. **A guarantee reachable only in theory** — *"it takes an eternity and a fortune to reach it"*.
2. **A guarantee cheap enough to dominate** — *"if assurance costs less than the expected cost of
   gambling, nobody gambles."*

**(new)** A gamble-vs-assurance report beside `CraftingHorizonReport`, computed from shipped tuning
only: per enhance level, the **expected** material cost of gambling to the next level (success chance,
downgrade risk, craft wear) against the cost of certainty (the consumables needed × their expected
farming cost from boss drop rates). It prints the ratio; **it asserts nothing** — the right ratio is a
balance judgement, and pinning it would be pinning a reading (`validation-ssot.md`).

---

## Tech stack

C# .NET 8 (`FusionRpg.Core` policy, `FusionRpg.Data` spend, `FusionRpg.Server` endpoint), xUnit,
Python 3 seedsmith (display names only). No new dependency. No **new** FE surface — the odds panel is
`item-surfaces` (module 20); the shipped ward checkbox is **deleted** here (§ Design 3).

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Enhance"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~CostClass"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~DropTable"
dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~Workbench"
dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~Workbench"
dotnet run --project gk-forge/tools/ItemSeedValidator
python gk-core/scripts/guard-dal.py
python gk-core/scripts/guard-actor-hub.py
python gk-core/scripts/audit-magic-numbers.py --targets M1
python gk-core/scripts/audit-overflow.py
cd gk-web/web/fusion-rpg-web; npx vitest run src/layers/relics/workbench.test.tsx
.\scripts\verify-change.ps1 -Paths <every changed path> -Session <active-session-id>
```

## Project structure

| Path | Role |
|---|---|
| `gk-core/src/FusionRpg.Core/Items/Materials/MaterialCatalog.cs` | **(new)** `MaterialClass.Assurance` + its three-id shape table |
| `gk-core/src/FusionRpg.Core/Items/Materials/CostClassMatrix.cs` | **(new)** a narrow `Allows` arm: `Temper` (assure, protect), T24's decaying verbs (protect), T23's `Repair` (repair) |
| `gk-core/src/FusionRpg.Core/Items/Mutation/EnhancePolicy.cs` | `AssureLoaded` in the context; the clamped sum before the roll |
| **(new)** `gk-core/src/FusionRpg.Core/Items/Mutation/CraftAssuranceTuning.cs` | Strict loader for the tuning file below |
| `gk-core/src/FusionRpg.Server/ItemWorkbench.cs`, `WorkbenchEndpoints.cs` | The ward defect fix — lines, not a flag |
| `gk-web/web/fusion-rpg-web/src/layers/relics/Workbench.tsx`, `workbench.test.tsx`, `src/lib/bus/items.ts` | Remove the free-ward checkbox and field in the same change (deletion only — the replacement odds panel is `item-surfaces`') |
| `gk-core/src/FusionRpg.Core/Items/Drops/DropTableValidator.cs` | The boss-only rule |
| **(new)** `gk-core/data/tuning/craft-assurance.v1.json` | The effect magnitudes |
| `gk-data/packs/fusion/data/seed/loot/**` | Boss-channel entries carrying `assurance.*` — authored runtime corpus, item module 11's |
| `docs/architecture/item/ssot-enhancement.md`, `ssot-materials-crafting.md` | The two amendments (§ Boundaries) |

## Code style

```csharp
// R-G1: assurance raises the odds up to CERTAINTY. min(1000, ...) is a BOUNDED RATIO — a probability
// cannot exceed 1000‰ — so it is exempt from the no-hard-ceiling rule (AGENTS.md) and says so here.
// Loading past certainty is refused by name upstream, so this clamp never silently eats a consumable.
var effective = Math.Min(1000L, (long)success + (long)ctx.AssureLoaded * t.AssureBonusMilli);
```

## Tunables

| Number | Meaning | Owner |
|---|---|---|
| `assureBonusMilli` | Success per-mille one `assurance.assure` adds | **(new)** `gk-core/data/tuning/craft-assurance.v1.json` |
| `repairCoverageBonusMilli` | Repair coverage one `assurance.repair` adds | Same file |
| Protect's effect | **Structural, not tunable** — it suppresses the attempt's item cost entirely; a partial protect would be a different mechanic and a second balance surface | `const`, commented |
| Which verbs accept which effect | The `Allows` arm | Code — a closed matrix, like the five classes' arms |
| Boss drop weights for `assurance.*` | R-G1's *"farm on boss"* — the time price of certainty | `gk-data/packs/fusion/data/seed/loot/**` boss tables (module 11's authored corpus) |

⛔ **One balance problem with `craft-risk-ladder`'s craft-wear table (R-G1).** `craftWearPerAttemptMilli`,
the enhance bands, `assureBonusMilli` and the boss drop weights are tuned **in one pass**, reading § Design
7's report — never one after the other. Shipping first values is sanctioned; calling them balance is
not.

`schemaVersion` + `version` inside the file; ⛔ *corrected 2026-09-18:* a revision is a **new
`craft-assurance.v{n+1}.json` published through `gk-core/tools/tuning/publish.py`**, never an in-place bump
(tunables-ssot T4; map § Tuning revisions, which reverses § Corrections #11). Every key required — a missing key throws (T5); Core never reads the file,
the host injects it (T7.2).

**Power ladder:** none of these numbers is level-derived — success and coverage are bounded
per-mille ratios, and drop weights are table weights. **No `ssot-power-scale.md` §10 row is owed.** If a
later pass makes any of them scale with `Θ`, it becomes a cost ladder and owes one first.

## Numeric types

- `assureBonusMilli`, `repairCoverageBonusMilli`: per-mille **bounded ratios** `[0, 1000]`, load-checked;
  exempt from the magnitude rules and commented as such.
- The success sum is computed in `long`, widened before multiplying (`(long)count * bonus`), then
  clamped — a large stack cannot overflow on the way to the clamp.
- Stack counts on the shelf are `long` (a material quantity on an endless axis); `AssureLoaded` is an
  `int` per-attempt load count, validated `≥ 0` and refused past certainty, so its range is structural.
- Floating-point is allowed (owner ruling 2026-09-15); nothing here needs it.

## ActorHub gate

**N/A and checked.** An assurance consumable changes an attempt's odds, an item's durability or its
`+X` — item state. The resulting stats reach actors through the existing equipment path into
`ActorHub`, and a broken item leaves through the existing assignments filter. **No composer, no private
fold, no Hub contribution.** `guard-actor-hub.py` stays green.

## Seedsmith / generator

**Generator involved: display only.** The three ids are a **closed vocabulary** the code owns
(`MaterialCatalog` shape table), so no generator mints them and no model picks a magnitude (P1).

| Stage | Adapter | Change | Tuning | New seed fields |
|---|---|---|---|---|
| Name / flavor / tags for the three ids | `gk-forge/tools/seedsmith/seedsmith/adapters/items/materialgen/vocab.py` (`_build_issuable`, `:110-126`) | The mirror gains the `Assurance` class shape (three ids). The `27` asserts are replaced by the reconciliation canary in the **same** change `species-materials` T33 specifies — whichever lands first replaces them, the second extends the canary | none | none — materialgen's row shape (name/flavor/tags) is unchanged; `audit_schema` (`pipeline/model.py:113`) stays clean |
| Boss drop entries | none — `gk-data/packs/fusion/data/seed/loot/**` is the authored runtime corpus (`gk-data/packs/fusion/data/seed/loot/README.md`); the band→row generator for `gk-data/packs/fusion/data/seed/items/drop-tables/` does not exist yet | — | — | — |

```powershell
$env:PYTHONPATH = "gk-forge/tools/seedsmith"
python -m seedsmith items generate --kind material --dry-run
python -m seedsmith items generate --kind material --write
cd gk-forge/tools/seedsmith; python -m seedsmith check gk-data/packs/fusion/data/seed/items --adapter items
```

**pytest:** `gk-forge/tools/seedsmith/tests/test_materials_gen.py`, `gk-forge/tools/seedsmith/tests/test_recipes_gen.py`.

## Testing strategy

| Level | What it asserts |
|---|---|
| Unit | ⭐ **The effect vocabulary is exactly three** (`assure`, `protect`, `repair`) — a closed vocabulary, pinned, and the test says so |
| Unit | `MaterialCatalog.ClassOf("assurance.protect") == Assurance`; `ClassOf` still throws outside the set; the five shipped classes still generate 27 |
| Unit | assure: `effectiveSuccess` = band chance + load × bonus, reported in `EnhanceAttempt.SuccessMilli`; enough loads reach exactly 1000 and the attempt always succeeds |
| Unit | assure: a load past certainty is refused by name; an `assure` line on a non-rolling verb is refused by name |
| Unit | protect: a peril failure with protect loaded keeps the level (today's ward behaviour, now paid for) |
| Unit | protect: past exhaustion (T24), a protected attempt leaves `durability_current` unchanged; an unprotected one decrements |
| Unit | protect: an `assurance.protect` line on a repair attempt is **refused by name**, and the repair's destruction chance is unchanged (D1, R10) |
| Data | ⭐ **The ward defect:** a request carrying `wardLoaded: true` and no `assurance.protect` stock is refused; with stock, one unit is debited in the same `TrySpendAndApply` transaction; replaying the `correlation_id` debits nothing twice |
| Data | Spent on load: a protected attempt that succeeds still debits the protect |
| Data | Replay with a **different** load on the same `correlation_id` returns the recorded outcome and debits nothing — the first request's load is the only one ever applied |
| Data | Insufficient assurance stock refuses the whole attempt: no level change, no recipe debit, no op row |
| Server | `wardLoaded: false` (what the shipped FE sends) is accepted and ignored; `wardLoaded: true` is refused by name |
| Unit | The policy's `WardLoaded`/`AssureLoaded` equal the counts in the debited line list — one input, proven by a request whose line list and a forged count disagree |
| Unit | Drop validator: an `assurance.*` entry in a sub-table reached through a `drop`-channel `Table` entry is refused, naming the referencing table |
| Unit | repair: each loaded unit raises coverage by `repairCoverageBonusMilli`; destruction chance unchanged |
| Unit | Tuning: a missing key throws; a ratio outside `[0, 1000]` is a load rejection naming the key |
| Unit | Drop validator: an `assurance.*` entry off the boss channel is refused with `drop.assurance-non-boss`; on it, accepted; no new error code |
| Report | § Design 7's gamble-vs-assurance ratio, per level — **printed, never asserted** |
| Guard | `guard-actor-hub.py`, `guard-dal.py` green; `audit-overflow.py` no new critical |

⛔ No test asserts a drop count, a player's stock, or a gamble/assurance ratio.

## Boundaries

**Always**
- Debit assurance in the **one** `TrySpendAndApply` transaction with the recipe lines.
- Refuse by name: overload past certainty, an effect on a verb that cannot use it, a stale `wardLoaded`.
- Keep D1: repair is the only destroy path, and this module does not touch its chance.
- Tune with the craft-wear table and the bands in one pass.
- Commit with plain `git` (explicit paths).

**Ask first**
- ⛔ **`MaterialClass.Assurance`** — against `ssot-materials-crafting.md` §3.1, with the
  "how much variance do I accept?" argument above.
- ⛔ **Amending `ssot-enhancement.md` §7.6** (`:548-551`) — protection that raises odds, and the
  `ward.enhance` → `assurance.protect` rename. Module 15's written design; filed in `item-map.md`, not
  assumed (the `craft-risk-ladder` bands ask is the precedent: it was filed and answered).

**Never**
- Keep the free ward: a protect effect that nothing debited.
- A second spend path (consumable belt, a second transaction) for a workbench attempt.
- A destroy outcome on the craft path (`MutationOp.cs:50-53`), or a new `ContentRuleViolated` code.
- Let *protect* (or any assurance effect) suppress or reduce a repair's destroy chance — R10: it is the
  durability sink. A change to D1 is a new owner ruling, not an ask this module files.
- A fallback currency or a shop price for the consumables — R-SC2 / R-G1: the source is a boss, and
  a price would re-make it the paywall `ssot-enhancement.md` warned about.
- A pity or guarantee **invented here** — enhancement pity is module 15's written, unbuilt design.
- Assert a population count or a balance ratio.

## Success criteria

1. `assurance.assure` / `.protect` / `.repair` exist as a closed three-id class under a filed, answered
   ask; `ClassOf` resolves them and still throws outside the set.
2. ⭐ **A player with enough consumables reaches 100% on an enhance attempt** — proven end to end
   through the endpoint, with the stack debited.
3. ⭐ **The free ward is gone**: protection happens only when stock is debited, in one transaction.
4. Past exhaustion, a protected craft does not wear the item; an unprotected one does.
5. Repair consumables raise coverage and leave D1's destruction chance untouched; *protect* is refused
   on a repair attempt (R10).
6. `assurance.*` drops only from boss-channel entries, enforced by the validator.
7. The gamble-vs-assurance report prints per level from shipped tuning.
8. No new error code, no new `CraftOperation`/`MutationOpKind`, no destroy outcome.
9. Core / Data / Server suites for the touched boundaries, `ItemSeedValidator`, seedsmith pytest green;
   guards green.

## Open questions

1. ✅ **DECIDED 2026-09-18 (R10) — *protect* does not cover repair destruction.** The repair destroy
   chance stands as the durability sink; `spec-item-durability-repair.md` D1 is unamended and module 7's
   map records no exception. § Design 2, 5.
