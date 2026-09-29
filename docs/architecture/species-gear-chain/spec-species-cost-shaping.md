# Spec: Species cost shaping (`species-cost-shaping`)

**Initiative:** `species-gear-chain` ([map](../species-gear-chain-map.md)) · **Module:** `species-cost-shaping`
**Owning program:** `item` module 14 (`salvage-craft`) + module 16 (`sockets`), by verb ownership
**Depends on:** `set-species-binding`
**Status:** spec, 2026-09-13. Awaiting owner approval. No build authorized. ⚠ *2026-09-18: approved through `tasks/species-gear-chain-plan.md`; build state — unbuilt (T32).*
**Source ideal:** [species-craft-ideal.md](../species-craft-ideal.md) § The shape 2

> **Amended 2026-09-18 for owner ruling R-SC2 (2026-09-18)** — `species-craft-ideal.md` § R-SC2.
> The threshold is **one default rung plus an explicit per-verb override** — explicit-or-absent, never
> a sentinel, the same shape `craft-risk-ladder` ships for the potential override
> (`HeadDerivationTables.cs:32-37`). Open question 1 is closed; § Design 1, § Tunables and § Testing
> strategy carry the shape. **Build state:** unbuilt — `grep -rn speciesCost src gk-core/data/tuning` returns
> nothing (T32, Phase 4).

---

## Objective

**Make a species-bound set piece cost something shaped by its species — using only material ids that
already exist, and only above a threshold rung.**

> **Owner, 2026-09-13:** *"yes, and gate it above a rung."*

This is the **legibility** half of the species binding. It makes the species visible at the bench
*before* species materials exist, and it widens no vocabulary — so it is shippable on
`set-species-binding` alone, with `species-materials` following later.

### Why the gate is the design, not a softener

**This is the Monster Hunter shape, and the gating is what makes it so.** In MH the rare per-monster
part gates the **top** of a tree while common and generic parts carry the early steps — which is
exactly what keeps low-tier creatures relevant.

Applying a species cost at **every** rung would make the first upgrade of every piece a species
errand. That is the *"every recipe becomes a travel itinerary"* failure `ssot-materials-crafting.md`
§3.4 already refused for zone-keyed ids. **The gate is not a concession; it is the thing that stops
this repeating a failure the repo has already ruled against.**

---

## What exists today — verified against the shipped tuning and code

### Built

- **`gk-core/data/tuning/materials.v1.json` `operations` has exactly ten rows** — `forge`, `upcycle`,
  `forge-gem`, `bore`, `imbue`, `socket`, `elevate`, `temper`, `reroll-one`, `reroll-all`. Each row is
  a leg set (`souls` / `substrate` / `shard` / `essence` / `catalyst`), each leg a `coefficient` plus
  a named `variable` class (`grade` | `rung` | `flat` | …).
- ⭐ **`rung` is already a first-class cost variable.** `bore`, `imbue`, `forge-gem` and `elevate` all
  price on it. **So "cost keys on a rarity rung" needs no new mechanism at all** — only a second rung
  to read (the species', rather than the item's).
- **`costBandMultiplierPerMille`** already exists (`cheap` 500 → `exorbitant` 8000) as the
  multiplier-shaped lever, and its own note records that it **mirrors**
  `gk-data/packs/fusion/data/seed/items/_registry/bands.v1.json`, which is *"FROZEN at registryVersion 1 and is the
  authority"* — mirrored because *"Core never reads a file"* (T7.2), with `MaterialCorpusTests`
  asserting the two agree value for value **against the real registry**.
- **`shard.{rarity}` is already minted** per rung, so a species' rung already has a material id.
- **`CraftOperation`** is a closed ten-member enum; *"adding a verb here is code."*
- `SetExclusivityValidator.cs:33` is the only set-aware craft rule today (D21 suppresses
  Strain/Splice on set pieces); `:40` `MaySocket => true`.

### Real gap

Nothing reads a **species** anywhere in the cost path. The multiplier and the rung variable exist; the
input does not — which is exactly what `set-species-binding` supplies.

---

## Design

### 1. A multiplier, keyed on the species' rung, gated above a threshold

```
speciesMultiplier(piece) =
    piece.speciesId is absent                      -> 1000‰   (generic, unchanged)
    speciesRung(piece) <  thresholdFor(verb)       -> 1000‰   (below the gate, unchanged)
    otherwise                                      -> speciesCostMultiplierMilli[speciesRung]

thresholdFor(verb) =
    speciesCostThresholdRungByVerb has verb        -> that authored rung   (explicit override)
    otherwise                                      -> speciesCostThresholdRung (the one default)
```

