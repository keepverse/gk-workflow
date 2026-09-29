# Spec: Gem tier and the insert ladder (`gem-tier`)

**Initiative:** `species-gear-chain` ([map](../species-gear-chain-map.md)) · **Module:** `gem-tier`
**Owning program:** `item` module 16 (`sockets`)
**Depends on:** nothing in the fifteen. Layer 0 — it can run in parallel with every other Layer-0 module.
**Status:** spec, 2026-09-13. Awaiting owner approval. No build authorized.

> **Build state (strengthen pass 2026-09-18): SHIPPED — T8 (`15ffb5f9`, tier derived from `powerBand`), T9 (`50368b57` + `eddd9e11`, `ForgeGem` verb + recipe).** The Status line above is the spec's 2026-09-13 state — the plan was approved and built. § What exists today / Real gap below are the **pre-build record** — kept for their reasoning, not as a description of current code; a `file:line` there points at where the code *was* when the spec was written. Current locations, re-verified against code this pass:
>
> - `ItemCardEndpoints.cs`: `UnauthoredInsertTier` const `:138` is a corpus-miss fallback only; `TierOf()` `:200-207` derives via `UniqueBudget.TierOfPowerBand`; the "day the corpus authors a tier" quote is gone
> - `ItemSurfaceEndpoints.cs:226`; `ItemWorkbench.cs:740` (the former third stamp site); `ForgeGem` `ItemWorkbench.cs:311`, reading `SocketTuning.UpcycleInputPerOutput` at `:344`; `MaterialHasNoRung` use `:280` (const `:102`)
> - `ContainerRow.cs`: `ContainerKind.Gem` `:40`, `"gem"` `:205`
> - `sockets.v1.json` (`version` 3): `insertTiers.count` `:48`, `upcycleInputPerOutput` `:49`, SOFT note `:50`; `SocketTuning.cs`: count parse `:204-205`, upcycle parse `:206`, validate `:207-209`, property `:107`, structural check `:193-196`
> - `GetSockets` callers: `ItemCard.cs:361`; `ItemWorkbench.cs:693`, `:746`, `:846`, `:1089`; `RpgStore.Items.cs:957`; `EquippedBoundAtoms.cs:55`
**Source ideal:** [tier-system-ideal.md](../tier-system-ideal.md) `:551-555`, `:563`, `:908`
— ⛔ **three of that ideal's four claims here are wrong as written; every number below was re-measured
this session and the corrections are stated inline.**

---

## Objective

**Give every socketed insert a real tier, so that a combination's tier-gated ingredient slots become
satisfiable — and give the `k → k+1` insert ladder a verb, so `upcycleInputPerOutput` stops being a
number nothing reads.**

⭐ **This is almost entirely a wiring problem, not a content one, and the ideal reported it as the
opposite.** Measured this session:

| Fact | Measured | Evidence |
|---|---|---|
| Gem entries shipped | **104** | `gk-data/packs/fusion/data/seed/items/gems/{g1,g2,g3}.json` — counted |
| Entries carrying `powerBand` | **104 / 104** | counted |
| Entries carrying a `tier` field | **0 / 104** — and an authored one would be **illegal** | `docs/architecture/item/entry-shapes.md:81` |
| A tier already derivable from `powerBand` | ✅ **yes, for all 104** | `gk-data/packs/fusion/data/seed/items/_registry/bands.v1.json:47-53` `powerBand.tierMap` |
| Production code that already does that derivation | ✅ **shipped** | `gk-core/src/FusionRpg.Core/Items/Gems/GemContainerBuild.cs:49` |
| What the socket path uses instead | a hardcoded `1` | `gk-core/src/FusionRpg.Server/ItemCardEndpoints.cs:128` |

```csharp
// GemContainerBuild.cs:48-54 — the derivation this module needs ALREADY EXISTS in production.
int tier;
try { tier = UniqueBudget.TierOfPowerBand(seed.PowerBand); }
catch (ArgumentOutOfRangeException) { ... }
```

`UniqueBudget.TierOfPowerBand` (`gk-core/src/FusionRpg.Core/Items/Uniques/UniqueBudget.cs:34-44`) is a frozen
mirror of `bands.v1.json`'s five-band map, and its own doc comment says so — *"a frozen mirror of
`bands.v1.json powerBand.tierMap`, not gem-specific, so this reuses it directly rather than authoring
a third private copy of the same five-band switch"* (`GemContainerBuild.cs:14-16`).

**Applying it to the shipped corpus, measured:**

| `powerBand` | Entries | → tier |
|---|---|---|
| `low` | 24 | **t2** |
| `medium` | 48 | **t3** |
| `high` | 32 | **t4** |

**No gem resolves below t2.** So the 118 unsatisfiable ingredient rows (§What exists today) become
satisfiable the moment the socket path stops hardcoding `1` — with **zero** corpus edits and **zero**
generator runs.

---

## What exists today — verified against code and the shipped corpus

### Built

