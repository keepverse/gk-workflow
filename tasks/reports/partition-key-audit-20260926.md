# Partition-key audit — the species-scoped item-set partition (2026-09-26)

**Owner instruction, verbatim:** *"audit what is correct, validator or corpus, fix wrong side instead of
choice, check the idea first."*

**Question.** Two components disagreed on the partition KEY for a species-scoped `set`:

| side | key | file:line |
|---|---|---|
| allocation | `sets/species/<raw speciesId>` (underscores kept) | `gk-forge/tools/ItemSeedValidator/Registries/NamespaceAllocation.cs:261` (pre-fix) |
| corpus | `sets/<hyphenated slug>`, from the set's own id | `gk-forge/tools/seedsmith/seedsmith/adapters/items/setgen/authored.py:99-103` |

**Result.** The evidence settles it, and the side that is wrong is **the allocation, not the corpus** —
and the `species/` path segment, not the spelling, is the whole of the defect. Fixed on the allocation
side only. `Coverage/EmptyPartition` **911 → 67** gaps; the validator's warnings **2589 → 2524**; every
other metric's finding count **+0**. No `data/**` row was touched.

Session: `tasks/sessions/partition-key-audit-20260926.json`. This lane does not merge; the manager
reviews.

---

## 0. Baseline reproduced first (mandatory)

The brief's stated baseline, reproduced before any edit, on this head:

```
$ PYTHONPATH=gk-forge/tools/seedsmith python -m seedsmith check gk-data/packs/fusion/data/seed/items --adapter items
931 gap, 612 note, 153 not_measured
```

**Exact match with the brief's `931 / 612 / 153`.** Full per-metric decomposition of that baseline
(`--json`):

| metric | severity | count |
|---|---|---:|
| `Coverage/EmptyPartition` | gap | **911** |
| `Coverage/PairwiseHole` | gap | 6 |
| `Quality/FlavourMissing` | gap | 5 |
| `Content/FieldMissing` | gap | 5 |
| `SemanticDedup/NearDuplicate` | gap | 4 |
| `SemanticDedup/NearDuplicate` | note | 554 |
| `Coverage/HostRoleDiversity` | note | 23 |
| `Distribution/CellDeviation` | note | 16 |
| `Quality/FlavourGeneric` | note | 12 |
| `Registration/Unobtainable` | note | 4 |
| `Distribution/CellOccupancy` | note | 2 |
| `Registration/MaterialNeverSpent` | note | 1 |
| (`Balance/OutOfEnvelope` + 22 others) | not_measured | 153 |

> ⚠ **The brief's `747 SemanticDedup/NearDuplicate` does not reproduce at this head. Measured: 558**
> (554 note + 4 gap). The 747 in `tasks/backlog-clean-up-todo.md`'s BCU2.11 reading is a stale-base
> figure from the reverted `ea2aeb756` run, not this tree. I quote 558 everywhere below because I
> reproduced it. A number I did not reproduce is not a result.

---

## 1. Is a species-scoped set partition one-per-species, or a namespace holding many sets?

**Answer: a NAMESPACE holding many sets. It is not one-per-species.** This is the question the
owning program's residue map flagged as unresolved, and it is resolvable.

| evidence | file:line |
|---|---|
| Each species gets a `SequenceShape.ThreeDigit` allocation, so the partition admits `set.<slug>-001 … -899` — many sets per species by construction | `NamespaceAllocation.cs:289`, `SequenceShape` enum `:7-28` |
| **`"900-999 is reserved in every partition for later use"`** — a partition is *expected* to take more entries | `setgen/emit.py:70-72` |
| `_merged_partition_rows` appends newly minted rows to an already-committed partition file, preserving what is there | `setgen/authored.py:106-130` |
| One file per partition, all of that partition's rows in it | `setgen/authored.py:340-349` |
| "the id sequence **continues, it does not restart**"; a rerun replaces only files owned by that batch | `docs/architecture/item/seed-contract.md:216`, `:224-226` |
| A partition receives *disjoint reserved vocabulary* — "a name-word **pool** nobody else holds" | `docs/architecture/item/authoring-fleet-plan.md:21-23` |
| The shape is already exercised: **6** shipped `sets/*.json` files carry >1 entry | measured over `gk-data/packs/fusion/data/seed/items/sets/**` |