**R-SC2's shape, stated so it is not softened later:** the override map is **explicit or absent**.
An absent verb key means *use the default*; a present key must carry a real rung id from the ten.
There is no sentinel value (no `null`, no `-1`, no `"default"` string) meaning "inherit" — the
absence of the key is the only way to inherit. A key naming a verb outside `CraftOperation`'s closed
set, or a rung outside the ten, is a **load rejection naming the key** (`tunables-ssot.md` T5).

**Why a source-bound gate is not a ceiling (R-SC2's prior-art correction).** Monster Hunter's
materials are **source-bound** — the right monster must be hunted, with no substitute — and that is a
*content* gate, not a price. Above the threshold this module only makes the cost **larger**; the
species material that makes it **source-bound** is `species-materials`'. The failure mode R-SC2 names
for that pairing — *a wall when the source is content nobody wants to fight* — is answered by making
the source reachable (the selection modules), never by a fallback currency; this module adds none.

Applied **beside** `costBandMultiplierPerMille`, never folded into it — the band multiplier mirrors a
**frozen registry** that is asserted value-for-value by `MaterialCorpusTests`, and folding a second
factor into it would break that assertion and fork a frozen authority.

⚠ **Multiplier composition order matters and must be stated:** both are per-mille, so applying them
naively multiplies two thousands. **Widen, multiply, then divide by 1000 exactly once at the end** —
never divide between the two.

### 2. Orthogonality — the MH rule that binds here

**Upgrade level and set membership stay independent.** No craft verb may break a set bonus, because
the bonus counts **membership**, not upgrade state — and `SetEvaluator` is already class-agnostic, so
this holds by construction today. **This module must not change that.**

### 3. The one shipped set rule that deserves a second look

D21 suppresses Strain/Splice on set pieces exactly as D2 forbade runewords in set items —
genre-confirmed, and not in question. **D2 also capped set pieces at one socket**; whether we want that
second restriction is a real question, and it is **`socket-allowance-by-kind`'s**, already decided
there as a tunable reduction rather than a cap of one. Named here only so the two are not re-litigated
separately.

---

## Tech stack

C# .NET 8 (`FusionRpg.Core/Items/Materials`), xUnit. No new dependency. No FE surface.

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Material"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~CostClass"
dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~MaterialSpend"
dotnet run --project gk-forge/tools/ItemSeedValidator
python gk-core/scripts/audit-magic-numbers.py --targets M1
python gk-core/scripts/audit-overflow.py
```

## Seedsmith / generator

**No generator involved.** The multiplier, the default threshold and R-SC2's per-verb override map are
authored runtime tuning in the current `data/tuning/materials.v{n}.json`, published as a new
`materials.v{n+1}.json` through `gk-core/tools/tuning/publish.py` (extended first — the multiplier table and the
override map are **new keys**, which `set` refuses to invent; tunables-ssot §7.1); the species
rung the gate reads comes from `set-species-binding`'s field. No seedsmith adapter, seed field or
regeneration is part of this module.

## Project structure

| Path | Role |
|---|---|
| `gk-core/data/tuning/materials.v1.json` | Gains `speciesCostMultiplierMilli` + `speciesCostThresholdRung` + `speciesCostThresholdRungByVerb` (R-SC2, ships `{}`) — ~~`version` bump~~ a **new** `materials.v{n+1}.json` via `publish.py`, extended first for the new keys (map § Tuning revisions) |
| `gk-core/src/FusionRpg.Core/Items/Materials/MaterialTuning.cs` | Parser + rejections |
| `gk-core/src/FusionRpg.Core/Items/Materials/CostClassMatrix.cs` | Read only — **no new verb, no sixth class here** |
| `tests/FusionRpg.Core.Tests/Items/Materials/` | Gate, composition-order and orthogonality tests |

## Code style

```csharp
// Applied BESIDE costBandMultiplierPerMille, never folded into it: that table MIRRORS the frozen
// bands.v1.json registry and MaterialCorpusTests asserts the two agree value-for-value, so folding
// a second factor in would fork a frozen authority.
// Widen first, divide by 1000 ONCE at the end — two per-mille factors applied naively multiply
// two thousands, and dividing between them loses precision twice.
var cost = checked(baseCost * bandMilli * speciesMilli / 1_000_000L);
```

⚠ The `/ 1_000_000L` is the two divisions combined into one. **This is the only place the combined
divisor may appear**, and it is commented because a reader will otherwise "fix" it to `/1000` twice.

---

## Tunables

| Number | Meaning | Owner |
|---|---|---|
| `speciesCostMultiplierMilli` — one per rung | Slice 2's lever. Shapes a set piece's cost by its species' rarity rung, using material ids that already exist | the next `data/tuning/materials.v{n+1}.json` publish (map § Tuning revisions) |
| `speciesCostThresholdRung` | ⭐ The gate — **the one default** (R-SC2). Below it, crafting stays generic | Same file |
| `speciesCostThresholdRungByVerb` — `{ craftOperationId: rungId }` | ⭐ **R-SC2's explicit per-verb override.** Ships **empty** (`{}`) — every verb uses the default until a balance pass shows a verb needs its own gate. Absent key ⇒ default; present key ⇒ that rung; never a sentinel | Same file |
| Which craft verbs the species cost applies to, keyed by `CraftOperation` id | Whether the species leg rides every verb or only some | Same file, `operations` |

⚠ **`speciesCostMultiplierMilli` is a rung-keyed cost ladder over a `long` magnitude, and therefore
owes a `ssot-power-scale.md` §10 row** — the same ask `rarity-promotion` and `item-upgrade-tree` file
for their own cost curves. `ssot-power-scale.md` §10 is a **closed inventory**: *"A power-shaped number
that is not in this table does not have permission to exist."* §10 rows 6/26/27/31/33 are the
precedent, and row 18 shows an authored per-rung table still earns one.
**File it once, covering all three modules.**

**Structural (stays `const`, with a comment saying why):** the closed 27-id material vocabulary and the
five spend classes. Widening either is a **reviewed change** against `ssot-materials-crafting.md`
§3.1/§3.4 — **not a tunable, and not this module's** (it is `species-materials`').

~~⚠ **A revision is the `version` field inside `materials.v1.json`, not a new file** — the shipped
pattern.~~ ⛔ *Corrected 2026-09-18 (strengthen pass — [map § Tuning revisions](../species-gear-chain-map.md), which reverses the map's § Corrections #11):* a revision publishes a **new** `<domain>.v{n+1}.json` through `gk-core/tools/tuning/publish.py` (tunables-ssot **T4**; the tool refuses to overwrite, `publish.py:556`), with the host's reader switched in the same commit — **never** an in-place `version` bump. The internal `version` field is not a revision identity (`sockets.v1.json` already reads `3` from in-place history). The number is not reserved here: it is whatever `publish.py` derives at build time, in the land order the map's table gives (for `sockets`, after strain-splice-host's `circuit-topology` v2 and `combo-budget`, per [strain-splice-host-map.md](../strain-splice-host-map.md) *Revision sequencing*). This module's publish is the **first** pending `materials` revision in the map's land
order; `species-materials` rebases onto it, and strain-splice-host's conditional `socket-pricing` publish
takes whatever number is next when it lands. And ⛔ **`costBandMultiplierPerMille` must not be edited**: it mirrors a frozen registry and a
test asserts the mirror.

## Numeric types

- Costs are **`long`**. They are magnitudes on an endless-progression axis, and `elevate`/`bore`
  already price on `rung`, so a cost scales with the ladder.
- **Widen before multiplying** — `(long)base * milli`, never `(long)(base * milli)`.
- **Divide by 1000 last, exactly once** — here, once for two combined per-mille factors.
- A per-mille `int` exceeds its range at `Θ` = 3,213 (`CLAUDE.md` "Numeric types"). **Floating-point is allowed** (owner ruling 2026-09-15) — a `float` not being integer-exact past 2^24 is precision, not overflow.
- **Overflow throws, never wraps.** `checked`, no silent `unchecked`.
- The multipliers themselves are **bounded ratios** in per-mille, bounds-checked at load — exempt and
  commented as such.

## ActorHub gate

**N/A and checked.** A craft *cost* is an economy number, not an actor combat / derived /
AppliedCombat magnitude. Nothing here composes, contributes to, or reads Hub output. **No private fold
is introduced.**

## Testing strategy

| Level | What it asserts |
|---|---|
| Unit | ⭐ **Below the threshold rung the cost is byte-identical to today** — the regression that proves the gate |
| Unit | At and above the threshold, the species multiplier applies |
| Unit | A piece with **no** species (the 40 `build.*`/`theme.*` themed sets) costs exactly as today |
| Unit | ⭐ **Composition order** — band × species with one division, proven against a hand-computed value |
| Unit | ⭐ **`costBandMultiplierPerMille` still mirrors `bands.v1.json` value for value** — the existing `MaterialCorpusTests` assertion must stay green, proving nothing was folded in |
| Unit | A multiplier outside `[0, ...]` or a threshold rung outside the ten is a **load rejection** |
| Unit | An absent `speciesCostMultiplierMilli` section **throws** — no key has a default (T5) |
| Unit | ⭐ **R-SC2 — override resolution:** a verb absent from `speciesCostThresholdRungByVerb` gates at the default; a verb present gates at its own rung; proven with one verb each side of the default |
| Unit | ⭐ **R-SC2 — no sentinel:** an override value of `null`, `""` or a non-rung string is a load rejection naming the verb key; an override key naming a non-`CraftOperation` id is a load rejection |
| Unit | The override **section** itself is required (an empty `{}` is legal; a missing section throws) — absence of the *map* is not the same as an empty map |
| Unit | Every rung has a multiplier row (closed vocabulary — pinning is correct) |
| Unit | ⭐ **Orthogonality** — a set bonus's evaluation is unchanged by any craft at any cost |
| Unit | `checked` throws rather than wrapping at the boundary |
| Contract | `ItemSeedValidator` green |

⛔ **No test asserts how many sets carry a species.** That is a reading.

## Boundaries

**Always**
- Apply the species multiplier beside the band multiplier, never inside it.
- Widen, multiply, divide once.
- Fail closed on a missing section, an unknown rung, or an out-of-range multiplier.
- Run `audit-magic-numbers.py --targets M1` — this module touches the balance surface directly.
- Commit with plain `git` (explicit paths).

**Ask first**
- The threshold rung value (Open question 1) — it is the whole feel of the feature.
- ⛔ **The `ssot-power-scale.md` §10 row** for `speciesCostMultiplierMilli` (above). §10 is closed and
  adding a row is a reviewed change to that document.
- Applying the species cost to a verb owned by another module (`bore`/`imbue` are module 16's).

**Never**
- ⛔ Edit `costBandMultiplierPerMille`. It mirrors a **frozen** registry asserted by a test.
- ⛔ Widen the 27-id material vocabulary or add a sixth spend class here. That is `species-materials`',
  and it is a reviewed change.
- Add a `CraftOperation` member — the enum is closed and *"adding a verb here is code."*
- Apply the species cost below the threshold. That is the travel-itinerary failure §3.4 refused.
- Let a craft verb break or re-check a set bonus.
- Write a balance number as a `const`. Policy, Catalog, Rules, Ruleset and Math files **are** the
  balance surface — no bare literals there.
- Assert a population count.

## Success criteria

1. A set piece whose species sits at or above the threshold rung costs more, by a tunable per-rung
   multiplier.
2. Below the threshold, and for species-less pieces, costs are **byte-identical to today**.
3. The band multiplier is untouched and still mirrors the frozen registry value for value.
4. Multiplier composition is one widen-multiply-divide, proven against a hand-computed value.
5. Missing section, unknown rung and out-of-range multiplier all **reject at load**.
6. Set bonus evaluation is provably unchanged.
7. No new material id, no new spend class, no new craft verb.
8. Core and Data suites green; `ItemSeedValidator` green; `audit-overflow.py` no new critical.

## Open questions

1. ✅ **RULED 2026-09-18 (R-SC2) — one value plus an explicit per-verb override.** The shape is in
   § Design 1 and § Tunables. The **rung value itself** is still balance data, set in T32 — the ruling
   fixes the shape, not the number. Original question: *where is the threshold rung set, and is it one
   value or per-verb?*
2. **Is the multiplier per-rung or a single factor applied above the gate?** **Recommendation:
   per-rung.** A flat factor makes the gate a cliff; a per-rung table lets the cost climb with the
   species, which is the MH shape being copied.
3. ⭐ **DECIDED 2026-09-13 (owner): yes — the species cost applies to `elevate`.** Balanced together
   with the promotion cost curve in `rarity-promotion`'s own review (T32/T26 in the plan), not stacked
   unexamined.