| Fact | Evidence |
|---|---|
| **104 gem entries, all carrying `powerBand`** — `low` 24 / `medium` 48 / `high` 32 | `gk-data/packs/fusion/data/seed/items/gems/g1.json`, `g2.json`, `g3.json` — counted this session |
| **`bands.v1.json` ships the band→tier map** — `trivial` 1, `low` 2, `medium` 3, `high` 4, `extreme` 5 | `gk-data/packs/fusion/data/seed/items/_registry/bands.v1.json:47-53` |
| **`UniqueBudget.TierOfPowerBand` is the one shared mirror of it**, already used by two consumers | `gk-core/src/FusionRpg.Core/Items/Uniques/UniqueBudget.cs:34-44` |
| **`GemContainerBuild.TryBuildOne` already derives a gem's tier from its band and refuses by name if the band is unknown** | `gk-core/src/FusionRpg.Core/Items/Gems/GemContainerBuild.cs:48-62` |
| **`ContainerKind.Gem` exists** (X7) and stringifies as `"gem"` | `gk-core/src/FusionRpg.Core/Effects/Atoms/ContainerRow.cs:34`, `:190` |
| **The evaluator's tier gate is real and correct** — `.Where(f => f.Insert.Tier >= need.MinTier)` | `gk-core/src/FusionRpg.Core/Items/Sockets/ComboMatcher.cs:89` — the one matcher both the evaluator and the surface's distance calc call (strain-splice-host SSH1.1 unified what this row once called "mirrored") |
| **The evaluator's tier gate is real and correct** — `.Where(f => f.Insert.Tier >= need.MinTier)` | `gk-core/src/FusionRpg.Core/Items/Sockets/ComboMatcher.cs:89` (moved here by SSH1.1, formerly CombinationEvaluator line 186); mirrored in the surface's distance calc at `gk-core/src/FusionRpg.Core/Items/Surfaces/CombinationDistance.cs:225` |
| **`insertTiers.count = 5` is parsed, validated and READ** — `StrainSpliceTuning` refuses an ingredient tier outside `[1..count]` | `gk-core/data/tuning/sockets.v1.json:41`; `gk-core/src/FusionRpg.Core/Items/Sockets/SocketTuning.cs:168`; read at `gk-core/src/FusionRpg.Core/Items/Sockets/StrainSpliceTuning.cs:124-128` |
| **`insertTiers.count` is explicitly a SOFT content axis, not a cap** — *"count is a SOFT content axis, not a cap: raising it extends the insert ladder and nothing in this module refuses the higher tier"* | `gk-core/data/tuning/sockets.v1.json:43`, restated at `:24` and `SocketTuning.cs:36` |
| **`CraftOperation.ForgeGem` exists in the closed operation enum and is already priced** — `souls` ×30 on `rung`, `shard` ×1 flat, `essence` ×3 on `rung`, `catalyst.forge` ×1 | `gk-core/src/FusionRpg.Core/Items/Materials/CostClassMatrix.cs:20`, `:53`; `gk-core/data/tuning/materials.v1.json` `operations.forge-gem` |
| **`ForgeGem` is already classified as a MINT**, so the forge-then-salvage loss-leak check covers it | `gk-core/src/FusionRpg.Core/Items/Materials/MaterialRecipeCatalog.cs:283-284` |
| **`upcycleInputPerOutput` is parsed and validated** — a ratio below 2 is a load rejection (*"manufactures tiers instead of consuming them"*) | `gk-core/data/tuning/sockets.v1.json:42`; `gk-core/src/FusionRpg.Core/Items/Sockets/SocketTuning.cs:169-173` |

### Wiring gap

These are inert paths, **not** architectural walls. Each is one call site.