**Consequence, and it kills a premise in the ledger.** BCU2.11's residue map hands `item-seedgen` the
question *"whether a species-scoped set is intended at all — if it is, the generator owes 904
**distinct** sets"*. The design says **no**: the generator owes 904 *partitions*, 844 of which already
hold one set each and may take more. The 60 unoccupied species are a real but different backlog (see §6).

## 2. Is the species identity the raw id, or the slug?

**Answer: the RAW, underscored id is the canonical species identity. The hyphenated form is a
representation projected at the item boundary, not an identity.**

The authority is explicit, and it is the corpus's own code — not the allocation:

> *"The creature dump still contains a small legacy variant slice whose `typeName` uses underscores
> (for example `BlackFootball_a`). **Those names remain the authoritative `speciesId` in the theme
> registry**, but `definitions.md` permits only kebab-case in a container id. **Normalise that
> representation at the item boundary instead of rewriting creature identifiers** or silently minting
> an invalid id."*
> — `gk-forge/tools/seedsmith/seedsmith/adapters/items/setgen/emit.py:41-54` (fold at `:50`)

Corroborating, all measured by me:

| evidence | reading |
|---|---|
| `gk-data/packs/fusion/data/seed/creatures/_registry/themes.v2.json` — 904 rows; `speciesId` with `_`: **73**, with `-`: **0** | the registry's spelling is underscored |
| The 844 shipped `creature.*` set entries' own `speciesId` field — with `_`: **65**, with `-`: **0** | the corpus agrees with the registry |
| `set.elephantzombie-a-001` carries `"speciesId": "elephantzombie_a"`, `"themeKey": "creature.elephantzombie_a"` | id kebab, identity underscored — both spellings ship, deliberately |
| `CreatureSpeciesCatalog.cs:136-137` throws unless `SpeciesId == SpeciesId.Trim().ToLowerInvariant()`, with the message *"must be non-empty lower-kebab"* | the runtime guard is **lower-case only**; the message over-promises (filed as a finding, §7) |
| `spec-set-species-binding.md` Open question 2a, **answered**: *"Persist the runtime catalog's spelling (lower-case), and assert in `ItemSeedValidator` that every non-absent `speciesId` resolves in `CreatureSpeciesCatalog`"* | the *field* keeps the registry spelling |

**So the underscored identity is authoritative — and the allocation was already right about it.** The
allocation's `idSlug` is used only for the *minted id prefix*, which `IdGrammar` forces to kebab. The
dispute was never about the identity.

## 3. Is a hyphen/underscore fold a sanctioned equivalence anywhere?

**Answer: it is a sanctioned *representation* fold at exactly two authoring boundaries, and it is NOT
an identity equivalence. There is no fold in `src/**` at all.**

| site | what it does |
|---|---|
| `setgen/emit.py:50` | `species_id.strip().lower().replace("_", "-")` — the container-id boundary |
| `NamespaceAllocation.cs:260` (pre-fix) / `:288` (post-fix) | the same fold, for the same reason (id grammar) |
| `consumablegen/schema.py:101`, `RegistrySet.cs:453`, `NamespaceAllocation.cs:207` | unrelated affix/consumable stems |
| **`src/**`** | **no occurrence** — grep over all C# for `Replace('_','-')` returns zero |

**And the allocation already treats both spellings as the same partition, on purpose.** Its `Add(...)`
call passes *both* `speciesId` and `idSlug` as the allocation's `Tokens`
(`NamespaceAllocation.cs:289`), and `CheckPartitionCohesion` compares a label against that token set
(`IdentityCheck.cs:234-239`) precisely so the two spellings are interchangeable *for label-checking*.

**This is why the validator emitted exactly 65 `PartitionMetaMismatch` warnings and not 844** — and the
65 is itself the diagnosis, reproduced by me:

- 844 species sets carry a `_meta.partition` of `sets/<slug>` while the allocation said `sets/species/<raw>`.
- For the **779 non-variant** species, `IdentityCheck.cs:237` compares the *token set*, and `sets` +
  the species name are both tokens of `sets/species/<id>`, so the disagreement is **silently tolerated**.
