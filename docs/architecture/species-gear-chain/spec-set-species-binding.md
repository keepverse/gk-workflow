# Spec: Set species binding (`set-species-binding`)

**Initiative:** `species-gear-chain` ([map](../species-gear-chain-map.md)) · **Module:** `set-species-binding`
**Owning program:** `item` module 13 (`set-charm-gen`)
**Status:** spec, 2026-09-13 · **revision 2, 2026-09-21** (owner ruling below). Approved through
`tasks/species-gear-chain-plan.md`. Build state: `speciesId` **built and proven** (forward emission,
deterministic repair); `setClass` — **ruled 2026-09-21: build the set-planning system**, delivered by
§ [The set-planning system](#the-set-planning-system--ruled-2026-09-21-owner).
**Source ideal:** [species-craft-ideal.md](../species-craft-ideal.md) § The shape 1

> **Owner, 2026-09-21:** *build the set-planning system — do not drop `setClass`. The 2026-09-10
> topology classes are the target, not a dead design: their role-count shapes are authored into a real
> set-planning system and the shipped sets are brought onto it.*

Revision 2 records that ruling, authors the classes as versioned data, and — per this spec's own
`Ask first` list — **answers Open question 1 from the class design rather than from convenience.**

---

## Objective

**Make a set piece's species and its topology class queryable fields, instead of strings a human can
read and a shape nobody declared.**

> **Owner, 2026-09-13:** *"real field, use deterministic engine to repair it, and extend seedsmith
> generator — this should be decided by deterministic engine, LLM shouldn't."*

844 shipped set entries are already themed on a creature. Nothing can *query* that today, so every
species-aware behaviour downstream — cost shaping, species materials, an armoury filter — has nothing
to key on. This module adds the key.

It needs **no new material, no new craft verb, and no evaluator change** — `SetEvaluator` is already
class-agnostic. It is a schema change, a generator change, a deterministic repair, and a
regeneration.

**The second field, ruled 2026-09-21.** `speciesId` is half of what a set declares. The other half is
the set's **topology class** — which of the three classes `decisions.md`'s 2026-09-10 **Set topology
classes** row (`decisions.md:141`) plans a set from. That row retired the universal four-member
default and the six-role cap and made the class a **declared planning input**, so a set without a
`setClass` is a set whose shape nothing can plan, validate or grow. § The set-planning system authors
the three classes as versioned tuning data, resolves every shipped entry onto them deterministically,
and refuses a shape no class admits.

⛔ **The LLM must not decide this, and the repo already enforces why.** Species identity is a
**join**, not a judgement. The binding principle is that the model writes *identity* (names, flavour)
while deterministic code writes everything a system keys on, and `audit_schema` exists precisely to
keep model output out of fields like this. A model-authored `speciesId` would be an unverifiable
guess at a fact the corpus already contains.

---

## What exists today — measured this session

### Built

**910 set entries across 885 files in `gk-data/packs/fusion/data/seed/items/sets/**`.** A shipped entry's fields are
`id`, `nameKey`, `name`, `themeKey`, `members`, `thresholds`, `flavor`, `tags`, `notes`.

⚠ **Corrected: there are three shapes, not one.** 880 of 910 entries carry exactly that nine-field
set; **24 lack `flavor`**, and **5 carry `flavorKey`/`iconKey` while lacking `tags`/`notes`**. The
repair must tolerate all three rather than assume the modal shape.

**884 distinct `themeKey` values**, by prefix (counted over entries):

| Prefix | Entries | Has a species? |
|---|---|---|
| `creature.*` | **844** | yes |
| `build.*` | 36 | no |
| `theme.*` | 31 | no |

- `SetEvaluator` counts **membership**, not upgrade state, and is class-agnostic — so adding a field
  changes no bonus.
- `SetExclusivityValidator.cs:33` is the **only** set-aware craft rule today (D21 suppresses
  Strain/Splice on set pieces); `:40` `MaySocket => true`.

### Real gap

There is **no `speciesId` and no `setClass` field on a set entry.** `themeKey` is a presentation key
that happens to encode the species.

⚠ *Revision 2 (2026-09-21) — status of that paragraph, since the reading above was taken at revision 1.*
**Both fields are now built.** `speciesId` ships on all 844 `creature.*` entries (a join from the theme
registry, with the 66 `build.*`/`theme.*` entries carrying explicit absence). `setClass` is emitted
forward by `set_entry` through `setgen/topology.py` and re-planned onto the shipped corpus by the
deterministic repair — the two remaining build steps of this revision. The paragraph is kept because
it is what the measurement found, not because it is still true.
### ⭐ The repair is total — and it has one trap, found by measurement

The ideal expected the repair to refuse a remainder. **It does not need to.** Measured directly:

> **All 844 distinct `creature.*` themeKeys resolve to a species in the 904-species catalog — 844 of
> 844, zero unresolved.**

⚠ **But only case-insensitively.** `themeKey` is lower-case (`creature.abyssswordstar`) while
`speciesId` is PascalCase (`AbyssSwordStar`). **An exact-match repair resolves zero of 844** — it
would silently produce an entirely empty column and look like a content gap rather than a join bug.

This is the single most important line in this spec: **the join is case-normalising, and that must be
explicit, tested, and commented — never incidental.**

### ⭐ A better join than parsing the key — found while specing `ladder-consistency-repair`

`gk-data/packs/fusion/data/seed/creatures/_registry/themes.v1.json` holds **904 theme rows keyed by exactly these
`themeKey` values**, and each row carries `speciesId` **as a field**:

```json
"creature.abyssswordstar": { "speciesId": "abyssswordstar", "displayName": "…", "rarity": "chimeric", … }
```

**So the corpus already ships a `themeKey → speciesId` index.** Preferring it over suffix-parsing is
strictly better: a registry lookup **fails loudly on a missing key**, while string manipulation
quietly produces a plausible-looking wrong answer. It also means the repair reads a *declared*
relationship rather than inferring one from a naming convention that nothing enforces.

⚠ **The case normalisation is still required** — the registry's `speciesId` is lower-case
(`abyssswordstar`) and the catalog's is PascalCase (`AbyssSwordStar`). The registry removes the
*parsing* risk, not the *casing* one.

⚠ **And one ordering constraint:** 84 of that registry's 904 rows carry retired rarity ids, being
fixed by `ladder-consistency-repair`. That module **regenerates the file**. This module reads
`speciesId`, which that fix does not touch — but the two must not regenerate the same tree
concurrently. **Sequence them, or read the catalog directly and use the registry only as a
cross-check.**

**Recommendation: use the registry as the primary join and the suffix parse as a cross-check**, with
a disagreement between the two treated as a refusal. Both are cheap; agreeing is the evidence.

⚠ **A correction to the ideal, stated rather than absorbed:** it carried *"844 of 884 distinct
themeKeys resolve today, so the repair must refuse and report the remainder."* The 884/844 split is
real but describes prefixes, not failures — **844 of 844 `creature.*` keys resolve.** The
refuse-and-report machinery is still required (see Boundaries), because a *future* key may not
resolve; it just has no backlog to work through today.

---

## Tech stack

Python 3 (seedsmith `items` adapter, module 13), C# .NET 8 (the importer/reader), pytest + xUnit.
No new dependency.

## Commands

```powershell
cd gk-forge/tools/seedsmith
python -m seedsmith check gk-data/packs/fusion/data/seed/items --adapter items
python -m seedsmith items repair-species            # add --write --allow-production-tree to apply
python -m seedsmith items repair-set-class          # add --write --allow-production-tree to apply
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_items_adapter.py -q
$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_set_topology.py -q
dotnet run --project gk-forge/tools/ItemSeedValidator
dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~ItemSet"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Set"
```

⚠ `test_items_adapter` **fails pre-existing on a clean HEAD** (`AGENTS.md`). Confirm it already fails
before blaming this change.

## Project structure

| Path | Role |
|---|---|
| `gk-forge/tools/seedsmith/seedsmith/adapters/items/setgen/**` | Forward: emit the fields |
| `gk-forge/tools/seedsmith/seedsmith/adapters/items/setgen/topology.py` | The set-planning parser, resolver and validator — the ONE place a class is resolved |
| `gk-forge/tools/seedsmith/seedsmith/adapters/items/setgen/topology_repair.py` | The deterministic backward re-plan over the shipped corpus |
| `gk-core/data/tuning/set-topology.v1.json` | The three class templates (member-role counts, tier ceilings, threshold templates) |
| `gk-forge/tools/seedsmith/seedsmith/adapters/items/**` (a new repair pass) | Backward: extract from `themeKey` |
| `gk-data/packs/fusion/data/seed/items/sets/**` | **Generated output** — regenerated, never hand-edited |
| `gk-core/src/FusionRpg.Data/**` set import | Reads and persists the new field |
| `gk-forge/tools/ItemSeedValidator/Program.cs` | Closure gate on the new field |

## Code style

The join is explicit about its normalisation and about absence:

```python
def species_for_theme(theme_key: str, catalog: "dict[str, str]") -> "str | None":
    """themeKey -> speciesId, or None for a theme with no species.

    ⚠ CASE-NORMALISING BY NECESSITY, not by convenience: themeKey ships lower-case
    ('creature.abyssswordstar') and speciesId ships PascalCase ('AbyssSwordStar'). An exact
    match resolves 0 of 844 and looks like a content gap instead of a join bug.

    Returns None ONLY for a non-creature theme (build.*/theme.*, 40 distinct today), which is an
    explicit ABSENT value. A creature.* key that fails to resolve is an ERROR, not a None —
    the caller must refuse and report it, never write absent."""
    prefix, _, rest = theme_key.partition(".")
    if prefix != "creature":
        return None
    return catalog.get(rest.lower())      # catalog keyed by speciesId.lower()
```

⭐ The distinction in that docstring is the whole correctness argument: **"no species" and "species not
found" must never collapse into the same value.** One is a fact about a build-themed set; the other is
a defect.

---

## The set-planning system — ruled 2026-09-21 (owner)

`setClass` is not a label invented beside the data. It is a set's **declared topology class**, resolved
by deterministic code from the set's own declared topology, out of class templates that live in
versioned tuning. The design is already locked: [`item/ssot-sets.md`](../item/ssot-sets.md) §3.4 and
`decisions.md:141` — three classes, four-member default retired, six-role cap retired.

### The three classes, as data

| Class | Member-role policy | Bonus-tier ceiling | Threshold template |
|---|---|---|---|
| `unique-species` | **10 or 15** distinct roles — a closed parameterization, not a floor | exactly **2** | `identity-then-full`: thresholds `2` and the template's final member-role count |
| `family` | **≥ 5** distinct roles | 3 | `ascending` |
| `general` | **≥ 2** distinct roles | 4 | `ascending` |

**No number in that table lives in code.** Each row is data in `gk-core/data/tuning/set-topology.v1.json`
(§ Tunables), parsed by `setgen/topology.py`. The universal *"every set has a threshold at 2"* rule is
**read from `set-charm-gen.v1.json`'s `setShape.mandatoryThresholdPieces`**, never copied —
`set-charm-gen` owns that concept (`tunables-ssot.md` §2: a number two domains need belongs to
whichever owns it).

### The resolution ladder — the class is *decided*, never guessed

The classes are a **ladder**, tried most-restrictive-first in the order the tuning file declares
(`resolutionOrder`). A set takes the first class that admits its declared topology:

```text
resolve_class(entry):         # input: the entry's distinct member ROLES and its threshold list
  check universal threshold rules first  -> refuse if broken (see below)
  for class in tuning.resolutionOrder:
      if class.memberRoleSet and distinct_roles not in class.memberRoleSet:  next class
      if distinct_roles < class.memberRoleMin:                              next class
      if len(thresholds)  > class.bonusTierCeiling:                         next class
      return class.id
  raise SetTopologyError      # NO class admits this shape -> refuse, naming the entry
```

Two definitions are load-bearing, and both come from the design rather than from the file layout:

- **`memberRoleCount` counts DISTINCT ROLES, never raw JSON member rows.** A role may ship one member
  row per frame and still contributes one point to the counter ([`crafting-coverage-engine.md`](../../ideas/crafting-coverage-engine.md);
  `ssot-sets.md` §4.5's "counting is per role, not per item").
- **Threshold invariants are universal and checked before the ladder**: the first threshold is at
  `mandatoryThresholdPieces`, the list is strictly increasing, and the top threshold is ≤ the distinct
  role count (`ssot-sets.md` §3.4, `SetThresholdUnreachable`).

**The ladder has no default and no fallback.** A shape no class admits is a refusal naming the entry —
exactly as a `creature.*` `themeKey` that does not resolve is a refusal — never a silent `general`.

#### The refusal vocabulary (closed, in `setgen/topology.py`)

One code per authoring mistake, so a repair report says *which* rule broke rather than "unclassified".
Universal by nature (checked before the ladder, because a set that breaks one is not a set of some
class — it is a defect): `no-members`, `no-thresholds`, `first-threshold-not-mandatory`,
`thresholds-not-ascending`, `top-threshold-above-role-count`. Per class, in ladder order:
`member-roles-not-in-class-set`, `member-roles-below-class-minimum`, `tier-count-above-class-ceiling`,
`threshold-template-mismatch`. Terminal: `no-class-admits-this-shape`.

⚠ **`no-class-admits-this-shape` is unreachable through a role floor**, stated here rather than left as
a silent dead branch: `mandatoryThresholdPieces` is 2 and the top threshold may not exceed the distinct
role count, so every universally-legal set already carries at least two roles — `general`'s own floor.
It is reachable through the tier ceiling (a five-threshold set), and the test suite exercises that
path and names the other one as unreachable.

### The shipped corpus is re-planned onto the ladder — measured

Readings over the shipped tree (`gk-data/packs/fusion/data/seed/items/sets/**`, 910 entries in 885 files, measured this
revision):

| Prefix | Entries | Distinct-role shape | Resolved class |
|---|---:|---|---|
| `creature.*` | 844 | 4 roles, 2 tiers | `general` |
| `build.*` | 36 | 4 roles, 2 tiers | `general` |
| `theme.*` | 26 | 4 roles, 2 or 3 tiers | `general` |
| `theme.*` | 4 | **6 roles, 3 tiers** | `family` |
| *(none)* | **0** | 10 or 15 roles | `unique-species` |

**Tally: `general` 906 · `family` 4 · `unique-species` 0 · refused 0.** Two independent readings agree
that `unique-species` is empty and stays empty until a kit is authored:
`species-craft-ideal.md:125` records *"no 10- or 15-role set exists"*, and the ideal's raw
member-row counts (4 × 894, 6 × 2, 8 × 12, 12 × 2) describe the same 910 entries this table does — the
eight- and twelve-row sets carry four and six **distinct roles**, because a role ships one row per
frame.

⚠ **Those counts are a READING, printed by the repair report, never asserted.** A test asserts the
**closure property** instead: every shipped entry resolves to exactly one class, and every resolved
entry satisfies its own class template.

⛔ **One out-of-fence reader is now one row behind, and it is filed not hidden.**
`gk-core/data/tuning/set-topology.v1.json`, `setgen/topology.py` and `setgen/topology_repair.py` are all in this
lane's fence; the C# mirror of the `set` kind's field list
(`gk-forge/tools/ItemSeedValidator/Registries/KindCatalog.cs:110-112`, the hand-transcribed twin of
`setgen/kinds.py` that `item/entry-shapes.md` §11 says exists "precisely because nothing else does") is
**not**. With `setClass` on all 910 entries and that row unchanged, `ItemSeedValidator` reports **910
new `UnknownKey` errors** (`41 -> 951`), each reading *"unknown key 'setClass' on kind 'set'"*. The
remedy is one field in one array — `extra: new[] { ..., "speciesId", "setClass" }` — and the Python
schema `seedsmith check` already accepts the field unharmed (**63 gap, 580 note, 153 not_measured**,
zero mentioning `setClass`). Filed as a todo row for the owning program.

### What the class does *not* decide

- **Identity.** `family`'s `requiredFamilyId`, `unique-species`'s `requiredSpeciesId` /
  `requiresUniqueCreature` / `hybridEligibility` are **module 25's**
  ([`item/spec-set-requirement-reconciliation.md`](../item/spec-set-requirement-reconciliation.md),
  `item/ssot-requirements.md` §2.1). They are deliberately **not** duplicated into the topology file:
  a row nothing reads is a lie in a table (`ssot-sets.md` §4.2's SC7 rule). `setClass` is a topology
  declaration; the identity contract a planner later attaches to it is that module's build.
- **Species.** `setClass` is **orthogonal to `speciesId`** — see Open question 1 below, now answered.
- **Bonus magnitudes.** The class changes no atom, no threshold's value and no evaluated bonus
  (Success criterion 5).
- **Forward shape policy.** The retired four-member default and six-role cap are `set-charm-gen`'s
  *generator* inputs (`set-charm-gen.v1.json` `setShape.typicalMembers` / `grandMembers` /
  `maxRoles`). Re-planning what the generator **authors** is that module's own work; this revision
  only makes the class of what it authors declarable.

### ⚠ The one judgement call, and how to reverse it

No shipped entry declares an identity selector, so a *ladder without an identity gate* and a *ladder
gated on identity* disagree on exactly the four 6-role `theme.*` sets:

| Reading | 6-role `theme.*` sets | Shipped tally |
|---|---|---|
| **Shape alone (taken here)** — the classes' role bands and tier ceilings decide | `family` (≥5 roles, ≤3 tiers) | general 906 · family 4 |
| Identity-gated — a class requiring `requiredFamilyId` is skipped when the entry declares none | `general` | general 910 · family 0 |

**Shape alone is taken because it is the class design's own criterion.** `decisions.md:141` states
the class's member-role count and bonus-tier policy as the shape the planner resolves a template
*into*, and `species-craft-ideal.md`'s class table — *"Lowest member-role count: 2 / 5 / 10 or 15"* —
is a role-count ladder, which is the reading the owner's *"their role-count shapes"* names. Identity
selectors are a **separate axis** (module 25) layered on top, not the discriminator.

⚠ **Forward debt this creates, stated rather than hidden.** The four `family` sets carry a class whose
identity contract module 25 will require. Module 25's `SetRequirementCompletability` check 1
(*"family has exactly one known family"*) cannot pass for them until the planner declares one, and this
revision must not fabricate one (Boundaries: **Never**). That is a declared *topology* fact with an
unresolved *identity*, recorded here and as a row for module 25's program — not a silently satisfied
requirement.

The ladder is **data**, so reversing the judgement is a tuning publish of `resolutionOrder` plumbed
with an identity gate (`gk-core/tools/tuning/publish.py set-topology`), not a code change — which is the point
of authoring the classes as data rather than as a constant in the generator.

## Tunables

**The set-planning numbers live in `gk-core/data/tuning/set-topology.v1.json`**, owned by item module 13 and
published through `gk-core/tools/tuning/publish.py` — never hand-edited (T4), never in code (T1).

| Value | Meaning | Owner |
|---|---|---|
| `classes[].memberRoleMin` | The class's lowest distinct-role count — `general` 2, `family` 5, `unique-species` 10 | `gk-core/data/tuning/set-topology.v1.json` |
| `classes[].memberRoleSet` | `unique-species`'s closed parameterization (`[10, 15]`); absent on the other two, whose role count grows only through an approved set-progression template | idem |
| `classes[].bonusTierCeiling` | The most cumulative bonus thresholds the class may expose — 4 / 3 / 2 | idem |
| `classes[].thresholdTemplate` | `ascending`, or `identity-then-full` for `unique-species` (thresholds `2` and the final role count) | idem |
| `resolutionOrder` | The ladder order — most restrictive class first | idem |
| `setShape.mandatoryThresholdPieces` | The universal "every set has a threshold at 2" rule — **read, never copied**, into the topology file | module 13 (`set-charm-gen`); `set-charm-gen.v1.json` |

**Structural:** none introduced. `speciesId` and `setClass` are identity strings.

## Numeric types

**No magnitude is produced or consumed.** `speciesId` and `setClass` are identity strings. Stated
explicitly so the next module does not assume this one settled a numeric question: the *cost*
shaped by this species is `species-cost-shaping`'s, and it is a per-mille multiplier there.

## ActorHub gate

**N/A and checked.** A set's species binding produces no actor combat / derived / AppliedCombat
number. Set bonuses continue to compose exactly as today, through `SetEvaluator` and the existing
atom path into `ActorHub`. **No private fold is introduced and no bonus magnitude changes** — adding a
field to an entry must not move a single number, which is Success criterion 5.

## Testing strategy

| Level | What it asserts |
|---|---|
| Unit (python) | ⭐ **The case-normalising join resolves a lower-case `themeKey` to a PascalCase `speciesId`** — the test that would have caught the zero-resolution trap |
| Unit (python) | A `build.*` / `theme.*` key yields **explicit absent**, distinguishable from not-found |
| Unit (python) | A `creature.*` key that does not resolve **raises and reports** — it never writes absent |
| Unit (python) | The repair is **idempotent**: running it twice produces a byte-identical tree |
| Unit (python) | The repair is **deterministic** — no RNG, no model call, no ordering dependence |
| Contract | `seedsmith check gk-data/packs/fusion/data/seed/items --adapter items` passes after regeneration |
| Contract | `ItemSeedValidator` closes: every non-absent `speciesId` resolves in the species catalog |
| Unit (C#) | Set bonus evaluation is **unchanged** for every shipped set — both fields are inert to `SetEvaluator` |
| Unit (python) | ⭐ **The ladder picks the most restrictive class that admits the shape** — a 6-role/3-tier entry resolves `family`, a 6-role/4-tier entry resolves `general`, a 10-role/`[2,10]` entry resolves `unique-species` |
| Unit (python) | A shape no class admits (5 tiers, or a first threshold not at 2, or a top threshold above the distinct role count) **refuses naming the entry** — never a silent `general` |
| Unit (python) | `memberRoleCount` counts **distinct roles**, not member rows: an 8-row/2-frame set is a 4-role set and must not resolve `family` |
| Unit (python) | `unique-species` is reachable **only** on its closed parameterization — a 10-role kit with 3 thresholds is not it |
| Unit (python) | The tuning loader **refuses a missing key rather than defaulting**, and refuses a class that is not in the ladder or a parameterized class whose ceiling disagrees with its own values |
| Unit (python) | The mandatory first threshold is **read from `set-charm-gen.v1.json`**, proved both ways: the default matches its owner and an explicit override is honoured |
| Contract (python) | Every shipped entry resolves to exactly one class, and its declared shape satisfies that class's template |
| Report | Print per-class resolved/refused counts — **readings, printed, never asserted** |

⛔ **No test asserts "844 sets carry a species."** That is a reading and it grows when content ships.
Assert the **closure property**: every `creature.*` key resolves, or the run fails naming the key.

## Boundaries

**Always**
- **Fix the generator and regenerate.** `gk-data/packs/fusion/data/seed/items/**` is seedsmith output — ~1011 of 1041 files
  carry `_meta.model`. This is the repo's most-repeated incident, twice attempted in one week.
- Keep "no species" and "species not found" as **different** outcomes.
- **Resolve a class through `gk-core/data/tuning/set-topology.v1.json` and `setgen/topology.py`** — one
  resolver, called by both the emitter and the repair pass, so the two paths can never disagree.
- Run `seedsmith check` and `ItemSeedValidator` before committing.
- Commit the generator change and the regenerated corpus as **separate logical commits**, via
  `git commit` with explicit `paths`.

**Ask first**
- Changing `themeKey`'s meaning. It stays the **presentation** key; this module adds fields beside
  it, it does not repurpose it.
- Changing the class ladder itself (the bands, the ceilings, the order) — that is a set-planning
  tuning revision with its own review, not a data correction.

⛔ *Answered 2026-09-21: the `setClass` vocabulary is no longer ask-first — the owner ruled the three
classes of `decisions.md:141` are the target and are built (§ The set-planning system).*

**Never**
- ⛔ **Let a model author `speciesId` or `setClass`.** One is a join, the other is a resolution over
  declared topology. `audit_schema` exists to keep model output out of fields a system keys on.
- ⛔ **Invent a fourth class** (a `legacy`/`unclassified` bucket) for shipped content the ladder does
  not admit. The owner's 2026-09-21 ruling rejected exactly that: a shape no class admits is a
  refusal to report, not a bucket to hide it in.
- ⛔ **Hand-edit a set JSON** to fix a resolution failure. The next generation run reverts it, the run
  ledger stops describing the file, and the change is invisible to every other consumer.
- Write `absent` for a `creature.*` key that failed to resolve, or a class for an entry no class
  admits. Either converts a defect into content.
- Fabricate a `requiredFamilyId` to satisfy a `family` class in the shipped corpus.
- Touch set bonus magnitudes. `ssot-sets.md` owns them, and D3's documented set-dominance spiral is
  the reason not to adjust them opportunistically.
- Let a craft verb break or re-check a set bonus — the bonus counts **membership**, not upgrade state.

## Success criteria

1. Every set entry carries `speciesId` (a real id or an explicit absent) and `setClass`.
2. `set-charm-gen` emits both fields for newly generated sets.
3. The deterministic repair fills every existing entry, with **no model call anywhere on the path**.
4. Every `creature.*` themeKey resolves, or the run fails naming the unresolved key.
5. ⭐ **No set bonus magnitude changes** — proven by a diff of evaluated bonuses before and after.
6. The repair is idempotent and deterministic, proven by a second run producing a byte-identical tree.
7. `seedsmith check --adapter items` and `ItemSeedValidator` green.
8. The corpus diff is a pure regeneration — verified by re-running the generator.
9. ⭐ **Every shipped entry resolves to exactly one topology class through `gk-core/data/tuning/set-topology.v1.json`,
   or the run refuses naming the entry** — never a silent default and never a fourth class.
10. The class ladder is **data**: changing a band, a ceiling or the resolution order is a tuning
    publish, and no threshold or role count appears in code.
11. `set-charm-gen` emits `setClass` forward for newly generated sets through the **same** resolver the
    repair pass uses.

## Open questions

1. ✅ **ANSWERED 2026-09-21 — do the 36 `build.*` and 30 `theme.*` sets get a `setClass` too?** **Yes,
   from the class design rather than from convenience.** The design's criterion is the set's *topology*
   — distinct member roles and the threshold list — and `setClass` is explicitly orthogonal to
   species, so a speciesless set is classified by its shape like any other. Measured: the 36 `build.*`
   sets resolve `general` (4 roles); the 30 `theme.*` sets resolve 26 `general` (4 roles) and 4
   `family` (6 roles). The two classes that *do* carry an identity requirement (`family`'s declared
   family, `unique-species`'s declared creature) stay empty until content declaring that identity
   exists — which `species-craft-ideal.md:125`'s own reading of the corpus already predicted.
2a. ⭐ **Which `speciesId` SPELLING is persisted?** — **decided here, because getting it wrong
   reproduces the casing bug one hop downstream.** The repo carries both: `gk-data/packs/fusion/data/generated/creatures/*.json`
   is **PascalCase** (`AbyssSwordStar`), while `CreatureSpeciesCatalog.Generated.cs`,
   `gk-data/packs/fusion/data/seed/creatures/species/**` and the themes registry are **lower-case** (`abyssswordstar`).
   `species-cost-shaping` looks up `BaseRarity` by this id against the **runtime catalog**, and
   `species-materials` keys material ids on it. **Persist the runtime catalog's spelling (lower-case),
   and assert in `ItemSeedValidator` that every non-absent `speciesId` resolves in
   `CreatureSpeciesCatalog`** — which is success criterion 7's closure check with the spelling pinned.

2. **Is `speciesId` nullable, or is there a sentinel?** **Recommendation: nullable/absent, never a
   sentinel string.** A sentinel would be indistinguishable from a species named after it, and
   `tunables-ssot.md` T5's posture — an expected-but-missing value is a rejection, never a silent
   default — is the precedent this repo already follows.
3. **Does the case-normalising join get pushed upstream** — i.e. should `themeKey` and `speciesId`
   share a casing convention? Recommendation: **no, not in this module.** Renormalising ids across two
   shipped corpora is a migration; a documented, tested join is the honest fix here. Worth filing as
   its own cleanup.

⭐ **AUDIT 2026-09-21 (lane sgc-1): `setClass` has no RUNTIME reader — and the designs say that is the current,
intended state rather than a gap.** Measured: `grep -rn "setClass" --include=*.cs src/` and the same over
`gk-web/web/fusion-rpg-web/src` return zero hits; the readers are the planner (`setgen/topology.py:376`, the authoring
consumer this spec designates) and the validator's registry mirror. The runtime consumer is module 25's *planned*
contract — `spec-set-requirement-reconciliation.md:27-33` declares `SetIdentityRequirement { setId, setClass, … }`
— and that module is specced-but-unbuilt. So the parent's "a row nothing reads is a lie in a table" rule is
satisfied on the authoring side, and the tracking row for the runtime half is **T58** in
`tasks/species-gear-chain-todo.md`. (This note began as a defect report and was corrected after checking the
designs; the contrast with `speciesId`, which `Items/Thresholds/SetCorpus.cs` does read at runtime, is a
difference of build order, not of discipline.)