| Gap | Evidence |
|---|---|
| ⛔ **`GemInsertCorpus.Load` hardcodes every insert to tier 1** instead of calling the shipped derivation. `public const int UnauthoredInsertTier = 1;` and it is stamped onto every entry it reads. | `gk-core/src/FusionRpg.Server/ItemCardEndpoints.cs:128`, used at `:154` |
| ⛔ **Two further sites re-stamp the same constant**, so fixing one is not enough | `gk-core/src/FusionRpg.Server/ItemSurfaceEndpoints.cs:225`; `gk-core/src/FusionRpg.Server/ItemWorkbench.cs:358` |
| ⛔ **`SocketTuning.UpcycleInputPerOutput` has no reader.** Parsed at `SocketTuning.cs:169`, validated at `:160-163`, exposed at `:105` — and **no `src/`, `tests/` or `tools/` site reads the property.** (Note: `MaterialTuning.UpcycleInputPerOutput`, `gk-core/src/FusionRpg.Core/Items/Materials/MaterialTuning.cs:103`, is a **different** property on a **different** ladder — `materials.v1.json`'s `upcycle` at ratio **5**, owned by module 14. Grepping the name alone reads as "it has consumers." It does not.) | counted this session |
| ⛔ **`forge-gem` has zero authored recipes.** `gk-data/packs/fusion/data/seed/items/recipes/recipes.json` holds 67 entries across 8 operations (`temper` 35, `elevate` 10, `forge` 7, `reroll-one` 5, `upcycle` 4, `bore` 3, `reroll-all` 2, `socket` 1) — **`forge-gem` is not among them** | counted this session |
| ⛔ **`ItemWorkbench` exposes no gem-forge verb.** Its five verbs are `Upcycle` (`:194`), `Enhance` (`:243`), `SocketAdd` (`:293`), `SocketInsert` (`:338`), `SocketImbue` (`:378`) | `gk-core/src/FusionRpg.Server/ItemWorkbench.cs` |

### Real gap

Exactly one, and it is small:

- ⛔ **`bands.v1.json`'s five bands do not all appear in the shipped gem corpus.** `trivial` (t1) and
  `extreme` (t5) are authored **zero** times; the generator's own rotation is deliberately narrowed to
  three — *"the three power bands every shipped gem partition has actually used… `bands.v1.json`'s own
  `powerBand.enum` is wider (adds `trivial`/`extreme`), but this module stays inside the PROVEN subset"*
  (`gk-forge/tools/seedsmith/seedsmith/adapters/items/gemgen/emit.py`, `POWER_BAND_ROTATION`). So the insert
  ladder that *exists* is `[2..4]`, not `[1..5]`. **That is a content-breadth gap, and it is the only
  one this module has** — it does not block a single shipped combination, because all 118 tier-gated
  ingredient rows need `minTier ≥ 2` and nothing needs t5.

### ⭐ The consequence, re-measured — and three of the ideal's numbers corrected

| Ideal's claim | Measured | Verdict |
|---|---|---|
| *"104 gem entries, `powerBand` 104/104, `tier` 0/104, `element` 8/104"* | 104 / 104 / 0 / 8 | ✅ **correct, all four** |
| *"`ItemCardEndpoints.cs:127` `UnauthoredInsertTier = 1`"* | the declaration is at **`:128`**; `:127` is its doc comment | ⚠ off by one |
| *"all 76 shipped combinations use `minTierPlan [1,1,2,2]`"* | **No combination entry carries a `minTierPlan` field.** The entries carry per-ingredient `{family, minTier, quantity}`. `minTierPlan: [1, 1, 2, 2]` lives in `gk-core/data/tuning/strain-splice.v1.json:7` — it is the **generator's** zip plan, not emitted data. Measured: the quantity-weighted multiset **is** exactly `(1,1,2,2)` for all 76 | ⚠ **substance right, cite wrong** |
| *"118 of 232 **ingredient slots** require tier ≥ 2"* | **232 is the ingredient ROW count, and 118 of those rows carry `minTier ≥ 2`** — that pair is internally consistent. Quantity-weighted **slots** are **304**, of which **152** need tier ≥ 2 | ⚠ the word "slots" is wrong; both readings are given here so no later session re-derives one and thinks the other is a defect |
| *"no shipped gem can satisfy them"* | ✅ true **today**, and false the instant the derivation is wired: **all 118 tier-≥2 rows name a family that has at least one shipped gem** (measured: 30 distinct ingredient families, 98 distinct gem families, **0 ingredient families with no gem**) | ⚠ true but reported as a content gap; it is a **wiring** gap |
| *"`upcycleInputPerOutput: 3` is parsed and then referenced nowhere else in `src/`"* | ✅ **correct** for that key. But its sibling `insertTiers.count` **is** read (`StrainSpliceTuning.cs:124`), so the section is not inert as a whole | ✅ with a caveat |
| *"Gem tier ids + upcycle ratio → `data/tuning/sockets.v{n}.json`"* (`:908`) | ⛔ **two errors.** (a) ~~`sockets.v1.json` already carries `"version": 2` — a revision is a **bump inside that file**, never a new `v{n}.json` filename~~ ⛔ *reversed 2026-09-18:* the ideal's `v{n}` phrasing was **right** — a revision is a new `sockets.v{n+1}.json` via `publish.py` (tunables-ssot T4; map § Tuning revisions). (b) A tunable list of "gem tier ids" must **not** be authored: the tier is already derivable from the authored `powerBand`, and a **tier field on a gem entry is an explicit `OwnershipViolation`** (`entry-shapes.md:81`) | ⛔ **rejected as written** |

**Two stale comments found while verifying, recorded so they are not cited as evidence later:**
`gk-core/src/FusionRpg.Core/Effects/Atoms/ContainerRow.cs:14` and
`gk-core/src/FusionRpg.Core/Items/Gems/GemContainerBuild.cs:27` both say *"60 shipped gem entries"*. Measured
**104**. Both are readings in prose, not assertions, so neither is a defect — but neither is evidence.

---

## Design

### 1. ⛔ No gem entry gains a `tier` field. The tier is DERIVED, and there is a shipped precedent.

`entry-shapes.md:81` lists the gem kind's rejects, verbatim:

> **Rejects:** … a `pool_rolls`, `weight`, or **tier field present (OwnershipViolation)**

and `:77` says what owns the tier instead:

> *(GENERATED, never authored)* | `gem.ember-shard.t1`…`.t5` — five tiered containers, `resonances`, `weight`

**The precedent is consumables, one section away.** `entry-shapes.md`'s consumable table:

> `powerBand` | AUTHORED (band) | required | `bands.v1.json`; **a generator derives `grade` (1–5) from
> this band's tier — `grade` is never authored directly**

and the C# that implements it — `ConsumableTuning.GradeTierMap`, whose own doc comment is
*"`bands.v1.json`'s frozen `powerBand.tierMap`, mirrored. Core never reads a file."*
(`gk-core/src/FusionRpg.Core/Items/Consumables/ConsumableTuning.cs:55-56`).

**Gem tier takes the identical shape.** One derivation, `powerBand → tier`, through the one shared
mirror that two consumers already use.

### 2. The fix is to delete a constant's use, not to add a number

`GemInsertCorpus.UnauthoredInsertTier`'s own doc comment states the safe-direction argument for the
hardcode and, in the same breath, names its own exit:

> *"`CombinationDistance` filters ingredients with `Insert.Tier >= need.MinTier`, so the lowest rung
> can only ever UNDER-report a resonance… **The day the corpus authors a tier, this reads it.**"*
> — `ItemCardEndpoints.cs:118-122`

**This module is that day — with the one amendment that the corpus does not "author" a tier, it
*carries* one, in `powerBand`.** The constant's three use sites
(`ItemCardEndpoints.cs:154`, `ItemSurfaceEndpoints.cs:225`, `ItemWorkbench.cs:358`) each resolve
`UniqueBudget.TierOfPowerBand(entry.powerBand)` instead. `UnauthoredInsertTier` survives **only** as
the fallback for a container the corpus does not carry at all — which is what `ItemWorkbench.cs:356-358`
and `ItemSurfaceEndpoints.cs:224-225` already treat it as.

⚠ **An unknown `powerBand` is a load rejection naming the gem, never a silent fall back to tier 1.**
That is T5, and `GemContainerBuild.cs:50-54` already refuses by name rather than guessing. Falling back
would reintroduce exactly the bug this module exists to remove, with no symptom.

### 3. The upcycle ladder rides `forge-gem`, an operation that already exists and is already priced

`k → k+1` needs four things. **Three are already shipped:**

| Need | State |
|---|---|
| An operation in the closed `CraftOperation` enum | ✅ `ForgeGem` (`CostClassMatrix.cs:20`) — **no enum widening, so not ask-first** |
| A price | ✅ `operations.forge-gem` in `materials.v1.json` — souls ×30 on `rung`, shard ×1 flat, essence ×3 on `rung`, `catalyst.forge` ×1 |
| The input ratio | ✅ `insertTiers.upcycleInputPerOutput: 3` (`sockets.v1.json:42`) — this module gives it its first reader |
| A recipe row and a verb | ⛔ **missing** — 0 of 67 recipes, and no sixth workbench verb |

**The verb copies the five-verb `ItemWorkbench` shape exactly** — `TryRecipe(recipeId,
CraftOperation.ForgeGem, …)` → stock check for `upcycleInputPerOutput` copies of the input gem →
`TrySpendAndApply` with a `WorkbenchGrant` of one output gem. It is closest in shape to `Upcycle`
(`ItemWorkbench.cs:194-220`), which is also a stock-to-stock mint with no host instance, and it needs
no new `MutationOpKind` for exactly that reason: **nothing is mutated.**

### 4. ⛔ The recipe rows are GENERATED. Author the generator, never the JSON.

`gk-data/packs/fusion/data/seed/items/recipes/recipes.json` carries `_meta.model: "claude-haiku-4-5-20251001"`,
`_meta.promptVersion: 1`, `_meta.batch: "recipes-all"`. It is seedsmith `recipegen`'s output.
**Adding `forge-gem` rows by hand forks the corpus from its generator**; the next run reverts them and
the ledger stops describing the file. The deliverable is the `recipegen` change plus the regenerated
diff — and if `recipegen` cannot yet express a `forge-gem` row, **fixing `recipegen` is the
deliverable**, not the JSON edit.

The same rule binds the one content item in §Real gap: if `trivial`/`extreme` gems are wanted, the
change is `POWER_BAND_ROTATION` in `gk-forge/tools/seedsmith/seedsmith/adapters/items/gemgen/emit.py` plus a
regeneration — never a hand edit to `g1/g2/g3.json`, each of which carries `_meta.model`.

### 5. `insertTiers.count` is a soft content axis, and nothing here turns it into a cap

The tuning file says so twice (`sockets.v1.json:43`, `:24`) and the parser's own comment says so a
third time (`SocketTuning.cs:36`). The only enforcement is `StrainSpliceTuning.cs:124-128`, which
refuses an **ingredient** tier outside `[1..count]` — a *recipe-authoring* guard, not a ceiling on
what an insert may become. **This module adds no clamp.** Raising `count` to 6 extends the ladder;
nothing in the socket layer refuses t6, and nothing here starts to.

---

## Tech stack

C# .NET 8 — `FusionRpg.Core/Items/{Gems,Sockets}`, `FusionRpg.Server` (`ItemWorkbench`,
`ItemCardEndpoints`, `ItemSurfaceEndpoints`), xUnit. Python 3 for the `recipegen`/`gemgen` change
(`gk-forge/tools/seedsmith`). No new dependency. No FE surface — a socket bench belongs to `item-surfaces`
module 20 / `gui-lego`. **SQL only inside `FusionRpg.Data`.**

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Socket"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Gem"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Material"
dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~ItemCard"
dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~Workbench"
dotnet run --project gk-forge/tools/ItemSeedValidator
python gk-core/scripts/guard-dal.py
python gk-core/scripts/guard-actor-hub.py
python gk-core/scripts/audit-overflow.py
python gk-core/scripts/audit-magic-numbers.py --domain sockets