- For the **65 underscored variants**, the label splits on `-` into `elephantzombie` + `a`, neither of
  which is a token of `sets/species/elephantzombie_a` — so the lint **fires**.

> ⭐ **The validator was already complaining about the spelling, on 65 of 844 rows, and nobody read it
> as a partition-KEY disagreement.** It was classified as cosmetic. It was the same defect.

## 4. Which side is derived from the other?

**Answer: the corpus's partition label is derived; the allocation's key is read from the authority.
The allocation is authoritative by construction.**

```
gk-data/packs/fusion/data/seed/creatures/_registry/themes.v2.json   ← the species roster (the authority)
        │
        ├─► RegistrySet.CreatureSpeciesIds      RegistrySet.cs:559-577  (reads it live, by design)
        │       └─► ExpandSpeciesThemes         NamespaceAllocation.cs:284-292  → partition + prefix
        │               └─► --list-partitions-json → Program.cs:109-112
        │                       └─► refresh_allocated_partitions.py --write  → the snapshot
        │                               └─► registries.py:85  → Coverage/EmptyPartition's `allocated`
        │
        └─► species_repair / setgen             join → the `speciesId` + `themeKey` a set entry carries
                └─► emit.py:41-54  set_id()     folds to kebab for the container id ONLY
                        └─► authored.py:99-103  _partition_of()  id body − sequence  →  `sets/<slug>`
                                └─► write_seed_file(out_dir, f"{partition}.json")   authored.py:346
```

The allocation **reads the roster**. The corpus's label is **computed from an id** — a projection of a
projection. `authored.py:100-101` says so itself: *"The partition is the id's own body minus the
sequence, which is what `naming.v1.json`'s `idTemplate` already says it is."*

---

## 5. Which side is wrong — and why that one

**The allocation. Specifically its `species/` path segment, which the registry never declares.**

### 5.1 The registry declares ONE partition key for `sets`, with ONE component

`gk-data/packs/fusion/data/seed/items/_registry/naming.v1.json`, `idNamespaces.sets`:

```
:365  "partitionCount": 41,
:367  "partitionKey": "themeId",
:368  "idTemplate": "set.{themeId}-{seq:03}",
```

Measured across **every** kind in that registry — does the declared key's component count predict the
path depth the allocation actually emits?

| namespaceKey | declared `partitionKey` | arity | actual depths |
|---|---|---:|---|
| `baseTypes` | `(roleId, frame, band)` | 3 | 1, 3 |
| `uniques` | `(themeId, rungBandLowOrdinal)` | 2 | 2 |
| `affixFamilies` | affix group id | 1 | 1 |
| `charms` | `axisGroupId` | 1 | 1 |
| `consumables` | `slot` | 1 | 1 |
| `displayTemplates` | `slot` | 1 | 1 |
| `dropTables` | `slot` | 1 | 1 |
| `relics` | `slug` | 1 | 1 |
| **`sets`** | **`themeId`** | **1** | **1, 2** ← the only kind with two depths |

`sets` was the **only** kind allocating two path depths for one declared key, and the extra depth was
the `species/` segment. `baseTypes`' depth-1 rows are a documented, deliberate exception (commander
roles are single-band by design, `NamespaceAllocation.cs:165-184`).

### 5.2 The registry's own note contradicts the code

`naming.v1.json:395` (`speciesThemesNote`) claims the species population uses the **"Same
`idTemplate`/`SequenceShape.ThreeDigit` mechanism as the other two populations."** It says nothing about
a second partition shape. The code used the same *id template* and a *different* partition shape. Note
and code disagree, and per the design gate, code is not evidence about intent — but here the **note is
the specification and the code is the deviation.**

### 5.3 The segment had no reader, no test, and no document

`grep -rn "sets/species"` over the whole repo returned exactly **two** locations: the line that
produced it, and the 904 rows of the derived snapshot it wrote. No test asserted it. No spec named it.
The only consumer that ever compared it to anything was `Coverage/EmptyPartition` — the metric it broke.

### 5.4 Why not fix the corpus instead — the honest counter-argument

The strongest evidence the *other* way is a real precedent, stated twice on 2026-09-07:

> *"a bare partition id is exactly the bug found (and fixed) the same day in
> `base-types/footing/plant/{a,b}.json`, where a missing directory prefix made real content invisible to
> `Corpus.partitions`' occupancy lookup"* — `setgen/combogen/authored.py:146-151`
>
> *"their `_meta.partition` was stamped missing the `base-types/` prefix every sibling uses, so the
> metric's `corpus.partitions` lookup could never match. **Fixed at the source, not here.**"* —
> `gk-forge/tools/seedsmith/tests/test_items_adapter.py:184-187`

That precedent says: *the label must equal the allocation; fix the label at the generator.* I did not
follow it, for three measured reasons:

1. **It fixed a label that was LESS specific than the allocation** (a missing directory prefix). Here
   the label is *differently specific*, and the extra specificity is the one with no declared
   authority. Following the precedent's direction would mean re-stamping **844 `_meta.partition`
   values and moving 844 files into a new `sets/species/` subdirectory** — a `data/**` change, outside
   this lane's fence, and a structural change to the corpus tree.
2. **The convention the precedent defends is already at 84%.** Measured over all 1005 distinct
   `_meta.partition` labels in the corpus: **158** match an allocated `PartitionId` exactly, 847 do not,
   and **844 of the 847 are these**. So "the label must equal the allocation" is not a convention the
   corpus reliably keeps — it is an accident of the allocation being right 161 times out of 165.
3. **The `species/` scope carries no uniqueness.** Measured: 904 species slugs are 904 distinct values
   with **0** collisions against the 41 declared `themeIds`/`buildThemeIds`. The scope segment bought
   nothing but a divergence.

What the fix **does** cost, stated rather than hidden: a reviewer reading `sets/elephantzombie-a` no
longer sees "this is a species-scoped partition" in the path. The correct vehicle for that signal
already exists and is already populated — the `speciesId` field, on all 844 entries
(`spec-set-species-binding.md` Success criterion 1), which is queryable, where a path segment is not.

### 5.5 The fix — one line, on the allocation side only

`gk-forge/tools/ItemSeedValidator/Registries/NamespaceAllocation.cs:289`, pre-fix `:261`:

```csharp
// before
Add(kind, $"{kind.Directory}/species/{speciesId}", $"set.{idSlug}-",
    SequenceShape.ThreeDigit, speciesId, idSlug);
// after
Add(kind, $"{kind.Directory}/{idSlug}", $"set.{idSlug}-",
    SequenceShape.ThreeDigit, speciesId, idSlug);
```

Deliberately **unchanged**: the id prefix `set.<idSlug>-` (so no id moves, no `IdOutsideNamespace`
risk, no re-authoring), both spellings in `Tokens` (so label-checking stays spelling-tolerant), and the
live read of the species roster. The underscored identity is not discarded — it stays on the
`speciesId`/`themeKey` fields, which is where the design puts it.

The derived snapshot was regenerated through the sanctioned tool, not hand-edited:

```
$ python gk-forge/tools/seedsmith/refresh_allocated_partitions.py --check     # exit 1, names 904 removed / 904 added
$ python gk-forge/tools/seedsmith/refresh_allocated_partitions.py --write     # wrote 1069 partitions
$ python gk-forge/tools/seedsmith/refresh_allocated_partitions.py --check     # exit 0 — idempotent
```

1069 partitions before and after; the diff is a **pure rename of 904 keys** (`git diff --stat`: 904
insertions, 904 deletions, 0 additions, 0 removals).

---

## 6. What the metric actually measures, and whether that is the right thing

**It measures the right thing; it was fed a wrong key.** No metric change was needed or made, and none
of the new tests pins a count.

`Coverage/EmptyPartition` (`gk-forge/tools/seedsmith/seedsmith/metrics/coverage.py:31-46`) is a set difference:
`allocated` (the adapter's `partitions` vocabulary, read from the allocation snapshot at
`registries.py:85`) minus `occupied` (`ctx.corpus.partitions`, i.e. the `_meta.partition` labels,
`corpus/model.py:104`, `:122-124`). The metric's own docstring states the asymmetry it depends on
(`coverage.py:8-11`): *"Allocated is adapter knowledge, not corpus knowledge (corpus only ever sees
partitions that already hold something)."* With one key space, that is sound. With two, every
allocation reads as empty.