# seedsmith side (recipegen forge-gem rows; gemgen only if the band rotation widens)
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_sockets_gen.py -q
cd gk-forge/tools/seedsmith; python -m seedsmith check gk-data/packs/fusion/data/seed/items --adapter items
```

## Project structure

| Path | Role |
|---|---|
| `gk-core/src/FusionRpg.Server/ItemCardEndpoints.cs` | `GemInsertCorpus.Load` resolves the tier from `powerBand`; `UnauthoredInsertTier` narrows to the not-in-corpus fallback only |
| `gk-core/src/FusionRpg.Server/ItemSurfaceEndpoints.cs` | same resolution at `:225` |
| `gk-core/src/FusionRpg.Server/ItemWorkbench.cs` | same resolution at `:358`; **the sixth verb** (`ForgeGem`), shaped on `Upcycle` (`:194`) |
| `gk-core/src/FusionRpg.Core/Items/Uniques/UniqueBudget.cs` | `TierOfPowerBand` — **reuse, do not copy**; a fourth private five-band switch is the defect |
| `gk-core/src/FusionRpg.Core/Items/Sockets/SocketTuning.cs` | `UpcycleInputPerOutput` gains its first reader |
| `data/tuning/sockets.v{n}.json` | ⚠ **A new `sockets.v{n+1}.json` via `publish.py` only if a number changes**, landing **after** strain-splice-host's `circuit-topology` (v2) and `combo-budget` — never an in-place bump of v1, which is no longer read once v2 exists. If `upcycleInputPerOutput: 3` stands as shipped (it did, T9), nothing is published |
| `gk-core/data/tuning/materials.v1.json` | `operations.forge-gem` — **confirm, do not re-author.** Already priced. ⚠ **R20:** its souls coefficient may be **repriced by strain-splice-host's `combo-budget` report** (derived, published `v{n+1}`) — never by this module |
| `tools/seedsmith/.../items/recipegen/` | emits the `forge-gem` recipe rows |
| `tools/seedsmith/.../items/gemgen/emit.py` | `POWER_BAND_ROTATION` — only if the owner widens the band spread |
| `gk-data/packs/fusion/data/seed/items/recipes/recipes.json` | ⛔ **generated output.** Regenerated, never hand-edited |
| `gk-data/packs/fusion/data/seed/items/gems/*.json` | ⛔ **generated output.** No `tier` field is ever added here |
| `tests/FusionRpg.Core.Tests/Items/Sockets/`, `gk-core/tests/FusionRpg.Server.Tests/` | the tier-resolution and forge-gem tests |

## Code style

Resolve through the one shared mirror, and **refuse rather than fall back** — the fallback is the bug:

```csharp
// The tier is DERIVED from the authored powerBand, never authored on the entry: entry-shapes.md:81
// makes a `tier` field on a gem an OwnershipViolation, and consumables already set this precedent
// (`grade` from powerBand's tier, ConsumableTuning.cs:55-56). UniqueBudget.TierOfPowerBand is the ONE
// mirror of bands.v1.json powerBand.tierMap -- GemContainerBuild.cs:14-16 reuses it for exactly this
// reason, and a fourth private five-band switch is the duplication that rule exists to stop.
//
// An unknown band THROWS. It must never fall back to UnauthoredInsertTier: a silently under-reported
// tier is the bug this module exists to remove (CombinationDistance.cs:225 filters on
// `Insert.Tier >= need.MinTier`, so tier 1 makes a satisfiable combination look unsatisfiable) and it
// has no symptom -- the player just never sees the resonance fire. T5: a missing tunable is a load
// rejection naming it, never a built-in default.
int tier;
try { tier = UniqueBudget.TierOfPowerBand(powerBand); }
catch (ArgumentOutOfRangeException)
{
    throw new GemCorpusRejection(
        $"gem '{id}' names powerBand '{powerBand}', which is not one of bands.v1.json's five — " +
        "an insert with no resolvable tier would silently under-report every tier-gated combination " +
        "it could have satisfied, which is a bonus that vanishes with no symptom");
}
```

---

## Tunables

| Number | Meaning | Owning `gk-core/data/tuning` file |
|---|---|---|
| `insertTiers.upcycleInputPerOutput` (**3** today) | How many tier-`k` inserts one tier-`k+1` insert costs — the primary drain on the gem inventory | `gk-core/data/tuning/sockets.v1.json` (**has `version`: 2 → bump if changed**) |
| `insertTiers.count` (**5** today) | How many rungs the insert ladder has. A **soft content axis**, explicitly not a cap | `gk-core/data/tuning/sockets.v1.json` (same file, same bump) |
| `operations.forge-gem` — `souls` ×30 on `rung`, `shard` ×1 flat, `essence` ×3 on `rung`, `catalyst.forge` ×1 | The upcycle's price | `gk-core/data/tuning/materials.v1.json` (**has `version`: 1 → bump if changed**). ⚠ **Already priced — confirm, do not re-author.** ⭐ **Now repriced by strain-splice-host's report (R20, 2026-09-18):** when [`combo-budget`](../strain-splice-host/spec-combo-budget.md) finds a Strain/Splice cell whose cheapest route has no bore or imbue leg, it derives the smallest `operations.forge-gem.souls.coefficient` that passes the cell, and [`socket-pricing`](../strain-splice-host/spec-socket-pricing.md) §5 publishes it as a new `materials.v{n+1}.json` with `gk-core/tools/tuning/publish.py` — sequenced per both maps' revision tables ([species-gear-chain-map.md](../species-gear-chain-map.md) § Tuning revisions `materials` row; [strain-splice-host-map.md](../strain-splice-host-map.md) §4 *Revision sequencing*). This module still confirms the leg's shape (souls on `rung` = output gem tier) and never re-authors it by hand; a republished coefficient is a price change, not a shape change, and this module's tests assert the shape, never the coefficient |
| `powerBand.tierMap` — `trivial` 1 … `extreme` 5 | The band→tier map every kind shares | `gk-data/packs/fusion/data/seed/items/_registry/bands.v1.json` — a **hand-authored registry** (`**/_registry/**`), not generated output, and **not** a `gk-core/data/tuning` file. It is a closed vocabulary: changing it is ask-first |

~~⚠ **A revision is a `version` bump inside the existing file, never a new `v{n}.json`.**~~ ⛔ *Corrected 2026-09-18 (strengthen pass — [map § Tuning revisions](../species-gear-chain-map.md), which reverses the map's § Corrections #11):* a revision publishes a **new** `<domain>.v{n+1}.json` through `gk-core/tools/tuning/publish.py` (tunables-ssot **T4**; the tool refuses to overwrite, `publish.py:556`), with the host's reader switched in the same commit — **never** an in-place `version` bump. The internal `version` field is not a revision identity (`sockets.v1.json` already reads `3` from in-place history). The number is not reserved here: it is whatever `publish.py` derives at build time, in the land order the map's table gives (for `sockets`, after strain-splice-host's `circuit-topology` v2 and `combo-budget`, per [strain-splice-host-map.md](../strain-splice-host-map.md) *Revision sequencing*). The
ideal's `sockets.v{n}.json` phrasing (`:908`) was right.

⛔ **No hard progression ceiling is introduced.** `insertTiers.count` stays a soft axis (its own note,
`sockets.v1.json:43`); a combination's granted tier stays unbounded above (`:24`); `upcycleInputPerOutput`
is a **bounded ratio between two tiers of one thing** (`:43`), which is PS-8 exempt by nature and says so
in the file.

**Structural (stays `const`, with a comment saying why):**
- `GemInsertCorpus.UnauthoredInsertTier = 1` — **kept, narrowed, and its existing comment already
  qualifies**: *"Structural, not a tunable: it is the identity of 'no tier was authored', and a balance
  pass has nothing to change here"* (`ItemCardEndpoints.cs:125-127`). After this module it means only
  *"this container is not in the gem corpus at all."*
- `UniqueBudget.TierOfPowerBand`'s five arms — a **mirrored closed registry**, not a balance number.
  Its comment already says why a sixth would be an atom-layer change (`UniqueBudget.cs:30-32`).
- `structuralCeiling = 4` / `SocketLimits.SocketMaxCeiling` — untouched by this module; already
  correctly marked structural and enforced by a throw (`SocketTuning.cs:158-162`).

## Numeric types

- **An insert tier is an ORDINAL, not a magnitude.** It is `int`, it is bounded by `insertTiers.count`,
  it is compared (`Insert.Tier >= need.MinTier`) and never multiplied into a damage number. Stated
  explicitly so no later reader assumes CLAUDE.md's `long` rule was overlooked here — **it does not
  apply, because a tier indexes a ladder; it is not a point on one.**
- ⛔ **A tier must never become a magnitude multiplier.** The magnitude a tier selects lives on the
  atom (`atom_id = {family}[.{variant}].t{tier}`, `definitions.md` §1) and rides `contentScale`
  through the existing atom path. Multiplying by the tier would be a **second** curve on top of the
  one the atom ladder already is — the exact defect `ssot-power-scale.md` §10 exists to prevent.
- **The forge-gem cost is a magnitude and is `long`** — it prices on `rung`, so it scales. Widen
  before multiplying (`(long)a * b`, never `(long)(a * b)`); divide by 1000 **last, exactly once**;
  floating-point is allowed (owner ruling 2026-09-15 — precision is not overflow; a `double` feeding a hashed or persisted value records the platform stamp (`ssot-power-scale.md` §10.7)); **integer
  overflow throws, never wraps.** The existing cost path already does this; this module adds no new arithmetic to it.
- `upcycleInputPerOutput` is a small `int` count of stock items, validated `>= 2` at load.

⛔ **No new `ssot-power-scale.md` §10 row is owed.** Nothing here derives a number from a level.
The tier comes from an authored band; the cost reads the already-listed `operations.*` path. Stated
explicitly rather than left for a reviewer to check — §10 is closed, and a row that is not owed is
worth saying out loud.

## ActorHub gate

**Contributes nothing; consumes nothing.** This module changes which **tier** an insert reports to the
socket/combination layer. It does not move a single combat number, because — measured — **no socket
state reaches combat at all today**: `store.GetSockets` has **7** production call sites, all
card/surface/workbench (`RpgStore.ItemCard.cs:351`, `ItemSurfaceEndpoints.cs:105`, `:181`,
`ItemWorkbench.cs:309`, `:359`, `:389`, `:612`), and **zero** in `gk-core/src/FusionRpg.Core/Battle/`, the
equip runtime, or `gk-fusion/src/FusionRpg.Injector/`. Closing that is
[`socket-combat-wiring`](spec-socket-combat-wiring.md)'s job, and it **depends on this module**.

⛔ **No `*Composer*`, no private `ChannelMods` combat writer, no second compose gate.**
`gk-core/scripts/guard-actor-hub.py` must stay green.

## Testing strategy

**Store tests run in memory**; a failed temp-delete is a **failure**, never `catch { }`.

| Level | What it asserts |
|---|---|
| Unit | ⭐ **Every gem entry's tier is `TierOfPowerBand(entry.powerBand)`** — asserted as the *relationship*, recomputed per entry, never as a table of expected values |
| Unit | An unknown `powerBand` is a **rejection naming the gem**, and never resolves to `UnauthoredInsertTier` |
| Unit | `UnauthoredInsertTier` is reached **only** for a container id the corpus does not carry — proven by a lookup miss, not by a tier-1 gem |
| Unit | `UniqueBudget.TierOfPowerBand` and `bands.v1.json`'s `powerBand.tierMap` **agree key-for-key** — the mirror is reconciled against its source, in the shape `SocketTuning.cs:158-162` already uses for `structuralCeiling` |
| Contract | `powerBand` membership is pinned at **5** — a **closed vocabulary** (`bands.v1.json` `bandCount: 5`, with the registry's own stated reason: one band per atom tier; a sixth needs a `.t6` row on every family). **Pinning is correct here and this is why.** |
| Contract | `insertTiers.count` is **not** enforced as a ceiling on an insert's tier — a tier above `count` is accepted by the socket layer, proving the soft axis stays soft |
| Contract | Every ingredient row's `minTier` falls inside `[1..insertTiers.count]` — the existing `StrainSpliceTuning.cs:124-128` guarantee, re-asserted |
| Integration | ⭐ **Every combination whose ingredient families are all present in the gem corpus becomes satisfiable** — computed from the corpus on both sides, never from a literal. This is the module's acceptance test |
| Integration | A `forge-gem` execution consumes exactly `upcycleInputPerOutput` copies of the input and grants exactly one output, from stock, in one transaction |
| Integration | Replaying the same `(playerId, correlationId)` is idempotent and returns the recorded result |
| Regression | An item with **no** sockets, and an item whose sockets are empty, resolve byte-identically to today |
| Guard | `guard-dal.py`, `guard-actor-hub.py` green; `ItemSeedValidator` green |

⛔ **No test asserts a population count.** **104** gems, **76** combinations, **67** recipes, **232**
ingredient rows, **118** tier-gated rows, **304** slots, **24/48/32** per band — every one of those is
a **reading that moves when content ships**, and pinning any of them would make a successful seed
extension look like a regression. Assert instead: `len(parsed) == entries on disk`; ids unique; every
`family` joins to the atom catalog; every `powerBand` is in the closed five; `tier ==
TierOfPowerBand(powerBand)` per entry; every ingredient family resolves. **Print the scale; never
assert it** ([validation-ssot.md](../validation-ssot.md) §4).

⛔ **No test asserts a gem's generated `name` or `nameKey`.** Authored text is the model's to change.

## Boundaries

**Always**
- Derive the tier from `powerBand` through `UniqueBudget.TierOfPowerBand` — **one mirror, reused**.
- Refuse an unknown band by name; never fall back to tier 1.
- Treat `gk-data/packs/fusion/data/seed/items/gems/**` and `gk-data/packs/fusion/data/seed/items/recipes/**` as **generator output** — all three
  gem partitions and `recipes.json` carry `_meta.model` / `promptVersion` / `batch`.
- Confirm `operations.forge-gem` rather than re-authoring it.
- Run store tests in memory.
- Commit with plain `git` (explicit paths).

**Ask first**
- ⛔ **Widening `bands.v1.json`'s `powerBand` enum.** It is a **closed vocabulary** with a stated
  structural reason — a sixth band needs a `.t6` atom row on every family, which is an atom-layer
  change, not a registry one (`gk-data/packs/fusion/data/seed/items/_registry/bands.v1.json:46`). Extending a closed enum is ask-first.
- ⛔ **Widening `gemgen`'s `POWER_BAND_ROTATION`** to author `trivial`/`extreme` gems. It changes the
  shipped ladder's breadth and needs a regeneration — a content decision, not a wiring one.
- Changing `upcycleInputPerOutput` from 3, or `insertTiers.count` from 5.
- Re-pricing `operations.forge-gem` **by hand or from this module**. The one sanctioned reprice is
  strain-splice-host `combo-budget`'s derived souls coefficient (R20), published by `socket-pricing`.
- Adding a `MutationOpKind` member. **This module needs none** — `forge-gem` mutates no instance — and
  that enum is separately ask-first with `Repair` and `Elevate` already queued
  ([spec-rarity-promotion.md](spec-rarity-promotion.md) §Real gap).

**Never**
- ⛔ Add a `tier` field to a gem entry. `entry-shapes.md:81` makes it an `OwnershipViolation`, and the
  band already carries it.
- ⛔ Hand-edit `gems/*.json` or `recipes.json`. Fix `gemgen` / `recipegen` and regenerate.
- ⛔ Write a fourth private `powerBand` switch. Three consumers, one mirror.
- ⛔ Let `insertTiers.count` become a clamp on an insert's tier. It is a soft axis and the file says so
  three times.
- ⛔ Silently under-report a tier. A combination that quietly never fires is the "bug with no symptom"
  `SocketLimits`' own comment warns about.
- ⛔ Multiply a magnitude by a tier. The tier **selects** an atom rung; it is not a coefficient.
- Assert a population count.

## Success criteria

1. ⭐ **Every shipped gem reports a tier derived from its own `powerBand`**, through
   `UniqueBudget.TierOfPowerBand`, at all three call sites — `ItemCardEndpoints.cs:154`,
   `ItemSurfaceEndpoints.cs:225`, `ItemWorkbench.cs:358`.
2. ⭐ **Every combination whose ingredient families are all present in the gem corpus is satisfiable**,
   proven by a test that computes both sides from the corpus. (Measured today: every one of the 118
   tier-gated ingredient rows names a family that has at least one shipped gem, so the expected
   outcome is *all of them* — but the test asserts the relationship, not that count.)
3. An unknown `powerBand` is a **rejection naming the gem**; no path falls back to tier 1.
4. `UnauthoredInsertTier` is reached only for a container the corpus does not carry, and its comment
   says so.
5. The mirror/registry reconciliation test is green: `TierOfPowerBand` agrees with
   `bands.v1.json powerBand.tierMap` key-for-key.
6. `SocketTuning.UpcycleInputPerOutput` has a real production reader.
7. `forge-gem` recipe rows exist **because `recipegen` emits them**, and the regenerated diff is
   committed. No seed JSON is hand-edited.
8. `ItemWorkbench` exposes a sixth verb with a POST endpoint, shaped on `Upcycle`, consuming exactly
   `upcycleInputPerOutput` inputs per output and idempotent on `(playerId, correlationId)`.
9. `insertTiers.count` remains a soft axis — a tier above it is accepted, proven by test.
10. Core, Server and Data suites green; `ItemSeedValidator` green; `guard-dal.py` and
    `guard-actor-hub.py` green; `audit-magic-numbers.py --domain sockets` clean.

## Open questions

1. **Does the shipped gem ladder stay `[2..4]`, or does `gemgen` widen to author `trivial` (t1) and
   `extreme` (t5) gems?**
   **Recommendation: stay at `[2..4]` for this module, and widen separately.** Nothing shipped needs
   t1 or t5 — all 118 tier-gated ingredient rows ask for `minTier ≥ 2`, and `removal.freeThroughTier: 2`
   / `costedThroughTier: 3` already price a `[2..4]` corpus sensibly. Widening is a regeneration with
   its own review; bundling it would make a wiring change and a content change land in one diff, which
   T7 forbids. *(Irreversible? No — a later regeneration adds rungs without migrating anything.)*

2. **`operations.forge-gem` prices two of its four legs on `rung` — but a gem has no rarity rung, it
   has a tier. What does the verb feed as `rung`?**
   **Recommendation: feed the OUTPUT tier as the rung input, and say so in the tuning file's own note.**
   It is the only number on a gem that varies, it makes a t4 upcycle cost more than a t2 one (which is
   the intent of a `rung`-variable leg), and the alternative — `MaterialHasNoRung`, which `Upcycle`
   passes at `ItemWorkbench.cs:205` — would make every gem tier cost the same and quietly delete the
   ladder's drain. Requires one line of tuning prose, no number change. *(Irreversible? No — the coefficient
   is tunable either way.)*

3. **Is `upcycleInputPerOutput: 3` still the right drain now that it has a reader, given module 14's
   material upcycle sits at 5?**
   **Recommendation: ship 3 unchanged and revisit after play.** The two ladders are deliberately
   different things — material grade `g → g+1` versus insert tier `k → k+1` — and the shipped values
   were chosen independently by their own owners (`materials.v1.json` `upcycle.note`, `sockets.v1.json:43`).
   Changing one to match the other now would be a balance decision wearing a consistency argument's
   clothes. It is a one-line tuning bump later. *(Irreversible? No.)*

4. ⭐ **DECIDED 2026-09-13 (owner): same-family only.** `forge-gem` upcycles within a family
   (3× `atom.might` t2 → 1× `atom.might` t3); it may **not** consume any three same-tier gems
   regardless of family. Cross-family conversion makes every gem fungible, which
   deletes the collection pressure the socket system runs on and makes `atom.elemental-power` (the one
   family with **7** shipped entries, versus 1 for each of the other 97) a laundering route into any
   other family. Same-family also needs no new tuning row — the family is already on the seed entry.
   *(Irreversible? Yes in one direction — a shipped cross-family recipe that later narrows would
   invalidate player stock. That is why it is asked before build, with a default of the narrow rule.)*