**The residue, decomposed by me from the post-fix run — 67, and every one of them real:**

| group | n | real? |
|---|---:|---|
| `sets/<slug>` for a species with **no** set entry | **60** | ✅ genuine gap |
| `sets/might-offense` | 1 | ✅ genuine — `build.might-offense` is allocated, and the corpus has `build.might-balance` and `build.might-defense` sets but no `-offense` |
| `attributes` | 1 | ✅ the documented deferred kind (`KindCatalog.cs` `ShapeDefined: false`) |
| `base-types/manipulator/humanoid/b`, `base-types/mantle/humanoid/a` | 2 | ✅ genuinely empty |
| `display-templates/4`, `/5`, `/6` | 3 | ✅ genuinely empty |

**The 844 that disappeared were false readings, and I can name every one of them.** The corpus's own
`speciesId` field joins **844 / 844** of them onto the allocation's species ids, with **0** corpus-only
entries — a set partition that holds a set is not empty, whatever the label says.

### Two things this audit found about the metric's own test

Both are findings, not fixes — the test is outside what this change should touch.

1. ⭐ **`test_items_adapter.py:203` is circular.** It asserts
   `assertNotIn(finding.subject, occupied)` where `occupied = self.corpus.partitions` — the *same*
   label set the metric differenced against. It therefore cannot detect a label/identity mismatch, and
   the 844 false gaps passed through it. Its stated intent (*"every reported subject is an allocated
   partition that **genuinely** holds no entries"*, `:190-191`) is not what it checks. My
   `test_every_shipped_set_entry_partitions_into_an_allocated_partition` closes that hole from the
   other side: it derives the partition from each entry's own id and requires it to be allocated.
2. ⚠ **`SemanticDedup/NearDuplicate`'s `subject` is not deterministic.** `_named_entries` iterates
   `for kind in corpus.kinds` (`metrics/dedup.py:85`), a `frozenset`, so the order of a pair's two sides
   inside the subject string follows per-process `PYTHONHASHSEED` randomization. Measured: **3 runs of
   the same tree produced 2 different orderings** (runs 1 and 3 agreed, run 2 differed), with the count
   stable at 4 gap / 554 note each time. This is pre-existing and unrelated to the partition key — but
   it is why a naive before/after diff of this metric shows 20 "changed" notes. Normalized
   order-insensitively, the pair set is **byte-identical: 558 pairs, 0 gained, 0 lost.**

---

## 7. Before / after — every number reproduced by me

### 7.1 The metric

```
$ PYTHONPATH=gk-forge/tools/seedsmith python -m seedsmith check gk-data/packs/fusion/data/seed/items --adapter items
before:  931 gap, 612 note, 153 not_measured
after:    87 gap, 612 note, 153 not_measured
```

Per-metric delta, every row except the one:

| metric | severity | before | after | delta |
|---|---|---:|---:|---:|
| `Coverage/EmptyPartition` | gap | 911 | **67** | **−844** |
| `Coverage/PairwiseHole` | gap | 6 | 6 | +0 |
| `Quality/FlavourMissing` | gap | 5 | 5 | +0 |
| `Content/FieldMissing` | gap | 5 | 5 | +0 |
| `SemanticDedup/NearDuplicate` | gap | 4 | 4 | +0 |
| `SemanticDedup/NearDuplicate` | note | 554 | 554 | +0 (order-insensitive) |
| `Coverage/HostRoleDiversity` | note | 23 | 23 | +0 |
| `Distribution/CellDeviation` | note | 16 | 16 | +0 |
| `Quality/FlavourGeneric` | note | 12 | 12 | +0 |
| `Registration/Unobtainable` | note | 4 | 4 | +0 |
| `Distribution/CellOccupancy` | note | 2 | 2 | +0 |
| `Registration/MaterialNeverSpent` | note | 1 | 1 | +0 |
| all `not_measured` | | 153 | 153 | +0 |

**Gap subjects: 931 → 87.** 904 subjects left, 60 appeared. That is a *relabelling*, not a loss: the
60 that appeared are the same 60 genuinely-unoccupied species partitions, now under the key the corpus
and the allocation agree on. 904 − 844 = 60.

**Notes: 612 → 612, and the `SemanticDedup/NearDuplicate` pair set is identical** (558, 0 gained,
0 lost) — verified by normalizing each subject's two sides before comparing.

### 7.2 The validator

```
$ dotnet run --project gk-forge/tools/ItemSeedValidator -- gk-data/packs/fusion/data/seed/items
before:  PASS — 3962 entries across 1013 files, 2589 warnings
after:   PASS — 3962 entries across 1013 files, 2524 warnings
```

−65 warnings, and the 65 are **exactly** the `PartitionMetaMismatch` count, one per underscored variant
species. No new code. The `PartitionMetaMismatch` class is now **0** across the whole corpus.

### 7.3 Tests — including the falsifiability check

| suite | before | after |
|---|---:|---:|
| `gk-forge/tests/FusionRpg.ItemSeedValidator.Tests` | 100 passed | **105 passed** |
| `gk-forge/tools/seedsmith/tests/test_items_adapter.py` | 18 passed | **21 passed** |
| `verify-change.py` scoped boundary (itemseedvalidator + seedsmith-items + seedsmith-tests + `test-substrate` guard + `gen-items-gate`) | — | **exit 0** |

**The new tests were checked against the pre-fix code, not just the post-fix code.** This is the part
that makes them evidence rather than decoration:

| test | pre-fix | post-fix |
|---|---|---|
| `SetSpeciesPartitionKeyTests.A_species_set_partition_is_named_by_the_id_template_slot` | **FAIL** — expected `sets/abyssswordstar`, actual `sets/species/abyssswordstar` | pass |
| `…No_species_partition_nests_under_a_scope_segment` | **FAIL** — collection not empty | pass |
| `…An_underscored_variant_species_partitions_on_the_kebab_id_slot` | **FAIL** — expected `sets/elephantzombie-a`, actual `sets/species/elephantzombie_a` | pass |
| `…A_species_set_labelled_the_way_setgen_labels_it_raises_no_PartitionMetaMismatch` | **FAIL** — `PartitionMetaMismatch` present | pass |
| `PartitionKeyShapeTests.test_no_allocation_nests_deeper_than_its_declared_partition_key` | **FAIL** — *"`sets` (partitionKey `'themeId'` = 1 component) allocates a 2-segment partition"* | pass |
| `…test_every_shipped_set_entry_partitions_into_an_allocated_partition` | **FAIL** — 844 orphan partitions named | pass |
| `…test_the_species_partition_key_is_the_id_template_slot_not_the_species_id` | **FAIL** — `'sets/blackfootball-a' not found in {...}` | pass |

**None of them pins a population count.** They assert a shape against `naming.v1.json` (a closed
vocabulary the repo owns), a closure property over the corpus, and a label-agreement lint — so a species
shipping tomorrow changes no assertion. That is `validation-ssot.md`'s rule applied rather than
relaxed.

### 7.4 What I did NOT do, deliberately

- **No `data/**` edit.** The corpus is generated; nothing under `gk-data/packs/fusion/data/seed/**` was touched, so no
  regeneration is owed and the sanctioned `successor_edges --dry-run` → `--write` shape was not needed.
- **No metric change, no tolerance, no case/hyphen fold.** The 844 findings went away because the key
  became the key the corpus already used — not because anything got more permissive. `coverage.py` is
  untouched.
- **No push, no PR, no merge.** The manager reviews.

### 7.5 The unfiltered seedsmith suite — 4 failures, none mine

`python -m pytest gk-forge/tools/seedsmith/tests -q` → `4 failed, 4703 passed, 4 skipped` (22m18s). All four
are outside the scoped boundary and none reads a file I touched (verified by grep):

| failure | cause | mine? |
|---|---|---|
| `test_tool_invocation_guard.py::test_every_python_file_under_the_tool_is_inside_a_scanned_scope` | a machine-local untracked `tools/seedsmith/.venv-verify/` tree; the file mentions `refresh_allocated_partitions.py` only in two comments | no |
| `test_topology_repair.py::test_written_partitions_are_lf_only` | Windows CRLF in a written run ledger (`set-charm-gen.ledger.json`) | no |
| `test_tree_plan_emit.py::RosterAndVocabularyTests::test_property_vocabulary_counts_match_the_spec_table` | `atomAttachPoint: length differs (7 vs 9)` — the stale atom-vocabulary row `DESIGN-GATE.md` records going stale repeatedly | no |
| `test_tree_plan_emit.py::EmitCheckRoundTripTests::test_the_real_committed_plan_agrees_with_a_fresh_check` | same stale vocabulary table | no |

`Core.Expeditions.Tests` (11/38 red, inherited) was not run and is not implicated: this change touches
no `src/**` file.

---

## 8. What I could not determine

1. **Whether the `species/` scope was a deliberate readability choice by a person, or an invention.**
   `git log -L` on the line gives one commit, `0597a3152` *"item-seed corpus: allocate + resolve the
   species-population set theme (causes 1+2)"*, and its message states the defect it fixed was
   **848 `IdOutsideNamespace` errors** — an **id-prefix** problem. The prefix half was the fix; the
   partition-id half rode along in the same `Add(...)` call. The body never mentions naming or scoping a
   partition, which is why I read it as incidental. If a person did intend the scope, §5.4 is the
   position to weigh, and the cost of that route is a 844-file corpus migration this lane may not make.
2. **Whether the owner wants the partition to *look* species-scoped.** The `speciesId` field answers
   that question for anything programmatic; a human scanning a directory listing no longer sees it. That
   is a preference, not a contract, and it is the one thing here I would put back to the owner.
3. **`naming.v1.json`'s `partitionCount: 41` is now more stale than it was** (it never counted the 904
   species partitions). The registry's `speciesThemesNote:395` explains *why* it is not enumerated — a
   growing population must not be pinned — so this is the documented behaviour, not drift I introduced.
   But the file is `data/**`, outside this fence, and its `partitionCountCheck.sets: 5` is a separate
   question I did not touch.
4. **The 60 unoccupied species partitions and `sets/might-offense` are a real content backlog** this
   audit sizes but does not fill. `fill.py:4-5` walks *discovered corpus partitions only*, so a fill can
   now reach them correctly — which is the practical unblocking of BCU2.11, and belongs to that program.

## 9. Open questions for the owner / the owning program

1. **Confirm the partition key is `sets/{idSlug}`** (a registry-literal reading of `partitionKey:
   "themeId"`), or say the `species/` scope should be restored — in which case the corpus must be
   migrated and the migration is a `data/**` change this lane could not make.
2. **`naming.v1.json:365`'s `partitionCount: 41` / `partitionCountCheck.sets: 5`** — should the registry
   record that the `sets` kind's partition population is registry-declared (41) plus
   roster-derived (N), so a reader does not have to know that? The `speciesThemesNote` explains it in
   prose; a field would make it machine-readable.
3. **`CreatureSpeciesCatalog.cs:136-137`** — the guard's message says *"must be non-empty lower-kebab"*
   while the check is `ToLowerInvariant()` only, and 73 shipped `speciesId`s carry `_`. Either the
   message or the check is wrong. Out of this lane's fence (`src/**`); filed, not touched.
4. **`metrics/dedup.py:85`** — sort `corpus.kinds` so `SemanticDedup/NearDuplicate`'s `subject` is
   deterministic. Out of this lane's fence; filed, not touched. (Its own header already worries about
   reproducibility for a different reason — `dedup.py:51` *"different across runs and unreproducible in
   CI"* — so this is the same concern reaching a second place.)
5. **`test_items_adapter.py:203`'s circular assertion** — now covered from the id side by
   `test_every_shipped_set_entry_partitions_into_an_allocated_partition`, but the circular line itself is
   still there and still cannot see a label/identity mismatch for any *other* kind.
6. **BCU2.11 can be re-run** — its recorded blocker ("a fill aimed at `sets/species/<id>` re-writes sets
   that already exist under the second key") is gone by construction, and 60 + 1 partitions are now
   correctly visible to `fill`. That re-run is a model-call spend decision, not this lane's.
